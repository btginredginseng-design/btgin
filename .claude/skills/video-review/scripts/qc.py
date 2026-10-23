#!/usr/bin/env python3
"""Automated quality check of a rendered video: frame-by-frame, audio and sync.

Checks (each finding has a timestamp, a severity, and the stage that should fix it):
  container    A/V stream durations differ, audio starts late/early, wrong duration vs render meta
  graphics     per overlay: not visible, outside title-safe, clipped at frame edge, off-center,
               left/right edges inconsistent between graphics (needs final.graphics.json + the pre-graphics edit)
  frames       black frames, frozen video, single-frame flashes / glitches
  audio        dead air, loudness off target, true-peak clipping, clicks at cut points
  sync         speech in the audio vs word timings in transcript.edited.json: global offset,
               drift across the video, words that land in silence

Usage:
  qc.py out/final.mp4 [--edit work/edit.mp4] [--graphics out/final.graphics.json]
        [--transcript work/transcript.edited.json] [--render-meta work/edit.render.json] -o out/qc/
Exit code 1 when any error-level finding exists, so it can gate a render loop.
"""
import argparse
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, "..", "defaults.json")))
findings = []


def add(sev, check, t, msg, stage, **extra):
    findings.append({"severity": sev, "check": check, "t": None if t is None else round(t, 3),
                     "message": msg, "fix_stage": stage, **extra})


def fmt(t):
    if t is None:
        return "—"
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:06.3f}"


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def ff_filter_log(path, vf=None, af=None):
    cmd = ["ffmpeg", "-v", "info", "-nostats", "-i", path]
    if vf:
        cmd += ["-vf", vf, "-an"]
    if af:
        cmd += ["-af", af, "-vn"]
    cmd += ["-f", "null", "-"]
    return subprocess.run(cmd, capture_output=True, text=True).stderr


def frame_at(path, t, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.4f}", "-i", path, "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-"],
                         capture_output=True).stdout
    if len(raw) < w * h * 3:
        return None
    return np.frombuffer(raw[:w * h * 3], dtype=np.uint8).reshape(h, w, 3)


def audio_pcm(path, sr):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


# ---------------------------------------------------------------- container

def check_container(path, info, render_meta):
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if not v:
        add("error", "container", None, "no video stream", "editing")
        return None
    n, d = v["avg_frame_rate"].split("/")
    fps = float(n) / float(d) if float(d) else 30.0
    frame = 1 / fps
    if a:
        vd, ad = float(v.get("duration", 0)), float(a.get("duration", 0))
        tol = CFG["av_duration_tolerance_frames"] * frame + 0.025
        if vd and ad and abs(vd - ad) > tol:
            add("error", "av-duration", min(vd, ad), f"video {vd:.3f}s vs audio {ad:.3f}s "
                f"({(ad - vd) * 1000:+.0f} ms): segments were cut off-grid or a stream was padded", "editing")
        vs, as_ = float(v.get("start_time", 0)), float(a.get("start_time", 0))
        if abs(vs - as_) > frame / 2:
            add("error", "av-start", 0, f"audio starts {(as_ - vs) * 1000:+.0f} ms relative to video", "editing")
    else:
        add("warn", "container", None, "no audio stream", "editing")
    if render_meta:
        exp = render_meta.get("expected_duration")
        dur = float(info["format"]["duration"])
        if exp and abs(dur - exp) > 2 * frame:
            add("error", "duration", dur, f"duration {dur:.3f}s, EDL expects {exp:.3f}s", "editing")
    return {"fps": fps, "width": v["width"], "height": v["height"], "duration": float(info["format"]["duration"])}


# ---------------------------------------------------------------- frames

def check_frames(path, meta):
    log = ff_filter_log(path, vf=f"blackdetect=d={CFG['black_min_s']}:pix_th=0.10")
    for m in re.finditer(r"black_start:([\d.]+) black_end:([\d.]+)", log):
        s, e = float(m.group(1)), float(m.group(2))
        add("error" if s > 0.05 else "warn", "black", s, f"black frames {fmt(s)}–{fmt(e)}", "editing")
    log = ff_filter_log(path, vf=f"freezedetect=n=0.002:d={CFG['freeze_min_s']}")
    for m in re.finditer(r"freeze_start: ([\d.]+)", log):
        add("warn", "freeze", float(m.group(1)), "video frozen (identical frames) — dropped frames or a stuck render", "editing")

    # Single-frame flashes: frame differs from both neighbours, while neighbours match each other.
    w, h = 96, 54
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-an", "-f", "rawvideo", "-pix_fmt", "gray",
                          "-s", f"{w}x{h}", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw[:len(raw) // (w * h) * w * h], dtype=np.uint8).reshape(-1, h, w).astype(np.int16)
    if len(fr) > 2:
        d_prev = np.abs(fr[1:-1] - fr[:-2]).mean(axis=(1, 2))
        d_next = np.abs(fr[1:-1] - fr[2:]).mean(axis=(1, 2))
        d_skip = np.abs(fr[2:] - fr[:-2]).mean(axis=(1, 2))
        T = CFG["flash_threshold"]
        for i in np.where((d_prev > T) & (d_next > T) & (d_skip < T / 3))[0]:
            add("error", "flash-frame", (i + 1) / meta["fps"], f"single-frame glitch (frame {i + 1})", "editing")


# ---------------------------------------------------------------- graphics

def graphic_bbox(final, edit, t, W, H):
    a, b = frame_at(final, t, W, H), frame_at(edit, t, W, H)
    if a is None or b is None:
        return None
    mask = (np.abs(a.astype(np.int16) - b.astype(np.int16)).max(axis=2) > CFG["graphic_diff_threshold"])
    # Ignore compression speckle: a real graphic row/column has a run of changed pixels.
    rows = np.where(mask.sum(axis=1) > max(3, W * 0.004))[0]
    cols = np.where(mask.sum(axis=0) > max(3, H * 0.004))[0]
    if len(rows) == 0 or len(cols) == 0:
        return {"empty": True}
    return {"empty": False, "x0": int(cols[0]), "x1": int(cols[-1]), "y0": int(rows[0]), "y1": int(rows[-1])}


def check_graphics(final, edit, gmeta, meta, outdir):
    W, H = meta["width"], meta["height"]
    sx, sy = CFG["safe_margin_x"] * W, CFG["safe_margin_y"] * H
    edges = {"left": [], "right": []}
    shots = []
    for g in gmeta["graphics"]:
        t0, d = g["in"], g["duration"]
        n = max(1, CFG["graphic_samples"])
        # Sample the settled part of the graphic: after the in-animation, before the out-animation.
        times = [t0 + 0.45 + (d - 0.8) * k / max(1, n - 1) for k in range(n)] if d > 1 else [t0 + d / 2]
        boxes = []
        for t in times:
            bb = graphic_bbox(final, edit, t, W, H)
            if bb is None:
                continue
            if bb["empty"]:
                add("error", "graphic-missing", t, f"{g['id']} ({g.get('treatment')}) not visible", "motion-graphics", graphic=g["id"])
                continue
            boxes.append((t, bb))
        # Alignment is judged on the most complete frame (largest box): a word-by-word reveal is
        # legitimately lopsided mid-build. Safe-area and clipping are checked on every sample.
        full = max(boxes, key=lambda tb: (tb[1]["x1"] - tb[1]["x0"]) * (tb[1]["y1"] - tb[1]["y0"]), default=None)
        for t, bb in boxes:
            cx = (bb["x0"] + bb["x1"]) / 2
            msgs = []
            if bb["x0"] <= 1 or bb["y0"] <= 1 or bb["x1"] >= W - 2 or bb["y1"] >= H - 2:
                msgs.append(("error", "graphic-clipped", "touches the frame edge (clipped)"))
            elif g.get("safe") and (bb["x0"] < sx or bb["x1"] > W - sx or bb["y0"] < sy or bb["y1"] > H - sy):
                msgs.append(("error", "graphic-unsafe", "outside title-safe area"))
            if g.get("align") == "center" and (t, bb) is full and abs(cx - W / 2) > CFG["center_tolerance"] * W:
                msgs.append(("error", "graphic-misaligned", f"off-center by {cx - W / 2:+.0f}px (declared center)"))
            for sev, check, m in msgs:
                add(sev, check, t, f"{g['id']} ({g.get('treatment')}): {m}", "motion-graphics", graphic=g["id"], bbox=bb)
                shots.append((t, bb, f"{g['id']} {check}"))
        if full and g.get("align") in edges:
            t, bb = full
            edges[g["align"]].append((g["id"], bb["x0"] if g["align"] == "left" else W - bb["x1"], t))
    for side, vals in edges.items():
        if len(vals) > 1:
            ref = float(np.median([v for _, v, _ in vals]))
            for gid, v, t in vals:
                if abs(v - ref) > CFG["edge_alignment_tolerance"] * W:
                    add("warn", "graphic-edge-inconsistent", t, f"{gid}: {side} edge at {v:.0f}px, other {side}-aligned "
                        f"graphics at {ref:.0f}px — not on the shared margin", "motion-graphics", graphic=gid)
    contact_sheet(final, shots, W, H, os.path.join(outdir, "flagged_frames.png"))


def contact_sheet(path, shots, W, H, out):
    if not shots:
        return
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return
    tw, th = 480, int(480 * H / W)
    sheet = Image.new("RGB", (tw * min(3, len(shots)), th * ((len(shots) + 2) // 3)), "black")
    for i, (t, bb, label) in enumerate(shots[:30]):
        f = frame_at(path, t, W, H)
        if f is None:
            continue
        im = Image.fromarray(f)
        d = ImageDraw.Draw(im)
        d.rectangle([bb["x0"], bb["y0"], bb["x1"], bb["y1"]], outline=(255, 0, 0), width=max(2, W // 400))
        d.line([(W / 2, 0), (W / 2, H)], fill=(0, 255, 255), width=1)
        sx, sy = CFG["safe_margin_x"] * W, CFG["safe_margin_y"] * H
        d.rectangle([sx, sy, W - sx, H - sy], outline=(0, 255, 0), width=1)
        d.text((10, 10), f"{fmt(t)} {label}", fill=(255, 255, 0))
        sheet.paste(im.resize((tw, th)), ((i % 3) * tw, (i // 3) * th))
    sheet.save(out)


# ---------------------------------------------------------------- audio

def check_audio(path, render_meta):
    log = ff_filter_log(path, af=f"silencedetect=n={CFG['dead_air_db']}dB:d={CFG['dead_air_min_s']}")
    for m in re.finditer(r"silence_start: ([\d.]+)[\s\S]*?silence_end: ([\d.]+)", log):
        s, e = float(m.group(1)), float(m.group(2))
        add("warn", "dead-air", s, f"{e - s:.1f}s of silence {fmt(s)}–{fmt(e)}", "editing")
    log = ff_filter_log(path, af="ebur128=peak=true")
    summ = log[log.rfind("Summary:"):]
    mi, mp = re.search(r"I:\s+(-?[\d.]+) LUFS", summ), re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", summ)
    loud = {}
    if mi:
        lufs = float(mi.group(1))
        loud["integrated_lufs"] = lufs
        if abs(lufs - CFG["loudness_target_lufs"]) > CFG["loudness_tolerance"]:
            add("warn", "loudness", None, f"integrated {lufs:.1f} LUFS, target {CFG['loudness_target_lufs']} "
                f"(normalize: ffmpeg -af loudnorm=I={CFG['loudness_target_lufs']}:TP={CFG['true_peak_max_db']})", "editing")
    if mp and mp.group(1) != "-inf":
        tp = float(mp.group(1))
        loud["true_peak_db"] = tp
        if tp > CFG["true_peak_max_db"]:
            add("error" if tp > 0 else "warn", "true-peak", None, f"true peak {tp:.1f} dBTP > {CFG['true_peak_max_db']}", "editing")
    if render_meta and render_meta.get("cut_points"):
        sr = 48000
        x = audio_pcm(path, sr)
        dx = np.abs(np.diff(x))
        base = np.median(dx) + 1e-6
        for c in render_meta["cut_points"]:
            i = int(c * sr)
            win = dx[max(0, i - int(0.005 * sr)): i + int(0.005 * sr)]
            local = np.median(dx[max(0, i - sr // 10): i + sr // 10]) + base
            if len(win) and win.max() > CFG["click_ratio"] * local and win.max() > 0.05:
                add("warn", "cut-click", c, f"audible click at cut ({win.max() / local:.0f}x local slope)", "editing")
    return loud


# ---------------------------------------------------------------- sync

def check_sync(path, transcript, duration):
    """Cross-correlate 'where the transcript says speech is' with 'where the audio has voice energy'."""
    hop = 0.01
    x = audio_pcm(path, 16000)
    n = int(16000 * hop)
    frames = len(x) // n
    if frames < 50:
        return {}
    rms = np.sqrt((x[:frames * n].reshape(frames, n) ** 2).mean(axis=1))
    db = 20 * np.log10(rms + 1e-9)
    lo, hi = np.percentile(db, 5), np.percentile(db, 95)
    if hi - lo < 10:
        return {"note": "no speech/silence contrast in the audio (music bed?); sync not measurable"}
    voiced = (db > lo + 0.4 * (hi - lo)).astype(np.float32)
    expect = np.zeros(frames, dtype=np.float32)
    words = transcript["words"]
    for w in words:
        expect[int(w["start"] / hop): max(int(w["start"] / hop) + 1, int(w["end"] / hop))] = 1
    def lag_of(a, b):
        a, b = a - a.mean(), b - b.mean()
        L = 50  # +/- 500 ms
        best, best_l = -np.inf, 0
        for l in range(-L, L + 1):
            if l >= 0:
                s = float((a[l:] * b[:len(b) - l]).sum())
            else:
                s = float((a[:l] * b[-l:]).sum())
            if s > best:
                best, best_l = s, l
        return best_l * hop * 1000  # +ms = audio later than transcript
    result = {"global_offset_ms": lag_of(voiced, expect)}
    if abs(result["global_offset_ms"]) > CFG["sync_max_offset_ms"]:
        add("error", "av-sync", 0, f"speech is {result['global_offset_ms']:+.0f} ms off the expected word timing "
            "(captions/graphics timed to words will look early/late)", "editing")
    win = int(CFG["sync_window_s"] / hop)
    drift = []
    for s in range(0, frames - win // 2, win):
        if expect[s:s + win].sum() < 30:
            continue
        lag = lag_of(voiced[s:s + win], expect[s:s + win])
        drift.append((s * hop, lag))
    result["windows"] = [{"t": round(t, 2), "offset_ms": l} for t, l in drift]
    if len(drift) >= 2 and abs(drift[-1][1] - drift[0][1]) > CFG["sync_max_offset_ms"]:
        add("error", "av-drift", drift[-1][0], f"sync drifts from {drift[0][1]:+.0f} ms to {drift[-1][1]:+.0f} ms "
            "across the video (frame-rate mismatch or off-grid cuts)", "editing")
    silent = [w for w in words if voiced[int(w["start"] / hop): int(w["end"] / hop) + 1].sum() == 0]
    if words and len(silent) / len(words) > CFG["silent_word_ratio_max"]:
        add("error", "words-in-silence", silent[0]["start"], f"{len(silent)}/{len(words)} transcript words land in "
            f"silence (first: '{silent[0]['word']}' at {fmt(silent[0]['start'])})", "editing")
    return result


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--edit", help="pre-graphics render, needed for graphic checks")
    ap.add_argument("--graphics", help="final.graphics.json from composite.py")
    ap.add_argument("--transcript", help="transcript.edited.json for sync checks")
    ap.add_argument("--render-meta", help="edit.render.json from render_cuts.py")
    ap.add_argument("-o", "--outdir", required=True)
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    render_meta = json.load(open(a.render_meta)) if a.render_meta else None
    meta = check_container(a.video, probe(a.video), render_meta)
    if meta is None:
        sys.exit(1)
    check_frames(a.video, meta)
    if a.graphics and a.edit:
        check_graphics(a.video, a.edit, json.load(open(a.graphics)), meta, a.outdir)
    # Compositing never retimes the edit, so the edit's cut points are valid for the final too.
    loud = check_audio(a.video, render_meta)
    sync = check_sync(a.video, json.load(open(a.transcript)), meta["duration"]) if a.transcript else {}

    findings.sort(key=lambda f: (f["severity"] != "error", f["t"] if f["t"] is not None else -1))
    errors = sum(f["severity"] == "error" for f in findings)
    report = {"video": a.video, "meta": meta, "loudness": loud, "sync": sync,
              "errors": errors, "warnings": len(findings) - errors, "findings": findings}
    json.dump(report, open(os.path.join(a.outdir, "qc_report.json"), "w"), indent=1)
    lines = [f"# QC report: `{a.video}`", "",
             f"**{'FAIL' if errors else 'PASS'}**: {errors} errors, {len(findings) - errors} warnings · "
             f"{meta['width']}x{meta['height']} @ {meta['fps']:.2f} fps · {meta['duration']:.2f}s"
             + (f" · {loud['integrated_lufs']:.1f} LUFS" if "integrated_lufs" in loud else "")
             + (f" · sync {sync['global_offset_ms']:+.0f} ms" if sync else ""), "",
             "| Sev | Time | Check | Finding | Fix in |", "|---|---|---|---|---|"]
    for f in findings:
        lines.append(f"| {f['severity']} | {fmt(f['t'])} | {f['check']} | {f['message']} | {f['fix_stage']} |")
    if os.path.exists(os.path.join(a.outdir, "flagged_frames.png")):
        lines += ["", "Flagged frames (red = graphic bbox, green = title-safe, cyan = center): `flagged_frames.png`"]
    open(os.path.join(a.outdir, "qc_report.md"), "w").write("\n".join(lines) + "\n")
    print(f"[qc] {'FAIL' if errors else 'PASS'}: {errors} errors, {len(findings) - errors} warnings -> {a.outdir}/qc_report.md")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
