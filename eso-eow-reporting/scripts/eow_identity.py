# eow_identity.py — per-person identity registry for the EOW skill.
# Captured ONCE at first run (the person's name + ĒSO level), stored in
# <BASE>/stores/identities.json, and reused every time after. Assigns a stable,
# collision-safe FILE KEY used for all of that person's files (EOW_Report PDF,
# eow_data sidecar, milestone store, snapshot).
#
#   identities.json:  { "Peter Hall": {"level": "Associate", "key": "Hall"}, ... }
#   key = LAST NAME; if a DIFFERENT person already holds that last name, fall back to
#   First+Last (e.g. "PeterHall"), then First+Last2... so keys never collide.

import json, os
import eow_paths as P

LEVELS = ["Associate", "Senior Associate", "Associate Principal", "Principal", "Senior Principal", "Operations Manager"]


def _registry_path(base=None):
    return os.path.join(P.stores_dir(base), "identities.json")


def load_identities(base=None):
    p = _registry_path(base)
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_identities(ids, base=None):
    with open(_registry_path(base), "w", encoding="utf-8") as f:
        json.dump(ids, f, indent=2, ensure_ascii=False)


def _firstlast(full):
    return "".join(c for c in str(full).title() if c.isalnum()) or "Unknown"


def key_for(full_name, base=None):
    """Registered key if known; otherwise the default last-name key (no write)."""
    ids = load_identities(base)
    rec = ids.get(full_name)
    if rec and rec.get("key"):
        return rec["key"]
    return P.default_person_key(full_name)


def get(full_name, base=None):
    """Return {'level','key'} if this person has been set up, else None (= first run)."""
    return load_identities(base).get(full_name)


def register(full_name, level, base=None):
    """First-run capture. Returns {'level','key'}. Idempotent: updates the level but keeps
    the key. Collision-safe: last name, else First+Last, else First+Last2..."""
    ids = load_identities(base)
    if full_name in ids:
        ids[full_name]["level"] = level
        save_identities(ids, base)
        return ids[full_name]
    used = {v["key"]: n for n, v in ids.items()}
    key = P.default_person_key(full_name)
    if key in used and used[key] != full_name:           # same last name as someone else
        key = _firstlast(full_name); bkey = key; i = 2
        while key in used and used[key] != full_name:
            key = "%s%d" % (bkey, i); i += 1
    ids[full_name] = {"level": level, "key": key}
    save_identities(ids, base)
    return ids[full_name]
