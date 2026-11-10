---
name: mockup-first
description: Show the user a mockup and get approval before any frontend change. Use before building a new page or screen, or changing UI layout, styling, interaction, or visuals.
---

# Mockup first

Every visible frontend change starts with a **mockup** the user approves. The real code stays untouched until they approve it. Logic-only frontend work with no visible change (data fetching, state bugs) skips this skill.

If you are a delegated agent and your brief says the mockup is already approved, skip to step 4.

## Steps

1. Build the mockup as one self-contained HTML file, choosing the form by the change:
   - **New page or screen**: the new page alone.
   - **Change to an existing UI**: a **before/after** page. Put the current UI on the left and the proposed version on the right at the same viewport width, and label each changed region. For "before", use a screenshot of the running app or a copy of the current markup.

   Make the design decisions with the `frontend-design` skill. Use realistic content and the project's real fonts, colors, and tokens. Show each state the change touches (hover, empty, error, mobile width) where it looks different. Embed images as data URIs so the file renders standalone.
2. Save it as `mockups/<slug>.html` in the project. Show it with the T3 tools `html_preview` then `html_render`. Outside T3 Code, serve it per the remote-access rule and give the URL.
3. Summarize the proposed change in 2–4 bullets, then end the turn and wait. This step is done only when the user explicitly approves. For each round of feedback, update the same file, show it again, and wait again.
4. Build from the approved mockup. It is the spec: match it exactly. When the work goes through a GitHub issue first, follow "Attaching to an issue" below. To delegate the build, follow "Delegating the build" below.
5. Screenshot the real UI in the same states and compare it with the mockup. Fix any drift before reporting.

## Attaching to an issue

When a GitHub issue carries the spec, the approved mockup travels with it as an issue artifact, because `mockups/` is local and often gitignored:

- Attach it: `gh issue artifact create <issue> mockups/<slug>.html#Mockup` (needs `gh` 2.103 or later). It becomes an HTML artifact that GitHub renders in a sandbox, so it must stay self-contained.
- In the issue body, name the `Mockup` artifact as the visual spec. A builder in any checkout fetches it with `gh issue artifact download`.
- After each later round of approved changes, update the same artifact with `gh issue artifact edit <issue> <artifact-number> --body-file mockups/<slug>.html`, so its version history records the design.
- If `gh issue artifact` fails (the feature is in public preview), add a screenshot to the issue body with `gh issue edit <issue> --attach <png>` and say so to the user.

## Delegating the build

Codex builds reliably but has weak visual taste, so the brief leaves Sol no visual choices:

- Give the mockup path (or the issue's `Mockup` artifact) as the spec, plus the target files and the existing components and tokens to reuse, by path.
- Spell out what a static mockup cannot show, as concrete values: motion (what moves, duration in ms, easing), and any state the mockup omits (sizes in px or tokens, colors as values or tokens).
- Include this verbatim: "The mockup at `<path>` is approved by the user; skip the mockup-first approval step and build it. Match it exactly. Where the mockup does not cover a case, choose the option closest to the existing UI and list it under Deviations in your report. Done when every state in the mockup is implemented and you return a screenshot of each state at desktop and mobile width, with paths."
- Check every returned screenshot against the mockup. Send each mismatch back as a new task with the exact correction.
