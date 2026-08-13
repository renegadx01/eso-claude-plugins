import pandas as pd
import streamlit as st

from lib.auth import get_authed_client
from lib.branding import brand_header

brand_header("Team Needed — capacity demand vs. supply, by role")
st.caption(
    "Problem it answers: are we over- or under-staffed by role, based on what "
    "people have actually planned against their weekly capacity. This uses "
    "`allocations` + `people`, not a pipeline/hiring model (that entity "
    "doesn't exist in Supabase yet — see PLATFORM_MODEL.md Phase 5)."
)

client = get_authed_client()

people = pd.DataFrame(
    client.table("people").select("id, full_name, role, weekly_capacity").eq("active", True).execute().data
)
if people.empty:
    st.info("No active people.")
    st.stop()

weeks_df = pd.DataFrame(client.table("allocations").select("week_of").execute().data)
if weeks_df.empty:
    st.info("No allocations yet — nothing to compare against capacity.")
    st.stop()

week_options = sorted(weeks_df["week_of"].unique(), reverse=True)
week = st.selectbox("Week of", week_options)

allocations = pd.DataFrame(
    client.table("allocations").select("person_id, planned_hours").eq("week_of", week).execute().data
)
# Sum each person's allocations across all their projects *before* merging —
# otherwise a person staffed on 2+ projects gets one row per project, which
# double-counts their weekly_capacity in the "by role" supply total and
# hides them from "individuals over capacity" (each row compared to full
# capacity individually, instead of their total planned hours).
if allocations.empty:
    alloc_by_person = pd.DataFrame(columns=["person_id", "planned_hours"])
else:
    alloc_by_person = allocations.groupby("person_id", as_index=False)["planned_hours"].sum()

merged = people.merge(alloc_by_person, left_on="id", right_on="person_id", how="left")
merged["planned_hours"] = merged["planned_hours"].fillna(0)

st.subheader("By role")
by_role = merged.groupby("role", as_index=False).agg(
    supply_capacity=("weekly_capacity", "sum"),
    demand_planned=("planned_hours", "sum"),
)
by_role["gap"] = (by_role["demand_planned"] - by_role["supply_capacity"]).round(1)
over_capacity_roles = by_role[by_role["gap"] > 0]

if not over_capacity_roles.empty:
    st.warning(
        "Role(s) with more planned demand than capacity this week: "
        + ", ".join(f"{r.role} ({r.gap:+g} hrs)" for r in over_capacity_roles.itertuples())
    )

st.bar_chart(by_role.set_index("role")[["supply_capacity", "demand_planned"]], stack=False)
st.dataframe(by_role, width="stretch", hide_index=True)

st.subheader("Individuals over their own capacity this week")
merged["over_under"] = (merged["planned_hours"] - merged["weekly_capacity"]).round(1)
overloaded = merged[merged["over_under"] > 0].sort_values("over_under", ascending=False)
if overloaded.empty:
    st.caption("Nobody is planned over their weekly capacity this week.")
else:
    st.dataframe(
        overloaded[["full_name", "role", "planned_hours", "weekly_capacity", "over_under"]],
        width="stretch", hide_index=True,
    )
