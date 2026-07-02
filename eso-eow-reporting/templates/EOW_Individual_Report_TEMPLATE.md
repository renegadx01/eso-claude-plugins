# END OF WEEK REPORT — INDIVIDUAL (TALK-TO-FILL)
**Submitted by:** {{NAME}}  ·  **Role:** {{ROLE}}
**Week Ending:** {{DATE}}

---

<!--
HOW TO USE — TALK TO FILL
=========================
You do not type this report. You talk it.

ALWAYS-QUERY RULE (non-negotiable): never produce, finalize, or render the report
with gaps. For every project and every field, if anything is missing, vague, or
ambiguous, ASK before writing it down. Keep asking until each field is confirmed
or explicitly declared "nothing to report." A guessed value is a defect.

Say to Claude: "Let's do my EOW report."
Claude first confirms your ROLE (sets your hours tier), then shows you the FIELD
CHECKLIST below for each project and lets you DICTATE as much as you can in one go
— any order, by voice. Claude fills the report, cleans up the language, enforces
the rules, derives your hours, then reads back only the GAPS as a single list for
you to fill. It does NOT march through one question at a time, and it never renders
the bundled SAMPLE (the example projects in scripts/render_*.py) as your report.

You can also paste raw OneNote notes and say "populate from these" — Claude reads
them first, then only asks about the gaps.

ONENOTE SHORTHAND KEY (Claude reads these automatically if you paste notes):
  ~~crossed out~~   = Completed this week        -> "This Week — Outcomes"
  *asterisk*        = Needs to happen next week   -> "Look Ahead — Next Week"
  MKW               = Maggie needs to DECIDE/ACT  -> Section 1 "Action Required"
  FYI (or MKW-FYI)  = Maggie awareness only       -> Section 1 "FYI / Awareness"
  !exclamation      = Barrier                     -> "Barriers"

ROLE & HOURS TIER (set once, top of report; from scripts/capacity.json):
  Two tiers on a flat 40-hour base. ASSOCIATE has its own column; EVERYONE ELSE
  (Sr Associate, Assoc Principal, Principal, Sr Principal) shares one. Role picks
  the column used to auto-allocate next week's hours. Default = "Everyone else".

HOURS — ALL NUMBERS LIVE IN scripts/eow_hours.py (do not restate them here):
  Next-week hours: eow_hours.allocate(projects_next_pace, role, name) — never hand-enter.
  This-week consistency check: eow_hours.report_check(stated, reported, role) derives the
  implied pace from the hours and flags a mismatch with the stated pace. Sprint vs Heavy
  can't be told apart from hours — confirm that label. If reported total > 40,
  eow_hours.reported_overflow() raises an MKW flag (over actual time -> route to Maggie).

TEMPORARY PACES — LEVER LOCK (Hold, Sprint, Catapult):
  A temporary pace = a pace PLUS a lever (a milestone record in scripts/eow_milestones.py).
  The full lever-lock rule is canonical in SKILL.md. In short: you cannot move off a
  temporary pace while its lever milestone is open; only completing it unlocks the pace;
  the lever can be slipped (old date kept, surfaces as a flag) but the pace stays put.

BUDGET (internal — do not display in report):
  1 On Track · 2 Monitor · 3 Concern · 4 Critical

REPORT RULES (Claude enforces these as you talk; full list is in SKILL.md):
  - Outcomes, not activities: "Sent structural backgrounds; received proposal" — not "coordinating with structural."
  - Cap outcomes at 3–4 lines per project. Decisions, things sent/received, milestones hit. Cut the rest.
  - Every look-ahead item and milestone needs a specific date: "Jun 5," not "next week."
  - Every barrier needs: owner + resolution path + target date. A barrier without an owner is an observation.
  - MKW items are classified by TYPE first:
      ACTION (Maggie decides/does something) needs: what exactly + how long it takes her + by when + priority (🔴/🟡/🟢).
      FYI (awareness only) needs: just the note + the project. NO deadline, NO priority, NO "Maggie's time."
  - FLAG, DON'T GUESS: if an owner, a time estimate, or who-does-what is ambiguous, write "TBD — confirm" and flag it. Never invent a value to fill a cell.
  - DECIDED is not COMMUNICATED: a decision made internally but not yet relayed becomes a look-ahead comms task ("Notify [party] of [decision] — [date]").
  - MKW Action "time to act" = the time MAGGIE spends doing it. It is NOT your staffing hours (those live in the Hours sheets).
  - HOURS: report ACTUAL hours this week (Sheet A); next week's hours are AUTO-DERIVED from the next-week pace (Sheet B). Over the 40 base, reported or allocated, flags to MKW — never scaled away.

MISSING INFORMATION PROTOCOL (ALWAYS QUERY):
  Do NOT finalize a project block until Phase, Pace, Budget, Hours reported, Look-Ahead,
  Barriers, MKW items (each typed Action or FYI), every OPEN milestone, and Next-week pace
  are confirmed or explicitly declared "nothing to report." Never write "None" without
  confirmation. Ask for any gaps as ONE consolidated list, never one item at a time. For any
  temporary pace, its lever must be an open milestone; run the lever lock on any change.

FONT (when rendered): Mabry Pro family. Brand: ĒSO command format (see rollup template).
-->

---

## FIELD CHECKLIST — what each project needs (dictate in any order; Claude fills, then asks only about gaps)

**First (once):** "What's your role — Associate, Senior Associate, Associate Principal, Principal, Senior Principal, or Operations Manager?" *(Sets the hours tier; see scripts/capacity.json.)*

**If the role is Operations Manager (overhead role):** there is ONE preset project, **Operations and Admin** (do not ask which project), and you **skip Phase, Budget, Pace, and Next-week pace**. Ask everything else as normal: outcomes, hours, look-ahead (dated), barriers, MKW items (FYI/Action), and milestones. Hours are a flat 40-hr overhead week (no pace, no implied-pace check); Sheet B shows 40 on Operations and Admin.

**Per project, Claude needs all of the following — dictate what you can in one go; Claude fills what you give and then asks only about whatever is left blank:**

1. "Which project, and what phase is it in — SD, DD, CD, or CA?"
2. "What actually happened this week? What got sent, received, decided, or finished?" *(Claude keeps only outcomes, caps at 3–4.)*
3. "What pace was it this week, 1 to 7?" — and — "Where's the budget, 1 to 4?"
4. "How many hours did you actually put on it this week?" *(Claude runs `report_check` — derives the implied pace from the hours and flags any mismatch with #3. Sprint vs Heavy can't be inferred from hours — confirm the label.)*
5. "What's coming next week, and on what date each?" *(Claude rejects 'soon'/'next week' and asks for the date.)*
6. "Anything blocking you? If so — who owns it, how does it get unblocked, and by when?"
7. "Anything for Maggie on this project? For EACH item, first: is it an **ACTION** (she has to decide or do something) or an **FYI** (just awareness)?"
   - If ACTION: *"What exactly, how long will it take her, by when, and how urgent (🔴 urgent / 🟡 this week / 🟢 when available)?"*
   - If FYI: *"What's the note?"* — that's all; Claude does NOT ask for a deadline or priority on an FYI.
   *(A project can have both. Claude rejects an Action missing its time/by/priority, and never invents those for an FYI.)*
8. **MILESTONE CHECK — read the open ones back, don't ask from scratch.** Claude loads this project's OPEN milestones from THIS PERSON's own store — `eow_milestones.ensure_store(person, base_dir)` resolves `stores/milestones_<LastName>.json` (created on first use; never touches anyone else's store) — and reads them out: *"On {project} you have open: {label} — {date}. For each: still on track, slipped to a new date, or completed this week?"* On track leaves it; a new date calls `slip_milestone()` (old date kept, auto-flags in the rollup); "done" calls `complete_milestone()` (becomes a win, drops off next week's timeline). Then: *"Any NEW milestone for {project}, with its date?"* → `add_milestone()`. An unaddressed open milestone is a defect. On finalize, the report saves to the shared week folder: `eow_paths.ensure_week_folder()` resolves (and, if you're the first to submit this week, creates) `Submissions/<week>/`, and your PDF + sidecar JSON + a read-only milestone snapshot all drop in there. The rolling per-person store remains the source of truth; the snapshot is archive only.
9. **NEXT-WEEK PACE.** *"Next week — what pace is this project headed to, 1 to 7?"* Drives the auto-allocation. **If the project is at a TEMPORARY pace (Hold/Sprint/Catapult), run the lever lock** (see SKILL.md): a change off it is allowed only if its lever milestone was completed in step 8; otherwise the pace stays put and the slip flags to Maggie. Setting a new temporary pace requires its lever to exist as an open milestone.

**At the end, Claude builds the two hours sheets automatically:** Sheet A from #4 (with the derived-pace check and the over-40 MKW flag), Sheet B from #9 via `eow_hours.allocate(...)`.

---

## THIS WEEK — PROJECTS

<!-- One block per project, rendered in the ĒSO command format. -->
### {{PROJECT}}  ·  {{PHASE}}  ·  Pace: {{PACE}} {{(lever milestone, if temporary)}}  ·  Budget: {{BUDGET}}  ·  {{HRS}} hrs
- **Outcomes:** {{3–4 outcome lines}}
- **Look ahead:** {{item — date}}
- **Barriers:** {{barrier — owner — resolution path — target date}}  *(or "None.")*
- **MKW — Action:** {{what — Maggie's time — by when — priority}}  *(or "None this week.")*
- **MKW — FYI:** {{awareness note}}  *(or omit if none)*
- **Open milestones:** {{label — date — on track / slipped / completed}}

---

## SHEET A — HOURS REPORTED (week ending {{DATE}})

*Actuals for the week just ended. Implied pace = reverse lookup (`eow_hours.derive_pace`); Check flags stated ≠ implied; Allocated-last-wk auto-fills from the prior week's Sheet B (shows "—" if none); Variance = Reported − Allocated. If the total exceeds 40, an over-time MKW flag is raised.*

| Project | Pace stated | Reported | Implied pace | Check | Allocated last wk | Variance |
|---|---|---|---|---|---|---|
| {{Project}} | {{Pace}} | {{hrs}} | {{derived}} | {{✓ / ⚑ mismatch}} | {{hrs / —}} | {{±hrs}} |
| **Total** | | **{{sum}}** | | | **{{sum}}** | **{{±}}** |

**Utilization:** {{reported total}} / 40 = {{%}}  {{⚑ over actual time — flag to MKW, if >40}}

---

## SHEET B — HOURS ALLOCATED, NEXT WEEK (week of {{NEXT DATES}})

*Forward-looking. Hours auto-derived from each project's next-week pace via `eow_hours.allocate` — not hand-entered. Temp column carries the lever milestone and its status.*

| Project | Next-wk pace | Allocated | Temp — lever / status |
|---|---|---|---|
| {{Project}} | {{Pace}} | {{hrs}} | {{— / lever milestone + status}} |
| **Total** | | **{{sum}}** | |

**Capacity check:** {{allocated total}} / 40 → {{"⚑ overcommitted by N hrs — flag to MKW" or "N hrs slack"}}

---

## WINS / WATCH / FOCUS
- **Win this week:** {{win — include any milestone completed}}
- **Watch / risk:** {{watch — include milestone slips and temp-pace persistence}}
- **Focus next week:** {{one-line focus}}
