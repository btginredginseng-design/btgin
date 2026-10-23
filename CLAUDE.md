# btgin: video production pipeline

This repo is a set of Claude Code skills for editing videos professionally, end to end.
Start with `.claude/skills/video-pipeline/SKILL.md`. It routes to the six stage skills:

1. `video-scripting`: niche research (outlier videos, hooks, title patterns) → script
2. `video-editing`: Whisper transcript → retake/filler/silence cuts → FFmpeg render
3. `video-design`: beat map + design system (design.md, tokens.css)
4. `motion-graphics`: Hyperframes HTML compositions built by sub-agents → rendered → composited
5. `video-review`: automated frame-by-frame QC (alignment, safe area, sync, loudness, glitches) + visual pass
6. `video-feedback`: apply notes, then record lessons into each stage's Learned rules / defaults.json

Conventions:
- One folder per video under `projects/<name>/` (layout in video-pipeline/SKILL.md). Media is git-ignored.
- Before working in a stage, read that stage's SKILL.md including its **Learned rules** block. Never edit the
  block by hand; use `video-feedback/scripts/add_lesson.py`.
- Fix problems at the stage that caused them and re-run downstream; never patch a final render.
- Tooling check: `bash .claude/skills/video-pipeline/scripts/smoke_test.sh`
