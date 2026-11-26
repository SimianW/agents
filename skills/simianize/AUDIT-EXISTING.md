# Auditing existing checks

Disclosed reference for `simianize` when a repo already has its own review-tier script, PR-body check, or file-length check.

## Existing review-tier script (Step 2)

A repo with `scripts/review-tier.py` (or `scripts/check-pr-body.py` supporting `tier`) keeps its tier classifier. Note the tier command for Step 5 (`python3 scripts/review-tier.py [base]`, say), then check two things separately:

1. **PR-body gate:** verify the repo also has a PR-body check script and CI job (e.g., `scripts/check-pr-body.py` + `.github/workflows/pr-body.yml`). If it only has a standalone tier script and no body checker, keep one tier classifier: either add PR-body checking to that script, or install `check-pr-body.py` with its `classify` delegating to the repo's tier script for both the full PR and the changes after the approved commit. Never install a second, independent classifier with unfilled `TODO(repo)` defaults. Add the CI workflow and note the exact `<body check command>` for Step 5.
2. **Self-coverage:** each of these **gate files** must evaluate to tier 2, with no tier 0 rule (comment-only, docs, format) able to lower them:

- CI workflows (`.github/workflows/`, or the CI host's equivalent);
- the tier script and the PR-body check;
- any helper whose answer can lower a tier (such as a comment-only detector).

Show the user any gate file that falls short and offer to make it tier 2 with a unit test for each. Change only those rules; leave the rest of the script untouched.

**Done when (existing script):** the repo has both a tier command and a working PR-body check + CI job, and the PR-body check gets its tier from the same classifier as the tier command (on the same change, both name the same tier); in a scratch worktree, appending a line of code to each gate file one at a time makes the tier command print `Review tier: 2` naming that file, and the script's tests pass.

## Upgrading an existing PR-body checker

When `/simianize` runs again on a repo that already has a PR-body checker, whether `scripts/check-pr-body.py` or a check integrated into `scripts/review-tier.py` (or another script the `<body check command>` names), compare it with the template in `~/.agents/skills/review-loop/scripts/check-pr-body.py` and upgrade these generic parts from the template (in an integrated checker, add the equivalent functions and modes to that script rather than installing a second classifier):

- `VERDICT_ITEM` and `check_body`: the ``(diff `<12-hex>`)`` suffix;
- the `diff-hash` mode (`rev` defaults to `HEAD`) and the tree-pair `diff_hash`, which hashes `<merge-base>^{tree}..<rev>^{tree}` instead of `git diff` output, so no local git config changes it;
- `check_after_review`: the diff-hash match before the after-approval check;
- the `AGENT_STEERING_*` rules (`AGENTS.md` and `CLAUDE.md` by basename, in any folder).

Keep the repo's own `DEFAULT_BASE`, `HIGH_RISK_*`, `CHECKS_ONLY_*`, `classify_special`, and any other custom repo rules as they are. Until the upgrade lands, PRs keep the plain `` approved at `<sha>` `` Verdict the old checker accepts.

**Done when (upgrade):** the checker's `diff-hash <base> HEAD` prints the same hash as the template's, a Verdict with the right diff hash passes and a wrong one fails, a nested `AGENTS.md` is tier 1, and each gate file is still tier 2.

## Existing file-length check (Step 3)

A repo that already enforces file length (e.g., ESLint `max-lines`) keeps its own check and skips installing `file-length.py` and `file-length.yml`, **provided** it also compares caps against the PR's base:

- A PR that adds or raises a cap must fail unless its body contains a `- **Cap raised:**` item for that path (exact format in the `pr` skill).
- A check that only inspects the working tree lets raised caps pass silently.

If the repo's check lacks base-cap comparison, add it to the repo's own tooling (the PR-body check is a natural home since CI already passes it the PR body and base), with tests.
