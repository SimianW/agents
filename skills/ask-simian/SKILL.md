---
name: ask-simian
description: Ask what each workflow file is for and which one to edit for a change. A map of the files simianize sets up and the global steering behind them.
disable-model-invocation: true
---

# Ask Simian

You don't remember which file holds which rule, so ask.

Find the user's question in the tables below, then read the file itself before you answer: the summaries here are for orientation only. Answer with the file to edit, the section in it, and the **scope** the edit will have. For which skill or flow fits a situation, send the user to `/ask-matt`.

## Scope

Every rule lives at one of four scopes. Settle the scope first; it picks the file.

- **Everywhere**: the global steering in `~/.agents`, read in every session on every machine. Commit and push an edit there in the same task.
- **Every repo set up from now on**: a template in `~/.agents/skills/simianize/`. A repo that is already set up holds a copy. Re-running `/simianize` there updates `docs/agents/workflow.md`, the `## Workflow` block in `AGENTS.md`, `docs/agents/changelog.md`, and the size and file-length scripts and workflows. It also upgrades the generic parts of `scripts/check-pr-body.py` (Verdict format, `diff-hash`, after-approval check, agent steering rules) and keeps the repo's path settings (`simianize/AUDIT-EXISTING.md`). Every other file is the repo's own once written (`docs/bugfix.md`, `CODING_STANDARDS.md`, `docs/agents/`, a standalone tier script), so make the same edit there by hand.
- **This repo only**: the repo's own file.
- **This machine only**: `~/.agents/machine.md`, which git does not track. Each machine has its own.

## Which file to edit

| To change | This repo | Every repo from now on |
|---|---|---|
| the always-on workflow pointers in `AGENTS.md` (invariants, Frontend language/tokens) | `AGENTS.md`, `## Workflow` | `simianize/workflow-block.md` |
| the detailed PR gate, PR size, cap-ratchet, or new-feature flow | `docs/agents/workflow.md` | `simianize/workflow.md` |
| the PR size thresholds, or which paths count as code | top of `scripts/pr-size.py` | `simianize/pr-size.py` |
| when the size label is set, or how CI sets it | `.github/workflows/pr-size.yml` | `simianize/pr-size.yml` |
| the file length limit, or a file's cap | top of `scripts/file-length.py` | `simianize/file-length.py` |
| how CI runs the file-length check | `.github/workflows/file-length.yml` | `simianize/file-length.yml` |
| which paths need more or less review | top of `scripts/check-pr-body.py` (or `scripts/review-tier.py`) | `review-loop/scripts/check-pr-body.py` |
| how `/simianize` audits existing tier or file-length checks | | `simianize/AUDIT-EXISTING.md` |
| a rule reviewers must enforce | `CODING_STANDARDS.md` | `simianize/coding-standards.md` |
| where tests go, or the checks to run before a PR | `docs/agents/seams.md` | `simianize/seams.md` |
| the bug-fix steps | `docs/bugfix.md` | `simianize/bugfix.md` |
| how changelog entries are written, and when | `docs/agents/changelog.md`, and the Changelog pointer in `## Workflow` | `simianize/changelog.md` |
| where issues live, and the commands for them | `docs/agents/issue-tracker.md` | upstream `setup-matt-pocock-skills` |
| the triage label names | `docs/agents/triage-labels.md`, and the labels on the tracker | upstream `setup-matt-pocock-skills` |
| a domain term | `GLOSSARY.md`, with `domain-modeling` | |
| a decision that is hard to reverse | a new file in `docs/adr/`, with `domain-modeling` | |
| what `/simianize` sets up, or its order | | `simianize/SKILL.md` |

These rules live only in `~/.agents`:

| To change | Edit |
|---|---|
| opt-in lead-and-delegate mode (~5 tool call threshold, thread hygiene) | `~/.agents/skills/simian-mode/SKILL.md` |
| which model does which role, brief format, or Verify checklist | `~/.agents/delegation.md` |
| default review triggers (for repos with no review rule), panel models, rounds, or briefs | `~/.agents/skills/review-loop/SKILL.md` |
| the PR body layout or `Cap raised` format | `~/.agents/skills/pr/SKILL.md` |
| the Tier or Verdict item's format | three places together: `review-loop/SKILL.md`, `pr/SKILL.md`, and every repo's `scripts/check-pr-body.py` |
| how replies are written (bold, math, English tips, file links, local pages, pointers) | `~/.agents/AGENTS.md` |
| how a mockup is built, approved, and verified | `~/.agents/skills/mockup-first/SKILL.md` |
| a fact or rule for this machine only | `~/.agents/machine.md` |
| the headings a new machine's file starts from | `~/.agents/machine.example.md` |
| how `~/.agents` syncs, or which upstream skills carry local edits | `~/.agents/README.md` |

A skill that came from upstream (listed in `~/.agents/.skill-lock.json`) loses local edits on `npx skills update -g`. After editing one, list it in the README's "Upstream skills" section.

## What each file is for

In a repo:

| File | Holds | Read by |
|---|---|---|
| `CLAUDE.md` | the one line `@AGENTS.md` | Claude Code |
| `AGENTS.md`, `## Agent skills` | pointers to `docs/agents/` skill configs | every engineering skill |
| `AGENTS.md`, `## Workflow` | concise invariants (PRs, file limit, glossary) and 1-line pointers to workflow, seams, bugfix, frontend, changelog | every session |
| `docs/agents/workflow.md` | full PR gate commands, PR size, file-length ratchet, new-feature 4-skill flow, delegation note | opening/merging PRs, raising caps, new features, `/simian-mode` |
| `docs/agents/changelog.md` | changelog rules and categories | user-visible PRs and releases |
| `CHANGELOG.md` | release entries (`## [Unreleased]` + releases) | users |
| `docs/agents/issue-tracker.md` | where issues live and commands for them | `to-spec`, `to-tickets`, `implement`, `triage`, `code-review` |
| `docs/agents/triage-labels.md` | triage label names | `triage`, `to-spec`, `to-tickets` |
| `docs/agents/domain.md` | how to read `GLOSSARY.md` and ADRs | skills that explore the code |
| `docs/agents/seams.md` | agreed test seams and pre-PR checks | `tdd`, `to-spec`, `implement`, `diagnosing-bugs` |
| `docs/bugfix.md` | bug-fix steps: Control, Red, Green, Review and ship | any bug fix |
| `CODING_STANDARDS.md` | judgement-call rules checks can't make | `review-loop`, `code-review`; `retro` adds to it |
| `GLOSSARY.md` | domain terms | every skill that names things |
| `docs/adr/` | hard-to-reverse decisions | skills that explore the code |
| `scripts/check-pr-body.py` | path tiers and PR-body Review check | `review-loop`, CI |
| `.github/workflows/pr-body.yml` | runs PR-body check on ready PRs | CI |
| `scripts/pr-size.py` | PR code-size label and non-code exclusions | CI, local checks |
| `.github/workflows/pr-size.yml` | labels every PR by code size | CI |
| `scripts/file-length.py` | code file line limit and cap ratchet | CI, local checks |
| `.github/workflows/file-length.yml` | runs file-length check on PRs and pushes | CI |

In `~/.agents`:

| File | Holds |
|---|---|
| `AGENTS.md` | lean global rules for Claude Code, Codex, and Antigravity: machine file, English coaching, reply formatting, local pages, thread titles, and pointers to `README.md`, `delegation.md`, and `review-loop` |
| `claude/CLAUDE.md` | the one line `@~/.agents/AGENTS.md` |
| `delegation.md` | shared disclosed reference: role → model/`target` table, brief rules, `Verify` checklist |
| `machine.md` | untracked machine-only facts and rules |
| `machine.example.md` | starter headings for `machine.md` |
| `README.md` | sync architecture, machine-local excludes, and locally edited upstream skills |
| `skills/simian-mode/` | opt-in user-invoked toggle for lead-and-delegate engineering workflow |
| `skills/simianize/` | `SKILL.md` setup steps, `AUDIT-EXISTING.md`, `workflow-block.md`, `workflow.md`, and per-repo templates |
| `skills/review-loop/` | `SKILL.md` (with default review triggers, panel, ledger, briefs) and `scripts/check-pr-body.py` |
| `skills/review-loop-deprecated/` | old single-reviewer loop; runs only when asked by name |
| `skills/pr/SKILL.md` | PR body template including `Review`, `Tier`, and `Cap raised` format |
| other `skills/<name>/` | individual skills; `/ask-matt` maps those from `mattpocock/skills` |
