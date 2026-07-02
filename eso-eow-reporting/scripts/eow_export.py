# eow_export.py — writes the structured sidecar JSON next to each individual EOW report.
# This is the DATA CONTRACT the Week-at-a-Glance (Monday look-ahead) skill consumes.
# Called when an individual EOW report is finalized. Never parse the rendered PDF; emit this.

import json, os

SCHEMA_VERSION = 1

def build_payload(person, role, week_ending, next_week_of, projects, mkw_actions=None,
                  allocated_total=None, focus=None):
    """
    person/role: strings. week_ending/next_week_of: ISO 'YYYY-MM-DD'.
    projects: list of dicts, each:
        {project, next_pace, allocated_hours, temporary(bool), lever(str|None),
         look_ahead:[{item,date}], barriers_owned:[{barrier,path,date}],
         milestones_due:[{label,date}]}
    mkw_actions: list of {project, ask, kind('action'|'fyi'), direction('owe'|'waiting'), by, priority}
                 For kind=='fyi': by/priority are None (awareness only, no deadline/priority).
    focus: the person's one-line "focus next week" string (used by Week-at-a-Glance team alignment).
    """
    if allocated_total is None:
        allocated_total = round(sum(p.get("allocated_hours", 0) for p in projects), 1)
    return {
        "schema_version": SCHEMA_VERSION,
        "person": person, "role": role,
        "week_ending": week_ending, "next_week_of": next_week_of,
        "allocated_total": allocated_total,
        "projects": projects,
        "mkw_actions": mkw_actions or [],
        "focus": focus or "",
    }

def write_sidecar(payload, out_dir=".", base=None):
    """Write eow_data_<Key>_<week_ending>.json into out_dir. Returns the path.
    Pass `base` (the shared EOW folder) to key on the identity registry (First+Last on
    a shared-last-name collision); otherwise falls back to the last-name key.
    Keying always goes through eow_paths.person_slug — the one canonical implementation —
    so this file's key can never drift from the PDF / milestone-store / snapshot keys."""
    import eow_paths
    key = eow_paths.person_slug(payload["person"], base)
    fn = f"eow_data_{key}_{payload['week_ending']}.json"
    path = os.path.join(out_dir, fn)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return path
