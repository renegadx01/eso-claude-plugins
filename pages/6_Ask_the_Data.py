import streamlit as st

from lib.auth import get_authed_client
from lib.branding import brand_header
from lib.claude_agent import ask, is_configured

brand_header("Ask the Data")
st.caption(
    "A Claude-powered assistant that can query the live Supabase data — "
    "capacity, burn, allocations, actions, flags, milestones. Read-only: it "
    "can look things up but never writes or resolves anything. Each question "
    "runs its own fresh lookup — for follow-ups, restate any names or "
    "filters you want carried forward."
)

if not is_configured():
    st.info(
        "Not wired up yet — this needs a real Anthropic API key. The tool "
        "surface and chat UI are built and ready; add `ANTHROPIC_API_KEY` in "
        "`.streamlit/secrets.toml` (see `secrets.toml.example` for where) "
        "once that's worth paying for, then reload this page. No API cost "
        "is incurred until then."
    )
    st.stop()

if "ask_history" not in st.session_state:
    st.session_state.ask_history = []

for turn in st.session_state.ask_history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

question = st.chat_input("e.g. Who's over-allocated this week? What's the burn on Golden Bear?")
if question:
    st.session_state.ask_history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            answer, tool_calls = ask(get_authed_client(), st.session_state.ask_history)
        except Exception as e:
            answer = None
            st.error(f"Something went wrong asking Claude: {e}")
        if answer is not None:
            if tool_calls:
                with st.expander(f"Looked up {len(tool_calls)} thing(s)"):
                    for name, args in tool_calls:
                        st.caption(f"`{name}({args})`")
            st.markdown(answer)
            st.session_state.ask_history.append({"role": "assistant", "content": answer})
