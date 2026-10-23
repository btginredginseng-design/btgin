#!/usr/bin/env python3
"""Build a beat map: every moment in the edit that deserves a visual response, and why.

A beat is a timed story event (a stat, a list item, a question, a turn, a section change,
a music hit). Each one gets an intensity (1 = caption emphasis only, 2 = graphic, 3 = big moment)
and a suggested treatment. Spacing rules then decide which beats actually get a graphic, so
motion graphics land where the story needs them instead of everywhere.

Inputs:
  transcript.edited.json   (from video-editing/plan_cuts.py; OUTPUT timeline)
  --script script.md       optional: '## Section' headings and **emphasis** marks from scripting stage
  --music music.wav        optional: tempo + beat grid so graphic in-points can hit the music

Outputs: beat_map.json, beat_map.md

Usage:
  beat_map.py work/transcript.edited.json -o work/ [--script script.md] [--music music/track.mp3] [--fps 30]
"""
import argparse
import difflib
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, "..", "defaults.json")))

NUM = re.compile(r"^[$€£]?\d[\d,.]*(%|x|k|m|b)?$|^(hundred|thousand|million|billion|half|double|triple)$", re.I)


def norm(w):
    return re.sub(r"[^\w%$']+", "", w.lower())


def fmt(t):
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:05.2f}"


def sentences(words, gap):
    out, cur = [], []
    for w in words:
        if cur and (w["start"] - cur[-1]["end"] > gap or cur[-1]["word"].rstrip()[-1:] in ".?!"):
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return out


def parse_script(path):
    """Return [(section_name, first_words)], and the set of **emphasized** words."""
    text = open(path).read()
    sections, emph = [], set()
    for m in re.finditer(r"\*\*(.+?)\*\*", text):
        emph.update(norm(w) for w in m.group(1).split())
    cur = None
    for line in text.splitlines():
        h = re.match(r"^#{2,3}\s+(.+)", line)
        if h:
            cur = h.group(1).strip()
            continue
        body = re.sub(r"\[.*?\]|\*\*|[*_>`-]", "", line).strip()
        if cur and body:
            sections.append((cur, [norm(w) for w in body.split()][:6]))
            cur = None
    return sections, emph


def align_sections(sections, sents):
    """Find where each script section starts in the spoken edit (fuzzy first-words match)."""
    out, start_idx = [], 0
    for name, first in sections:
        best, best_i = 0.0, None
        for i in range(start_idx, len(sents)):
            spoken = [norm(w["word"]) for w in sents[i]][:len(first)]
            r = difflib.SequenceMatcher(None, first, spoken).ratio()
            if r > best:
                best, best_i = r, i
        if best_i is not None and best >= 0.5:
            out.append((name, sents[best_i][0]["start"]))
            start_idx = best_i + 1
    return out


def music_grid(path):
    """Tempo + beat times via spectral-flux onsets and autocorrelation (numpy only)."""
    import numpy as np
    sr, hop, nfft = 22050, 512, 2048
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    if len(x) < nfft * 4:
        return None
    n = 1 + (len(x) - nfft) // hop
    idx = np.arange(nfft)[None, :] + hop * np.arange(n)[:, None]
    spec = np.abs(np.fft.rfft(x[idx] * np.hanning(nfft), axis=1))
    flux = np.maximum(0, np.diff(np.log1p(spec), axis=0)).sum(axis=1)
    flux = (flux - flux.mean()) / (flux.std() + 1e-9)
    fr = sr / hop
    ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
    lags = np.arange(len(ac))
    lo, hi = int(fr * 60 / 180), int(fr * 60 / 60)
    lag = lo + int(np.argmax(ac[lo:hi]))
    bpm = 60 * fr / lag
    phase = max(range(lag), key=lambda p: flux[p::lag].sum())
    beats = [(p + 1) / fr for p in range(phase, len(flux), lag)]
    # Strongest onsets (top 5%) are "hits": drops, snares worth landing a big graphic on.
    thr = np.percentile(flux, 95)
    hits = [(i + 1) / fr for i in range(1, len(flux) - 1)
            if flux[i] > thr and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1]]
    return {"bpm": round(float(bpm), 1), "beats": [round(b, 3) for b in beats],
            "downbeats": [round(b, 3) for b in beats[::4]], "hits": [round(h, 3) for h in hits]}


def detect_beats(words, sents, emph, section_starts, cfg):
    beats = []
    lists, turns = set(cfg["list_markers"]), set(cfg["turn_markers"])
    for si, s in enumerate(sents):
        text = " ".join(w["word"] for w in s).strip()
        n0 = norm(s[0]["word"])
        pause_before = s[0]["start"] - sents[si - 1][-1]["end"] if si else 0
        base = {"t": s[0]["start"], "end": s[-1]["end"], "text": text}
        if s[0]["start"] < cfg["hook_seconds"] and si == 0:
            beats.append({**base, "type": "hook", "intensity": 3, "why": "opening line: earns the next 30 seconds"})
        if n0 in lists or (n0 == "number" and len(s) > 1 and norm(s[1]["word"]) in {"one", "two", "three", "1", "2", "3"}):
            beats.append({**base, "type": "list", "intensity": 2, "why": f"list marker '{s[0]['word']}'"})
        elif n0 in turns:
            beats.append({**base, "type": "turn", "intensity": 1 + (pause_before > 0.4),
                          "why": f"story turns on '{s[0]['word']}'"})
        if text.endswith("?"):
            beats.append({**base, "type": "question", "intensity": 2, "why": "question opens a loop"})
        for w in s:
            nw = norm(w["word"])
            if NUM.match(nw) or NUM.match(w["word"].strip(".,!?")):
                beats.append({"t": w["start"], "end": w["end"], "text": text, "keyword": w["word"].strip(".,!?"),
                              "type": "stat", "intensity": 3 if "%" in w["word"] or "$" in w["word"] else 2,
                              "why": "concrete number: show it, don't just say it"})
            elif nw and nw in emph:
                beats.append({"t": w["start"], "end": w["end"], "text": text, "keyword": w["word"].strip(".,!?"),
                              "type": "emphasis", "intensity": 2, "why": "marked **emphasis** in script"})
        beats.append({**base, "type": "line", "intensity": 1, "why": "caption"})
    for name, t in section_starts:
        beats.append({"t": t, "end": t + 1.5, "text": name, "type": "section", "intensity": 2,
                      "why": f"script section '{name}' starts"})
    beats.sort(key=lambda b: (b["t"], -b["intensity"]))
    return beats


PRIORITY = ["stat", "hook", "list", "question", "emphasis", "section", "turn"]


def choose_graphics(beats, cfg, music):
    """Spacing rules: graphics need air, and a big moment is followed by visual rest.

    Strongest beats claim their slot first (intensity, then type priority), so a section
    title never steals the slot of the stat spoken a second later.
    """
    for b in beats:
        b["graphic"] = False
    cands = [b for b in beats if b["intensity"] >= cfg["graphic_min_intensity"] and b["type"] != "line"]
    cands.sort(key=lambda b: (-b["intensity"], PRIORITY.index(b["type"]) if b["type"] in PRIORITY else 99, b["t"]))
    chosen = []
    for b in cands:
        t = b["t"]
        near = [c for c in chosen if abs(c["t"] - t) < cfg["min_graphic_gap"]]
        resting = [c for c in chosen if c["intensity"] >= 3 and 0 < t - c["t"] < cfg["rest_after_big"]]
        dense = [c for c in chosen if abs(c["t"] - t) < 5]
        if near:
            b["skipped"] = f"within {cfg['min_graphic_gap']}s of {near[0]['type']} graphic"
        elif resting and b["intensity"] < 3:
            b["skipped"] = "visual rest after a big moment"
        elif len(dense) >= cfg["max_graphics_per_10s"]:
            b["skipped"] = f"density cap {cfg['max_graphics_per_10s']}/10s"
        else:
            b["graphic"] = True
            chosen.append(b)
            if music:
                m = min(music["beats"] + music["hits"], key=lambda x: abs(x - t), default=None)
                if m is not None and abs(m - t) <= cfg["music_snap"]:
                    b["music_sync"] = m
    return beats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("transcript")
    ap.add_argument("-o", "--outdir", required=True)
    ap.add_argument("--script")
    ap.add_argument("--music")
    ap.add_argument("--fps", type=float, default=30)
    a = ap.parse_args()

    tr = json.load(open(a.transcript))
    words = tr["words"]
    sents = sentences(words, CFG["sentence_gap"])
    emph, section_starts = set(), []
    if a.script:
        sections, emph = parse_script(a.script)
        section_starts = align_sections(sections, sents)
    music = music_grid(a.music) if a.music else None

    beats = choose_graphics(detect_beats(words, sents, emph, section_starts, CFG), CFG, music)
    lead = CFG["lead_frames"] / a.fps  # graphics land a hair before the word, never after
    for i, b in enumerate(beats):
        b["id"] = f"B{i + 1:02d}"
        b["treatment"] = CFG["treatments"].get(b["type"], "caption-only")
        b["in"] = round(max(0.0, b.get("music_sync", b["t"]) - lead), 3)
        b["t"], b["end"] = round(b["t"], 3), round(b["end"], 3)

    out = {"duration": tr.get("duration"), "fps": a.fps, "music": music,
           "sections": [{"name": n, "t": round(t, 3)} for n, t in section_starts], "beats": beats}
    os.makedirs(a.outdir, exist_ok=True)
    json.dump(out, open(os.path.join(a.outdir, "beat_map.json"), "w"), indent=1)

    g = [b for b in beats if b["graphic"]]
    lines = ["# Beat map", "",
             f"Duration {fmt(tr.get('duration') or 0)} · {len(beats)} beats · {len(g)} graphics"
             + (f" · music {music['bpm']} BPM" if music else ""), "",
             "| ID | In | Type | Int | Treatment | Graphic | Why / text |", "|---|---|---|---|---|---|---|"]
    for b in beats:
        if b["type"] == "line" and not b["graphic"]:
            continue
        mark = "**YES**" if b["graphic"] else ("skip: " + b.get("skipped", "low intensity"))
        txt = b.get("keyword") or b["text"][:50]
        lines.append(f"| {b['id']} | {fmt(b['in'])} | {b['type']} | {b['intensity']} | {b['treatment']} | {mark} | {b['why']} — “{txt}” |")
    open(os.path.join(a.outdir, "beat_map.md"), "w").write("\n".join(lines) + "\n")
    print(f"[beat_map] {len(beats)} beats, {len(g)} graphics -> {a.outdir}/beat_map.json")


if __name__ == "__main__":
    main()
