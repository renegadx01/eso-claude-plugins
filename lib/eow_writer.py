"""Bridge between the Streamlit app and the EOW reporting scripts.

Imports eow_db / eow_db_write from the sibling eso-eow-reporting repo by
adding that scripts directory to sys.path at import time. The service-role
Supabase config lives at <EOW_System>/.config/supabase.json (gitignored) —
the same file the CLI batch script uses.

Public API:
  EOW_BASE          — absolute path to the shared EOW_System folder
  test_connection() — returns person count or raises
  process_payload() — normalize + dry-run or live-write one sidecar dict
"""

import sys
from datetime import date, timedelta
from pathlib import Path

# ── resolve paths ──────────────────────────────────────────────────────────
# This file lives at: <EOW_System>/platform/eso-platform-app/lib/eow_writer.py
# The EOW scripts live at: <EOW_System>/github_upload/eso-claude-plugins/
#                           eso-eow-reporting/scripts/
_THIS = Path(__file__).resolve()
EOW_BASE = str(_THIS.parents[3])   # three levels up from lib/ -> EOW_System

_SCRIPTS = (
    _THIS.parents[3]
    / "github_upload"
    / "eso-claude-plugins"
    / "eso-eow-reporting"
    / "scripts"
)

if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import eow_db          # noqa: E402  (path manipulation must come first)
import eow_db_write    # noqa: E402


# ── priority normalisation (McIvor schema uses lowercase_underscore) ────────
_PRIORITY_MAP = {
    "urgent":         "Urgent",
    "this_week":      "This week",
    "when_available": "When available",
}

def _norm_priority(p):
    if not p:
        return None
    return _PRIORITY_MAP.get(str(p).lower().replace(" ", "_"), p)


def _iso_to_slash(s):
    """'2026-08-08' -> '8/8' so _extract_needed_by regex can parse it."""
    try:
        d = date.fromisoformat(str(s))
        return f"{d.month}/{d.day}"
    except Exception:
        return s


def _next_monday(week_ending_iso):
    try:
        d = date.fromisoformat(week_ending_iso)
        return (d + timedelta(days=7 - d.weekday())).isoformat()
    except Exception:
        return "2026-08-10"


def normalize(payload: dict) -> dict:
    """Coerce any sidecar schema variant to the v2 shape eow_db_write expects.

    Handles three schema variants found in the wild:
      v2  — next_week_hours, top-level mkw_actions (Hall, Mendez, Stovall)
      v1  — allocated_hours, top-level mkw_actions (Martin, Smith)
      alt — name/hrs_reported, per-project or top-level mkw_items (McIvor, Villasana)
    """
    p = dict(payload)

    if "next_week_of" not in p:
        p["next_week_of"] = _next_monday(p.get("week_ending", ""))

    projects_out = []
    per_project_actions = []   # McIvor: mkw_items embedded inside project

    for proj in p.get("projects", []):
        name = proj.get("project") or proj.get("name", "Unknown")

        hours = proj.get("next_week_hours")
        if hours is None:
            hours = proj.get("allocated_hours", 0)

        barriers_raw = proj.get("barriers_owned") or proj.get("barriers") or []
        barriers_out = [
            {"barrier": b.get("barrier", ""), "path": b.get("path", ""), "date": b.get("date", "") or ""}
            for b in barriers_raw if isinstance(b, dict)
        ]

        la_raw = proj.get("look_ahead") or []
        la_out = []
        for item in la_raw:
            if isinstance(item, str):
                la_out.append({"item": item, "date": ""})
            elif isinstance(item, dict):
                la_out.append({"item": item.get("item", ""), "date": item.get("date", "") or ""})

        projects_out.append({
            "project": name,
            "next_week_hours": hours,
            "look_ahead": la_out,
            "barriers_owned": barriers_out,
            "milestones_due": proj.get("milestones_due") or [],
        })

        for item in proj.get("mkw_items", []):
            per_project_actions.append((item, name))

    # McIvor: total next-week hours in hours.next_week_allocated, single project
    if projects_out and all(p2["next_week_hours"] == 0 for p2 in projects_out):
        total = (p.get("hours") or {}).get("next_week_allocated", 0)
        if total and len(projects_out) == 1:
            projects_out[0]["next_week_hours"] = total

    # Villasana: next_week_allocation is {project: {pace, pace_int}} — distribute by weight
    if "next_week_allocation" in p and all(p2["next_week_hours"] == 0 for p2 in projects_out):
        nwa = p["next_week_allocation"]
        total_weight = sum(
            v.get("pace_int", 0) for v in nwa.values() if isinstance(v, dict)
        )
        capacity = (p.get("hours") or {}).get("total", 40)
        for p2 in projects_out:
            entry = nwa.get(p2["project"], {})
            weight = entry.get("pace_int", 0) if isinstance(entry, dict) else 0
            if total_weight:
                p2["next_week_hours"] = round(capacity * weight / total_weight, 1)

    p["projects"] = projects_out

    # ── normalise mkw_actions ───────────────────────────────────────────────
    raw_actions = (
        p.get("mkw_actions")                  # v2/v1: top-level list
        or [(i, i.get("project", "")) for i in p.get("mkw_items", [])]  # Villasana
        or per_project_actions                 # McIvor: embedded in project
    )

    actions_out = []
    for entry in raw_actions:
        item, proj_name = (entry, entry.get("project", "")) if isinstance(entry, dict) else entry
        kind = item.get("kind", "fyi")
        ask = item.get("ask") or item.get("note", "")
        if not ask:
            continue
        by_raw = item.get("by")
        if by_raw and str(by_raw).count("-") == 2:
            by_raw = _iso_to_slash(by_raw)
        actions_out.append({
            "project": proj_name or item.get("project", ""),
            "ask": ask,
            "kind": kind,
            "direction": item.get("direction") or item.get("owner"),
            "by": by_raw,
            "priority": _norm_priority(item.get("priority")),
        })

    p["mkw_actions"] = actions_out
    p.pop("mkw_items", None)
    return p


def test_connection() -> int:
    """Return number of people rows on success, raise on failure."""
    return eow_db.test_connection(EOW_BASE)


def process_payload(payload: dict, dry_run: bool = True) -> dict:
    """Normalise one sidecar dict and (optionally) write it to Supabase.

    Returns the result dict from eow_db_write.write_payload(), augmented with
    a 'person' key for display convenience.
    """
    normalised = normalize(payload)
    result = eow_db_write.write_payload(EOW_BASE, normalised, dry_run=dry_run)
    result["person"] = normalised.get("person", "Unknown")
    result["week_ending"] = normalised.get("week_ending", "")
    result["next_week_of"] = normalised.get("next_week_of", "")
    return result
