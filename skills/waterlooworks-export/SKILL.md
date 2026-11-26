---
name: waterlooworks-export
description: Export every posting from a WaterlooWorks job search to dated JSON files.
disable-model-invocation: true
---

# WaterlooWorks export

Produce a fresh snapshot of the selected WaterlooWorks search by opening each posting's detail page. Use the browser's logged-in session and preserve the site's displayed data.

## 1. Open and authenticate

Discover the available Computer Use/browser tools and read their tool schemas before calling them. If an actual computer-use skill is available and applicable, read it and follow its interaction constraints. This skill does not assume a tool or skill literally named `computer-use` exists.

Inspect the current browser tab before navigation. Reuse an existing WaterlooWorks session; otherwise open `https://waterlooworks.uwaterloo.ca/home.htm`.

If redirected to the university sign-in or MFA page, ask the user to complete login in the browser. Keep the tab open, and resume after their reply by inspecting it again. Do not request a password or MFA code in chat or read credentials from browser storage. If login is already complete, continue without asking again.

Completion: a logged-in WaterlooWorks page is visible.

## 2. Establish scope

Navigate through **Co-op → Full-cycle service → Jobs / Applications**, then open the job search if necessary. Labels may change; inspect the current UI.

For “same as before,” use **My Program: Yes** unless the user specified another search. Preserve an explicitly selected folder or filter. Do not silently substitute the old Top 70, saved jobs, or a previous snapshot for the current full search.

Record the URL, visible filters, current result count, and start time. Tell the user which search and how many jobs will be captured. Read all pages, starting from the first; do not assume the previous count of 721 or 719 still applies.

Completion: the intended search scope and its displayed count are recorded.

## 3. Capture each posting

Use [browser capture reference](references/browser-capture.md) for the observed table/modal selectors, batching, schema and transfer procedure. Treat those selectors as examples to verify, not a stable API.

For each list page, collect its rows and timestamp, then open each job title. Wait for a detail view containing that job's exact ID and complete job/application information. Capture the rendered detail text and links before closing it and moving on. Preserve whitespace and labels in the original detail text; extract additional structured fields only as an optional supplement.

Use an ID-keyed checkpoint to avoid duplicates. Await each detail load and each page change. Keep batches shorter than the browser tool's timeout, and persist completed batches locally where practical. Report progress about once per minute.

Exporting authorizes reading, pagination and opening/closing details. It does not authorize applying, cancelling applications, saving jobs, removing results or changing documents. Opening a posting may naturally mark it Viewed. Keep the user-selected filters stable; if a Viewed/New filter causes the result set to change as jobs are opened, capture the initial ID list first or clarify the intended scope.

If a detail fails, preserve the checkpoint, inspect the browser and retry that ID once. On a repeated failure or expired session, stop dependent collection and report the affected IDs or ask the user to log in again. Never fill a failed current detail with an old snapshot. Resume by ID after inspecting the actual page state.

Completion: every intended ID has a fresh, complete detail, with no unresolved failures. If results change mid-run, reconcile page boundaries and missing IDs; document the change rather than asserting a false total.

## 4. Export and verify

Default destination: `research/` under the user's current project. Use the capture date in `America/Toronto`, unless a different timezone/destination was requested. Preserve earlier captures; use a timestamp suffix for another capture on the same date.

Write a capture bundle following the reference, then run:

```bash
python3 <skill-directory>/scripts/export_snapshot.py <capture.json> \
  --output-dir <project>/research --stem waterlooworks-YYYY-MM-DD \
  --previous <optional-previous-source.json>
```

Omit `--previous` when no comparison is needed. The exporter validates unique IDs, row/detail correspondence and required fields before producing:

- `*-source.json`: complete posting records, including raw detail text and links.
- `*-rows.json`: lightweight list-page records.
- `*-metadata.json`: scope, timestamps, coverage and optional ID/count comparison.

For incomplete captures, keep a clearly named `*.partial.json` checkpoint and report the gap; do not run the complete-snapshot exporter or label partial results complete.

Completion: files parse as JSON, each intended job appears exactly once, required sections are present, and counts match the reconciled scope. In the final reply, link the source file, report captured/expected counts and any limitations, and briefly distinguish the other two files if supplied. Treat missing IDs in a comparison as “not in the current results,” not necessarily deleted jobs.
