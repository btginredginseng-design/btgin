---
name: video-feedback
description: Apply the user's review notes to a video edit, then turn the notes that reveal a pattern into permanent rules (SKILL.md learned rules and defaults.json values) so the same mistake doesn't happen on future projects. Use whenever the user gives notes/feedback/changes on an edit, says something looks wrong, or asks the pipeline to "remember", "learn" or "stop doing" something.
---

# Video feedback: fix this edit, prevent the next one

Every note gets two answers: **a fix in this project** and **a decision about whether it's a lesson**.
A lesson changes the instructions or defaults the pipeline reads, so future projects start from it.

## 1. Capture the notes

Write the user's notes to `projects/<p>/notes/notes.md`, one per line, timestamps on the final video:
```
00:12 cut feels abrupt, she's mid-breath
0:41-0:44 the stat card covers her face
general: too many graphics in the intro
```
Then map each note to what the pipeline did at that moment:
```bash
F=.claude/skills/video-feedback/scripts
python3 $F/map_notes.py projects/<p>/notes/notes.md --edl projects/<p>/work/edl.json \
  --render-meta projects/<p>/work/edit.render.json --beats projects/<p>/work/beat_map.json \
  --graphics projects/<p>/out/final.graphics.json --transcript projects/<p>/work/transcript.edited.json \
  -o projects/<p>/notes/notes.json
```
For each note this gives the source time, nearby cuts and removals, graphics on screen, beats and words, and a
guessed owning stage. Confirm the owner yourself: look at the frame (`ffmpeg -ss`) before deciding.
If a note is ambiguous ("feels off"), ask one specific question rather than guessing.

## 2. Fix this project, at the stage that owns it

| Owner | How to fix (never patch the final render directly) |
|---|---|
| editing | `notes/overrides.json` force_keep/force_cut (source times from notes.json) or `--max-pause` etc. → plan_cuts → render_cuts |
| design | edit `work/beat_map.json` (graphic true/false, treatment) or `design/design.md` / `tokens.css` |
| motion-graphics | edit `graphics/<ID>/index.html` (or re-dispatch its sub-agent with the note) → re-render that graphic |
| scripting | rewrite in `script.md`. Usually needs a re-shoot, so tell the user rather than faking it in the edit |
| review | QC missed it: add/tighten a check (see step 3) |

Then re-run everything downstream of the earliest stage you touched → composite → **video-review**. Reply with what
changed per note.

## 3. Decide what becomes a lesson

Ask of each note: **"Would this mistake happen again on the next project?"**

- **Yes, a systematic cause** (a default, a template, a missing rule, a QC blind spot) → record a lesson.
- **Taste that's consistent for this user/channel** ("I like longer pauses") → record a lesson, scoped in the rule
  text ("For <channel>: …") if the user has several channels.
- **One-off** (this take was bad, this word was misheard) → fix only. Don't record it, because noise in the rules makes
  them worse.

Record it at the stage that *caused* it (not where it was noticed), with the reason. Use a number when the fix is a number:
```bash
python3 $F/add_lesson.py --stage video-editing --rule "Keep up to 0.45 s of pause before a punchline" \
   --why "user notes on demo-01: punchlines felt rushed at 0.35" --source demo-01 --set max_pause=0.45
python3 $F/add_lesson.py --stage motion-graphics \
   --rule "Never center with transform translate(-50%); use inset+flex or animate xPercent/yPercent" \
   --why "a tween overwrote the transform and pushed the headline 120 px off-center" --source demo-01/B01
python3 $F/add_lesson.py --stage video-review --rule "Check graphics against the speaker face zone" \
   --why "stat card covered the face at 0:41 and QC passed it" --source demo-01
python3 $F/add_lesson.py --list
```
`add_lesson.py` regenerates the **Learned rules** block of the target SKILL.md (every stage reads its block before
working), applies `--set` to that stage's `defaults.json` (old → new values logged), and appends to `lessons.jsonl`.

Beyond a rule, fix the root cause when it's in code you own: a broken template, a missing QC check, a
detector threshold. A lesson saying "remember to X" is weaker than a template that can't do the wrong thing, so
do both. A QC miss should become a QC check where possible.

## 4. Keep the rules healthy
- Before adding, `--list` the stage's lessons. If a new note contradicts an old lesson, ask the user which wins and
  `--retire` the loser (`--retire L004 --why "superseded by L009"`).
- More than ~15 active rules in a stage → consolidate related ones into the body of that SKILL.md and retire them.
- Tell the user, in one line each, which lessons were recorded, so they can veto any.

## Learned rules

Rules added from review notes by the video-feedback skill. They override the defaults above.

<!-- LEARNED-RULES:START -->
_None yet._
<!-- LEARNED-RULES:END -->
