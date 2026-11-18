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
- **Every repo set up from now on**: a template in `~/.agents/skills/simianize/`. A repo that is already set up holds a copy. Re-running `/simianize` there brings over a change to the `## Workflow` and `## Changelog` sections and to the size script and its workflow. Every other file is the repo's own once written (`docs/bugfix.md`, `CODING_STANDARDS.md`, `docs/agents/`, the tier script), so make the same edit there by hand.
- **This repo only**: the repo's own file.
- **This machine only**: `~/.agents/machine.md`, which git does not track. Each machine has its own.

## Which file to edit

| To change | This repo | Every repo from now on |
|---|---|---|
| the PR and merge rule, or the new-feature flow | `AGENTS.md`, `## Workflow` | `simianize/workflow.md` |
| whether a repo needs a mockup first, its UI language, or where its design tokens are | `AGENTS.md`, `## Workflow`, the Frontend bullet | `simianize/workflow.md` |
| the PR size thresholds, or which paths count as code | the settings at the top of `scripts/pr-size.py` | `simianize/pr-size.py` |
| when the size label is set, or how CI sets it | `.github/workflows/pr-size.yml` | `simianize/pr-size.yml` |
| which paths need more or less review | the settings at the top of `scripts/check-pr-body.py` (or the repo's own `scripts/review-tier.py`) | `review-loop/scripts/check-pr-body.py` |
| a rule reviewers must enforce | `CODING_STANDARDS.md` | `simianize/coding-standards.md` |
| where tests go, or the checks to run before a PR | `docs/agents/seams.md` | `simianize/seams.md` |
| the bug-fix steps | `docs/bugfix.md` | `simianize/bugfix.md` |
| how changelog entries are written, and when | `AGENTS.md`, `## Changelog` | `simianize/changelog.md` |
| where issues live, and the commands for them | `docs/agents/issue-tracker.md` | upstream `setup-matt-pocock-skills` |
| the triage label names | `docs/agents/triage-labels.md`, and the labels on the tracker | upstream `setup-matt-pocock-skills` |
| a domain term | `GLOSSARY.md`, with the `domain-modeling` skill | |
| a decision that is hard to reverse | a new file in `docs/adr/`, with the `domain-modeling` skill | |
| what `/simianize` sets up, or its order | | `simianize/SKILL.md` |

These rules live only in `~/.agents`:

| To change | Edit |
|---|---|
| which model does which kind of work | `~/.agents/claude/CLAUDE.md`, the Subagents table |
| how a delegate's result is checked | `~/.agents/claude/CLAUDE.md`, Verify |
| when a repo with no review rule needs a review | `~/.agents/claude/CLAUDE.md`, Reviews |
| review rounds, the panel models, the reviewer and cross-check briefs | `~/.agents/skills/review-loop/SKILL.md` |
| the PR body layout | `~/.agents/skills/pr/SKILL.md` |
| the Tier or Verdict item's format | three places together: `review-loop/SKILL.md`, `pr/SKILL.md`, and the pattern in every repo's `scripts/check-pr-body.py` |
| how replies are written (bold, math, English tips, links to files) | `~/.agents/AGENTS.md` |
| how a mockup is built, approved and verified | `~/.agents/skills/mockup-first/SKILL.md` |
| the mockup rule for a repo that is not set up | `~/.agents/AGENTS.md`, Frontend changes |
| a fact or rule for this machine only: which machine it is, how you reach it, the other machines it reaches, the local page address, its tools and paths | `~/.agents/machine.md` |
| the headings a new machine's file starts from | `~/.agents/machine.example.md` |
| how `~/.agents` syncs, or which upstream skills carry local edits | `~/.agents/README.md` |

A skill that came from upstream (listed in `~/.agents/.skill-lock.json`) loses local edits on `npx skills update -g`. After editing one, list it in the README's "Upstream skills" section.

## What each file is for

In a repo:

| File | Holds | Read by |
|---|---|---|
| `CLAUDE.md` | the one line `@AGENTS.md` | Claude Code |
| `AGENTS.md`, `## Agent skills` | pointers to the three `docs/agents/` files below | every engineering skill |
| `AGENTS.md`, `## Workflow` | the PR gate, PR size, reviews, naming, the frontend rule, new features, subagent models, and pointers to seams and bug fixes | every session |
| `AGENTS.md`, `## Changelog` | how a changelog bullet is written, and when; only in a repo that ships versioned releases | any PR the user can notice, and any release |
| `CHANGELOG.md` | the entries themselves: `## [Unreleased]` on top, then one per release | users |
| `docs/agents/issue-tracker.md` | where issues live and the commands for them | `to-spec`, `to-tickets`, `implement`, `triage`, `code-review` |
| `docs/agents/triage-labels.md` | the label string for each triage role | `triage`, `to-spec`, `to-tickets` |
| `docs/agents/domain.md` | how to read `GLOSSARY.md` and the ADRs | skills that explore the code |
| `docs/agents/seams.md` | the agreed test seams, and the checks to run before a PR | `tdd`, `to-spec`, `implement`, `diagnosing-bugs` |
| `docs/bugfix.md` | the bug-fix steps: Control, Red, Green, Review and ship | any bug fix |
| `CODING_STANDARDS.md` | judgement-call rules a check can't make | `review-loop` (pasted into the brief), `code-review`; `retro` adds to it |
| `GLOSSARY.md` | the repo's domain terms | every skill that names things |
| `docs/adr/` | decisions that are hard to reverse | skills that explore the code |
| `scripts/check-pr-body.py` | the tier of each path, and the check on a PR body's Review section | `review-loop`, CI |
| `.github/workflows/pr-body.yml` | runs that check on every ready PR | CI |
| `scripts/pr-size.py` | the size label for a change, and which paths count as code | CI; anyone, locally |
| `.github/workflows/pr-size.yml` | sets the size label on every PR | CI |

In `~/.agents`:

| File | Holds |
|---|---|
| `claude/CLAUDE.md` | Claude Code's global rules: delegation, Verify, Reviews |
| `AGENTS.md` | global rules for Claude Code and Codex: reply formatting, English coaching, local pages, steering-file upkeep |
| `machine.md` | facts and rules for this machine only; not tracked |
| `machine.example.md` | the headings a `machine.md` starts from |
| `README.md` | how the checkout syncs across machines, and how upstream skills are updated |
| `skills/simianize/` | `SKILL.md`, the setup steps; every other file is a template it writes from |
| `skills/review-loop/` | `SKILL.md`, the review loop; `scripts/check-pr-body.py`, the gate's template |
| `skills/review-loop-deprecated/` | the old single-reviewer loop (Sol, then Opus); runs only when asked by name |
| `skills/pr/SKILL.md` | the PR body template, with the Review section |
| other `skills/<name>/` | one skill each; `/ask-matt` maps the ones from `mattpocock/skills` |
