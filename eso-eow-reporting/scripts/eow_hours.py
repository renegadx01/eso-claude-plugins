# eow_hours.py — next-week hours allocation + reported-hours checks for the EOW skill.
#
# MODEL (locked with Pete 2026.06.19): role-specific ABSOLUTE hour bands on a flat
# 40-hour base for everyone. Two tiers — "Associate" and "Everyone else" (Senior
# Associate / Associate Principal / Principal / Senior Principal). Role selects the
# column; it does NOT scale a capacity number. Pace -> hours is a direct lookup.
#
#   #  Pace          Assoc  Everyone-else   Temporary?
#   1  Hold          0      0               yes (lever)
#   2  Maintenance   4      2               no
#   3  Light         8      4               no
#   4  Moderate      10     6               no
#   5  Sprint        16     10              yes (lever)
#   6  Heavy         20     10              no
#   7  Catapult      32     20              yes (lever)
#
# Per Pete: never scale proposed hours down. If next-week allocation OR reported
# hours run over the 40-hour base, FLAG it to Maggie (it carries up into the rollup).
# Maintenance/Light bands were ranges; the allocation target is the top of the band.

import json, os

BASE = 40.0  # flat 40-hour week for everyone; role changes the band, not the base.

# (Associate, Everyone-else)
PACE_HOURS = {
    1: (0,  0),    # Hold
    2: (4,  2),    # Maintenance
    3: (8,  4),    # Light
    4: (10, 6),    # Moderate
    5: (16, 10),   # Sprint
    6: (20, 10),   # Heavy
    7: (32, 20),   # Catapult
}
PACE_NAME = {1:"Hold",2:"Maintenance",3:"Light",4:"Moderate",5:"Sprint",6:"Heavy",7:"Catapult"}
PACE_NUM  = {v.lower(): k for k, v in PACE_NAME.items()}
TEMPORARY = {"Hold", "Sprint", "Catapult"}  # locked to a lever (a milestone) that ends them

# Operations Manager (and any future overhead-only role) does NOT use pace allocation.
# Flat 40-hr overhead week on a single preset project; pace/budget/phase don't apply.
OVERHEAD_ROLES = {"Operations Manager"}
OVERHEAD_PROJECT = "Operations and Admin"

def is_overhead(role):
    return str(role).strip().lower() in {r.lower() for r in OVERHEAD_ROLES}

ROLE_STORE = "capacity.json"   # name -> role; e.g. {"_default_role":"Everyone else","Sample Employee":"Associate"}


def load_role(name, store=ROLE_STORE):
    cfg = {}
    if os.path.exists(store):
        cfg = json.load(open(store, encoding="utf-8"))
    return cfg.get(name, cfg.get("_default_role", "Everyone else"))


def tier(role):
    """0 = Associate column, 1 = Everyone-else column."""
    return 0 if str(role).strip().lower() == "associate" else 1


def pace_num(pace):
    """Accept 7, 'Heavy', 'Heavy (6)' -> int 1..7."""
    if isinstance(pace, int):
        return pace
    p = str(pace).strip()
    for name, n in PACE_NUM.items():
        if p.lower().startswith(name):
            return n
    digits = "".join(c for c in p if c.isdigit())
    return int(digits) if digits else 0


def allocate(projects, role, name=None):
    """
    projects: list of (project_name, next_week_pace)  [pace as int or name]
    Returns rows + total + over/under-40 info + a Maggie-bound flag.
    Each row: (project, hours, pace_name, note). Proposed hours are kept, never scaled.
    """
    if is_overhead(role):
        # No pace. One preset project, flat 40-hr overhead — exactly the base, no flag.
        return {"rows": [(OVERHEAD_PROJECT, BASE, "Overhead", "flat 40-hr overhead")],
                "total": BASE, "base": BASE, "overflow": False, "over_by": 0, "slack": 0,
                "mkw_flag": None, "capacity_note": "40-hr overhead (Operations Manager)"}
    col = tier(role)
    rows = []
    for proj, pace in projects:
        n = pace_num(pace)
        hrs = PACE_HOURS.get(n, (0, 0))[col]
        rows.append((proj, hrs, PACE_NAME.get(n, str(pace)), f"matches {PACE_NAME.get(n,'').lower()} pace"))
    total = round(sum(h for _, h, _, _ in rows), 1)
    over = round(total - BASE, 1)
    overflow = over > 0
    flag = None
    if overflow:
        who = f"{name}'s " if name else ""
        flag = (f"⚑ MKW: {who}next-week allocation totals {total:g} vs the 40-hr base "
                f"(over by {over:g}). Numbers kept as-is — Maggie to confirm priorities, "
                f"reassignment, or approved overtime.")
    return {
        "rows": rows, "total": total, "base": BASE,
        "overflow": overflow, "over_by": over if overflow else 0,
        "slack": round(-over, 1) if over < 0 else 0,
        "mkw_flag": flag,
        "capacity_note": capacity_note(total),
    }


# ---- reported hours (this week) -------------------------------------------------

def derive_pace(hours, role):
    """Reverse lookup: actual hours -> implied pace name. CONSISTENCY CHECK ONLY.
    Hours can't separate Sprint from Heavy (intent, not hours, distinguishes them)."""
    h = float(hours)
    if h <= 0:
        return "Hold"
    if tier(role) == 0:  # Associate
        if h <= 4:  return "Maintenance"
        if h <= 8:  return "Light"
        if h <= 13: return "Moderate"
        if h <= 18: return "Sprint"
        if h <= 26: return "Heavy"
        return "Catapult"
    else:               # Everyone else
        if h <= 2:  return "Maintenance"
        if h <= 4:  return "Light"
        if h <= 7:  return "Moderate"
        if h <= 15: return "Sprint/Heavy"
        return "Catapult"


def pace_matches(stated, reported_hours, role):
    """True if the stated pace is consistent with the hours-implied pace."""
    implied = derive_pace(reported_hours, role)
    s = PACE_NAME.get(pace_num(stated), str(stated))
    if implied == "Sprint/Heavy":
        return s in ("Sprint", "Heavy")
    return s == implied


def report_check(stated, reported_hours, role):
    """Returns (implied_pace, ok, note) for Sheet A's Check column."""
    implied = derive_pace(reported_hours, role)
    ok = pace_matches(stated, reported_hours, role)
    note = "✓" if ok else f"⚑ mismatch — logged {reported_hours:g} reads as {implied}"
    return implied, ok, note


def reported_overflow(reported_total, name=None):
    """If actual hours logged exceed the 40-hr base, flag to Maggie."""
    over = round(float(reported_total) - BASE, 1)
    if over > 0:
        who = f"{name} " if name else ""
        return (f"⚑ MKW: {who}logged {reported_total:g} hrs this week vs the 40-hr base "
                f"(over by {over:g}). Over actual time — confirm overtime or rebalance.")
    return None


def utilization(reported_total):
    return round(100.0 * float(reported_total) / BASE)


def capacity_note(total):
    over = round(float(total) - BASE, 1)
    if over > 0: return f"overcommitted by {over:g} hrs — flag to MKW"
    if over < 0: return f"{abs(over):g} hrs slack"
    return "fully allocated"
