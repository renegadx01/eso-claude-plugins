import streamlit as st

from .supabase_client import get_client


def is_demo_mode():
    """?demo=1 in the URL switches the whole app to made-up local data (see
    lib/demo_data.py / lib/demo_client.py) — no login, no real Supabase
    query, safe to poke at freely. Never persists past this browser tab."""
    return st.query_params.get("demo") == "1"


def require_login():
    """Gate a page behind Supabase Auth. Call as the first thing on every
    page (after st.set_page_config) — st.stop()s the script if not signed in."""
    if is_demo_mode():
        return

    if "session" not in st.session_state:
        st.session_state.session = None

    if st.session_state.session is None:
        _login_form()
        st.stop()


def _login_form():
    st.title("Sign in — ĒSO Platform")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Sign in") and email and password:
        try:
            result = get_client().auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            st.session_state.session = result.session
            st.session_state.user_email = result.user.email
            st.rerun()
        except Exception as e:
            st.error(f"Sign-in failed: {e}")
    st.caption(
        "No account yet? Ask an admin to add you in Supabase → Authentication → Users."
    )


def get_authed_client():
    """Client with the signed-in user's session attached, so table queries
    run as that user and are subject to RLS (not bypassed like service_role).
    In demo mode, returns the fake client over made-up data instead."""
    if is_demo_mode():
        from .demo_client import DemoClient
        return DemoClient()

    client = get_client()
    session = st.session_state.get("session")
    if session:
        client.auth.set_session(session.access_token, session.refresh_token)
    return client


def logout_button():
    if is_demo_mode():
        with st.sidebar:
            st.info(
                "🎭 **Demo mode** — every number on this page is made up. "
                "Remove `?demo=1` from the URL for the real, signed-in app.",
                icon="🎭",
            )
        return

    with st.sidebar:
        st.caption(f"Signed in as {st.session_state.get('user_email', '')}")
        if st.button("Sign out"):
            get_client().auth.sign_out()
            st.session_state.session = None
            st.rerun()
