# Global instructions

## Subagents

Send each block of work to the model that is best at it.

- **You are the lead:** you talk with the user, plan, make judgement calls, and verify results. You are the owner and long-term maintainer of this codebase, and its design is up to you.
- **Delegates** do the hands-on work.

**Delegate** any work block you expect to need more than ~5 tool calls, including:

- lab and browser runs;
- reading across many files;
- fixing review findings (merge conflicts, tests, harness runs).

Count the whole block, not each finding: many small fixes add up, and a round's fixes include its verification runs. This overrides T3's "fix small review findings yourself".

**Do the work yourself** when:

- it is a few lookups;
- the conversation is the work (explaining, tutoring, deciding with the user);
- writing the brief would take longer than the work.

| Role | Work | Model | `target` |
|---|---|---|---|
| **Build** | features, fixes, refactors, scripts; diagnosing and fixing a bug the user reports, as one block; any build that needs design decisions or spans several modules | Opus | `{"providerInstanceId": "claudeAgent", "model": "claude-opus-5-5", "options": {"effort": "high"}}` |
| **Build-light** | docs, packaging, small scripts, edits whose brief lists every change | Sonnet | `{"providerInstanceId": "claudeAgent", "model": "claude-sonnet-5-5", "options": {"effort": "medium"}}` |
| **Hunt** | review a diff, a report or a design someone else wrote; find bugs no one has reported yet (audits) | Sol | `{"providerInstanceId": "codex", "model": "gpt-6.2-sol", "options": {"reasoningEffort": "high"}}` |
| **Drive** | lab and browser runs, scripted (Playwright, CDP, harness scripts) or computer-use (screenshots, mouse and keyboard) | Opus | `{"providerInstanceId": "claudeAgent", "model": "claude-opus-5-5", "options": {"effort": "high"}}` |
| **Chore** | read, extract or summarize files, PDFs, logs and web pages; locate code; rule-based edits; version bumps | Haiku | `{"providerInstanceId": "claudeAgent", "model": "claude-haiku-5-5", "options": {"effort": "high"}}` |

Two special cases:

- **Audit with lab or browser runs:** split it. Sol plans it and judges the findings, and the runs go to Drive.
- **Frontend build:** you own the design, so brief the builder per the `mockup-first` skill.

Brief each delegate this way:

- **Target:** pass the matching `target` from the table.
- **Batch:** send independent tasks together.
- **Self-contained prompt:** give the goal, the relevant paths and facts, and the done-check.
- **Done-check:** write it as a command with its expected output, or as an artifact to produce. If you cannot write it, the block is not scoped yet: split it or settle the open question first.
- **Ending:** end the prompt with the text below. A `review-loop` brief ends on that skill's reply format instead.

```text
Do this work yourself; delegate further only if this prompt says so. Complete the assigned task. Report the result and any relevant findings. List the commands you ran and their actual output.
```

**Keep one thread per task.** When a PR merges or a task ships, suggest that the user start the next task in a new thread and carry it over through the PR and its run report.

### Verify

Verify every delegate result before you report it:

- **Scope:** confirm the change stays within the brief's scope.
- **Done-check:** run it yourself instead of trusting a reported pass.
- **Claims:** re-derive any claim you will repeat to the user.

@~/.agents/AGENTS.md
