"""Made-up demo data for developing the dashboard's look and feel without
touching the shared production Supabase database. Every project, person,
and number here is fictional — none of it corresponds to real ĒSO clients,
staff, or financials. See lib/demo_client.py for how this gets served up as
a stand-in for the real Supabase client, and lib/auth.py for how a page opts
into demo mode (?demo=1 in the URL).

Column names match db/migrations/001_base_schema.sql exactly so the fake
client can be a drop-in replacement for the real one.
"""

PEOPLE = [
    {"id": "ppl-jordan", "full_name": "Jordan Reyes", "key": "jordan", "role": "Principal Architect", "weekly_capacity": 40, "billable": True, "active": True},
    {"id": "ppl-priya", "full_name": "Priya Nair", "key": "priya", "role": "Project Architect", "weekly_capacity": 40, "billable": True, "active": True},
    {"id": "ppl-alex", "full_name": "Alex Chen", "key": "alex", "role": "Job Captain", "weekly_capacity": 40, "billable": True, "active": True},
    {"id": "ppl-morgan", "full_name": "Morgan Lee", "key": "morgan", "role": "Interior Designer", "weekly_capacity": 40, "billable": True, "active": True},
    {"id": "ppl-sam", "full_name": "Sam Okafor", "key": "sam", "role": "Job Captain", "weekly_capacity": 40, "billable": True, "active": True},
    {"id": "ppl-devon", "full_name": "Devon Brooks", "key": "devon", "role": "Design Coordinator", "weekly_capacity": 40, "billable": False, "active": True},
]

RATES = [
    {"id": "rate-principal-cost", "role": "Principal Architect", "rate_type": "cost", "hourly_rate": 85, "effective_date": "2026-01-01"},
    {"id": "rate-pa-cost", "role": "Project Architect", "rate_type": "cost", "hourly_rate": 65, "effective_date": "2026-01-01"},
    {"id": "rate-jc-cost", "role": "Job Captain", "rate_type": "cost", "hourly_rate": 55, "effective_date": "2026-01-01"},
    {"id": "rate-id-cost", "role": "Interior Designer", "rate_type": "cost", "hourly_rate": 50, "effective_date": "2026-01-01"},
    {"id": "rate-dc-cost", "role": "Design Coordinator", "rate_type": "cost", "hourly_rate": 35, "effective_date": "2026-01-01"},
]

PROJECTS = [
    {"id": "proj-willow", "name": "Willow Creek Residence", "client_name": "The Hendersons", "project_type": "Residential — new build", "rate_type": "standard", "status": "active", "total_fee": 185000, "start_date": "2026-03-02", "target_end": "2027-01-15"},
    {"id": "proj-rosedale", "name": "Rosedale Duplex Remodel", "client_name": "Rosedale Partners", "project_type": "Residential — remodel", "rate_type": "standard", "status": "active", "total_fee": 96000, "start_date": "2026-02-09", "target_end": "2026-09-30"},
    {"id": "proj-baker", "name": "Baker Street Café", "client_name": "Baker St. Hospitality Group", "project_type": "Commercial — hospitality", "rate_type": "standard", "status": "active", "total_fee": 145000, "start_date": "2026-07-06", "target_end": "2027-03-01"},
    {"id": "proj-pecan", "name": "Pecan Grove ADU", "client_name": "Whitfield Family", "project_type": "Residential — ADU", "rate_type": "standard", "status": "active", "total_fee": 62000, "start_date": "2025-11-03", "target_end": "2026-08-28"},
    {"id": "proj-marfa", "name": "Marfa Modern", "client_name": "Ostrander Trust", "project_type": "Residential — new build", "rate_type": "standard", "status": "active", "total_fee": 310000, "start_date": "2026-05-11", "target_end": "2027-09-01"},
    {"id": "proj-eastside", "name": "Eastside Makers Studio", "client_name": "Eastside Collective LLC", "project_type": "Commercial — light industrial", "rate_type": "standard", "status": "active", "total_fee": 210000, "start_date": "2026-01-12", "target_end": "2026-10-15"},
    {"id": "proj-overlook", "name": "Overlook Terrace Multifamily", "client_name": "Overlook Terrace Development", "project_type": "Multifamily", "rate_type": "standard", "status": "active", "total_fee": 420000, "start_date": "2026-07-20", "target_end": "2028-02-01"},
    {"id": "proj-eso-office", "name": "ĒSO Office Buildout", "client_name": "ĒSO Internal", "project_type": "Commercial — TI (internal)", "rate_type": "standard", "status": "completed", "total_fee": 75000, "start_date": "2025-09-01", "target_end": "2026-03-01"},
]

# Phases follow the standard SD/DD/CD/CA split. fee/budget_hours are rough,
# made-up numbers — not derived from a real loaded rate.
PHASES = [
    # Willow Creek Residence — mid-DD
    {"id": "ph-willow-sd", "project_id": "proj-willow", "name": "Schematic Design", "fee": 27750, "budget_hours": 220, "pct_complete": 100, "sequence": 1},
    {"id": "ph-willow-dd", "project_id": "proj-willow", "name": "Design Development", "fee": 37000, "budget_hours": 300, "pct_complete": 60, "sequence": 2},
    {"id": "ph-willow-cd", "project_id": "proj-willow", "name": "Construction Documents", "fee": 92500, "budget_hours": 620, "pct_complete": 0, "sequence": 3},
    {"id": "ph-willow-ca", "project_id": "proj-willow", "name": "Construction Administration", "fee": 27750, "budget_hours": 180, "pct_complete": 0, "sequence": 4},
    # Rosedale Duplex Remodel — deep in CD, running hot (good "at risk" case)
    {"id": "ph-rosedale-sd", "project_id": "proj-rosedale", "name": "Schematic Design", "fee": 14400, "budget_hours": 110, "pct_complete": 100, "sequence": 1},
    {"id": "ph-rosedale-dd", "project_id": "proj-rosedale", "name": "Design Development", "fee": 19200, "budget_hours": 150, "pct_complete": 100, "sequence": 2},
    {"id": "ph-rosedale-cd", "project_id": "proj-rosedale", "name": "Construction Documents", "fee": 48000, "budget_hours": 260, "pct_complete": 85, "sequence": 3},
    {"id": "ph-rosedale-ca", "project_id": "proj-rosedale", "name": "Construction Administration", "fee": 14400, "budget_hours": 90, "pct_complete": 0, "sequence": 4},
    # Baker Street Café — just kicked off
    {"id": "ph-baker-sd", "project_id": "proj-baker", "name": "Schematic Design", "fee": 21750, "budget_hours": 170, "pct_complete": 40, "sequence": 1},
    {"id": "ph-baker-dd", "project_id": "proj-baker", "name": "Design Development", "fee": 29000, "budget_hours": 230, "pct_complete": 0, "sequence": 2},
    {"id": "ph-baker-cd", "project_id": "proj-baker", "name": "Construction Documents", "fee": 72500, "budget_hours": 480, "pct_complete": 0, "sequence": 3},
    {"id": "ph-baker-ca", "project_id": "proj-baker", "name": "Construction Administration", "fee": 21750, "budget_hours": 140, "pct_complete": 0, "sequence": 4},
    # Pecan Grove ADU — wrapping up CA
    {"id": "ph-pecan-sd", "project_id": "proj-pecan", "name": "Schematic Design", "fee": 9300, "budget_hours": 75, "pct_complete": 100, "sequence": 1},
    {"id": "ph-pecan-dd", "project_id": "proj-pecan", "name": "Design Development", "fee": 12400, "budget_hours": 100, "pct_complete": 100, "sequence": 2},
    {"id": "ph-pecan-cd", "project_id": "proj-pecan", "name": "Construction Documents", "fee": 31000, "budget_hours": 210, "pct_complete": 100, "sequence": 3},
    {"id": "ph-pecan-ca", "project_id": "proj-pecan", "name": "Construction Administration", "fee": 9300, "budget_hours": 70, "pct_complete": 70, "sequence": 4},
    # Marfa Modern — early DD, big project
    {"id": "ph-marfa-sd", "project_id": "proj-marfa", "name": "Schematic Design", "fee": 46500, "budget_hours": 340, "pct_complete": 100, "sequence": 1},
    {"id": "ph-marfa-dd", "project_id": "proj-marfa", "name": "Design Development", "fee": 62000, "budget_hours": 460, "pct_complete": 30, "sequence": 2},
    {"id": "ph-marfa-cd", "project_id": "proj-marfa", "name": "Construction Documents", "fee": 155000, "budget_hours": 980, "pct_complete": 0, "sequence": 3},
    {"id": "ph-marfa-ca", "project_id": "proj-marfa", "name": "Construction Administration", "fee": 46500, "budget_hours": 300, "pct_complete": 0, "sequence": 4},
    # Eastside Makers Studio — deep CD, over budget hours (at-risk example)
    {"id": "ph-eastside-sd", "project_id": "proj-eastside", "name": "Schematic Design", "fee": 31500, "budget_hours": 240, "pct_complete": 100, "sequence": 1},
    {"id": "ph-eastside-dd", "project_id": "proj-eastside", "name": "Design Development", "fee": 42000, "budget_hours": 320, "pct_complete": 100, "sequence": 2},
    {"id": "ph-eastside-cd", "project_id": "proj-eastside", "name": "Construction Documents", "fee": 105000, "budget_hours": 560, "pct_complete": 95, "sequence": 3},
    {"id": "ph-eastside-ca", "project_id": "proj-eastside", "name": "Construction Administration", "fee": 31500, "budget_hours": 200, "pct_complete": 0, "sequence": 4},
    # Overlook Terrace Multifamily — just started
    {"id": "ph-overlook-sd", "project_id": "proj-overlook", "name": "Schematic Design", "fee": 63000, "budget_hours": 480, "pct_complete": 20, "sequence": 1},
    {"id": "ph-overlook-dd", "project_id": "proj-overlook", "name": "Design Development", "fee": 84000, "budget_hours": 640, "pct_complete": 0, "sequence": 2},
    {"id": "ph-overlook-cd", "project_id": "proj-overlook", "name": "Construction Documents", "fee": 210000, "budget_hours": 1300, "pct_complete": 0, "sequence": 3},
    {"id": "ph-overlook-ca", "project_id": "proj-overlook", "name": "Construction Administration", "fee": 63000, "budget_hours": 400, "pct_complete": 0, "sequence": 4},
    # ĒSO Office Buildout — completed
    {"id": "ph-eso-office-sd", "project_id": "proj-eso-office", "name": "Schematic Design", "fee": 11250, "budget_hours": 90, "pct_complete": 100, "sequence": 1},
    {"id": "ph-eso-office-dd", "project_id": "proj-eso-office", "name": "Design Development", "fee": 15000, "budget_hours": 120, "pct_complete": 100, "sequence": 2},
    {"id": "ph-eso-office-cd", "project_id": "proj-eso-office", "name": "Construction Documents", "fee": 37500, "budget_hours": 250, "pct_complete": 100, "sequence": 3},
    {"id": "ph-eso-office-ca", "project_id": "proj-eso-office", "name": "Construction Administration", "fee": 11250, "budget_hours": 75, "pct_complete": 100, "sequence": 4},
]

# Planned hours for the upcoming week. Sam is intentionally overloaded and
# Devon intentionally under-planned, so Team Needed has something to flag.
ALLOCATIONS = [
    {"id": "alloc-1", "person_id": "ppl-jordan", "project_id": "proj-willow", "week_of": "2026-08-10", "planned_hours": 10, "pace": None},
    {"id": "alloc-2", "person_id": "ppl-jordan", "project_id": "proj-marfa", "week_of": "2026-08-10", "planned_hours": 8, "pace": None},
    {"id": "alloc-3", "person_id": "ppl-jordan", "project_id": "proj-overlook", "week_of": "2026-08-10", "planned_hours": 6, "pace": None},
    {"id": "alloc-4", "person_id": "ppl-priya", "project_id": "proj-willow", "week_of": "2026-08-10", "planned_hours": 24, "pace": None},
    {"id": "alloc-5", "person_id": "ppl-priya", "project_id": "proj-baker", "week_of": "2026-08-10", "planned_hours": 14, "pace": None},
    {"id": "alloc-6", "person_id": "ppl-alex", "project_id": "proj-rosedale", "week_of": "2026-08-10", "planned_hours": 30, "pace": None},
    {"id": "alloc-7", "person_id": "ppl-alex", "project_id": "proj-pecan", "week_of": "2026-08-10", "planned_hours": 8, "pace": None},
    {"id": "alloc-8", "person_id": "ppl-morgan", "project_id": "proj-baker", "week_of": "2026-08-10", "planned_hours": 20, "pace": None},
    {"id": "alloc-9", "person_id": "ppl-morgan", "project_id": "proj-eastside", "week_of": "2026-08-10", "planned_hours": 16, "pace": None},
    {"id": "alloc-10", "person_id": "ppl-sam", "project_id": "proj-eastside", "week_of": "2026-08-10", "planned_hours": 28, "pace": None},
    {"id": "alloc-11", "person_id": "ppl-sam", "project_id": "proj-overlook", "week_of": "2026-08-10", "planned_hours": 20, "pace": None},
    {"id": "alloc-12", "person_id": "ppl-devon", "project_id": "proj-overlook", "week_of": "2026-08-10", "planned_hours": 12, "pace": None},
    # week_of 2026-07-27 — a past week that also has logged actuals below
    # (week_ending 2026-07-31, the Friday of the same Mon-Fri week), so
    # Time Allocation has one real overlapping week to compare planned vs.
    # actual on, not just three disjoint single-series weeks.
    {"id": "alloc-13", "person_id": "ppl-jordan", "project_id": "proj-willow", "week_of": "2026-07-27", "planned_hours": 10, "pace": None},
    {"id": "alloc-14", "person_id": "ppl-jordan", "project_id": "proj-overlook", "week_of": "2026-07-27", "planned_hours": 8, "pace": None},
    {"id": "alloc-15", "person_id": "ppl-priya", "project_id": "proj-willow", "week_of": "2026-07-27", "planned_hours": 24, "pace": None},
    {"id": "alloc-16", "person_id": "ppl-priya", "project_id": "proj-baker", "week_of": "2026-07-27", "planned_hours": 12, "pace": None},
    {"id": "alloc-17", "person_id": "ppl-alex", "project_id": "proj-rosedale", "week_of": "2026-07-27", "planned_hours": 34, "pace": None},
    {"id": "alloc-18", "person_id": "ppl-morgan", "project_id": "proj-eastside", "week_of": "2026-07-27", "planned_hours": 22, "pace": None},
    {"id": "alloc-19", "person_id": "ppl-morgan", "project_id": "proj-baker", "week_of": "2026-07-27", "planned_hours": 10, "pace": None},
    {"id": "alloc-20", "person_id": "ppl-sam", "project_id": "proj-eastside", "week_of": "2026-07-27", "planned_hours": 30, "pace": None},
    {"id": "alloc-21", "person_id": "ppl-sam", "project_id": "proj-overlook", "week_of": "2026-07-27", "planned_hours": 8, "pace": None},
    {"id": "alloc-22", "person_id": "ppl-devon", "project_id": "proj-overlook", "week_of": "2026-07-27", "planned_hours": 12, "pace": None},
]

# Actual logged hours for two weeks that already happened. Deliberately
# doesn't match ALLOCATIONS exactly — planned vs. actual should diverge a
# little, same as real life.
TIME_ENTRIES = [
    # week ending 2026-07-24
    {"id": "te-1", "person_id": "ppl-jordan", "project_id": "proj-willow", "phase_id": "ph-willow-dd", "week_ending": "2026-07-24", "hours": 9, "source": "eow"},
    {"id": "te-2", "person_id": "ppl-jordan", "project_id": "proj-marfa", "phase_id": "ph-marfa-dd", "week_ending": "2026-07-24", "hours": 7, "source": "eow"},
    {"id": "te-3", "person_id": "ppl-priya", "project_id": "proj-willow", "phase_id": "ph-willow-dd", "week_ending": "2026-07-24", "hours": 26, "source": "eow"},
    {"id": "te-4", "person_id": "ppl-priya", "project_id": "proj-baker", "phase_id": "ph-baker-sd", "week_ending": "2026-07-24", "hours": 12, "source": "eow"},
    {"id": "te-5", "person_id": "ppl-alex", "project_id": "proj-rosedale", "phase_id": "ph-rosedale-cd", "week_ending": "2026-07-24", "hours": 33, "source": "eow"},
    {"id": "te-6", "person_id": "ppl-alex", "project_id": "proj-pecan", "phase_id": "ph-pecan-ca", "week_ending": "2026-07-24", "hours": 6, "source": "eow"},
    {"id": "te-7", "person_id": "ppl-morgan", "project_id": "proj-baker", "phase_id": "ph-baker-sd", "week_ending": "2026-07-24", "hours": 18, "source": "eow"},
    {"id": "te-8", "person_id": "ppl-morgan", "project_id": "proj-eastside", "phase_id": "ph-eastside-cd", "week_ending": "2026-07-24", "hours": 19, "source": "eow"},
    {"id": "te-9", "person_id": "ppl-sam", "project_id": "proj-eastside", "phase_id": "ph-eastside-cd", "week_ending": "2026-07-24", "hours": 31, "source": "eow"},
    {"id": "te-10", "person_id": "ppl-sam", "project_id": "proj-overlook", "phase_id": "ph-overlook-sd", "week_ending": "2026-07-24", "hours": 14, "source": "eow"},
    {"id": "te-11", "person_id": "ppl-devon", "project_id": "proj-overlook", "phase_id": "ph-overlook-sd", "week_ending": "2026-07-24", "hours": 10, "source": "eow"},
    # week ending 2026-07-31
    {"id": "te-12", "person_id": "ppl-jordan", "project_id": "proj-willow", "phase_id": "ph-willow-dd", "week_ending": "2026-07-31", "hours": 11, "source": "eow"},
    {"id": "te-13", "person_id": "ppl-jordan", "project_id": "proj-overlook", "phase_id": "ph-overlook-sd", "week_ending": "2026-07-31", "hours": 6, "source": "eow"},
    {"id": "te-14", "person_id": "ppl-priya", "project_id": "proj-willow", "phase_id": "ph-willow-dd", "week_ending": "2026-07-31", "hours": 22, "source": "eow"},
    {"id": "te-15", "person_id": "ppl-priya", "project_id": "proj-baker", "phase_id": "ph-baker-sd", "week_ending": "2026-07-31", "hours": 16, "source": "eow"},
    {"id": "te-16", "person_id": "ppl-alex", "project_id": "proj-rosedale", "phase_id": "ph-rosedale-cd", "week_ending": "2026-07-31", "hours": 36, "source": "eow"},
    {"id": "te-17", "person_id": "ppl-morgan", "project_id": "proj-eastside", "phase_id": "ph-eastside-cd", "week_ending": "2026-07-31", "hours": 24, "source": "eow"},
    {"id": "te-18", "person_id": "ppl-morgan", "project_id": "proj-baker", "phase_id": "ph-baker-sd", "week_ending": "2026-07-31", "hours": 10, "source": "eow"},
    {"id": "te-19", "person_id": "ppl-sam", "project_id": "proj-eastside", "phase_id": "ph-eastside-cd", "week_ending": "2026-07-31", "hours": 29, "source": "eow"},
    {"id": "te-20", "person_id": "ppl-sam", "project_id": "proj-overlook", "phase_id": "ph-overlook-sd", "week_ending": "2026-07-31", "hours": 9, "source": "eow"},
    {"id": "te-21", "person_id": "ppl-devon", "project_id": "proj-overlook", "phase_id": "ph-overlook-sd", "week_ending": "2026-07-31", "hours": 14, "source": "eow"},
]

ACTIONS = [
    {"id": "act-1", "project_id": "proj-rosedale", "raised_by": "ppl-alex", "kind": "ask", "body": "Need the client's decision on the exterior cladding sample before CD set can finalize the wall sections.", "direction": None, "needed_by": "2026-08-12", "priority": "Urgent", "status": "open", "raised_on": "2026-08-01"},
    {"id": "act-2", "project_id": "proj-eastside", "raised_by": "ppl-sam", "kind": "ask", "body": "Structural engineer needs confirmation on the mezzanine live-load assumption to close out CD.", "direction": None, "needed_by": "2026-08-15", "priority": "This week", "status": "open", "raised_on": "2026-07-30"},
    {"id": "act-3", "project_id": "proj-marfa", "raised_by": "ppl-jordan", "kind": "fyi", "body": "Client is traveling through mid-August — DD review meeting will likely slip a week.", "direction": None, "needed_by": None, "priority": None, "status": "open", "raised_on": "2026-08-02"},
    {"id": "act-4", "project_id": "proj-baker", "raised_by": "ppl-morgan", "kind": "ask", "body": "Health department wants the kitchen hood layout confirmed before SD can be considered complete.", "direction": None, "needed_by": "2026-08-20", "priority": "When available", "status": "open", "raised_on": "2026-08-03"},
    {"id": "act-5", "project_id": "proj-overlook", "raised_by": "ppl-devon", "kind": "fyi", "body": "City pre-application meeting is scheduled for 8/18 — no action needed yet.", "direction": None, "needed_by": None, "priority": None, "status": "open", "raised_on": "2026-08-04"},
]

FLAGS = [
    {"id": "flag-1", "project_id": "proj-eastside", "person_id": "ppl-sam", "phase_id": "ph-eastside-cd", "rule": "phase_over_budget_hours", "severity": "critical", "body": "CD phase is at 95% of budgeted hours with structural coordination still open — likely to go over.", "status": "open", "raised_on": "2026-08-01T09:00:00Z"},
    {"id": "flag-2", "project_id": "proj-rosedale", "person_id": "ppl-alex", "phase_id": "ph-rosedale-cd", "rule": "phase_over_budget_hours", "severity": "info", "body": "CD phase is at 85% of budgeted hours — worth watching, not critical yet.", "status": "open", "raised_on": "2026-08-01T09:05:00Z"},
]

MILESTONES = [
    {"id": "ms-1", "project_id": "proj-rosedale", "phase_id": "ph-rosedale-cd", "label": "Permit set submittal", "due_date": "2026-08-14", "status": "open", "is_key": True, "completed_on": None, "owner_id": "ppl-alex"},
    {"id": "ms-2", "project_id": "proj-eastside", "phase_id": "ph-eastside-cd", "label": "100% CD milestone", "due_date": "2026-08-22", "status": "open", "is_key": True, "completed_on": None, "owner_id": "ppl-sam"},
    {"id": "ms-3", "project_id": "proj-baker", "phase_id": "ph-baker-sd", "label": "Client SD approval", "due_date": "2026-07-28", "status": "open", "is_key": False, "completed_on": None, "owner_id": "ppl-morgan"},
    {"id": "ms-4", "project_id": "proj-marfa", "phase_id": "ph-marfa-dd", "label": "DD progress review", "due_date": "2026-08-18", "status": "open", "is_key": False, "completed_on": None, "owner_id": "ppl-jordan"},
    {"id": "ms-5", "project_id": "proj-overlook", "phase_id": "ph-overlook-sd", "label": "City pre-application meeting", "due_date": "2026-08-18", "status": "open", "is_key": False, "completed_on": None, "owner_id": "ppl-devon"},
    {"id": "ms-6", "project_id": "proj-pecan", "phase_id": "ph-pecan-ca", "label": "Final inspection walk", "due_date": "2026-07-30", "status": "completed", "is_key": True, "completed_on": "2026-07-29", "owner_id": "ppl-alex"},
]


def _phase_burn_rows():
    """Reconstructs v_phase_burn's SQL over the fixture data above (same
    logic as the view in 001_base_schema.sql)."""
    projects_by_id = {p["id"]: p for p in PROJECTS}
    people_by_id = {p["id"]: p for p in PEOPLE}
    cost_rate_by_role = {r["role"]: r["hourly_rate"] for r in RATES if r["rate_type"] == "cost"}

    rows = []
    for ph in PHASES:
        entries = [t for t in TIME_ENTRIES if t["phase_id"] == ph["id"]]
        accrued_hours = sum(t["hours"] for t in entries)
        budget_hours = ph["budget_hours"]
        fee_burn = (ph["fee"] * accrued_hours / budget_hours) if budget_hours else None
        cost_burn = sum(
            t["hours"] * cost_rate_by_role.get(people_by_id[t["person_id"]]["role"], 0)
            for t in entries
        )
        rows.append({
            "phase_id": ph["id"],
            "project": projects_by_id[ph["project_id"]]["name"],
            "phase": ph["name"],
            "budget_hours": budget_hours,
            "fee": ph["fee"],
            "accrued_hours": accrued_hours,
            "fee_burn": fee_burn,
            "cost_burn": cost_burn,
        })
    return rows


def _person_week_rows():
    """Reconstructs v_person_week's SQL over the fixture data above."""
    people_by_id = {p["id"]: p for p in PEOPLE}
    totals = {}
    for t in TIME_ENTRIES:
        key = (t["person_id"], t["week_ending"])
        totals[key] = totals.get(key, 0) + t["hours"]

    rows = []
    for (person_id, week_ending), logged_hours in totals.items():
        person = people_by_id[person_id]
        rows.append({
            "full_name": person["full_name"],
            "week_ending": week_ending,
            "logged_hours": logged_hours,
            "weekly_capacity": person["weekly_capacity"],
            "utilization_pct": round(logged_hours / person["weekly_capacity"] * 100, 1),
        })
    return rows


V_PHASE_BURN = _phase_burn_rows()
V_PERSON_WEEK = _person_week_rows()

TABLES = {
    "people": PEOPLE,
    "rates": RATES,
    "projects": PROJECTS,
    "phases": PHASES,
    "allocations": ALLOCATIONS,
    "time_entries": TIME_ENTRIES,
    "actions": ACTIONS,
    "flags": FLAGS,
    "milestones": MILESTONES,
    "v_phase_burn": V_PHASE_BURN,
    "v_person_week": V_PERSON_WEEK,
}
