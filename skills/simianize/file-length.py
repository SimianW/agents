#!/usr/bin/env python3
"""Length limit for every code file, with a cap for each file already over it.

Usage:
    python3 scripts/file-length.py          # check every code file; exit 1 on any problem
    python3 scripts/file-length.py --caps   # print a CAPS block for the files over MAX_LINES

Reads the working tree: tracked files, and untracked files that git does not ignore. Only code
counts, by the same rule as the size label: `is_code` is loaded from scripts/pr-size.py, so its
SKIP_* settings decide here too. Binary files are left out.

Lines are counted as ESLint's `max-lines` counts them: \\r\\n, \\r, \\n, U+2028 and U+2029 end a line,
blank lines and comments count, and the empty piece after a final line break does not. An empty
file is 1 line.

A file over MAX_LINES fails unless CAPS holds its path. A capped file fails when it grows past its
cap, and also when it shrinks below it: the cap must come down to the new length, so caps only
ratchet down. A cap whose file is back within MAX_LINES, or gone, must be dropped.

CI runs this on every PR and on every push to the default branch: .github/workflows/file-length.yml.
Exits 0 when every file passes, or after --caps; 1 on a failing file or when git fails; 2 on bad usage.
"""
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


# --------------------------------------------------------------------------------------------
# Repo settings. Paths are repo-relative with forward slashes.
# --------------------------------------------------------------------------------------------

MAX_LINES = 500

# Each code file over MAX_LINES, capped at its length. Raising a cap needs the reason in the PR
# body; prefer splitting the file along a seam.
# TODO(repo): fill from the output of `python3 scripts/file-length.py --caps`.
CAPS = {
}


# --------------------------------------------------------------------------------------------
# The rest is generic.
# --------------------------------------------------------------------------------------------

LINE_BREAK = re.compile("\r\n|[\r\n\u2028\u2029]")


class GitError(Exception):
    pass


def git(*args, cwd=None):
    result = subprocess.run(["git", *args], capture_output=True, cwd=cwd)
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", "replace").strip()
        raise GitError(f"git {' '.join(args)} failed: {message}")
    return result.stdout


def load_is_code():
    """Return `is_code` from pr-size.py beside this script (its name has a hyphen, so no import)."""
    path = Path(__file__).resolve().with_name("pr-size.py")
    spec = importlib.util.spec_from_file_location("pr_size", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.is_code


def count_lines(data):
    lines = LINE_BREAK.split(data.decode("utf-8", "replace"))
    if len(lines) > 1 and lines[-1] == "":
        lines.pop()
    return len(lines)


def code_file_lines(root, is_code):
    """Return {path: lines} for every code file in the working tree."""
    listed = git("ls-files", "-z", cwd=root) + b"\0"
    listed += git("ls-files", "--others", "--exclude-standard", "-z", cwd=root)
    result = {}
    for raw in set(listed.split(b"\0")):
        path = raw.decode("utf-8", "replace")
        if not path or not is_code(path):
            continue
        try:
            data = Path(root, path).read_bytes()
        except OSError:  # Deleted, a nested repo's folder or a dangling symlink: nothing to count.
            continue
        if b"\0" not in data:
            result[path] = count_lines(data)
    return result


def problems(files):
    found = []
    for path, lines in files.items():
        if lines > MAX_LINES and path not in CAPS:
            found.append(f"{path}: {lines} lines, over the limit of {MAX_LINES}: split it along a seam, "
                         f"or cap it at {lines} in CAPS with the reason in the PR body")
    for path, cap in CAPS.items():
        lines = files.get(path)
        if lines is None:
            found.append(f"{path}: capped, but not a code file in the tree: drop its cap")
        elif lines <= MAX_LINES:
            found.append(f"{path}: {lines} lines, within the limit of {MAX_LINES}: drop its cap")
        elif lines > cap:
            found.append(f"{path}: {lines} lines, over its cap of {cap}: split it along a seam, "
                         f"or raise its cap with the reason in the PR body")
        elif lines < cap:
            found.append(f"{path}: {lines} lines, under its cap of {cap}: lower its cap to {lines}")
    return sorted(found)


def caps_block(files):
    over = sorted((path, lines) for path, lines in files.items() if lines > MAX_LINES)
    if not over:
        return "CAPS = {\n}"
    rows = "".join(f"    {json.dumps(path, ensure_ascii=False)}: {lines},\n" for path, lines in over)
    return "CAPS = {\n" + rows + "}"


def main(argv):
    if argv not in ([], ["--caps"]):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        is_code = load_is_code()
        root = git("rev-parse", "--show-toplevel").decode("utf-8").strip()
        files = code_file_lines(root, is_code)
    except (GitError, OSError) as error:
        print(f"file-length: {error}", file=sys.stderr)
        return 1
    if argv == ["--caps"]:
        print(caps_block(files))
        return 0
    found = problems(files)
    for line in found:
        print(line)
    if found:
        print(f"file-length: {len(found)} problem{'s' * (len(found) != 1)} in {len(files)} files checked")
        return 1
    print(f"file-length: ok, {len(files)} files checked, {len(CAPS)} capped")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
