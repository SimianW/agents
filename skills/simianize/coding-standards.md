# Coding standards

Read at review time. Formatting and lint are the tooling's job; this file holds only judgement calls a check can't make.

## Regression tests for fixed bugs

A fix for a bug the user reported, or one found in review, comes with a test that fails without the fix, at a seam from [docs/agents/seams.md](docs/agents/seams.md). If the bug can only be reproduced by hand, the PR says so and gives the steps that reproduce it.

Flag a fix with neither as `should`.
