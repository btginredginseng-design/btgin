"""Re-render only the footage frames of render_v3; reuse card frames from the previous render."""
import subprocess, sys
import render_v3 as V

prev, out = sys.argv[1], sys.argv[2]
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", prev, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{V.W}x{V.H}",
                        "-r", str(V.FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                        "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
reader, base, n = V.R.footage_reader(), V.Base(), V.W * V.H * 3
for g in range(V.TOTAL):
    old = dec.stdout.read(n)
    if V.F0 <= g < V.FEND:
        enc.stdin.write(V.render(g, base, next(reader)).tobytes())
    else:
        enc.stdin.write(old)
    if g % 200 == 0:
        print("frame", g, "/", V.TOTAL, flush=True)
enc.stdin.close(); enc.wait()
print("done", flush=True)
