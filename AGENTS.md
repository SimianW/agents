## This machine

`~/.agents/machine.md` is part of these instructions and carries the same weight as this file. It holds what is true on this one machine:

- which machine this is and who the user is;
- how the user reaches it, and which other machines it can reach and how;
- its tools and paths;
- the values that other sections write in angle brackets, such as `<host>`;
- rules that apply only here.

Its content is free-form and differs from machine to machine.

- **Read it first.** When its content is not already in your context, read the whole file before your first action.
- **Let it override.** Where it is more specific than this file, follow it.
- **Keep it current.**
  - When a rule needs a value the file lacks, ask the user for the value, then save it.
  - When the user tells you a lasting fact about this machine, confirm it belongs to this machine, then save it.
  - Save each entry under a fitting heading; `~/.agents/machine.example.md` suggests some.
  - For a secret, save where it is stored, **never its value**.

@~/.agents/machine.md

## Bold punctuation

- **Bold whole words only.** Never open or close `**` inside a word, especially next to an apostrophe or other punctuation, because the bold won't render.
- **Keep bare URLs away from markup.** Never put a bare URL directly next to `**`, `_`, `~`, or full-width punctuation such as `（`, `：`, `，`. GFM extends a bare URL until the next space, so it swallows the closing `**` and the bold breaks. Leave the URL unbolded and put a space after it, or wrap it as `<http://…>` or `[label](http://…)`.

| Case | Write | Not |
|---|---|---|
| Word | `**what's**` | `what**'s**` |
| URL | `**Open：** http://<host>:5190 （…）` | `**Open：http://<host>:5190**（…）` |

## English coaching

The user is learning English. When their message has a spelling, word-choice, phrasing, or grammar mistake, start the reply with an **English tips** block, then answer normally.

**Scope**

- Write the block only when it has at least one concrete correction; every bullet shows a change.
- Leave capitalization alone: lowercase sentence beginnings, lowercase "i", and the capitalization of names, languages, products, acronyms, or technical terms. If capitalization is the only issue, skip the block. When correcting another mistake, preserve the user's capitalization in the quoted correction.
- Code, commands, and pasted content are outside the block's scope.

**Layout**

- One bullet per mistake, most important first, at most three.
- Start every bullet with `- `, because lines without it get merged into one paragraph.
- After `- ` comes the quote, never a category label such as "grammar" or "syntax"; the explanation names the actual problem instead.
- End the block with a `---` line.

Each bullet has three parts, in this order:

| # | Part | Bold only |
|---|---|---|
| 1 | What the user wrote, in quotes. Quote only as much of the sentence as is needed to see the mistake. | The words that the correction removes or replaces. If the mistake is only a missing word, nothing in the quote is bold. |
| 2 | An arrow (→) and the corrected version. | The words that were added or replaced. |
| 3 | An en dash (–) and one short, plain sentence that says what changed and why. | n/a |

**Bolding**

- A word that is the same in both versions is never bold, even when it sits between two changes. Compare the two versions word by word before writing the bullet.
- When only punctuation changes, bold the punctuation together with the word it touches, such as "on exam **2 ?**" → "on exam **2?**".
- Use plain quotes, not code formatting, so the bold shows.

Example:

```markdown
- "does t3 code have feature" → "does t3 code have **a** feature" – A singular countable noun needs an article here.
- "**leanring**" → "**learning**" – the "r" comes before the "n".
- "which lesson does quiz **one** content up to?" → "which lesson does quiz **one's** content **go** up to?" – "one's" shows possession, and the sentence needs the verb "go".

---
```

## File editing

When you ask the user to edit a file themselves, give the command with `vim`, not `nano`.

## Local pages

When asking the user to open a locally generated page, preview, or app:

1. **Serve** it at `http://<host>:<port>/<path>` and bind the server to `<bind>`; `machine.md` sets `<host>` and `<bind>`.
2. **Verify** that the URL responds.
3. **Link** the full clickable URL in the reply.
4. **Keep** the server running while the user reviews it.

## Sending files

When the user asks you to send a file, put a Markdown link to its absolute path in your reply, such as `[name](/abs/path/file.pdf)`; T3 Code opens these links in its panel. Do not use attachment upload tools for this.

## Math notation

Write every mathematical formula in LaTeX, including formulas in chat replies, and even when the output may be shown in a terminal. Use `$...$` for inline math and `$$...$$` for display math.

Unicode symbols and plain-text notation are not substitutes:

| Write | Not | Problem |
|---|---|---|
| `$\sum$` | `Σ` | Unicode symbol |
| `$P_{i,j}^{(n)}$` | `P_{i,j}^{(n)}` | LaTeX outside math delimiters |
| `$x^2$` | `x^2` | plain-text notation |

## Steering files

`~/.agents` (this file, `skills/`, `claude/CLAUDE.md`) is a git checkout of `SimianW/agents`, shared by all of the user's machines.

- **Commit and push** every edit you make there, in the same task.
- **Exception:** `machine.md` is the one file git ignores, so it stays on this machine.
- **Skills CLI:** read `~/.agents/README.md` before you run it.

## Reviews

When the repo's AGENTS.md or CLAUDE.md sets a review rule, follow it instead of this section.

Otherwise, run the `review-loop` skill before you push or merge a change that meets any of these triggers:

| Trigger | The change |
|---|---|
| **Sensitive areas** | touches auth, sessions, secrets, permissions, payments, or the privacy of user data |
| **Data** | adds or edits a database migration or schema, or deletes data |
| **Infrastructure** | changes deploy, CI, Docker/compose, hooks, cron/launchd/systemd, or sync and install scripts |
| **Interfaces** | changes a public API, CLI or config format that other code or machines depend on |
| **Size** | changes more than ~300 lines of behavior code (not counting generated, vendored, moved or imported files, prose, or throwaway prototypes) |

For anything else, your own verification is enough. If you skip review on a change close to one of these triggers, say so in one line of your report.

## Frontend changes

Before any visible frontend change, use the `mockup-first` skill: show the user a mockup and **wait for approval**.

## Thread titles

In T3 Code, after every user message, call `t3_thread_update` with `action: "regenerate_title"` on the current thread, so the title tracks the conversation. Make the call in your first batch of tool calls, alongside any independent calls, so it adds no extra round trip and the title updates while you work; never leave it until after your final reply. T3 Code writes the title with the user's title model and instructions.
