import pandas as pd
import streamlit as st

from lib.auth import get_authed_client
from lib.branding import brand_header

brand_header("Firm KPIs — financial health at a glance")
st.caption(
    "The 10 standard architecture-firm financial KPIs (Monograph's framework). "
    "Three are computable today from real Supabase data — clearly marked as "
    "**proxies**, since the underlying inputs aren't quite what the textbook "
    "formula calls for. The rest are called out as blocked rather than faked, "
    "same convention as the rest of this app."
)

client = get_authed_client()


# ============================================================================
# 1. Utilization Rate (proxy — planned hours, not logged actuals)
# ============================================================================
st.header("1. Utilization Rate")
st.caption(
    "Target formula: billable hours ÷ total hours. `time_entries` (actual "
    "logged hours) is still empty firmwide, so this uses **planned hours from "
    "`allocations`** instead — a look-ahead proxy, not a look-back actual. "
    "Benchmarks: all staff 60–65%, technical/professional staff 75–85%, "
    "principals 40–50%; over 85% suggests burnout risk."
)

people = pd.DataFrame(
    client.table("people")
    .select("id, full_name, role, weekly_capacity, billable")
    .eq("active", True)
    .execute()
    .data
)

weeks_df = pd.DataFrame(client.table("allocations").select("week_of").execute().data)

if people.empty or weeks_df.empty:
    st.info("Not enough data yet (need active `people` and at least one week of `allocations`).")
else:
    week = st.selectbox("Week of", sorted(weeks_df["week_of"].unique(), reverse=True), key="util_week")

    alloc = pd.DataFrame(
        client.table("allocations")
        .select("person_id, planned_hours")
        .eq("week_of", week)
        .execute()
        .data
    )
    alloc_by_person = alloc.groupby("person_id", as_index=False)["planned_hours"].sum()

    util = people.merge(alloc_by_person, left_on="id", right_on="person_id", how="left")
    util["planned_hours"] = util["planned_hours"].fillna(0)
    util["utilization_pct"] = (util["planned_hours"] / util["weekly_capacity"] * 100).round(1)

    is_principal = util["role"].str.contains("principal", case=False, na=False)
    cohorts = {
        "All staff (60–65%)": util,
        "Technical/professional (75–85%)": util[util["billable"] & ~is_principal],
        "Principals (40–50%)": util[is_principal],
    }

    cols = st.columns(len(cohorts))
    for col, (label, subset) in zip(cols, cohorts.items()):
        with col:
            if subset.empty:
                st.metric(label, "—")
            else:
                st.metric(label, f"{subset['utilization_pct'].mean():.0f}%")

    st.caption(
        "Includes people with no allocation row this week as 0% — if that's "
        "incomplete planning rather than genuine idle time, these averages "
        "understate real planned utilization."
    )
    st.dataframe(
        util[["full_name", "role", "billable", "planned_hours", "weekly_capacity", "utilization_pct"]]
        .sort_values("utilization_pct", ascending=False),
        width="stretch", hide_index=True,
    )


# ============================================================================
# 2 & 3. Backlog Volume + Net Revenue Per Employee (proxies — share a base calc)
# ============================================================================
st.header("2. Backlog Volume  &  3. Net Revenue Per Employee")
st.caption(
    "Both need **fee earned to date**, which this approximates as "
    "`phase.fee × phase.pct_complete` (a manually-tracked figure, not derived "
    "from billing) rather than actual invoiced revenue. Both also use "
    "`projects.total_fee` as a stand-in for **net operating revenue** — the "
    "real metric nets out consultant/reimbursable pass-throughs, which "
    "`total_fee` doesn't distinguish. Treat these as directional, not exact."
)

projects = pd.DataFrame(
    client.table("projects").select("id, name, total_fee").eq("status", "active").execute().data
)
phases = pd.DataFrame(client.table("phases").select("project_id, fee, pct_complete").execute().data)

if projects.empty:
    st.info("No active projects yet.")
else:
    # pct_complete's scale (0–1 vs 0–100) isn't documented — normalize defensively.
    if not phases.empty and phases["pct_complete"].max() > 1:
        phases = phases.assign(pct_complete=phases["pct_complete"] / 100)

    phases["fee_earned"] = (phases["fee"].fillna(0) * phases["pct_complete"].fillna(0))
    earned_by_project = phases.groupby("project_id", as_index=False)["fee_earned"].sum()

    proj = projects.merge(earned_by_project, left_on="id", right_on="project_id", how="left")
    proj["fee_earned"] = proj["fee_earned"].fillna(0)
    proj["total_fee"] = proj["total_fee"].fillna(0)
    proj["backlog"] = proj["total_fee"] - proj["fee_earned"]

    total_contract_value = proj["total_fee"].sum()
    total_earned = proj["fee_earned"].sum()
    total_backlog = proj["backlog"].sum()
    active_headcount = len(people) if not people.empty else None

    col1, col2, col3 = st.columns(3)
    col1.metric("Active contract value", f"${total_contract_value:,.0f}")
    col2.metric("Fee earned to date (proxy)", f"${total_earned:,.0f}")
    col3.metric("Backlog (proxy)", f"${total_backlog:,.0f}")

    if active_headcount:
        st.metric("Net revenue per employee (proxy)", f"${total_earned / active_headcount:,.0f}")

    st.dataframe(
        proj[["name", "total_fee", "fee_earned", "backlog"]].sort_values("backlog", ascending=False),
        width="stretch", hide_index=True,
    )


# ============================================================================
# Blocked — wired up, waiting on real hours data
# ============================================================================
st.header("Blocked — wired up, waiting on real hours")
st.warning(
    "**Net Multiplier** (net operating revenue ÷ direct labor) and the "
    "**true, logged-hours Utilization Rate** both already have a home in the "
    "schema — `rates.rate_type = 'cost'` plus `time_entries` cover the direct-"
    "labor side. They're blank because `time_entries` has 0 rows firmwide. "
    "These will compute correctly the moment real actual hours land."
)


# ============================================================================
# Financial KPIs — from QuickBooks (financials table, migration 005)
# ============================================================================
st.header("Financial KPIs — from QuickBooks")

try:
    fin_rows = pd.DataFrame(
        client.table("financials")
        .select("*")
        .order("period_ending", desc=True)
        .limit(12)
        .execute()
        .data
    )
    fin_table_exists = True
except Exception:
    fin_rows = pd.DataFrame()
    fin_table_exists = False

if not fin_table_exists:
    st.warning(
        "Apply migration **005_financials_and_health.sql** in Supabase, then "
        "enter QuickBooks figures on the **Financial Import** page to unlock "
        "these KPIs."
    )
elif fin_rows.empty:
    st.info(
        "No financial data yet — go to **Financial Import** and enter the "
        "QuickBooks figures for at least one month."
    )
else:
    latest = fin_rows.iloc[0]
    label  = latest.get("period_label") or latest["period_ending"]

    st.caption(f"Most recent period: **{label}**")

    # ── Net Multiplier ──────────────────────────────────────────────────────
    st.subheader("4. Net Multiplier")
    st.caption("Net operating revenue ÷ direct labor cost. Target: ≥ 2.5× for a healthy firm.")
    nr  = latest.get("net_revenue")
    dlc = latest.get("direct_labor_cost")
    if nr and dlc and dlc > 0:
        nm = round(nr / dlc, 2)
        delta = f"{'above' if nm >= 2.5 else 'below'} 2.5× target"
        st.metric("Net Multiplier", f"{nm}×", delta=delta,
                  delta_color="normal" if nm >= 2.5 else "inverse")
    else:
        st.caption("Need net_revenue and direct_labor_cost — enter both on Financial Import.")

    # ── Overhead Multiplier ─────────────────────────────────────────────────
    st.subheader("5. Overhead Multiplier")
    st.caption("Overhead ÷ direct labor cost. Target: < 1.0× (ideally 0.5–0.8×).")
    oh = latest.get("overhead")
    if oh and dlc and dlc > 0:
        om = round(oh / dlc, 2)
        delta = f"{'ok' if om < 1.0 else 'high'}"
        st.metric("Overhead Multiplier", f"{om}×", delta=delta,
                  delta_color="normal" if om < 1.0 else "inverse")
    else:
        st.caption("Need overhead and direct_labor_cost.")

    # ── Break-Even Rate ─────────────────────────────────────────────────────
    st.subheader("6. Break-Even Rate")
    st.caption("(Direct labor + overhead) ÷ billable hours. What you must charge per hour to break even.")
    if dlc and oh:
        # Use planned billable hours from allocations as proxy until time_entries has data
        try:
            alloc_hrs = pd.DataFrame(
                client.table("allocations").select("planned_hours, people(billable)").execute().data
            )
            billable_hrs = alloc_hrs[
                alloc_hrs["people"].apply(lambda p: p.get("billable", False) if p else False)
            ]["planned_hours"].sum() if not alloc_hrs.empty else 0
        except Exception:
            billable_hrs = 0

        if billable_hrs > 0:
            # Annualise: assume ~4.33 weeks/month
            annual_hrs = billable_hrs * 4.33
            ber = round((dlc + oh) / annual_hrs, 2)
            st.metric("Break-Even Rate (proxy)", f"${ber:.2f}/hr",
                      help="Uses planned allocation hours as proxy for actual billable hours.")
        else:
            st.caption("Need billable hours data (time_entries or allocations).")
    else:
        st.caption("Need direct_labor_cost and overhead.")

    # ── Profit-to-Earnings ──────────────────────────────────────────────────
    st.subheader("7. Profit-to-Earnings Ratio")
    st.caption("Net profit ÷ net revenue. Target: 15–20%+ for a well-run studio.")
    np_ = latest.get("net_profit")
    if np_ is not None and nr and nr > 0:
        pte = round(np_ / nr * 100, 1)
        delta = f"{'healthy' if pte >= 15 else 'below target'}"
        st.metric("P/E Ratio", f"{pte}%", delta=delta,
                  delta_color="normal" if pte >= 15 else "inverse")
    else:
        st.caption("Need net_revenue and net_profit.")

    # ── Cash Flow ───────────────────────────────────────────────────────────
    st.subheader("8. Cash Balance")
    st.caption("Bank position at period end (from QB Balance Sheet).")
    cb = latest.get("cash_balance")
    if cb is not None:
        st.metric("Cash balance", f"${cb:,.0f}")
    else:
        st.caption("Need cash_balance.")

    # ── Aged AR ─────────────────────────────────────────────────────────────
    st.subheader("9. Accounts Receivable")
    st.caption("Total outstanding AR at period end. Target: < 60 days average.")
    ar = latest.get("accounts_receivable")
    if ar is not None:
        st.metric("AR balance", f"${ar:,.0f}")
        st.caption(
            "Average days outstanding requires per-invoice aging — not yet tracked. "
            "The balance above is from the QB Balance Sheet."
        )
    else:
        st.caption("Need accounts_receivable.")

    # ── trend table ─────────────────────────────────────────────────────────
    st.subheader("Trend — last 12 months")
    trend = fin_rows[["period_label", "net_revenue", "direct_labor_cost",
                       "overhead", "net_profit", "cash_balance"]].copy()
    for col in ["net_revenue", "direct_labor_cost", "overhead", "net_profit", "cash_balance"]:
        trend[col] = trend[col].apply(
            lambda v: f"${v:,.0f}" if pd.notna(v) and v is not None else "—"
        )
    st.dataframe(trend, hide_index=True, width="stretch")

# ── Pending Proposals — still needs CRM ─────────────────────────────────────
st.header("10. Pending Proposals")
st.info(
    "Needs the **pipeline** table (Phase 5 of PLATFORM_MODEL.md) synced from "
    "the CRM. Which CRM is the source of truth is still an open decision — "
    "not built until that's resolved."
)
