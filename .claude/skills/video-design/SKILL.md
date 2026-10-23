---
name: video-design
description: Plan motion graphics before building them. Generate a beat map (every story moment in the edit that deserves a visual, with intensity and reason, optionally synced to music) and a project design system (design.md + tokens.css) so graphics are intentional, consistent and not generic. Use after the rough cut and before any motion graphics, or when asked for a beat map, style guide, design guidelines or graphics plan.
---

# Video design: beat map + design system

Generic motion graphics come from two failures: graphics placed **where there's room** instead of **where the story
turns**, and styles chosen **per graphic** instead of **per video**. This stage fixes both before anything is built.

Read the **Learned rules** at the bottom first.

## 1. Beat map

```bash
D=.claude/skills/video-design/scripts
python3 $D/beat_map.py projects/<p>/work/transcript.edited.json -o projects/<p>/work \
        --script projects/<p>/script.md [--music projects/<p>/music/track.mp3] --fps 30
```
Detects beats from the edited transcript: `hook`, `stat` (numbers), `list`, `question`, `turn` ("but", "actually"),
`emphasis` (`**bold**` in the script), `section` (script `##` headings), plus music tempo/beats/hits.
Each beat gets intensity 1–3, a suggested treatment and a `why`. Spacing rules (`defaults.json`) decide which
get a graphic: strongest beats claim slots first, there's a minimum gap, a density cap, and visual rest after big moments.
Graphic in-points land `lead_frames` before the word (and on a music beat if one is within `music_snap`).

**Then edit the beat map as a director** (`work/beat_map.json`, set `"graphic": true/false`, change `treatment`):
- Does every graphic answer "what does the viewer need to *see* here that they can't from the speaker?" If not, cut it.
- Is the hook graphic the strongest of the video? Is the payoff the second strongest?
- Are there 20+ s stretches with nothing? Consider a `punch-in` (edit-level zoom) rather than another graphic.
- Check `beat_map.md` for skipped beats you'd rather have than a chosen one. Swap them.

## 2. Design system (once per channel/series, adjusted per video)

Write `projects/<p>/design/design.md` from `references/design-guidelines.md`, then generate
`projects/<p>/design/tokens.css` from it (copy `.claude/skills/motion-graphics/templates/tokens.css` and change values).
Every graphic reads only these tokens.

Derive it, don't invent it:
- **From the footage**: extract 6 frames (`ffmpeg -ss T -i edit.mp4 -frames:v 1 f.png`) and look at them. Pick the
  accent so it contrasts with the set, wardrobe and skin tones, and pick plate opacity for the busiest background.
- **From the content**: a calm explainer gets soft eases and longer holds. A high-energy short gets snappier eases and harder cuts.
- **From the channel**: reuse an existing design.md if the series has one. Consistency beats novelty.
- **From the niche research**: what do top outliers do visually? Do the same where it's convention (captions) and
  differ deliberately where it's not.

## 3. Hand-off checklist
- [ ] `work/beat_map.json` reviewed, every `graphic: true` beat has a reason you'd defend
- [ ] `design/design.md` + `design/tokens.css` written, accent tested against real frames
- [ ] Treatment for every graphic beat exists as a template in `motion-graphics/templates/` or is described in
      design.md precisely enough for a sub-agent to build it

## Learned rules

Rules added from review notes by the video-feedback skill. They override the defaults above.

<!-- LEARNED-RULES:START -->
_None yet._
<!-- LEARNED-RULES:END -->
