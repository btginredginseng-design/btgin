---
name: video-scripting
description: Research a niche's top-performing videos (outlier views, hooks, title patterns, pacing) and write a new video script from the patterns that win. Use when asked to script a video, find hooks, analyse competitors/a niche/a channel, or plan a video's structure before filming.
---

# Video scripting: research what wins, then write

Goal: a script whose hook, structure and length come from **evidence in the niche**, written in a
format the downstream stages can read (sections drive the beat map, `**bold**` marks graphic moments).

Before starting, read the **Learned rules** at the bottom of this file. They override everything above them.

## 1. Collect the niche sample

```bash
S=.claude/skills/video-scripting/scripts
python3 $S/niche_analyze.py fetch "ytsearch40:<niche query>" -d projects/<p>/research/raw
python3 $S/niche_analyze.py fetch "https://www.youtube.com/@<competitor>/videos" -d projects/<p>/research/raw --limit 60
```
- Pull 3–5 competitor channels plus 1–2 searches: 80–200 videos. Fewer than ~40 and the pattern stats are noise.
- No yt-dlp or no network access? Ask the user for a CSV (`id,title,views,duration,upload_date,channel,transcript`)
  from their analytics tool, or have them paste the transcripts of 10 videos they admire.

## 2. Analyse

```bash
python3 $S/niche_analyze.py analyze projects/<p>/research/raw -o projects/<p>/research --top 15
```
Read `research/niche_report.md`, then **read the actual hook transcripts of the top outliers yourself**.
The regex labels are a first pass. You do the real analysis. For each of the top 10, write down:

| Field | What to extract |
|---|---|
| Hook mechanism | What creates the curiosity gap in the first 1–3 seconds? (claim, result shown first, stakes, question, pattern-break) |
| Promise | What the viewer is told they'll get, and *when* that's said (seconds) |
| Proof | How the hook is made credible (number, demo, credential, visible result) |
| Structure | Chapters / sections and their order; where the payoff lands as % of runtime |
| Re-hooks | Lines that reopen curiosity mid-video ("but that's not the crazy part") |
| CTA | Where and how (mid-roll vs end, soft vs hard) |

Save the analysis to `research/patterns.md` and end it with **3 hook formulas specific to this niche**, each
written as a template (e.g. `"I [did costly/extreme thing] so you don't have to: here's the [n] that matter"`) citing
the outlier videos it came from. Patterns with positive lift in the report are candidates. Patterns the whole niche
already uses are table stakes, not differentiators. See `references/hook-patterns.md` for the general catalogue.

## 3. Write the script

Write `projects/<p>/script.md` using `references/script-template.md`. Non-negotiables:

- **Hook = first 5 seconds, ≤ 2 sentences, no greeting, no channel intro.** Write 3 hook variants from the 3
  formulas, pick one, and keep the others in a `<!-- alt hooks -->` comment.
- State the promise within 15 s. Deliver the first payoff before 30 % of runtime.
- A re-hook every 60–90 s for long-form, every ~15 s for shorts.
- Target length = the niche's top-outlier median from the report (±20 %). Words = minutes × the niche's median wpm
  (fallback 150 wpm long-form, 170 shorts).
- Mark the moments that deserve a visual with `**bold**` (numbers, the one key term per section). These become
  beats. Bold at most one phrase per ~10 s, because bolding everything means nothing stands out.
- Put production notes in brackets on their own line: `[B-ROLL: ...]`, `[GFX: ...]`, `[SFX: ...]`. Never inline in
  spoken text, since the editor matches the spoken words against the transcript.
- Write for the ear: short sentences, contractions, one idea per sentence, numbers as the speaker will say them.

## 4. Hand-off

Give the user: the chosen hook + 2 alternates, the script, estimated runtime, and one line per section on *why*
(which outlier pattern it borrows). The `## Section` headings and `**bold**` marks are read by
`video-design/scripts/beat_map.py --script`, so keep that format.

## Learned rules

Rules added from review notes by the video-feedback skill. They override the defaults above.

<!-- LEARNED-RULES:START -->
_None yet._
<!-- LEARNED-RULES:END -->
