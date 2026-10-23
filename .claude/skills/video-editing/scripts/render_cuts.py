#!/usr/bin/env python3
"""Render an edl.json with FFmpeg: trim every keep range and concatenate.

Every cut point is snapped to the video frame grid so the audio and video segments
have identical lengths (cuts that drift by a fraction of a frame are the usual cause
of creeping A/V desync). Each audio segment gets a 8 ms fade in/out so cuts don't click.

Usage:
  render_cuts.py work/edl.json -o work/edit.mp4 [--preview] [--crf 18]
"""
import argparse
import json
import os
import subprocess
import tempfile
from fractions import Fraction


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    streams = json.loads(out)["streams"]
    v = next((s for s in streams if s["codec_type"] == "video"), None)
    a = next((s for s in streams if s["codec_type"] == "audio"), None)
    return v, a


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edl")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--preview", action="store_true", help="fast 540p proxy render")
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--fade", type=float, default=0.008, help="audio fade per cut, seconds")
    a = ap.parse_args()

    edl = json.load(open(a.edl))
    src = edl["source"]
    v, au = probe(src)
    fps = Fraction(v["avg_frame_rate"]) if v else Fraction(30)
    if fps == 0:
        fps = Fraction(v["r_frame_rate"])

    def grid(t):
        return float(round(Fraction(t) * fps) / fps)

    parts, labels = [], []
    snapped = []
    for i, k in enumerate(edl["keep"]):
        s, e = grid(k["start"]), grid(k["end"])
        if e - s < float(1 / fps):
            continue
        snapped.append((s, e))
        d = e - s
        if v:
            parts.append(f"[0:v]trim=start={s:.6f}:end={e:.6f},setpts=PTS-STARTPTS[v{i}]")
        if au:
            fd = min(a.fade, d / 4)
            parts.append(f"[0:a]atrim=start={s:.6f}:end={e:.6f},asetpts=PTS-STARTPTS,"
                         f"afade=t=in:d={fd:.4f},afade=t=out:st={d - fd:.6f}:d={fd:.4f}[a{i}]")
        labels.append(("" if not v else f"[v{i}]") + ("" if not au else f"[a{i}]"))
    n = len(labels)
    parts.append("".join(labels) + f"concat=n={n}:v={1 if v else 0}:a={1 if au else 0}"
                 + ("[vc]" if v else "") + ("[ac]" if au else ""))
    vout = "[vc]"
    if v and a.preview:
        parts.append("[vc]scale=-2:540[vp]")
        vout = "[vp]"

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(";\n".join(parts))
        script = f.name
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-i", src, "-filter_complex_script", script]
    if v:
        cmd += ["-map", vout, "-c:v", "libx264", "-preset", "ultrafast" if a.preview else "medium",
                "-crf", str(28 if a.preview else a.crf), "-pix_fmt", "yuv420p", "-r", str(fps)]
    if au:
        cmd += ["-map", "[ac]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    cmd += ["-movflags", "+faststart", a.output]
    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    try:
        subprocess.run(cmd, check=True)
    finally:
        os.unlink(script)

    # Record the frame-snapped cut list next to the render so QC can check cut points exactly.
    cuts, acc = [], 0.0
    for s, e in snapped:
        acc += e - s
        cuts.append(round(acc, 4))
    meta = {"source": src, "output": a.output, "fps": float(fps), "segments": snapped,
            "cut_points": cuts[:-1], "expected_duration": round(acc, 4)}
    json.dump(meta, open(os.path.splitext(a.output)[0] + ".render.json", "w"), indent=1)
    print(f"[render_cuts] {n} segments -> {a.output} ({acc:.2f}s)")


if __name__ == "__main__":
    main()
