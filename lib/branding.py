"""ĒSO brand system — colors, logo, and the global CSS injected on every page.

Palette from the ĒSO Brand Guide (Winter 2026):
  MIDNIGHT   #214144  primary dark — header bar, accents
  PEARL      #edeae2  light warm gray — sidebar background, borders
  BONE       #f9f7f4  off-white — main background
  CLAY       #828279  mid gray — secondary text, sidebar labels
  BURNT CLAY #61655f  darker gray — subheadings
  LASER      #e9ff14  electric yellow — accent only, never a base color

apply_branding() injects all global CSS and must be called once per session
(from app.py, before st.navigation / pg.run). render_sidebar_nav() renders
the custom collapsible nav dropdowns — call it after require_login().
brand_header() is the public API for page-level titles.
"""

import base64
from pathlib import Path

import streamlit as st

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

MIDNIGHT   = "#214144"
PEARL      = "#edeae2"
BONE       = "#f9f7f4"
CLAY       = "#828279"
BURNT_CLAY = "#61655f"
LASER      = "#e9ff14"

WORDMARK = ASSETS_DIR / "logo" / "eso_wordmark_clay.png"
MARK     = ASSETS_DIR / "logo" / "eso_mark_color.png"


def _b64(path: Path) -> str:
    try:
        return base64.b64encode(path.read_bytes()).decode()
    except Exception:
        return ""


_WORDMARK_B64 = _b64(WORDMARK)
_MARK_B64     = _b64(MARK)

_CSS = f"""
<style>

/* ── Brand variables ─────────────────────────────────────────────────────── */
:root {{
  --midnight:   {MIDNIGHT};
  --pearl:      {PEARL};
  --bone:       {BONE};
  --clay:       {CLAY};
  --burnt-clay: {BURNT_CLAY};
  --laser:      {LASER};
}}

/* ── Dot-grid background on the main content area ────────────────────────── */
[data-testid="stMain"] {{
  background-image: radial-gradient(
    circle,
    rgba(33, 65, 68, 0.08) 1.5px,
    transparent 1.5px
  );
  background-size: 22px 22px;
  background-attachment: fixed;
}}

/* ── Top header bar — Midnight with ESO wordmark ─────────────────────────── */
[data-testid="stHeader"] {{
  background: var(--midnight) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
}}

[data-testid="stHeader"]::before {{
  content: "";
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 110px;
  height: 28px;
  background: url("data:image/png;base64,{_WORDMARK_B64}") left center / contain no-repeat;
  filter: brightness(0) invert(1);
  opacity: 0.85;
  pointer-events: none;
}}

/* Header toolbar icons — readable on Midnight */
[data-testid="stHeader"] button svg,
[data-testid="stToolbar"] svg,
[data-testid="stToolbarActions"] svg,
[data-testid="stDecoration"] {{
  color: rgba(255, 255, 255, 0.65) !important;
  fill: rgba(255, 255, 255, 0.65) !important;
}}
[data-testid="stHeader"] button:hover svg {{
  color: #fff !important;
  fill: #fff !important;
}}

/* ── Sidebar — Pearl background, dark readable text ──────────────────────── */
[data-testid="stSidebar"] {{
  background: var(--pearl) !important;
  border-right: 1px solid rgba(33, 65, 68, 0.10) !important;
}}

/* Sidebar header area (logo zone) */
[data-testid="stSidebarHeader"] {{
  background: var(--pearl) !important;
  border-bottom: 1px solid rgba(33, 65, 68, 0.08) !important;
  padding-bottom: 8px !important;
}}

/* Logo image — clay wordmark is readable on pearl, no filter needed */
[data-testid="stSidebarHeader"] img,
[data-testid="stSidebar"] [data-testid="stImage"] img {{
  opacity: 0.9;
}}

/* Hide Streamlit's auto-generated nav — replaced by render_sidebar_nav() */
[data-testid="stSidebarNav"] {{
  display: none !important;
}}

/* ── Sidebar expanders (custom nav sections) ─────────────────────────────── */
[data-testid="stSidebar"] [data-testid="stExpander"] {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}}

[data-testid="stSidebar"] details {{
  border: none !important;
  background: transparent !important;
}}

[data-testid="stSidebar"] details summary {{
  padding: 10px 12px 6px !important;
  user-select: none !important;
  border-radius: 0 !important;
  background: transparent !important;
}}

[data-testid="stSidebar"] details summary:hover {{
  background: rgba(33, 65, 68, 0.05) !important;
}}

/* Section label text inside the expander summary */
[data-testid="stSidebar"] details summary p,
[data-testid="stSidebar"] details summary span {{
  font-size: 9px !important;
  font-weight: 800 !important;
  letter-spacing: 0.18em !important;
  text-transform: uppercase !important;
  color: var(--clay) !important;
}}

/* Expander chevron icon */
[data-testid="stSidebar"] details summary svg {{
  color: var(--clay) !important;
  fill: var(--clay) !important;
  width: 12px !important;
  height: 12px !important;
}}

/* Expander content area */
[data-testid="stSidebar"] details[open] > div:last-child {{
  padding: 2px 0 8px 0 !important;
}}

/* ── Sidebar page links ───────────────────────────────────────────────────── */
[data-testid="stSidebar"] [data-testid="stPageLink"] a,
[data-testid="stSidebar"] a[data-testid="stPageLink"] {{
  color: var(--midnight) !important;
  font-size: 13px !important;
  font-weight: 400 !important;
  border-radius: 6px !important;
  margin: 1px 8px !important;
  padding: 7px 12px !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  text-decoration: none !important;
  border-left: 3px solid transparent !important;
  transition: background 0.12s, color 0.12s !important;
}}

[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {{
  background: rgba(33, 65, 68, 0.07) !important;
  color: var(--midnight) !important;
}}

[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {{
  background: rgba(33, 65, 68, 0.09) !important;
  font-weight: 600 !important;
  border-left: 3px solid var(--laser) !important;
  color: var(--midnight) !important;
  padding-left: 9px !important;
}}

/* ── Sidebar generic text / caption ─────────────────────────────────────── */
[data-testid="stSidebar"] p {{
  color: var(--clay) !important;
}}
[data-testid="stSidebar"] .stCaption p,
[data-testid="stSidebar"] small {{
  color: var(--clay) !important;
  font-size: 11px !important;
  opacity: 0.75;
}}

/* ── Sidebar logout / action button ─────────────────────────────────────── */
[data-testid="stSidebar"] .stButton > button {{
  background: rgba(33, 65, 68, 0.06) !important;
  color: var(--midnight) !important;
  border: 1px solid rgba(33, 65, 68, 0.15) !important;
  border-radius: 6px !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  padding: 4px 12px !important;
  width: 100%;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
  background: rgba(33, 65, 68, 0.12) !important;
  border-color: rgba(33, 65, 68, 0.25) !important;
}}

/* Sidebar info / alert box */
[data-testid="stSidebar"] .stAlert {{
  background: rgba(233, 255, 20, 0.08) !important;
  border-color: rgba(33, 65, 68, 0.15) !important;
  color: var(--midnight) !important;
  border-radius: 8px !important;
}}

/* Sidebar divider */
[data-testid="stSidebar"] hr {{
  border-color: rgba(33, 65, 68, 0.10) !important;
  margin: 8px 12px !important;
}}

/* ── Visual hierarchy — headings ─────────────────────────────────────────── */
h1 {{
  font-size: 1.85rem !important;
  font-weight: 700 !important;
  color: var(--midnight) !important;
  letter-spacing: -0.03em !important;
  line-height: 1.15 !important;
  margin-bottom: 0 !important;
}}

h2, .stSubheader {{
  font-size: 1.05rem !important;
  font-weight: 700 !important;
  color: var(--midnight) !important;
  letter-spacing: -0.01em !important;
  margin-top: 1.75rem !important;
  padding-bottom: 4px !important;
  border-bottom: 1px solid var(--pearl) !important;
}}

h3 {{
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  color: var(--clay) !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  margin-top: 1.25rem !important;
}}

/* ── Metric cards ────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {{
  background: #fff !important;
  border: 1px solid var(--pearl) !important;
  border-radius: 12px !important;
  padding: 18px 22px !important;
  box-shadow: 0 1px 4px rgba(33, 65, 68, 0.06) !important;
}}

[data-testid="stMetricLabel"] > div {{
  font-size: 9.5px !important;
  font-weight: 700 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--clay) !important;
}}

[data-testid="stMetricValue"] > div {{
  font-size: 2.1rem !important;
  font-weight: 700 !important;
  color: var(--midnight) !important;
  letter-spacing: -0.04em !important;
}}

[data-testid="stMetricDelta"] {{
  font-size: 12px !important;
  font-weight: 500 !important;
}}

/* ── Dataframes ──────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] > div {{
  border-radius: 10px !important;
  overflow: hidden !important;
  border: 1px solid var(--pearl) !important;
  box-shadow: 0 1px 3px rgba(33, 65, 68, 0.05) !important;
}}

/* ── Selectbox / inputs ──────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] > div > div {{
  border-radius: 8px !important;
  border-color: var(--pearl) !important;
  background: #fff !important;
}}

[data-testid="stSelectbox"] label,
[data-testid="stTextInput"] label,
[data-testid="stDateInput"] label {{
  font-size: 10px !important;
  font-weight: 700 !important;
  letter-spacing: 0.10em !important;
  text-transform: uppercase !important;
  color: var(--clay) !important;
}}

/* ── Info / warning / error / success alerts ─────────────────────────────── */
[data-testid="stAlert"] {{
  border-radius: 8px !important;
  border-left-width: 3px !important;
}}

/* ── Primary buttons ─────────────────────────────────────────────────────── */
.stButton > button[kind="primary"] {{
  background: var(--midnight) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 7px !important;
  font-weight: 600 !important;
}}
.stButton > button[kind="primary"]:hover {{
  opacity: 0.88 !important;
}}

/* ── Chat input (Ask the Data page) ─────────────────────────────────────── */
[data-testid="stChatInput"] {{
  border-radius: 10px !important;
  border-color: var(--pearl) !important;
  background: #fff !important;
}}

/* ── Accent rule under page titles ──────────────────────────────────────── */
hr.eso-accent {{
  border: none;
  height: 3px;
  width: 48px;
  background: var(--laser);
  margin: -0.5rem 0 1.5rem 0;
  border-radius: 2px;
}}

/* ── Section label ───────────────────────────────────────────────────────── */
.eso-section-label {{
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--clay);
  margin-bottom: 8px;
  display: block;
}}

</style>
"""


def apply_branding() -> None:
    """Call once in app.py after st.set_page_config — injects all global CSS.
    Does NOT call st.logo() so the sidebar logo is fully controlled by
    render_sidebar_nav()."""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_sidebar_nav() -> None:
    """Render the custom collapsible nav dropdowns in the sidebar.
    Call this in app.py after require_login() and before pg.run()."""
    with st.sidebar:
        # Logo at the top of the sidebar content
        if WORDMARK.exists():
            st.image(str(WORDMARK), use_container_width=True)
        st.divider()

        st.page_link("pages/0_Command_Center.py", label="Command Center", icon="🎯")
        st.divider()

        with st.expander("Micro — Weekly Heartbeat", expanded=True):
            st.page_link("pages/8_EOW_Submit.py",  label="EOW Submit",  icon="📤")
            st.page_link("pages/1_EOW_Inputs.py",  label="EOW Inputs",  icon="📋")
            st.page_link("pages/2_MKW_Rollup.py",  label="MKW Rollup",  icon="🗞️")

        with st.expander("Macro — Project Lifecycle", expanded=True):
            st.page_link("pages/9_Project_Dashboard.py",  label="Project Dashboard", icon="🏗️")
            st.page_link("pages/3_Time_Allocation.py",    label="Time Allocation",   icon="⏱️")
            st.page_link("pages/4_Burn_Rate.py",          label="Burn Rate",         icon="🔥")
            st.page_link("pages/5_Team_Needed.py",        label="Team Needed",       icon="👥")
            st.page_link("pages/7_Firm_KPIs.py",          label="Firm KPIs",         icon="📊")
            st.page_link("pages/10_Financial_Import.py",  label="Financial Import",  icon="💰")
            st.page_link("pages/6_Ask_the_Data.py",       label="Ask the Data",      icon="💬")


def brand_header(title: str, caption: str | None = None) -> None:
    """Page title + Laser accent rule, with optional caption below."""
    st.title(title)
    st.markdown('<hr class="eso-accent">', unsafe_allow_html=True)
    if caption:
        st.caption(caption)
