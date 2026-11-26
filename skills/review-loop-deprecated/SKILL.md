---
name: review-loop-deprecated
description: Deprecated single-reviewer review loop (Sol rounds, then a final Opus pass). Superseded by review-loop; run only when the user asks for it by name.
disable-model-invocation: true
---

# review-loop-deprecated

Deprecated: `review-loop` replaces this with a three-model panel. Kept for
reference and for runs the user asks for by name.

This is a workflow for making your code changes more correct before (or
sometimes after) filing a pull request: a reviewer model checks the diff in a
loop. The reviewer runs the model in the **Hunt** row of
`~/.agents/delegation.md`. A final pass by Opus 5.5 follows the reviewer's approval.

Make the most minimal possible changes to appease the reviewers. Be careful
of scope creep and don't be scared to push back.

## Budget

- If the repo has `scripts/review-tier.py` or `scripts/check-pr-body.py`, run
  it against the base (`check-pr-body.py tier <base>`); its tier sets the
  budget: tier 0 needs no review, tier 1 gets the default, tier 2 may extend
  to 5. Otherwise use the rules below.
- Default: 3 rounds total. Round 1 is full. Later rounds check only
  changed code and open findings.
- Extend to 5 only for security, permissions, auth, data loss, or
  state/concurrency, while a blocker or should stays open with evidence. Or when
  the user asks.
- Stop early if a round returns only nits. Declined nits and comment,
  doc, or format-only fixes need no new round.
- Stop at the first APPROVE on the current behavior diff. 5 rounds is the
  hard ceiling.
- After the reviewer approves, a final Opus pass (step 5) has its own budget: 2 rounds
  (tier 1, or the default), 3 (tier 2, or an extended loop). Tier 0 gets none.
- One reviewer at a time. Reviewers must not start subagents or reviewers.
- Keep a ledger: id, severity, outcome, usage if returned. Never guess it.

## 1. Scope

Run `git status --short`. Do not stash, discard, or include unrelated
changes. Limit review to the change paths if they separate cleanly.
Otherwise stop and ask.

Find the base after `git fetch origin`:

- PR: `gh pr view <n> --json baseRefName,headRefOid`. Check out the branch
  only if clean. Confirm `HEAD` is the PR head, or ahead only by this
  change. Base: `git merge-base HEAD origin/<baseRefName>`.
- Local: `git merge-base HEAD origin/<default-branch>`. No remote: a base
  the user names, or `HEAD` for uncommitted changes only.

The change is base to working tree in those paths, with untracked files.
Use one diff command all rounds. State intent and out-of-scope in 1-2
sentences. Run covering checks. Do not send code this change breaks. Note
missing or pre-failing checks in the brief.

## 2. Start the reviewer

In T3, call `orchestrator_capabilities`. Use the Hunt model and options from
`~/.agents/delegation.md` unless the user named another. Record provider, model, and
effort only if exposed. Use `delegate_task` every round (`role: "review"`,
`mode: "async"`). Save `taskId`. New `clientRequestId` per round.
`childThreadId` is storage, not the next target. Do not use
`t3_thread_send`, `create_threads`, or `t3_thread_launch` for review.

If T3 tools are not listed, try one direct capability call. Outside T3, use
a native subagent on the Hunt model and keep its ID. In Claude Code, use a
custom subagent only if it is set up to run the Hunt model. If no route runs it
(for example, Codex credits ran out), ask the user once which model to use instead, run the whole
loop on that one model, and name it in the PR line.

Do not edit scoped files while review runs. Wait for the notice. Do not
poll or start a second reviewer. Timeout, error, or no reply is not
approval. On failure, cancel, verify stop, restart with the ledger.

Round 1 brief (T3 children get no history). If the repo has
`CODING_STANDARDS.md`, paste its full text where the brief says `Standards`;
otherwise drop that block and the `### Standards` table.

```
Review only. Do not edit, commit, push, comment on PRs, or start subagents.
Repo: <abs path> Base: <sha> Tier: <tier, if review-tier.py exists>
Intent: <intent> Out of scope: <scope> Checks: <results>
See: git diff <base> [-- <paths>]; git status --short (read untracked).
Standards (apply every rule to the diff):
<full text of CODING_STANDARDS.md>
Read surrounding code. Find bugs, broken callers, mismatch with intent.
Skip formatting unless it hides a bug. Hold to the smallest change. Flag code,
tests, or guards the intent does not need. Other paths, rare cases, small
perf, extra compat: nits.
blocker = intended case wrong. should = real bug callers will hit, in intent. nit = rest.
A standards rule sets its own severity when it names one.
Reply in Markdown, in this shape. Number findings R1, R2, ... and keep ids
stable across rounds; write "None." under Findings when there are none.

## Verdict: APPROVE | CHANGES

### Findings
- **R1 · blocker|should|nit** `<file>:<line>`: <claim>
  **Fix:** <suggestion>

### Standards
| Rule | Result |
|---|---|
| <each standards rule by heading> | pass, or <finding id> |
```

## 3. Answer findings

Check each finding and severity yourself. Another path, rare case, or
small cost is a nit, whatever label it came with.

- Agree: smallest fix. Prefer delete or narrow over new lock, cache,
  helper, or option. Fix the case that happened. Add one focused test
  that fails without the fix; when the repo's standards require one, it is
  mandatory. Show it failing on the old code.
- Disagree: say why, with evidence (file:line, test, output).
- Out of scope or nit: decline in one line. List as follow-up.

Update the ledger. Re-run checks and `git diff --shortstat <base>`. If
review grew the diff, cut first. Do not agree just to end the loop.

## 4. Next round

Start one only if budget remains and a blocker or should is open, behavior code
changed, or approval does not cover the current behavior diff. Use a fresh
`delegate_task` in T3, or follow up the saved native ID. Send the round 1 brief,
the ledger (`fixed:` / `disagree:` / `declined:` + evidence), the same base
diff, and the change since last round. Tell the reviewer: open ids and changed
code only, and list each old id under `### Earlier findings` as `resolved` or
`still open: <reason>`.

## 5. Final Opus pass

Once the reviewer approves, run one more full review with Opus 5.5 on extra-high effort
(T3 target: `{"providerInstanceId": "claudeAgent", "model": "claude-opus-5-5",
"options": {"effort": "xhigh"}}`). Send the round 1 brief with the full base
diff, plus the ledger so Opus skips settled ids, and tell Opus to number its
findings F1, F2, ... Answer its findings as in
step 3. If you fix a blocker or should, the next Opus round checks open ids and
changed code only; it does not go back to the reviewer. Opus's APPROVE on the current
behavior diff closes the loop. Skip this pass when the whole loop already ran on
Opus 5.5.

## 6. Stop and ship

Agreed: APPROVE from the last reviewer on the current behavior diff, no
blocker or should open, no concern of your own. Stuck: an item stays disputed
after two replies, or budget ends. Show both sides in 2-3 lines each. The user
decides. Budget end is not approval.

Override: if, after a stuck report, the user explicitly says to ship anyway,
the user is the last reviewer and the current behavior diff counts as
approved. Never override on your own. Write the Verdict as
`overridden by <user> at <sha>`, with the user's login and no `@`, and mark
each open item `overridden` in the ledger.

Do not push during the loop. Push after agreement only if the user asked
to push, ship, or update the PR. If you push to a PR, add the Verdict and
Reviewers items and a folded ledger under the body's `## Review` section, after
its Tier item (layout in the `pr` skill; add the section above the model blurb
if the body has none):

```markdown
- **Verdict:** approved at `<sha>` | overridden by <user> at `<sha>`
- **Reviewers:** <model> ×<N> → <final model> ×<M>

<details>
<summary>Findings: <n> fixed, <n> declined, <n> overridden</summary>

| ID | Severity | Outcome | Finding |
|---|---|---|---|
| R1 | blocker | fixed | `<file>:<line>` <claim, one line> |
| F1 | nit | declined | <claim>: <reason> |

</details>
```

Keep the Verdict item in exactly this shape: CI scripts match it. `<sha>` is
the short hash of the commit holding the diff the last reviewer approved or
the user overrode. Drop `, <n> overridden` when there is no override. A
later commit that changes behavior needs a new loop and a new `<sha>`. Drop
`→ <final model> ×<M>` when the whole loop ran on one model, and the
`<details>` block when no reviewer raised a finding.

To enforce this in a repo's CI, copy `scripts/check-pr-body.py` from the
`review-loop` skill into the repo's `scripts/`, fill its `TODO(repo)` blanks, and add the
workflow at the bottom of that file. Its `tier` mode prints `Review tier: N`.

Report to the user in this shape:

```markdown
**Review loop: approved** at `<sha>` · <N> rounds <model>, <M> <final model> · pushed: yes|no

| ID | Severity | Outcome | Finding |
|---|---|---|---|
| R1 | blocker | fixed | <claim, one line> |
| F1 | nit | declined | <claim>: <reason> |

**Diff:** <shortstat before> → <shortstat after>

**Usage:** <per model, or "not exposed">
```

A stuck loop reads **Review loop: stuck** instead, and the disputed items
follow. An overridden loop reads **Review loop: approved (override)**, and
its `overridden` items stay in the table.
