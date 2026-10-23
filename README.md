# btgin

Claude Code skills for professional video editing: from niche research to a QC-checked final render,
with a feedback loop that makes the pipeline better after every project.

| Stage | Skill | What it does | Key tools |
|---|---|---|---|
| 1. Scripting | `video-scripting` | Finds outlier videos in a niche, extracts their hooks, title patterns and pacing, writes a script from what wins | `niche_analyze.py` (yt-dlp) |
| 2. Editing | `video-editing` | Transcribes with Whisper, detects retakes, false starts, fillers, stutters and dead air, cuts on a frame-accurate grid | `transcribe.py`, `plan_cuts.py`, `render_cuts.py` (FFmpeg) |
| 3. Design | `video-design` | Beat map of story moments (plus music beats) with spacing rules; per-project design system | `beat_map.py`, `design.md`, `tokens.css` |
| 4. Motion graphics | `motion-graphics` | Hyperframes-format HTML/GSAP compositions, one sub-agent per graphic, rendered with alpha and composited | `scaffold_graphics.py`, `render_html.mjs`, `composite.py` |
| 5. Review | `video-review` | Frame-by-frame QC: misaligned, clipped or unsafe graphics, A/V sync and drift, black, frozen or flash frames, loudness, clicks | `qc.py` + `video-qc-reviewer` agent |
| 6. Feedback | `video-feedback` | Maps timestamped notes to the cut, beat or graphic responsible, fixes them, and records lessons into skill rules and defaults | `map_notes.py`, `add_lesson.py` |

## Setup

- `ffmpeg`, Python 3 + `numpy` (+ `pillow` for QC contact sheets)
- Whisper: `pip install faster-whisper` (or `openai-whisper`, or whisper.cpp)
- Node 18+ with `playwright` (Chromium) for rendering graphics; optionally the Hyperframes CLI
  (`npx skills add heygen-com/hyperframes`), which is used automatically when installed
- `yt-dlp` for niche research

Verify with `bash .claude/skills/video-pipeline/scripts/smoke_test.sh`.

## Use

In Claude Code: *"Edit projects/launch/raw/a-roll.mp4 into a 6-minute video with motion graphics"*, or invoke a stage
directly (*"do niche research on home espresso"*, *"QC projects/launch/out/final.mp4"*, *"notes: 0:41 the card covers my face"*).
