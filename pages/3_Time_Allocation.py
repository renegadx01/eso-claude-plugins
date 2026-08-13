import pandas as pd
import streamlit as st

from lib.auth import get_authed_client
from lib.branding import brand_header

brand_header("Time Allocation — planned vs. actual, by person")
st.caption(
    "Problem it answers: is what people said they'd work on next week "
    "matching what they actually logged? **Planned** comes from `allocations` "
    "(week_of), **Actual** comes from `time_entries` (week_ending) — those are "
    "different week fields by design (forward plan vs. logged actual), so "
    "treat this as two trend lines to compare, not a single reconciled number."
)

client = get_authed_client()

people_df = pd.DataFrame(client.table("people").select("id, full_name").order("full_name").execute().data)
if people_df.empty:
    st.info("No people yet.")
    st.stop()

selected = st.multiselect("Filter by person", people_df["full_name"], default=list(people_df["full_name"]))
selected_ids = people_df.loc[people_df["full_name"].isin(selected), "id"].tolist()

if not selected_ids:
    st.info("Pick at least one person.")
    st.stop()

actual = pd.DataFrame(
    client.table("time_entries")
    .select("week_ending, hours, people(full_name)")
    .in_("person_id", selected_ids)
    .execute()
    .data
)
planned = pd.DataFrame(
    client.table("allocations")
    .select("week_of, planned_hours, people(full_name)")
    .in_("person_id", selected_ids)
    .execute()
    .data
)

if actual.empty and planned.empty:
    st.info("No allocations or time entries for the selected people yet.")
    st.stop()


def _week_start(date_col):
    """Monday of the week containing each date. week_of (allocations) is
    already a Monday; week_ending (time_entries) is a Friday — comparing
    those raw values directly means a week's plan and its own actual never
    share a key, so every week would show only one series. Normalizing both
    to the same week-start date is what actually lets them line up."""
    # "W-SUN" = weeks running Mon-Sun (pandas names a week period after its
    # LAST day) — start_time then gives the Monday. "W-MON" would give the
    # Tuesday-Monday week instead, which is not what we want here.
    return pd.to_datetime(date_col).dt.to_period("W-SUN").dt.start_time.dt.strftime("%Y-%m-%d")


if not actual.empty:
    actual["full_name"] = actual["people"].apply(lambda p: p["full_name"] if p else None)
    actual["week"] = _week_start(actual["week_ending"])
    actual_by_week = actual.groupby("week", as_index=False)["hours"].sum().rename(columns={"hours": "Actual"})
else:
    actual_by_week = pd.DataFrame(columns=["week", "Actual"])

if not planned.empty:
    planned["full_name"] = planned["people"].apply(lambda p: p["full_name"] if p else None)
    planned["week"] = _week_start(planned["week_of"])
    planned_by_week = planned.groupby("week", as_index=False)["planned_hours"].sum().rename(columns={"planned_hours": "Planned"})
else:
    planned_by_week = pd.DataFrame(columns=["week", "Planned"])

combined = pd.merge(actual_by_week, planned_by_week, on="week", how="outer").sort_values("week")
st.subheader("Team total: planned vs. actual, by week")
st.bar_chart(combined.set_index("week"), stack=False)
st.dataframe(combined, width="stretch", hide_index=True)

st.subheader("By person")
if not actual.empty:
    st.write("**Actual hours logged**")
    st.dataframe(
        actual.pivot_table(index="week_ending", columns="full_name", values="hours", aggfunc="sum").fillna(0),
        width="stretch",
    )
if not planned.empty:
    st.write("**Planned hours (next week)**")
    st.dataframe(
        planned.pivot_table(index="week_of", columns="full_name", values="planned_hours", aggfunc="sum").fillna(0),
        width="stretch",
    )
