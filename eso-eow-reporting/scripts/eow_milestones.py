# eow_milestones.py — persistent milestone store for the EOW skill.
# Milestones live OUTSIDE any single week. They are opened during the individual
# EOW capture, carry over week to week until completed, and only drop off the
# rollup timeline when status == "complete". Date changes are recorded as slips,
# never silently overwritten.
#
# Store location: a shared milestones.json (file server today, SharePoint List later).
# Schema per record:
#   id           stable slug, e.g. "island-ledge-permit"
#   project      display name
#   label        short milestone name, e.g. "Permit set"
#   date         current target, ISO "YYYY-MM-DD"
#   status       "open" | "complete"
#   key          bool — render as a key/emphasized node on the timeline
#   completed_on ISO date or null
#   slips        list of {from, to, recorded_on} — slip history (kept, per Pete)

import json, os, glob, re
from datetime import date
import eow_paths

DEFAULT_STORE = "milestones.json"
STORES_SUBDIR = "stores"   # per-person stores: <base>/stores/milestones_<Person>.json


def store_path(person, base_dir="."):
    """Stable ROLLING store file for one person — the single source of truth.
    Carries over week to week; the individual report reads/writes only this file.
    Key comes from the identity registry (First+Last on a shared-last-name collision)."""
    return os.path.join(base_dir, STORES_SUBDIR, "milestones_%s.json" % eow_paths.person_slug(person, base_dir))


def ensure_store(person, base_dir="."):
    """Return the person's store path, creating stores/ + an empty file on first use."""
    p = store_path(person, base_dir)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if not os.path.exists(p):
        save_store([], p)
    return p


def load_all_stores(base_dir="."):
    """Merge EVERY per-person store under <base>/stores/ — the rollup timeline input.
    Each record is tagged with its owner (from the filename) so the rollup can attribute it.
    The individual report never calls this; it uses only its own store_path()."""
    out = []
    for path in sorted(glob.glob(os.path.join(base_dir, STORES_SUBDIR, "milestones_*.json"))):
        owner = re.sub(r"^milestones_|\.json$", "", os.path.basename(path))
        for m in load_store(path):
            m = dict(m); m.setdefault("owner", owner); out.append(m)
    return out


def write_snapshot(records, week_folder, person, base=None):
    """Read-only snapshot of this person's OPEN milestones, dropped in the week folder
    next to the PDF/sidecar. Archive only — never read back as the source of truth.
    Pass `base` (the shared EOW folder) so the key matches the registry on collisions."""
    os.makedirs(week_folder, exist_ok=True)
    snap = os.path.join(week_folder, "milestones_snapshot_%s.json" % eow_paths.person_slug(person, base))
    save_store(open_milestones(records), snap)
    return snap


def load_store(path=DEFAULT_STORE):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_store(records, path=DEFAULT_STORE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def open_milestones(records):
    """All currently-open milestones, sorted by date — the timeline input."""
    return sorted(
        [m for m in records if m.get("status", "open") == "open"],
        key=lambda m: m["date"],
    )


def timeline_points(records):
    """(date, 'Project\\nLabel', key) tuples the renderer draws."""
    return [
        (date.fromisoformat(m["date"]), f'{m["project"]}\n{m["label"]}', bool(m.get("key")))
        for m in open_milestones(records)
    ]


def add_milestone(records, id, project, label, target_date, key=False):
    """Append a new open milestone during capture. No-op if id already exists."""
    if any(m["id"] == id for m in records):
        return records
    records.append({
        "id": id, "project": project, "label": label,
        "date": target_date, "status": "open", "key": key,
        "completed_on": None, "slips": [],
    })
    return records


def slip_milestone(records, id, new_date, today=None):
    """Move a milestone's date and RECORD the slip (old date kept in history)."""
    today = today or date.today().isoformat()
    for m in records:
        if m["id"] == id and m["date"] != new_date:
            m.setdefault("slips", []).append(
                {"from": m["date"], "to": new_date, "recorded_on": today}
            )
            m["date"] = new_date
    return records


def complete_milestone(records, id, today=None):
    """Mark complete — shows as a win this week, gone from next week's timeline."""
    today = today or date.today().isoformat()
    for m in records:
        if m["id"] == id:
            m["status"] = "complete"
            m["completed_on"] = today
    return records


def slipped_this_week(records, since):
    """Milestones whose date moved on/after `since` (ISO) — feed Section 5 flags."""
    out = []
    for m in records:
        for s in m.get("slips", []):
            if s["recorded_on"] >= since:
                out.append((m["project"], m["label"], s["from"], s["to"]))
    return out
