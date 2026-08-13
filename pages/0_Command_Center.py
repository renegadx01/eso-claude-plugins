"""Maggie's weekly command center — the 8 MKW Rollup sections, live from Supabase.

Follows the exact section order from EOW_MKW_Rollup_TEMPLATE.md:
  1 MKW Actions          4 Milestone Timeline
  2 Calendar             5 Watch Items & Flags
  3 Project Status Dash  6 Wins  7 Team Snapshot  8 Hours Reconciliation
"""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from lib.auth import get_authed_client
from lib.branding import brand_header

PRIORITY_ORDER = {"Urgent": 0, "This week": 1, "When available": 2}
PRIORITY_EMOJI = {"Urgent": "🔴", "This week": "🟡", "When available": "🟢"}

# Budget scale mirrors MKW PDF color key: 1 On Track → 4 Critical
BUDGET_OPTIONS = ["1 · On Track", "2 · Monitor", "3 · Concern", "4 · Critical"]
_HEALTH_TO_BUDGET = {
    "on_track": "1 · On Track",
    "monitor":  "2 · Monitor",
    "concern":  "3 · Concern",
    "critical": "4 · Critical",
}
_BUDGET_TO_HEALTH = {v: k for k, v in _HEALTH_TO_BUDGET.items()}

brand_header("MKW — Command Center")
st.caption("Eight-section rollup · live from Supabase · Maggie sets budget status here")

client = get_authed_client()

# ── Week selector ─────────────────────────────────────────────────────────────
weeks_raw = client.table("allocations").select("week_of").execute().data
if not weeks_raw:
    st.info("No EOW data yet — have the team submit via EOW Submit first.")
    st.stop()

week_options = sorted({r["week_of"] for r in weeks_raw}, reverse=True)
week = st.selectbox("Planning week of", week_options, key="cmd_week")

# Derive Friday of planning week — stored as project_health.week_ending
week_dt     = date.fromisoformat(week)
week_friday = (week_dt + timedelta(days=4)).isoformat()

# ── Fetch all data ─────────────────────────────────────────────────────────────
projects_raw = (
    client.table("projects")
    .select("id, name, client_name, status, phases!phases_project_id_fkey(name, pct_complete)")
    .eq("status", "active")
    .order("name")
    .execute()
    .data
)

allocs_raw = (
    client.table("allocations")
    .select("project_id, planned_hours, people(id, full_name, role, weekly_capacity)")
    .eq("week_of", week)
    .execute()
    .data
)

actions_raw = (
    client.table("actions")
    .select("id, project_id, kind, body, priority, needed_by, projects(name), people(full_name)")
    .eq("status", "open")
    .execute()
    .data
)

flags_raw = (
    client.table("flags")
    .select("id, project_id, rule, severity, body, raised_on, projects(name)")
    .eq("status", "open")
    .execute()
    .data
)

milestones_raw = (
    client.table("milestones")
    .select("id, project_id, label, due_date, is_key, projects(name)")
    .neq("status", "completed")
    .order("due_date")
    .execute()
    .data
)

try:
    health_raw = (
        client.table("project_health")
        .select("project_id, health, note")
        .eq("week_ending", week_friday)
        .execute()
        .data
    )
    health_table_ok = True
except Exception:
    health_raw = []
    health_table_ok = False

# ── Indexes ───────────────────────────────────────────────────────────────────
allocs_by_proj: dict[str, list] = {}
for a in allocs_raw:
    allocs_by_proj.setdefault(a["project_id"], []).append(a)

next_ms: dict[str, dict] = {}
lever_ms: list[dict] = []
for m in milestones_raw:
    pid = m["project_id"]
    if pid not in next_ms:
        next_ms[pid] = m
    if m.get("is_key"):
        lever_ms.append(m)

health_by_proj: dict[str, dict] = {h["project_id"]: h for h in health_raw}
proj_by_id:    dict[str, dict] = {p["id"]: p for p in projects_raw}

for a in actions_raw:
    a["_project"] = (a.get("projects") or {}).get("name")
    a["_person"]  = (a.get("people")   or {}).get("full_name")
for f in flags_raw:
    f["_project"] = (f.get("projects") or {}).get("name")

# ── Firm Pulse ────────────────────────────────────────────────────────────────
st.divider()
p1, p2, p3, p4 = st.columns(4)
n_projects = len(projects_raw)
n_people   = len({a["people"]["id"] for a in allocs_raw if a.get("people")})
total_hrs  = sum(a["planned_hours"] for a in allocs_raw)
n_actions  = sum(1 for a in actions_raw if a.get("kind") in ("ask", "action"))
n_critical = sum(1 for f in flags_raw if f.get("severity") == "critical")

p1.metric("Active projects", n_projects)
p2.metric("Total planned hrs", f"{total_hrs}h")
p3.metric("MKW actions open", n_actions,
          delta="need a decision" if n_actions else "all clear",
          delta_color="inverse" if n_actions else "normal")
p4.metric("Critical flags", n_critical,
          delta="review" if n_critical else "none",
          delta_color="inverse" if n_critical else "normal")

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# 1. MKW ACTIONS
# ═════════════════════════════════════════════════════════════════════════════
st.header("1. MKW Actions")
st.caption(
    "**Action Required** = Maggie must decide or do something — sorted 🔴 Urgent first.  "
    "**FYI / Awareness** = no decision needed."
)

required_rows = sorted(
    [a for a in actions_raw if a.get("kind") in ("ask", "action")],
    key=lambda a: PRIORITY_ORDER.get(a.get("priority"), 9),
)
fyi_rows = [a for a in actions_raw if a.get("kind") == "fyi"]

st.subheader("Action Required")
if not required_rows:
    st.success("No actions requiring a decision this week.")
else:
    st.dataframe(
        pd.DataFrame([{
            "":        PRIORITY_EMOJI.get(a.get("priority"), "⚪"),
            "Project": a["_project"] or "—",
            "Ask":     a.get("body") or "—",
            "From":    a["_person"] or "—",
            "By":      a.get("needed_by") or "—",
        } for a in required_rows]),
        hide_index=True, width="stretch",
    )

st.subheader("FYI / Awareness")
if not fyi_rows:
    st.caption("No FYIs this week.")
else:
    st.dataframe(
        pd.DataFrame([{
            "Project": a["_project"] or "—",
            "Note":    a.get("body") or "—",
            "From":    a["_person"] or "—",
        } for a in fyi_rows]),
        hide_index=True, width="stretch",
    )

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# 2. MKW CALENDAR
# ═════════════════════════════════════════════════════════════════════════════
st.header("2. MKW Calendar")
st.info(
    "Maggie's own meetings and reviews for the coming week are not yet stored in "
    "Supabase. Once a `calendar_items` table is added, this section populates "
    "automatically. For now, add calendar context manually in the note below.",
    icon="📅",
)
with st.expander("Add a calendar note for this week"):
    st.text_area(
        "Calendar / meetings note",
        key="cal_note",
        placeholder="e.g. Tue 8/12 — Diocese SD review 1h · Thu 8/14 — Primm DD walkthrough 2h",
        height=80,
        label_visibility="collapsed",
    )

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# 3. PROJECT STATUS DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
st.header("3. Project Status Dashboard")
st.caption(
    "Phase · Budget (1 On Track → 4 Critical) · Next Milestone.  "
    "Set Budget status here — saves to Supabase when you click Save.  "
    "Blocked / lever projects surface in Section 5, not here."
)

if not health_table_ok:
    st.warning(
        "Apply migration **005_financials_and_health.sql** in Supabase to enable "
        "Budget status editing. Showing read-only until then."
    )

if not projects_raw:
    st.info("No active projects.")
else:
    # Build display rows, capturing original Budget for change detection
    dashboard_rows = []
    for p in projects_raw:
        pid     = p["id"]
        phases  = p.get("phases") or []
        phase_s = " / ".join(ph["name"] for ph in phases) if phases else "—"
        ms      = next_ms.get(pid)
        ms_s    = f"{ms['label']}  ·  {ms['due_date']}" if ms else "—"
        h       = health_by_proj.get(pid, {}).get("health", "")
        budget  = _HEALTH_TO_BUDGET.get(h, "1 · On Track")
        dashboard_rows.append({
            "_id":           pid,
            "Project":       p["name"],
            "Phase":         phase_s,
            "Budget":        budget,
            "Next Milestone": ms_s,
        })

    orig_budgets = {r["_id"]: r["Budget"] for r in dashboard_rows}
    display_df   = pd.DataFrame(dashboard_rows).drop(columns=["_id"])

    if health_table_ok:
        edited_df = st.data_editor(
            display_df,
            column_config={
                "Budget": st.column_config.SelectboxColumn(
                    "Budget",
                    options=BUDGET_OPTIONS,
                    required=True,
                    width="medium",
                ),
                "Project":        st.column_config.TextColumn(disabled=True),
                "Phase":          st.column_config.TextColumn(disabled=True),
                "Next Milestone": st.column_config.TextColumn(disabled=True),
            },
            hide_index=True,
            width="stretch",
            key="proj_dash_editor",
        )

        if st.button("Save budget status", type="primary"):
            errors = []
            saved  = 0
            for i, row in edited_df.iterrows():
                pid    = dashboard_rows[i]["_id"]
                budget = row["Budget"]
                health = _BUDGET_TO_HEALTH.get(budget, "on_track")
                if health_table_ok:
                    try:
                        client.table("project_health").upsert(
                            {"project_id": pid, "week_ending": week_friday,
                             "health": health, "note": None},
                            on_conflict="project_id,week_ending",
                        ).execute()
                        saved += 1
                    except Exception as e:
                        errors.append(f"{row['Project']}: {e}")
            if errors:
                for err in errors:
                    st.error(err)
            else:
                st.success(f"Budget status saved for {saved} projects — week ending {week_friday}.")
                st.rerun()
    else:
        st.dataframe(display_df, hide_index=True, width="stretch")

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# 4. MILESTONE TIMELINE
# ═════════════════════════════════════════════════════════════════════════════
st.header("4. Milestone Timeline")
st.caption("All open milestones sorted by due date. ★ = lever — project is blocked until this completes.")

if not milestones_raw:
    st.info("No open milestones across active projects.")
else:
    ms_df = pd.DataFrame([{
        "Due":       m["due_date"],
        "★":         "★" if m.get("is_key") else "",
        "Project":   (m.get("projects") or {}).get("name", "—"),
        "Milestone": m["label"],
    } for m in milestones_raw])
    st.dataframe(ms_df, hide_index=True, width="stretch")

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# 5. WATCH ITEMS & FLAGS
# ═════════════════════════════════════════════════════════════════════════════
st.header("5. Watch Items & Flags")
st.caption("Barriers, risks, and open lever milestones (⚑ Blocked). Milestone slip tracking coming once slip history is stored.")

has_anything = bool(flags_raw or lever_ms)
if not has_anything:
    st.success("No open flags or blockers.")
else:
    watch_rows = []

    for m in lever_ms:
        pname = (m.get("projects") or {}).get("name", "Unknown")
        watch_rows.append({
            "Area":   f"⚑ Blocked",
            "Project": pname,
            "Item":   f"Waiting on: **{m['label']}** (due {m['due_date']})",
        })

    for f in flags_raw:
        sev   = f.get("severity", "info")
        icon  = "🚨" if sev == "critical" else "⚠️"
        watch_rows.append({
            "Area":    icon + " " + (f.get("rule") or sev).capitalize(),
            "Project": f["_project"] or "—",
            "Item":    f.get("body") or "—",
        })

    if watch_rows:
        st.dataframe(pd.DataFrame(watch_rows), hide_index=True, width="stretch")

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# 6. WINS THIS WEEK
# ═════════════════════════════════════════════════════════════════════════════
st.header("6. Wins This Week")
st.info(
    "Wins and completed milestones aren't yet written to Supabase — they live "
    "in each person's EOW sidecar JSON (field `wins` / completed milestone "
    "records). Once a `wins` table or a `completed_at` column on `milestones` "
    "is added, this section populates automatically.",
    icon="🏆",
)

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# 7. PROJECT SNAPSHOT — STAFFING & FOCUS NEXT WEEK
# ═════════════════════════════════════════════════════════════════════════════
st.header("7. Project Snapshot — Staffing Next Week")
st.caption(
    "Who is on each project next week and how many hours — grouped by project, "
    "not by person. Focus lines come from EOW PDFs and aren't in Supabase yet."
)

if not projects_raw:
    st.info("No active projects.")
else:
    snap_rows = []
    for p in projects_raw:
        pid   = p["id"]
        team  = allocs_by_proj.get(pid, [])
        if not team:
            continue
        team_str = "  ·  ".join(
            f"{a['people']['full_name'].split()[0]} ({a['planned_hours']}h)"
            for a in sorted(team, key=lambda x: -x["planned_hours"])
            if a.get("people")
        )
        total_proj_hrs = sum(a["planned_hours"] for a in team)
        snap_rows.append({
            "Project":     p["name"],
            "Staff on deck": team_str or "—",
            "Total hrs":   total_proj_hrs,
            "Focus":       "— (from EOW PDF)",
        })

    if snap_rows:
        st.dataframe(
            pd.DataFrame(snap_rows).sort_values("Total hrs", ascending=False),
            hide_index=True, width="stretch",
        )
    else:
        st.info("No allocations for active projects this week.")

st.divider()

# ═════════════════════════════════════════════════════════════════════════════
# 8. HOURS BY PROJECT
# ═════════════════════════════════════════════════════════════════════════════
st.header("8. Hours by Project")
st.caption(
    "Planned hours per project this week from EOW allocations. "
    "Actual logged hours (`time_entries`) are empty until the team starts "
    "logging — that column will populate automatically when they do."
)

if not allocs_raw:
    st.info(f"No allocations for week of {week}.")
else:
    proj_hrs: dict[str, float] = {}
    proj_reported: dict[str, float] = {}

    # Try to pull reported hours by project from time_entries
    try:
        te_raw = (
            client.table("time_entries")
            .select("hours, project_id")
            .eq("week_ending", week_friday)
            .execute()
            .data
        )
        for te in te_raw:
            pid = te.get("project_id")
            if pid:
                proj_reported[pid] = proj_reported.get(pid, 0) + te["hours"]
    except Exception:
        te_raw = []

    for a in allocs_raw:
        pid = a["project_id"]
        proj_hrs[pid] = proj_hrs.get(pid, 0) + a["planned_hours"]

    hours_rows = []
    for p in projects_raw:
        pid     = p["id"]
        planned = proj_hrs.get(pid, 0)
        if not planned:
            continue
        reported = proj_reported.get(pid)
        hours_rows.append({
            "Project":      p["name"],
            "Planned hrs":  planned,
            "Reported hrs": f"{reported:g}h" if reported is not None else "— (not logged)",
        })

    hours_rows.sort(key=lambda r: -r["Planned hrs"])
    total_planned = sum(r["Planned hrs"] for r in hours_rows)
    hours_rows.append({
        "Project":      "Total",
        "Planned hrs":  total_planned,
        "Reported hrs": "",
    })

    st.dataframe(pd.DataFrame(hours_rows), hide_index=True, width="stretch")
