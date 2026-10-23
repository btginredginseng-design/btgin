"""ACE NADI production film: 1920x1080 @30fps, clean-luxury style.

Usage: python3 -I build.py [preview_seconds_list]
"""
import math, subprocess, sys, os, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(BASE, '..', 'vid', 'clips')
A = os.path.join(BASE, 'assets')
W, H, FPS = 1920, 1080, 30
GRADE = open(os.path.join(BASE, 'grade.txt')).read().strip()

# palette
DEEP = (74, 36, 112)
PURPLE = (118, 70, 168)
LAV = (196, 180, 226)
INK = (72, 66, 88)
WHITE = (255, 255, 255)

KR = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
EN_L = '/usr/share/fonts/opentype/inter/Inter-Light.otf'
EN_M = '/usr/share/fonts/opentype/inter/Inter-Medium.otf'
EN_XL = '/usr/share/fonts/opentype/inter/InterDisplay-ExtraLight.otf'
EN_T = '/usr/share/fonts/opentype/inter/InterDisplay-Thin.otf'


@functools.lru_cache(None)
def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def ease_out(p):
    p = clamp(p); return 1 - (1 - p) ** 3

def ease_io(p):
    p = clamp(p); return 4 * p ** 3 if p < .5 else 1 - (-2 * p + 2) ** 3 / 2

def ease_out_expo(p):
    p = clamp(p); return 1 if p >= 1 else 1 - 2 ** (-10 * p)


# ---------------------------------------------------------------- text sprites
@functools.lru_cache(None)
def text_sprite(text, path, size, color, tracking=0.0, shadow=False):
    f = font(path, size)
    asc, desc = f.getmetrics()
    # measure with tracking
    widths = [f.getlength(ch) for ch in text]
    tw = int(sum(widths) + tracking * max(len(text) - 1, 0)) + 8
    th = asc + desc + 8
    im = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tracking == 0:
        d.text((4, 4), text, font=f, fill=color + (255,))
    else:
        x = 4.0
        for ch, w_ in zip(text, widths):
            d.text((x, 4), ch, font=f, fill=color + (255,))
            x += w_ + tracking
    return im


def with_alpha(im, a):
    if a >= 0.999:
        return im
    arr = np.asarray(im).copy()
    arr[..., 3] = (arr[..., 3].astype(np.float32) * a).astype(np.uint8)
    return Image.fromarray(arr)


def wipe(im, f, soft=60):
    """reveal left->right with a soft edge; f in 0..1"""
    if f >= 0.999:
        return im
    w, h = im.size
    arr = np.asarray(im).copy()
    x = np.arange(w, dtype=np.float32)
    edge = f * (w + soft) - soft
    m = np.clip((edge + soft - x) / soft, 0, 1)
    arr[..., 3] = (arr[..., 3].astype(np.float32) * m[None, :]).astype(np.uint8)
    return Image.fromarray(arr)


def paste_rise(layer, im, x, y, p, a=1.0, dist=None):
    """mask-rise: sprite slides up from under its own baseline"""
    w, h = im.size
    dist = dist or h
    off = int(round((1 - ease_out(p)) * dist))
    if off >= h:
        return
    piece = im.crop((0, 0, w, h - off)) if off > 0 else im
    layer.alpha_composite(with_alpha(piece, a), (int(x), int(y + off)))


def paste(layer, im, x, y, a=1.0):
    if a <= 0.003:
        return
    x, y = int(round(x)), int(round(y))
    w, h = im.size
    # clip to frame
    x0, y0 = max(0, -x), max(0, -y)
    x1, y1 = min(w, W - x), min(h, H - y)
    if x1 <= x0 or y1 <= y0:
        return
    if (x0, y0, x1, y1) != (0, 0, w, h):
        im = im.crop((x0, y0, x1, y1))
    layer.alpha_composite(with_alpha(im, a), (x + x0, y + y0))


# ---------------------------------------------------------------- brand assets
def mask_sprite(name, height, color):
    m = Image.open(os.path.join(A, f'{name}_mask.png')).convert('L')
    arr = np.asarray(m).astype(np.float32)
    arr = np.clip((arr - 28) / 200.0, 0, 1) ** 0.9
    m = Image.fromarray((arr * 255).astype(np.uint8))
    s = height / m.size[1]
    m = m.resize((int(m.size[0] * s), height), Image.LANCZOS)
    im = Image.new('RGBA', m.size, color + (0,))
    im.putalpha(m)
    return im

EMBLEM = mask_sprite('emblem', 330, DEEP)
WORDMARK = mask_sprite('wordmark', 150, DEEP)
KNAME = mask_sprite('kname', 46, DEEP)
EMBLEM_S = mask_sprite('emblem', 250, DEEP)
WORDMARK_S = mask_sprite('wordmark', 112, DEEP)


def build_pouch(height):
    p = Image.open(os.path.join(A, 'pouch1.png')).convert('RGBA')
    arr = np.asarray(p).astype(np.float32)
    rgb = arr[..., :3]
    # lift the photo's grey to a clean white pouch, keep ink colours
    rgb = np.clip((rgb - 20) * 1.42, 0, 255)
    arr[..., :3] = rgb
    p = Image.fromarray(arr.astype(np.uint8))
    s = height / p.size[1]
    p = p.resize((int(p.size[0] * s), height), Image.LANCZOS)
    pad = 90
    canvas = Image.new('RGBA', (p.size[0] + pad * 2, p.size[1] + pad * 2), (0, 0, 0, 0))
    sh = Image.new('RGBA', canvas.size, (60, 30, 90, 0))
    a = Image.new('L', canvas.size, 0)
    a.paste(p.getchannel('A'), (pad + 18, pad + 30))
    a = a.filter(ImageFilter.GaussianBlur(28)).point(lambda v: int(v * 0.30))
    sh.putalpha(a)
    canvas.alpha_composite(sh)
    canvas.alpha_composite(p, (pad, pad))
    return canvas, pad, p.size

POUCH, POUCH_PAD, POUCH_SZ = build_pouch(800)
_pa = np.asarray(POUCH.getchannel('A')).astype(np.float32) / 255
_py, _px = np.mgrid[0:POUCH.size[1], 0:POUCH.size[0]].astype(np.float32)
_pouch_inner = np.zeros_like(_pa)
_pouch_inner[POUCH_PAD:POUCH_PAD + POUCH_SZ[1], POUCH_PAD:POUCH_PAD + POUCH_SZ[0]] = 1
_pmask = np.asarray(Image.open(os.path.join(A, 'pouch1.png')).getchannel('A').resize(POUCH_SZ, Image.LANCZOS)).astype(np.float32) / 255


def pouch_with_sheen(p):
    """diagonal light sweep across the pouch, p 0..1"""
    if p <= 0 or p >= 1:
        return POUCH
    arr = np.asarray(POUCH).astype(np.float32)
    diag = (_px + _py * 0.55)
    span = POUCH.size[0] + POUCH.size[1] * 0.55
    c = -200 + p * (span + 400)
    band = np.exp(-((diag - c) / 90.0) ** 2) * 0.55
    m = np.zeros_like(_pa)
    m[POUCH_PAD:POUCH_PAD + POUCH_SZ[1], POUCH_PAD:POUCH_PAD + POUCH_SZ[0]] = _pmask
    band *= m
    arr[..., :3] = arr[..., :3] + (255 - arr[..., :3]) * band[..., None]
    return Image.fromarray(arr.astype(np.uint8))


def radial(cx, cy, rx, ry, power=2.0):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
    return np.clip(1 - d, 0, 1) ** power


def scrim(side):
    """soft white light pool behind text, returned as float alpha map"""
    if side == 'left':
        g = radial(330, 820, 1150, 520, 1.25)
    elif side == 'right':
        g = radial(W - 330, 820, 1150, 520, 1.25)
    else:
        g = radial(W / 2, H / 2, 1300, 700, 1.1)
    return np.clip(g * 1.25, 0, 0.86)

SCRIM = {'left': scrim('left'), 'right': scrim('right'), 'center': scrim('center')}
GLOW = radial(W * 0.62, H * 0.38, 1400, 900, 1.6)


def end_background():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    t = np.clip((x / W) * 0.55 + (y / H) * 0.45, 0, 1)[..., None]
    c0 = np.array([250, 248, 253], np.float32)
    c1 = np.array([226, 216, 242], np.float32)
    bg = c0 * (1 - t) + c1 * t
    bg += radial(W * 0.5, H * 0.45, 900, 600, 1.5)[..., None] * 10
    return np.clip(bg, 0, 255)

END_BG = end_background()


def orb_sprite(r, color, alpha):
    s = r * 4
    im = Image.new('RGBA', (s, s), color + (0,))
    a = Image.new('L', (s, s), 0)
    ImageDraw.Draw(a).ellipse((r, r, 3 * r, 3 * r), fill=int(255 * alpha))
    im.putalpha(a.filter(ImageFilter.GaussianBlur(r * 0.45)))
    return im

ORBS = [(orb_sprite(160, LAV, .35), 0.18, 0.30, 0.020, 0.0),
        (orb_sprite(220, (225, 210, 245), .45), 0.78, 0.72, -0.015, 1.3),
        (orb_sprite(110, PURPLE, .12), 0.70, 0.22, 0.018, 2.1),
        (orb_sprite(90, LAV, .30), 0.30, 0.80, -0.02, 3.3)]


# ---------------------------------------------------------------- shots
class Shot:
    def __init__(self, clip, ss, speed, dur, z0, z1, c0, c1, kind='video'):
        self.clip, self.ss, self.speed, self.dur = clip, ss, speed, dur
        self.z0, self.z1, self.c0, self.c1 = z0, z1, c0, c1
        self.kind = kind
        self.proc = None
        self.idx = -1
        self.last = None
        self.start = 0

    def open(self):
        if self.clip is None:
            return
        need = self.dur * self.speed + 0.6
        cmd = ['ffmpeg', '-v', 'error', '-ss', f'{self.ss:.3f}', '-t', f'{need:.3f}',
               '-i', os.path.join(CLIPS, f'c{self.clip}.mp4'), '-an',
               '-filter_complex',
               f'[0:v]setpts=(PTS-STARTPTS)/{self.speed},fps={FPS},scale={W}:{H},{GRADE},format=rgb24',
               '-f', 'rawvideo', '-']
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=W * H * 3 * 2)

    def close(self):
        if self.proc:
            self.proc.stdout.close(); self.proc.kill(); self.proc.wait(); self.proc = None

    def raw(self, i):
        if self.proc is None:
            self.open()
        while self.idx < i:
            buf = self.proc.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:
                break
            self.last = Image.frombuffer('RGB', (W, H), buf, 'raw', 'RGB', 0, 1)
            self.idx += 1
        return self.last

    def frame(self, lt):
        """lt = local time in seconds -> PIL RGB 1920x1080 (Ken Burns applied)"""
        i = max(0, int(round(lt * FPS)))
        img = self.raw(i)
        p = ease_io(lt / self.dur)
        z = self.z0 + (self.z1 - self.z0) * p
        cx = self.c0[0] + (self.c1[0] - self.c0[0]) * p
        cy = self.c0[1] + (self.c1[1] - self.c0[1]) * p
        bw, bh = W / z, H / z
        x0 = clamp(cx * W - bw / 2, 0, W - bw)
        y0 = clamp(cy * H - bh / 2, 0, H - bh)
        return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + bw, y0 + bh))


SHOTS = [
    Shot('01', 0.0, .85, 8.4, 1.04, 1.14, (.52, .58), (.55, .60)),  # 0 intro + production line
    Shot('06', 0.5, 1.0, 4.0, 1.05, 1.12, (.50, .50), (.55, .50)),  # 1 dual function
    Shot('02', 0.4, .80, 4.2, 1.04, 1.10, (.45, .50), (.50, .50)),  # 2 actives data
    Shot('07', 0.0, .90, 4.0, 1.05, 1.12, (.50, .50), (.52, .50)),  # 3 ferment
    Shot('08', 0.25, .50, 4.0, 1.10, 1.20, (.56, .45), (.58, .50)), # 4 filling
    Shot('04', 1.2, 1.0, 3.8, 1.05, 1.12, (.60, .50), (.62, .50)),  # 5 sheet into pouch
    Shot('05', 1.0, 1.0, 3.8, 1.03, 1.10, (.45, .50), (.50, .55)),  # 6 sealing
    Shot('09', 1.3, .50, 3.4, 1.06, 1.14, (.50, .50), (.55, .50)),  # 7 seal close-up
    Shot('03', 0.3, 1.0, 3.8, 1.05, 1.13, (.50, .50), (.45, .55)),  # 8 batch coding
    Shot('14', 0.5, 1.0, 3.8, 1.20, 1.26, (.60, .40), (.62, .38)),  # 9 inspection
    Shot('15', 0.3, .80, 3.4, 1.05, 1.12, (.55, .50), (.60, .48)),  # 10 hands
    Shot('06', 6.0, .70, 8.6, 1.10, 1.16, (.50, .50), (.55, .50), 'product'),  # 11
    Shot('05', 8.5, .90, 4.8, 1.05, 1.10, (.50, .50), (.50, .52), 'quality'),  # 12
    Shot(None, 0, 1, 4.8, 1, 1, (.5, .5), (.5, .5), 'end'),                    # 13
]
# transition into shot i+1: (type, duration)
TRANS = [('zoom', .6), ('dissolve', .5), ('whip', .45), ('flash', .6), ('dissolve', .5),
         ('whip', .45), ('zoom', .55), ('flash', .6), ('whip', .45), ('dissolve', .5),
         ('flash', .7), ('dissolve', .6), ('flash', .7)]

t = 0.0
for i, s in enumerate(SHOTS):
    s.start = t
    if i < len(TRANS):
        t = s.start + s.dur - TRANS[i][1]
TOTAL = SHOTS[-1].start + SHOTS[-1].dur
NFRAMES = int(round(TOTAL * FPS))


# ---------------------------------------------------------------- shot post-processing
def soft_blur(img, r):
    if r < 0.3:
        return img
    small = img.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(r / 4))
    return small.resize((W, H), Image.BICUBIC)


def wash(img, color, a):
    arr = np.asarray(img).astype(np.float32)
    arr = arr * (1 - a) + np.array(color, np.float32) * a
    return Image.fromarray(arr.astype(np.uint8))


def shot_image(i, lt):
    s = SHOTS[i]
    if s.kind == 'end':
        return Image.fromarray(END_BG.astype(np.uint8))
    img = s.frame(lt)
    if i == 0:
        # dreamy intro, then a focus pull into the facility
        p = ease_io((lt - 2.9) / 1.2)
        img = soft_blur(img, 26 * (1 - p))
        img = wash(img, (247, 244, 251), 0.62 * (1 - p))
    elif s.kind == 'product':
        img = soft_blur(img, 22)
        img = wash(img, (247, 244, 251), 0.70)
    elif s.kind == 'quality':
        img = soft_blur(img, 5)
        img = wash(img, (247, 244, 251), 0.45)
    return img


# ---------------------------------------------------------------- transitions
def zoom_img(img, z):
    bw, bh = W / z, H / z
    x0, y0 = (W - bw) / 2, (H - bh) / 2
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + bw, y0 + bh))


def hsmear(img, k):
    if k < 1.5:
        return img
    return img.resize((max(8, int(W / k)), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)


def transition(kind, a, b, p):
    e = ease_io(p)
    if kind == 'dissolve':
        return Image.blend(a, b, e)
    if kind == 'flash':
        out = np.asarray(Image.blend(a, b, e)).astype(np.float32) / 255
        g = (GLOW * 0.85 * math.sin(math.pi * p) ** 1.5)[..., None]
        col = np.array([1.0, 0.97, 1.0], np.float32)
        out = 1 - (1 - out) * (1 - g * col)
        return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
    if kind == 'zoom':
        za = zoom_img(a, 1 + 0.35 * e)
        zb = zoom_img(b, 1.25 - 0.25 * e)
        bl = 18 * math.sin(math.pi * p)
        return Image.blend(soft_blur(za, bl), soft_blur(zb, bl), clamp((p - .25) / .5))
    if kind == 'whip':
        k = 1 + 40 * math.sin(math.pi * p)
        shift = int(W * 0.5 * e)
        ca = Image.new('RGB', (W, H)); ca.paste(a, (-shift, 0)); ca.paste(a.transpose(Image.FLIP_LEFT_RIGHT), (W - shift, 0))
        cb = Image.new('RGB', (W, H)); cb.paste(b, (W // 2 - shift, 0)); cb.paste(b.transpose(Image.FLIP_LEFT_RIGHT), (W // 2 - shift - W, 0))
        mix = Image.blend(hsmear(ca, k), hsmear(cb, k), clamp((p - .3) / .4))
        return mix
    raise ValueError(kind)


# ---------------------------------------------------------------- overlay elements
ELEMS = []   # each: fn(layer, t) ; scrims: list of (side, t0, t1)
SCRIMS = []


def chapter(shot, num, label, head, sub=None, side='left', head2=None):
    s = SHOTS[shot]
    t0 = s.start + (0.55 if shot else 4.3)
    t1 = s.start + s.dur - (TRANS[shot][1] if shot < len(TRANS) else 0) - 0.05
    SCRIMS.append((side, t0 - 0.3, t1 + 0.1))
    lab = text_sprite(label, EN_M, 21, PURPLE, tracking=7)
    numi = text_sprite(num, EN_XL, 58, PURPLE) if num else None
    hd = text_sprite(head, KR, 64, DEEP, tracking=1)
    hd2 = text_sprite(head2, KR, 64, DEEP, tracking=1) if head2 else None
    sb = text_sprite(sub, KR, 30, INK, tracking=0.5) if sub else None
    ytop = 700 if not hd2 else 640
    right = side == 'right'

    def xpos(w):
        return W - 130 - w if right else 130

    def fn(layer, t):
        if t < t0 - 0.05 or t > t1 + 0.05:
            return
        out = clamp((t1 - t) / 0.45)
        fa = ease_out(out)
        lt = t - t0
        y = ytop
        # label row: number + line + label
        rowh = 64
        line_len = 70 * ease_out(lt / 0.7)
        if numi:
            nw = numi.size[0]
            x = xpos(nw + 26 + 70 + 22 + lab.size[0])
            paste(layer, numi, x, y - 12, ease_out(lt / 0.6) * fa)
            lx = x + nw + 22
        else:
            x = xpos(70 + 22 + lab.size[0])
            lx = x
        ImageDraw.Draw(layer).line([(lx, y + 30), (lx + line_len, y + 30)], fill=PURPLE + (int(255 * fa),), width=2)
        paste(layer, wipe(lab, ease_out((lt - .15) / .8)), lx + 70 + 22, y + 17, fa)
        y += rowh + 6
        paste_rise(layer, hd, xpos(hd.size[0]), y, (lt - .25) / .75, fa)
        y += hd.size[1] - 2
        if hd2:
            paste_rise(layer, hd2, xpos(hd2.size[0]), y, (lt - .4) / .75, fa)
            y += hd2.size[1] - 2
        if sb:
            p = ease_out((lt - .6) / .7)
            paste(layer, sb, xpos(sb.size[0]), y + 14 + 14 * (1 - p), p * fa)
    ELEMS.append(fn)


# --- intro logo lockup (over blurred facility)
def intro(layer, t):
    if t > 3.7:
        return
    out = ease_io((t - 2.8) / 0.8)
    a_out = 1 - out
    sc = 1 + 0.05 * out
    # emblem
    p = ease_out((t - 0.25) / 1.1)
    em = EMBLEM
    if abs(sc - 1) > 1e-3 or p < 1:
        z = (0.94 + 0.06 * p) * sc
        em = EMBLEM.resize((int(EMBLEM.size[0] * z), int(EMBLEM.size[1] * z)), Image.BICUBIC)
    cy = 330
    paste(layer, em, W / 2 - em.size[0] / 2, cy - em.size[1] / 2 + 10 * (1 - p), p * a_out)
    # wordmark wipes in
    p2 = ease_out((t - 0.85) / 1.1)
    paste(layer, wipe(WORDMARK, p2, soft=120), W / 2 - WORDMARK.size[0] / 2, 545, a_out)
    # korean name rises
    p3 = (t - 1.35) / .8
    paste_rise(layer, KNAME, W / 2 - KNAME.size[0] / 2, 712, p3, a_out)
    # tagline
    tg = text_sprite('미백 · 주름개선 2중 기능성 화장품', KR, 30, INK, tracking=1)
    p4 = ease_out((t - 1.7) / .8)
    paste(layer, tg, W / 2 - tg.size[0] / 2, 790 + 10 * (1 - p4), p4 * a_out)
ELEMS.append(intro)


# --- actives data (shot 2): frosted glass card on the right
CARDS = []   # (x0, y0, x1, y1, t0, t1) frosted panels, applied on the base frame


def actives(layer, t):
    s = SHOTS[2]
    t0, t1 = s.start + .5, s.start + s.dur - TRANS[2][1] - .05
    if t < t0 - .05 or t > t1 + .05:
        return
    fa = ease_out(clamp((t1 - t) / .45))
    lt = t - t0
    x = 1250
    lab = text_sprite('KEY ACTIVES', EN_M, 21, PURPLE, tracking=7)
    d = ImageDraw.Draw(layer)
    d.line([(x, 262), (x + 70 * ease_out(lt / .7), 262)], fill=PURPLE + (int(255 * fa),), width=2)
    paste(layer, wipe(lab, ease_out((lt - .1) / .8)), x + 92, 249, fa)
    rows = [(2.0, '{:.0f}%', '나이아신아마이드', '피부 미백에 도움', 'BRIGHTENING', 0.2),
            (0.04, '{:.2f}%', '아데노신', '피부 주름개선에 도움', 'WRINKLE CARE', 0.6)]
    y = 300
    for val, fmt, kr, desc, en, dl in rows:
        p = ease_out((lt - dl) / .9)
        off = 18 * (1 - p)
        cnt = val * ease_out_expo((lt - dl) / 1.3)
        num = text_sprite(fmt.format(cnt), EN_T, 120, DEEP)
        paste(layer, num, x - 8, y + off, p * fa)
        e = text_sprite(en, EN_M, 16, PURPLE, tracking=4)
        paste(layer, e, x + 2, y + 150 + off, p * fa)
        k = text_sprite(kr, KR, 38, DEEP, tracking=1)
        paste(layer, k, x, y + 176 + off, p * fa)
        de = text_sprite(desc, KR, 24, INK, tracking=.5)
        paste(layer, de, x + 2, y + 228 + off, p * fa)
        y += 300
        if dl < .5:
            d.line([(x, y - 26), (x + 470 * ease_out((lt - .5) / .8), y - 26)], fill=LAV + (int(230 * fa),), width=1)
ELEMS.append(actives)
CARDS.append((1180, 210, 1790, 900, SHOTS[2].start + .25, SHOTS[2].start + SHOTS[2].dur - TRANS[2][1] + .05))


# --- 23ml counter on filling
def ml_counter(layer, t):
    s = SHOTS[4]
    t0, t1 = s.start + .55, s.start + s.dur - TRANS[4][1] - .05
    if t < t0 or t > t1 + .05:
        return
    fa = ease_out(clamp((t1 - t) / .45))
    lt = t - t0
    v = 23 * ease_out_expo((lt - .3) / 1.6)
    num = text_sprite(f'{v:.0f}', EN_T, 150, DEEP)
    unit = text_sprite('ml', EN_L, 46, PURPLE)
    p = ease_out((lt - .3) / .8)
    paste(layer, num, 130, 470 + 20 * (1 - p), p * fa)
    paste(layer, unit, 130 + num.size[0] + 4, 470 + 92 + 20 * (1 - p), p * fa)
ELEMS.append(ml_counter)


# --- product section
PRODUCT_ROWS = [
    ('2%', '나이아신아마이드', '피부 미백에 도움'),
    ('0.04%', '아데노신', '피부 주름개선에 도움'),
    ('4종', '히알루론산', '촉촉한 수분 공급'),
    ('7종', '발효 성분', '유산균 발효 PDRN · 쌀 · 인삼 발효'),
]


def product(layer, t):
    s = SHOTS[11]
    t0 = s.start + .35
    t1 = s.start + s.dur - TRANS[11][1] - .05
    if t < t0 - .05 or t > t1 + .1:
        return
    fa = ease_out(clamp((t1 - t) / .5))
    lt = t - t0
    # pouch
    p = ease_out((lt) / 1.2)
    sheen = clamp((lt - 1.6) / 1.4)
    img = pouch_with_sheen(sheen) if 0 < sheen < 1 else POUCH
    fl = 6 * math.sin(lt * 1.3)
    px = 560 - img.size[0] / 2 - 60 * (1 - p)
    py = H / 2 - img.size[1] / 2 + 10 + fl
    paste(layer, img, px, py, p * fa)
    badge = text_sprite('PREMIUM TENCEL SHEET  ·  23ml', EN_M, 18, PURPLE, tracking=4)
    pb = ease_out((lt - 1.0) / .8)
    paste(layer, badge, 560 - badge.size[0] / 2, 985, pb * fa)
    # header
    x = 1010
    lab = text_sprite('KEY INGREDIENTS', EN_M, 21, PURPLE, tracking=7)
    d = ImageDraw.Draw(layer)
    d.line([(x, 196), (x + 70 * ease_out((lt - .3) / .7), 196)], fill=PURPLE + (int(255 * fa),), width=2)
    paste(layer, wipe(lab, ease_out((lt - .4) / .8)), x + 92, 183, fa)
    hd = text_sprite('한 장에 담은 핵심 성분', KR, 58, DEEP, tracking=1)
    paste_rise(layer, hd, x, 228, (lt - .55) / .8, fa)
    y = 360
    for k, (val, name, desc) in enumerate(PRODUCT_ROWS):
        dl = 1.0 + k * .38
        pr = ease_out((lt - dl) / .8)
        v = text_sprite(val, EN_XL if val[-1] == '%' else KR, 62 if val[-1] == '%' else 50, PURPLE)
        nm = text_sprite(name, KR, 36, DEEP, tracking=1)
        ds = text_sprite(desc, KR, 24, INK, tracking=.5)
        off = 24 * (1 - pr)
        paste(layer, v, x + off, y + (0 if val[-1] == '%' else 8), pr * fa)
        paste(layer, nm, x + 230 + off, y + 2, pr * fa)
        paste(layer, ds, x + 232 + off, y + 52, pr * fa)
        d.line([(x, y + 112), (x + 760 * ease_out((lt - dl - .1) / .9), y + 112)], fill=LAV + (int(220 * fa * pr),), width=1)
        y += 140
ELEMS.append(product)


# --- quality section
def quality(layer, t):
    s = SHOTS[12]
    t0 = s.start + .45
    t1 = s.start + s.dur - TRANS[12][1] - .05
    if t < t0 - .05 or t > t1 + .1:
        return
    fa = ease_out(clamp((t1 - t) / .5))
    lt = t - t0
    lab = text_sprite('QUALITY TESTED', EN_M, 21, PURPLE, tracking=7)
    d = ImageDraw.Draw(layer)
    cx = W / 2
    lw = 70 * ease_out(lt / .7)
    d.line([(cx - lab.size[0] / 2 - 30 - lw, 268), (cx - lab.size[0] / 2 - 30, 268)], fill=PURPLE + (int(255 * fa),), width=2)
    d.line([(cx + lab.size[0] / 2 + 30, 268), (cx + lab.size[0] / 2 + 30 + lw, 268)], fill=PURPLE + (int(255 * fa),), width=2)
    paste(layer, wipe(lab, ease_out((lt - .1) / .8)), cx - lab.size[0] / 2, 255, fa)
    hd = text_sprite('믿을 수 있는 품질, 꼼꼼한 검사', KR, 58, DEEP, tracking=1)
    paste_rise(layer, hd, cx - hd.size[0] / 2, 300, (lt - .25) / .8, fa)
    cols = [('HEAVY METALS', '중금속 4종', '불검출'),
            ('MICROBIAL TEST', '미생물', '불검출'),
            ('FREE FROM', '파라벤 · 페녹시에탄올', '무첨가')]
    cw = 520
    for k, (en, kr, res) in enumerate(cols):
        dl = .7 + k * .3
        pr = ease_out((lt - dl) / .8)
        ccx = cx + (k - 1) * cw
        e = text_sprite(en, EN_M, 17, PURPLE, tracking=5)
        a_ = text_sprite(kr, KR, 32, INK, tracking=.5)
        r = text_sprite(res, KR, 64, DEEP, tracking=2)
        off = 20 * (1 - pr)
        paste(layer, e, ccx - e.size[0] / 2, 500 + off, pr * fa)
        paste(layer, r, ccx - r.size[0] / 2, 540 + off, pr * fa)
        paste(layer, a_, ccx - a_.size[0] / 2, 632 + off, pr * fa)
        if k:
            d.line([(ccx - cw / 2, 510), (ccx - cw / 2, 510 + 160 * pr)], fill=LAV + (int(230 * fa),), width=1)
    fn = text_sprite('* 자사 품질 시험성적서 기준', KR, 20, INK)
    paste(layer, fn, cx - fn.size[0] / 2, 800, ease_out((lt - 1.6) / .8) * fa * .85)
ELEMS.append(quality)
SCRIMS.append(('center', SHOTS[12].start + .1, SHOTS[12].start + SHOTS[12].dur - .3))


# --- end card
def endcard(layer, t):
    s = SHOTS[13]
    lt = t - s.start
    if lt < 0:
        return
    for im, ox, oy, sp, ph in ORBS:
        x = ox * W + math.sin(lt * .6 + ph) * 40 + sp * lt * W
        y = oy * H + math.cos(lt * .5 + ph) * 30
        paste(layer, im, x - im.size[0] / 2, y - im.size[1] / 2, clamp(lt / .6))
    p = ease_out((lt - .25) / 1.1)
    z = 0.94 + 0.06 * p
    em = EMBLEM_S.resize((int(EMBLEM_S.size[0] * z), int(EMBLEM_S.size[1] * z)), Image.BICUBIC)
    paste(layer, em, W / 2 - em.size[0] / 2, 250 - em.size[1] / 2 + 12 * (1 - p), p)
    paste(layer, wipe(WORDMARK_S, ease_out((lt - .7) / 1.1), soft=120), W / 2 - WORDMARK_S.size[0] / 2, 400)
    paste_rise(layer, KNAME, W / 2 - KNAME.size[0] / 2, 528, (lt - 1.1) / .8)
    tg = text_sprite('피부 미백 · 주름개선 2중 기능성 화장품', KR, 32, INK, tracking=1)
    pt = ease_out((lt - 1.4) / .8)
    paste(layer, tg, W / 2 - tg.size[0] / 2, 610 + 10 * (1 - pt), pt)
    chips = ['23ml', 'TENCEL SHEET', 'MADE IN KOREA']
    d = ImageDraw.Draw(layer)
    sprites = [text_sprite(c, EN_M, 18, PURPLE, tracking=4) for c in chips]
    gap = 26
    tw = sum(sp.size[0] + 44 for sp in sprites) + gap * (len(sprites) - 1)
    x = W / 2 - tw / 2
    for k, sp in enumerate(sprites):
        pc = ease_out((lt - 1.75 - k * .15) / .7)
        bw = sp.size[0] + 44
        d.rounded_rectangle([x, 700, x + bw, 744], radius=22, outline=PURPLE + (int(170 * pc),), width=1)
        paste(layer, sp, x + 22, 708, pc)
        x += bw + gap
    by = text_sprite('BTGin  ·  www.acenadi.com', EN_L, 20, INK, tracking=3)
    paste(layer, by, W / 2 - by.size[0] / 2, 960, ease_out((lt - 2.2) / .8) * .8)
ELEMS.append(endcard)


# --- chapters
chapter(0, None, 'MADE IN SEJONG, KOREA', '배합부터 검수까지,', '세종 BTGin 자체 제조시설', head2='직접 만듭니다')
chapter(1, None, 'DUAL FUNCTION', '2중 기능성 포뮬러', '피부 미백 · 주름개선에 도움을 주는 기능성 화장품')
chapter(3, None, 'BIO-FERMENT COMPLEX', '7종 발효 성분', '유산균 발효 PDRN · 쌀 발효 · 인삼 발효')
chapter(4, '01', 'FILLING', '1매 23ml 에센스', '시트 가득 넉넉하게 담았습니다')
chapter(5, None, 'PREMIUM TENCEL SHEET', '부드럽게 밀착되는', '얼굴에 촘촘하게 감기는 텐셀 시트', head2='텐셀 시트')
chapter(6, '02', 'SEALING', '정밀 실링', '에센스의 신선함을 그대로')
chapter(8, '03', 'TRACEABILITY', '제조번호 개별 인쇄', '모든 제품의 생산 이력을 관리합니다', side='right')
chapter(9, '04', 'INSPECTION', '한 장 한 장,', '꼼꼼한 검수를 거쳐 출고됩니다', head2='직접 검수합니다')

# the 23ml chapter already shows the counter: move its head lower via spacing hack
# (counter sits at y 470..620, chapter block starts at 700)


@functools.lru_cache(None)
def card_mask(w, h, r=28):
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    return m


def glass(base, box, a):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    reg = base.crop(box)
    bl = reg.resize((w // 6, h // 6), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5)).resize((w, h), Image.BICUBIC)
    bl = wash(bl, (250, 248, 253), 0.74)
    m = card_mask(w, h).point(lambda v: int(v * a))
    out = base.copy()
    out.paste(bl, (x0, y0), m)
    d = ImageDraw.Draw(out, 'RGBA')
    d.rounded_rectangle([x0, y0, x1 - 1, y1 - 1], radius=28, outline=(255, 255, 255, int(200 * a)), width=2)
    return out


# ---------------------------------------------------------------- render
def compose(fi):
    t = fi / FPS
    # base frame
    act = [i for i, s in enumerate(SHOTS) if s.start <= t < s.start + s.dur]
    if not act:
        act = [len(SHOTS) - 1]
    if len(act) == 1:
        i = act[0]
        base = shot_image(i, t - SHOTS[i].start)
    else:
        i, j = act[0], act[1]
        kind, td = TRANS[i]
        p = (t - SHOTS[j].start) / td
        base = transition(kind, shot_image(i, t - SHOTS[i].start), shot_image(j, t - SHOTS[j].start), p)
    # scrims
    arr = None
    for side, s0, s1 in SCRIMS:
        if s0 <= t <= s1:
            a = ease_io((t - s0) / .5) * ease_io((s1 - t) / .5)
            if a > 0.002:
                if arr is None:
                    arr = np.asarray(base).astype(np.float32)
                m = SCRIM[side][..., None] * a
                arr = arr * (1 - m) + np.array([250, 248, 253], np.float32) * m
    if arr is not None:
        base = Image.fromarray(arr.astype(np.uint8))
    for (x0, y0, x1, y1, c0, c1) in CARDS:
        if c0 <= t <= c1:
            a = ease_io((t - c0) / .45) * ease_io((c1 - t) / .4)
            base = glass(base, (x0, y0, x1, y1), a)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for fn in ELEMS:
        fn(layer, t)
    out = base.convert('RGBA')
    out.alpha_composite(layer)
    # close shots no longer needed
    for k, s in enumerate(SHOTS):
        if s.proc and t > s.start + s.dur + .1:
            s.close()
    return out.convert('RGB')


def main():
    args = sys.argv[1:]
    if args and args[0] == 'stills':
        os.makedirs(os.path.join(BASE, 'stills'), exist_ok=True)
        for ts in [float(x) for x in args[1:]]:
            for s in SHOTS:
                s.close(); s.idx = -1
            img = compose(int(ts * FPS))
            img.resize((960, 540), Image.LANCZOS).save(os.path.join(BASE, 'stills', f's_{ts:05.1f}.jpg'), quality=88)
        return
    out = os.path.join(BASE, 'video_noaudio.mp4')
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                            '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                            '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for fi in range(NFRAMES):
        enc.stdin.write(compose(fi).tobytes())
        if fi % 150 == 0:
            print(f'{fi}/{NFRAMES}', flush=True)
    enc.stdin.close(); enc.wait()
    print('TOTAL', TOTAL)


if __name__ == '__main__':
    print('total seconds', round(TOTAL, 2), 'frames', NFRAMES)
    for i, s in enumerate(SHOTS):
        print(i, s.clip, round(s.start, 2), round(s.start + s.dur, 2))
    main()
