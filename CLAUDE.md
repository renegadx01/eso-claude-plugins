# CLAUDE.md — eso-platform-app

Project brief for Claude Code. Read first.

**See also:** `EOW_System/PLATFORM_STATUS.md` (two levels up) — the living
cross-repo status doc: what's actually live in Supabase right now, real
backfill state, and open decisions pending. Read it alongside this file, not
instead of it.

## What this project owns

The **ĒSO Platform UI**: a Streamlit app that gives the team visibility into
the data in Supabase — capacity (utilization by person/week) and burn (fee and
hours vs. budget by phase), per Phase 2 of the roadmap in `PLATFORM_MODEL.md`
(plugin repo). It is read-only in v1.

This project does **not** own the schema, migrations, or RLS policies — those
live in the sibling project `eso-platform-supabase`. This app only *reads*
from the two views it already exposes (`v_person_week`, `v_phase_burn`) via
the Supabase JS/Python client, as a signed-in user, subject to RLS.

## Reality check (keep in mind)

Eight-person firm. This is an internal ops dashboard, not a product. Favor the
simplest thing that gets capacity/burn visibility in front of Maggie and the
team — do not over-engineer auth, roles, or design before there's a real need.

## Auth model

- Every user signs in with Supabase Auth (email + password). There is no
  separate login system — identity is unified with the rest of the platform.
- The app uses the Supabase **anon key** only, never service_role. Once a user
  signs in, their session is attached to the client (`auth.set_session`), so
  every query runs as that user and is subject to RLS — same "authenticated
  role can read/write" policy already defined in `eso-platform-supabase`.
- New team members are added manually today: Supabase dashboard ->
  Authentication -> Users -> Add User. There is no self-serve signup flow in
  v1 — don't build one without checking with Pete first, since it changes who
  can create accounts against production data.

## Known gap

Postgres views run with the view owner's privileges by default (not the
querying user's), unless created with `security_invoker = true` (PG15+). If
`v_person_week` / `v_phase_burn` were created by a superuser, RLS on the
underlying tables may not actually be enforced when queried through the view.
This isn't a practical problem today because the existing RLS policy already
grants full read access to any authenticated user anyway — but if RLS is ever
tightened to be person/team-scoped, this needs revisiting (recreate the views
with `security_invoker = true`, in `eso-platform-supabase`).

## Conventions

- Read-only for now. Do not add write paths (e.g. resolving actions/flags)
  without confirming scope — that's a deliberate v2 decision, not a default.
- Never commit `.streamlit/secrets.toml` — it's gitignored. Use
  `secrets.toml.example` as the template.
- Keep pages simple: one Streamlit page per view, gated by `lib.auth.require_login`.

## Ask the Data (`pages/6_Ask_the_Data.py`, `lib/claude_agent.py`)

A chat page backed by the Claude API (Python SDK's beta `tool_runner`,
`model="claude-opus-5"`) with nine read-only tools — one per table/view
(`people`, `projects`, `v_person_week`, `v_phase_burn`, `allocations`,
`time_entries`, `actions`, `flags`, `milestones`) — each a thin wrapper
around `get_authed_client().table(...).select(...)`, so it inherits the same
RLS/anon-key posture as the rest of the app. Requires `ANTHROPIC_API_KEY` in
`.streamlit/secrets.toml`.

Deliberately simple: each question runs its own fresh tool-use loop.
Conversation history is replayed to Claude as plain text (no persisted
tool_use/tool_result blocks across turns) — cheaper and avoids the
bookkeeping of reconstructing multi-turn tool state, at the cost of Claude
not "remembering" exactly which rows it looked up in earlier turns. If that
tradeoff stops being acceptable, the fix is to persist the full Anthropic
message history (including tool blocks) in `st.session_state` instead of
just the text.

Same read-only rule as the rest of the app: all nine tools issue `.select()`
only. If real write paths (e.g. "resolve this flag" via chat) are ever
wanted, that's the same v2 decision called out above, not a default here.
