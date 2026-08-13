import pandas as pd
import streamlit as st

from lib.auth import get_authed_client
from lib.branding import brand_header

brand_header("EOW Inputs — one person, one week")
st.caption(
    "The raw weekly input bucket. Outcomes, look-ahead notes, wins, and focus "
    "are captured in the EOW PDF today but not yet written to Supabase — see "
    "the note at the bottom."
)

client = get_authed_client()

people_df = pd.DataFrame(client.table("people").select("id, full_name").order("full_name").execute().data)
if people_df.empty:
    st.info("No people in the database yet.")
    st.stop()

person_name = st.selectbox("Person", people_df["full_name"])
person_id = people_df.loc[people_df["full_name"] == person_name, "id"].iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Hours reported (actuals)")
    te = pd.DataFrame(
        client.table("time_entries")
        .select("week_ending, hours, projects(name), phases(name)")
        .eq("person_id", person_id)
        .order("week_ending", desc=True)
        .limit(20)
        .execute()
        .data
    )
    if te.empty:
        st.info("No time entries for this person yet.")
    else:
        te["project"] = te["projects"].apply(lambda p: p["name"] if p else None)
        te["phase"] = te["phases"].apply(lambda p: p["name"] if p else None)
        st.dataframe(te[["week_ending", "project", "phase", "hours"]], width="stretch", hide_index=True)

with col2:
    st.subheader("Hours planned (next week)")
    al = pd.DataFrame(
        client.table("allocations")
        .select("week_of, planned_hours, projects(name)")
        .eq("person_id", person_id)
        .order("week_of", desc=True)
        .limit(20)
        .execute()
        .data
    )
    if al.empty:
        st.info("No allocations for this person yet.")
    else:
        al["project"] = al["projects"].apply(lambda p: p["name"] if p else None)
        st.dataframe(al[["week_of", "project", "planned_hours"]], width="stretch", hide_index=True)

st.subheader("Actions raised by this person (open)")
ac = pd.DataFrame(
    client.table("actions")
    .select("kind, body, priority, needed_by, status, projects(name)")
    .eq("raised_by", person_id)
    .eq("status", "open")
    .order("needed_by")
    .execute()
    .data
)
if ac.empty:
    st.info("No open actions raised by this person.")
else:
    ac["project"] = ac["projects"].apply(lambda p: p["name"] if p else None)
    st.dataframe(ac[["kind", "project", "body", "priority", "needed_by"]], width="stretch", hide_index=True)

st.subheader("Flags / barriers involving this person (open)")
fl = pd.DataFrame(
    client.table("flags")
    .select("rule, severity, body, status, projects(name)")
    .eq("person_id", person_id)
    .eq("status", "open")
    .execute()
    .data
)
if fl.empty:
    st.info("No open flags for this person.")
else:
    fl["project"] = fl["projects"].apply(lambda p: p["name"] if p else None)
    st.dataframe(fl[["project", "rule", "severity", "body"]], width="stretch", hide_index=True)

st.warning(
    "Not yet in Supabase for this person: weekly **outcomes** (what got done), "
    "**look-ahead** notes, **wins**, and **focus next week**. These are "
    "currently narrative text captured only in the EOW PDF sidecar — adding "
    "them here needs a small schema addition (e.g. a `weekly_notes` table) "
    "before they can show up on this page."
)
