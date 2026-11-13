# This machine

## Identity

- This machine: `<name>`, <what it is and what it is for>
- OS: <OS and version; say so when it runs inside WSL, a VM or a container>
- The user: <who the user is here, when that changes what an agent does>

## Access

- <How the user reaches it: sits at it, or connects from another device over Tailscale or SSH>

## Other machines

- `<name>`: <what it is>, reached with <an SSH alias, a Tailscale name, or a linked T3 environment>

## Local pages

- `<host>`: `<name>`, this machine's Tailscale MagicDNS name; `localhost` on the machine the user sits at
- `<bind>`: the Tailscale interface or `0.0.0.0`; `127.0.0.1` on the machine the user sits at

## Tools and paths

- <A tool an agent would assume is here but is missing, or one that is here and unusual>
- <Where things live: repos, data, lab folders, where secrets are stored>

## Rules

- <What to do differently on this machine, and why>
