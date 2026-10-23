"""Builds the soundtrack: original footage audio + synthesized minor SFX (no music)."""
import subprocess, sys, wave
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from render import SRC, PRE, NF, DET, FIN, FPS, FEND, CUTS, SECTION_CUTS, FLASH_CUTS, TOTAL

SR = 48000
N = int(TOTAL / FPS * SR) + SR
mix = np.zeros((N, 2), np.float32)
rng = np.random.default_rng(7)


def onepole_lp(x, fc):
    """time-varying one-pole lowpass; fc array (Hz) per sample"""
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x); s = 0.0
    for n in range(len(x)):
        s = (1 - a[n]) * x[n] + a[n] * s
        y[n] = s
    return y


def whoosh(dur=0.7, peak=0.6, f_lo=250, f_hi=5500, pan=(-.6, .6)):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / (1 - peak) * 4.5))
    fc = f_lo + (f_hi - f_lo) * env ** 1.3
    x = rng.standard_normal(n).astype(np.float64)
    y = onepole_lp(x, fc)
    y = onepole_lp(y, fc * 1.4)            # 2-pole for smoother tone
    y = y - onepole_lp(y, np.full(n, 120.0))  # remove rumble
    y = y / (np.abs(y).max() + 1e-9) * env
    p = np.interp(t, [0, 1], pan)
    return np.stack([y * np.sqrt((1 - p) / 2), y * np.sqrt((1 + p) / 2)], 1), peak * dur


def hit(dur=1.4, f0=95, f1=42):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 9)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t * 3.2)
    click = onepole_lp(rng.standard_normal(n), np.full(n, 1800.0)) * np.exp(-t * 60) * 1.5
    y = y + click
    y /= np.abs(y).max()
    return np.stack([y, y], 1), 0.0


def tick(f=2600, dur=0.09):
    n = int(dur * SR); t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * f * t) + .35 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 70)
    y *= np.minimum(1, t * SR / 40)
    return np.stack([y, y], 1) / 1.35, 0.0


def shimmer(dur=2.2):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for k, f in enumerate([1046.5, 1568, 2093, 2637, 3136]):
        y += np.sin(2 * np.pi * f * t + k) * np.exp(-t * (1.6 + k * .4)) / (1 + k * .5)
    y *= np.minimum(1, t / 0.02) * (1 + .15 * np.sin(2 * np.pi * 5 * t))
    y /= np.abs(y).max()
    l = np.concatenate([y, np.zeros(240)])[:n]; r = np.concatenate([np.zeros(240), y])[:n]
    return np.stack([l, r], 1), 0.0


def riser(dur=2.4):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    env = t ** 2.5 * np.minimum(1, (1 - t) * 30 + .0)
    fc = 200 + 3800 * t ** 2
    y = onepole_lp(rng.standard_normal(n), fc)
    y = y / np.abs(y).max() * env
    tone = np.sin(2 * np.pi * np.cumsum(110 + 220 * t ** 2) / SR) * env * .25
    y = y + tone
    return np.stack([y, y], 1), 0.0


def add(sound, at, gain_db):
    s, offset = sound
    i = int((at - offset) * SR)
    g = 10 ** (gain_db / 20)
    j0 = max(0, i); j1 = min(N, i + len(s))
    if j1 > j0:
        mix[j0:j1] += s[j0 - i:j1 - i] * g


def T(gframe):
    return gframe / FPS


# --- footage audio (kept as recorded, level-matched)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC[0], "-i", SRC[1], "-filter_complex",
                      "[0:a][1:a]concat=n=2:v=0:a=1,aresample=48000", "-f", "f32le", "-ac", "2", "-"],
                     capture_output=True).stdout
fa = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
fa = fa[: int(NF / FPS * SR)]
rms = np.sqrt((fa ** 2).mean())
fa *= 10 ** (-21 / 20) / rms
n = len(fa); t = np.arange(n) / SR
fa *= np.minimum(1, t / 0.12)[:, None]
fa *= np.clip((n / SR - t) / 0.7, 0, 1)[:, None]
s0 = int(PRE / FPS * SR)
mix[s0:s0 + n] += fa

# --- SFX
add(riser(2.4), 0.12, -24)
add(hit(1.6), T(10), -20)
add(tick(2200), T(26), -30)
add(whoosh(.8, .7, 300, 6500), T(PRE), -17)
add(hit(1.8, 80, 38), T(PRE), -15)
for k, fr in enumerate([8, 14, 24, 32]):
    add(tick(2400 + 200 * k), T(PRE + fr + 3), -31)

for n_, c in enumerate(CUTS):
    g = PRE + c
    if c in SECTION_CUTS:
        d = 1 if n_ % 2 == 0 else -1
        add(whoosh(.75, .62, 250, 6000, (-.7 * d, .7 * d)), T(g), -16)
        add(tick(2600), T(g + 13), -30)
        add(tick(2000), T(g + 18), -33)
    elif c in FLASH_CUTS:
        add(whoosh(.45, .6, 400, 7000), T(g), -24)
        add(shimmer(1.2), T(g), -36)
    else:
        add(whoosh(.4, .55, 500, 4500), T(g), -27)

# end cards: faint air bed so the cards never sit in dead silence
nb = int((DET + FIN) / FPS * SR) + int(.7 * SR)
tb = np.arange(nb) / SR
bed = onepole_lp(rng.standard_normal(nb), np.full(nb, 900.0))
bed = bed / np.abs(bed).max() * np.minimum(1, tb / .8) * np.clip((tb[-1] - tb) / 1.6, 0, 1)
bed2 = onepole_lp(rng.standard_normal(nb), np.full(nb, 900.0)) / np.abs(bed).max()
add((np.stack([bed, bed2 / np.abs(bed2).max() * np.abs(bed).max()], 1), 0.0), T(FEND) - .7, -34)
add(whoosh(1.0, .55, 200, 5000), T(FEND), -15)
add(hit(1.8, 70, 36), T(FEND + 2), -17)
add(tick(2300), T(FEND + 18), -27)
for k in range(6):
    add(tick(2000 + 150 * k), T(FEND + 34 + 7 * k + 2), -28)
add(whoosh(.9, .6, 200, 3500), T(FEND + DET - 8), -22)
add(hit(2.2, 75, 34), T(FEND + DET + 8), -14)
add(shimmer(2.6), T(FEND + DET + 8), -25)

mix = mix[: int(TOTAL / FPS * SR)]
# gentle peak control
pk = np.abs(mix).max()
a = np.abs(mix)
mix = np.where(a < .7, mix, np.sign(mix) * (.7 + .2 * np.tanh((a - .7) / .2)))
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("peak in", pk, "len", len(mix) / SR)
