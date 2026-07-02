---
name: eso-eow-reporting
description: Produce ĒSO / Point B Design Group End-of-Week reports — both the individual EOW report (filled by talking it through) and the consolidated MKW Rollup that reads everyone's individual reports and rolls them into one principal-facing document. Renders to a branded ĒSO PDF (letterhead, color key, milestone timeline). Trigger on "let's do my EOW report," "fill out my end of week," "build the MKW rollup," "weekly rollup for Maggie," "consolidate the team's EOW reports," or any weekly status reporting for the firm.
---

# ĒSO EOW Reporting

Two linked workflows. An **individual EOW report** that each person fills by talking it through, and a **consolidated MKW Rollup** that reads everyone's individual reports and produces one branded document for the principal (Maggie / MKW). Both render to a branded ĒSO PDF using the assets in this skill (no hand-written document XML — build HTML and render with weasyprint).

**Single source of truth (do not restate numbers elsewhere):** all hour bands, the reverse pace→hours lookup, the 40-hr base, and the over-cap flags live ONLY in `scripts/eow_hours.py`. The name→role map lives in `scripts/capacity.json`. Milestone records live in **per-person rolling stores** at `scripts/stores/milestones_<LastName>.json` (one file per employee, the single source of truth, carried week to week). The store API is in `scripts/eow_milestones.py`. The skill ships with NO real data — only a fictional `stores/milestones_SampleEmployee.json` for the format reference. This file and the templates describe behavior and point at those modules; they never reprint the band tables. If a number needs to change, change it in `eow_hours.py` and nowhere else.

**Missing information — two different behaviors:**
- **Individual report (Workflow 1): always query.** Never finalize or render with gaps. If any field is missing, vague, or ambiguous, ask before writing it, and keep asking until every field is confirmed or explicitly declared "nothing to report." A guessed value is a defect.
- **MKW Rollup (Workflow 2): never query the principal — flag instead.** Querying already happened upstream at each individual report. The rollup generates even when incomplete and surfaces gaps as visible flags (missing reports, missing fields, "TBD — confirm"), routing any questions back to the report owner, not Maggie.

Bundled files:
- `templates/EOW_Individual_Report_TEMPLATE.md` — the individual report structure + talk-to-fill interview script.
- `templates/EOW_MKW_Rollup_TEMPLATE.md` — the rollup structure + consolidation mapping.
- `assets/header_band.png`, `assets/footer_band.png` — the ĒSO letterhead bands (logo + split-circle mark; tagline + ĒSO-ARCH.COM footer).
- `scripts/render_eow_individual.py`, `scripts/render_mkw_rollup.py` — working render scripts (HTML + weasyprint).
- `scripts/eow_milestones.py` — milestone store API: per-person `store_path(person, base)` / `ensure_store(...)`, `load_all_stores(base)` (merges every employee's store for the rollup), `write_snapshot(...)` (weekly-folder archive copy), plus open/add/complete/slip helpers.
**Per-person file key (from the identity registry, `eow_paths.person_slug(person, base)`):** the report PDF (`EOW_Report_<Key>_<week>.pdf`), the `eow_data_<Key>_...json` sidecar, the `milestones_<Key>.json` store, and the snapshot all key the same way. The key is the person's LAST NAME, and automatically becomes First+Last (e.g. `JaneHall`) when two people share a last name — `eow_identity` handles this at first-run registration.

- `scripts/eow_paths.py` — shared-folder + weekly-submission convention: `BASE` (the shared EOW_System folder), `ensure_week_folder()` (first submitter creates `Submissions/<week>/`, others reuse it), `week_folder()`, `stores_dir()`. Week folders are named `YYYY.MM.DD - MM.DD` (week-starting Monday → Friday).
- `scripts/eow_identity.py` — first-run identity registry (`<BASE>/stores/identities.json`): `register(name, level, base)` captures the person's name + ĒSO level once and assigns a stable, collision-safe file key (last name; First+Last if two people share a last name); `get(...)` checks whether someone is already set up; `key_for(...)` resolves their key.
- `scripts/eow_hours.py` + `scripts/capacity.json` — **canonical** two-tier absolute-hours allocator (pace → hours by role), the reverse check, and the name→role map.
- `scripts/eow_export.py` — writes the structured sidecar JSON (`eow_data_<LastName>_<weekending>.json`) that the Week-at-a-Glance / Monday look-ahead skill consumes.
- `reference/EOW_*_SAMPLE.pdf` — what good output looks like.

---

## Workflow 1 — Individual EOW report (talk-to-fill)

**Default behavior — interview, never render the sample.** On trigger, immediately begin the talk-to-fill interview below, one project at a time (or, if the person asks how it works, explain the flow first). Do NOT output, paste, or render the bundled example. The data inside `scripts/render_*.py` is a fictional SAMPLE ("Sample Employee", Project Alpha/Beta/Gamma, wk 6/12) kept for format reference only — it must be replaced entirely with the current person's answers, and `SAMPLE_DATA` set to `False`, before anything renders. Never present the sample projects (Project Alpha, etc.) as this week's report.

When someone says "let's do my EOW report," **check whether they're set up** (memory pointer, or `eow_identity.get(name, BASE)`). **First run only — identity setup:** ask two things, then never again — (1) their **name** (have them type it out), and (2) their **ĒSO level** offered as a pick list — Associate / Senior Associate / Associate Principal / Principal / Senior Principal / **Operations Manager** — with the option to type their own. Call `eow_identity.register(name, level, BASE)` (returns their file `key` + `level`) and save a one-line pointer in memory (name, level, key) so it isn't asked again. The **level is the hours-tier role** (Associate tier vs everyone-else; passed straight to `eow_hours.allocate`/`report_check`) and the **key names all their files**. On later runs, read name/level/key from the pointer. Then work through `templates/EOW_Individual_Report_TEMPLATE.md`. **Do not ask one field at a time.** Per project, lay out the full checklist of what is needed, let the person dictate as much as they can in one pass (any order, by voice), map it onto the fields, then read back a SINGLE consolidated list of only what is still missing — and repeat until every field is resolved. If they paste raw OneNote notes, read those first and only ask about the gaps. The always-query rule still holds (every field confirmed or declared "nothing to report"); it is the asking STYLE that is batched, not the completeness bar.

**Per project, confirm all of:** Phase (SD/DD/CD/CA) · Pace this week (1–7) · Budget (1–4) · This-week outcomes · **Hours reported this week** · Look-ahead (each with a date) · Barriers (each with owner + path + date) · MKW item(s) · Open milestones resolved · **Next-week pace (1–7)**. Never write "None" without explicit confirmation.

**Operations Manager is the exception (overhead role, `eow_hours.is_overhead`).** This role does NOT use pace at all and works a flat 40-hr overhead week. When the person's level is Operations Manager: there is ONE preset project, **Operations and Admin** (do not ask which project), and you **skip Phase, Budget, Pace, and Next-week pace** entirely. Ask the same everything-else: this-week outcomes · hours · look-ahead (with dates) · barriers (owner + path + date) · MKW items (FYI/Action) · open milestones. Hours are flat 40 overhead — `eow_hours.allocate([], "Operations Manager", name)` returns the single 40-hr `Operations and Admin` row; do NOT run the implied-pace check (there is no stated pace). Sheet A still shows their reported hours; Sheet B shows the flat 40-hr overhead.

**MKW items — classify FYI vs Action first.** For each thing involving Maggie, ask the TYPE before the details:
- **Action** = Maggie has to decide or do something. Requires: what exactly + how long it takes her + by when + priority (🔴/🟡/🟢).
- **FYI** = awareness only, no decision or task for her. Requires: just the note + which project. **No deadline, no priority, no "Maggie's time"** — never invent those for an FYI.
A single project can have both an Action and an FYI; capture them separately. This type drives where the item lands in the rollup (Section 1 Action Required vs FYI / Awareness).

**Milestones are queried, not re-typed.** Milestones persist outside any single week and carry over until completed. They live in THIS PERSON's own store — resolve the path with `eow_milestones.ensure_store(person, base_dir)` (creates `stores/milestones_<LastName>.json` on first use; an individual report never touches anyone else's store). At capture, read back each project's OPEN milestones from that store and resolve every one before finalizing the project block:
- still on track → leave it (it carries to next week automatically);
- slipped → `slip_milestone()` — the old date is kept and the slip auto-surfaces in the rollup's flags;
- completed → `complete_milestone()` — it shows as a win this week and drops off next week's timeline.
Then ask for any NEW milestone (with date) → `add_milestone()`. An unaddressed open milestone is a defect, same as a blank field.

**Reported hours → derived-pace check (this week).** For each project, ask the actual hours logged. Run `eow_hours.report_check(stated_pace, reported_hours, role)` to derive the implied pace from the hours and compare it to the pace the person stated. If they disagree, flag it and have them confirm. Hours cannot separate Sprint from Heavy — confirm that label, never infer it. If the person's reported TOTAL exceeds the 40-hr base, `eow_hours.reported_overflow()` raises an MKW flag.

**Next-week hours are allocated, not asked.** Confirm each active project's NEXT-WEEK pace (1–7). Run `eow_hours.allocate(projects_next_pace, role, name)` — hours come straight from the band table in `eow_hours.py`, never hand-entered. Show the proposed table back for adjustment. Keep the numbers as-is: if the total exceeds 40, do NOT scale down; surface the returned `mkw_flag`. Under 40 shows as slack.

**On finalize, save to the shared week folder.** Set `eow_paths.BASE` to the shared `EOW_System` folder in the user's workspace, then resolve this week's drop folder once: `wk = eow_paths.ensure_week_folder()` (the FIRST submitter that week creates `Submissions/<week>/`; everyone else reuses the same folder — `week` is `YYYY.MM.DD - MM.DD`, the week-starting Monday → Friday). Write all three of the person's artifacts into `wk`:
1. the rendered **PDF** (`EOW_Report_<LastName>_<week>.pdf`);
2. the **sidecar** — `eow_export.build_payload(..., focus=<one-line next-week focus>)` + `write_sidecar(payload, out_dir=wk, base=BASE)` (MKW items carry their `kind` "action"/"fyi"; include the person's one-line `focus` so Week-at-a-Glance can show team alignment; the Monday look-ahead reads this JSON, never the PDF);
3. the **milestone snapshot** — `eow_milestones.write_snapshot(records, wk, person)` (read-only archive copy).
The rolling per-person store at `eow_paths.stores_dir()/milestones_<LastName>.json` stays the source of truth (update it via `ensure_store`/add/slip/complete); the snapshot is archive only. Optionally record a one-line pointer in memory (store path + the person's role) — never a copy of the milestones.

**Two hours sheets close the loop (see template for layout):** Sheet A = Hours Reported (actuals, implied-pace check, variance vs last week's Sheet B, utilization vs 40). Sheet B = Hours Allocated next week (auto-derived from next-week pace, total vs 40).

## Workflow 2 — MKW Rollup (consolidate everyone)

When someone says "build the MKW rollup," point `eow_paths.BASE` at the shared `EOW_System` folder and read the CURRENT week's submission folder — `eow_paths.week_folder()` (resolve a prior week by passing its Monday). Consume every `eow_data_<LastName>_<week>.json` sidecar (and/or PDF) found there, and map fields up into the eight sections in `templates/EOW_MKW_Rollup_TEMPLATE.md`:
- Every person's **MKW items** → Section 1, which is split in two under one heading: **Action Required** (the Action-type items, sorted 🔴 Urgent, then 🟡 This week, then 🟢 When available) and **FYI / Awareness** (the FYI-type items, no priority — just project, note, who).
- The principal's own meetings → Section 2 (Calendar).
- Every project's Phase / Pace / Budget / next milestone → Section 3 (Dashboard).
- Every open milestone, across ALL people → Section 4 (Milestone Timeline chart), built by merging every per-person store via `eow_milestones.load_all_stores(base_dir)`.
- Watch items + soft barriers + **milestone slips + temporary-pace persistence flags** → Section 5 (escalate to Section 1 Action Required if marked urgent). Wins → Section 6. Each person's next-week focus → Section 7.
- Each person's **hours**: reported total, utilization %, next-week allocated total, over/under 40 (and any over-time MKW flag) → Section 8 (Hours reconciliation).

Inputs are the per-person sidecars (and PDFs) sitting in this week's `Submissions/<week>/` folder. A report missing from the folder is a visible gap — flag it ("⚑ Jane's report not in"), never invent it. Milestones live in per-person rolling stores under `<BASE>/stores/milestones_<LastName>.json`; the rollup timeline merges them all via `load_all_stores(BASE)` (set `render_mkw_rollup.BASE_DIR` to the same `EOW_System` folder). As connectors come online both the folder and the stores can move to SharePoint without changing the helper interface. **The rollup saves into that same current-week folder** — `render_mkw_rollup.py` writes `EOW_MKW_Rollup_<week>.pdf` into `Submissions/<week>/` (via `eow_paths.ensure_week_folder(BASE_DIR, week_monday(WEEK_END))`) on real runs, so Maggie's rollup lands beside the individual reports it consolidated. (Sample runs stay in the working dir.)

---

## Data model (internal — do not print these definitions)

**Pace:** 1 Hold · 2 Maintenance · 3 Light · 4 Moderate · 5 Sprint · 6 Heavy · 7 Catapult. Hold/Sprint/Catapult are temporary (lever-locked). The hour value of each pace, per role tier, is defined ONLY in `scripts/eow_hours.py` — read it there, never restate it.
**Budget:** 1 On Track · 2 Monitor · 3 Concern · 4 Critical.
**MKW item kind:** `action` (what + how long + by when + priority) or `fyi` (note + project only).
**OneNote shorthand:** `~~done~~` → outcomes · `*starred*` → look-ahead · `MKW` → Maggie ACTION · `FYI` (or `MKW-FYI`) → Maggie FYI/awareness · `!` → barrier.
**Milestone record:** id · project · label · date · status (open/complete) · key · completed_on · slips[] (from/to/recorded_on). See `eow_milestones.py`.

### Pace → hours and the reverse check
Two tiers on a flat 40-hour base — **Associate** vs **Everyone else** (Sr Associate / Assoc Principal / Principal / Sr Principal). Role (from `capacity.json`) selects the column; it does not scale a capacity number. **All band values, the reverse hours→pace lookup, the "top of band" rule, and the over-40 flags are canonical in `scripts/eow_hours.py`** (functions `allocate`, `report_check`, `derive_pace`, `reported_overflow`). Call those functions; do not maintain a copy of the numbers anywhere else.

### Temporary paces — lever lock (Hold · Sprint · Catapult)
A temporary pace is a pace **plus a lever**, and the lever is tracked as a **milestone record** in the store (not a loose string). It is **locked** to that milestone:
- **Setting** a temporary pace requires its lever to exist as an open milestone (`add_milestone()` if new). A temporary pace with no lever is incomplete — ask for it.
- **The pace cannot change while the lever is open.** Do not let someone move off a temporary pace unless its milestone is completed.
- **Only `complete_milestone()` unlocks** the pace → it then transitions to a non-temporary resting pace (Maintenance / Light / Moderate / Heavy), and the milestone shows as a win this week.
- The lever may be **moved** via `slip_milestone()` (old date kept, surfaces as a slip flag) — but the project **stays at its temporary pace** against the new date.
- **Persistence:** a temporary pace whose lever is still open another week ages — flag once it's dragging ("Catapult entering week 3 — lever still open").

This lever-lock logic is canonical here; the individual template references it rather than restating it. Run the lever lock before accepting any next-week pace change on a temporary project.

## Rules (enforce on every report)
Outcomes not activities · cap 3–4 outcomes per project · every look-ahead and milestone needs a specific date · every barrier needs owner + resolution path + date · every MKW **Action** needs what + how long + by when + priority · every MKW **FYI** needs only the note + project (no deadline, no priority) · never carry, move, or drop a milestone without explicit confirmation · temporary paces stay locked to their lever (only completion unlocks) · next-week hours are auto-derived from pace via `eow_hours.py`, never hand-entered · hours over the 40 base (reported or allocated) flag to MKW, never scaled away.

---

## Rendering to branded PDF (the ĒSO command format)

Build an HTML document and render with `weasyprint`. The timeline needs `matplotlib`. Install both: `pip install weasyprint matplotlib --break-system-packages`. Do NOT write Word/OOXML by hand. Adapt `scripts/render_mkw_rollup.py` or `scripts/render_eow_individual.py`.

**Section 4 (Milestone Timeline) is mandatory and self-building.** The rollup render builds the timeline inline by merging every per-person store under `<BASE_DIR>/stores/` (`eow_milestones.load_all_stores`) on every run, and aborts if no open milestone exists. Never embed a pre-existing or prior-week timeline image.

**Letterhead (every page):** embed `assets/header_band.png` and `assets/footer_band.png` as `position: fixed` elements (top and bottom). Reserve page margins:
```
@page { size: Letter; margin: 2.65cm 1.45cm 1.95cm 1.45cm; }
#hdr { position: fixed; top: -2.2cm; left:0; right:0; }
#ftr { position: fixed; bottom: -1.55cm; left:0; right:0; }
#hdr img, #ftr img { width:100%; display:block; }
```
**Brand:** Font Mabry Pro (fallback Helvetica/Arial). Color key — green `#DCE9D5` On Track · yellow `#FBE9C9` Monitor · red `#F5D5CE` Urgent · gray `#EFEFEF` header fill · ink `#1A1A1A` · lime accent `#C9D646`.
