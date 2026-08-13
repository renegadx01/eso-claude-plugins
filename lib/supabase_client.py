import streamlit as st
from supabase import Client, create_client


@st.cache_resource
def get_client() -> Client:
    """Base client, keyed only to the project URL + anon key. Never given the
    service_role key — this app runs as whichever user logs in, and RLS on
    the "authenticated" role is the security boundary, matching the
    convention in eso-platform-supabase's CLAUDE.md."""
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
