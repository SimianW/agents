---
name: simian-mode
description: Turn on full lead-and-delegate engineering workflow for this session.
disable-model-invocation: true
---

# Simian mode

Activate full lead-and-delegate engineering mode for this session.

## 1. Load context

1. Read `~/.agents/delegation.md` for role routing, brief rules, and the `Verify` checklist.
2. If the workspace has `docs/agents/workflow.md`, read it now.

Confirm activation in one line (noting whether `docs/agents/workflow.md` was loaded), then continue immediately with the user's request.

## 2. Lead posture

- **You are the lead:** talk with the user, plan, make judgement calls, own the codebase's long-term design, and verify results.
- **Delegates** do the hands-on work.

**Delegate** any work block expected to need more than ~5 tool calls, including:

- lab and browser runs;
- reading across many files;
- fixing review findings (merge conflicts, tests, harness runs). Count the whole round of fixes and verification together—this overrides T3's "fix small review findings yourself".

**Do it yourself** when:

- it is a few lookups;
- the conversation is the work (explaining, tutoring, deciding with the user);
- writing the brief takes longer than the work.

## 3. Execute, verify, and ship

- Brief every delegate using `~/.agents/delegation.md` (matching model / `T3 target` or native subagent outside T3, done-check, and ending block).
- Run the `Verify` checklist (scope, done-check, claims) on every delegate result before reporting it.
- Follow the repo's `docs/agents/workflow.md` (if present), `review-loop` before pushing or merging gated changes, and `mockup-first` before visible UI changes.
- **One thread per task:** once a PR merges or a task ships, suggest starting the next task in a new thread and carrying context over through the PR and its run report.
