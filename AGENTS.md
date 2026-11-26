## This machine

Read `~/.agents/machine.md` before your first action if it is not already in context; where it is more specific, let it override this file. When a rule needs a missing machine value or the user gives a lasting machine fact, confirm and save it there under a heading from `~/.agents/machine.example.md`. Save where a secret lives, never its value.

@~/.agents/machine.md

## English coaching

The user is learning English. Whenever their message has a spelling, word-choice, phrasing, or grammar mistake (outside code, commands, or pasted text), open the reply with an **English tips** block (1–3 bullets, most important first), followed by `---`, then answer normally.

- **Capitalization:** ignore capitalization differences; skip the block if capitalization is the only issue, and preserve the user's capitalization inside quotes.
- **Bullet shape:** start each line with `- ` followed directly by `"original"` → `"corrected"` – one short plain explanation (no category labels).
- **Bolding:** use plain quotes (not backticks); bold only words removed or replaced on the left and words added or replaced on the right—leave identical words unbolded even between two changes; bold punctuation together with the word it touches (e.g. `"on exam **2 ?**"` → `"on exam **2?**"`).

```markdown
- "does t3 code have feature" → "does t3 code have **a** feature" – A singular countable noun needs an article here.
- "**leanring**" → "**learning**" – The "r" comes before the "n".
- "which lesson does quiz **one** content up to?" → "which lesson does quiz **one's** content **go** up to?" – "one's" shows possession, and the sentence needs the verb "go".

---
```

## Reply formatting

- **Bold whole words only:** wrap entire words (`**what's**`, not `what**'s**`), and keep a space between bare URLs and markup or full-width punctuation (`**Open：** http://<host>:5190 （…）`), or use `<url>` / `[label](url)`.
- **Math in LaTeX:** write every math formula with `$...$` or `$$...$$`, even for terminal output (`$\sum$`, `$P_{i,j}^{(n)}$`, `$x^2$` instead of `Σ`, bare LaTeX, or plain text).
- **Files and edits:** suggest `vim` (not `nano`) when asking the user to edit a file. To send a file, link its absolute path in Markdown (`[name](/abs/path/file.pdf)`) instead of using attachment upload tools.

## Local pages

Serve locally generated pages at `http://<host>:<port>/<path>` bound to `<bind>` (`machine.md`), verify the URL responds, share the clickable URL, and keep the server running during review.

## Thread titles

Call `t3_thread_update` (`action: "regenerate_title"`) only when the topic clearly shifts and the title no longer fits, batched with another tool call—never as a standalone turn.

## Pointers

- **Steering files (`~/.agents`):** before editing `~/.agents` or running the `skills` CLI, read `~/.agents/README.md`. Commit and push every edit to `~/.agents` in the same task (`machine.md` is git-ignored and stays local).
- **Delegation:** before starting a subagent for a named role (`Build`, `Build-light`, `Hunt`, `Drive`, `Chore`), read `~/.agents/delegation.md` for its model, `T3 target`, brief format, and `Verify` checklist.
- **Reviews:** unless the repo sets its own review rule, consult `review-loop` ("Default triggers": sensitive areas, data, infra, public interfaces, or large behavior changes) before pushing or merging; note in one line if skipped near a trigger.
- **Frontend:** before any visible UI change, run `mockup-first` and wait for user approval.
