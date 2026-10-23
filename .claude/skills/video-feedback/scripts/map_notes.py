#!/usr/bin/env python3
"""Map timestamped review notes onto what the pipeline actually did at that moment.

notes.md: one note per line, timestamps on the FINAL video:
  00:12 cut feels abrupt, she's mid-breath
  0:41-0:44 the stat card covers her face
  1:05 caption is late
  general: too many graphics in the intro

For each note this finds the nearest cut (source time, removal reason), the beats and graphics
on screen, and the transcript words, then guesses which stage owns the fix. Output notes.json is
what the video-feedback skill works from: fix this edit, then decide which notes are lessons.

Usage:
  map_notes.py notes.md --edl work/edl.json --render-meta work/edit.render.json \
     --beats work/beat_map.json --graphics out/final.graphics.json --transcript work/transcript.edited.json -o work/notes.json
"""
import argparse
import json
import re

TS = r"(?:(\d+):)?(\d{1,2}):(\d{2}(?:\.\d+)?)"
KEYWORDS = {
    "video-editing": ["cut", "jump", "breath", "pause", "silence", "retake", "um", "uh", "filler", "pacing", "slow", "fast", "audio", "sync", "loud", "quiet", "click", "abrupt"],
    "motion-graphics": ["graphic", "text", "title", "card", "counter", "animation", "font", "covers", "overlap", "position", "misaligned", "aligned", "off-center", "ease", "pop"],
    "video-design": ["too many", "busy", "cluttered", "generic", "boring", "color", "style", "brand", "consistent", "beat", "timing of graphics", "empty"],
    "video-scripting": ["hook", "story", "structure", "cta", "payoff", "script", "boring start", "re-shoot", "reshoot"],
    "video-review": ["missed", "qc", "should have caught"],
}


def secs(h, m, s):
    return int(h or 0) * 3600 + int(m) * 60 + float(s)


def out_to_src(t, render_meta):
    """Output time -> source time using the frame-snapped segments of the render."""
    if not render_meta:
        return None
    acc = 0.0
    for s, e in render_meta["segments"]:
        if t <= acc + (e - s):
            return round(s + (t - acc), 3)
        acc += e - s
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("notes")
    ap.add_argument("--edl")
    ap.add_argument("--render-meta")
    ap.add_argument("--beats")
    ap.add_argument("--graphics")
    ap.add_argument("--transcript")
    ap.add_argument("-o", "--output", required=True)
    a = ap.parse_args()
    load = lambda p: json.load(open(p)) if p else None
    edl, rm, bm, gm, tr = map(load, (a.edl, a.render_meta, a.beats, a.graphics, a.transcript))

    out = []
    for line in open(a.notes):
        line = line.strip().lstrip("-* ").strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(rf"^{TS}(?:\s*[-–]\s*{TS})?\s*[:\-–]?\s*(.*)$", line)
        note = {"raw": line}
        if m:
            t0 = secs(*m.group(1, 2, 3))
            t1 = secs(*m.group(4, 5, 6)) if m.group(5) else t0
            note.update(t=t0, t_end=t1, text=m.group(7))
        else:
            note.update(t=None, t_end=None, text=re.sub(r"^general\s*:\s*", "", line, flags=re.I))
        low = note["text"].lower()
        # Design keywords are judgements about the whole set ("too many", "generic"): weight them higher.
        scores = {st: sum(k in low for k in kws) * (2 if st == "video-design" else 1) for st, kws in KEYWORDS.items()}
        ctx = {}
        if note["t"] is not None:
            t0, t1 = note["t"] - 0.5, note["t_end"] + 0.5
            if rm:
                cuts = [c for c in rm.get("cut_points", []) if t0 - 0.5 <= c <= t1 + 0.5]
                ctx["cuts_near"] = cuts
                ctx["source_time"] = out_to_src(note["t"], rm)
                if cuts:
                    scores["video-editing"] += 1
            if edl and ctx.get("source_time") is not None:
                st = ctx["source_time"]
                ctx["removed_near"] = [r for r in edl["removed"] if abs(r["start"] - st) < 3 or abs(r["end"] - st) < 3]
            if gm:
                on = [g for g in gm["graphics"] if g["in"] <= t1 and g["in"] + g["duration"] >= t0]
                ctx["graphics_on_screen"] = [g["id"] for g in on]
                if on:
                    scores["motion-graphics"] += 1
            if bm:
                ctx["beats"] = [f"{b['id']} {b['type']}{' (graphic)' if b.get('graphic') else ''}"
                                for b in bm["beats"] if t0 <= b["t"] <= t1 and b["type"] != "line"]
            if tr:
                ctx["words"] = " ".join(w["word"] for w in tr["words"] if t0 <= w["start"] <= t1)
        note["context"] = ctx
        ranked = sorted(scores.items(), key=lambda kv: -kv[1])
        note["likely_stage"] = ranked[0][0] if ranked[0][1] > 0 else "unclear"
        out.append(note)
    json.dump(out, open(a.output, "w"), indent=1)
    for n in out:
        when = f"{n['t']:.2f}s" if n["t"] is not None else "general"
        print(f"[{n['likely_stage']}] {when}: {n['text']}  {json.dumps(n['context'])[:160]}")


if __name__ == "__main__":
    main()
