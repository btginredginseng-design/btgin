"""Re-render only the logo-affected frames; reuse every other frame of the previous render."""
import subprocess, sys
import numpy as np
from render_ko import render, W, H, FPS, LOGO, FIN, TOTAL

prev, out = sys.argv[1], sys.argv[2]
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", prev, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                        "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
n = W * H * 3
for g in range(TOTAL):
    old = dec.stdout.read(n)
    if g < LOGO + 16 or g >= FIN:   # logo card (+ its dissolve into the hero) and the closing card
        enc.stdin.write(render(g, None).tobytes())
    else:
        enc.stdin.write(old)
enc.stdin.close(); enc.wait()
print("done")
