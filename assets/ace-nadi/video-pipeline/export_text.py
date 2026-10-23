"""Export each text-motion element of the film as a transparent 1920x1080 WebM (VP9 alpha) + PNG still."""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B

OUT = os.path.join(B.BASE, 'text_motions')
os.makedirs(OUT, exist_ok=True)

# names in the order build.py registers ELEMS
names = ['00_intro_logo', '03_key_actives_card', '05a_23ml_counter', '10_product_key_ingredients',
         '11_quality_tested', '12_end_card',
         '01_made_in_sejong', '02_dual_function', '04_bio_ferment', '05_filling_23ml', '06_tencel_sheet',
         '07_sealing', '08_traceability', '09_inspection']
assert len(names) == len(B.ELEMS)

act_card = B.CARDS[0]


def card_layer(layer, t):
    """the frosted card can't blur Canva's background, so export it as a soft white panel"""
    x0, y0, x1, y1, c0, c1 = act_card
    if c0 <= t <= c1:
        a = B.ease_io((t - c0) / .45) * B.ease_io((c1 - t) / .4)
        d = ImageDraw.Draw(layer)
        d.rounded_rectangle([x0, y0, x1 - 1, y1 - 1], radius=28, fill=(250, 248, 253, int(205 * a)),
                            outline=(255, 255, 255, int(220 * a)), width=2)


def frames_for(fn):
    """find the frame window where the element draws anything"""
    hit = []
    for fi in range(B.NFRAMES):
        layer = Image.new('RGBA', (B.W, B.H), (0, 0, 0, 0))
        fn(layer, fi / B.FPS)
        if layer.getbbox():
            hit.append(fi)
    return hit[0], hit[-1]


def render(name, fns, f0, f1):
    path = os.path.join(OUT, f'{name}.webm')
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba',
                            '-s', f'{B.W}x{B.H}', '-r', str(B.FPS), '-i', '-',
                            '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuva420p', '-b:v', '0', '-crf', '24',
                            '-row-mt', '1', '-auto-alt-ref', '0', path], stdin=subprocess.PIPE)
    best, best_a = None, -1
    for fi in range(f0, f1 + 1):
        t = fi / B.FPS
        layer = Image.new('RGBA', (B.W, B.H), (0, 0, 0, 0))
        for fn in fns:
            fn(layer, t)
        enc.stdin.write(layer.tobytes())
        # keep the most "complete" frame as the PNG still
        a = np.asarray(layer.getchannel('A'), dtype=np.uint32).sum()
        if a >= best_a:
            best, best_a = layer, a
    enc.stdin.close(); enc.wait()
    best.save(os.path.join(OUT, f'{name}.png'))
    return (f1 - f0 + 1) / B.FPS


rows = []
elems = dict(zip(names, B.ELEMS))
# merge the 23ml counter with the filling chapter, and the card with the actives text
groups = [(n, [elems[n]]) for n in names if n not in ('05a_23ml_counter', '05_filling_23ml', '03_key_actives_card')]
groups.append(('05_filling_23ml', [elems['05a_23ml_counter'], elems['05_filling_23ml']]))
groups.append(('03_key_actives_card', [card_layer, elems['03_key_actives_card']]))
for name, fns in sorted(groups):
    lo, hi = [], []
    for fn in fns:
        a, b = frames_for(fn); lo.append(a); hi.append(b)
    f0, f1 = max(0, min(lo) - 2), min(B.NFRAMES - 1, max(hi) + 2)
    dur = render(name, fns, f0, f1)
    rows.append((name, f0 / B.FPS, dur))
    print(f'{name}: starts {f0 / B.FPS:.2f}s in film, {dur:.2f}s long', flush=True)

# soft light scrims (static PNGs) used behind chapter text
for side, m in B.SCRIM.items():
    a = (m * 255).astype(np.uint8)
    im = Image.new('RGBA', (B.W, B.H), (250, 248, 253, 0)); im.putalpha(Image.fromarray(a))
    im.save(os.path.join(OUT, f'scrim_{side}.png'))
Image.fromarray(B.END_BG.astype(np.uint8)).save(os.path.join(OUT, 'end_card_background.png'))
with open(os.path.join(OUT, 'timings.txt'), 'w') as f:
    for r in rows:
        f.write(f'{r[0]}\t{r[1]:.2f}\t{r[2]:.2f}\n')
