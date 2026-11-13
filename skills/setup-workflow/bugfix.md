# Fixing a bug

The steps for any bug the user reports or a review or test run finds. Each step ends on its completion criterion; finish it before starting the next.

## 1. Control

Reproduce the bug <where and how: the command, environment or page>. <When this repo runs on top of another system: reproduce it with this repo's code and without it. If it also happens without, it is the other system's bug: stop and report that to the user.> If you cannot reproduce it, the user's capture (a log, a trace, a screenshot) stands in for the run, and the PR says so.

Done when: you have seen the bug yourself, or the user's capture shows this repo's own code going wrong.

## 2. Red

Build the feedback loop with the `diagnosing-bugs` skill (Phase 1), at the first seam in [docs/agents/seams.md](agents/seams.md) that reaches the bug.

Done when: one command goes **red** on this bug, and you have run it and seen it fail.

## 3. Green

Fix it with the `tdd` skill: the smallest change that turns the step 2 command **green**.

Done when: the step 2 command passes, and so does every check in <the CI workflow file>, run locally.

## 4. Review and ship

Follow the Workflow rule in [AGENTS.md](../AGENTS.md). The PR body carries the step 1 result and the step 2 command.

Done when: the PR is open with the `- **Tier:** N` item in its Review section and, for tiers 1 and 2, an APPROVE recorded as `- **Verdict:** approved at <sha>`.
