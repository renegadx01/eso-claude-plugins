import pandas as pd
import streamlit as st

from lib.auth import get_authed_client
from lib.branding import brand_header


brand_header("MKW Rollup — firm-wide weekly view")
st.caption(
    "Mirrors the sections of the weekly MKW Rollup PDF, built live from "
    "Supabase instead of the local sidecar files. Sections that don't have a "
    "home in Supabase yet are called out rather than skipped silently."
)

client = get_authed_client()
PRIORITY_ORDER = {"Urgent": 0, "This week": 1, "When available": 2}

# ---- 1. Action Required / FYI ------------------------------------------------
st.header("1. MKW Actions")

actions = pd.DataFrame(
    client.table("actions")
    .select("kind, body, priority, needed_by, direction, projects(name), people(full_name)")
    .eq("status", "open")
    .execute()
    .data
)
if actions.empty:
    st.info("No open actions.")
else:
    actions["project"] = actions["projects"].apply(lambda p: p["name"] if p else None)
    actions["raised_by"] = actions["people"].apply(lambda p: p["full_name"] if p else None)

    required = actions[actions["kind"] == "action"].copy()
    fyis = actions[actions["kind"] == "fyi"].copy()

    st.subheader("Action Required")
    if required.empty:
        st.caption("No actions requiring a decision this week.")
    else:
        required["_sort"] = required["priority"].map(PRIORITY_ORDER).fillna(9)
        required = required.sort_values("_sort")
        st.dataframe(
            required[["priority", "project", "body", "raised_by", "needed_by"]],
            width="stretch", hide_index=True,
        )

    st.subheader("FYI / Awareness")
    if fyis.empty:
        st.caption("No FYIs this week.")
    else:
        st.dataframe(fyis[["project", "body", "raised_by"]], width="stretch", hide_index=True)

# ---- 2. Project Status Dashboard --------------------------------------------
st.header("2. Project Status Dashboard")
projects = pd.DataFrame(
    client.table("projects")
    # projects <-> phases has FKs in both directions (phases.project_id, and
    # projects.current_phase_id) — the !fkey-name hint picks the phases-belong
    # -to-this-project direction, not the other one.
    .select("name, status, phases!phases_project_id_fkey(name)")
    .eq("status", "active")
    .order("name")
    .execute()
    .data
)
if projects.empty:
    st.info("No active projects.")
else:
    projects["current_phase"] = projects["phases"].apply(
        lambda phs: ", ".join(p["name"] for p in phs) if phs else "—"
    )
    projects["health"] = "— not tracked —"
    st.dataframe(projects[["name", "current_phase", "health"]], width="stretch", hide_index=True)
    st.caption(
        "**health** isn't in Supabase yet — the PDF rollup shows On Track / "
        "Monitor / Concern / Critical per project, hand-assessed each week. "
        "Needs a schema decision before it can live here."
    )

# ---- 3. Milestone Timeline (open milestones) --------------------------------
st.header("3. Milestone Timeline")
milestones = pd.DataFrame(
    client.table("milestones")
    .select("label, due_date, is_key, projects(name)")
    .neq("status", "completed")
    .order("due_date")
    .execute()
    .data
)
if milestones.empty:
    st.info("No open milestones.")
else:
    milestones["project"] = milestones["projects"].apply(lambda p: p["name"] if p else None)
    milestones["key"] = milestones["is_key"].map({True: "★", False: ""})
    st.dataframe(milestones[["due_date", "key", "project", "label"]], width="stretch", hide_index=True)

# ---- 4. Watch Items & Flags --------------------------------------------------
st.header("4. Watch Items & Flags")
flags = pd.DataFrame(
    client.table("flags")
    .select("rule, severity, body, projects(name)")
    .eq("status", "open")
    .execute()
    .data
)
if flags.empty:
    st.info("No open flags.")
else:
    flags["project"] = flags["projects"].apply(lambda p: p["name"] if p else None)
    st.dataframe(flags[["severity", "project", "rule", "body"]], width="stretch", hide_index=True)

# ---- 5. Wins / Team Snapshot (gap) ------------------------------------------
st.header("5. Wins & Team Snapshot")
st.warning(
    "Not yet in Supabase: **Wins this week** and each person's **focus next "
    "week** one-liner. Both are narrative text the EOW PDF already captures "
    "per person, per week — they just aren't written to the database. Once "
    "there's a table for them, this section drops straight in."
)

# ---- 6. Hours Reconciliation -------------------------------------------------
st.header("6. Hours Reconciliation")
weeks = pd.DataFrame(client.table("time_entries").select("week_ending").execute().data)
if weeks.empty:
    st.info("No time entries yet — nothing to reconcile.")
else:
    week_options = sorted(weeks["week_ending"].unique(), reverse=True)
    week = st.selectbox("Week ending", week_options)

    reported = pd.DataFrame(
        client.table("time_entries")
        .select("hours, people(id, full_name)")
        .eq("week_ending", week)
        .execute()
        .data
    )
    reported["person_id"] = reported["people"].apply(lambda p: p["id"] if p else None)
    reported["full_name"] = reported["people"].apply(lambda p: p["full_name"] if p else None)
    reported_by_person = reported.groupby(["person_id", "full_name"], as_index=False)["hours"].sum()
    reported_by_person = reported_by_person.rename(columns={"hours": "reported"})

    people = pd.DataFrame(client.table("people").select("id, full_name, weekly_capacity").execute().data)

    merged = people.merge(reported_by_person[["person_id", "reported"]], left_on="id", right_on="person_id", how="left")
    merged["reported"] = merged["reported"].fillna(0)
    merged["utilization_pct"] = (merged["reported"] / merged["weekly_capacity"] * 100).round(1)
    merged["over_under"] = (merged["reported"] - merged["weekly_capacity"]).round(1)

    merged = merged[merged["reported"] > 0].sort_values("full_name")
    if merged.empty:
        st.info(f"No hours reported for week ending {week}.")
    else:
        st.dataframe(
            merged[["full_name", "reported", "weekly_capacity", "utilization_pct", "over_under"]]
            .rename(columns={"weekly_capacity": "capacity", "over_under": "over/under"}),
            width="stretch", hide_index=True,
        )
        st.caption(f"Team total reported: {merged['reported'].sum():g} hrs")
