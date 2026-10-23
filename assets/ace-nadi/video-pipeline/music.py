"""Original ambient-piano score, 100 BPM, D major, 24 bars = 57.6 s (synced to the edit)."""
import os, wave
import numpy as np

SR = 48000
BPM = 100
BEAT = 60 / BPM            # 0.6 s
BAR = BEAT * 4             # 2.4 s
NBARS = 24
DUR = NBARS * BAR + 2.0
N = int(DUR * SR)
rng = np.random.default_rng(11)
L = np.zeros((N, 2), np.float32)   # tracks mixed into one buffer per bus
pad_bus = np.zeros((N, 2), np.float32)
pno_bus = np.zeros((N, 2), np.float32)
drm_bus = np.zeros((N, 2), np.float32)
bass_bus = np.zeros((N, 2), np.float32)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def put(bus, sig, at, pan=0.0, gain=1.0):
    i = int(at * SR)
    j = min(N, i + len(sig))
    if j <= i:
        return
    l, r = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    bus[i:j, 0] += sig[:j - i] * l * gain
    bus[i:j, 1] += sig[:j - i] * r * gain


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    # vectorised one-pole via scipy-free recursion in chunks (python loop is fine for our sizes)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s = (1 - a) * x[i] + a * s
        y[i] = s
    return y


# ---------------------------------------------------------------- instruments
def piano(m, dur=2.8, vel=0.6, bright=1.0):
    f = mtof(m)
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n, np.float32)
    B = 0.0004
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > 9000:
            break
        amp = (1 / k ** 1.6) * (bright ** (k - 1))
        dec = 1.1 + 0.55 * k + f / 900
        s += amp * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t * dec)
    # felt hammer: soft attack, slight thump
    s *= np.minimum(1, t / 0.006)
    s += np.sin(2 * np.pi * f * 0.5 * t) * np.exp(-t * 18) * 0.15
    rel = int(0.25 * SR)
    s[-rel:] *= np.linspace(1, 0, rel)
    return (s * vel * 0.35).astype(np.float32)


def pad(notes, dur, att=1.0, rel=1.4, cutoff=1800, vol=0.12):
    n = int((dur + rel) * SR); t = np.arange(n) / SR
    s = np.zeros(n, np.float32)
    for m in notes:
        f = mtof(m)
        for det in (-0.07, 0.0, 0.065):
            ff = f * 2 ** (det / 12)
            ph = rng.uniform(0, 6.28)
            s += np.sin(2 * np.pi * ff * t + ph) * 0.5
            s += np.sin(2 * np.pi * ff * 2 * t + ph) * 0.12
            s += np.sin(2 * np.pi * ff * 3 * t + ph) * 0.05
    env = np.minimum(1, t / att)
    tail = t > dur
    env[tail] *= np.exp(-(t[tail] - dur) / (rel / 3))
    s *= env * (1 + 0.08 * np.sin(2 * np.pi * 0.25 * t))
    s = s / len(notes) * vol
    return lowpass(s, cutoff).astype(np.float32)


def bass(m, dur, vol=0.32):
    f = mtof(m)
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.18 * np.sin(2 * np.pi * 2 * f * t)
    env = np.minimum(1, t / 0.05) * np.exp(-t * 0.35)
    r = int(0.3 * SR); env[-r:] *= np.linspace(1, 0, r)
    return (s * env * vol).astype(np.float32)


def kick(vol=0.55):
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 46 + 70 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 7) * np.minimum(1, t / .002) * vol).astype(np.float32)


_sh = rng.standard_normal(int(0.09 * SR)).astype(np.float32)
_sh = _sh - lowpass(_sh, 5000)


def shaker(vol=0.05):
    t = np.arange(len(_sh)) / SR
    return (_sh * np.exp(-t * 55) * np.minimum(1, t / .004) * vol).astype(np.float32)


def snap(vol=0.12):
    n = int(0.25 * SR); t = np.arange(n) / SR
    nz = rng.standard_normal(n).astype(np.float32)
    nz = nz - lowpass(nz, 1500)
    body = np.sin(2 * np.pi * 330 * t) * np.exp(-t * 40) * 0.4
    return ((nz * np.exp(-t * 30) + body) * vol).astype(np.float32)


def bell(m, vol=0.12):
    f = mtof(m)
    n = int(3.0 * SR); t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 2)
         + 0.2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 4))
    return (s * np.exp(-t * 1.3) * np.minimum(1, t / .003) * vol).astype(np.float32)


# ---------------------------------------------------------------- harmony
# D major: Dmaj9 - Bm11 - Gmaj9 - Asus  (voicings: [bass] + upper)
CH = {
    'D':  (38, [50, 57, 61, 64, 66]),
    'Bm': (35, [47, 54, 57, 62, 64]),
    'G':  (31, [43, 50, 54, 57, 59]),
    'A':  (33, [45, 52, 57, 59, 64]),
    'Em': (40, [52, 55, 59, 62, 66]),
    'F#m': (42, [54, 57, 61, 64, 69]),
}
PROG = ['D', 'Bm', 'G', 'A'] * 4 + ['G', 'A', 'F#m', 'Bm', 'Em', 'A'] + ['D', 'D']
assert len(PROG) == NBARS

ARP = [0, 2, 1, 3, 2, 4, 3, 1]          # 8th-note pattern over chord tones (+12)
MELODY = {17: [(0, 78), (2, 76)], 18: [(0, 81), (2.5, 78)], 19: [(0, 78), (2, 73)],
          20: [(0, 74), (2, 76)], 21: [(0, 78), (2, 76), (3, 73)]}

for b, name in enumerate(PROG):
    t0 = b * BAR
    root, up = CH[name]
    last = b >= 22
    # --- pad (always), brighter from the product section
    cut = 1400 if b < 8 else 2000 if b < 17 else 2600
    if last:
        if b == 22:
            put(pad_bus, pad(up + [69], 2 * BAR + 0.5, att=0.6, rel=2.5, cutoff=2400, vol=0.13), t0)
    else:
        put(pad_bus, pad(up, BAR, att=0.9 if b == 0 else 0.35, rel=1.3, cutoff=cut,
                         vol=0.06 if b < 2 else 0.11), t0, 0.0)
    # --- piano
    hi = [m + 12 for m in up]
    if b < 2:
        for k, idx in enumerate([0, 3, 2, 4]):
            put(pno_bus, piano(hi[idx], 3.0, 0.45 + 0.1 * (k == 0)), t0 + k * BEAT, pan=-0.2 + 0.13 * k)
    elif b < 22:
        for k, idx in enumerate(ARP):
            v = (0.55 if k % 2 == 0 else 0.4) * (1.1 if b >= 17 else 1.0)
            swing = 0.012 if k % 2 else 0.0
            put(pno_bus, piano(hi[idx], 2.4, v, bright=0.92 if b < 17 else 1.0), t0 + k * BEAT / 2 + swing,
                pan=-0.35 + 0.1 * idx)
    elif b == 22:
        # final rolled chord
        for k, m in enumerate([50, 57, 62, 66, 69, 73, 76]):
            put(pno_bus, piano(m + 12 if m < 60 else m, 5.5, 0.55), t0 + k * 0.07, pan=-0.4 + 0.12 * k)
    # --- bass from bar 4
    if 4 <= b < 22:
        put(bass_bus, bass(root + 12, BAR), t0)
    elif b == 22:
        put(bass_bus, bass(root + 12, 2 * BAR + 1.0, 0.3), t0)
    # --- drums: bars 8..21 (breath on bar 16 second half before product reveal)
    if 8 <= b < 22:
        for beat in range(4):
            tb = t0 + beat * BEAT
            if b == 16 and beat >= 2:
                continue
            if beat in (0, 2):
                put(drm_bus, kick(0.5 if b < 17 else 0.58), tb)
            if b >= 12 and beat in (1, 3):
                put(drm_bus, snap(), tb, pan=0.1)
            for h in range(2):
                put(drm_bus, shaker(0.045 if h else 0.03), tb + h * BEAT / 2, pan=0.35)
    # --- bell melody over product section
    if b in MELODY:
        for beat, m in MELODY[b]:
            put(pno_bus, bell(m), t0 + beat * BEAT, pan=0.25)

# reverse-cymbal style swell into the product reveal (bar 17)
n = int(2.0 * SR); t = np.arange(n) / SR
nz = rng.standard_normal(n).astype(np.float32)
nz = nz - lowpass(nz, 3000)
put(drm_bus, nz * (t / 2.0) ** 3 * 0.12, 17 * BAR - 2.0)
put(drm_bus, nz[::-1].copy() * (t / 2.0) ** 3 * 0.06, 22 * BAR - 2.0)


# ---------------------------------------------------------------- mix + reverb
def reverb(x, secs, decay, mix):
    n_ir = int(secs * SR)
    ir = rng.standard_normal((n_ir, 2)).astype(np.float32) * np.exp(-np.arange(n_ir) / SR * decay)[:, None]
    ir[:int(0.015 * SR)] = 0
    Lf = 1 << int(np.ceil(np.log2(len(x) + n_ir)))
    wet = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], Lf) * np.fft.rfft(ir[:, c], Lf), Lf)[:len(x)] for c in range(2)], 1)
    wet *= np.max(np.abs(x)) / (np.max(np.abs(wet)) + 1e-9)
    return x + wet * mix

pno = reverb(pno_bus, 3.0, 2.2, 0.55)
padr = reverb(pad_bus, 3.0, 1.8, 0.4)
drm = reverb(drm_bus, 1.2, 6.0, 0.18)
mix = pno * 1.0 + padr * 1.0 + drm * 0.9 + bass_bus * 0.9
# master: gentle glue, fade in/out
mix = np.tanh(mix * 1.4) / 1.4
fi = int(0.4 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
end = int((NBARS * BAR) * SR)
mix = mix[:end]
fo = int(1.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
mix *= 0.89 / np.max(np.abs(mix))
pcm = (mix * 32767).astype(np.int16)
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music.wav')
with wave.open(path, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('wrote', path, len(mix) / SR)
