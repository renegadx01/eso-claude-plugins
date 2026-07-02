# EOW ROLLUP — EXECUTIVE OVERVIEW
*Week ending {{DATE}}  ·  Prepared for MKW  ·  Sources: EOW Roadmap Reports from {{names}}*

---

<!--
WHAT THIS IS
============
The consolidated, Maggie-facing rollup. Built by consolidating the individual EOW
reports (see EOW_Individual_Report_TEMPLATE.md). One person's report feeds these
sections; everyone's reports stack into the dashboard, timeline, and snapshot.

HOW TO BUILD IT
===============
Say to Claude: "Build the MKW rollup from this week's reports."
Point eow_paths.BASE at the shared EOW_System folder; Claude reads the CURRENT week's
folder — eow_paths.week_folder() -> Submissions/<week>/ — ingests every per-person
sidecar (eow_data_<LastName>_<week>.json) and/or PDF there, and maps fields up. A report
missing from the folder is a visible gap to flag, never invented. Maps:
  - MKW items (all people)           -> Section 1, SPLIT IN TWO under one heading:
        * Action Required  = Action-type items, sorted 🔴 then 🟡 then 🟢
        * FYI / Awareness  = FYI-type items, no priority (project · note · who)
  - Maggie's own calendar/meetings   -> Section 2
  - Phase / Pace / Budget (all proj) -> Section 3 dashboard
  - OPEN milestones (the store)      -> Section 4 timeline chart (self-building)
  - Watch, risks, milestone slips,   -> Section 5 (temp-pace persistence flags too)
  - Wins this week                   -> Section 6
  - Each person's focus next week    -> Section 7
  - Each person's hours              -> Section 8 (reported total, utilization %,
                                        next-week allocated total, over/under 40)

WHY SECTION 1 IS SPLIT (Maggie's request): she wants an at-a-glance separation
between what she must ACT on and what is just for her AWARENESS. The type is set
upstream by each person on their individual report (Action vs FYI), so the rollup
just routes by that type — it never re-decides it. An Action escalated as urgent
sits at the top of Action Required; an FYI never carries a priority or a deadline.

NEVER QUERY THE PRINCIPAL — FLAG INSTEAD:
  Querying happens UPSTREAM, when each person fills their individual report. The rollup
  must NOT quiz Maggie. It generates even when inputs are incomplete and SURFACES every
  gap as a visible flag — missing reports ("⚑ Jesus's report not in"), missing fields,
  and any "TBD — confirm" carried up. Route the underlying questions back to the report
  owner, never to Maggie.

FLAG, DON'T GUESS:
  Carry any "TBD — confirm" or ambiguous owner/time straight through into Section 5 as a
  flagged "To confirm" row. Never invent an owner or a number to make the rollup look complete.

TEMPORARY-PACE & MILESTONE FLAGS (into Section 5; escalate to Section 1 Action Required if urgent):
  - ⚑ Milestone slipped: any lever/milestone whose date moved this week
    (eow_milestones.slipped_this_week()). The project stays at its temporary pace.
  - ⚑ Persistence: a temporary pace (Hold/Sprint/Catapult) whose lever is still open
    another week — flag once it's dragging ("Catapult entering week 3").
HOURS / OVER-CAPACITY FLAGS:
  - Any person whose reported hours OR next-week allocation exceed the 40-hr base carries
    an over-capacity MKW flag (eow_hours raises it). Numbers are kept, never scaled — Maggie
    decides priorities, reassignment, or approved overtime. Show it in Section 8 and, if
    urgent, Section 1 Action Required.

STANDING CONTEXT (do not surface as a question or risk):
  The AI team — Maggie (MKW), Jon, Steve, and Peter — are in constant communication and
  collaborate continuously on the platform/automation work.

ĒSO COMMAND FORMAT
==================
Render to the ĒSO letterhead (HTML + weasyprint; see scripts/render_mkw_rollup.py):
  - Header band (logo + split-circle mark) and footer band, fixed on every page.
  - Title: "EOW ROLLUP — EXECUTIVE OVERVIEW" (bold), italic gray subtitle line.
  - Numbered section headings with a thin rule under each.
  - Branded color key in tables:
        GREEN  #DCE9D5 = On Track       YELLOW #FBE9C9 = Monitor / this week
        RED    #F5D5CE = Urgent         GRAY   #EFEFEF = table header / FYI fill
        INK    #1A1A1A = text/rules     LIME   #C9D646 = accent
  - Font: Mabry Pro family.
  - Section 4 timeline is self-building on every run by MERGING every per-person
    store under <BASE_DIR>/stores/ (eow_milestones.load_all_stores -> timeline_points);
    point BASE_DIR at the shared EOW folder. Aborts if no open milestone exists.
-->

---

## 1. MKW ACTIONS — WEEK OF {{DATES}}

*Two blocks. **Action Required** = things Maggie must decide or do, sorted 🔴 Urgent first. **FYI / Awareness** = no decision needed, no priority. "Time / By" applies to Actions only and is the time Maggie spends acting — not the requester's staffing hours (those live in Section 8).*

Priority chips (Actions only): 🔴 Urgent = red `#F5D5CE` · 🟡 This week = yellow `#FBE9C9` · 🟢 When available = green `#DCE9D5`.

### Action Required

| Priority | Project | Ask | Requested by | Time / By |
|---|---|---|---|---|
| 🔴 Urgent | {{Project}} | {{What exactly Maggie must decide/do — full context}} | {{Name(s)}} | {{Time · by when}} |
| 🟡 This week | {{Project}} | {{Ask}} | {{Name}} | {{Time · by when}} |
| 🟢 When available | {{Project}} | {{Ask}} | {{Name}} | {{Time · by when}} |

### FYI / Awareness

| Project | Note | From |
|---|---|---|
| {{Project}} | {{Informational note for Maggie — no action needed}} | {{Name}} |

---

## 2. MKW CALENDAR — WEEK OF {{DATES}}

*Maggie's own meetings/reviews for the coming week.*

| When | Project | Ask | Time |
|---|---|---|---|
| {{Mon M/D}} | {{Project}} | {{What's needed from Maggie}} | {{30 min / 1 hr}} |
| {{All week}} | {{Project}} | {{Async item}} | {{Async / TBD}} |

---

## 3. PROJECT STATUS DASHBOARD

*Phase / Pace / Budget / next milestone for every active project. Budget cell uses the color key. Temporary paces show their lever milestone (e.g. "Sprint · until pricing set 6/15").*

| Project | Phase | Pace | Budget | Next Milestone |
|---|---|---|---|---|
| {{Project}} | {{SD/DD/CD/CA}} | {{Pace · lever if temp}} | {{color pill}} | {{milestone — date}} |

---

## 4. MILESTONE TIMELINE

*Self-building every run by merging all per-person stores under stores/ (deadlines/milestones ONLY, no actions/tasks). Key milestones in lime, others in ink. Aborts if no open milestone exists.*

{{timeline.png}}

---

## 5. WATCH ITEMS & FLAGS

*Soft barriers, risks, "TBD — confirm" carried up, milestone slips, and temporary-pace persistence. Escalate to Section 1 Action Required if marked urgent.*

| Area | Item |
|---|---|
| {{Project}} | {{Watch item / risk}} |
| ⚑ To confirm | {{Carried-up TBD — routed to owner, not Maggie}} |
| ⚑ Milestone slipped | {{Project — {label} moved {from} → {to}}} |
| ⚑ Persistence | {{Project — [Sprint/Catapult] entering week N, lever still open}} |

---

## 6. WINS THIS WEEK

*Includes every milestone completed this week.*

| Area | Win |
|---|---|
| {{Area}} | {{Win}} |

---

## 7. TEAM SNAPSHOT — FOCUS NEXT WEEK

| Person | Focus next week |
|---|---|
| {{Name}} | {{One-line focus, with rough hours by project}} |

---

## 8. HOURS RECONCILIATION

*One row per person. Reported = actual hours this week (Sheet A). Utilization = reported / 40. Allocated next wk = auto-derived from next-week paces (Sheet B). Over/Under = vs the 40-hr base. Any over-40 (reported or allocated) carries an MKW flag; numbers are kept, never scaled.*

| Person | Reported (this wk) | Utilization | Allocated (next wk) | Over / Under 40 |
|---|---|---|---|---|
| {{Name}} | {{hrs}} | {{%}} | {{hrs}} | {{⚑ +N over / N slack}} |
| **Team total** | **{{sum}}** | | **{{sum}}** | |
