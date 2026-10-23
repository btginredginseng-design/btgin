"""GinHongsam Daily Balance - production film renderer.

Usage:
  python3 render.py preview f1 f2 ...   -> PNG stills of given global frames
  python3 render.py video  OUT.mp4      -> silent video (audio built by sfx.py)
"""
import subprocess, sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

U = "/root/.claude/uploads/25c59277-18aa-55ab-9218-a328aca5ae4b"
SRC = [f"{U}/94fd8a47-part_1.mp4", f"{U}/f59f0fa4-Part_2.mp4"]
HERE = os.path.dirname(os.path.abspath(__file__))
GRADE = open(os.path.join(HERE, "grade.txt")).read().strip()

W, H, FPS = 1920, 1080, 30
SW, SH = 2560, 1440
PRE = 75                      # pre-roll frames
NF = 469 + 480                # footage frames
DET = 195                     # product details card
FIN = 150                     # final card
F0 = PRE                      # first footage frame (global)
FEND = PRE + NF               # first frame after footage
TOTAL = FEND + DET + FIN

# palette
CREAM = (244, 235, 221)
GOLD = (214, 166, 92)
RED = (176, 28, 36)
INK = (14, 12, 11)

FD = "/usr/share/fonts/opentype/inter/"
KO = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

# --- shots (footage frame start, x0, x1 of real content, mode, vertical anchor, zoom dir)
SHOTS = [
    (0,   0, 2560, "cover", .5,  1),   # A wide line
    (30,  0, 2290, "cover", .5, -1),   # B filler
    (61,  0, 2560, "cover", .5,  1),   # C filling nozzles
    (98,  0, 1338, "panel", .5,  1),   # D
    (142, 0, 2099, "cover", .55, -1),  # E pouches on belt
    (179, 254, 2560, "cover", .4, 1),  # F weight screen
    (208, 0, 1842, "cover", .55, -1),  # G hand weighing
    (256, 1213, 2560, "panel", .5, 1), # H clean-room conveyor
    (289, 0, 1013, "panel", .5, 1),    # I sterilizer
    (322, 0, 2560, "cover", .5, -1),   # J water bath
    (356, 0, 2560, "cover", .5, 1),    # K dryer
    (389, 0, 1283, "panel", .5, 1),    # L belt
    (432, 578, 2560, "cover", .45, -1),# M boxing pouches
    (469, 745, 2560, "cover", .4, 1),  # N workers
    (504, 0, 2560, "cover", .5, -1),   # O boxes on line
    (581, 0, 2560, "cover", .5, 1),    # P box on scale
    (632, 832, 2560, "panel", .5, 1),  # Q coder
    (670, 0, 2560, "cover", .5, -1),   # R coder line
    (702, 761, 2560, "cover", .45, 1), # S worker room
    (741, 127, 2560, "cover", .5, -1), # T packing carton
    (836, 0, 2560, "cover", .5, 1),    # U taping
    (882, 0, 2560, "cover", .5, -1),   # V palletizing
]
SHOT_END = [s[0] for s in SHOTS[1:]] + [NF]

SECTIONS = [  # footage start, end, num, label, headline, sub
    (98, 179, "01", "FILLING & SEALING", "50 mL in every pouch", "Filled and sealed on our automated line."),
    (179, 256, "02", "QUALITY CHECK", "Weight-checked on the line", "Consistent pouches, batch after batch."),
    (256, 356, "03", "STERILIZATION", "Sterilized after sealing", "Sealed pouches go through post-sterilization."),
    (356, 504, "04", "INSPECTION", "Checked by hand", "Our team inspects pouches before boxing."),
    (504, 702, "05", "PACKAGING", "30 pouches. One box.", "Each box is weighed and batch-coded."),
    (702, NF, "06", "READY TO SHIP", "Made in Korea", "Packed and palletized at BTGin, Daejeon."),
]
SECTION_CUTS = {s[0] for s in SECTIONS}
CUTS = [s[0] for s in SHOTS[1:]]
FLASH_CUTS = {322, 469, 882}


def cut_type(c):
    if c in SECTION_CUTS:
        return "whip"
    if c in FLASH_CUTS:
        return "flash"
    return "zoom"


# ---------------- helpers
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def eo(t):  # ease out cubic
    t = clamp(t); return 1 - (1 - t) ** 3


def ei(t):
    t = clamp(t); return t ** 3


def eio(t):
    t = clamp(t); return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2


_fonts = {}


def font(name, size):
    k = (name, size)
    if k not in _fonts:
        path = KO if name == "ko" else FD + name + ".otf"
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]


_txt = {}


def text_img(text, fname, size, color, tracking=0.0, alpha=255):
    k = (text, fname, size, color, tracking, alpha)
    if k in _txt:
        return _txt[k]
    f = font(fname, size)
    asc, desc = f.getmetrics()
    pad = int(size * .25)
    if tracking:
        widths = [f.getlength(ch) for ch in text]
        tw = sum(widths) + tracking * size * (len(text) - 1)
    else:
        tw = f.getlength(text)
    im = Image.new("RGBA", (int(tw) + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tracking:
        x = pad
        for ch, w in zip(text, widths):
            d.text((x, pad), ch, font=f, fill=color + (alpha,))
            x += w + tracking * size
    else:
        d.text((pad, pad), text, font=f, fill=color + (alpha,))
    im._pad = pad
    _txt[k] = im
    return im


def with_alpha(im, a):
    if a >= .999:
        return im
    arr = np.array(im)
    arr[..., 3] = (arr[..., 3].astype(np.float32) * a).astype(np.uint8)
    return Image.fromarray(arr)


def put(frame, im, x, y, a=1.0, reveal=1.0, anchor="l"):
    """Composite text image. reveal<1 slides it up inside its own box (mask reveal)."""
    if a <= 0.003 or reveal <= 0.003:
        return
    pad = getattr(im, "_pad", 0)
    w, h = im.size
    if anchor == "c":
        x = x - w / 2 + pad
    x, y = int(x - pad), int(y - pad)
    dy = int((1 - reveal) * h * .85)
    if dy:
        im = im.crop((0, 0, w, h - dy))
        y += dy
    im = with_alpha(im, a)
    frame.alpha_composite(im, (max(x, 0), max(y, 0)))


def line(frame, x, y, length, a=1.0, color=GOLD, thick=2, vertical=False):
    if length < 1 or a <= 0:
        return
    d = ImageDraw.Draw(frame)
    c = color + (int(255 * a),)
    if vertical:
        d.rectangle([x, y, x + thick - 1, y + length], fill=c)
    else:
        d.rectangle([x, y, x + length, y + thick - 1], fill=c)


def anim(f, t_in, t_out=None, din=14, dout=10):
    """returns (reveal, alpha, exit_dy)"""
    pin = eo((f - t_in) / din)
    pout = ei((f - (t_out - dout)) / dout) if t_out is not None else 0
    return pin, pin * (1 - pout), -14 * pout


# ---------------- static overlays
def radial(w, h, cx, cy, r, color, amax):
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - cx) / r) ** 2 + ((yy - cy) / r) ** 2)
    a = np.exp(-(d * 1.9) ** 2) * amax
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., :3] = color
    arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr)


def grad_lowerleft():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a = np.clip((yy / H - .38) / .62, 0, 1) ** 1.4 * .82
    a *= np.clip(1.25 - xx / W, 0, 1) ** .8
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., :3] = (8, 6, 5)
    arr[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(arr)


def grad_left():
    xx = np.tile(np.arange(W, dtype=np.float32), (H, 1))
    a = np.clip(1 - xx / (W * .72), 0, 1) ** 1.3 * .85
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., :3] = (8, 6, 5)
    arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr)


def vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
    v = 1 - np.clip(d - .55, 0, 1) * .55
    return v[..., None].astype(np.float32)


GL = grad_lowerleft()
GLEFT = grad_left()
VIG = vignette()
DITHER = [np.random.uniform(-1.5, 1.5, (H, W, 1)).astype(np.float32) for _ in range(4)]
GLOW = radial(W, H, W / 2, H * .55, 900, (120, 70, 30), .55)
LEAK = radial(1400, 1400, 700, 700, 700, (255, 150, 60), 1.0)


# ---------------- footage
def footage_reader():
    cmd = ["ffmpeg", "-v", "error", "-i", SRC[0], "-i", SRC[1], "-filter_complex",
           f"[0:v][1:v]concat=n=2:v=1:a=0,{GRADE},format=rgb24[v]", "-map", "[v]",
           "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=SW * SH * 3 * 2)
    n = SW * SH * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield Image.frombuffer("RGB", (SW, SH), b, "raw", "RGB", 0, 1)


def footage_frame_seek(i):
    src, j = (SRC[0], i) if i < 469 else (SRC[1], i - 469)
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf",
                        f"select=eq(n\\,{j}),{GRADE},format=rgb24", "-frames:v", "1",
                        "-f", "rawvideo", "-"], capture_output=True).stdout
    return Image.frombuffer("RGB", (SW, SH), b, "raw", "RGB", 0, 1)


def shot_of(i):
    k = 0
    for n, s in enumerate(SHOTS):
        if s[0] <= i:
            k = n
    return k


def cover_box(x0, x1, anchor, z, drift):
    x0, x1 = x0 + 6 if x0 else 0, x1 - 6 if x1 < SW else SW
    cw, ch = x1 - x0, SH
    if cw / ch >= W / H:
        bw, bh = ch * W / H, ch
    else:
        bw, bh = cw, cw * H / W
    bw, bh = bw / z, bh / z
    cx = x0 + cw / 2 + drift * (cw - bw) * .5
    cy = anchor * SH
    cy = min(max(cy, bh / 2), SH - bh / 2)
    cx = min(max(cx, x0 + bw / 2), x1 - bw / 2)
    return (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)


_shadow = {}


def panel_shadow(w, h):
    if (w, h) not in _shadow:
        m = 60
        im = Image.new("RGBA", (w + m * 2, h + m * 2), (0, 0, 0, 0))
        ImageDraw.Draw(im).rectangle([m, m + 18, m + w, m + h + 18], fill=(0, 0, 0, 170))
        _shadow[(w, h)] = im.filter(ImageFilter.GaussianBlur(28))
    return _shadow[(w, h)]


def compose_shot(src, i):
    """Footage frame i (footage index) -> 1920x1080 RGB, reframed."""
    k = shot_of(i)
    s0, x0, x1, mode, anchor, zd = SHOTS[k]
    s1 = SHOT_END[k]
    t = (i - s0) / max(1, s1 - s0)
    z = 1.0 + .06 * (t if zd > 0 else 1 - t)
    if mode == "cover":
        box = cover_box(x0, x1, anchor, z, .25 * (t - .5) * zd)
        return src.resize((W, H), Image.BILINEAR, box=box)
    # panel layout
    bbox = cover_box(x0, x1, .5, 1.0, 0)
    bg = src.resize((480, 270), Image.BILINEAR, box=bbox).filter(ImageFilter.GaussianBlur(12))
    bg = bg.resize((W, H), Image.BICUBIC)
    bg = Image.fromarray((np.asarray(bg, np.float32) * .42).astype(np.uint8))
    xa, xb = (x0 + 6 if x0 else 0), (x1 - 6 if x1 < SW else SW)
    ph = min(860, int(880 * SH / (xb - xa)))
    pw = int(round((xb - xa) / SH * ph))
    zz = 1.0 + .05 * t
    cw, chh = (xb - xa) / zz, SH / zz
    cx, cy = (xa + xb) / 2, SH / 2
    fg = src.resize((pw, ph), Image.BILINEAR, box=(cx - cw / 2, cy - chh / 2, cx + cw / 2, cy + chh / 2))
    e = eo((i - s0) / 16)
    px = int(W - 130 - pw + (1 - e) * 90)
    py = int((H - ph) / 2)
    bg = bg.convert("RGBA")
    bg.alpha_composite(panel_shadow(pw, ph), (px - 60, py - 60))
    bg.paste(fg, (px, py))
    d = ImageDraw.Draw(bg)
    d.rectangle([px, py, px + pw - 1, py + ph - 1], outline=CREAM + (90,), width=1)
    L = int(46 * e)
    for (ax, ay, sx, sy) in [(px - 10, py - 10, 1, 1), (px + pw + 9, py + ph + 9, -1, -1)]:
        d.rectangle([min(ax, ax + sx * L), min(ay, ay + sy * 2), max(ax, ax + sx * L), max(ay, ay + sy * 2)], fill=GOLD + (255,))
        d.rectangle([min(ax, ax + sx * 2), min(ay, ay + sy * L), max(ax, ax + sx * 2), max(ay, ay + sy * L)], fill=GOLD + (255,))
    return bg.convert("RGB")


def zoom_img(im, s, blur=0):
    if s != 1.0:
        bw, bh = W / s, H / s
        im = im.resize((W, H), Image.BILINEAR, box=((W - bw) / 2, (H - bh) / 2, (W + bw) / 2, (H + bh) / 2))
    if blur > .5:
        im = im.filter(ImageFilter.BoxBlur(blur))
    return im


def hblur(im, k):
    if k <= 1.2:
        return im
    return im.resize((max(8, int(W / k)), H), Image.BILINEAR).resize((W, H), Image.BILINEAR)


def apply_transition(img, i):
    """img: composed footage frame at footage index i; returns transformed RGB."""
    T = 5
    for n, c in enumerate(CUTS):
        if c - T <= i < c + T:
            tp = cut_type(c)
            out = i < c
            u = (c - i) / T if out else (i - c + 1) / T  # 1 far .. ~0 at cut
            p = 1 - u  # 0 far .. 1 at cut
            if tp == "zoom":
                s = 1 + .14 * eio(p) if out else 1 + .14 * eio(p)
                img = zoom_img(img, s if out else s, blur=10 * p)
            elif tp == "whip":
                dirn = 1 if (n % 2 == 0) else -1
                shift = int(eio(p) * 420) * (-dirn if out else dirn)
                arr = np.roll(np.asarray(img), shift, axis=1)
                img = hblur(Image.fromarray(arr), 1 + 40 * p ** 1.5)
            elif tp == "flash":
                img = zoom_img(img, 1 + .05 * p, blur=4 * p)
                a = np.asarray(img, np.float32)
                w = p ** 2 * .85
                a = a * (1 - w) + np.array([255, 240, 220], np.float32) * w
                img = Image.fromarray(a.astype(np.uint8))
            if tp == "whip":
                # warm light leak sweeping across on section cuts
                lx = int(-700 + (W + 700) * ((i - (c - T)) / (2 * T)))
                lk = with_alpha(LEAK, .55 * math.sin(math.pi * clamp((i - (c - T)) / (2 * T))))
                base = img.convert("RGBA")
                layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                layer.alpha_composite(lk, (max(0, lx), 0)) if lx >= 0 else layer.alpha_composite(lk.crop((-lx, 0, 1400, 1400)), (0, 0))
                ba = np.asarray(base, np.float32)[..., :3]
                la = np.asarray(layer, np.float32)
                ba = ba + la[..., :3] * (la[..., 3:4] / 255) * .8
                img = Image.fromarray(np.clip(ba, 0, 255).astype(np.uint8))
            break
    return img


# ---------------- graphics per global frame
def hud(fr, g):
    i = g - F0
    a = eo((i - 92) / 15) * (1 - eo((i - (NF - 8)) / 8))
    if a <= 0:
        return
    put(fr, text_img("BTGin", "InterDisplay-SemiBold", 30, CREAM), 84, 60, a * .9)
    sec = next((s for s in SECTIONS if s[0] <= i < s[1]), None)
    if sec:
        put(fr, text_img(f"{sec[2]} / 06", "Inter-Medium", 18, CREAM, .22), W - 84 - 110, 66, a * .8)
    # progress line
    line(fr, 84, H - 52, W - 168, a * .25, CREAM, 1)
    line(fr, 84, H - 52, int((W - 168) * clamp(i / NF)), a * .9, GOLD, 1)


def section_text(fr, g):
    i = g - F0
    for s0, s1, num, lab, head, sub in SECTIONS:
        if s0 - 1 <= i < s1:
            f = i - s0
            dur = s1 - s0
            # darkening gradient
            ga = eo(f / 10) * (1 - ei((f - (dur - 8)) / 8))
            fr.alpha_composite(with_alpha(GL, ga))
            x, y = 120, 778
            r, a, dy = anim(f, 5, dur, 14, 9)
            put(fr, text_img(num, "InterDisplay-Medium", 24, GOLD, .1), x, y + dy, a, r)
            lp = eo((f - 8) / 14)
            line(fr, x + 46, y + 16 + dy, int(56 * lp), a)
            r, a, dy = anim(f, 10, dur, 14, 9)
            put(fr, text_img(lab, "Inter-SemiBold", 21, CREAM, .28), x + 118, y + 2 + dy, a * .9, r)
            r, a, dy = anim(f, 13, dur, 16, 9)
            put(fr, text_img(head, "InterDisplay-SemiBold", 66, CREAM), x - 3, y + 40 + dy, a, r)
            r, a, dy = anim(f, 18, dur, 16, 9)
            put(fr, text_img(sub, "Inter-Regular", 27, CREAM), x, y + 132 + dy, a * .78, r)


def preroll(fr, g):
    f = g
    fr.alpha_composite(with_alpha(GLOW, eo(f / 30) * (1 - ei((f - 60) / 15))))
    cx, cy = W / 2, H / 2
    out = ei((f - 58) / 16)
    lp = eio((f - 4) / 26)
    L = int(460 * lp)
    line(fr, int(cx - L / 2), int(cy + 10), L, 1 - out)
    r, a, dy = anim(f, 10, None, 22)
    tr = .18 - .12 * eo((f - 10) / 40)
    put(fr, text_img("BTGin", "InterDisplay-SemiBold", 108, CREAM, round(tr, 3)), cx, cy - 128 + dy, a * (1 - out), r, "c")
    r, a, dy = anim(f, 24, None, 20)
    put(fr, text_img("GINSENG & GINSENOSIDE FOR HUMAN HEALTH", "Inter-Medium", 20, GOLD, .32), cx, cy + 40, a * (1 - out), r, "c")


def title(fr, g):
    i = g - F0
    if i >= 98:
        return
    T_OUT = 98
    ga = eo(i / 12) * (1 - ei((i - 90) / 8))
    fr.alpha_composite(with_alpha(GLEFT, ga))
    x = 130
    r, a, dy = anim(i, 4, T_OUT, 16, 8)
    line(fr, x, 352, int(64 * eo((i - 4) / 16)), a)
    put(fr, text_img("KOREAN RED GINSENG BEVERAGE", "Inter-SemiBold", 21, GOLD, .3), x + 84, 338 + dy, a, r)
    r, a, dy = anim(i, 8, T_OUT, 18, 8)
    put(fr, text_img("GinHongsam", "InterDisplay-Light", 132, CREAM), x - 6, 382 + dy, a, r)
    r, a, dy = anim(i, 14, T_OUT, 18, 8)
    put(fr, text_img("Daily Balance", "InterDisplay-SemiBold", 132, CREAM), x - 6, 530 + dy, a, r)
    r, a, dy = anim(i, 24, T_OUT, 18, 8)
    put(fr, text_img("진홍삼데일리밸런스", "ko", 40, CREAM, .08), x, 712 + dy, a * .85, r)
    r, a, dy = anim(i, 32, T_OUT, 18, 8)
    put(fr, text_img("INSIDE OUR PRODUCTION LINE  ·  DAEJEON, KOREA", "Inter-Medium", 19, CREAM, .26), x, 790 + dy, a * .7, r)


DETAILS = [
    ("50 mL × 30", "pouches per box"),
    ("Korean red ginseng", "extract at the heart"),
    ("Jujube · Pear · Honey", "for a smooth, mellow taste"),
    ("Goji · Reishi · Ginger", "with hovenia & a herbal blend"),
    ("25 kcal", "per pouch"),
    ("Ready to drink", "store at room temperature"),
]


def details(fr, f):
    out = DET
    x0 = 150
    r, a, dy = anim(f, 14, out, 14, 12)
    line(fr, x0, 214 + dy, int(64 * eo((f - 14) / 16)), a)
    put(fr, text_img("THE PRODUCT", "Inter-SemiBold", 21, GOLD, .3), x0 + 84, 200 + dy, a, r)
    r, a, dy = anim(f, 18, out, 16, 12)
    put(fr, text_img("GinHongsam Daily Balance", "InterDisplay-SemiBold", 76, CREAM), x0 - 4, 240 + dy, a, r)
    r, a, dy = anim(f, 24, out, 16, 12)
    put(fr, text_img("진홍삼데일리밸런스  ·  Red Ginseng Beverage", "ko", 30, CREAM), x0, 346 + dy, a * .75, r)
    cw, chh, gx, gy = 500, 150, 70, 52
    for n, (big, small) in enumerate(DETAILS):
        cx = x0 + (n % 3) * (cw + gx)
        cy = 480 + (n // 3) * (chh + gy)
        t0 = 34 + n * 7
        r, a, dy = anim(f, t0, out, 16, 12)
        line(fr, cx, cy + dy, int(cw * eio((f - t0) / 20)), a * .9, GOLD, 2)
        put(fr, text_img(f"0{n+1}", "Inter-Medium", 17, GOLD, .2), cx, cy + 22 + dy, a, r)
        put(fr, text_img(big, "InterDisplay-SemiBold", 44, CREAM), cx, cy + 52 + dy, a, r)
        r2, a2, dy2 = anim(f, t0 + 4, out, 16, 12)
        put(fr, text_img(small, "Inter-Regular", 24, CREAM), cx, cy + 112 + dy2, a2 * .72, r2)


def final(fr, f):
    fr.alpha_composite(with_alpha(GLOW, eo(f / 20)))
    cx = W / 2
    fade = 1 - ei((f - (FIN - 24)) / 24)
    r, a, dy = anim(f, 8, None, 26)
    tr = .06 - .05 * eo((f - 8) / 60)
    put(fr, text_img("A daily moment of care.", "InterDisplay-Light", 92, CREAM, round(tr, 3)), cx, 380 + dy, a * fade, r, "c")
    r, a, dy = anim(f, 22, None, 22)
    put(fr, text_img("하루 한 포, 나를 챙기는 시간", "ko", 34, CREAM, .05), cx, 512 + dy, a * fade * .8, r, "c")
    L = int(300 * eio((f - 30) / 24))
    line(fr, int(cx - L / 2), 600, L, fade)
    r, a, dy = anim(f, 36, None, 20)
    put(fr, text_img("GinHongsam Daily Balance", "InterDisplay-SemiBold", 40, CREAM), cx, 640 + dy, a * fade, r, "c")
    r, a, dy = anim(f, 44, None, 20)
    put(fr, text_img("BTGin Co., Ltd.   ·   Daejeon, Korea   ·   www.btgin.com", "Inter-Regular", 22, CREAM, .04), cx, 708 + dy, a * fade * .7, r, "c")


# ---------------- frame assembly
def finish(img):
    a = np.asarray(img.convert("RGB"), np.float32) * VIG
    a += DITHER[np.random.randint(0, 4)]
    return np.clip(a, 0, 255).astype(np.uint8)


def render_global(g, src_frame=None, last_base=None):
    if g < PRE:
        fr = Image.new("RGBA", (W, H), INK + (255,))
        preroll(fr, g)
        # flash into footage
        p = ei((g - (PRE - 6)) / 6)
        if p > 0:
            a = np.asarray(fr, np.float32)
            a[..., :3] = a[..., :3] * (1 - p * .9) + np.array([255, 240, 220]) * p * .9
            fr = Image.fromarray(a.astype(np.uint8))
        return finish(fr), None
    if g < FEND:
        i = g - F0
        base = compose_shot(src_frame, i)
        if i < 6:  # out of preroll flash
            base = apply_flash_in(base, i)
        base = apply_transition(base, i)
        fr = base.convert("RGBA")
        title(fr, g)
        section_text(fr, g)
        hud(fr, g)
        return finish(fr), base
    if g < FEND + DET:
        f = g - FEND
        b = last_base
        bl = eo(f / 22)
        bgi = b.filter(ImageFilter.GaussianBlur(1 + 18 * bl)) if bl > .02 else b
        bgi = zoom_img(bgi, 1 + .04 * f / DET)
        arr = np.asarray(bgi, np.float32) * (1 - .62 * bl)
        fr = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
        details(fr, f)
        # dissolve to final card
        x = eio((f - (DET - 14)) / 14)
        if x > 0:
            dark = Image.new("RGBA", (W, H), INK + (255,))
            final(dark, 0)
            fr = Image.blend(fr, dark, x)
        return finish(fr), None
    f = g - FEND - DET
    fr = Image.new("RGBA", (W, H), INK + (255,))
    final(fr, f)
    return finish(fr), None


def apply_flash_in(img, i):
    p = 1 - eo(i / 6)
    a = np.asarray(img, np.float32)
    a = a * (1 - p * .9) + np.array([255, 240, 220], np.float32) * p * .9
    return Image.fromarray(a.astype(np.uint8))


def main():
    mode = sys.argv[1]
    if mode == "preview":
        outdir = os.path.join(HERE, "prev"); os.makedirs(outdir, exist_ok=True)
        last = None
        for gs in sys.argv[2:]:
            g = int(gs)
            src = footage_frame_seek(g - F0) if F0 <= g < FEND else None
            if g >= FEND:
                last = compose_shot(footage_frame_seek(NF - 1), NF - 1)
            arr, _ = render_global(g, src, last)
            Image.fromarray(arr).save(f"{outdir}/f{g:05d}.png")
        return
    out = sys.argv[2]
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-vf", "noise=alls=3:allf=t",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                            "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    reader = footage_reader()
    last = None
    for g in range(TOTAL):
        src = next(reader) if F0 <= g < FEND else None
        arr, base = render_global(g, src, last)
        if g == FEND - 1:
            last = compose_shot(src, g - F0)  # clean base (no transition) for end card
        enc.stdin.write(arr.tobytes())
        if g % 60 == 0:
            print("frame", g, "/", TOTAL, flush=True)
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    main()
