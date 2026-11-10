# agents

Global steering for Claude Code and Codex, shared by every machine. This repo is checked out at `~/.agents`.

| Path | Read by |
|---|---|
| `AGENTS.md` | Claude Code through `@~/.agents/AGENTS.md` in `claude/CLAUDE.md`; Codex through the symlink `~/.codex/AGENTS.md` |
| `claude/CLAUDE.md` | Claude Code, through the symlink `~/.claude/CLAUDE.md` |
| `skills/<name>/` | Codex directly; Claude Code through the symlinks `~/.claude/skills/<name>` |
| `.skill-lock.json` | the [skills CLI](https://github.com/vercel-labs/skills): where each upstream skill came from |
| `bin/sync`, `systemd/` | the timer that pulls this repo every 10 minutes |
| `bin/session-check` | the SessionStart hook of Claude Code and Codex |
| `machine.md` | not tracked; this machine's Tailscale MagicDNS name, used by `AGENTS.md` |

The symlinks, `machine.md`, the installed timer, and the hook entries live on each machine, outside git.

## Edit

Edit the files in `~/.agents`, then commit and push:

```sh
cd ~/.agents && git add -A && git commit -m "..." && git pull --rebase && git push
```

## Sync

- **Pull**: on each machine, the `agents-sync` timer runs `bin/sync` every 10 minutes. It pulls with `--ff-only`, so it never overwrites local work, and it adds or removes `~/.claude/skills` links to match `skills/`. Check it with `systemctl --user list-timers agents-sync.timer` and `journalctl --user -u agents-sync`.
- **Push**: `AGENTS.md` tells agents to commit and push their edits here in the same task.
- **Check**: at session start, `bin/session-check` tells the agent when this checkout has uncommitted files, unpushed commits, or commits the timer could not pull. To resolve: commit or discard the uncommitted files, then `git pull --rebase && git push`.

## Upstream skills

Git is the source of truth. The skills CLI is only an import tool: run it on one machine, review the diff, commit, push, and let other machines pull.

```sh
npx skills update -g      # or: npx skills add <owner/repo> -g -a claude-code -a codex
git -C ~/.agents diff
```

An update overwrites local edits to an upstream skill. These skills carry local edits:

- `pr` (upstream `mattpocock/skills`): the `+`/`-` colour rule for `diff` blocks.

Restore those edits with `git checkout -p` before you commit. Skills not listed in `.skill-lock.json` are authored here and have no upstream.

## New machine

```sh
# 1. Check out the repo. If ~/.agents already exists, adopt it in place
#    so the skills directory never disappears:
cd ~/.agents && git init -b main && git remote add origin git@github.com:SimianW/agents.git \
  && git fetch origin && git reset origin/main && git checkout -- . && git branch -u origin/main
#    Otherwise: git clone git@github.com:SimianW/agents.git ~/.agents
#    Without a GitHub SSH key, use https://github.com/SimianW/agents.git with `gh auth setup-git`.

# 2. This machine's MagicDNS name (not `hostname`; `tailscale status --self --json` shows it as DNSName):
echo "This machine's Tailscale MagicDNS name, used as \`<host>\` in local page URLs: \`<name>\`" > ~/.agents/machine.md

# 3. Symlinks:
mkdir -p ~/.claude/skills ~/.codex
ln -sfn ../.agents/AGENTS.md ~/.codex/AGENTS.md
ln -sfn ../.agents/claude/CLAUDE.md ~/.claude/CLAUDE.md
sh ~/.agents/bin/sync

# 4. Timer (Linux, systemd user session; loginctl enable-linger keeps it running while logged out):
mkdir -p ~/.config/systemd/user && cp ~/.agents/systemd/agents-sync.* ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now agents-sync.timer
```

5. Hooks: add `sh "$HOME/.agents/bin/session-check"` as a `SessionStart` command hook in `~/.claude/settings.json` and in `~/.codex/hooks.json`.
