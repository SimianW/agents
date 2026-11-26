---
name: review-loop
description: Use before pushing or merging a change that meets the repo's review rule or default triggers (sensitive areas, data, infra, public interfaces, >300 LOC), or when the user says "review loop".
---

# review-loop

A **panel** of two models from two families reviews the diff **blind**
and in parallel. You, the lead, merge their findings into one **ledger**,
**cross-check** every solo finding with the other seat, fix what holds up in
one batch, and re-check narrowly. Evidence settles findings, not votes or
confidence.

Make the smallest changes that settle confirmed findings. Watch for scope
creep, and push back with evidence.

## Panel

| Seat | Model, effort | Id prefix | T3 `target` |
|---|---|---|---|
| Sol | `gpt-6.2-sol`, high, fast | `S` | `{"providerInstanceId": "codex", "model": "gpt-6.2-sol", "options": {"reasoningEffort": "high", "serviceTier": "priority"}}` |
| Opus | `claude-opus-5-5`, high | `O` | `{"providerInstanceId": "claudeAgent", "model": "claude-opus-5-5", "options": {"effort": "high"}}` |

This table sets the reviewers for this skill, in place of the Hunt row in
`~/.agents/delegation.md`. Swap a seat only when the user names another model.

**Routing.** In T3, call `orchestrator_capabilities` once. Every panel and
cross-check call is a new `delegate_task` (`role: "review"`,
`mode: "async"`) with a new `clientRequestId`; save each `taskId`.
`childThreadId` is storage, not a target: review runs only through
`delegate_task`, never `t3_thread_send`, `create_threads`, or
`t3_thread_launch`. Outside T3, run the seats your harness reaches natively
(Opus in Claude Code, Sol in Codex) and keep each subagent ID.

**Short seat.** A seat that cannot run (provider missing, credits out, two
failed starts) drops out. With one seat left, ask the user once which model
fills in. Name the seats that ran in the report and PR.

## Ledger

One row per merged finding, kept from round 1 to the report:

- `L` id, and the seat ids it merges (`L1` = `S1`, `O2`);
- severity: `blocker`, `should`, or `nit`;
- found by, and cross-check result (confirmed by / refuted by);
- outcome: `open`, `fixed`, `disputed`, `declined`, `narrowed`, or
  `overridden`;
- chain: the `L` id whose fix wrote the code it is in (`L8 ← L6`), if any;
- evidence: file:line trace, repro, or test output.

Also count each seat's calls (panel plus cross-check) and record usage when
a tool returns it. Never guess either.

## Default triggers

When the repo sets its own review rule, follow it instead. Otherwise run
`review-loop` before pushing or merging any change that meets a trigger below:

| Trigger | The change |
|---|---|
| **Sensitive areas** | touches auth, sessions, secrets, permissions, payments, or user data privacy |
| **Data** | adds or edits a database migration or schema, or deletes data |
| **Infrastructure** | changes deploy, CI, Docker/compose, hooks, cron/launchd/systemd, or sync/install scripts |
| **Interfaces** | changes a public API, CLI, or config format other code or machines depend on |
| **Size** | changes more than ~300 lines of behavior code (excluding generated, vendored, moved/imported files, prose, or throwaway prototypes) |

For anything else, your own verification suffices. If you skip review on a
change close to a trigger, say so in one line of your report.

## Budget

- If the repo has a tier script, run the tier command its `AGENTS.md` or
  `docs/agents/workflow.md` names: `python3 scripts/review-tier.py [base]` or
  `python3 scripts/check-pr-body.py tier [base]`. Tier 0: no review.
  Tier 1: up to 2 rounds. Tier 2: up to 3.
- No tier script: 2 rounds; 3 for security, permissions, auth, data loss,
  or state/concurrency, or when the user asks.
- 3 rounds is the ceiling; only the user lifts it. A lift adds one round
  unless the user names more.
- A round is one panel pass plus its merge and cross-check. Cross-check
  calls are part of their round.
- Round 1 leaving only nits ends the loop, unless a nit fix touches a
  tier 1+ file (step 6). Declined nits and fixes to tier 0 files only need
  no new round.
- A merge round (see After approval) does not count against the budget.

## 1. Scope

Run `git status --short`. Leave unrelated changes out: no stash, no
discard. Limit review to the change paths if they separate cleanly.
Otherwise stop and ask.

Find the base after `git fetch origin`:

- PR: `gh pr view <n> --json baseRefName,headRefOid`. Check out the branch
  only if clean. Confirm `HEAD` is the PR head, or ahead only by this
  change. Base: `git merge-base HEAD origin/<baseRefName>`.
- Local: `git merge-base HEAD origin/<default-branch>`. No remote: a base
  the user names, or the commit the uncommitted change started from.

Commit the change in those paths before round 1, untracked files included,
so nothing reviewed sits outside the hash. The change is `<base>..<head>`,
where `<head>` is that commit's sha. Use one diff command all rounds.
Compute the 12-char diff hash of exactly that commit with the `diff-hash`
mode of the repo's configured PR-body checker (`scripts/check-pr-body.py`,
or an integrated check such as `scripts/review-tier.py`), e.g.
`python3 scripts/check-pr-body.py diff-hash <base> <head>`, or, when the
repo has no checker or its checker has no `diff-hash` mode, with this
one-liner (which hashes `<merge-base>^{tree}..<head>^{tree}` so local
diff-rendering git config cannot change it, matching the current template
checker):

```
python3 -c 'import hashlib,subprocess,sys; g=lambda *a:subprocess.check_output(["git",*a],text=True).strip(); b,h=g("merge-base",sys.argv[2],sys.argv[1]),sys.argv[2]; t=lambda r:g("rev-parse","--verify",r+"^{tree}"); print(hashlib.sha256((t(b)+".."+t(h)+"\n").encode()).hexdigest()[:12])' <base> <head>
```

State intent and out-of-scope in 1-2 sentences. Copy the PR body's (or
draft evidence's) `Existing tests modified/removed` entry into the brief's
`Test changes:` line, or write `None`.
Run covering checks; send only code that passes them. If a check needs
set-up (dependencies, browsers), do it before round 1 and say so in
`Checks:`, so every seat can rerun it. Note missing or pre-failing checks in
the brief.

## 2. Round 1: blind panel

Start every seat in one message, in parallel, with the same brief. Each seat
sees only its own brief, never another seat's findings: blindness is what
makes overlap meaningful. Wait for every seat's notice, with scoped files
untouched and no polling. A timeout, error, or empty reply is not approval:
cancel that seat, confirm it stopped, and restart it once.

Report to the user once per round, after its merge and cross-check settle.
A seat that finishes while others are still out goes into the ledger, and
the turn ends with no message.

If the repo has `CODING_STANDARDS.md`, paste its full text where the brief
says `Standards`; otherwise drop that block and the `### Standards` table.

```
Review only. Do not edit, commit, push, comment on PRs, or start subagents.
Repo: <abs path> Base: <sha> Head: <sha> Tier: <tier, if a tier script exists>
Intent: <intent> Out of scope: <scope> Checks: <results>
Test changes: <Existing tests modified/removed entry from PR body or draft evidence, or "None">
See: git diff <base> <head> [-- <paths>]
Compute the 12-char diff hash of exactly <base>..<head> and put it in your Verdict header:
<the repo's PR-body checker diff-hash command, e.g. python3 scripts/check-pr-body.py diff-hash <base> <head>>
or, with no checker or no diff-hash mode:
python3 -c 'import hashlib,subprocess,sys; g=lambda *a:subprocess.check_output(["git",*a],text=True).strip(); b,h=g("merge-base",sys.argv[2],sys.argv[1]),sys.argv[2]; t=lambda r:g("rev-parse","--verify",r+"^{tree}"); print(hashlib.sha256((t(b)+".."+t(h)+"\n").encode()).hexdigest()[:12])' <base> <head>
Standards (apply every rule to the diff):
<full text of CODING_STANDARDS.md>
Read surrounding code. Find bugs, broken callers, mismatch with intent.
Skip formatting unless it hides a bug. Hold to the smallest change. Flag code,
tests, or guards the intent does not need. Flag unexplained removal or weakening
of existing test assertions as `should`; `Test changes:` gives the author's
reasons. Other paths, rare cases, small perf, extra compat: nits.
blocker = intended case wrong. should = real bug on a real path, in intent. nit = rest.
A real path is a user action or a call the repo's own code makes. A defect only
tests or hand-built inputs reach is a nit unless the intent names that path.
A standards rule sets its own severity when it names one.
Every blocker or should needs evidence: a file:line trace of the failing path,
a repro, or a failing test. Without evidence it counts as a nit.
Reply in Markdown, in this shape. Number findings <P>1, <P>2, ... and keep ids
stable across rounds; write "None." under Findings when there are none.

## Verdict: APPROVE | CHANGES (diff `<12-hex>`)

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
- Found by both seats: **confirmed**; no cross-check.
- Seats that agree on a finding but not its severity: set it yourself from
  the evidence. Lowering a seat's blocker or should needs your own evidence
  (repro, trace) in the ledger.
- Solo blocker or should: goes to cross-check. Solo nit: you decide alone.

## 4. Cross-check

Send each seat, in parallel, the solo blockers and shoulds the *other* seat
raised: one call per seat, all its findings in one list, with the raising
seat's name left out.

```
Check findings only. Do not edit, commit, push, or start subagents.
Repo: <abs path> Base: <sha> Head: <sha> Intent: <intent>
See: git diff <base> <head> [-- <paths>]
For each finding, read the code and decide confirm, refute, or unsure.
Back confirm or refute with evidence: a file:line trace, a repro, or test output.

- **L2 · should** `<file>:<line>`: <claim>
  **Evidence given:** <evidence>

Reply in Markdown, one line per finding:
- **L2:** confirm | refute | unsure: <evidence>
```

The other seat is the only checker. Settle each finding:

| Checker | Result |
|---|---|
| confirms with evidence | **confirmed** |
| refutes with evidence | `declined` as a nit |
| anything else | you judge from the evidence; still unclear: `disputed` |

You may still dispute a confirmed finding, with evidence.

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
- Chain: at the second link on one branch (`L8 ← L6 ← L1`), narrow
  instead of patching again. Put that branch back to its base behavior, or
  switch it off where it starts, with a test that shows the base behavior;
  mark its findings `narrowed` and file them as one follow-up issue. If the
  user's request named that branch, ask before cutting it.

Update the ledger. Commit the fixes; that commit is the new `<head>`.
Re-run checks and `git diff --shortstat <base> HEAD`. If
review grew the diff, cut first. Agree only on the evidence, never to end
the loop.

## 6. Next round

Start one only if budget remains and a finding is `disputed` or step 5
changed any file at tier 1 or above: behavior code, or an agent steering file
(`AGENTS.md` or `CLAUDE.md` in any folder, `CODING_STANDARDS.md`,
`docs/bugfix.md`, `docs/agents/*`). Start every seat in parallel with a fresh
call: the round 1 brief with the new `<head>`, the ledger (`fixed:` /
`disputed:` / `declined:` + evidence), the same base, and the change since
last round. Each seat's scope is:

- its own ids that are fixed, open, or disputed;
- its own blockers and shoulds you declined or downgraded, so it can answer;
- the change since last round.

Each seat lists its ids under `### Earlier findings` as `resolved` or
`still open: <reason>`; a seat with no ids writes `None.` there and reviews
only the change. A decline the seat still contests with new evidence becomes
`disputed`. Seats raise new findings only in changed code; those go through
steps 3-5.

## 7. Stop and ship

**Approved:** the last round reviewed the committed `<sha>` you will record
in the PR, every approving seat's Verdict header hash equals
`diff-hash <base> <sha>` for that commit, and after its merge and
cross-check no blocker or should is `open` or `disputed`. A hash mismatch
means a seat reviewed other content: re-run that seat on `<sha>`.
A seat's CHANGES verdict does not block when all of its findings were
declined or refuted. You have no concern of your own. If only Tier-0
follow-up edits (a README nit, say) were committed after `<sha>`, the loop
is still Approved: keep `Verdict:` on the last reviewed `<sha>` and its
verified diff hash.

**Stuck:** a finding is still `disputed` after a round that re-checked it,
the budget ends with a blocker or should open, or the budget ends with a
fix to a tier ≥ 1 file committed that no round has reviewed yet. Show both
sides in 2-3 lines each (for an unreviewed fix: the findings it addresses
and its diff). Budget end is not approval. The user decides among:

- **Narrow:** cut the contested branch back to base behavior and file a
  follow-up issue; the cut gets one review round. Recommend it when the
  open findings form a chain or sit on a branch no live run reached, and
  say how often live runs reached it.
- **Another round:** fix and re-review.
- **Override:** ship as is (below).

**Override:** if, after a stuck report, the user explicitly says to ship
anyway, the user is the last reviewer and the current behavior diff counts
as approved. Never override on your own. Write the Verdict as
``overridden by <user> at `<sha>` (diff `<12-hex>`)``, with the user's
login and no `@`, and mark each open item `overridden` in the ledger.

Pushing to a **draft PR** branch before review is allowed so CI runs early,
when the user asked to open or ship a PR. **Marking a PR ready for review**
or pushing behavior changes to an already-ready PR requires approval first.
Never move `Verdict:` to a commit the panel did not review—agent steering
files (`AGENTS.md` or `CLAUDE.md` in any folder, `CODING_STANDARDS.md`,
`docs/bugfix.md`, `docs/agents/*`) are tier 1 and require re-review after
fixes. If you update a PR body after approval, add the Verdict and Reviewers items and a folded
ledger under the body's `## Review` section, after its Tier item (layout in
the `pr` skill; add the section above the model blurb if the body has none):

```markdown
- **Verdict:** approved at `<sha>` (diff `<12-hex>`) | overridden by <user> at `<sha>` (diff `<12-hex>`)
- **Reviewers:** gpt-6.2-sol ×<a>, claude-opus-5-5 ×<b>

<details>
<summary>Findings: <n> fixed, <n> declined, <n> narrowed, <n> overridden</summary>

| ID | Severity | Outcome | Finding |
|---|---|---|---|
| L1 (S1, O2) | blocker | fixed | `<file>:<line>` <claim, one line> |
| L2 (O1) | nit | declined | <claim>: <reason> |

</details>
```

Keep the Verdict item in exactly this shape: CI scripts match it and verify
`<12-hex>` against the hash of `<merge-base>^{tree}..<sha>^{tree}`. `<sha>` is
the short hash of the commit the panel approved or the user overrode;
`<12-hex>` is the hash you verified against the approving seats' headers
under Approved, never one recomputed over a commit no seat reviewed. Write
the ``(diff `<12-hex>`)`` suffix when the repo's configured PR-body checker
(`scripts/check-pr-body.py`, or an integrated check such as
`scripts/review-tier.py`) has a `diff-hash` mode, or the repo has no
checker. A repo whose checker predates `diff-hash` keeps the plain `` approved at `<sha>` `` shape (and
`` overridden by <user> at `<sha>` ``), since its CI rejects the suffix, until
`/simianize` upgrades the checker. Drop
`, <n> narrowed` or `, <n> overridden` when there is none. A later commit
that changes any tier ≥ 1 file needs a new loop, a new `<sha>`, and a new
diff hash; a merge of the base branch follows After approval instead. `×<a>`
counts a seat's panel and cross-check calls; list only seats that ran. Drop
the `<details>` block when no seat raised a finding.

To enforce this in a repo's CI, copy `scripts/check-pr-body.py` from this
skill into the repo's `scripts/`, fill its `TODO(repo)` blanks, and add the
workflow at the bottom of that file. Its `tier` mode prints `Review tier: N`.

Report to the user in this shape:

```markdown
**Review loop: approved** at `<sha>` · <N> rounds · Sol ×<a>, Opus ×<b> · pushed: yes|no

| ID | Severity | Outcome | Finding |
|---|---|---|---|
| L1 (S1, O2) | blocker | fixed | <claim, one line> |
| L2 (O1) | nit | declined | <claim>: <reason> |

**Diff:** <shortstat before> → <shortstat after>

**Usage:** <per seat, or "not exposed">
```

A stuck loop reads **Review loop: stuck** instead, and the disputed items
follow. An overridden loop reads **Review loop: approved (override)**, and
its `overridden` items stay in the table.

## After approval

When the base branch moves after approval:

- Update the branch only when GitHub reports a merge conflict, and only by
  merging `origin/<base>` into it. Never rebase, amend, or force-push an
  approved branch.
- Leave the Verdict item as it is. Never point it at a commit that no seat
  and not the user saw, and never move a user's override.
- Run the PR-body check. Pass: push. Fail on the merge: run one **merge
  round**. Every seat reviews only the conflict resolution
  (`git show --remerge-diff <merge>`), and the round does not count against
  the budget. APPROVE: set the Verdict to the merge commit and its diff hash
  (the configured checker's `diff-hash origin/<base> <merge>`, e.g.
  `python3 scripts/check-pr-body.py diff-hash origin/<base> <merge>`). A confirmed
  blocker or should: fix it in a normal round, which counts; with no budget
  left, the loop is Stuck.
- An overridden PR whose check fails after the merge goes back to the user
  as Stuck; it gets no merge round.
