# Delegation

Shared reference for starting subagents and verifying their work. Read when activating `/simian-mode` or when any skill or repo names a delegation role.

## Roles

| Role | Work | Model | `T3 target` |
|---|---|---|---|
| **Build** | features, fixes, refactors, scripts; diagnosing and fixing a reported bug as one block; builds needing design decisions or spanning modules | Opus | `{"providerInstanceId": "claudeAgent", "model": "claude-opus-5-5", "options": {"effort": "high"}}` |
| **Build-light** | docs, packaging, small scripts, edits whose brief lists every change | Sonnet | `{"providerInstanceId": "claudeAgent", "model": "claude-sonnet-5-5", "options": {"effort": "medium"}}` |
| **Hunt** | review a diff, report, or design someone else wrote; proactive audits for unreported bugs | Sol | `{"providerInstanceId": "codex", "model": "gpt-6.2-sol", "options": {"reasoningEffort": "high", "serviceTier": "priority"}}` |
| **Drive** | lab and browser runs, scripted (Playwright, CDP, harness scripts) or computer-use (screenshots, mouse, keyboard) | Sol | `{"providerInstanceId": "codex", "model": "gpt-6.2-sol", "options": {"reasoningEffort": "high", "serviceTier": "priority"}}` |
| **Chore** | read, extract, or summarize files, PDFs, logs, and web pages; locate code; rule-based edits; version bumps | Haiku | `{"providerInstanceId": "claudeAgent", "model": "claude-haiku-5-5", "options": {"effort": "high"}}` |

Two special cases:

- **Audit with lab or browser runs:** split it—Hunt plans the audit and judges findings, Drive runs the lab or browser steps.
- **Frontend build:** you own the design; brief the builder per the `mockup-first` skill.

## Briefs

- **Routing:** in T3 Code, launch via `delegate_task` with the matching `T3 target` JSON above; outside T3, use your harness's native subagent tool when the named model is available.
- **Batch:** launch independent tasks together in one turn.
- **Self-contained prompt:** state the goal, relevant paths and facts, and the done-check.
- **Done-check:** write a concrete command with its expected output, or an artifact to produce. If you cannot write one, the block is unscoped—split it or settle the open question first.
- **Ending:** close every brief with the block below (`review-loop` briefs use that skill's reply format instead):

```text
Do this work yourself; delegate further only if this prompt says so. Complete the assigned task. Report the result and any relevant findings. List the commands you ran and their actual output.
```

## Verify

Verify every delegate result before reporting it to the user:

- **Scope:** confirm changes stay inside the brief's scope.
- **Done-check:** run the done-check yourself rather than trusting a reported pass.
- **Claims:** re-derive any claim you will repeat to the user.
