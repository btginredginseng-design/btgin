"""Builds the soundtrack: original footage audio + synthesized minor SFX (no music)."""
import subprocess, sys, wave
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from render_ko import SRC
from render_v3 import NF, FPS, F0, FEND, XF, C1, C2, FIN, LOGO, TOTAL, STEPS, CALLOUT

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



# --- original footage audio, untouched apart from level and the dissolve fades
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC[0], "-i", SRC[1], "-filter_complex",
                      "[0:a][1:a]concat=n=2:v=0:a=1,aresample=48000", "-f", "f32le", "-ac", "2", "-"],
                     capture_output=True).stdout
fa = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()[: int(NF / FPS * SR)]
fa *= 10 ** (-20 / 20) / np.sqrt((fa ** 2).mean())
n = len(fa); t = np.arange(n) / SR
xf = XF / FPS
fa *= (np.minimum(1, t / xf) * np.clip((n / SR - t) / xf, 0, 1))[:, None]
s0 = int(F0 / FPS * SR)
mix[s0:s0 + n] += fa


def bed(t0, t1, fin=.8, fout=.8):
    nb = int((t1 - t0) * SR); tb = np.arange(nb) / SR
    env = np.minimum(1, tb / fin) * np.clip((tb[-1] - tb) / fout, 0, 1)
    l = onepole_lp(rng.standard_normal(nb), np.full(nb, 800.0)); r = onepole_lp(rng.standard_normal(nb), np.full(nb, 800.0))
    l /= np.abs(l).max(); r /= np.abs(r).max()
    return np.stack([l * env, r * env], 1), 0.0


# quiet air under the cards so they never sit in dead silence
add(bed(0, T(F0 + XF) + .3, .6, 1.0), 0, -36)
add(bed(T(C1) - .3, T(TOTAL), 1.0, 1.4), T(C1) - .3, -36)

# very subtle accents
add(hit(1.6, 70, 38), T(4), -30)
add(shimmer(1.8), T(6), -36)
add(whoosh(.9, .6, 200, 2500), T(LOGO - XF), -33)
add(whoosh(1.0, .6, 200, 2500), T(F0 + 2), -32)
for st in STEPS:
    t_in = st[0] + (XF + 4 if st[0] == 0 else 6)
    add(whoosh(.5, .5, 600, 3500), T(F0 + t_in + 3), -36)
# callout: soft tick as the circle closes, another as the card pops
add(tick(2400), T(F0 + CALLOUT["t0"] + 14), -34)
add(tick(2000), T(F0 + CALLOUT["t0"] + 20), -32)
add(whoosh(1.0, .6, 200, 2500), T(C1 + 2), -31)
add(whoosh(.8, .6, 200, 2500), T(C2 + 2), -33)
add(whoosh(.8, .6, 200, 2500), T(FIN + 2), -33)
add(hit(2.2, 70, 34), T(FIN + 8), -27)
add(shimmer(2.6), T(FIN + 8), -32)

mix = mix[: int(TOTAL / FPS * SR)]
a = np.abs(mix)
mix = np.where(a < .7, mix, np.sign(mix) * (.7 + .2 * np.tanh((a - .7) / .2)))
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("len", len(mix) / SR)
