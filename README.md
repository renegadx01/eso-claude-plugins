# eso-platform-app

Read-only Streamlit dashboard on top of the ĒSO Platform database (Supabase):
capacity (`v_person_week`) and burn (`v_phase_burn`). See `CLAUDE.md` for the
full brief and `eso-claude-plugins/PLATFORM_MODEL.md` (plugin repo) for the
product vision.

## Setup

1. `python -m venv .venv && .venv\Scripts\activate` (Windows) or
   `source .venv/bin/activate` (Mac/Linux).
2. `pip install -r requirements.txt`
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and
   fill in:
   - `SUPABASE_URL` — same project as `eso-platform-supabase`.
   - `SUPABASE_ANON_KEY` — Supabase dashboard -> Project Settings -> API ->
     anon/public key. **Not** the service_role key.
   - `ANTHROPIC_API_KEY` *(optional)* — only needed for the "Ask the Data"
     page. Get one from console.anthropic.com -> API Keys. Leave the
     placeholder in place until you're ready to pay for API usage — the page
     detects that and shows a "not wired up yet" message instead of erroring.
4. Make sure you have a Supabase Auth user: dashboard -> Authentication ->
   Users -> Add User (email + password). There's no self-serve signup yet.
5. `streamlit run app.py`

## Pages

- **EOW Inputs** (`pages/1_EOW_Inputs.py`) — one person's weekly report.
- **MKW Rollup** (`pages/2_MKW_Rollup.py`) — firm-wide weekly view.
- **Time Allocation** (`pages/3_Time_Allocation.py`) — planned vs. actual hours, by person.
- **Burn Rate** (`pages/4_Burn_Rate.py`) — fee/hours vs. budget, by phase.
- **Team Needed** (`pages/5_Team_Needed.py`) — capacity demand vs. supply, by role.
- **Ask the Data** (`pages/6_Ask_the_Data.py`) — Claude-powered natural-language
  assistant over the same tables (see below). Read-only, needs `ANTHROPIC_API_KEY`.

## Ask the Data — use cases

What the assistant can answer today is bounded by what's actually in Supabase
— see `PLATFORM_MODEL.md` (plugin repo) for the full domain model and phased
roadmap. Three tiers:

### Answerable now, with live data

**Capacity** (`v_person_week`)
- "Who's over-allocated this week?"
- "What's Scott Stovall's utilization over the last 4 weeks?"
- "Is anyone under 50% utilization right now?"
- "What's the team's average utilization this week vs. last week?"

**Burn** (`v_phase_burn`)
- "What's the fee burn on Golden Bear vs. its budget?"
- "Which phases are over budget hours?"
- "What's the cost burn on the Deer Crossing schematic design phase?"

**Planned work** (`allocations` — a forward plan, not actuals)
- "What is Hall planning to work on next week?"
- "Which projects have the most planned hours next week?"
- "Is next week's total planned load over or under total firm capacity?"

**Open work / asks / blockers** (`actions`, `flags`)
- "What asks are waiting on a decision, sorted by priority?"
- "What critical flags are open, and on which projects?"
- "Which projects have open flags but no open actions?"

**Milestones**
- "What's the next key milestone across active projects?"
- "Any overdue milestones?"
- "Which active projects have no milestone due in the next 4 weeks?"

**Roster / projects** (`people`, `projects`)
- "List active projects with their client and start date."
- "What roles do we have, and how many people in each?"

### Answerable, but expect the assistant to flag a real gap

These have a real tool and real table behind them, but the data itself is
thin or partial today (per `PLATFORM_STATUS.md`) — a good answer here is the
assistant saying so, not guessing:
- "Did planned hours match what actually got logged last week?" —
  `time_entries` has almost no real data yet; actuals aren't structurally
  captured until Monograph (or the platform itself) is wired up.
- "How does billed compare to logged hours on this project?" — no
  billed-vs-logged distinction exists in the schema yet (a named Phase 2 gap).
- "What's each project's health status (On Track/Monitor/Concern/Critical)?" —
  not in Supabase; still PDF-only, same caveat as the MKW Rollup page.
- "What were this week's Wins?" — narrative text, PDF-only, no table for it.

### Not answerable yet — needs schema from a later roadmap phase

- "Who's Responsible/Accountable for this phase?" — needs the Process
  Framework + RACI tables (Phase 3); not modeled.
- "What target % effort should each role have on this phase?" — same gap.
- "If milestone X slips two weeks, what's the downstream impact on next
  week's workload?" — needs cascade/forecasting logic (Phase 4); only the
  slip itself (`milestone_slips`) is captured, not its ripple effect.
- "What's in the pipeline, and when should we staff for it?" — needs the
  `pipeline` entity (Phase 5); doesn't exist yet.
- "What would utilization look like if we hired one more person?" — needs
  the scenario/plan-version dimension (Phase 5); reserved in the model, not
  built.
- "Which team has the most slack capacity?" — needs a `teams` entity;
  `v_person_week` only rolls up by person today, not team.

## Deploying

Streamlit Community Cloud is the simplest path: point it at this repo, set
`SUPABASE_URL` / `SUPABASE_ANON_KEY` in its secrets UI (same keys as above).
No server to manage.

## Security note

This app never holds the service_role key. It signs users in via Supabase
Auth and queries as them, so Postgres RLS (defined in `eso-platform-supabase`)
is the actual access boundary — see `CLAUDE.md` for a known caveat about RLS
and views.
