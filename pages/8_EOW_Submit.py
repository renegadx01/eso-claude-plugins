import json

import pandas as pd
import streamlit as st

from lib.branding import brand_header
from lib.eow_writer import process_payload, test_connection

brand_header("EOW Submit — load sidecar JSONs into Supabase")
st.caption(
    "Upload one or more EOW sidecar JSON files (the `eow_data_*.json` files "
    "produced by the EOW skill). Preview what will be written, then confirm. "
    "Handles all three schema variants in the wild. Re-submitting the same "
    "week is safe — allocations overwrite, actions/flags are deduped."
)

# ── connectivity check ──────────────────────────────────────────────────────
try:
    n_people = test_connection()
except Exception as e:
    st.error(f"Cannot reach Supabase: {e}")
    st.stop()

st.caption(f"Connected — {n_people} people in DB.")

# ── file upload ─────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Drop EOW sidecar JSON files here",
    type="json",
    accept_multiple_files=True,
    help="eow_data_<Person>_<date>.json — one or more at a time.",
)

if not uploaded:
    st.info("Upload at least one `eow_data_*.json` to continue.")
    st.stop()

# ── parse uploads ───────────────────────────────────────────────────────────
payloads = []
parse_errors = []
for f in uploaded:
    try:
        payloads.append((f.name, json.loads(f.read())))
    except Exception as e:
        parse_errors.append(f"{f.name}: {e}")

if parse_errors:
    for err in parse_errors:
        st.error(f"Parse error — {err}")

if not payloads:
    st.stop()

# ── dry-run preview ─────────────────────────────────────────────────────────
st.subheader("Preview")

dry_results = []
all_unresolved = []

for fname, payload in payloads:
    result = process_payload(payload, dry_run=True)
    dry_results.append((fname, result))
    for s in result.get("skipped", []):
        all_unresolved.append({"file": fname, "type": s["type"], "name": s["name"]})

# Summary table
summary_rows = []
for fname, r in dry_results:
    rows = r.get("rows", {})
    summary_rows.append({
        "person": r.get("person", fname),
        "week ending": r.get("week_ending", ""),
        "next week of": r.get("next_week_of", ""),
        "allocations": len(rows.get("allocations", [])),
        "actions": len(rows.get("actions", [])),
        "flags": len(rows.get("flags", [])),
        "unresolved": len(r.get("skipped", [])),
    })

st.dataframe(
    pd.DataFrame(summary_rows),
    hide_index=True,
    width="stretch",
)

total_alloc = sum(r["allocations"] for r in summary_rows)
total_act   = sum(r["actions"]     for r in summary_rows)
total_flags = sum(r["flags"]       for r in summary_rows)
total_unres = sum(r["unresolved"]  for r in summary_rows)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Allocations", total_alloc)
col2.metric("Actions",     total_act)
col3.metric("Flags",       total_flags)
col4.metric("Unresolved",  total_unres, help="Projects not yet in Supabase — rows skipped, not an error.")

if all_unresolved:
    with st.expander(f"{total_unres} unresolved project name(s) — will be skipped"):
        st.caption(
            "These project names appear in the sidecar but don't match any "
            "project in Supabase. Add them via the Supabase dashboard or the "
            "projects table, then re-submit to capture the missing rows."
        )
        st.dataframe(pd.DataFrame(all_unresolved), hide_index=True, width="stretch")

# ── write confirmation ──────────────────────────────────────────────────────
st.subheader("Write to Supabase")

if total_alloc == 0 and total_act == 0 and total_flags == 0:
    st.warning(
        "Nothing resolved to write — all project names unresolved or files "
        "are empty. Add the projects to Supabase first."
    )
    st.stop()

confirmed = st.checkbox(
    f"I've reviewed the preview above and want to write "
    f"{total_alloc} allocations, {total_act} actions, and {total_flags} flags "
    f"to Supabase."
)

if not confirmed:
    st.caption("Check the box above to enable the write button.")
    st.stop()

if st.button("Write to Supabase", type="primary"):
    written_summary = []
    errors = []
    progress = st.progress(0, text="Writing…")

    for i, (fname, payload) in enumerate(payloads):
        progress.progress((i) / len(payloads), text=f"Writing {payload.get('person', fname)}…")
        try:
            result = process_payload(payload, dry_run=False)
            written = result.get("written", {})
            dupes   = result.get("skipped_duplicates", {})
            written_summary.append({
                "person": result.get("person", fname),
                "allocations written": len(written.get("allocations", [])),
                "actions written":     len(written.get("actions", [])),
                "flags written":       len(written.get("flags", [])),
                "dupes skipped":       sum(dupes.values()),
                "unresolved":          len(result.get("skipped", [])),
            })
        except Exception as e:
            errors.append(f"{fname}: {e}")

    progress.progress(1.0, text="Done.")

    if errors:
        for err in errors:
            st.error(err)

    if written_summary:
        st.success(
            f"Written — {sum(r['allocations written'] for r in written_summary)} allocations, "
            f"{sum(r['actions written'] for r in written_summary)} actions, "
            f"{sum(r['flags written'] for r in written_summary)} flags."
        )
        st.dataframe(pd.DataFrame(written_summary), hide_index=True, width="stretch")
        st.caption("Refresh the MKW Rollup, Team Needed, or Firm KPIs pages to see the updated data.")
