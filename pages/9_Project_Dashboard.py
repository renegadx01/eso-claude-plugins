import pandas as pd
import streamlit as st

from lib.auth import get_authed_client
from lib.branding import brand_header

brand_header("Project Dashboard — project-centric view")
st.caption(
    "Projects as the primary entity: who is on each one this week, phase health, "
    "open actions and flags, next milestone. Health badges are set here by Maggie "
    "and feed into the MKW Rollup. Requires migration 005 to be applied for health "
    "saves to persist."
)

client = get_authed_client()

HEALTH_OPTIONS  = ["on_track", "monitor", "concern", "critical"]
HEALTH_EMOJI    = {"on_track": "🟢", "monitor": "🟡", "concern": "🟠", "critical": "🔴"}
HEALTH_LABEL    = {"on_track": "On Track", "monitor": "Monitor",
                   "concern": "Concern", "critical": "Critical"}

# ── week selector ──────────────────────────────────────────────────────────
weeks_df = pd.DataFrame(client.table("allocations").select("week_of").execute().data)
if weeks_df.empty:
    st.info("No allocations yet — submit EOW data first.")
    st.stop()

week_options = sorted(weeks_df["week_of"].unique(), reverse=True)
week = st.selectbox("Week of", week_options, key="proj_dash_week")

# ── fetch all data for this week ───────────────────────────────────────────
projects_raw = (
    client.table("projects")
    .select("id, name, client_name, status, total_fee, phases(name, fee, pct_complete, budget_hours)")
    .eq("status", "active")
    .order("name")
    .execute()
    .data
)

allocs_raw = (
    client.table("allocations")
    .select("project_id, planned_hours, people(full_name, role)")
    .eq("week_of", week)
    .execute()
    .data
)

actions_raw = (
    client.table("actions")
    .select("project_id, kind, priority")
    .eq("status", "open")
    .execute()
    .data
)

flags_raw = (
    client.table("flags")
    .select("project_id, severity")
    .eq("status", "open")
    .execute()
    .data
)

milestones_raw = (
    client.table("milestones")
    .select("project_id, label, due_date, is_key")
    .eq("status", "open")
    .order("due_date")
    .execute()
    .data
)

# ── try to load health assessments (requires migration 005) ────────────────
try:
    health_raw = (
        client.table("project_health")
        .select("project_id, health, note")
        .eq("week_ending", week)
        .execute()
        .data
    )
    health_table_exists = True
except Exception:
    health_raw = []
    health_table_exists = False

# ── index data by project_id ───────────────────────────────────────────────
allocs_by_proj: dict[str, list] = {}
for a in allocs_raw:
    pid = a["project_id"]
    allocs_by_proj.setdefault(pid, []).append(a)

action_counts: dict[str, dict] = {}
for a in actions_raw:
    pid = a["project_id"]
    action_counts.setdefault(pid, {"ask": 0, "fyi": 0})
    action_counts[pid][a.get("kind", "fyi")] = action_counts[pid].get(a.get("kind", "fyi"), 0) + 1

flag_counts: dict[str, dict] = {}
for f in flags_raw:
    pid = f["project_id"]
    flag_counts.setdefault(pid, {"critical": 0, "info": 0})
    flag_counts[pid][f.get("severity", "info")] = flag_counts[pid].get(f.get("severity", "info"), 0) + 1

next_milestone: dict[str, dict] = {}
for m in milestones_raw:
    pid = m["project_id"]
    if pid not in next_milestone:
        next_milestone[pid] = m

health_by_proj: dict[str, dict] = {h["project_id"]: h for h in health_raw}

# ── health edit state ──────────────────────────────────────────────────────
if "health_edits" not in st.session_state:
    st.session_state.health_edits = {}

# ── overview table ─────────────────────────────────────────────────────────
st.subheader("Active Projects")

overview_rows = []
for p in projects_raw:
    pid = p["id"]
    team = allocs_by_proj.get(pid, [])
    total_hrs = sum(a["planned_hours"] for a in team)
    people_list = ", ".join(
        f"{a['people']['full_name'].split()[-1]} ({a['planned_hours']}h)"
        for a in sorted(team, key=lambda x: x["planned_hours"], reverse=True)
        if a.get("people")
    ) or "—"

    phases = p.get("phases") or []
    active_phase = phases[-1]["name"] if phases else "—"
    pct = max((ph.get("pct_complete") or 0) for ph in phases) if phases else 0

    acts = action_counts.get(pid, {})
    flgs = flag_counts.get(pid, {})
    ms = next_milestone.get(pid)

    current_h = health_by_proj.get(pid, {}).get("health", "")
    h_label = (HEALTH_EMOJI.get(current_h, "⚪") + " " + HEALTH_LABEL.get(current_h, "Not set")) if current_h else "⚪ Not set"

    overview_rows.append({
        "project": p["name"],
        "client": p.get("client_name") or "—",
        "phase": active_phase,
        "health": h_label,
        "team this week": people_list,
        "hrs": total_hrs or "—",
        "actions": acts.get("ask", 0) or "—",
        "flags 🔴": flgs.get("critical", 0) or "—",
        "next milestone": ms["label"][:40] + "…" if ms and len(ms["label"]) > 40 else (ms["label"] if ms else "—"),
        "due": ms["due_date"] if ms else "—",
    })

st.dataframe(pd.DataFrame(overview_rows), hide_index=True, width="stretch")

# ── per-project drill-down ─────────────────────────────────────────────────
st.subheader("Project Detail")

if not health_table_exists:
    st.warning(
        "Health assessments require migration **005_financials_and_health.sql** "
        "to be applied in Supabase. The rest of this page works without it."
    )

health_saves = {}

for p in projects_raw:
    pid = p["id"]
    team = allocs_by_proj.get(pid, [])
    current_h = health_by_proj.get(pid, {}).get("health") or st.session_state.health_edits.get(pid)

    emoji = HEALTH_EMOJI.get(current_h, "⚪")
    label = f"{emoji}  {p['name']}"
    if flag_counts.get(pid, {}).get("critical", 0):
        label += "  🚨"

    with st.expander(label, expanded=False):
        col_health, col_meta = st.columns([1, 2])

        with col_health:
            st.caption("HEALTH ASSESSMENT")
            if health_table_exists:
                idx = HEALTH_OPTIONS.index(current_h) if current_h in HEALTH_OPTIONS else 0
                new_h = st.selectbox(
                    "Status",
                    HEALTH_OPTIONS,
                    index=idx,
                    format_func=lambda x: HEALTH_EMOJI[x] + " " + HEALTH_LABEL[x],
                    key=f"health_{pid}",
                    label_visibility="collapsed",
                )
                health_note = st.text_input("Note (optional)", key=f"note_{pid}",
                                            value=health_by_proj.get(pid, {}).get("note") or "")
                health_saves[pid] = {"health": new_h, "note": health_note}
            else:
                h_disp = HEALTH_LABEL.get(current_h, "Not set")
                st.markdown(f"**{emoji} {h_disp}**")
                st.caption("Apply migration 005 to enable editing.")

        with col_meta:
            st.caption("TEAM THIS WEEK")
            if team:
                for a in sorted(team, key=lambda x: x["planned_hours"], reverse=True):
                    if a.get("people"):
                        name = a["people"]["full_name"]
                        role = a["people"]["role"]
                        hrs  = a["planned_hours"]
                        st.markdown(f"- **{name}** _{role}_ — {hrs}h")
            else:
                st.caption("No allocations this week.")

        # phases
        phases = p.get("phases") or []
        if phases:
            st.caption("PHASES")
            phase_rows = []
            for ph in phases:
                pct = ph.get("pct_complete") or 0
                if pct > 1:
                    pct = pct / 100
                phase_rows.append({
                    "phase": ph["name"],
                    "fee": f"${ph['fee']:,.0f}" if ph.get("fee") else "—",
                    "budget hrs": ph.get("budget_hours") or "—",
                    "complete": f"{pct*100:.0f}%",
                })
            st.dataframe(pd.DataFrame(phase_rows), hide_index=True, use_container_width=True)

        # actions
        proj_actions = [a for a in actions_raw if a["project_id"] == pid]
        if proj_actions:
            st.caption(f"OPEN ACTIONS ({len(proj_actions)})")
            for a in proj_actions:
                icon = "🔴" if a.get("priority") == "Urgent" else "🟡"
                st.markdown(f"{icon} {a.get('body') or a.get('kind', '')}")

        # flags
        proj_flags = [f for f in flags_raw if f["project_id"] == pid]
        if proj_flags:
            st.caption(f"OPEN FLAGS ({len(proj_flags)})")
            for f in proj_flags:
                sev = f.get("severity", "info")
                icon = "🚨" if sev == "critical" else "⚠️"
                st.markdown(f"{icon} {f.get('body') or sev}")

        # milestones
        proj_ms = [m for m in milestones_raw if m["project_id"] == pid]
        if proj_ms:
            st.caption("OPEN MILESTONES")
            for m in proj_ms[:3]:
                star = "★ " if m.get("is_key") else ""
                st.markdown(f"- {star}{m['label']} — **{m['due_date']}**")

# ── save health assessments ────────────────────────────────────────────────
if health_table_exists and health_saves:
    st.divider()
    if st.button("Save health assessments", type="primary"):
        session = st.session_state.get("session")
        user_id = None
        if session:
            people_rows = client.table("people").select("id").execute().data
            # rough match — just save without assessed_by if we can't resolve
        errors = []
        for pid, vals in health_saves.items():
            try:
                client.table("project_health").upsert(
                    {
                        "project_id": pid,
                        "week_ending": week,
                        "health": vals["health"],
                        "note": vals["note"] or None,
                    },
                    on_conflict="project_id,week_ending",
                ).execute()
            except Exception as e:
                errors.append(str(e))
        if errors:
            for err in errors:
                st.error(err)
        else:
            st.success(f"Health assessments saved for week of {week}.")
            st.rerun()
