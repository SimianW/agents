# agents

Global steering for Claude Code and Codex, shared by every machine. This repo is checked out at `~/.agents`.

| Path | Read by |
|---|---|
| `AGENTS.md` | Claude Code through `@~/.agents/AGENTS.md` in `claude/CLAUDE.md`; Codex through the symlink `~/.codex/AGENTS.md` |
| `claude/CLAUDE.md` | Claude Code, through the symlink `~/.claude/CLAUDE.md` |
| `skills/<name>/` | Codex directly; Claude Code through the symlinks `~/.claude/skills/<name>` |
| `.skill-lock.json` | the [skills CLI](https://github.com/vercel-labs/skills): where each upstream skill came from |
| `machine.md` | not tracked; this machine's Tailscale MagicDNS name, used by `AGENTS.md` |

The symlinks and `machine.md` live on each machine, outside git.

## Edit

Edit the files in `~/.agents`, then commit and push:

```sh
cd ~/.agents && git pull --ff-only && git add -A && git commit -m "..." && git push
```

On every other machine, pull:

```sh
git -C ~/.agents pull --ff-only
```

## Upstream skills

Git is the source of truth. The skills CLI is only an import tool: run it on one machine, review the diff, commit, push, and let other machines pull.

```sh
npx skills update -g      # or: npx skills add <owner/repo> -g -a claude-code -a codex
git -C ~/.agents diff
```

An update overwrites local edits to an upstream skill. These skills carry local edits:

- `pr` (upstream `mattpocock/skills`): the `+`/`-` colour rule for `diff` blocks.
- `review-loop` (upstream `SimianW/skills`): `at <sha>` in the review line.

Restore those edits with `git checkout -p` before you commit. If you add a skill, create its Claude Code symlink on each machine (see below).

## New machine

```sh
# 1. Check out the repo. If ~/.agents already exists, adopt it in place
#    so the skills directory never disappears:
cd ~/.agents && git init -b main && git remote add origin git@github.com:SimianW/agents.git \
  && git fetch origin && git reset origin/main && git checkout -- . && git branch -u origin/main
#    Otherwise: git clone git@github.com:SimianW/agents.git ~/.agents

# 2. This machine's MagicDNS name (not `hostname`; `tailscale status --self --json` shows it as DNSName):
echo "This machine's Tailscale MagicDNS name, used as \`<host>\` in local page URLs: \`<name>\`" > ~/.agents/machine.md

# 3. Symlinks:
mkdir -p ~/.claude/skills ~/.codex
ln -sfn ../.agents/AGENTS.md ~/.codex/AGENTS.md
ln -sfn ../.agents/claude/CLAUDE.md ~/.claude/CLAUDE.md
for d in ~/.agents/skills/*/; do n=$(basename "$d"); [ -e ~/.claude/skills/"$n" ] || ln -s ../../.agents/skills/"$n" ~/.claude/skills/"$n"; done
```
