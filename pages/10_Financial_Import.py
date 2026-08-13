import pandas as pd
import streamlit as st

from lib.auth import get_authed_client
from lib.branding import brand_header

brand_header("Financial Import — QuickBooks data into Supabase")
st.caption(
    "Manual entry path for monthly QuickBooks figures. One row per calendar "
    "month. Once populated, the Firm KPIs page computes Net Multiplier, "
    "Overhead Multiplier, Break-Even Rate, Profit-to-Earnings, Cash Flow, "
    "and Aged AR from real data instead of proxies. "
    "Requires migration **005_financials_and_health.sql** to be applied first."
)

client = get_authed_client()

# ── check migration is applied ─────────────────────────────────────────────
try:
    existing = pd.DataFrame(
        client.table("financials").select("*").order("period_ending", desc=True).execute().data
    )
    migration_applied = True
except Exception:
    st.error(
        "The `financials` table doesn't exist yet. Apply migration "
        "**005_financials_and_health.sql** in the Supabase SQL editor first, "
        "then reload this page."
    )
    st.stop()

# ── existing data ──────────────────────────────────────────────────────────
st.subheader("Periods on record")
if existing.empty:
    st.info("No financial periods entered yet.")
else:
    display = existing[[
        "period_label", "period_ending", "gross_revenue", "net_revenue",
        "direct_labor_cost", "overhead", "net_profit",
        "accounts_receivable", "cash_balance", "source",
    ]].copy()
    for col in ["gross_revenue", "net_revenue", "direct_labor_cost",
                "overhead", "net_profit", "accounts_receivable", "cash_balance"]:
        display[col] = display[col].apply(
            lambda v: f"${v:,.0f}" if pd.notna(v) and v is not None else "—"
        )
    st.dataframe(display, hide_index=True, width="stretch")

# ── entry form ─────────────────────────────────────────────────────────────
st.subheader("Add / update a period")
st.caption(
    "All dollar fields come from your QuickBooks P&L and Balance Sheet for the "
    "period. Leave blank if you don't have that figure yet — partial entries are fine."
)

with st.form("financial_entry"):
    col1, col2 = st.columns(2)
    with col1:
        period_ending = st.date_input(
            "Period ending (last day of month)",
            help="E.g. 2026-07-31 for July 2026.",
        )
        period_label = st.text_input(
            "Period label",
            placeholder="July 2026",
            help="Display name used in charts and KPI cards.",
        )
    with col2:
        source = st.selectbox("Source", ["manual", "quickbooks_csv"], index=0)
        notes = st.text_area("Notes", placeholder="Any context about this period…", height=80)

    st.divider()
    st.markdown("**Revenue** — from QuickBooks P&L")
    c1, c2 = st.columns(2)
    with c1:
        gross_revenue = st.number_input("Gross revenue ($)", min_value=0.0, step=100.0,
                                        help="Total revenue before removing pass-throughs.")
    with c2:
        net_revenue = st.number_input("Net revenue ($)", min_value=0.0, step=100.0,
                                      help="After subtracting reimbursables and consultant pass-throughs.")

    st.markdown("**Cost & overhead** — from QuickBooks P&L")
    c3, c4 = st.columns(2)
    with c3:
        direct_labor = st.number_input("Direct labor cost ($)", min_value=0.0, step=100.0,
                                       help="Billable staff salaries + burden for the period.")
    with c4:
        overhead = st.number_input("Overhead ($)", min_value=0.0, step=100.0,
                                   help="Rent, non-billable salaries, software, G&A, etc.")

    st.markdown("**Balance sheet** — from QuickBooks Balance Sheet")
    c5, c6 = st.columns(2)
    with c5:
        ar = st.number_input("Accounts receivable ($)", min_value=0.0, step=100.0,
                             help="Total outstanding AR balance at period end.")
    with c6:
        cash = st.number_input("Cash balance ($)", min_value=0.0, step=100.0,
                               help="Bank account balance at period end.")

    submitted = st.form_submit_button("Save period", type="primary")

if submitted:
    net_profit = (net_revenue or 0) - (direct_labor or 0) - (overhead or 0)
    row = {
        "period_ending":      period_ending.isoformat(),
        "period_label":       period_label or period_ending.strftime("%B %Y"),
        "gross_revenue":      gross_revenue or None,
        "net_revenue":        net_revenue or None,
        "direct_labor_cost":  direct_labor or None,
        "overhead":           overhead or None,
        "net_profit":         net_profit if (net_revenue or direct_labor or overhead) else None,
        "accounts_receivable": ar or None,
        "cash_balance":       cash or None,
        "source":             source,
        "notes":              notes or None,
    }
    try:
        client.table("financials").upsert(row, on_conflict="period_ending").execute()
        st.success(f"Saved period ending {period_ending}. Net profit: ${net_profit:,.0f}")
        st.rerun()
    except Exception as e:
        st.error(f"Save failed: {e}")

# ── QB CSV upload skeleton ─────────────────────────────────────────────────
st.divider()
with st.expander("QuickBooks CSV import (skeleton — not yet wired)"):
    st.caption(
        "Future path: export a **Profit & Loss** report from QuickBooks Online "
        "(Reports → Profit & Loss → Export → CSV), then upload here. The importer "
        "will parse the standard QB P&L CSV column layout and pre-fill the form "
        "above. Not built yet — manual entry above covers the same data."
    )
    st.file_uploader(
        "Upload QuickBooks P&L CSV",
        type="csv",
        disabled=True,
        help="Coming soon — use manual entry above for now.",
    )
