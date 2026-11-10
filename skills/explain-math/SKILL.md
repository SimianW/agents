---
name: explain-math
description: Explain a math concept visual-first, as a rendered HTML page with color-coded diagrams beside each formula.
disable-model-invocation: true
argument-hint: "Which concept, formula, or proof should I explain?"
---

# Explain math

Explain the concept **visual-first**: show the picture, then the formula that describes it. The deliverable is one HTML page published with `html_render`, followed by a short chat reply.

## Steps

1. **Pin down the target.** Name the concept, the question the user is actually stuck on, and what they already know, using the arguments and the conversation. Ask one question only when the target is genuinely unclear. Done when you can state, in one sentence, what the user should be able to see or do after reading.
2. **Plan the ideas.** Split the explanation into its central ideas, in the order they build on each other. For each, pick a diagram form (see [Diagrams](#diagrams)) and the key quantities it involves. Assign each key quantity one color (see [Color coding](#color-coding)). Done when every idea has a diagram form and every key quantity has a color.
3. **Build the page.** Write a self-contained HTML page following [Rendering](#rendering): each idea gets prose, its formula, and its diagram side by side, with a one-line caption. Draw plots from the actual equations. Done when every central idea from step 2 appears with its diagram.
4. **Check it.** Open the page with `html_preview` in both `light` and `dark`, and at a narrow width. Done when every key formula has a matching diagram, every colored symbol matches its diagram color, and all labels stay readable in every view. Fix and re-preview until all three hold.
5. **Publish.** Show the page with `html_render`. Keep the chat reply below it short: add only what the page doesn't say, such as a question that checks the user's understanding or offers the next step.

When `html_render` is not available, explain in chat instead: write math in LaTeX (`$…$` inline, `$$…$$` display), and describe each diagram in words beside its step.

## Diagrams

- Give each central idea its own diagram, placed beside the step it explains, with a one-line caption.
- Pick the form from the idea: function or inequality → plot; geometry or vectors → labeled figure; derivation → a strip of steps, one picture per step; comparison or limiting case → panels side by side; changing parameter → slider or step button.
- Draw plots from the actual equations, using inline SVG or JS.

## Color coding

- Give each key quantity one color and use it everywhere that quantity appears: formula (`\htmlClass{c-blue}{x}`), diagram, and the prose that names it.
- Palette (Okabe-Ito): `#0072B2` blue, `#E69F00` orange, `#009E73` green, `#D55E00` vermillion, `#CC79A7` purple. At most 5 at once; everything else uses the theme's foreground or muted colors.
- Pair every color with a label or legend.

## Rendering

- Follow the T3 Code theme in light and dark mode through its injected CSS variables: `--card` and `--border` for panels, `--foreground` and `--muted-foreground` for text and axes, `--code-background` for code. Mix each palette color with the foreground so it stays readable in both modes, e.g. `--c-blue: color-mix(in oklab, #0072B2 70%, var(--foreground))`. Color SVG strokes and fills with these variables too.
- Write math in LaTeX, rendered with KaTeX and its auto-render extension from `https://cdn.jsdelivr.net/npm/katex@0.16/dist/`. Use `\( … \)` for inline math and `$$ … $$` for display math.
- Color KaTeX with `\htmlClass{c-blue}{x}` and pass `trust: true`, because `\textcolor` accepts only literal colors.
- When the user's message gets an English tips block, it stays in the chat reply, below the page.
