"""진홍삼 데일리 밸런스 production video, v3 - built to the BTGin Design System.

Reuses footage loading and reframing from render_ko.py; everything on top (cards, overlays,
type, colours, motion) follows the design system's video spec.
  python3 render_v3.py preview f1 f2 ...
  python3 render_v3.py video OUT.mp4
"""
import subprocess, sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import render_ko as R

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = "/tmp/claude-0/-home-user-btgin/25c59277-18aa-55ab-9218-a328aca5ae4b/scratchpad/btgfonts/BTGin_Fonts"
IMG = R.IMG

# warm grade: slightly less saturation, +red, -blue (green floors calmed as before)
R.GRADE = ("huesaturation=saturation=-0.3:strength=2:colors=g+c,eq=saturation=0.92,"
           "colorbalance=rm=0.03:bm=-0.03:rh=0.025:bh=-0.03,curves=all='0/0.01 0.5/0.49 1/0.98'")

W, H, FPS = 1920, 1080, 30
NF = R.NF

# ---------- timeline (frames)
LOGO, HERO = 60, 135
XF = 18                        # scene crossfade 0.6 s
SHOT_XF = 6                    # footage-shot crossfade 0.2 s
F0 = LOGO + HERO - XF
FEND = F0 + NF
C1 = FEND - XF
C1_LEN, C2_LEN, FIN_LEN = 180, 195, 165
C2 = C1 + C1_LEN - XF
FIN = C2 + C2_LEN - XF
TOTAL = FIN + FIN_LEN

# ---------- design tokens
IVORY, CREAM, WHITE = (251, 247, 241), (243, 236, 226), (255, 255, 255)
RED, GOLD, GOLD_D, GOLD_V = (176, 18, 43), (201, 163, 90), (156, 122, 60), (232, 207, 148)
INK, BODY, MUTED = (42, 28, 24), (91, 74, 66), (140, 123, 112)
LINE = (91, 74, 66, 41)
SCRIM = (26, 14, 10)

F = {
    "serif500": f"{FONTS}/1_Noto_Serif_KR (headlines)/NotoSerifKR-Medium.otf",
    "serif600": f"{FONTS}/1_Noto_Serif_KR (headlines)/NotoSerifKR-SemiBold.otf",
    "sans400": f"{FONTS}/2_Pretendard (body)/Pretendard-Regular.otf",
    "sans500": f"{FONTS}/2_Pretendard (body)/Pretendard-Medium.otf",
    "sans600": f"{FONTS}/2_Pretendard (body)/Pretendard-SemiBold.otf",
    "latinI": f"{FONTS}/3_Cormorant_Garamond (English labels)/CormorantGaramond-MediumItalic.ttf",
    "latin600": f"{FONTS}/3_Cormorant_Garamond (English labels)/CormorantGaramond-SemiBold.ttf",
}

# step text: Korean name = client's caption sheet; English name and KR · EN description approved draft
STEPS = [  # footage start, end, Korean name, English name, description
    (0, 98, "비티진 자체 생산 라인", "BTGin's Own Production Line",
     "대전 비티진 공장에서 직접 만듭니다 · Made in our own factory in Daejeon"),
    (98, 179, "자동화 라인에서 충진 및 밀봉", "Automated Filling & Sealing",
     "한 포에 50mL씩 충진합니다 · 50 mL filled into every pouch"),
    (179, 256, "한 포씩 정밀 중량 체크", "Precise Weight Check, Pouch by Pouch",
     "중량을 하나하나 확인합니다 · Each pouch weighed and checked"),
    (256, 356, "밀봉 후 철저한 살균 공정", "Thorough Sterilization After Sealing",
     "밀봉한 파우치를 살균 처리합니다 · Sealed pouches are sterilized"),
    (356, 504, "수작업 최종 검수", "Final Inspection by Hand",
     "포장 전 직원이 직접 확인합니다 · Checked by our staff before packing"),
    (504, 702, "30포씩 정성껏 포장", "Carefully Packed, 30 Pouches a Box",
     "10포씩 3개의 속박스 · 3 inner boxes of 10 pouches"),
    (702, NF, "제조부터 포장까지, 비티진이 직접", "Made and Packed by BTGin",
     "100% 자체 생산 · 100% in-house production"),
]
# callout: footage window, target centre, circle radius, card position, number, caption lines
CALLOUT = dict(t0=526, t1=578, cx=1050, cy=832, r=124, card=(1300, 440), num="30포",
               cap=("한 박스 구성", "30 pouches per box"))

SHOT_CUTS = [s[0] for s in R.SHOTS[1:]]


# ---------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def eoc(t):  # ease-out cubic
    t = clamp(t); return 1 - (1 - t) ** 3


def eio(t):
    t = clamp(t); return .5 - .5 * math.cos(math.pi * t)


def eback(t):  # ease-out back (slight overshoot)
    t = clamp(t); c = 1.4
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


IN = 21          # 0.7 s text rise + fade
POP_GAP = 13.5   # 0.45 s between popping cards
RISE = 30


# ---------- type
_fonts, _cache = {}, {}


def font(key, size):
    k = (key, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(F[key], size)
    return _fonts[k]


def text(segs, key, size, track=0.0, color=INK):
    """segs: str or [(text, color), ...]; track in em. Returns RGBA with ._pad, ._w."""
    if isinstance(segs, str):
        segs = [(segs, color)]
    k = (tuple(segs), key, size, track)
    if k in _cache:
        return _cache[k]
    f = font(key, size)
    asc, desc = f.getmetrics()
    pad = int(size * .4)
    chars = [(ch, c) for s, c in segs for ch in s]
    widths = [f.getlength(ch) for ch, _ in chars]
    tw = sum(widths) + track * size * (len(chars) - 1)
    im = Image.new("RGBA", (int(tw + 2 * pad + 2), asc + desc + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = pad
    for (ch, c), w in zip(chars, widths):
        d.text((x, pad), ch, font=f, fill=tuple(c[:3]) + ((c[3] if len(c) > 3 else 255),))
        x += w + track * size
    im._pad, im._w, im._asc = pad, tw, asc
    _cache[k] = im
    return im


def alpha(im, a):
    if a >= .999:
        return im
    arr = np.array(im)
    arr[..., 3] = (arr[..., 3].astype(np.float32) * a).astype(np.uint8)
    return Image.fromarray(arr)


def put(fr, im, x, y, f, t0, anchor="l", clip=False, a_mul=1.0, out=None):
    """Design-system text motion: rise 30 px + fade over 0.7 s (ease-out cubic).
    clip=True: headline revealed bottom-to-top inside its own box. out=(t_out, dur) fades out."""
    p = eoc((f - t0) / IN)
    a = p * a_mul
    if out is not None:
        a *= 1 - eio((f - out[0]) / out[1])
    if a <= .003:
        return
    pad = im._pad
    if anchor == "c":
        x -= im._w / 2
    elif anchor == "r":
        x -= im._w
    x, y = int(round(x - pad)), int(round(y - pad))
    w, h = im.size
    if clip:
        vis = int(h * p)
        if vis <= 0:
            return
        im = im.crop((0, 0, w, vis))
        y += h - vis
    else:
        y += int(round(RISE * (1 - p)))
    fr.alpha_composite(alpha(im, a), (x, y))


def rrect(fr, box, fill, radius, outline=None, width=1, a=1.0):
    layer = Image.new("RGBA", fr.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fa = fill[3] if len(fill) > 3 else 255
    d.rounded_rectangle(box, radius, fill=tuple(fill[:3]) + (int(fa * a),),
                        outline=(tuple(outline[:3]) + (int((outline[3] if len(outline) > 3 else 255) * a),)) if outline else None,
                        width=width)
    fr.alpha_composite(layer)


def chip(fr, x, y, label, f, t0, kind="plain", size=24):
    """Fully round chip that pops in with a slight overshoot. kind: plain | main. Returns width."""
    col = WHITE if kind == "main" else INK
    im = text(label, "sans600" if kind == "main" else "sans500", size, -.01, col)
    w, h = int(im._w) + 48, size + 30
    p = eback((f - t0) / 14)
    a = eoc((f - t0) / 8)
    if a > .003:
        s = max(.01, .9 + .1 * p)
        cw, ch = int(w * s), int(h * s)
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        if kind == "main":
            d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=RED + (255,))
        else:
            d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=WHITE + (255,), outline=LINE, width=1)
        layer.alpha_composite(im, (24 - im._pad, (h - size) // 2 - im._pad - int(size * .08)))
        layer = layer.resize((cw, ch), Image.LANCZOS)
        fr.alpha_composite(alpha(layer, a), (int(x + (w - cw) / 2), int(y + (h - ch) / 2)))
    return w


# ---------- images
def load_product(n, box_w, box_h):
    im = Image.open(f"{IMG}/{n}.webp").convert("RGB")
    a = np.asarray(im)
    ys, xs = np.where((a < 245).any(2))
    pad = 30
    im = im.crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad, im.width), min(ys.max() + pad, im.height)))
    s = min(box_w / im.width, box_h / im.height)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def logo(width, white=False):
    im = Image.open(f"{IMG}/6.webp").convert("RGBA")
    im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    if white:
        arr = np.array(im); arr[..., :3] = 255; im = Image.fromarray(arr)
    return im


PANEL = 760                                  # photo panel size, radius 36
PANEL_X, PANEL_Y = W - 150 - PANEL, (H - PANEL) // 2
P_HERO = load_product(1, PANEL - 90, PANEL - 90)
P_SET = load_product(3, PANEL - 70, PANEL - 70)
P_POUCH = load_product(5, PANEL - 120, PANEL - 90)
P_FIN = load_product(4, 640, 330)
LOGO_COLOR = logo(560)
LOGO_SMALL = logo(170)
LOGO_WHITE = logo(150, white=True)


def photo_panel(fr, prod, f, t0=0):
    """White panel, radius 36, hairline border; product photo centred. Fades + rises with the text."""
    p = eoc((f - t0) / IN)
    if p <= .003:
        return
    dy = int(RISE * (1 - p))
    layer = Image.new("RGBA", (PANEL, PANEL), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((0, 0, PANEL - 1, PANEL - 1), 36, fill=WHITE + (255,), outline=LINE, width=1)
    mask = Image.new("L", (PANEL, PANEL), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, PANEL - 1, PANEL - 1), 36, fill=255)
    ph = Image.new("RGBA", (PANEL, PANEL), (0, 0, 0, 0))
    ph.paste(prod, ((PANEL - prod.width) // 2, (PANEL - prod.height) // 2))
    ph.putalpha(Image.composite(ph.getchannel("A"), Image.new("L", ph.size, 0), mask))
    layer.alpha_composite(ph)
    fr.alpha_composite(alpha(layer, p), (PANEL_X, PANEL_Y + dy))


def headline(fr, lines, x, y, size, f, t0, anchor="l", stagger=4):
    """Noto Serif KR 500, -0.04em, line-height 1.3, revealed bottom-to-top line by line."""
    for k, segs in enumerate(lines):
        put(fr, text(segs, "serif500", size, -.04), x, y + k * size * 1.3, f, t0 + k * stagger, anchor, clip=True)
    return y + len(lines) * size * 1.3


def label(fr, s, x, y, f, t0, anchor="l"):
    put(fr, text(s, "latinI", 40, 0, GOLD_D), x, y, f, t0, anchor)


# ---------- title cards
def card_logo(f):
    fr = Image.new("RGBA", (W, H), IVORY + (255,))
    p = eoc((f - 6) / IN)
    if p > .003:
        fr.alpha_composite(alpha(LOGO_COLOR, p),
                           ((W - LOGO_COLOR.width) // 2, (H - LOGO_COLOR.height) // 2 + int(RISE * (1 - p))))
    return fr


def card_hero(f):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    photo_panel(fr, P_HERO, f, 4)
    x = 150
    label(fr, "Made by BTGin", x, 250, f, 6)
    y = headline(fr, [[("진홍삼", RED)], [("데일리 밸런스", INK)]], x - 6, 312, 104, f, 12)
    put(fr, text("Gin Hong Sam Daily Balance", "sans400", 32, -.02, BODY), x, y + 24, f, 26)
    put(fr, text("Korean Red Ginseng Herbal Blend", "sans400", 30, -.02, BODY), x, y + 72, f, 30)
    cx = x
    for k, (s, kind) in enumerate([("6년근 홍삼", "main"), ("14가지 원료", "plain"), ("HACCP", "plain")]):
        cx += chip(fr, cx, y + 150, s, f, 40 + k * POP_GAP, kind) + 12
    return fr


def card_info(f):
    fr = Image.new("RGBA", (W, H), IVORY + (255,))
    photo_panel(fr, P_SET, f, 4)
    x = 150
    label(fr, "Product Information", x, 170, f, 6)
    y = headline(fr, [[("30포", RED), ("로 채운", INK)], [("한 달의 선물", INK)]], x - 4, 230, 84, f, 12)
    rows = [("내용량", "1,500mL (50mL × 30포)"), ("구성", "10포 × 3개 속박스"), ("열량", "1포당 25kcal"),
            ("섭취방법", "하루 1포, 그대로 드세요"), ("보관방법", "직사광선을 피해 실온 보관"),
            ("소비기한", "제조일로부터 24개월")]
    y += 36
    for k, (lab, val) in enumerate(rows):
        t0 = 30 + k * 5
        yy = y + k * 66
        put(fr, text(lab, "sans500", 24, -.02, MUTED), x, yy + 4, f, t0)
        put(fr, text(val, "sans500", 30, -.02, INK), x + 170, yy, f, t0)
        if k < len(rows) - 1:
            a = eoc((f - t0) / IN)
            if a > .003:
                rrect(fr, (x, yy + 50, x + 700, yy + 50), LINE, 0, a=a)
    return fr


def card_ingredients(f):
    fr = Image.new("RGBA", (W, H), CREAM + (255,))
    photo_panel(fr, P_POUCH, f, 4)
    x = 150
    label(fr, "14 Ingredients", x, 200, f, 6)
    y = headline(fr, [[("홍삼에 과일과 버섯을", INK)], [("더한 ", INK), ("14가지", RED), (" 원료", INK)]], x - 4, 260, 76, f, 12)
    put(fr, text("Red ginseng blended with fruits and mushrooms", "sans400", 30, -.02, BODY), x, y + 20, f, 26)
    yy = y + 100
    chip(fr, x, yy, "6년근 홍삼농축액", f, 36, "main", 26)
    rows = [["대추", "배", "벌꿀", "구기자"], ["영지버섯", "생강", "헛개나무열매"], ["대보농축액", "프락토올리고당"]]
    k = 1
    for ri, row in enumerate(rows):
        cx = x
        for name in row:
            cx += chip(fr, cx, yy + 80 + ri * 70, name, f, 36 + k * 4) + 12
            k += 1
    return fr


def card_final(f):
    fr = Image.new("RGBA", (W, H), IVORY + (255,))
    cx = W / 2
    label(fr, "A Daily Moment of Care", cx, 250, f, 6, "c")
    y = headline(fr, [[("하루 한 포,", INK)], [("나를 챙기는", RED), (" 시간", INK)]], cx, 312, 100, f, 12, "c")
    put(fr, text("One pouch a day, a moment to take care of yourself", "sans400", 30, -.02, BODY), cx, y + 22, f, 26, "c")
    # chips row, centred
    items = [("6년근 홍삼", "main"), ("14가지 원료", "plain"), ("HACCP", "plain")]
    widths = [int(text(s, "sans600" if k == "main" else "sans500", 24, -.01)._w) + 48 for s, k in items]
    tw = sum(widths) + 12 * (len(items) - 1)
    xx = cx - tw / 2
    for k, ((s, kind), w) in enumerate(zip(items, widths)):
        chip(fr, xx, y + 100, s, f, 36 + k * POP_GAP, kind)
        xx += w + 12
    p = eoc((f - 62) / IN)
    if p > .003:
        fr.alpha_composite(alpha(LOGO_SMALL, p), (int(cx - LOGO_SMALL.width / 2), int(860 + RISE * (1 - p))))
    put(fr, text("고객센터 1600-4546  ·  www.btginmall.com", "sans400", 20, -.01, MUTED), cx, 962, f, 66, "c")
    out = eio((f - (FIN_LEN - 20)) / 20)
    if out > 0:
        fr = Image.blend(fr, Image.new("RGBA", (W, H), (0, 0, 0, 255)), out)
    return fr


# ---------- footage overlays
def grad_bottom():
    yy = np.arange(H, dtype=np.float32)[:, None]
    a = np.clip((yy - (H - 520)) / 520, 0, 1) ** 1.2 * .82
    arr = np.zeros((H, W, 4), np.uint8); arr[..., :3] = SCRIM
    arr[..., 3] = np.broadcast_to((a * 255).astype(np.uint8), (H, W))
    return Image.fromarray(arr)


def grad_top():
    yy = np.arange(H, dtype=np.float32)[:, None]
    a = np.clip(1 - yy / 220, 0, 1) ** 1.5 * .42
    arr = np.zeros((H, W, 4), np.uint8); arr[..., :3] = SCRIM
    arr[..., 3] = np.broadcast_to((a * 255).astype(np.uint8), (H, W))
    return Image.fromarray(arr)


GB, GT = grad_bottom(), grad_top()


def pin_icon(size=26, color=GOLD_V):
    s = 4
    im = Image.new("RGBA", (size * s, int(size * 1.35) * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w = size * s
    d.ellipse((0, 0, w - 1, w - 1), fill=color + (255,))
    d.polygon([(w * .12, w * .66), (w * .88, w * .66), (w / 2, im.height - 1)], fill=color + (255,))
    r = w * .2
    d.ellipse((w / 2 - r, w / 2 - r, w / 2 + r, w / 2 + r), fill=(0, 0, 0, 0))
    return im.resize((size, int(size * 1.35)), Image.LANCZOS)


PIN = pin_icon()
HUD_TOP = 64


def hud(fr, i):
    """Logo, location, step block, counter, progress bar. i = footage index."""
    ha = eoc((i - XF) / IN) * (1 - eio((i - (NF - XF - 6)) / 12))
    if ha <= .003:
        return
    fr.alpha_composite(alpha(GT, ha))
    fr.alpha_composite(alpha(GB, ha))
    # top-left: white logo + label
    fr.alpha_composite(alpha(LOGO_WHITE, ha), (120, HUD_TOP))
    lab = text("자체 생산 라인  ·  IN-HOUSE PRODUCTION", "sans500", 20, .16, WHITE)
    mid = HUD_TOP + LOGO_WHITE.height * .36
    fr.alpha_composite(alpha(lab, ha * .95), (int(120 + LOGO_WHITE.width + 28 - lab._pad), int(mid - 12 - lab._pad)))
    # top-right: pin + location
    loc = text("BTGIN FACTORY  ·  DAEJEON, KOREA", "sans500", 20, .16, WHITE)
    lx = W - 120 - loc._w
    fr.alpha_composite(alpha(loc, ha * .95), (int(lx - loc._pad), int(mid - 12 - loc._pad)))
    fr.alpha_composite(alpha(PIN, ha), (int(lx - 16 - PIN.width), int(mid - PIN.height / 2 - 2)))
    # step block (bottom-left)
    k = max(n for n, s in enumerate(STEPS) if s[0] <= i)
    s0, s1, ko, en, desc = STEPS[k]
    t_in = s0 + (XF + 4 if s0 == 0 else 6)
    out = (s1 - 12, 12) if k < len(STEPS) - 1 else (NF - XF - 6, 12)
    put(fr, text(f"STEP {k + 1:02d}", "sans600", 22, .24, GOLD_V), 120, 706, i, t_in, out=out)
    put(fr, text(ko, "serif500", 80, -.04, WHITE), 116, 744, i, t_in + 3, clip=True, out=out)
    put(fr, text(en, "sans400", 32, -.02, WHITE), 120, 858, i, t_in + 7, a_mul=.9, out=out)
    put(fr, text(desc, "sans400", 24, -.02, WHITE), 120, 912, i, t_in + 10, a_mul=.72, out=out)
    # counter (bottom-right)
    cur = text(f"{k + 1:02d}", "latin600", 34, .04, GOLD_V)
    rest = text(f" / {len(STEPS):02d}", "latin600", 34, .04, WHITE)
    rx = W - 120 - rest._w
    fr.alpha_composite(alpha(rest, ha * .7), (int(rx - rest._pad), int(906 - rest._pad)))
    fr.alpha_composite(alpha(cur, ha), (int(rx - cur._w - 4 - cur._pad), int(906 - cur._pad)))
    # progress bar: 2 px, gold fill, one dot per step
    y = H - 84
    x0, x1 = 120, W - 120
    prog = clamp(i / (NF - 1))
    rrect(fr, (x0, y - 1, x1, y), (255, 255, 255, 70), 0, a=ha)
    rrect(fr, (x0, y - 1, x0 + int((x1 - x0) * prog), y), GOLD_V, 0, a=ha)
    for n in range(len(STEPS)):
        dx = x0 + (x1 - x0) * n / (len(STEPS) - 1)
        reached = STEPS[n][0] <= i
        r = 6 if n == k else 4
        col = GOLD_V + (255,) if reached else (255, 255, 255, 140)
        rrect(fr, (dx - r, y - r, dx + r, y + r), col, r, a=ha)
        if n == k:
            rrect(fr, (dx - 11, y - 11, dx + 11, y + 11), (0, 0, 0, 0), 11, outline=GOLD_V + (150,), width=1, a=ha)


def callout(fr, i):
    c = CALLOUT
    if not (c["t0"] - 1 <= i < c["t1"]):
        return
    f = i - c["t0"]
    out = 1 - eio((i - (c["t1"] - 10)) / 10)
    cx, cy, r = c["cx"], c["cy"], c["r"]
    # circle draws on (4 px, gold-on-video)
    sweep = eoc(f / 14) * 360
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if sweep > 1:
        d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + sweep, fill=GOLD_V + (int(255 * out),), width=4)
    # line from circle edge to card
    kx, ky = c["card"]
    ex, ey = cx + r * math.cos(math.radians(-45)), cy + r * math.sin(math.radians(-45))
    tx, ty = kx, ky + 75
    lp = eoc((f - 10) / 10)
    if lp > 0:
        d.line((ex, ey, ex + (tx - ex) * lp, ey + (ty - ey) * lp), fill=GOLD_V + (int(255 * out),), width=2)
    fr.alpha_composite(layer)
    # ivory card pops with overshoot
    t0 = 18
    p = eback((f - t0) / 14)
    a = eoc((f - t0) / 8) * out
    if a > .003:
        cw, chh = 300, 150
        card = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle((0, 0, cw - 1, chh - 1), 20, fill=IVORY + (255,))
        num = text(c["num"], "serif500", 44, -.04, RED)
        card.alpha_composite(num, (28 - num._pad, 18 - num._pad))
        l1 = text(c["cap"][0], "sans500", 22, -.02, BODY)
        l2 = text(c["cap"][1], "sans400", 20, -.02, MUTED)
        card.alpha_composite(l1, (28 - l1._pad, 82 - l1._pad))
        card.alpha_composite(l2, (28 - l2._pad, 112 - l2._pad))
        s = max(.01, .85 + .15 * p)
        sc = card.resize((int(cw * s), int(chh * s)), Image.LANCZOS)
        fr.alpha_composite(alpha(sc, a), (int(kx + (cw - sc.width) / 2), int(ky + (chh - sc.height) / 2)))


# ---------- footage base with 0.2 s shot crossfades
class Base:
    def __init__(self):
        self.prev = None     # last composed frame
        self.held = None     # last frame of the outgoing shot

    def get(self, src, i):
        img = R.compose_footage(src, i)
        cut = next((c for c in SHOT_CUTS if c <= i < c + SHOT_XF), None)
        if cut is not None:
            if i == cut:
                self.held = self.prev
            if self.held is not None:
                img = Image.blend(self.held, img, eio((i - cut + 1) / (SHOT_XF + 1)))
        self.prev = R.compose_footage(src, i) if cut is not None else img
        return img


def footage_layer(base, src, i):
    fr = base.get(src, i).convert("RGBA")
    callout(fr, i)
    hud(fr, i)
    return fr


def finish(img):
    a = np.asarray(img.convert("RGB"), np.float32) + R.DITHER[np.random.randint(0, 4)]
    return np.clip(a, 0, 255).astype(np.uint8)


def xfade(a, b, g, start):
    return Image.blend(a, b, eio((g - start) / XF))


def render(g, base, src):
    i = g - F0
    if g < LOGO - XF:
        fr = card_logo(g)
        if g < 12:
            fr = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), fr, eio(g / 12))
        return finish(fr)
    if g < LOGO:
        return finish(xfade(card_logo(g), card_hero(g - (LOGO - XF)), g, LOGO - XF))
    if g < F0:
        return finish(card_hero(g - (LOGO - XF)))
    if g < F0 + XF:
        return finish(xfade(card_hero(g - (LOGO - XF)), footage_layer(base, src, i), g, F0))
    if g < C1:
        return finish(footage_layer(base, src, i))
    if g < FEND:
        return finish(xfade(footage_layer(base, src, i), card_info(g - C1), g, C1))
    if g < C2:
        return finish(card_info(g - C1))
    if g < C2 + XF:
        return finish(xfade(card_info(g - C1), card_ingredients(g - C2), g, C2))
    if g < FIN:
        return finish(card_ingredients(g - C2))
    if g < FIN + XF:
        return finish(xfade(card_ingredients(g - C2), card_final(g - FIN), g, FIN))
    return finish(card_final(g - FIN))


def main():
    if sys.argv[1] == "preview":
        out = os.path.join(HERE, "prev_v3"); os.makedirs(out, exist_ok=True)
        for gs in sys.argv[2:]:
            g = int(gs)
            base = Base()
            src = None
            if F0 <= g < FEND:
                i = g - F0
                cut = next((c for c in SHOT_CUTS if c <= i < c + SHOT_XF), None)
                if cut is not None:
                    base.prev = R.compose_footage(R.footage_seek(cut - 1), cut - 1)
                    for j in range(cut, i):
                        base.get(R.footage_seek(j), j)
                src = R.footage_seek(i)
            Image.fromarray(render(g, base, src)).save(f"{out}/f{g:05d}.png")
        return
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                            "-pix_fmt", "yuv420p", sys.argv[2]], stdin=subprocess.PIPE)
    reader = R.footage_reader()
    base = Base()
    for g in range(TOTAL):
        src = next(reader) if F0 <= g < FEND else None
        enc.stdin.write(render(g, base, src).tobytes())
        if g % 100 == 0:
            print("frame", g, "/", TOTAL, flush=True)
    enc.stdin.close(); enc.wait()
    print("done", flush=True)


if __name__ == "__main__":
    main()
