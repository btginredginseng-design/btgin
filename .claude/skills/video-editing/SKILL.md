---
name: video-editing
description: Rough-cut raw talking footage automatically. Transcribe with Whisper (word timestamps), detect retakes, false starts, filler words, stutters and dead air, then cut with FFmpeg on a frame-accurate grid. Use when asked to edit raw footage, remove silences/ums/mistakes/retakes, make a rough cut or a jump-cut edit.
---

# Video editing: transcript-driven rough cut

Pipeline: **transcribe → plan cuts (reviewable) → render → verify**. Nothing is cut blindly: every removal
is listed with its reason in `cuts_report.md` before rendering.

Read the **Learned rules** at the bottom first. They override the defaults below.

## 0. Requirements
- `ffmpeg`/`ffprobe` on PATH, Python 3 + numpy.
- A Whisper backend: `pip install faster-whisper` (recommended), or `openai-whisper`, or whisper.cpp
  (`whisper-cli` + `--model-path model.bin`). Check with `python3 -c "import faster_whisper"`.
- Multiple takes/cameras: concatenate raw clips first (`ffmpeg -f concat`), or run per clip and edit each.

## 1. Transcribe

```bash
E=.claude/skills/video-editing/scripts
python3 $E/transcribe.py projects/<p>/raw/a-roll.mp4 -o projects/<p>/work/transcript.json --model medium --language en
```
- Use `large-v3` for final cuts with accents or jargon, and `small` for a quick proxy pass.
- It deliberately keeps disfluencies and doesn't condition on previous text, so retakes stay visible.
- Sanity check: open the transcript and skim 3 random segments against the footage. Whisper sometimes
  hallucinates text in long silences. Delete those words from `transcript.json` before planning.

## 2. Plan the cuts

```bash
python3 $E/plan_cuts.py projects/<p>/work/transcript.json projects/<p>/raw/a-roll.mp4 -o projects/<p>/work \
        [--overrides projects/<p>/notes/overrides.json]
```
What it removes (tunable in `defaults.json`):

| Detector | Rule |
|---|---|
| Retake cue | Phrase containing "scratch that", "let me start over", … → drop it **and the phrase before it** |
| Retake / false start | A phrase whose words match the start of one of the next 3 phrases (≥ `retake_similarity`) → keep only the **last** take |
| Filler | Standalone `um/uh/erm/…` (`fillers`) |
| Stutter | Immediately repeated word ("the the") → drop the first |
| Dead air | Pauses longer than `max_pause` are trimmed to it, while natural pauses stay |
| Snap | Each cut moves to the quietest 10 ms within ±`snap_window`, then onto the video frame grid |

**Review `work/cuts_report.md` yourself before rendering.** Look for:
- A "retake" that was actually deliberate repetition for emphasis ("never, never do this") → `force_keep`.
- A dropped phrase whose replacement take is *worse* (incomplete) → `force_keep` the earlier one and
  `force_cut` the later one.
- Content the speaker flagged verbally but that wasn't caught ("wait, no", "hold on") → `force_cut`.

Write those decisions to `notes/overrides.json` (`{"force_keep": [[s, e]], "force_cut": [[s, e]]}`, source seconds)
and re-run step 2. Never hand-edit `edl.json`, because overrides survive re-planning and hand edits don't.

Pacing: talking-head long-form: `max_pause` 0.30–0.40. Shorts/high-energy: 0.15–0.25. Tutorials where the viewer
follows along: 0.5+. Set per project with `--max-pause` and record a lesson if the user's taste differs from the default.

## 3. Render

```bash
python3 $E/render_cuts.py projects/<p>/work/edl.json -o projects/<p>/work/edit_preview.mp4 --preview   # fast proxy
python3 $E/render_cuts.py projects/<p>/work/edl.json -o projects/<p>/work/edit.mp4                       # master
```
Writes `edit.render.json` (frame-snapped segments + cut points) next to the output. QC and feedback use it.
Each audio segment gets an 8 ms fade, so cuts don't click.

## 4. Verify before handing off
```bash
python3 .claude/skills/video-review/scripts/qc.py projects/<p>/work/edit.mp4 \
   --transcript projects/<p>/work/transcript.edited.json --render-meta projects/<p>/work/edit.render.json -o projects/<p>/work/qc
```
Must pass with no `av-*`, `words-in-silence` or `flash-frame` errors. Then watch the first 30 s and 3 random
cut points of the preview yourself (extract frames/clips with ffmpeg), since QC can't judge whether a cut *feels* right.

## Outputs consumed downstream
- `work/transcript.edited.json`: words on the **output** timeline (beat map, captions, graphics timing, QC sync).
- `work/edit.mp4` + `work/edit.render.json`: base layer for motion graphics and QC.

## Learned rules

Rules added from review notes by the video-feedback skill. They override the defaults above.

<!-- LEARNED-RULES:START -->
_None yet._
<!-- LEARNED-RULES:END -->
