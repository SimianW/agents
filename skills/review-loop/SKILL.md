---
name: review-loop
description: Use before pushing or merging a change that meets the AGENTS.md Reviews triggers or the repo's review rule, or when the user says "review loop".
---

# review-loop

A **panel** of three models from three families reviews the diff **blind**
and in parallel. You, the lead, merge their findings into one **ledger**,
**cross-check** every solo finding with the other seats, fix what holds up in
one batch, and re-check narrowly. Evidence settles findings, not votes or
confidence.

Make the smallest changes that settle confirmed findings. Watch for scope
creep, and push back with evidence.

## Panel

| Seat | Model, effort | Id prefix | T3 `target` |
|---|---|---|---|
| Sol | `gpt-6.2-sol`, high | `S` | `{"providerInstanceId": "codex", "model": "gpt-6.2-sol", "options": {"reasoningEffort": "high"}}` |
| Opus | `claude-opus-5-5`, high | `O` | `{"providerInstanceId": "claudeAgent", "model": "claude-opus-5-5", "options": {"effort": "high"}}` |
| Neon | `gemini-4-neon`, high | `N` | `{"providerInstanceId": "antigravity", "model": "gemini-4-neon", "options": {"thought_level": "high"}}` |

This table sets the reviewers for this skill, in place of the CLAUDE.md
Hunt row. Swap a seat only when the user names another model.

**Routing.** In T3, call `orchestrator_capabilities` once. Every panel and
cross-check call is a new `delegate_task` (`role: "review"`,
`mode: "async"`) with a new `clientRequestId`; save each `taskId`.
`childThreadId` is storage, not a target: review runs only through
`delegate_task`, never `t3_thread_send`, `create_threads`, or
`t3_thread_launch`. Outside T3, run the seats your harness reaches natively
(Opus in Claude Code, Sol in Codex) and keep each subagent ID.

**Short seat.** A seat that cannot run (provider missing, credits out, two
failed starts) drops out. Two seats still make a panel. With one seat left,
ask the user once which model fills in. Name the seats that ran in the
report and PR.

## Ledger

One row per merged finding, kept from round 1 to the report:

- `L` id, and the seat ids it merges (`L1` = `S1`, `N2`);
- severity: `blocker`, `should`, or `nit`;
- found by, and cross-check result (confirmed by / refuted by);
- outcome: `open`, `fixed`, `disputed`, `declined`, or `overridden`;
- evidence: file:line trace, repro, or test output.

Also count each seat's calls (panel plus cross-check) and record usage when
a tool returns it. Never guess either.

## Budget

- If the repo has `scripts/review-tier.py` or `scripts/check-pr-body.py`,
  run its tier mode (`check-pr-body.py tier <base>`). Tier 0: no review.
  Tier 1: up to 2 rounds. Tier 2: up to 3.
- No tier script: 2 rounds; 3 for security, permissions, auth, data loss,
  or state/concurrency, or when the user asks.
- 3 rounds is the ceiling; only the user lifts it.
- A round is one panel pass plus its merge and cross-check. Cross-check
  calls are part of their round.
- Round 1 leaving only nits ends the loop. Declined nits and comment, doc,
  or format-only fixes need no new round.

## 1. Scope

Run `git status --short`. Leave unrelated changes out: no stash, no
discard. Limit review to the change paths if they separate cleanly.
Otherwise stop and ask.

Find the base after `git fetch origin`:

- PR: `gh pr view <n> --json baseRefName,headRefOid`. Check out the branch
  only if clean. Confirm `HEAD` is the PR head, or ahead only by this
  change. Base: `git merge-base HEAD origin/<baseRefName>`.
- Local: `git merge-base HEAD origin/<default-branch>`. No remote: a base
  the user names, or `HEAD` for uncommitted changes only.

The change is base to working tree in those paths, with untracked files.
Use one diff command all rounds. State intent and out-of-scope in 1-2
sentences. Run covering checks; send only code that passes them. If a check
needs set-up (dependencies, browsers), do it before round 1 and say so in
`Checks:`, so every seat can rerun it. Note missing or pre-failing checks in
the brief.

## 2. Round 1: blind panel

Start every seat in one message, in parallel, with the same brief. Each seat
sees only its own brief, never another seat's findings: blindness is what
makes overlap meaningful. Wait for every seat's notice, with scoped files
untouched and no polling. A timeout, error, or empty reply is not approval:
cancel that seat, confirm it stopped, and restart it once.

If the repo has `CODING_STANDARDS.md`, paste its full text where the brief
says `Standards`; otherwise drop that block and the `### Standards` table.

```
Review only. Do not edit, commit, push, comment on PRs, or start subagents.
Repo: <abs path> Base: <sha> Tier: <tier, if a tier script exists>
Intent: <intent> Out of scope: <scope> Checks: <results>
See: git diff <base> [-- <paths>]; git status --short (read untracked).
Standards (apply every rule to the diff):
<full text of CODING_STANDARDS.md>
Read surrounding code. Find bugs, broken callers, mismatch with intent.
Skip formatting unless it hides a bug. Hold to the smallest change. Flag code,
tests, or guards the intent does not need. Other paths, rare cases, small
perf, extra compat: nits.
blocker = intended case wrong. should = real bug on a real path, in intent. nit = rest.
A real path is a user action or a call the repo's own code makes. A defect only
tests or hand-built inputs reach is a nit unless the intent names that path.
A standards rule sets its own severity when it names one.
Every blocker or should needs evidence: a file:line trace of the failing path,
a repro, or a failing test. Without evidence it counts as a nit.
Reply in Markdown, in this shape. Number findings <P>1, <P>2, ... and keep ids
stable across rounds; write "None." under Findings when there are none.

## Verdict: APPROVE | CHANGES

### Findings
- **<P>1 · blocker|should|nit** `<file>:<line>`: <claim>
  **Evidence:** <trace, repro, or test>
  **Fix:** <suggestion>

### Standards
| Rule | Result |
|---|---|
| <each standards rule by heading> | pass, or <finding id> |
```

`<P>` is the seat's id prefix.

## 3. Merge

- Read each finding against the code yourself and set its severity. Another
  path, rare case, or small cost is a nit, whatever label it came with. A
  blocker or should without evidence is a nit.
- Findings with the same root cause become one `L` id that lists every seat
  id.
- Found by two or more seats: **confirmed**; no cross-check.
- Seats that agree on a finding but not its severity: set it yourself from
  the evidence. Lowering a seat's blocker or should needs your own evidence
  (repro, trace) in the ledger. If you cannot settle it, add the severity
  question to the cross-check call of a seat that did not raise it; with
  none left, you decide.
- Solo blocker or should: goes to cross-check. Solo nit: you decide alone.

## 4. Cross-check

Send each seat, in parallel, the solo blockers and shoulds the *other* seats
raised: one call per seat, all its findings in one list, with the raising
seat's name left out.

```
Check findings only. Do not edit, commit, push, or start subagents.
Repo: <abs path> Base: <sha> Intent: <intent>
See: git diff <base> [-- <paths>]
For each finding, read the code and decide confirm, refute, or unsure.
Back confirm or refute with evidence: a file:line trace, a repro, or test output.

- **L2 · should** `<file>:<line>`: <claim>
  **Evidence given:** <evidence>

Reply in Markdown, one line per finding:
- **L2:** confirm | refute | unsure: <evidence>
```

Settle each finding:

| Checkers | Result |
|---|---|
| at least one confirms with evidence | **confirmed** |
| both refute with evidence | `declined` as a nit |
| anything else | you judge from the evidence; still unclear: `disputed` |

With a two-seat panel, the single checker decides: confirm → confirmed,
refute → declined, unsure → you judge. You may still dispute a confirmed
finding, with evidence.

## 5. Fix

Confirmed means real; severity sets the action. Fix every confirmed blocker
and should in one batch. A nit, confirmed or not, is declined unless it is a
one-line change inside the intent.

- Agree: smallest fix. Prefer delete or narrow over new lock, cache,
  helper, or option. Fix the case that happened. Add one focused test
  that fails without the fix; when the repo's standards require one, it is
  mandatory. Show it failing on the old code.
- Disagree: mark `disputed` and write why, with evidence (file:line, test,
  output).
- Out of scope: decline in one line. List as follow-up.

Update the ledger. Re-run checks and `git diff --shortstat <base>`. If
review grew the diff, cut first. Agree only on the evidence, never to end
the loop.

## 6. Next round

Start one only if budget remains and behavior code changed in step 5 or a
finding is `disputed`. Start every seat in parallel with a fresh call: the
round 1 brief, the ledger (`fixed:` / `disputed:` / `declined:` + evidence),
the same base diff, and the change since last round. Each seat's scope is:

- its own ids that are fixed, open, or disputed;
- its own blockers and shoulds you declined or downgraded, so it can answer;
- the change since last round.

Each seat lists its ids under `### Earlier findings` as `resolved` or
`still open: <reason>`; a seat with no ids writes `None.` there and reviews
only the change. A decline the seat still contests with new evidence becomes
`disputed`. Seats raise new findings only in changed code; those go through
steps 3-5.

## 7. Stop and ship

**Approved:** the last round reviewed the current behavior diff, and after
its merge and cross-check no blocker or should is `open` or `disputed`.
A seat's CHANGES verdict does not block when all of its findings were
declined or refuted. You have no concern of your own.

**Stuck:** a finding is still `disputed` after a round that re-checked it,
or the budget ends with a blocker or should open. Show both sides in 2-3
lines each. The user decides. Budget end is not approval.

**Override:** if, after a stuck report, the user explicitly says to ship
anyway, the user is the last reviewer and the current behavior diff counts
as approved. Never override on your own. Write the Verdict as
`overridden by <user> at <sha>`, with the user's login and no `@`, and mark
each open item `overridden` in the ledger.

Push only after approval, and only if the user asked to push, ship, or
update the PR. If you push to a PR, add the Verdict and Reviewers items and
a folded ledger under the body's `## Review` section, after its Tier item
(layout in the `pr` skill; add the section above the model blurb if the
body has none):

```markdown
- **Verdict:** approved at `<sha>` | overridden by <user> at `<sha>`
- **Reviewers:** gpt-6.2-sol ×<a>, claude-opus-5-5 ×<b>, gemini-4-neon ×<c>

<details>
<summary>Findings: <n> fixed, <n> declined, <n> overridden</summary>

| ID | Severity | Outcome | Finding |
|---|---|---|---|
| L1 (S1, N2) | blocker | fixed | `<file>:<line>` <claim, one line> |
| L2 (O1) | nit | declined | <claim>: <reason> |

</details>
```

Keep the Verdict item in exactly this shape: CI scripts match it. `<sha>` is
the short hash of the commit holding the diff the panel approved or the
user overrode. Drop `, <n> overridden` when there is no override. A later
commit that changes behavior needs a new loop and a new `<sha>`. `×<a>`
counts a seat's panel and cross-check calls; list only seats that ran. Drop
the `<details>` block when no seat raised a finding.

To enforce this in a repo's CI, copy `scripts/check-pr-body.py` from this
skill into the repo's `scripts/`, fill its `TODO(repo)` blanks, and add the
workflow at the bottom of that file. Its `tier` mode prints `Review tier: N`.

Report to the user in this shape:

```markdown
**Review loop: approved** at `<sha>` · <N> rounds · Sol ×<a>, Opus ×<b>, Neon ×<c> · pushed: yes|no

| ID | Severity | Outcome | Finding |
|---|---|---|---|
| L1 (S1, N2) | blocker | fixed | <claim, one line> |
| L2 (O1) | nit | declined | <claim>: <reason> |

**Diff:** <shortstat before> → <shortstat after>

**Usage:** <per seat, or "not exposed">
```

A stuck loop reads **Review loop: stuck** instead, and the disputed items
follow. An overridden loop reads **Review loop: approved (override)**, and
its `overridden` items stay in the table.
