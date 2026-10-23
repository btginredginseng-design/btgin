#!/usr/bin/env python3
"""Decide what to cut from raw footage: retakes, filler words, stutters and dead air.

Reads a word-level transcript (from transcribe.py) and writes an edit decision list.
Nothing is rendered here, so the plan can be reviewed and overridden before render_cuts.py.

Outputs:
  edl.json                  keep ranges (source time) + every removal with its reason
  transcript.edited.json    kept words re-timed onto the OUTPUT timeline (used by design/captions/QC)
  cuts_report.md            human-readable list of removals to sanity-check

Overrides (optional, from editor notes):  overrides.json
  {"force_keep": [[12.0, 15.5]], "force_cut": [[40.2, 41.0]]}   # source-time seconds

Usage:
  plan_cuts.py work/transcript.json raw/take1.mp4 -o work/ [--overrides notes/overrides.json]
               [--max-pause 0.3] [--no-snap]
"""
import argparse
import difflib
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULTS = json.load(open(os.path.join(HERE, "..", "defaults.json")))


def norm(w):
    return re.sub(r"[^\w']+", "", w.lower())


def fmt(t):
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:06.3f}"


def load_words(transcript):
    words = []
    for seg in transcript["segments"]:
        for w in seg.get("words", []):
            if w["end"] <= w["start"]:
                w["end"] = w["start"] + 0.05
            words.append({"start": float(w["start"]), "end": float(w["end"]),
                          "word": w["word"], "n": norm(w["word"]), "keep": True, "reason": None})
    words.sort(key=lambda w: w["start"])
    return words


def phrases_of(words, gap):
    out, cur = [], []
    for i, w in enumerate(words):
        if cur and (w["start"] - words[cur[-1]]["end"] > gap or words[cur[-1]]["word"].rstrip()[-1:] in ".?!"):
            out.append(cur)
            cur = []
        cur.append(i)
    if cur:
        out.append(cur)
    return out


def mark(words, idxs, reason):
    for i in idxs:
        if words[i]["keep"]:
            words[i]["keep"] = False
            words[i]["reason"] = reason


def detect_cues(words, phrases, cfg):
    """'scratch that' / 'let me start over' -> drop that phrase and the one before it."""
    for pi, ph in enumerate(phrases):
        text = " ".join(words[i]["n"] for i in ph)
        if any(re.search(r"\b" + re.escape(c) + r"\b", text) for c in cfg["cue_phrases"]):
            mark(words, ph, "retake cue")
            if pi > 0:
                mark(words, phrases[pi - 1], "retake (before cue)")


def detect_retakes(words, phrases, cfg):
    """A phrase that matches the start of a later phrase is an abandoned take: keep the last one."""
    for pi, ph in enumerate(phrases):
        a = [words[i]["n"] for i in ph if words[i]["n"] and words[i]["n"] not in cfg["fillers"]]
        if len(a) < 2:
            continue
        for pj in range(pi + 1, min(len(phrases), pi + 1 + cfg["retake_lookahead"])):
            later = phrases[pj]
            if words[later[0]]["start"] - words[ph[-1]]["end"] > cfg["retake_window"]:
                break
            b = [words[i]["n"] for i in later if words[i]["n"] and words[i]["n"] not in cfg["fillers"]]
            if len(b) < 2:
                continue
            # Compare against the same-length prefix of the later phrase: false starts are prefixes.
            ratio = difflib.SequenceMatcher(None, a, b[:len(a) + 1]).ratio()
            if ratio >= cfg["retake_similarity"] and b[:2] == a[:2]:
                mark(words, ph, f"retake (redone at {fmt(words[later[0]]['start'])}, sim {ratio:.2f})")
                break


def detect_fillers_and_stutters(words, cfg):
    fillers = set(cfg["fillers"])
    for i, w in enumerate(words):
        if w["n"] in fillers:
            mark(words, [i], "filler")
        elif cfg["drop_stutters"] and i + 1 < len(words) and w["n"] and w["n"] == words[i + 1]["n"] \
                and words[i + 1]["start"] - w["end"] < 0.5:
            mark(words, [i], "stutter")


def apply_overrides(words, ov):
    for s, e in ov.get("force_cut", []):
        for w in words:
            if w["start"] < e and w["end"] > s:
                w["keep"], w["reason"] = False, "manual cut"
    for s, e in ov.get("force_keep", []):
        for w in words:
            if w["start"] >= s - 0.01 and w["end"] <= e + 0.01:
                w["keep"], w["reason"] = True, None


def energy_envelope(media, hop=0.01):
    """RMS per 10 ms of the source audio, for snapping cut points to the quietest moment."""
    try:
        import numpy as np
    except ImportError:
        return None
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", media, "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    n = int(16000 * hop)
    frames = len(x) // n
    if frames == 0:
        return None
    return np.sqrt((x[:frames * n].reshape(frames, n) ** 2).mean(axis=1) + 1e-12), hop


def snap(t, env, window, lo, hi):
    """Move t to the quietest 10 ms frame within +/- window, staying inside [lo, hi]."""
    if env is None:
        return t
    rms, hop = env
    a = max(lo, t - window)
    b = min(hi, t + window)
    i0, i1 = int(a / hop), int(b / hop) + 1
    if i1 <= i0 or i0 >= len(rms):
        return t
    seg = rms[i0:min(i1, len(rms))]
    return (i0 + int(seg.argmin())) * hop + hop / 2


def probe_fps(media):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=avg_frame_rate", "-of", "csv=p=0", media],
                         capture_output=True, text=True).stdout.strip()
    try:
        num, den = out.split("/")
        return float(num) / float(den) if float(den) else None
    except ValueError:
        return None


def build_keeps(words, cfg, duration, env, fps=None):
    keeps = []
    n = len(words)
    for i, w in enumerate(words):
        if not w["keep"]:
            continue
        prev_end = words[i - 1]["end"] if i > 0 else 0.0
        next_start = words[i + 1]["start"] if i + 1 < n else duration
        s = max(w["start"] - cfg["pad_pre"], prev_end if i > 0 and not words[i - 1]["keep"] else 0.0)
        e = min(w["end"] + cfg["pad_post"], next_start if i + 1 < n and not words[i + 1]["keep"] else duration)
        keeps.append([s, e])
    merged = []
    # A gap shorter than max_pause stays as natural breathing room; longer gaps are trimmed.
    bridge = max(0.0, cfg["max_pause"] - cfg["pad_pre"] - cfg["pad_post"])
    for s, e in keeps:
        if merged and s - merged[-1][1] <= bridge:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    if env is not None and cfg["snap_window"] > 0:
        for k, (s, e) in enumerate(merged):
            lo = merged[k - 1][1] if k else 0.0
            hi = merged[k + 1][0] if k + 1 < len(merged) else duration
            merged[k] = [snap(s, env, cfg["snap_window"], lo, e), snap(e, env, cfg["snap_window"], s, hi)]
    if fps:  # same frame grid render_cuts.py uses, so edited timings match the render exactly
        merged = [[round(s * fps) / fps, round(e * fps) / fps] for s, e in merged]
    return [[round(s, 4), round(e, 4)] for s, e in merged if e - s >= cfg["min_keep"]]


def remap(words, keeps):
    """Map kept words from source time onto the output timeline."""
    out, k = [], 0
    starts = []
    acc = 0.0
    for s, e in keeps:
        starts.append(acc)
        acc += e - s
    for w in words:
        if not w["keep"]:
            continue
        mid = (w["start"] + w["end"]) / 2
        while k < len(keeps) and keeps[k][1] < mid:
            k += 1
        if k == len(keeps):
            break
        s, e = keeps[k]
        if mid < s:
            continue
        offset = starts[k] - s
        out.append({"start": round(max(w["start"], s) + offset, 3),
                    "end": round(min(w["end"], e) + offset, 3),
                    "word": w["word"], "src_start": w["start"]})
    return out, acc


def removal_spans(words):
    spans = []
    for w in words:
        if w["keep"]:
            continue
        if spans and spans[-1]["reason"] == w["reason"] and w["start"] - spans[-1]["end"] < 1.0:
            spans[-1]["end"] = w["end"]
            spans[-1]["text"] += " " + w["word"]
        else:
            spans.append({"start": w["start"], "end": w["end"], "reason": w["reason"], "text": w["word"]})
    return spans


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("transcript")
    ap.add_argument("media")
    ap.add_argument("-o", "--outdir", required=True)
    ap.add_argument("--overrides")
    ap.add_argument("--no-snap", action="store_true", help="skip energy-based cut snapping")
    for k in ("pad_pre", "pad_post", "max_pause", "phrase_gap", "retake_similarity"):
        ap.add_argument("--" + k.replace("_", "-"), type=float)
    a = ap.parse_args()

    cfg = dict(DEFAULTS)
    for k in ("pad_pre", "pad_post", "max_pause", "phrase_gap", "retake_similarity"):
        if getattr(a, k) is not None:
            cfg[k] = getattr(a, k)

    tr = json.load(open(a.transcript))
    duration = float(tr.get("duration") or 0)
    words = load_words(tr)
    if not duration:
        duration = words[-1]["end"] + 1 if words else 0
    phrases = phrases_of(words, cfg["phrase_gap"])

    detect_cues(words, phrases, cfg)
    detect_retakes(words, phrases, cfg)
    detect_fillers_and_stutters(words, cfg)
    if a.overrides and os.path.exists(a.overrides):
        apply_overrides(words, json.load(open(a.overrides)))

    env = None if a.no_snap else energy_envelope(a.media)
    keeps = build_keeps(words, cfg, duration, env, probe_fps(a.media))
    edited, out_dur = remap(words, keeps)
    removed = removal_spans(words)

    os.makedirs(a.outdir, exist_ok=True)
    edl = {"source": a.media, "source_duration": duration, "output_duration": round(out_dur, 3),
           "settings": {k: v for k, v in cfg.items() if not k.startswith("_")},
           "keep": [{"start": s, "end": e} for s, e in keeps], "removed": removed}
    json.dump(edl, open(os.path.join(a.outdir, "edl.json"), "w"), indent=1)
    json.dump({"source": a.media, "duration": round(out_dur, 3), "words": edited},
              open(os.path.join(a.outdir, "transcript.edited.json"), "w"), indent=1)

    lines = [f"# Cut plan for `{a.media}`", "",
             f"Source {fmt(duration)} → output {fmt(out_dur)} "
             f"({100 * (1 - out_dur / duration) if duration else 0:.0f}% removed, {len(keeps)} segments)", "",
             "| Source time | Reason | Text |", "|---|---|---|"]
    for r in removed:
        lines.append(f"| {fmt(r['start'])}–{fmt(r['end'])} | {r['reason']} | {r['text'][:80]} |")
    open(os.path.join(a.outdir, "cuts_report.md"), "w").write("\n".join(lines) + "\n")
    print(f"[plan_cuts] {len(keeps)} keep segments, {len(removed)} removals, "
          f"{fmt(duration)} -> {fmt(out_dur)}  ({a.outdir}/edl.json)")


if __name__ == "__main__":
    main()
