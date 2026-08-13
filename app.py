import streamlit as st

from lib.auth import logout_button, require_login
from lib.branding import MARK, apply_branding, render_sidebar_nav

st.set_page_config(
    page_title="ĒSO Platform",
    page_icon=str(MARK),
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_branding()
require_login()

pg = st.navigation(
    {
        "Command": [
            st.Page("pages/0_Command_Center.py", title="Command Center", icon="🎯"),
        ],
        "Micro — Weekly Heartbeat": [
            st.Page("pages/8_EOW_Submit.py",   title="EOW Submit",  icon="📤"),
            st.Page("pages/1_EOW_Inputs.py",   title="EOW Inputs",  icon="📋"),
            st.Page("pages/2_MKW_Rollup.py",   title="MKW Rollup",  icon="🗞️"),
        ],
        "Macro — Project Lifecycle": [
            st.Page("pages/9_Project_Dashboard.py",  title="Project Dashboard", icon="🏗️"),
            st.Page("pages/3_Time_Allocation.py",    title="Time Allocation",   icon="⏱️"),
            st.Page("pages/4_Burn_Rate.py",          title="Burn Rate",         icon="🔥"),
            st.Page("pages/5_Team_Needed.py",        title="Team Needed",       icon="👥"),
            st.Page("pages/7_Firm_KPIs.py",          title="Firm KPIs",         icon="📊"),
            st.Page("pages/10_Financial_Import.py",  title="Financial Import",  icon="💰"),
            st.Page("pages/6_Ask_the_Data.py",       title="Ask the Data",      icon="💬"),
        ],
    }
)
render_sidebar_nav()
logout_button()
pg.run()
