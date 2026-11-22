---
name: simianize
description: "Set up a repo for the PR-and-review workflow: Matt Pocock's skill config, the review-tier gate, PR size labels, the file-length ratchet, test seams, the bug-fix steps, and the Workflow block in AGENTS.md. Re-run it to update a repo."
disable-model-invocation: true
---

# Simianize

Scaffold the per-repo files the workflow assumes, in six layers:

- **Base**: the issue tracker, triage labels and domain docs that Matt Pocock's engineering skills read.
- **Gate**: the review-tier script and the `pr-body` CI check that the `review-loop` and `pr` skills write for.
- **Size**: the CI jobs that label every PR by the lines of code it changes and hold every code file to a length limit.
- **Seams**: the test seams agreed once for this repo, and the bug-fix steps built on them.
- **Block**: the `## Workflow` section in the repo's instructions, which ties the skills together.
- **Changelog**: the rules for writing release notes, for a repo that ships versioned releases.

The repo's own files win. Each step adds what is missing and updates what an earlier run wrote; content the templates do not cover (versioning, releases, lab rules) stays as it is. In each step, explore first, then ask that step's questions together in one dialog, each led by your recommended answer, then show a draft of every file before you write it. Keep this machine's name and paths out of the files you write: a local URL reads `http://<host>:<port>`.

## 1. Base

First settle the **instructions file**. `AGENTS.md` holds the repo's instructions and `CLAUDE.md` is the one line `@AGENTS.md`, so Claude Code and Codex read the same text:

- Neither file exists: create both.
- Only `AGENTS.md` exists: create `CLAUDE.md`.
- `CLAUDE.md` holds instructions of its own: ask the user whether to move them into `AGENTS.md` (recommended). If they decline, `CLAUDE.md` is the instructions file for this run.

Then read [setup-matt-pocock-skills](../setup-matt-pocock-skills/SKILL.md) and run its whole process, with two changes. Its `## Agent skills` block goes in the instructions file you just settled, in place of its own rule for picking or asking for a file. And its sections are asked together in one dialog, as in every step here. Every later step writes to that same file.

On a re-run, when the done-check below already passes, go to step 2.

Done when: `CLAUDE.md` and the instructions file exist, `docs/agents/issue-tracker.md` and `docs/agents/domain.md` exist, the instructions file has the `## Agent skills` block, and the tracker has every label in `docs/agents/triage-labels.md`.

## 2. Gate

A repo that already has a tier script (`scripts/review-tier.py`, or `scripts/check-pr-body.py` with a `tier` mode) keeps it: note its tier command for step 5 and go to step 3.

Otherwise:

1. Copy [check-pr-body.py](../review-loop/scripts/check-pr-body.py) to `scripts/check-pr-body.py`.
2. Fill every `TODO(repo)` and rewrite the header docstring for this repo. Match the repo's tree against the tier 2 list in the script's comment, then ask the user to confirm the tier 2 paths and the tier 0 paths.

   Classify by **path**. A file that holds both risky and ordinary code is tier 2 as a whole. `classify_special` stays as the template has it, returning `None`, with its `TODO(repo)` taken out of the docstring; write a rule that reads a file's content only when the user asks for one, because such a rule is a heuristic that goes stale as the file changes.
3. Write `.github/workflows/pr-body.yml` from the example at the bottom of the script. On another CI host, port the same job.
4. Ask the user before you make `pr-body` a required check in branch protection: a repo setting is theirs to change.

Done when: no `TODO(repo)` remains in the script, and `python3 scripts/check-pr-body.py tier` prints `Review tier: 2`, because this change adds the gate itself.

## 3. Size

CI labels every PR by the lines of code it changes, on the Kubernetes scale (`size/XS` to `size/XXL`), and holds every code file to a length limit. Only code counts: prose, lock files and binary files are left out. `pr-size.py` holds that definition of code, and `file-length.py` reads it from there.

1. Copy [pr-size.py](pr-size.py) to `scripts/pr-size.py` and fill every `TODO(repo)`. Propose the paths in this repo that are not code (docs, notes, generated or vendored output, results), and ask the user to confirm them.
2. Copy [pr-size.yml](pr-size.yml) to `.github/workflows/pr-size.yml`. On another CI host, port the same job.
3. Create each label that `python3 scripts/pr-size.py --labels` prints and the tracker lacks.
4. **File length.** A repo that already enforces file length (ESLint `max-lines`, say) keeps its own check: skip substeps 4 and 5. Otherwise copy [file-length.py](file-length.py) to `scripts/file-length.py`. Run `python3 scripts/file-length.py --caps`, show the user the files it caps at their current length, and ask them to confirm `MAX_LINES` (500 recommended). Paste the output for the confirmed limit over `CAPS`, and take out its `TODO(repo)`. Caps only ratchet down: the check fails when a capped file shrinks and its cap stays.
5. Copy [file-length.yml](file-length.yml) to `.github/workflows/file-length.yml`, with its `TODO(repo)` filled by the default branch. On another CI host, port the same job.

On a re-run, keep the repo's settings at the top of each script (`MAX_LINES` and `CAPS` among them) and bring over the rest of the templates.

Done when: no `TODO(repo)` remains in the scripts or workflows, `python3 scripts/pr-size.py` prints a `size/` label followed by a file list that holds only code, the tracker has all six labels, and `python3 scripts/file-length.py` prints `file-length: ok…` and exits 0 (or the repo's own length check passes).

## 4. Seams

1. **Standards.** When `CODING_STANDARDS.md` is missing, write it from [coding-standards.md](coding-standards.md).
2. **Seams.** Find where the tests live and the commands that run them (test directories, package scripts, the CI workflow). Propose the seams in order of preference, cheapest first, each with one line on what it catches and what it misses, and ask the user to confirm the list. Write `docs/agents/seams.md` from [seams.md](seams.md). When no CI workflow runs the repo's tests, ask the user whether to add one that runs the test command (recommended), so the seams file has a workflow to name. When another doc already lists the seams, move the list and leave a pointer in its place, so `seams.md` is the single source.
3. **Bug fixes.** When `docs/bugfix.md` is missing, write it from [bugfix.md](bugfix.md), and ask the user how a bug is shown to be this repo's own (its Control step). When it exists, keep its steps and only point its seam list at `seams.md`.

Done when: every seam in `docs/agents/seams.md` names a path that exists and a command that runs, and no other file lists the seams.

## 5. Block

Write the `## Workflow` section from [workflow.md](workflow.md) into the instructions file, after `## Agent skills`, with every `<blank>` filled: the base branch, and the tier command from step 2.

The Frontend bullet is for a repo with a user-visible frontend. Ask the user, recommending yes when the repo has UI files (HTML, CSS, components); on yes, fill its blanks from the repo, and on no, leave the bullet out.

When the section exists, update it in place. A template bullet replaces the bullet on the same topic; sentences in it that are specific to this repo stay, and so do bullets the template lacks. Show the user the diff before you write.

Done when: the block has no `<blank>` left, and every path it names exists (`GLOSSARY.md` and `mockups/` excepted: the `domain-modeling` and `mockup-first` skills create them on first use).

## 6. Changelog

Ask the user whether this repo ships versioned releases whose changes users read. Recommend yes when the repo has a `CHANGELOG.md`, a version field or release tags, and no otherwise. On no, go to step 7.

On yes, ask when an entry is written, with these two options:

- **Unreleased per PR** (recommended): every PR with a change the user can notice adds its bullet under a standing `## [Unreleased]` heading, and the release PR renames that heading to the version. This is Keep a Changelog's own rule and what the template says; no change is forgotten at release time.
- **With the version bump**: the entry is written in the PR that changes the version. Replace the template's Unreleased paragraph with "Add the entry in the PR that changes the version.", and take `## [Unreleased]` out of its heading sentence and its example.

Then write the `## Changelog` section from [changelog.md](changelog.md) into the instructions file, with the `<blank>` filled by the repo's version format. When the section exists, update it by step 5's rule.

Bring the repo in line with the choice:

- `CHANGELOG.md`: create it with a `# Changelog` title when it is missing. On Unreleased per PR, its first `##` heading is `## [Unreleased]`: add the heading when it is not there.
- On Unreleased per PR, find what else reads the top of `CHANGELOG.md` (a version check, a release script, the release steps in the instructions file) and update each in this same change, with its tests.

Done when: the section has no `<blank>` left, `CHANGELOG.md` matches the choice, and every check the repo runs in CI passes locally.

## 7. Ship

Commit the setup on its own branch and ship it by the block you just wrote: this PR is the first run of the gate and of the size label. Report the files written, the files left alone, and what is left for the user to do by hand. Tell the user that `/ask-simian` says which of these files to edit for a later change.
