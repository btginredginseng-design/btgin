#!/usr/bin/env python3
"""Overlay rendered graphics onto the edit at their beat times.

Reads every graphics/<ID>/graphic.json:
  {"id": "B09", "beat": "B09", "treatment": "number-counter", "in": 4.97, "duration": 2.4,
   "file": "out.mov", "layer": 10, "align": "right", "safe": "title"}

Writes:
  final.mp4             edit + graphics (audio copied untouched from the edit)
  final.graphics.json   the overlay windows, for video-review/qc.py

Usage:
  composite.py work/edit.mp4 graphics/ -o out/final.mp4 [--crf 18]
"""
import argparse
import glob
import json
import os
import subprocess


def probe_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,avg_frame_rate", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    n, d = s["avg_frame_rate"].split("/")
    return s["width"], s["height"], float(n) / float(d)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edit")
    ap.add_argument("graphics_dir")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--crf", type=int, default=18)
    a = ap.parse_args()

    W, H, fps = probe_size(a.edit)
    items = []
    for meta_path in sorted(glob.glob(os.path.join(a.graphics_dir, "*", "graphic.json"))):
        g = json.load(open(meta_path))
        f = os.path.join(os.path.dirname(meta_path), g.get("file", "out.mov"))
        if not os.path.exists(f):
            print(f"[composite] skip {g['id']}: {f} not rendered")
            continue
        g["path"] = f
        items.append(g)
    items.sort(key=lambda g: (g.get("layer", 10), g["in"]))

    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-i", a.edit]
    for g in items:
        cmd += ["-i", g["path"]]
    chain, last = [], "[0:v]"
    for i, g in enumerate(items, start=1):
        t0, t1 = g["in"], g["in"] + g["duration"]
        # Shift the graphic onto the edit's timeline and scale it to the edit's frame size.
        chain.append(f"[{i}:v]scale={W}:{H},format=yuva420p,setpts=PTS-STARTPTS+{t0:.4f}/TB[g{i}]")
        chain.append(f"{last}[g{i}]overlay=0:0:eof_action=pass:enable='between(t,{t0:.4f},{t1:.4f})'[v{i}]")
        last = f"[v{i}]"
    if not items:
        chain.append("[0:v]null[v0]")
        last = "[v0]"
    cmd += ["-filter_complex", ";".join(chain), "-map", last, "-map", "0:a?", "-c:v", "libx264",
            "-crf", str(a.crf), "-pix_fmt", "yuv420p", "-r", str(fps), "-c:a", "copy",
            "-movflags", "+faststart", a.output]
    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    subprocess.run(cmd, check=True)
    windows = [{k: g.get(k) for k in ("id", "beat", "treatment", "in", "duration", "align", "safe", "text")}
               for g in items]
    json.dump({"edit": a.edit, "output": a.output, "width": W, "height": H, "fps": fps, "graphics": windows},
              open(os.path.splitext(a.output)[0] + ".graphics.json", "w"), indent=1)
    print(f"[composite] {len(items)} graphics -> {a.output}")


if __name__ == "__main__":
    main()
