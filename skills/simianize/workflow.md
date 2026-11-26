# Repo workflow

Disclosed procedure for pull requests, size/length checks, and multi-step feature delivery. Always-on invariants live in `AGENTS.md`.

## Pull requests and review gate

Every change reaches `<base branch>` through a PR.

1. Run `<tier command>` and include `- **Tier:** N` under `## Review` in the PR body (use the `pr` skill). Open the PR as a **draft** (`pr-body` CI runs on ready PRs).
2. For **Tiers 1 and 2**, run `review-loop` on the final diff (within the tier's round budget). On `APPROVE`, `review-loop` adds `- **Verdict:**` and `- **Reviewers:**` to the PR body. (**Tier 0** skips this step.)
3. Run the local body check: `<body check command>` (e.g., `PR_BODY="$(cat body.md)" python3 scripts/check-pr-body.py`).
4. Mark the draft PR **ready** once the local check passes, and merge only after CI is green.

## PR size

CI labels each PR from `size/XS` to `size/XXL` by lines of code changed (excluding prose, lock files, and binaries). Run `python3 scripts/pr-size.py` to check locally; CI owns setting the label.

## File length ratchet

Every code file stays at or under `<limit>` lines.

- Split a growing file along a seam before raising a cap.
- Existing files over the limit are capped in `<caps location>`; caps only ratchet down. When a change shortens a capped file, lower its cap (or drop it once within `<limit>`) in the same PR.
- Adding or raising a cap requires a `- **Cap raised:**` item in the PR body (exact format in the `pr` skill), or CI fails.
- Run `<length command>` locally before opening or updating a PR.

## New features

1. `to-spec` publishes the spec to the issue tracker labelled `ready-for-agent`.
2. Build directly with `implement <spec>`, or split via `to-tickets` and build with `implement-spec <spec>`.
3. Run `code-review` against the spec issue. Sort findings into **fix now / follow-up issue / drop** (one-line reason each) and stop for the user to choose. File each follow-up as a `ready-for-agent` issue.
4. After fixes, run `review-loop` on the final diff at its tier (listing approved refactors in its Intent).
5. Open a PR whose body includes `Closes #<issue>` and the `## Review` section's `Tier` item.

`to-spec`, `to-tickets`, `implement`, and `implement-spec` are user-invoked: at each handoff, tell the user the exact command to type (e.g., `/to-spec`).

## Delegation

Role models, `target` values, brief rules, and the `Verify` checklist live in `~/.agents/delegation.md` (and are activated for full sessions via `/simian-mode`). Any brief for delegated `implement` work must name the `tdd` skill and `docs/agents/seams.md`.
