---
name: motion-graphics
description: Build motion graphics as code (HTML/CSS + GSAP timelines in Hyperframes composition format), render them to transparent video and composite them onto the edit at their beat times. Fans out one Claude sub-agent per graphic. Use when asked for motion graphics, animated text, lower thirds, counters, titles, kinetic typography or Hyperframes compositions.
---

# Motion graphics: code → video elements

Every graphic is an HTML composition in **Hyperframes format** (HeyGen's open-source HTML-to-video framework):
a root element with `data-composition-id`, `data-width`, `data-height` and `data-duration`, and one **paused** GSAP
timeline registered at `window.__timelines[<id>]`. Because the renderer seeks that timeline frame by frame,
output is deterministic: the same HTML always gives the same frames.

Read the **Learned rules** at the bottom first.

Inputs: `work/beat_map.json` (graphic beats), `work/transcript.edited.json`, `design/design.md`, `design/tokens.css`.

## 1. Scaffold one composition per graphic beat

```bash
M=.claude/skills/motion-graphics/scripts
python3 $M/scaffold_graphics.py projects/<p>/work/beat_map.json projects/<p>/work/transcript.edited.json \
        -o projects/<p>/graphics --tokens projects/<p>/design/tokens.css
```
Creates `graphics/<BEAT_ID>/index.html` (template filled with text and word timings) and `graphic.json`
(in-point, duration, alignment, safe-area: read by composite and QC). Templates: `kinetic-headline`,
`number-counter`, `keyword-pop`, `list-card`, `section-title`. New treatments: copy the closest template.

## 2. Build/refine with sub-agents (parallel)

For each graphic, spawn a **`motion-graphic-builder`** sub-agent (`.claude/agents/motion-graphic-builder.md`),
all in one message so they run in parallel. Give each one only what it needs:

```
Graphic: projects/<p>/graphics/B09   (index.html + graphic.json already scaffolded)
Beat: {id, type, text, keyword, why, t, in}           ← paste the beat entry
Spoken words in window (output time): ...            ← from transcript.edited.json
Design system: projects/<p>/design/design.md
Task: refine index.html to match design.md for treatment "<treatment>", render it, self-check stills, report.
```
Do the work yourself instead of using sub-agents when there are ≤ 2 graphics or the user asked not to fan out.
After they return, **open one still from each graphic side by side** and check consistency across the set:
same treatment means same position, size and motion. Sub-agents can't see each other's work, so this check is yours.

## 3. Render

```bash
node $M/render_html.mjs projects/<p>/graphics/B09/index.html -o projects/<p>/graphics/B09/out.mov      # ProRes 4444 w/ alpha
node $M/render_html.mjs projects/<p>/graphics/B09/index.html --still 1.2 -o /tmp/b09.png             # one frame to inspect
```
Engine: uses `npx hyperframes render` when the Hyperframes CLI is installed (`npx skills add heygen-com/hyperframes`
adds its own authoring skill), otherwise headless Chromium via Playwright + FFmpeg. Templates load GSAP from a CDN,
and `templates/hf-timeline.js` provides a GSAP-compatible subset when the CDN is unreachable (offline/sandboxed renders),
so stick to the API it documents (to/from/fromTo/set, numeric props, standard eases) unless real GSAP is guaranteed.

## 4. Composite

```bash
python3 $M/composite.py projects/<p>/work/edit.mp4 projects/<p>/graphics -o projects/<p>/out/final.mp4
```
Overlays each `out.mov` at its `in` time (layer order from `graphic.json`) and writes `final.graphics.json` for QC.
Then run the **video-review** skill. Don't call a graphic done until QC passes.

## Authoring rules (all compositions)
- Root: `<div id="root" data-composition-id="ID" data-width="1920" data-height="1080" data-duration="D">`.
  Standalone files never use `<template>`. Render length = root `data-duration`, not the timeline length.
- One `gsap.timeline({paused: true})`, registered as `window.__timelines["ID"]` after it's fully built. No
  `setTimeout`, `requestAnimationFrame`, CSS `@keyframes`/transitions, `Math.random()` or `Date`: they break seeking.
- Transparent `html, body` background. Colors, fonts, sizes and durations come only from `tokens.css` variables.
- **Position with layout (inset/flex/grid), not with `transform: translate(-50%)`.** The timeline owns `transform`.
  If you must center with a transform, animate `xPercent: -50` / `yPercent: -50` in every tween.
- Text lands on the spoken word: times in the composition are relative to its `in`, which is the beat's word time
  minus the template lead (see `graphic.json`). Use `data-at` per word from the transcript, never estimates.
- Add `data-qc-align` / `data-qc-safe` on the main element. `graphic.json` `align` must match what you built.
- Layer z-order with CSS `z-index`. `data-track-index` is a timeline lane, not a z-order.

## Learned rules

Rules added from review notes by the video-feedback skill. They override the defaults above.

<!-- LEARNED-RULES:START -->
_None yet._
<!-- LEARNED-RULES:END -->
