## Workflow

- PRs & size: every change reaches `<base branch>` through a PR. Before opening, updating, or merging a PR, read [docs/agents/workflow.md](docs/agents/workflow.md).
- File length: keep code files at or under <limit> lines (split along a seam before raising a cap); see [docs/agents/workflow.md](docs/agents/workflow.md) for cap-ratchet rules and `<length command>`.
- Reviews: every gate review before merge (and any branch/PR review request) runs `review-loop` using `<tier command>`; only `implement` / `implement-spec` runs `code-review` before it.
- Naming: use [GLOSSARY.md](GLOSSARY.md) terms in modules, tests, and docs; add new terms there.
- Testing & bugs: test at the seams in [docs/agents/seams.md](docs/agents/seams.md); fix bugs via [docs/bugfix.md](docs/bugfix.md).
- Dev docs: put each module/test role in its header comment; keep setup, commands, and gotchas in `<developer doc>`.
- Frontend: run `mockup-first` before any visible UI change (`mockups/`; default UI language `<language>`; tokens in `<path>`).
- New features: for multi-step specs/tickets (`to-spec`, `to-tickets`, `implement`, `implement-spec`), read [docs/agents/workflow.md](docs/agents/workflow.md).
