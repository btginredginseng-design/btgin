---
name: video-pipeline
description: End-to-end professional video production. Orchestrates the six stages (scripting from niche research, Whisper+FFmpeg rough cut, beat map and design system, code-built motion graphics with sub-agents, automated frame-by-frame QC, and feedback that updates the pipeline's own rules). Use when asked to make, produce or edit a whole video, or when unsure which video skill applies.
---

# Video pipeline

| # | Stage | Skill | Main output |
|---|---|---|---|
| 1 | Scripting | `video-scripting` | `research/niche_report.md`, `script.md` |
| 2 | Editing | `video-editing` | `work/edit.mp4`, `work/transcript.edited.json` |
| 3 | Design | `video-design` | `work/beat_map.json`, `design/design.md`, `design/tokens.css` |
| 4 | Motion graphics | `motion-graphics` | `graphics/<ID>/out.mov`, `out/final.mp4` |
| 5 | Review | `video-review` | `out/qc/qc_report.md` |
| 6 | Feedback | `video-feedback` | fixes + `Learned rules` / `defaults.json` updates |

Start wherever the user's material starts: raw footage only → stage 2. A finished edit → stages 3–5.
Notes on an edit → stage 6. Load each stage's SKILL.md when you reach it, because each has its own learned rules.

## Project layout

```
projects/<name>/
  brief.md                 goal, audience, platform, length, references
  research/                niche data + niche_report.md + patterns.md
  script.md
  raw/                     source footage (never modified)
  music/
  work/                    transcript.json, edl.json, cuts_report.md, transcript.edited.json,
                           edit.mp4, edit.render.json, beat_map.json/.md
  design/                  design.md, tokens.css
  graphics/<BEAT_ID>/      index.html, graphic.json, out.mov
  out/                     final.mp4, final.graphics.json, qc/
  notes/                   notes.md, notes.json, overrides.json
```
Big media (`raw/`, `music/`, `*.mp4`, `*.mov`) is git-ignored. Commit the text artifacts, since they're the edit's source of truth.

## Full run

```bash
P=projects/<name>; S=.claude/skills
# 2 edit
python3 $S/video-editing/scripts/transcribe.py $P/raw/a-roll.mp4 -o $P/work/transcript.json
python3 $S/video-editing/scripts/plan_cuts.py $P/work/transcript.json $P/raw/a-roll.mp4 -o $P/work --overrides $P/notes/overrides.json
#   → review work/cuts_report.md
python3 $S/video-editing/scripts/render_cuts.py $P/work/edl.json -o $P/work/edit.mp4
# 3 design
python3 $S/video-design/scripts/beat_map.py $P/work/transcript.edited.json -o $P/work --script $P/script.md [--music $P/music/x.mp3]
#   → review beat_map, write design/design.md + tokens.css
# 4 graphics
python3 $S/motion-graphics/scripts/scaffold_graphics.py $P/work/beat_map.json $P/work/transcript.edited.json -o $P/graphics --tokens $P/design/tokens.css
#   → motion-graphic-builder sub-agents in parallel (render + self-check each)
python3 $S/motion-graphics/scripts/composite.py $P/work/edit.mp4 $P/graphics -o $P/out/final.mp4
# 5 review
python3 $S/video-review/scripts/qc.py $P/out/final.mp4 --edit $P/work/edit.mp4 --graphics $P/out/final.graphics.json \
   --transcript $P/work/transcript.edited.json --render-meta $P/work/edit.render.json -o $P/out/qc
```

## Checkpoints with the user
Stop and show the user (with a frame or short clip, not just text) at:
1. **After the script**: hook choice and structure. Re-shooting is the most expensive fix.
2. **After the rough cut**: `cuts_report.md` summary + preview render. Pacing is a taste call.
3. **After the beat map + design.md**: the graphics plan, before the sub-agents spend effort building it.
4. **Final**: QC report + final render.
Skip a checkpoint only when the user says to run straight through.

## Principles
- Every stage writes reviewable text (EDL, beat map, design.md) **before** rendering. Change the text, never the pixels.
- Timing flows from words: transcript → EDL → edited transcript → beats → graphics → QC. Never estimate a time
  that can be looked up.
- Fix at the stage that caused the problem, re-run downstream, re-QC.
- Every note is a chance to improve the pipeline: run `video-feedback`.

## Learned rules

Rules added from review notes by the video-feedback skill. They override the defaults above.

<!-- LEARNED-RULES:START -->
_None yet._
<!-- LEARNED-RULES:END -->
