"""Re-render only the footage frames (captions changed); reuse all card frames from the previous render."""
import subprocess, sys
from render_ko import render, footage_reader, W, H, FPS, F0, FEND, TOTAL

prev, out = sys.argv[1], sys.argv[2]
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", prev, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                        "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
reader = footage_reader()
n = W * H * 3
for g in range(TOTAL):
    old = dec.stdout.read(n)
    if F0 <= g < FEND:
        enc.stdin.write(render(g, next(reader)).tobytes())
    else:
        enc.stdin.write(old)
    if g % 200 == 0:
        print("frame", g, "/", TOTAL, flush=True)
enc.stdin.close(); enc.wait()
print("done")
