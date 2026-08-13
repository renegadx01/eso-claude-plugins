"""Claude-backed natural-language assistant over the ĒSO Platform data.

Read-only by construction: every tool issues a `.select()` against Supabase
through the signed-in user's authed client (subject to RLS), never a write.
Each question runs its own fresh tool-use loop — the text-only history is
replayed for conversational context, but tool calls/results are not
persisted across turns. That keeps token usage and the implementation both
simple; see CLAUDE.md's "favor the simplest thing" note.
"""

import json

import streamlit as st
from anthropic import Anthropic, beta_tool

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """
You are a data assistant for ĒSO Architecture, an eight-person architecture
firm, embedded in their internal ops platform. You answer questions about
capacity, project burn, planned vs. actual hours, open actions, flags, and
milestones by calling the tools provided — never from memory or assumption.

Schema notes worth knowing before you query:
- `allocations.week_of` is a forward-looking PLAN (what someone said they'd
  work on next week). `time_entries.week_ending` is ACTUAL logged hours for a
  week that already happened. These are different week semantics by design —
  never treat them as the same field or compute a single "actual vs. planned"
  number without checking both are for a comparable week.
- `actions.kind` is only ever "ask" or "fyi" (never "action").
- `flags.severity` is only ever "info" or "critical" (a binary, not a scale).
- `time_entries` may have little or no real data today — there is currently
  no structured source for actual/reported hours (that will eventually come
  from Monograph or the platform itself). If a time_entries query comes back
  empty, say so plainly rather than implying nobody logged hours.
- Person and project names must match exactly (case-sensitive) for the
  lookup tools to find them. If a query returns nothing, try `list_people` or
  `list_projects` to check the exact name before concluding there's no data.

Things that are NOT in this database at all, so don't attempt them with the
tools or guess an answer — say plainly that it isn't tracked yet:
- Billed-vs-logged hours (only logged/accrued hours exist; nothing marks an
  hour as invoiced).
- Project health status (On Track / Monitor / Concern / Critical) and
  "Wins this week" — both still live only in the weekly PDF, not the database.
- RACI / process framework (who's Responsible vs. Accountable per phase,
  target % effort per role per phase).
- Team-level rollups — capacity/burn views are per-person and per-project
  only; there's no team entity to group by.
- Pipeline / prospective projects, hiring signals, or what-if scenario
  planning — none of that is modeled yet.
- Slip-to-downstream-workload cascade impact — a slip itself may be visible
  as a milestone's due date changing, but there's no computed ripple effect.

Always ground answers in the tool results you actually received. State
figures precisely (exact hours, dates, counts) rather than rounding or
estimating. If the data doesn't answer the question, say what's missing
instead of guessing. You are read-only — never imply you changed, resolved,
or wrote anything.
""".strip()


def _rows(query, limit=300):
    return query.limit(limit).execute().data


def _flatten(rows, mapping):
    """mapping: {embedded_key: (flat_key, sub_key)} — pulls one field out of
    a nested Supabase embed (e.g. people(full_name)) into a flat column."""
    for r in rows:
        for embedded_key, (flat_key, sub_key) in mapping.items():
            embedded = r.pop(embedded_key, None)
            r[flat_key] = embedded.get(sub_key) if embedded else None
    return rows


def _build_tools(supabase):
    @beta_tool
    def list_people(active_only: bool = True) -> str:
        """List people at the firm with role and weekly capacity.

        Args:
            active_only: If true (default), only include currently active people.
        """
        q = supabase.table("people").select(
            "full_name, role, weekly_capacity, billable, active"
        ).order("full_name")
        if active_only:
            q = q.eq("active", True)
        return json.dumps(_rows(q), default=str)

    @beta_tool
    def list_projects(status: str = "active") -> str:
        """List projects.

        Args:
            status: Filter by status ("active", "completed", etc). Pass "all" for no filter.
        """
        q = supabase.table("projects").select(
            "name, client_name, status, total_fee, start_date, target_end"
        ).order("name")
        if status and status != "all":
            q = q.eq("status", status)
        return json.dumps(_rows(q), default=str)

    @beta_tool
    def get_capacity(person_name: str = "", week_ending: str = "") -> str:
        """Get weekly utilization per person from v_person_week: logged hours
        vs. weekly capacity, with a computed utilization percentage.

        Args:
            person_name: Exact full name to filter to one person. Empty for everyone.
            week_ending: ISO date (YYYY-MM-DD) to filter to one week. Empty for all weeks.
        """
        q = supabase.table("v_person_week").select("*").order("week_ending", desc=True)
        if person_name:
            q = q.eq("full_name", person_name)
        if week_ending:
            q = q.eq("week_ending", week_ending)
        return json.dumps(_rows(q), default=str)

    @beta_tool
    def get_burn(project_name: str = "") -> str:
        """Get fee/hours burn per phase from v_phase_burn: budget hours and
        fee vs. accrued hours, fee burn, and cost burn.

        Args:
            project_name: Exact project name to filter to one project. Empty for all projects.
        """
        q = supabase.table("v_phase_burn").select("*")
        if project_name:
            q = q.eq("project", project_name)
        return json.dumps(_rows(q), default=str)

    @beta_tool
    def list_allocations(person_name: str = "", project_name: str = "", week_of: str = "") -> str:
        """List planned hours (allocations) — what people said they'd work on
        next week, per person/project/week_of. This is a PLAN, not actuals.

        Args:
            person_name: Exact full name to filter to one person. Empty for everyone.
            project_name: Exact project name to filter to one project. Empty for all projects.
            week_of: ISO date (YYYY-MM-DD) for the planning week. Empty for all weeks.
        """
        q = supabase.table("allocations").select(
            "week_of, planned_hours, people(full_name), projects(name)"
        ).order("week_of", desc=True)
        if week_of:
            q = q.eq("week_of", week_of)
        rows = _flatten(_rows(q), {"people": ("person", "full_name"), "projects": ("project", "name")})
        if person_name:
            rows = [r for r in rows if r["person"] == person_name]
        if project_name:
            rows = [r for r in rows if r["project"] == project_name]
        return json.dumps(rows, default=str)

    @beta_tool
    def list_time_entries(person_name: str = "", project_name: str = "", week_ending: str = "") -> str:
        """List actual logged hours (time_entries), per person/project/week_ending.

        Args:
            person_name: Exact full name to filter to one person. Empty for everyone.
            project_name: Exact project name to filter to one project. Empty for all projects.
            week_ending: ISO date (YYYY-MM-DD) for the week the hours were logged. Empty for all weeks.
        """
        q = supabase.table("time_entries").select(
            "week_ending, hours, source, people(full_name), projects(name)"
        ).order("week_ending", desc=True)
        if week_ending:
            q = q.eq("week_ending", week_ending)
        rows = _flatten(_rows(q), {"people": ("person", "full_name"), "projects": ("project", "name")})
        if person_name:
            rows = [r for r in rows if r["person"] == person_name]
        if project_name:
            rows = [r for r in rows if r["project"] == project_name]
        return json.dumps(rows, default=str)

    @beta_tool
    def list_actions(status: str = "open", project_name: str = "") -> str:
        """List actions raised during EOW — either an "ask" needing a
        decision, or an "fyi" for awareness only.

        Args:
            status: Filter by status ("open", "resolved", etc). Pass "all" for no filter.
            project_name: Exact project name to filter to one project. Empty for all projects.
        """
        q = supabase.table("actions").select(
            "kind, body, priority, needed_by, direction, status, raised_on, "
            "projects(name), people(full_name)"
        ).order("raised_on", desc=True)
        if status and status != "all":
            q = q.eq("status", status)
        rows = _flatten(_rows(q), {"projects": ("project", "name"), "people": ("raised_by", "full_name")})
        if project_name:
            rows = [r for r in rows if r["project"] == project_name]
        return json.dumps(rows, default=str)

    @beta_tool
    def list_flags(severity: str = "", project_name: str = "") -> str:
        """List open flags/barriers raised during EOW.

        Args:
            severity: Filter by severity, "info" or "critical". Empty for both.
            project_name: Exact project name to filter to one project. Empty for all projects.
        """
        q = supabase.table("flags").select(
            "severity, rule, body, status, raised_on, projects(name), people(full_name)"
        ).eq("status", "open").order("raised_on", desc=True)
        if severity:
            q = q.eq("severity", severity)
        rows = _flatten(_rows(q), {"projects": ("project", "name"), "people": ("person", "full_name")})
        if project_name:
            rows = [r for r in rows if r["project"] == project_name]
        return json.dumps(rows, default=str)

    @beta_tool
    def list_milestones(project_name: str = "", include_completed: bool = False) -> str:
        """List project milestones, ordered by due date.

        Args:
            project_name: Exact project name to filter to one project. Empty for all projects.
            include_completed: If true, include completed milestones too (default: only open ones).
        """
        q = supabase.table("milestones").select(
            "label, due_date, status, is_key, completed_on, projects(name)"
        ).order("due_date")
        if not include_completed:
            q = q.neq("status", "completed")
        rows = _flatten(_rows(q), {"projects": ("project", "name")})
        if project_name:
            rows = [r for r in rows if r["project"] == project_name]
        return json.dumps(rows, default=str)

    return [
        list_people, list_projects, get_capacity, get_burn,
        list_allocations, list_time_entries, list_actions, list_flags,
        list_milestones,
    ]


PLACEHOLDER_KEY = "paste Anthropic API key here"


def is_configured() -> bool:
    """False until a real ANTHROPIC_API_KEY is in secrets.toml — lets the
    page show a "not wired up yet" state instead of crashing, since this is
    deliberately being built ahead of Pete deciding whether/when to pay for
    API usage."""
    key = st.secrets.get("ANTHROPIC_API_KEY", "")
    return bool(key) and key != PLACEHOLDER_KEY


def _client() -> Anthropic:
    return Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])


def ask(supabase, history):
    """Answer the latest question in `history` (a list of {"role", "content"}
    dicts, text-only, with the new user turn already appended by the caller).

    Returns (answer_text, tool_calls) where tool_calls is a list of
    (tool_name, tool_input) for anything Claude looked up along the way.
    """
    messages = [
        {"role": h["role"], "content": h["content"]}
        for h in history
        if h["role"] in ("user", "assistant")
    ]

    tools = _build_tools(supabase)
    runner = _client().beta.messages.tool_runner(
        model=MODEL,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=messages,
    )

    tool_calls = []
    final = None
    for message in runner:
        final = message
        for block in message.content:
            if block.type == "tool_use":
                tool_calls.append((block.name, block.input))

    if final is None:
        return "No response from Claude.", tool_calls

    text = "\n".join(b.text for b in final.content if b.type == "text")
    return text or "(no text in response)", tool_calls
