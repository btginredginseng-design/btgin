---
name: video-review
description: Automated frame-by-frame quality check of an edited or final video. Catches misaligned/off-center/clipped/unsafe text and graphics, missing graphics, audio-video sync offset and drift, words landing in silence, black/frozen/flash frames, dead air, loudness and clipping, and clicks at cuts. Then does a visual review of flagged frames. Use before delivering any render, or when asked to QC/review/check a video.
---

# Video review: automated QC + visual pass

Two layers: **measurements** a script can make exactly (sync, positions, loudness), then **your eyes** on the
frames it flags plus a fixed sample. A render isn't delivered until both pass.

Read the **Learned rules** at the bottom first.

## 1. Run the automated QC

```bash
R=.claude/skills/video-review/scripts
python3 $R/qc.py projects/<p>/out/final.mp4 \
   --edit projects/<p>/work/edit.mp4 --graphics projects/<p>/out/final.graphics.json \
   --transcript projects/<p>/work/transcript.edited.json --render-meta projects/<p>/work/edit.render.json \
   -o projects/<p>/out/qc
```
Exit code 1 means there are errors. Outputs `qc_report.md`, `qc_report.json` and `flagged_frames.png` (red = graphic
bbox, green = title-safe, cyan = center line).

| Check | How it's measured | Typical cause → fix stage |
|---|---|---|
| `graphic-misaligned` | Overlay bbox (final vs edit pixel diff) on its most complete frame vs declared `align` | transform overwritten by a tween → motion-graphics |
| `graphic-clipped` / `graphic-unsafe` | bbox touches frame edge / crosses title-safe margins | text too long for the box → motion-graphics |
| `graphic-edge-inconsistent` | left/right-aligned graphics not on a shared margin | hard-coded positions → motion-graphics |
| `graphic-missing` | no pixel difference while the graphic should be on screen | render failed / wrong `in` → motion-graphics |
| `av-sync` / `av-drift` | cross-correlation of voice activity vs transcript word timings, globally and per 10 s window | off-grid cuts, VFR source, fps mismatch → editing |
| `words-in-silence` | transcript words whose span has no voice energy | stale transcript, bad remap → editing |
| `av-duration` / `av-start` | stream durations and start times | padded audio, encoder priming → editing |
| `flash-frame` / `black` / `freeze` | per-frame difference analysis, blackdetect, freezedetect | 1-frame segments, bad overlay → editing |
| `dead-air`, `loudness`, `true-peak`, `cut-click` | silencedetect, EBU R128, sample slope at cut points | → editing (normalize with `loudnorm`) |

Variable-frame-rate phone footage is the #1 cause of drift. If `av-drift` fires, check with `ffprobe` (r_frame_rate ≠
avg_frame_rate), transcode the source to constant fps (`-vsync cfr -r 30`) and redo editing.

## 2. Visual pass (yours, not the script's)

QC can't judge taste, meaning or anything it wasn't told to measure. Spawn the **`video-qc-reviewer`** sub-agent
(`.claude/agents/video-qc-reviewer.md`), or do it yourself on short videos, to look at:
- every frame in `flagged_frames.png`, to confirm or dismiss each finding (false positives: graphics over moving footage)
- a still from the **middle of every graphic** and **±3 frames around every cut in the first 30 s**
- the hook (first 5 s) at 5 fps, frame by frame

and check for: text over the face/speaker zone, wrong words or typos in graphics (compare to transcript), a graphic
that contradicts what's said, jump cuts that land mid-gesture or mid-blink, inconsistent style between graphics.

## 3. Act on findings
- Each finding names its `fix_stage`. Fix it there (never patch the final render), re-render, re-run QC.
- Loop until QC passes and the visual pass has no errors. Report warnings you chose to accept, with the reason.
- **If the user later reports an error QC missed**, that's a QC bug: use the video-feedback skill to add a
  check or tighten a threshold in `defaults.json`, so it's caught automatically next time.

## Learned rules

Rules added from review notes by the video-feedback skill. They override the defaults above.

<!-- LEARNED-RULES:START -->
_None yet._
<!-- LEARNED-RULES:END -->
