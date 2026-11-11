# agents

Global steering for Claude Code and Codex, shared by every machine. This repo is checked out at `~/.agents`.

| Path | Read by |
|---|---|
| `AGENTS.md` | Claude Code through `@~/.agents/AGENTS.md` in `claude/CLAUDE.md`; Codex through the symlink `~/.codex/AGENTS.md` |
| `claude/CLAUDE.md` | Claude Code, through the symlink `~/.claude/CLAUDE.md` |
| `skills/<name>/` | Codex directly; Claude Code through the symlinks `~/.claude/skills/<name>` |
| `.skill-lock.json` | the [skills CLI](https://github.com/vercel-labs/skills): where each upstream skill came from |
| `bin/sync`, `systemd/`, `launchd/` | the timer (Linux) or launchd agent (macOS) that pulls this repo every 10 minutes |
| `bin/session-check` | the SessionStart hook of Claude Code and Codex |
| `machine.md` | not tracked; this machine's `<host>` and `<bind>` for local page URLs, used by `AGENTS.md` |

The symlinks, `machine.md`, the installed timer, the hook entries, and any machine-local skills live on each machine, outside git.

## Edit

Edit the files in `~/.agents`, then commit and push:

```sh
cd ~/.agents && git add -A && git commit -m "..." && git pull --rebase && git push
```

## Sync

- **Pull**: on each machine, the `agents-sync` timer runs `bin/sync` every 10 minutes. It pulls with `--ff-only`, so it never overwrites local work, adds a `~/.claude/skills` link for every directory in `skills/`, and removes links whose target is gone. Check it on Linux with `systemctl --user list-timers agents-sync.timer` and `journalctl --user -u agents-sync`; on macOS with `launchctl print gui/$(id -u)/com.github.simianw.agents-sync` (`last exit code`) and `~/Library/Logs/agents-sync.log` (errors only).
- **Push**: `AGENTS.md` tells agents to commit and push their edits here in the same task.
- **Check**: at session start, `bin/session-check` tells the agent when this checkout has uncommitted files, unpushed commits, or commits the timer could not pull. To resolve: commit or discard the uncommitted files, then `git pull --rebase && git push`.

## Machine-local skills and files

To keep a skill (or any other file under `~/.agents`) on one machine only, list it in that machine's `~/.agents/.git/info/exclude`, not in `.gitignore`:

```sh
echo 'skills/agent-browser/' >> ~/.agents/.git/info/exclude
```

Git then ignores it, so `bin/session-check` does not report it, and `bin/sync` still links it into `~/.claude/skills` and leaves that link alone. Its `.skill-lock.json` entry is tracked, so drop it before you commit (`git checkout -p .skill-lock.json`); `npx skills update -g` then skips that skill, and you update it by running `npx skills add` again.

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

# 2. Local page address (AGENTS.md, "Local pages"). Remote machine: <host> is the
#    MagicDNS name (not `hostname`; `tailscale status --self --json` shows it as DNSName).
cat > ~/.agents/machine.md <<'MD'
This machine's values for local pages (see "Local pages" in AGENTS.md):

- `<host>`: `<name>`, this machine's Tailscale MagicDNS name
- `<bind>`: the Tailscale interface or `0.0.0.0`
MD
#    Machine the user sits at: `<host>` is `localhost` and `<bind>` is `127.0.0.1`.

# 3. Symlinks:
mkdir -p ~/.claude/skills ~/.codex
ln -sfn ../.agents/AGENTS.md ~/.codex/AGENTS.md
ln -sfn ../.agents/claude/CLAUDE.md ~/.claude/CLAUDE.md
sh ~/.agents/bin/sync

# 4a. Timer on Linux (systemd user session; loginctl enable-linger keeps it running while logged out):
mkdir -p ~/.config/systemd/user && cp ~/.agents/systemd/agents-sync.* ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now agents-sync.timer

# 4b. Timer on macOS (launchd user agent; runs while you are logged in). Its PATH covers
#     /usr/bin and Homebrew; git must reach GitHub without a terminal, e.g. an SSH key
#     without a passphrase or in the macOS keychain, or HTTPS through `gh auth setup-git`.
P=com.github.simianw.agents-sync
mkdir -p ~/Library/LaunchAgents && cp ~/.agents/launchd/$P.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/$P.plist
launchctl kickstart gui/$(id -u)/$P   # one run now; check `last exit code` in `launchctl print`
```

5. Hooks: add `sh "$HOME/.agents/bin/session-check"` as a `SessionStart` command hook in `~/.claude/settings.json` and in `~/.codex/hooks.json`, then approve the new Codex hook in Codex with `/hooks`.
6. Machine-local skills and leftovers: see [Machine-local skills and files](#machine-local-skills-and-files).
