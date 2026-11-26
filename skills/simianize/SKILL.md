---
name: simianize
description: "Set up or update a repo's PR, review-tier, size, file-length, seam, bugfix, and workflow files."
disable-model-invocation: true
---

# Simianize

Scaffold or update the per-repo workflow files in six layers:

- **Base**: issue tracker, triage labels, and domain docs for Matt Pocock's engineering skills.
- **Gate**: review-tier script and `pr-body` CI check for `review-loop` and `pr`.
- **Size**: PR code-size labels (`size/XS`–`size/XXL`) and the file-length ratchet.
- **Seams**: `CODING_STANDARDS.md`, agreed test seams (`docs/agents/seams.md`), and `docs/bugfix.md`.
- **Workflow**: disclosed `docs/agents/workflow.md` plus a concise `## Workflow` pointer block in `AGENTS.md`.
- **Changelog**: release-note rules, for repos with versioned releases.

**Working rules:** The repo's own content wins—add what is missing and update earlier template output while keeping repo-specific rules (versioning, releases, lab rules). Explore each step first, ask that step's questions together in one dialog (recommended answer first), and show file drafts before writing. Keep machine-specific names and paths out of repo files (write `http://<host>:<port>`).

## 1. Base

Settle the **instructions file**: `AGENTS.md` holds repo instructions and `CLAUDE.md` is `@AGENTS.md`:

- Neither exists: create both.
- Only `AGENTS.md` exists: create `CLAUDE.md`.
- `CLAUDE.md` holds its own instructions: ask whether to move them into `AGENTS.md` (recommended). If declined, `CLAUDE.md` is the instructions file for this run.

Record the instructions file's starting line count for Step 7 (`0` if newly created).

Read [setup-matt-pocock-skills](../setup-matt-pocock-skills/SKILL.md) and run its process with two changes: place its `## Agent skills` block in the settled instructions file, and batch its questions into one dialog. On a re-run where the done-check already passes, proceed to Step 2.

Done when: `CLAUDE.md` and the instructions file exist, `docs/agents/issue-tracker.md` and `docs/agents/domain.md` exist, the instructions file has `## Agent skills`, and the tracker has every label named in `docs/agents/triage-labels.md` and `docs/agents/issue-tracker.md` (including `wayfinder:map`, `wayfinder:research`, `wayfinder:prototype`, `wayfinder:grilling`, `wayfinder:task` when listed).

## 2. Gate

- **Existing custom tier script (`scripts/review-tier.py`, etc.):** read [AUDIT-EXISTING.md](AUDIT-EXISTING.md) and follow "Existing review-tier script", then continue to Step 3.
- **Re-run on a template `scripts/check-pr-body.py`:** keep its top `# Repo settings` block (including `HIGH_RISK_*`, `CHECKS_ONLY_*`, and `classify_special`, adding `AGENT_STEERING_*` if missing), replace everything below `# The rest is generic` from [check-pr-body.py](../review-loop/scripts/check-pr-body.py), and audit gate-file self-coverage per [AUDIT-EXISTING.md](AUDIT-EXISTING.md). (Or delete `scripts/check-pr-body.py` first to set it up fresh below.)

Otherwise:

1. Copy [check-pr-body.py](../review-loop/scripts/check-pr-body.py) to `scripts/check-pr-body.py`.
2. Fill every `TODO(repo)` and rewrite the header docstring for this repo. Match the tree against the tier 2 list in the script comment, and confirm tier 2 and tier 0 paths with the user. Classify by **path** (mixed risky/ordinary files are tier 2 as a whole). Leave `classify_special` returning `None` (removing its `TODO(repo)` comment) unless the user asks for a content heuristic.
3. Write `.github/workflows/pr-body.yml` from the example at the bottom of the script (or port to the repo's CI host).
4. Ask before making `pr-body` a required branch-protection check.

Done when: no `TODO(repo)` remains in `scripts/check-pr-body.py`, and `python3 scripts/check-pr-body.py tier` prints `Review tier: 2`.

## 3. Size

1. Copy [pr-size.py](pr-size.py) to `scripts/pr-size.py`, fill every `TODO(repo)`, and confirm non-code paths (docs, notes, generated/vendored output, results) with the user.
2. Copy [pr-size.yml](pr-size.yml) to `.github/workflows/pr-size.yml` (or port to the repo's CI host).
3. Create any missing label printed by `python3 scripts/pr-size.py --labels`.
4. **File length:** if the repo already enforces file length (e.g. ESLint `max-lines`), read [AUDIT-EXISTING.md](AUDIT-EXISTING.md) and follow "Existing file-length check" (skipping both `file-length.py` and `file-length.yml`). Otherwise:
   - Copy [file-length.py](file-length.py) to `scripts/file-length.py`, run `python3 scripts/file-length.py --caps`, confirm `MAX_LINES` (500 recommended) and starting `CAPS` with the user, paste them into the script, and remove its `TODO(repo)`.
   - Copy [file-length.yml](file-length.yml) to `.github/workflows/file-length.yml` with the default branch filled in (or port to the repo's CI host).

On a re-run, keep the repo's top-of-script settings (`MAX_LINES`, `CAPS`, excluded paths) and update the rest from the templates.

Done when: no `TODO(repo)` remains, `python3 scripts/pr-size.py` outputs a `size/` label with only code files, all six size labels exist on the tracker, and `python3 scripts/file-length.py` exits 0 (or the repo's own length check passes).

## 4. Seams

1. **Standards:** if `CODING_STANDARDS.md` is missing, write it from [coding-standards.md](coding-standards.md).
2. **Seams:** inspect tests, scripts, and CI; propose seams cheapest-first (each with what it catches and misses), confirm with the user, and write `docs/agents/seams.md` from [seams.md](seams.md). If no CI workflow runs tests, offer to add one (recommended). Move any duplicate seam list from other docs into `seams.md` and leave a pointer.
3. **Bug fixes:** if `docs/bugfix.md` is missing, write it from [bugfix.md](bugfix.md) and ask how a bug is isolated to this repo (its Control step). If it exists, keep its steps and point its seams at `docs/agents/seams.md`.

Done when: every seam in `docs/agents/seams.md` names an existing path and working command, and no other doc duplicates the seam list.

## 5. Workflow

1. Write `docs/agents/workflow.md` from [workflow.md](workflow.md) with every `<blank>` filled (base branch, tier command, body check command, length limit, caps location, length command). If it already exists, update template sections in place while keeping repo-specific additions.
2. Write the compact `## Workflow` pointer block from [workflow-block.md](workflow-block.md) into the instructions file after `## Agent skills` with every `<blank>` filled.
   - Omit the Dev docs bullet if no developer doc exists.
   - Ask whether the repo has a user-visible frontend (recommend yes when UI files exist); fill language and tokens path on yes, omit the Frontend bullet on no.
   - On a re-run where the instructions file has an older inline `## Workflow` section, migrate its procedure into `docs/agents/workflow.md`, replace the section with the pointer block, and keep repo-specific bullets/sentences. Show the diff before writing.
3. Audit other sections in the instructions file: offer to disclose any task-specific section over ~15 lines (versioning, lab, API contract) into `docs/agents/<topic>.md`, leaving a 1-line pointer naming when to read it. Keep always-needed facts inline.

Done when: neither `docs/agents/workflow.md` nor the instructions file has any `<blank>` left, and every path referenced exists (`GLOSSARY.md` and `mockups/` excepted).

## 6. Changelog

Ask whether this repo ships user-facing versioned releases (recommend yes if `CHANGELOG.md`, version field, or release tags exist). On no, continue to Step 7.

On yes, choose when entries are written:

- **Unreleased per PR** (recommended): user-visible PRs add a bullet under `## [Unreleased]`; release PRs rename it to the version.
- **With the version bump**: write the entry in the version-bump PR (adjust the template to remove `## [Unreleased]`).

Write `docs/agents/changelog.md` from [changelog.md](changelog.md) with the repo's version format, and add its 1-line pointer to `## Workflow` in the instructions file:

- Unreleased per PR:
  ``- Changelog: user-visible PRs add a bullet under `## [Unreleased]` in `CHANGELOG.md`; read [docs/agents/changelog.md](docs/agents/changelog.md) first.``
- With version bump:
  ``- Changelog: version-bump PRs update `CHANGELOG.md`; read [docs/agents/changelog.md](docs/agents/changelog.md) first.``

If the instructions file has a legacy `## Changelog` section, migrate repo-specific lines into `docs/agents/changelog.md` and replace it with the pointer. Create `CHANGELOG.md` when missing; when **Unreleased per PR** is chosen, ensure `## [Unreleased]` is the first `##` heading (inserting it if an existing file lacks one) and update any version/release scripts that parse the top of `CHANGELOG.md`.

Done when: `docs/agents/changelog.md` has no `<blank>`, the instructions file has the pointer and no `## Changelog` section, `CHANGELOG.md` matches the choice, and local CI checks pass.

## 7. Ship

Commit the setup on its own branch and ship via `docs/agents/workflow.md` (this PR is the first live run of the gate and size label). Report files written, files untouched, the instructions file's line count before vs. after, and any manual steps left (such as branch protection). Remind the user that `/ask-simian` maps which file to edit later.
