"""진홍삼 데일리 밸런스 - Korean production video for Coupang / Naver Smart Store.

Original cuts kept as edited; only gentle fades, centred framing with blurred fill,
Korean captions and product cards.
  python3 render_ko.py preview f1 f2 ...
  python3 render_ko.py video OUT.mp4
"""
import subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

U = "/root/.claude/uploads/25c59277-18aa-55ab-9218-a328aca5ae4b"
IMG = "/tmp/claude-0/-home-user-btgin/25c59277-18aa-55ab-9218-a328aca5ae4b/images"
SRC = [f"{U}/94fd8a47-part_1.mp4", f"{U}/f59f0fa4-Part_2.mp4"]
HERE = os.path.dirname(os.path.abspath(__file__))
GRADE = ("huesaturation=saturation=-0.35:strength=2:colors=g+c,"
         "colorbalance=rm=0.015:bm=-0.01:rh=0.02:bh=-0.02,"
         "curves=all='0/0.01 0.5/0.49 1/0.98',eq=saturation=1.05")

W, H, FPS = 1920, 1080, 30
SW, SH = 2560, 1440
NF = 469 + 480

# global timeline (frames)
LOGO = 60                     # BTGin logo card
HERO = 105                    # product hero card (incl. dissolve into footage)
XF = 20                       # dissolve length card <-> footage
F0 = LOGO + HERO - XF         # footage starts under the hero dissolve
FEND = F0 + NF
C1 = FEND - XF                # details card 1 starts dissolving over last footage frames
C1_LEN, C2_LEN, FIN_LEN, XC = 165, 180, 150, 15
C2 = C1 + C1_LEN - XC
FIN = C2 + C2_LEN - XC
TOTAL = FIN + FIN_LEN

BG = (250, 247, 242)
INK = (42, 26, 23)
RED = (150, 26, 34)
GOLD = (176, 128, 56)
WHITE = (255, 255, 255)
KO = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
FD = "/usr/share/fonts/opentype/inter/"

# real content columns of each shot in the source (full-res px); centred on output
SHOTS = [(0, 0, 2560), (30, 0, 2290), (61, 0, 2560), (98, 0, 1338), (142, 0, 2099),
         (179, 254, 2560), (208, 0, 1842), (256, 1213, 2560), (289, 0, 1013),
         (322, 0, 2560), (356, 0, 2560), (389, 0, 1283), (432, 578, 2560),
         (469, 745, 2560), (504, 0, 2560), (581, 0, 2560), (632, 832, 2560),
         (670, 0, 2560), (702, 761, 2560), (741, 127, 2560), (836, 0, 2560), (882, 0, 2560)]

CAPTIONS = [  # footage start, end, number, caption (wording from the client's caption sheet)
    (0, 98, "01", "비티진 자체 생산 라인"),
    (98, 179, "02", "자동화 라인에서 충진 및 밀봉"),
    (179, 256, "03", "한 포씩 정밀 중량 체크"),
    (256, 356, "04", "밀봉 후 철저한 살균 공정"),
    (356, 504, "05", "수작업 최종 검수"),
    (504, 702, "06", "30포씩 정성껏 포장"),
    (702, NF, "07", "제조부터 포장까지, 비티진이 직접"),
]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def es(t):  # smooth ease in-out (sine)
    t = clamp(t); return .5 - .5 * np.cos(np.pi * t)


def fade(f, t_in, t_out=None, din=15, dout=12):
    a = es((f - t_in) / din)
    if t_out is not None:
        a *= 1 - es((f - (t_out - dout)) / dout)
    return a


_fonts, _txt = {}, {}


def font(name, size):
    k = (name, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(KO if name == "ko" else FD + name + ".otf", size)
    return _fonts[k]


def text_img(text, fname, size, color, tracking=0.0):
    k = (text, fname, size, color, tracking)
    if k in _txt:
        return _txt[k]
    f = font(fname, size)
    asc, desc = f.getmetrics()
    pad = int(size * .3)
    widths = [f.getlength(c) for c in text]
    tw = sum(widths) + tracking * size * (len(text) - 1)
    im = Image.new("RGBA", (int(tw) + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tracking:
        x = pad
        for c, w in zip(text, widths):
            d.text((x, pad), c, font=f, fill=color + (255,)); x += w + tracking * size
    else:
        d.text((pad, pad), text, font=f, fill=color + (255,))
    im._pad = pad
    im._w = tw
    _txt[k] = im
    return im


def with_alpha(im, a):
    if a >= .999:
        return im
    arr = np.array(im)
    arr[..., 3] = (arr[..., 3].astype(np.float32) * a).astype(np.uint8)
    return Image.fromarray(arr)


def put(fr, im, x, y, a=1.0, rise=0.0, anchor="l"):
    """Gentle fade with a small rise (rise = px still to travel)."""
    if a <= .003:
        return
    pad = im._pad
    if anchor == "c":
        x -= im._w / 2
    elif anchor == "r":
        x -= im._w
    fr.alpha_composite(with_alpha(im, a), (int(x - pad), int(y - pad + rise)))


def rect(fr, box, color, a=1.0, radius=0):
    layer = Image.new("RGBA", fr.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(box, radius, fill=color + (int(255 * a),))
    fr.alpha_composite(layer)


# ---------- product photos (white bg -> multiplied onto card colour)
def load_product(n, height):
    im = Image.open(f"{IMG}/{n}.webp").convert("RGB")
    a = np.asarray(im)
    mask = (a < 245).any(2)
    ys, xs = np.where(mask)
    pad = 20
    im = im.crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0), min(xs.max() + pad, im.width), min(ys.max() + pad, im.height)))
    w = int(im.width * height / im.height)
    return im.resize((w, height), Image.LANCZOS)


def place_product(fr, prod, x, y, a):
    """multiply-blend so the white photo background disappears into the card."""
    if a <= .003:
        return
    region = fr.crop((x, y, x + prod.width, y + prod.height)).convert("RGB")
    mul = ImageChops.multiply(region, prod)
    blended = Image.blend(region, mul, a)
    fr.paste(blended, (x, y))


P_HERO = load_product(1, 820)
P_SET = load_product(2, 700)
P_POUCH = load_product(5, 860)
P_FIN = load_product(4, 520)


def load_logo(width):
    im = Image.open(f"{IMG}/6.webp").convert("RGBA")
    im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
    return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)


LOGO_BIG = load_logo(760)
LOGO_SMALL = load_logo(150)


def put_img(fr, im, x, y, a):
    if a > .003:
        fr.alpha_composite(with_alpha(im, a), (int(x), int(y)))


def vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
    return (1 - np.clip(d - .6, 0, 1) * .35)[..., None].astype(np.float32)


def bottom_grad():
    yy = np.tile(np.arange(H, dtype=np.float32)[:, None], (1, W))
    a = np.clip((yy / H - .58) / .42, 0, 1) ** 1.5 * .78
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr)


VIG = vignette()
BGRAD = bottom_grad()
DITHER = [np.random.uniform(-1.2, 1.2, (H, W, 1)).astype(np.float32) for _ in range(4)]


# ---------- footage
def footage_reader():
    cmd = ["ffmpeg", "-v", "error", "-i", SRC[0], "-i", SRC[1], "-filter_complex",
           f"[0:v][1:v]concat=n=2:v=1:a=0,{GRADE},format=rgb24[v]", "-map", "[v]", "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=SW * SH * 6)
    n = SW * SH * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        yield Image.frombuffer("RGB", (SW, SH), b, "raw", "RGB", 0, 1)


def footage_seek(i):
    src, j = (SRC[0], i) if i < 469 else (SRC[1], i - 469)
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"select=eq(n\\,{j}),{GRADE},format=rgb24",
                        "-frames:v", "1", "-f", "rawvideo", "-"], capture_output=True).stdout
    return Image.frombuffer("RGB", (SW, SH), b, "raw", "RGB", 0, 1)


def compose_footage(src, i):
    x0, x1 = 0, SW
    for s in SHOTS:
        if s[0] <= i:
            _, x0, x1 = s
    if x0 == 0 and x1 == SW:
        return src.resize((W, H), Image.BICUBIC)
    xa, xb = (x0 + 6 if x0 else 0), (x1 - 6 if x1 < SW else SW)
    cw = xb - xa
    bh = cw * H / W
    bg = src.resize((480, 270), Image.BILINEAR, box=(xa, (SH - bh) / 2, xb, (SH + bh) / 2))
    bg = bg.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BICUBIC)
    bg = Image.fromarray((np.asarray(bg, np.float32) * .55).astype(np.uint8))
    fw = int(round(cw * H / SH))
    fg = src.resize((fw, H), Image.BICUBIC, box=(xa, 0, xb, SH))
    fx = (W - fw) // 2
    # soft shadow at the panel edges
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rectangle([fx - 6, 0, fx + fw + 6, H], fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(24))
    bg = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), bg, sh)
    bg.paste(fg, (fx, 0))
    return bg


def captions(fr, i):
    ga = 0.0
    for s0, s1, lab, cap in CAPTIONS:
        t_in = s0 + (XF + 4 if s0 == 0 else 6)
        if s0 <= i < s1:
            ga = max(ga, fade(i, max(0, s0 - 2), s1 + 2, 12, 12))
    if ga > 0:
        fr.alpha_composite(with_alpha(BGRAD, ga))
    for s0, s1, lab, cap in CAPTIONS:
        t_in = s0 + (XF + 4 if s0 == 0 else 6)
        if t_in - 1 <= i < s1:
            a = fade(i, t_in, s1 - 2, 14, 12)
            rise = 12 * (1 - es((i - t_in) / 18))
            put(fr, text_img(lab, "InterDisplay-Medium", 26, (226, 186, 120), .12), W / 2, 872, a, rise, "c")
            put(fr, text_img(cap, "ko", 54, WHITE, .01), W / 2, 922, a, rise, "c")


# ---------- cards
def card_logo(f):
    fr = Image.new("RGBA", (W, H), BG + (255,))
    a = fade(f, 4, None, 18)
    put_img(fr, LOGO_BIG, (W - LOGO_BIG.width) / 2, (H - LOGO_BIG.height) / 2 + 10 * (1 - es(f / 24)), a)
    return fr


def card_hero(f):
    fr = Image.new("RGBA", (W, H), BG + (255,))
    place_product(fr, P_HERO, W - 150 - P_HERO.width, (H - P_HERO.height) // 2 + 10, fade(f, 0, None, 20))
    x = 150
    for k, (txt, fn, sz, col, tr, y) in enumerate([
        ("6년근 국내산 홍삼", "ko", 30, GOLD, .08, 300),
        ("진홍삼", "ko", 128, RED, .02, 350),
        ("데일리 밸런스", "ko", 76, INK, .02, 510),
        ("Korean Red Ginseng Herbal Blend", "Inter-Medium", 24, GOLD, .08, 620),
        ("홍삼에 대추 · 배 · 벌꿀을 더한 하루 한 포", "ko", 34, INK, 0, 690),
    ]):
        t = 6 + k * 6
        put(fr, text_img(txt, fn, sz, col, tr), x, y, fade(f, t, None, 16), 14 * (1 - es((f - t) / 20)))
    line_a = fade(f, 30, None, 16)
    rect(fr, (x, 668, x + int(80 * line_a), 670), GOLD, line_a)
    return fr


def info_rows(fr, f, x, y0, rows, t0, step=6, gap=78):
    for k, (lab, val) in enumerate(rows):
        t = t0 + k * step
        a = fade(f, t, None, 16)
        rise = 10 * (1 - es((f - t) / 20))
        y = y0 + k * gap
        put(fr, text_img(lab, "ko", 26, GOLD, .04), x, y + 6, a, rise)
        put(fr, text_img(val, "ko", 36, INK), x + 190, y, a, rise)
        if k < len(rows) - 1:
            rect(fr, (x, y + gap - 18, x + 690, y + gap - 17), (225, 214, 198), a)


def card_info(f):
    fr = Image.new("RGBA", (W, H), BG + (255,))
    place_product(fr, P_SET, 1010 - P_SET.width, (H - P_SET.height) // 2, fade(f, 0, None, 20))
    x = 1080
    put(fr, text_img("PRODUCT INFO", "Inter-SemiBold", 20, GOLD, .3), x, 240, fade(f, 6, None, 16))
    put(fr, text_img("제품 정보", "ko", 64, RED), x, 276, fade(f, 10, None, 16), 12 * (1 - es((f - 10) / 20)))
    info_rows(fr, f, x, 410, [
        ("내용량", "1,500mL (50mL × 30포)"),
        ("열량", "685kcal (총 내용량 기준)"),
        ("섭취방법", "하루 1포, 그대로 드세요"),
        ("보관방법", "직사광선을 피해 실온 보관"),
        ("소비기한", "제조일로부터 24개월"),
        ("식품유형", "인삼 · 홍삼음료"),
    ], 18)
    return fr


def chip(fr, x, y, txt, a, rise, filled=False, size=30):
    im = text_img(txt, "ko", size, WHITE if filled else INK)
    w = int(im._w) + 44
    h = size + 30
    if a > .003:
        rect(fr, (x, int(y + rise), x + w, int(y + rise) + h), RED if filled else (240, 232, 220), a, h // 2)
        put(fr, im, x + 22, y + 13 + rise - size * .08, a)
    return w


def card_ingredients(f):
    fr = Image.new("RGBA", (W, H), BG + (255,))
    place_product(fr, P_POUCH, 190, (H - P_POUCH.height) // 2, fade(f, 0, None, 20))
    x = 900
    put(fr, text_img("INGREDIENTS", "Inter-SemiBold", 20, GOLD, .3), x, 150, fade(f, 6, None, 16))
    put(fr, text_img("원재료", "ko", 64, RED), x, 186, fade(f, 10, None, 16), 12 * (1 - es((f - 10) / 20)))
    t = 18
    a = fade(f, t, None, 16); r = 10 * (1 - es((f - t) / 20))
    chip(fr, x, 300, "6년근 국내산 홍삼농축액", a, r, True, 34)
    rows = [["대추", "배", "벌꿀", "구기자", "영지버섯"], ["생강", "헛개나무열매", "대보농축액"],
            ["프락토올리고당", "난소화성말토덱스트린"]]
    y = 396
    for ri, row in enumerate(rows):
        cx = x
        for ci, name in enumerate(row):
            t = 26 + ri * 8 + ci * 3
            cx += chip(fr, cx, y, name, fade(f, t, None, 14), 8 * (1 - es((f - t) / 18))) + 14
        y += 78
    # nutrition + package claims
    t = 58
    a = fade(f, t, None, 16); r = 10 * (1 - es((f - t) / 20))
    rect(fr, (x, 650, x + 880, 651), (225, 214, 198), a)
    put(fr, text_img("영양 정보 (1포 50mL 기준)", "ko", 26, GOLD, .04), x, 680, a, r)
    put(fr, text_img("지방 0g  ·  콜레스테롤 0mg  ·  나트륨 0mg", "ko", 34, INK), x, 724, a, r)
    t = 68
    a = fade(f, t, None, 16); r = 10 * (1 - es((f - t) / 20))
    rect(fr, (x, 800, x + 880, 801), (225, 214, 198), a)
    cx = x
    for k, c in enumerate(["보존료 무첨가", "인공색소 무첨가", "합성향료 무첨가", "카페인 없음"]):
        tt = t + 4 + k * 3
        cx += chip(fr, cx, 830, c, fade(f, tt, None, 14), 8 * (1 - es((f - tt) / 18)), size=26) + 12
    return fr


def card_final(f):
    fr = Image.new("RGBA", (W, H), BG + (255,))
    place_product(fr, P_FIN, W - 90 - P_FIN.width, (H - P_FIN.height) // 2, fade(f, 0, None, 20))
    x = 150
    items = [("하루 한 포,", "ko", 84, INK, 330), ("나를 챙기는 시간", "ko", 84, RED, 440),
             ("진홍삼 데일리 밸런스", "ko", 40, INK, 600)]
    for k, (txt, fn, sz, col, y) in enumerate(items):
        t = 8 + k * 8
        put(fr, text_img(txt, fn, sz, col, .02 if fn == "ko" else .12), x, y, fade(f, t, None, 18), 14 * (1 - es((f - t) / 22)))
    t = 32
    put_img(fr, LOGO_SMALL, x, 664 + 14 * (1 - es((f - t) / 22)), fade(f, t, None, 18))
    put(fr, text_img("Made in Korea", "Inter-Medium", 22, GOLD, .12), x + LOGO_SMALL.width + 22, 680, fade(f, t + 4, None, 18))
    la = fade(f, 30, None, 16)
    rect(fr, (x, 572, x + int(90 * la), 574), GOLD, la)
    # badges
    cx = x
    for k, b in enumerate(["6년근 국내산", "HACCP 식품안전관리인증"]):
        t = 44 + k * 5
        cx += chip(fr, cx, 790, b, fade(f, t, None, 14), 8 * (1 - es((f - t) / 18)), False, 26) + 12
    # fade to black at the very end
    out = es((f - (FIN_LEN - 20)) / 20)
    if out > 0:
        fr = Image.blend(fr, Image.new("RGBA", (W, H), (0, 0, 0, 255)), out)
    return fr


def finish(img, vig=True):
    a = np.asarray(img.convert("RGB"), np.float32)
    if vig:
        a = a * VIG
    a += DITHER[np.random.randint(0, 4)]
    return np.clip(a, 0, 255).astype(np.uint8)


def footage_layer(src, i):
    fr = compose_footage(src, i).convert("RGBA")
    captions(fr, i)
    return fr


def render(g, src):
    """src: graded source frame for footage index g-F0 (or None)."""
    i = g - F0
    if g < LOGO:
        fr = card_logo(g)
        if g < 10:  # fade up from black
            fr = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), fr, es(g / 10))
        return finish(fr, False)
    if g < F0:
        fr = card_hero(g - LOGO)
        x = es((g - LOGO) / 15)
        if x < 1:
            fr = Image.blend(card_logo(g), fr, x)
        return finish(fr, False)
    if g < F0 + XF:  # hero dissolves into footage
        return finish(Image.blend(card_hero(g - LOGO), footage_layer(src, i), es((g - F0) / XF)))
    if g < C1:
        return finish(footage_layer(src, i))
    if g < FEND:  # footage dissolves into card 1
        return finish(Image.blend(footage_layer(src, i), card_info(g - C1), es((g - C1) / XF)))
    if g < C2:
        return finish(card_info(g - C1), False)
    if g < C2 + XC:
        return finish(Image.blend(card_info(g - C1), card_ingredients(g - C2), es((g - C2) / XC)), False)
    if g < FIN:
        return finish(card_ingredients(g - C2), False)
    if g < FIN + XC:
        return finish(Image.blend(card_ingredients(g - C2), card_final(g - FIN), es((g - FIN) / XC)), False)
    return finish(card_final(g - FIN), False)


def main():
    if sys.argv[1] == "preview":
        out = os.path.join(HERE, "prev_ko"); os.makedirs(out, exist_ok=True)
        for gs in sys.argv[2:]:
            g = int(gs)
            src = footage_seek(g - F0) if F0 <= g < FEND else None
            Image.fromarray(render(g, src)).save(f"{out}/f{g:05d}.png")
        return
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                            "-pix_fmt", "yuv420p", sys.argv[2]], stdin=subprocess.PIPE)
    reader = footage_reader()
    for g in range(TOTAL):
        src = next(reader) if F0 <= g < FEND else None
        enc.stdin.write(render(g, src).tobytes())
        if g % 100 == 0:
            print("frame", g, "/", TOTAL, flush=True)
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    main()
