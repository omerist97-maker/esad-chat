"""Network Marketing — "Hayatına göre çalış" 20 sn dikey (1080x1920) motion graphics videosu #2.

Açık zeminli, kalın sert gölgeli (neo-brütalist) tipografi; 150 BPM vuruşlarına senkron.
Kullanım: python3 render.py music.wav out.mp4   |   python3 render.py x kare.png <kare_no>
"""
import math
import subprocess
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
DUR = 20.0
BEAT = 0.4  # 150 BPM

FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_MED = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"

CREAM = (244, 239, 230)
BLACK = (17, 17, 17)
ORANGE = (255, 90, 31)
GREEN = (0, 196, 120)
BLUE = (47, 91, 255)
PINK = (255, 120, 180)
GRAY = (52, 52, 58)
RED = (230, 40, 40)
LX = 80  # sol hizalama kenarı


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, d):
    return clamp((t - t0) / d)


def ease_out_expo(p):
    return 1 if p >= 1 else 1 - 2 ** (-10 * p)


def ease_out_back(p, s=1.9):
    p -= 1
    return 1 + p * p * ((s + 1) * p + s)


def ease_in_out(p):
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


# ---------------------------------------------------------------- metin
@lru_cache(maxsize=None)
def font(size, path=FONT):
    return ImageFont.truetype(path, size)


@lru_cache(maxsize=None)
def text_img(text, size, color, shadow=None, depth=0, path=FONT, maxw=920):
    """Metin görseli; isteğe bağlı sert (offset) gölge ile."""
    while True:
        f = font(size, path)
        x0, y0, x1, y1 = f.getbbox(text)
        if x1 - x0 <= maxw or size < 20:
            break
        size = int(size * 0.94)
    if shadow is not None and depth == 0:
        depth = max(6, size // 16)
    pad = 8
    img = Image.new("RGBA", (x1 - x0 + 2 * pad + depth, y1 - y0 + 2 * pad + depth), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if shadow is not None:
        d.text((pad - x0 + depth, pad - y0 + depth), text, font=f, fill=shadow + (255,))
    d.text((pad - x0, pad - y0), text, font=f, fill=color + (255,))
    return img


@lru_cache(maxsize=None)
def pill_img(text, size, fg, bg, shadow=None, padx=40, pady=22, radius=None):
    t = text_img(text, size, fg)
    dep = 10 if shadow else 0
    w, h = t.width + 2 * padx, t.height + 2 * pady
    img = Image.new("RGBA", (w + dep, h + dep), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = radius if radius is not None else h // 2
    if shadow:
        d.rounded_rectangle((dep, dep, w + dep - 1, h + dep - 1), radius=r, fill=shadow + (255,))
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=bg + (255,), outline=BLACK + (255,), width=5)
    img.alpha_composite(t, (padx, pady))
    return img


@lru_cache(maxsize=None)
def stamp_img(text, size, color, rot):
    t = text_img(text, size, color)
    w, h = t.width + 80, t.height + 50
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((6, 6, w - 7, h - 7), radius=18, outline=color + (255,), width=12)
    img.alpha_composite(t, (40, 25))
    return img.rotate(rot, expand=True, resample=Image.BICUBIC)


def put(layer, img, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if alpha <= 0.01 or scale <= 0.01:
        return
    if abs(scale - 1) > 0.005:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.1:
        img = img.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 0.99:
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(cx - img.width / 2), int(cy - img.height / 2)
    sx, sy = max(0, -x), max(0, -y)
    ex, ey = min(img.width, W - x), min(img.height, H - y)
    if ex <= sx or ey <= sy:
        return
    layer.alpha_composite(img.crop((sx, sy, ex, ey)), (x + sx, y + sy))


def put_left(layer, img, x, cy, **kw):
    put(layer, img, x + img.width / 2, cy, **kw)


def reveal_left(layer, img, x, cy, p):
    """Maske içinden aşağıdan kayarak, sola hizalı açılan metin."""
    if p <= 0:
        return
    off = int((1 - ease_out_expo(p)) * img.height)
    tmp = Image.new("RGBA", img.size, (0, 0, 0, 0))
    tmp.paste(img, (0, off))
    put_left(layer, tmp, x, cy)


def slam_left(layer, img, x, cy, t, t0, rot=0.0):
    if t < t0:
        return
    p = prog(t, t0, 0.2)
    s = 1 + 1.3 * (1 - ease_out_expo(p))
    put(layer, img, x + img.width / 2, cy, scale=s, rot=rot, alpha=clamp(p * 3))


def slam(layer, img, cx, cy, t, t0, rot=0.0):
    if t < t0:
        return
    p = prog(t, t0, 0.2)
    put(layer, img, cx, cy, scale=1 + 1.3 * (1 - ease_out_expo(p)), rot=rot, alpha=clamp(p * 3))


# ---------------------------------------------------------------- dokular
rng = np.random.default_rng(5)
GRAIN = rng.normal(0, 3, (H + 64, W + 64, 1)).astype(np.float32)


def dot_grid(d, color, t=0.0, gap=60, r=3):
    off = (t * 40) % gap
    for y in range(-gap, H + gap, gap):
        for x in range(0, W + gap, gap):
            d.ellipse((x - r, y + off - r, x + r, y + off + r), fill=color)


# ---------------------------------------------------------------- ikonlar
def draw_alarm(d, cx, cy, s, c, t):
    k = s / 100
    j = 10 * k * math.sin(t * 90)
    cx += j
    for side in (-1, 1):
        d.pieslice((cx + side * 55 * k - 35 * k, cy - 105 * k, cx + side * 55 * k + 35 * k, cy - 35 * k),
                   200 if side < 0 else 250, 290 if side < 0 else 340, fill=c)
    d.ellipse((cx - 80 * k, cy - 80 * k, cx + 80 * k, cy + 80 * k), outline=c, width=int(14 * k))
    d.line((cx, cy, cx, cy - 50 * k), fill=c, width=int(12 * k))
    d.line((cx, cy, cx + 38 * k, cy + 10 * k), fill=c, width=int(12 * k))
    d.line((cx - 60 * k, cy + 70 * k, cx - 80 * k, cy + 100 * k), fill=c, width=int(12 * k))
    d.line((cx + 60 * k, cy + 70 * k, cx + 80 * k, cy + 100 * k), fill=c, width=int(12 * k))
    # titreşim çizgileri
    for side in (-1, 1):
        for i in range(2):
            r = 110 * k + i * 25 * k
            d.arc((cx - r, cy - r, cx + r, cy + r), (-30 if side > 0 else 150), (30 if side > 0 else 210),
                  fill=c, width=int(8 * k))


def draw_laptop(d, cx, cy, s, c, screen):
    k = s / 100
    d.rounded_rectangle((cx - 120 * k, cy - 80 * k, cx + 120 * k, cy + 70 * k), radius=int(12 * k), fill=c)
    d.rectangle((cx - 104 * k, cy - 64 * k, cx + 104 * k, cy + 54 * k), fill=screen)
    d.polygon([(cx - 150 * k, cy + 80 * k), (cx + 150 * k, cy + 80 * k), (cx + 165 * k, cy + 105 * k),
               (cx - 165 * k, cy + 105 * k)], fill=c)
    # ekranda wifi
    for i, r in enumerate((60, 40, 20)):
        d.arc((cx - r * k, cy + 20 * k - r * k, cx + r * k, cy + 20 * k + r * k), 225, 315, fill=c, width=int(9 * k))
    d.ellipse((cx - 7 * k, cy + 13 * k, cx + 7 * k, cy + 27 * k), fill=c)


def draw_pin(d, x, y, s, fill, outline=BLACK):
    k = s / 100
    d.ellipse((x - 45 * k, y - 140 * k, x + 45 * k, y - 50 * k), fill=fill, outline=outline, width=int(7 * k))
    d.polygon([(x - 38 * k, y - 78 * k), (x + 38 * k, y - 78 * k), (x, y)], fill=fill, outline=outline)
    d.line([(x - 38 * k, y - 78 * k), (x, y), (x + 38 * k, y - 78 * k)], fill=outline, width=int(7 * k))
    d.ellipse((x - 16 * k, y - 111 * k, x + 16 * k, y - 79 * k), fill=CREAM)


def draw_person(d, cx, cy, s, c):
    k = s / 100
    d.ellipse((cx - 22 * k, cy - 62 * k, cx + 22 * k, cy - 18 * k), fill=c)
    d.pieslice((cx - 42 * k, cy - 8 * k, cx + 42 * k, cy + 76 * k), 180, 360, fill=c)


# ---------------------------------------------------------------- olaylar
HITS = [(0.0, 18), (0.4, 18), (0.8, 18), (1.2, 26), (1.6, 34), (2.0, 14), (4.8, 10), (8.0, 12),
        (8.4, 8), (8.8, 8), (9.2, 14), (9.6, 10), (10.0, 10), (10.4, 10), (10.8, 10), (12.0, 16),
        (12.8, 36), (13.6, 12), (16.0, 12), (16.4, 12), (16.8, 20), (17.6, 40)]
FLASHES = [(1.6, 0.9), (12.8, 0.9), (17.6, 0.8)]


def shake(t):
    dx = dy = 0.0
    for t0, s in HITS:
        if t >= t0:
            e = s * math.exp(-(t - t0) * 16)
            dx += e * math.sin(t * 91 + t0 * 3)
            dy += e * math.cos(t * 79 + t0)
    return dx, dy


def zoom_punch(t):
    return 1 + sum((s / 380) * math.exp(-(t - t0) * 11) for t0, s in HITS if t >= t0)


def flash(t):
    return max([s * math.exp(-(t - t0) * 9) for t0, s in FLASHES if t >= t0] + [0])


# ---------------------------------------------------------------- sahneler
def scene_monday(t, bg, fg):
    """0–1.6: ALARM. TRAFİK. MESAİ. YETER!"""
    d = ImageDraw.Draw(fg)
    put(fg, text_img("PAZARTESİ • 07:00", 54, (170, 170, 175), path=FONT_MED), W / 2, 330)
    draw_alarm(d, W / 2, 560, 120, (200, 200, 205), t)
    words = [(0.0, "ALARM.", (210, 210, 215), -6), (0.4, "TRAFİK.", (210, 210, 215), 5),
             (0.8, "MESAİ.", (210, 210, 215), -4), (1.2, "YETER!", ORANGE, 3)]
    cur = [w for w in words if t >= w[0]][-1]
    t0, txt, c, rot = cur
    p = prog(t, t0, 0.14)
    img = stamp_img(txt, 170 if txt != "YETER!" else 210, c, rot)
    put(fg, img, W / 2, 1080, scale=1 + 0.8 * (1 - ease_out_expo(p)), alpha=clamp(p * 4))
    # sayaç gibi küçük alt yazılar
    n = len([w for w in words if t >= w[0]])
    put(fg, text_img(f"{n}/4  RUTİN", 44, (120, 120, 128), path=FONT_MED), W / 2, 1400)


DAYS = [("PZT", "SPOR + KAHVE", GREEN), ("SAL", "İŞ • 3 SAAT", BLUE), ("ÇAR", "AİLE GÜNÜ", PINK),
        ("PER", "İŞ • EVDEN", BLUE), ("CUM", "SEYAHAT", ORANGE), ("CMT", "İŞ • SAHİLDEN", BLUE),
        ("PAZ", "DİNLEN", GREEN)]


def scene_calendar(t, bg, fg):
    """1.6–4.8: TAKVİMİN SENİN."""
    dot_grid(ImageDraw.Draw(bg), (222, 214, 200), t)
    d = ImageDraw.Draw(fg)
    slam_left(fg, text_img("TAKVİMİN", 150, BLACK), LX, 360, t, 1.6)
    slam_left(fg, text_img("SENİN.", 190, ORANGE, shadow=BLACK), LX, 540, t, 2.0, rot=2)
    y0, rh = 740, 140
    for i, (day, act, c) in enumerate(DAYS):
        y = y0 + i * rh
        tr = 2.2 + i * 0.12
        pr = ease_out_expo(prog(t, tr, 0.3))
        if pr <= 0:
            continue
        d.line((LX, y + rh / 2 + 4, LX + (W - 2 * LX) * pr, y + rh / 2 + 4), fill=(200, 192, 178), width=3)
        put_left(fg, text_img(day, 60, BLACK), LX, y, alpha=pr)
        # önce eski mesai yazısı, sonra üstüne yeni aktivite
        ta = 2.8 + i * 0.2
        pa = prog(t, ta, 0.28)
        if pa <= 0:
            put_left(fg, text_img("09:00 – 18:00", 46, (160, 154, 144), path=FONT_MED), LX + 190, y, alpha=pr)
        else:
            x = LX + 190 + (1 - ease_out_expo(pa)) * 700
            put_left(fg, pill_img(act, 46, BLACK, c, shadow=BLACK), x, y)


BLOCKS = [(5.2, 7, "SPOR", GREEN), (5.6, 10, "İŞ", BLUE), (6.0, 13.5, "ÇOCUKLAR", ORANGE),
          (6.4, 16.5, "KAHVE", PINK), (6.8, 20.5, "İŞ", BLUE)]


def hour_y(h):
    return 800 + (h - 6) / 18 * 960


def scene_planner(t, bg, fg):
    """4.8–8.0: GÜNÜNÜ SEN TASARLA."""
    dot_grid(ImageDraw.Draw(bg), (222, 214, 200), t)
    d = ImageDraw.Draw(fg)
    reveal_left(fg, text_img("GÜNÜNÜ", 130, BLACK), LX, 290, prog(t, 4.8, 0.3))
    slam_left(fg, text_img("SEN", 150, BLUE, shadow=BLACK), LX, 440, t, 5.0)
    reveal_left(fg, text_img("TASARLA.", 130, BLACK), LX, 590, prog(t, 5.15, 0.3))
    # zaman çizelgesi
    rx = LX + 150
    pr = ease_in_out(prog(t, 4.8, 0.5))
    d.line((rx, hour_y(6), rx, hour_y(6) + (hour_y(24) - hour_y(6)) * pr), fill=BLACK, width=6)
    for h in range(6, 25, 3):
        if pr >= (h - 6) / 18:
            y = hour_y(h)
            d.line((rx - 20, y, rx + 20, y), fill=BLACK, width=6)
            put(fg, text_img(f"{h:02d}:00", 34, BLACK, path=FONT_MED), LX + 50, y)
    # şimdi çizgisi
    ny = hour_y(6 + 18 * prog(t, 4.8, 3.2))
    d.line((rx, ny, W - LX, ny), fill=ORANGE, width=4)
    d.ellipse((rx - 14, ny - 14, rx + 14, ny + 14), fill=ORANGE)
    # sürüklenerek yerine oturan bloklar
    for t0, h, label, c in BLOCKS:
        if t < t0 - 0.25:
            continue
        p = ease_out_back(prog(t, t0 - 0.25, 0.4), 1.4)
        y = hour_y(h)
        x = rx + 50 + max(0.0, 1 - p) * 900
        img = pill_img(label, 52, BLACK, c, shadow=BLACK, radius=22, padx=44)
        put_left(fg, img, x, y)
        if prog(t, t0 - 0.25, 0.4) < 1:  # parmak imleci
            fx, fy = x + img.width - 40, y + 20
            d.ellipse((fx - 34, fy - 34, fx + 34, fy + 34), fill=(255, 255, 255, 170), outline=BLACK, width=5)


CITIES = [(9.6, "İSTANBUL", (300, 1080)), (10.0, "BODRUM", (700, 1260)), (10.4, "KAPADOKYA", (430, 1430)),
          (10.8, "BALİ", (800, 960))]


def scene_office(t, bg, fg):
    """8.0–11.2: LAPTOP + İNTERNET = OFİS  →  harita pinleri."""
    bd = ImageDraw.Draw(bg)
    d = ImageDraw.Draw(fg)
    if t < 9.6:
        bd.rectangle((0, 0, W, H), fill=BLUE)
        dot_grid(bd, (70, 112, 255), t)
        sp = ease_out_back(prog(t, 8.0, 0.35))
        if sp > 0.05:
            draw_laptop(d, W / 2, 470, 190 * sp, CREAM, BLUE)
        slam_left(fg, text_img("LAPTOP", 170, CREAM, shadow=BLACK), LX, 820, t, 8.0)
        slam_left(fg, text_img("+ İNTERNET", 150, CREAM, shadow=BLACK), LX, 1010, t, 8.4)
        slam_left(fg, text_img("=", 170, ORANGE, shadow=BLACK), LX, 1230, t, 8.8)
        slam_left(fg, text_img("OFİS.", 260, ORANGE, shadow=BLACK), LX + 140, 1230, t, 9.2, rot=-3)
        return
    dot_grid(bd, (222, 214, 200), t)
    put_left(fg, text_img("BUGÜN OFİSİN:", 90, BLACK), LX, 330)
    shown = [c for c in CITIES if t >= c[0]]
    # kesikli rota
    for (ta, _, a), (tb, _, b) in zip(shown, shown[1:]):
        p = ease_in_out(prog(t, tb, 0.3))
        n = 18
        for i in range(int(n * p)):
            if i % 2 == 0:
                x0 = a[0] + (b[0] - a[0]) * i / n
                y0 = a[1] + (b[1] - a[1]) * i / n - 120 * math.sin(math.pi * i / n)
                x1 = a[0] + (b[0] - a[0]) * (i + 1) / n
                y1 = a[1] + (b[1] - a[1]) * (i + 1) / n - 120 * math.sin(math.pi * (i + 1) / n)
                d.line((x0, y0, x1, y1), fill=BLACK, width=6)
    for i, (t0, name, (x, y)) in enumerate(shown):
        p = prog(t, t0, 0.25)
        drop = (1 - ease_out_back(p, 2.5)) * -300
        cur = i == len(shown) - 1
        d.ellipse((x - 30, y - 10, x + 30, y + 10), fill=(200, 192, 178))
        draw_pin(d, x, y + drop, 120 if cur else 80, ORANGE if cur else (190, 182, 170))
    t0, name, (px, py) = shown[-1]
    for i in range(3):
        q = ((t - t0) / 0.9 + i / 3) % 1
        r = 40 + q * 320
        a = int(200 * (1 - q))
        d.ellipse((px - r, py - r * 0.45, px + r, py + r * 0.45), outline=ORANGE + (a,), width=6)
    slam(fg, text_img(name, 170, ORANGE, shadow=BLACK), W / 2, 1720, t, t0)


def scene_boss(t, bg, fg):
    """11.2–12.8: PATRONUN KİM Mİ? AYNAYA BAK."""
    d = ImageDraw.Draw(fg)
    z = 1 + 0.08 * prog(t, 11.2, 1.6)
    reveal_left(fg, text_img("PATRONUN", 150, CREAM), LX, 380, prog(t, 11.2, 0.3))
    reveal_left(fg, text_img("KİM Mİ?", 150, CREAM), LX, 550, prog(t, 11.6, 0.3))
    pm = ease_out_back(prog(t, 12.0, 0.35), 1.4)
    if pm > 0.02:
        mw, mh = 520 * z * pm, 720 * z * pm
        cx, cy = W / 2, 1180
        box = (cx - mw / 2, cy - mh / 2, cx + mw / 2, cy + mh / 2)
        d.rounded_rectangle((box[0] + 16, box[1] + 16, box[2] + 16, box[3] + 16), radius=int(260 * pm), fill=ORANGE)
        d.rounded_rectangle(box, radius=int(260 * pm), fill=(60, 64, 80), outline=CREAM, width=12)
        # yansıma parıltısı
        sx = box[0] + (mw + 300) * prog(t, 12.1, 0.5) - 150
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).rounded_rectangle(box, radius=int(260 * pm), fill=255)
        shine = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(shine).polygon([(sx, box[1]), (sx + 90, box[1]), (sx - 160, box[3]), (sx - 250, box[3])],
                                      fill=(255, 255, 255, 110))
        shine.putalpha(Image.fromarray(np.minimum(np.asarray(shine.getchannel("A")), np.asarray(mask))))
        fg.alpha_composite(shine)
        draw_person(d, cx, cy + 40 * pm, 380 * pm, CREAM)
    if t >= 12.25:
        slam(fg, text_img("AYNAYA BAK.", 120, ORANGE), W / 2, 1680, t, 12.25)


def scene_team(t, bg, fg):
    """12.8–16.0: TEK BAŞINA DEĞİL — EKİBİNLE BÜYÜ."""
    bd = ImageDraw.Draw(bg)
    bd.rectangle((0, 0, W, H), fill=ORANGE)
    d = ImageDraw.Draw(fg)
    slam_left(fg, text_img("TEK BAŞINA", 130, CREAM, shadow=BLACK), LX, 300, t, 12.8)
    slam_left(fg, text_img("DEĞİL.", 130, CREAM, shadow=BLACK), LX, 440, t, 13.2)
    cols, rows, cw, ch = 5, 5, 184, 150
    gx, gy = W / 2 - (cols - 1) * cw / 2, 720
    cells = [(c, r) for r in range(rows) for c in range(cols)]
    center = (2, 2)
    cells.sort(key=lambda cr: (cr[0] - center[0]) ** 2 + (cr[1] - center[1]) ** 2)
    count = 0
    for i, (c, r) in enumerate(cells):
        t0 = 13.0 + (0 if i == 0 else 0.4 + i * 0.065)
        p = prog(t, t0, 0.3)
        if p <= 0:
            continue
        count += 1
        s = 120 * ease_out_back(p)
        x, y = gx + c * cw, gy + r * ch + 50
        you = i == 0
        col = CREAM if you else BLACK
        if you:
            d.ellipse((x - 80, y - 85, x + 80, y + 75), outline=CREAM, width=8)
        draw_person(d, x, y, s * (1.15 if you else 1), col)
    # sayaç
    put(fg, pill_img(f"EKİP: {count}", 50, BLACK, CREAM, shadow=BLACK), W - 250, 1770)
    if t >= 14.4:
        reveal_left(fg, text_img("EKİBİNLE BÜYÜ.", 110, BLACK), LX, 1590, prog(t, 14.4, 0.3))


def scene_outro(t, bg, fg):
    """16.0–20.0: İŞİNE GÖRE DEĞİL, HAYATINA GÖRE ÇALIŞ. + CTA"""
    bd = ImageDraw.Draw(bg)
    final = t >= 17.6
    if final:
        p = ease_out_expo(prog(t, 17.6, 0.35))
        r = p * 2300
        bd.ellipse((W / 2 - r, 1300 - r, W / 2 + r, 1300 + r), fill=ORANGE)
    txt = BLACK if final else CREAM
    slam_left(fg, text_img("İŞİNE GÖRE DEĞİL,", 104, txt), LX, 420, t, 16.0)
    slam_left(fg, text_img("HAYATINA GÖRE", 120, txt), LX, 570, t, 16.4)
    slam_left(fg, text_img("ÇALIŞ.", 290, CREAM if final else ORANGE, shadow=BLACK), LX, 800, t, 16.8, rot=-2)
    if final:
        pp = ease_out_back(prog(t, 17.75, 0.35))
        pulse = 1 + 0.035 * math.sin((t - 17.6) * math.pi / BEAT)
        put(fg, pill_img("ŞİMDİ KATIL", 96, CREAM, BLACK, shadow=CREAM, padx=70, pady=36), W / 2, 1220,
            scale=max(0.01, pp) * pulse)
        reveal_left(fg, text_img("Detaylı bilgi için DM'den yaz", 58, BLACK, path=FONT_MED), W / 2 - 400, 1400,
                    prog(t, 18.0, 0.35))
        d = ImageDraw.Draw(fg)
        for i in range(3):
            a = clamp(math.sin(t * 8 - i * 0.9) * 0.5 + 0.5) * prog(t, 18.2, 0.3)
            y = 1510 + i * 48
            d.line([(W / 2 - 42, y), (W / 2, y + 32), (W / 2 + 42, y)], fill=BLACK + (int(255 * a),), width=13)


SCENES = [
    (0.0, 1.6, scene_monday, GRAY),
    (1.6, 4.8, scene_calendar, CREAM),
    (4.8, 8.0, scene_planner, CREAM),
    (8.0, 11.2, scene_office, CREAM),
    (11.2, 12.8, scene_boss, BLACK),
    (12.8, 16.0, scene_team, ORANGE),
    (16.0, 20.01, scene_outro, BLACK),
]


def render_frame(t):
    idx = max(i for i, s in enumerate(SCENES) if t >= s[0])
    t0, _, fn, color = SCENES[idx]
    bg = Image.new("RGBA", (W, H), color + (255,))
    # sahne geçişi: önceki rengin üzerinde büyüyen daire
    if idx > 0 and t - t0 < 0.22:
        prev = SCENES[idx - 1][3]
        if prev != color:
            p = ease_out_expo((t - t0) / 0.22)
            bg = Image.new("RGBA", (W, H), prev + (255,))
            r = 60 + p * 1150
            ImageDraw.Draw(bg).ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=color)
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(t, bg, fg)
    frame = Image.alpha_composite(bg, fg)

    # hikâye ilerleme çubuğu + etiket
    dark = color in (CREAM,) or (fn is scene_outro and t >= 17.6)
    ui = BLACK if dark else CREAM
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((40, 50, W - 40, 60), radius=5, fill=ui + (70,))
    d.rounded_rectangle((40, 50, 40 + (W - 80) * t / DUR, 60), radius=5, fill=ui)
    frame.alpha_composite(text_img("#ÖZGÜRÇALIŞ", 38, ui, path=FONT_MED), (40, 86))

    z = zoom_punch(t)
    dx, dy = shake(t)
    if z > 1.002 or abs(dx) > 0.5 or abs(dy) > 0.5:
        cw, ch = W / z, H / z
        x0 = (W - cw) / 2 - dx / z
        y0 = (H - ch) / 2 - dy / z
        frame = frame.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)

    arr = np.asarray(frame.convert("RGB")).astype(np.float32)
    ox, oy = (int(t * 7.5) * 37) % 64, (int(t * 7.5) * 23) % 64  # gren 4 karede bir değişir
    arr += GRAIN[oy:oy + H, ox:ox + W]
    f = flash(t)
    if f > 0.01:
        arr = arr * (1 - f) + 255 * f
    return np.clip(arr, 0, 255).astype(np.uint8)


def main():
    music, out = sys.argv[1], sys.argv[2]
    if out.endswith(".png"):
        Image.fromarray(render_frame(int(sys.argv[3]) / FPS)).save(out)
        return
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", music,
           "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        proc.stdin.write(render_frame(i / FPS).tobytes())
    proc.stdin.close()
    proc.wait()


if __name__ == "__main__":
    main()
