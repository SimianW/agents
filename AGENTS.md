## Bold punctuation 

Bold whole words only. Never open or close `**` inside a word, especially next to an apostrophe or other punctuation, because the bold won't render. For example, write "**what's**", not "what**'s**".

Never put a bare URL directly next to `**`, `_`, `~`, or full-width punctuation such as `（`, `：`, `，`. GFM extends a bare URL until the next space, so it swallows the closing `**` and the bold breaks. Leave URLs unbolded and put a space after them, or wrap them as `<http://…>` or `[label](http://…)`. For example, write "**打开看：** http://<host>:5190 （…）", not "**打开看：http://<host>:5190**（…）".

## English coaching

The user is learning English. When their message has a spelling, word-choice, phrasing, or grammar mistake, start the reply with an **English tips** block, then answer normally. Write the block only when it has at least one concrete correction; every bullet shows a change.

Focus on mistakes other than capitalization. Ignore lowercase sentence beginnings, lowercase "i", and capitalization of names, languages, products, acronyms, or technical terms. When correcting another mistake, preserve the user's capitalization in the quoted correction. If capitalization is the only issue, skip the English tips block.

Write one bullet per mistake, most important first, at most three. Each bullet has three parts, in this order:

1. What the user wrote, in quotes. Bold only the words that the correction removes or replaces. If the mistake is only a missing word, nothing in the quote is bold.
2. An arrow (→) and the corrected version. Bold only the words that were added or replaced.
3. An en dash (–) and one short, plain sentence that says what changed and why.

A word that is the same in both versions is never bold, even when it sits between two changes. Compare the two versions word by word before writing the bullet. When only punctuation changes, bold the punctuation together with the word it touches, such as "on exam **2 ?**" → "on exam **2?**".

Do not start a bullet with a category label such as "grammar" or "syntax". The explanation names the actual problem instead. Quote only as much of the sentence as is needed to see the mistake. Use plain quotes, not code formatting, so the bold shows.

Example:

```markdown
- "does t3 code have feature" → "does t3 code have **a** feature" – A singular countable noun needs an article here.
- "**leanring**" → "**learning**" – the "r" comes before the "n".
- "which lesson does quiz **one** content up to?" → "which lesson does quiz **one's** content **go** up to?" – "one's" shows possession, and the sentence needs the verb "go".

---
```

End the block with a `---` line. Start every bullet with `- `, because lines without it get merged into one paragraph. Code, commands, and pasted content are outside the block's scope.

## File editing

When prompting the user to edit files, always use `vim` instead of `nano`.

## Remote access to local pages

When asking the user to open a locally generated page, preview, or app, serve it at `http://<host>:<port>/<path>` so they can access it remotely through Tailscale. `<host>` is this machine's Tailscale MagicDNS name, kept per machine in `~/.agents/machine.md`; when that file's content is not already in your context, read the file. `hostname` returns a different name. If the file is missing, ask the user for the name and save it there. Bind the server to the Tailscale interface or `0.0.0.0`, verify the URL responds, and keep the server running while the user reviews it. Include the full clickable URL in the reply.

@~/.agents/machine.md

## Sending files

When the user asks you to send a file, link it in your reply as Markdown with its absolute path, such as `[name](/abs/path/file.pdf)`; T3 Code opens these links in its panel. Do not use attachment upload tools for this.

## Math notation

Write every mathematical formula in LaTeX, including formulas in chat replies. Use `$...$` for inline math and `$$...$$` for display math. Do not substitute Unicode symbols or plain-text notation such as `Σ`, `P_{i,j}^{(n)}` outside math delimiters, or `x^2`, even when the output may be shown in a terminal.

## Steering files

`~/.agents` (this file, `skills/`, `claude/CLAUDE.md`) is a git checkout of `SimianW/agents`, shared by all of the user's machines. When you edit a file there, commit and push it in the same task. Before you run the skills CLI, read `~/.agents/README.md`.

## Frontend changes

Before any visible frontend change, use the `mockup-first` skill: show the user a mockup and wait for approval.
