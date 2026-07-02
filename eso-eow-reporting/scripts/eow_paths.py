# eow_paths.py — shared-folder + per-week submission conventions for the EOW skill.
#
# Layout (all under the shared Employee Ops EOW location = BASE):
#   <BASE>/stores/milestones_<Person>.json     rolling per-person milestone stores (source of truth)
#   <BASE>/Submissions/<week>/                  one folder per week; first submitter creates it
#       EOW_Individual_<Person>_<week>.pdf      each person's rendered report
#       eow_data_<Person>_<weekending>.json     each person's structured sidecar (rollup reads these)
#       milestones_snapshot_<Person>.json       read-only archive copy of their open milestones
#       EOW_MKW_Rollup_<week>.pdf               Maggie's consolidated rollup (written here on rollup run)
#
# Week folders are keyed to the week-STARTING Monday and named "YYYY.MM.DD - MM.DD"
# (Monday full date — Friday month.day), e.g. "2026.06.22 - 06.26".

import os
from datetime import date, timedelta

# REAL RUNS: set BASE to the shared EOW_System folder in the user's connected workspace,
# e.g. ".../ĒSO/04_AI/3_Employees Ops/EOW_System". Default "." is for local/sample runs.
BASE = "."
SUBMISSIONS_SUBDIR = "Submissions"
STORES_SUBDIR = "stores"   # must match eow_milestones.STORES_SUBDIR


def week_monday(d=None):
    """Monday of the week containing date d (default: today)."""
    d = d or date.today()
    return d - timedelta(days=d.weekday())


def week_friday(monday):
    return monday + timedelta(days=4)


def week_folder_name(monday=None):
    """'2026.06.22 - 06.26' — Monday full date, Friday month.day."""
    monday = monday or week_monday()
    return "%s - %s" % (monday.strftime("%Y.%m.%d"), week_friday(monday).strftime("%m.%d"))


def week_folder(base=None, monday=None):
    return os.path.join(base or BASE, SUBMISSIONS_SUBDIR, week_folder_name(monday))


def ensure_week_folder(base=None, monday=None):
    """Return this week's submission folder, creating it on first use.
    Idempotent: the first submitter creates it; everyone else reuses the same folder."""
    p = week_folder(base, monday)
    os.makedirs(p, exist_ok=True)
    return p


def default_person_key(person):
    """Canonical fallback file key for a person: LAST NAME, alnum, title-cased.
    'Peter Hall' -> 'Hall'. This is the ONE implementation of that rule — eow_identity.py
    and eow_export.py both call this rather than re-deriving it, so a person's PDF,
    sidecar, milestone store, and snapshot can never drift onto different keys."""
    parts = str(person).split()
    last = parts[-1] if parts else str(person)
    return "".join(c for c in last.title() if c.isalnum()) or "Unknown"


def person_slug(person, base=None):
    """Filename key for a person — used for the EOW_Report PDF, the eow_data sidecar,
    the milestone store, and the snapshot, so all of a person's files key the same way.
    If `base` is given and the person is in the identity registry (set up at first run),
    returns their REGISTERED key (which is First+Last when two people share a last name).
    Otherwise defaults to default_person_key(person): 'Peter Hall' -> 'Hall'."""
    if base is not None:
        try:
            import eow_identity
            return eow_identity.key_for(person, base)
        except Exception:
            pass
    return default_person_key(person)


def stores_dir(base=None):
    """Return <base>/stores, creating it if needed (rolling per-person stores live here)."""
    p = os.path.join(base or BASE, STORES_SUBDIR)
    os.makedirs(p, exist_ok=True)
    return p
