#!/usr/bin/env python3
"""Review tier and PR-body check for review-loop. A template: copy it into a repo and fill the TODOs.

Copy to `scripts/check-pr-body.py` in the repo, fill in the `TODO(repo)` blanks below, and run it
in CI on every pull request (example workflow at the bottom of this file).

Two modes:

    python3 scripts/check-pr-body.py tier [base]          # print `Review tier: N` for HEAD's changes
    PR_BODY=... python3 scripts/check-pr-body.py [base]   # check a PR body (CI)

`base` defaults to DEFAULT_BASE. The PR body records the review as a Markdown list, by convention
under a `## Review` heading at the end of the body (layout in the `pr` skill):

    ## Review

    - **Tier:** 1
    - **Verdict:** approved at `fd81ae1`
    - **Reviewers:** gpt-6.2-sol ×2, claude-opus-5-5 ×2, gemini-4-neon ×2

The check enforces:

1. The first Tier item gives N in 0..MAX_TIER, and N is at least the tier computed from the changed
   files against base.
2. When the computed tier is at least REVIEW_FROM_TIER, the last Verdict item reads
   `approved at <sha>` or `overridden by <user> at <sha>` (7 to 40 hex digits, backticks optional;
   the override form records a person shipping a stuck review-loop), the sha exists in this checkout,
   and nothing changed after it reaches REVIEW_FROM_TIER. The approved commit is replayed onto the
   current base with `git merge-tree` (git 2.40+), so a later merge or rebase of the base branch
   does not count as a change. When the replay conflicts, the check compares against the sha
   itself, limited to paths the PR touched.
3. The Reviewers item is for people; the check does not read it.

Items inside HTML comments (`<!-- ... -->`) and fenced code blocks do not count: they never render.

Exits 0 when the body passes; 1 with one `FAIL:` line per failure otherwise; 2 on bad usage.
"""
import os
import re
import subprocess
import sys
from pathlib import PurePosixPath


# --------------------------------------------------------------------------------------------
# Repo settings. Fill these in for each repo. Paths are repo-relative with forward slashes.
# --------------------------------------------------------------------------------------------

DEFAULT_BASE = "origin/main"  # TODO(repo): the base branch the PRs target.

MAX_TIER = 2  # Tiers run 0..MAX_TIER. 0: checks only; 1: ordinary code; 2: high risk.
REVIEW_FROM_TIER = 1  # Changes at this tier or above need a review-loop Verdict.

# Tier 2: paths where a mistake is costly. Match the "Reviews" triggers in the global AGENTS.md:
# auth, sessions, secrets, permissions, payments, user-data privacy, migrations and schema, data
# deletion, deploy, CI, Docker/compose, hooks, cron/launchd/systemd, sync and install scripts,
# and public APIs, CLIs or config formats other code depends on.
HIGH_RISK_PREFIXES = (
    ".github/workflows/",
    # TODO(repo): e.g. "src/auth/", "migrations/", "deploy/", "infra/".
)
HIGH_RISK_FILES = (
    "scripts/check-pr-body.py",  # This check gates itself: weakening it needs a tier-2 review.
    # TODO(repo): single files that read or write secrets, storage or permissions, e.g.
    # "Dockerfile", "docker-compose.yml", "src/config/schema.ts".
)

# Tier 0: changes that need only the CI checks, no review.
CHECKS_ONLY_PREFIXES = (
    "docs/",
    "notes/",
    # TODO(repo): asset or output folders, e.g. "design/", "assets/icons/", "results/".
)
CHECKS_ONLY_SUFFIXES = (
    ".md",
    # TODO(repo): e.g. ".png", ".svg", ".txt".
)


def classify_special(path, base_rev, root):
    """TODO(repo), optional: return (tier, reason) for a path that needs a closer look, or None.

    Prefer the path lists above: put a file that mixes risky and ordinary code in HIGH_RISK_FILES.
    A rule here is a heuristic that needs upkeep as the file changes, so write one only when a
    file's tier must depend on what changed inside it. butter, for example, reads
    extension/manifest.json at base_rev and in the working tree: a change to `permissions` or
    `content_scripts` is tier 2, a change to `version` alone is tier 0, anything else is tier 1.
    Read the old content with git("show", f"{base_rev}:{path}", cwd=root) and the new content
    from the working tree. Returning None falls through to the prefix rules.
    """
    return None


# --------------------------------------------------------------------------------------------
# The rest is generic. Change it only when the PR-body format in the `pr` skill changes.
# --------------------------------------------------------------------------------------------

FENCE_OPENER = re.compile(r"(`{3,}|~{3,})(.*)")
TIER_ITEM = re.compile(r"[-*] \*\*Tier:\*\* ([0-9]+)")
VERDICT_ITEM = re.compile(r"[-*] \*\*Verdict:\*\* (approved|overridden by [^`@\s]+) at (`?)([0-9a-fA-F]{7,40})\2")


def rendered_lines(body):
    """Return the body's stripped lines without the text that Markdown does not render.

    Drops HTML comments (`<!-- ... -->`, on one line or across several; the text around them on
    a line stays) and fenced code blocks (``` or ~~~, with or without an info string; all fence
    lines go). A fence closes on a line of only its own character, at least as long as the
    opener; a backtick opener's info string has no backtick, so ```x``` is inline code. An unclosed
    comment or fence hides the rest of the body. Fence markers inside a comment, and `<!--`
    inside a fence, are literal. Indented code blocks are not recognised.
    """
    lines = []
    fence = None  # (character, length) of the open fence
    in_comment = False
    for raw in (body or "").splitlines():
        stripped = raw.strip()
        if fence is not None:
            if stripped and set(stripped) == {fence[0]} and len(stripped) >= fence[1]:
                fence = None
            continue
        if not in_comment:
            opener = FENCE_OPENER.match(stripped)
            if opener and not (opener.group(1)[0] == "`" and "`" in opener.group(2)):
                fence = (opener.group(1)[0], len(opener.group(1)))
                continue
        kept, i = [], 0
        while i < len(raw):
            if in_comment:
                end = raw.find("-->", i)
                if end < 0:
                    break
                in_comment, i = False, end + 3
            else:
                start = raw.find("<!--", i)
                if start < 0:
                    kept.append(raw[i:])
                    break
                kept.append(raw[i:start])
                in_comment, i = True, start + 4
        lines.append("".join(kept).strip())
    return lines


class GitError(Exception):
    pass


def git(*args, cwd=None):
    result = subprocess.run(["git", *args], capture_output=True, cwd=cwd)
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", "replace").strip()
        raise GitError(f"git {' '.join(args)} failed: {message}")
    return result.stdout.decode("utf-8")


def changed_since(rev, root):
    """Paths that differ between rev and the working tree, untracked files included, sorted."""
    tracked = git("diff", "--name-only", "--no-renames", "-z", rev, "--", cwd=root)
    untracked = git("ls-files", "--others", "--exclude-standard", "-z", cwd=root)
    return sorted({path for path in (tracked + untracked).split("\0") if path})


def classify_path(path, base_rev, root):
    """Return (tier, reason) for one path. The first matching rule wins."""
    special = classify_special(path, base_rev, root)
    if special is not None:
        return special
    if path.startswith(HIGH_RISK_PREFIXES) or path in HIGH_RISK_FILES:
        return MAX_TIER, f"{path} (high risk)"
    if path.startswith(CHECKS_ONLY_PREFIXES) or PurePosixPath(path).suffix in CHECKS_ONLY_SUFFIXES:
        return 0, f"{path} (docs or assets)"
    return 1, path


def classify(paths, base_rev, root):
    """Return (tier, reasons): the highest tier any path reaches, and the paths that reach it."""
    results = [classify_path(path, base_rev, root) for path in sorted(set(paths))]
    tier = max(result_tier for result_tier, _ in results)
    return tier, [reason for result_tier, reason in results if result_tier == tier]


def check_body(body, tier, reasons, review_gate, head):
    """Return (failures, passes) for a PR body against the computed tier."""
    lines = rendered_lines(body)
    failures, passes = [], []

    claims = [int(m.group(1)) for m in map(TIER_ITEM.fullmatch, lines) if m]
    claimed = claims[0] if claims else None
    if claimed is None or claimed > MAX_TIER:
        failures.append(f"no `- **Tier:** N` item with N in 0..{MAX_TIER}; add `- **Tier:** {tier}`")
    elif claimed < tier:
        failures.append(f"body claims Tier {claimed}, but the changes reach tier {tier}: {'; '.join(reasons)}")
    else:
        passes.append(f"Tier {claimed} is at least the computed tier {tier}")

    if tier < REVIEW_FROM_TIER:
        passes.append(f"tier {tier} needs no Verdict item")
        return failures, passes

    verdicts = [m for m in map(VERDICT_ITEM.fullmatch, lines) if m]
    if not verdicts:
        failures.append(f"tier {tier} needs a Verdict item; add `- **Verdict:** approved at {head}` after review-loop approves")
        return failures, passes
    verdict, sha = verdicts[-1].group(1), verdicts[-1].group(3)
    passes.append(f"Verdict: {verdict} at {sha}")
    gate_failures, gate_passes = review_gate(sha)
    return failures + gate_failures, passes + gate_passes


def post_review_paths(sha, base, pr_paths, root):
    """Return (paths, rev): paths changed after the approved sha, and the rev holding their reviewed state."""
    old_base = git("merge-base", sha, base, cwd=root).strip()
    new_base = git("merge-base", "HEAD", base, cwd=root).strip()
    try:
        tree = git("merge-tree", "--write-tree", f"--merge-base={old_base}", sha, new_base, cwd=root)
        tree = tree.splitlines()[0].strip()
        return changed_since(tree, root), tree
    except GitError:  # The replay conflicts: compare against sha, limited to the PR's own paths.
        at_review = git("diff", "--name-only", "--no-renames", "-z", old_base, sha, "--", cwd=root)
        touched = {path for path in at_review.split("\0") if path} | set(pr_paths)
        return [path for path in changed_since(sha, root) if path in touched], sha


def check_after_review(sha, base, pr_paths, root):
    """Return (failures, passes) for the changes made after the approved commit."""
    try:
        full = git("rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}", cwd=root).strip()
    except GitError:
        return [f"approved commit {sha} is not in this checkout (force-push?); run review-loop again and update the sha"], []
    changed, reviewed = post_review_paths(full, base, pr_paths, root)
    if not changed:
        return [], [f"nothing changed after the approved commit {sha}"]
    tier, reasons = classify(changed, reviewed, root)
    if tier >= REVIEW_FROM_TIER:
        return [f"changes after the approved commit {sha} reach tier {tier}: {'; '.join(reasons)}; run review-loop again and update the sha"], []
    return [], [f"changes after the approved commit {sha} are tier 0"]


def collect(base):
    """Return (root, merge_base, paths) for HEAD's work against base."""
    root = git("rev-parse", "--show-toplevel").strip()
    merge_base = git("merge-base", "HEAD", base, cwd=root).strip()
    return root, merge_base, changed_since(merge_base, root)


def main(argv):
    tier_mode = bool(argv) and argv[0] == "tier"
    args = argv[1:] if tier_mode else argv
    if len(args) > 1 or (args and args[0].startswith("-")):
        print("usage: check-pr-body.py tier [base] | PR_BODY=... check-pr-body.py [base]", file=sys.stderr)
        return 2
    base = args[0] if args else DEFAULT_BASE
    try:
        root, merge_base, paths = collect(base)
        if not paths:
            print(f"check-pr-body: no changes against {base} (merge base {merge_base[:7]})", file=sys.stderr)
            return 1
        tier, reasons = classify(paths, merge_base, root)
        if tier_mode:
            print(f"Review tier: {tier}")
            print("\n".join(reasons))
            return 0
        head = git("rev-parse", "--short", "HEAD", cwd=root).strip()
        failures, passes = check_body(
            os.environ.get("PR_BODY", ""),
            tier,
            reasons,
            lambda sha: check_after_review(sha, base, paths, root),
            head,
        )
    except (GitError, OSError) as error:
        print(f"check-pr-body: {error}", file=sys.stderr)
        return 1
    for message in failures:
        print(f"FAIL: {message}")
    if failures:
        return 1
    for message in passes:
        print(f"PASS: {message}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


# --------------------------------------------------------------------------------------------
# Example CI: .github/workflows/pr-body.yml. Make `pr-body` a required check in branch
# protection. A draft run is renamed instead of skipped, because a skipped required check
# counts as passed.
#
# name: PR body
# on:
#   pull_request:
#     types: [opened, edited, synchronize, reopened, ready_for_review]
# jobs:
#   pr-body:
#     name: ${{ github.event.pull_request.draft && 'pr-body (draft, runs when ready)' || 'pr-body' }}
#     runs-on: ubuntu-latest
#     steps:
#       - if: ${{ !github.event.pull_request.draft }}
#         uses: actions/checkout@v4
#         with:
#           ref: ${{ github.event.pull_request.head.sha }}  # The head, not the merge ref.
#           fetch-depth: 0                                  # The Verdict sha needs history.
#       - if: ${{ !github.event.pull_request.draft }}
#         uses: actions/setup-python@v5
#         with:
#           python-version: '3.x'
#       - if: ${{ !github.event.pull_request.draft }}
#         env:
#           PR_BODY: ${{ github.event.pull_request.body }}
#           BASE_REF: origin/${{ github.event.pull_request.base.ref }}
#         run: python3 scripts/check-pr-body.py "$BASE_REF"
# --------------------------------------------------------------------------------------------
