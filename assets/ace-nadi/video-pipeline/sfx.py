"""Synthesized sound-design track (no music) synced to build.py's timeline."""
import os, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B

SR = 48000
rng = np.random.default_rng(7)
N = int((B.TOTAL + 0.5) * SR)
mix = np.zeros((N, 2), np.float32)


def env_ad(n, a, d_pow=3.0):
    t = np.linspace(0, 1, n, dtype=np.float32)
    ai = max(1, int(n * a))
    e = np.ones(n, np.float32)
    e[:ai] = np.linspace(0, 1, ai) ** 2
    e[ai:] = (1 - np.linspace(0, 1, n - ai)) ** d_pow
    return e


def onepole_sweep(x, f0, f1):
    """time-varying one-pole lowpass, cutoff sweeping f0->f1 (log)"""
    n = len(x)
    fc = np.exp(np.linspace(np.log(f0), np.log(f1), n))
    a = np.exp(-2 * np.pi * fc / SR).astype(np.float32)
    y = np.empty_like(x); s = 0.0
    for i in range(n):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y


def whoosh(dur=0.7, pan=(-.7, .7), peak=.45, lo=300, hi=4500):
    n = int(dur * SR)
    noise = rng.standard_normal(n).astype(np.float32)
    up = onepole_sweep(noise, lo, hi)
    hp = up - onepole_sweep(up, 120, 120)
    e = env_ad(n, peak, 2.2)
    sig = hp * e
    p = np.linspace(pan[0], pan[1], n)
    l, r = np.sqrt((1 - p) / 2), np.sqrt((1 + p) / 2)
    return np.stack([sig * l, sig * r], 1)


def shimmer(dur=2.2, base=1046.5, amp=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    for k, m in enumerate([1, 1.5, 2, 2.52, 3, 4]):
        f = base * m * (1 + 0.002 * np.sin(2 * np.pi * (4 + k) * t))
        out += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * (0.5 / (1 + k)) * np.exp(-t * (1.6 + k * .5))
    att = np.minimum(1, t / 0.02)
    out *= att * amp
    st = np.stack([out, np.roll(out, int(SR * .011))], 1)
    return st


def tick(freq=2300, dur=.07, amp=.35):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) * np.exp(-t * 70) * amp
    s += np.sin(2 * np.pi * freq * 2.01 * t) * np.exp(-t * 110) * amp * .3
    return np.stack([s, s], 1).astype(np.float32)


def pop(dur=.22, amp=.5):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 700 * np.exp(-t * 6) + 420
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 22) * amp
    return np.stack([s, s], 1).astype(np.float32)


def boom(dur=2.0, amp=.9):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 62 * np.exp(-t * 1.2) + 38
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 2.4) * np.minimum(1, t / .015) * amp
    nz = onepole_sweep(rng.standard_normal(n).astype(np.float32), 900, 120) * np.exp(-t * 5) * .5
    s = s + nz
    return np.stack([s, s], 1).astype(np.float32)


def swell(dur=1.0, amp=.5):
    """reverse-ish airy rise into a flash"""
    n = int(dur * SR)
    nz = rng.standard_normal(n).astype(np.float32)
    s = onepole_sweep(nz, 400, 7000)
    s = s - onepole_sweep(s, 200, 200)
    t = np.linspace(0, 1, n)
    e = np.where(t < .75, (t / .75) ** 2.5, (1 - (t - .75) / .25) ** 1.5)
    s = s * e * amp
    return np.stack([s, np.roll(s, 300)], 1).astype(np.float32)


def add(sig, at, gain=1.0):
    i = int(at * SR)
    if i < 0:
        sig = sig[-i:]; i = 0
    j = min(N, i + len(sig))
    mix[i:j] += sig[:j - i] * gain


# --- intro & end
add(swell(1.2, .35), 0.0)
add(boom(2.2, .8), 0.35, .9)
add(shimmer(2.6, 1046.5, .45), 0.35)
add(shimmer(2.0, 1568, .25), 1.0)
add(whoosh(1.0, (.0, .0), .7, 200, 2500), 2.7, .35)   # focus pull air

# --- transitions
for i, (kind, td) in enumerate(B.TRANS):
    nxt = B.SHOTS[i + 1].start
    mid = nxt + td / 2
    if kind == 'whip':
        add(whoosh(.55, (-.9, .9), .5, 500, 7000), mid - .3, .55)
    elif kind == 'zoom':
        add(whoosh(.8, (.0, .0), .55, 250, 5000), mid - .45, .5)
    elif kind == 'flash':
        add(swell(.9, .4), mid - .7)
        add(shimmer(1.6, 1318.5, .22), mid)
    else:
        add(whoosh(.9, (.3, -.3), .6, 200, 1600), mid - .5, .18)

# --- text ticks
ticks = [4.3] + [B.SHOTS[i].start + .55 for i in (1, 3, 4, 5, 6, 8, 9)]
for tt in ticks:
    add(tick(), tt, .8)
    add(tick(3100, .05, .2), tt + .09, .8)
# actives counters
s2 = B.SHOTS[2].start + .5
for dl in (.2, .6):
    add(pop(), s2 + dl, .7)
# 23ml counter
add(pop(.3, .5), B.SHOTS[4].start + .85, .7)
# product section
s11 = B.SHOTS[11].start + .35
add(whoosh(.9, (-.6, .2), .55, 200, 3000), s11 - .1, .45)
add(shimmer(1.6, 1760, .2), s11 + 1.6)          # pouch sheen
for k in range(4):
    add(pop(.2, .4), s11 + 1.0 + k * .38, .65)
# quality section
s12 = B.SHOTS[12].start + .45
for k in range(3):
    add(pop(.2, .45), s12 + .7 + k * .3, .6)
# end card
s13 = B.SHOTS[13].start
add(boom(2.4, .7), s13 + .25, .8)
add(shimmer(3.0, 1046.5, .4), s13 + .25)
add(shimmer(2.4, 1568, .2), s13 + .8)

# --- light reverb (FFT convolution with decaying noise IR)
ir_n = int(1.4 * SR)
ir = rng.standard_normal((ir_n, 2)).astype(np.float32) * np.exp(-np.arange(ir_n) / SR * 4.5)[:, None]
ir[0] = 0
L = 1 << int(np.ceil(np.log2(N + ir_n)))
wet = np.stack([np.fft.irfft(np.fft.rfft(mix[:, c], L) * np.fft.rfft(ir[:, c], L), L)[:N] for c in range(2)], 1)
wet /= np.max(np.abs(wet)) + 1e-9
dry = mix / (np.max(np.abs(mix)) + 1e-9)
out = dry * .85 + wet * .22
# fade tail, normalize to -3 dBFS
fade = int(.8 * SR)
out[-fade:] *= np.linspace(1, 0, fade)[:, None]
out *= 0.707 / np.max(np.abs(out))
pcm = (out * 32767).astype(np.int16)
path = os.path.join(B.BASE, 'sfx.wav')
with wave.open(path, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('wrote', path, N / SR)
