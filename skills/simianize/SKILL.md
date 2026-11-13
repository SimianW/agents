---
name: simianize
description: "Set up a repo for the PR-and-review workflow: Matt Pocock's skill config, the review-tier gate, test seams, the bug-fix steps, and the Workflow block in AGENTS.md. Re-run it to update a repo."
disable-model-invocation: true
---

# Simianize

Scaffold the per-repo files the workflow assumes, in four layers:

- **Base**: the issue tracker, triage labels and domain docs that Matt Pocock's engineering skills read.
- **Gate**: the review-tier script and the `pr-body` CI check that the `review-loop` and `pr` skills write for.
- **Seams**: the test seams agreed once for this repo, and the bug-fix steps built on them.
- **Block**: the `## Workflow` section in the repo's instructions, which ties the skills together.

The repo's own files win. Each step adds what is missing and updates what an earlier run wrote; content the templates do not cover (versioning, releases, lab rules) stays as it is. In each step, explore first, then ask the user one question at a time with your recommended answer first, then show a draft of every file before you write it.

## 1. Base

Read [setup-matt-pocock-skills](../setup-matt-pocock-skills/SKILL.md) and run its whole process, with one change: when `CLAUDE.md` only imports another file (`@AGENTS.md`), the imported file is the repo's instructions file, and the `## Agent skills` block goes there. Every later step writes to that same file.

On a re-run, when the done-check below already passes, go to step 2.

Done when: `docs/agents/issue-tracker.md` and `docs/agents/domain.md` exist, the instructions file has the `## Agent skills` block, and the tracker has every label in `docs/agents/triage-labels.md`.

## 2. Gate

A repo that already has a tier script (`scripts/review-tier.py`, or `scripts/check-pr-body.py` with a `tier` mode) keeps it: note its tier command for step 4 and go to step 3.

Otherwise:

1. Copy [check-pr-body.py](../review-loop/scripts/check-pr-body.py) to `scripts/check-pr-body.py`.
2. Fill every `TODO(repo)` and rewrite the header docstring for this repo. Match the repo's tree against the tier 2 list in the script's comment, then ask the user to confirm the tier 2 paths and the tier 0 paths.
3. Write `.github/workflows/pr-body.yml` from the example at the bottom of the script. On another CI host, port the same job.
4. Ask the user before you make `pr-body` a required check in branch protection: a repo setting is theirs to change.

Done when: no `TODO(repo)` remains in the script, and `python3 scripts/check-pr-body.py tier` prints `- **Tier:** 2`, because this change adds the gate itself.

## 3. Seams

1. **Standards.** When `CODING_STANDARDS.md` is missing, write it from [coding-standards.md](coding-standards.md).
2. **Seams.** Find where the tests live and the commands that run them (test directories, package scripts, the CI workflow). Propose the seams in order of preference, cheapest first, each with one line on what it catches and what it misses, and ask the user to confirm the list. Write `docs/agents/seams.md` from [seams.md](seams.md). When another doc already lists the seams, move the list and leave a pointer in its place, so `seams.md` is the single source.
3. **Bug fixes.** When `docs/bugfix.md` is missing, write it from [bugfix.md](bugfix.md), and ask the user how a bug is shown to be this repo's own (its Control step). When it exists, keep its steps and only point its seam list at `seams.md`.

Done when: every seam in `docs/agents/seams.md` names a path that exists and a command that runs, and no other file lists the seams.

## 4. Block

Write the `## Workflow` section from [workflow.md](workflow.md) into the instructions file, after `## Agent skills`, with every `<blank>` filled: the base branch, and the tier command from step 2.

When the section exists, update it in place. A template bullet replaces the bullet on the same topic; sentences in it that are specific to this repo stay, and so do bullets the template lacks. Show the user the diff before you write.

Done when: the block has no `<blank>` left, and every path it names exists (`GLOSSARY.md` excepted: the `domain-modeling` skill creates it on first use).

## 5. Ship

Commit the setup on its own branch and ship it by the block you just wrote: this PR is the gate's first run. Report the files written, the files left alone, and what is left for the user to do by hand.
