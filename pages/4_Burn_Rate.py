import pandas as pd
import streamlit as st

from lib.auth import get_authed_client
from lib.branding import brand_header

brand_header("Burn Rate — fee & hours vs. budget, by phase")
st.caption(
    "Problem it answers: which phases are burning through budget faster than "
    "they're progressing, project-by-project."
)

client = get_authed_client()

df = pd.DataFrame(client.table("v_phase_burn").select("*").execute().data)
if df.empty:
    st.info("No data in v_phase_burn yet.")
    st.stop()

projects = st.multiselect("Filter by project", sorted(df["project"].unique()))
if projects:
    df = df[df["project"].isin(projects)]

has_budget = df["budget_hours"].notna() & (df["budget_hours"] > 0)
df["hours_pct"] = None
df.loc[has_budget, "hours_pct"] = (df.loc[has_budget, "accrued_hours"] / df.loc[has_budget, "budget_hours"] * 100).round(1)

at_risk = df[has_budget & (df["hours_pct"] >= 90)]
if not at_risk.empty:
    st.warning(
        f"{len(at_risk)} phase(s) at or above 90% of budget hours: "
        + ", ".join(f"{r.project} / {r.phase} ({r.hours_pct:g}%)" for r in at_risk.itertuples())
    )

no_budget = df[~has_budget]
if not no_budget.empty:
    st.caption(
        f"{len(no_budget)} phase(s) have no `budget_hours` set, so burn % can't "
        "be computed for them — shown with hours_pct blank below."
    )

st.dataframe(
    df[["project", "phase", "budget_hours", "accrued_hours", "hours_pct", "fee", "fee_burn", "cost_burn"]],
    width="stretch", hide_index=True,
)

chart_df = df.copy()
# Phase names (Schematic Design, CD, etc.) repeat across every project — index
# by name alone and every project's "Schematic Design" collapses into one
# bar. Use "project — phase" so each phase gets its own bar.
chart_df["phase_label"] = chart_df["project"] + " — " + chart_df["phase"]
chart_df = chart_df.set_index("phase_label")[["budget_hours", "accrued_hours"]].dropna(subset=["budget_hours"])
if not chart_df.empty:
    st.bar_chart(chart_df, stack=False)
