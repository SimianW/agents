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
   - **Change to an existing UI**: a **before/after** page. Put the current UI on the left and the proposed version on the right at the same viewport width, and label each changed region. Build "before" one of two ways: copy the current UI's real markup and CSS into the panel, or, when the app runs locally, take a Playwright screenshot of the running UI and embed it.

   Make the design decisions with the `frontend-design` skill. Use realistic content and the project's real fonts, colors, tokens, and icon set (icons come from that set, not emoji). Write the text in the product's default UI language, not the language of the chat; add a version in another language only where its layout differs. Show each state the change touches (hover, empty, error, mobile width) where it looks different. Give each panel a visible label and an `id`, so a brief can point at one panel. Embed images as data URIs so the file renders standalone.
2. Save it as `mockups/<slug>.html` in the project. This is the mockup's only source file; put any render or inline copies in scratch, outside the repo. If the file is small (under about 50 KB), show it with the T3 tools `html_preview` then `html_render`. Otherwise, or outside T3 Code, serve it per the "Local pages" rule and give the URL.
3. Summarize the proposed change in 2–4 bullets, then end the turn and wait. This step is done only when the user explicitly approves. For each round of feedback, update the same file, show it again, and wait again.
4. Build from the approved mockup. It is the spec: match it exactly. When the work goes through a GitHub issue first, follow "Attaching to an issue" below. To delegate the build, follow "Delegating the build" below.
5. Follow "Verify against the mockup" below before reporting.

## Attaching to an issue

When a GitHub issue carries the spec, the approved mockup travels with it as a GitHub issue artifact (not a claude.ai Artifact), because `mockups/` is local and often gitignored:

- Run `gh --version` first. `gh issue artifact` needs `gh` 2.103 or later; upgrade `gh` if it is older.
- Attach it: `gh issue artifact create <issue> mockups/<slug>.html#Mockup`. It becomes an HTML artifact that GitHub renders in a sandbox, so it must stay self-contained.
- In the issue body, name the `Mockup` artifact as the visual spec. A builder in any checkout fetches it with `gh issue artifact download`.
- After each later round of approved changes, update the same artifact with `gh issue artifact edit <issue> <artifact-number> --body-file mockups/<slug>.html`, so its version history records the design.
- If `gh issue artifact` fails (the feature is in public preview), add a screenshot to the issue body with `gh issue edit <issue> --attach <png>` and say so to the user.

## Delegating the build

Send the build to the builder your routing rules name for builds. The brief leaves the builder no visual choices:

- Give the mockup path (or the issue's `Mockup` artifact) as the spec, plus the target files and the existing components and tokens to reuse, by path. Point at panels by `id` when the task covers only part of the mockup.
- Spell out what a static mockup cannot show, as concrete values: motion (what moves, duration in ms, easing), and any state the mockup omits (sizes in px or tokens, colors as values or tokens).
- Include this verbatim: "The mockup at `<path>` is approved by the user; skip the mockup-first approval step and build it. Match it exactly. Where the mockup does not cover a case, choose the option closest to the existing UI and list it under Deviations in your report. Done when every panel in scope is implemented and you return one screenshot of the real UI per panel, in the same state, theme, and width, named by panel `id`, with paths."

## Verify against the mockup

This applies whether you built the change or a delegate did. Compare the real UI with the mockup panel by panel: same state, theme, and width. Done when every panel in scope has a matching screenshot of the real UI and every difference is either fixed or listed under Deviations with its reason. For a delegated build, check each returned screenshot yourself and send each mismatch back as a new task with the exact correction.
