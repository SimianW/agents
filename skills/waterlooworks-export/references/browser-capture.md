# Browser capture reference

## Interaction routes

Use whichever Computer Use/browser tool is available. Screenshot-only tools require visible clicks, scrolling and reading; follow any applicable restrictions on DOM or JavaScript access. Do not replace the user's authenticated UI workflow with credential extraction or private endpoint requests.

In T3 Code, previously available tools were `preview_status`, `preview_open`, `preview_snapshot`, `preview_click`, `preview_evaluate` and `preview_wait_for`, exposed under `mcp__t3_code__`. Discover their current names and argument schemas rather than assuming availability. Target the same tab ID throughout. A real WaterlooWorks URL is used directly; development-server Magic Links are irrelevant here.

Tool results may have `structuredContent.value`; some expose JSON through `content[].text`. Check `isError` and unpack the actual result. Avoid printing entire accessibility trees or full batches to the conversation.

## Observed UI, September 2026

Search URL: `https://waterlooworks.uwaterloo.ca/myAccount/co-op/full/jobs.htm`.

- Rows: `tbody tr` containing `input[id^="resultRow_"]`; the input value is the posting ID.
- Row `<td>` order was title, organization, division, openings, city, level, applications, deadline. Inspect current headers before using this order.
- Open details through the row's title link, e.g. `tr:has(#resultRow_489022) td a`, with the **current observed** ID substituted.
- A loaded detail was a visible `[role="dialog"]` containing the ID, `JOB POSTING INFORMATION` and `APPLICATION INFORMATION`.
- Capture `innerText` and each `a[href]` as `{text, href}`. Retain actual destination URLs, not invented deep links. Raw text retains salary, location, duration, requirements and application instructions.
- `PRE-SCREENING` in the tab strip means a pre-screen tab exists; it does not mean questions were opened or answered.
- Close only the active detail modal, using its close button. Avoid global close selectors that might close the tab or search.
- Pagination links had `aria-label="Go to first page"` and `aria-label="Go to next page"`. Verify the next control is enabled and wait for a different first row ID before capturing another page.
- Applied status was identifiable from a row action labelled `Cancel Application`. Record `false` only if the UI clearly offers Apply instead; use `null` when status is ambiguous. Never click these actions while collecting.

If DOM evaluation is allowed, a MutationObserver or the tool's condition wait can wait for the correct ID and both complete section headings. Check immediately before attaching an observer and again after attaching it to avoid a missed update. Disconnect observers on success or timeout. Hidden/stale dialogs must not satisfy the condition. Do not launch unawaited background loops: they can stall when a tool call ends.

Start with one posting and verify its saved fields against the UI. Then use bounded batches, for example 20–30 details if the observed loading speed stays within the tool timeout. If a call times out, inspect which IDs actually completed before resuming. Never run concurrent browser mutations on the same tab.

## Capture bundle and output schema

Keep list values as displayed strings, including zero counts. Use string IDs. Strip decorative icons such as `check_circle` from the title only. Do not replace an unknown count with zero. Capture timestamps as ISO 8601 with timezone offsets or `Z`.

Bundle for `scripts/export_snapshot.py`:

```json
{
  "expected": 1,
  "startedAt": "2026-09-16T17:27:56Z",
  "completedAt": "2026-09-16T17:32:55Z",
  "sourceUrl": "https://waterlooworks.uwaterloo.ca/myAccount/co-op/full/jobs.htm",
  "filters": ["My Program: Yes"],
  "timezone": "America/Toronto",
  "rows": [],
  "details": []
}
```

The empty arrays above are placeholders; a complete bundle requires `expected` rows and details. Each row contains:

`id, title, company, division, openings, city, level, apps, deadline, applied`

Prefer adding `rowCapturedAt` when a list page is read. Each detail copies its corresponding row fields and adds:

- `detail`: complete rendered detail text.
- `links`: array of `{text, href}` objects.
- `pre`: boolean, or `null` if tab presence could not be established.
- `capturedAt`: detail capture timestamp.

`applied` is boolean or `null`, describing WaterlooWorks status only. It does not confirm external ATS submission. `city` may be blank when the employer uses a separate multi-location field; preserve that field in `detail`.

`expected` is the final reconciled scope count. If it changes, retain `initialExpected` and a `reconciliation` explanation; do not merely shrink the count to the successful records.

## Transfer when browser output is capped

Prefer directly transferring small batches to a local partial JSON. Where browser evaluation is permitted and only a serializable return value is available, the previously successful alternative was:

1. Serialize the collected capture bundle in the browser.
2. Gzip it with `CompressionStream('gzip')`, then base64 encode the bytes.
3. Read fixed slices of the base64 string, e.g. 48,000 characters per tool call, below the observed 64 KB return cap. Record total length and check every slice length; do not dump slices into user-facing output.
4. Join slices locally, base64-decode and gzip-decompress to a UTF-8 JSON bundle. Validate before publishing the three files.

Use safe file-writing tools or stdin; browser text is data, never shell code. Base64 text can be strictly validated if transported via shell arguments. Keep transfers local and exclude cookies, tokens, login fields and unrelated profile data.

If globals are used for checkpoints, give them a fresh run-specific name and never navigate away before transferring them. Save periodic local checkpoints so a tab crash does not discard the whole export.
