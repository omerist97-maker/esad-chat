"""Network Marketing — "Ekibimiz" 20 sn Instagram Reels (1080x1920) motion graphics videosu.

6 başlık, numaralı sahneler (01–06), zümrüt yeşili + altın stil; 120 BPM vuruşlarına senkron.
Kullanım: python3 render.py music.wav out.mp4   |   python3 render.py x kare.png <kare_no>
"""
import math
import subprocess
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
DUR = 20.0
BEAT = 0.5

FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_MED = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"

TEAL_TOP = (6, 46, 50)
TEAL_BOT = (2, 16, 20)
TEAL = (20, 120, 120)
TEAL_LT = (90, 210, 195)
GOLD = (245, 197, 66)
GOLD_DK = (190, 140, 30)
WHITE = (255, 255, 255)
CORAL = (255, 107, 107)
RED = (235, 50, 60)
AVATAR_COLORS = [GOLD, TEAL_LT, CORAL, (160, 140, 255), WHITE, (255, 170, 90)]


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
def text_img(text, size, color, path=FONT, maxw=940, outline=0):
    while True:
        f = font(size, path)
        x0, y0, x1, y1 = f.getbbox(text, stroke_width=outline)
        if x1 - x0 <= maxw or size < 20:
            break
        size = int(size * 0.94)
    pad = 10
    img = Image.new("RGBA", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if outline:
        d.text((pad - x0, pad - y0), text, font=f, fill=(0, 0, 0, 0), stroke_width=outline,
               stroke_fill=color + (255,))
    else:
        d.text((pad - x0, pad - y0), text, font=f, fill=color + (255,))
    return img


@lru_cache(maxsize=None)
def pill_img(text, size, fg, bg, padx=46, pady=26, path=FONT):
    t = text_img(text, size, fg, path)
    w, h = t.width + 2 * padx, t.height + 2 * pady
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=bg + (255,))
    img.alpha_composite(t, (padx, pady))
    return img


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
    ex, ey = min(img.width, layer.width - x), min(img.height, layer.height - y)
    if ex <= sx or ey <= sy:
        return
    layer.alpha_composite(img.crop((sx, sy, ex, ey)), (x + sx, y + sy))


def reveal(layer, img, cx, cy, p):
    if p <= 0:
        return
    off = int((1 - ease_out_expo(p)) * img.height)
    tmp = Image.new("RGBA", img.size, (0, 0, 0, 0))
    tmp.paste(img, (0, off))
    put(layer, tmp, cx, cy)


def pop(layer, img, cx, cy, t, t0, d=0.35, rot=0.0):
    if t < t0:
        return
    p = prog(t, t0, d)
    put(layer, img, cx, cy, scale=max(0.01, ease_out_back(p)), rot=rot, alpha=clamp(p * 4))


def slam(layer, img, cx, cy, t, t0, rot=0.0):
    if t < t0:
        return
    p = prog(t, t0, 0.22)
    put(layer, img, cx, cy, scale=1 + 1.5 * (1 - ease_out_expo(p)), rot=rot, alpha=clamp(p * 3))


# ---------------------------------------------------------------- arka plan
def make_bg():
    y = np.linspace(0, 1, H)[:, None, None]
    g = np.array(TEAL_TOP)[None, None] * (1 - y) + np.array(TEAL_BOT)[None, None] * y
    return Image.fromarray(np.broadcast_to(g, (H, W, 3)).astype(np.uint8)).convert("RGBA")


def make_bokeh():
    rng = np.random.default_rng(9)
    img = Image.new("RGBA", (W + 400, H + 400), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(26):
        x, y = rng.uniform(0, W + 400), rng.uniform(0, H + 400)
        r = rng.uniform(30, 140)
        c = (GOLD if rng.random() < 0.5 else TEAL_LT) + (int(rng.uniform(25, 60)),)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    return img.filter(ImageFilter.GaussianBlur(18))


BG = make_bg()
BOKEH = make_bokeh()


def background(t):
    bg = BG.copy()
    ox = int(200 + 150 * math.sin(t * 0.35))
    oy = int(200 + 180 * math.cos(t * 0.27))
    bg.alpha_composite(BOKEH.crop((ox, oy, ox + W, oy + H)))
    return bg


# ---------------------------------------------------------------- ikon çizimleri
def person(d, cx, cy, s, c, ring=None):
    k = s / 100
    if ring:
        d.ellipse((cx - 70 * k, cy - 70 * k, cx + 70 * k, cy + 70 * k), fill=ring)
    d.ellipse((cx - 22 * k, cy - 48 * k, cx + 22 * k, cy - 4 * k), fill=c)
    d.chord((cx - 42 * k, cy + 4 * k, cx + 42 * k, cy + 88 * k), 180, 360, fill=c)


def icon_starters(fg, d, u, cx, cy):
    """01 — tek tek ekibe katılan kişiler, '+1' etiketleri."""
    for i in range(9):
        c, r = i % 3, i // 3
        t0 = 0.15 + i * 0.11
        p = prog(u, t0, 0.35)
        if p <= 0:
            continue
        s = 105 * max(0.0, ease_out_back(p))
        x, y = cx + (c - 1) * 240, cy + (r - 1) * 220
        person(d, x, y, s, TEAL_BOT, ring=AVATAR_COLORS[i % len(AVATAR_COLORS)])
        q = prog(u, t0, 0.7)
        if q < 1:
            put(fg, text_img("+1", 54, GOLD), x + 70, y - 70 - 70 * q, alpha=1 - q)


def icon_not_alone(fg, d, u, cx, cy):
    """02 — merkezdeki kişinin etrafında birleşen ekip."""
    n = 6
    pts = [(cx + 300 * math.cos(i * 2 * math.pi / n - math.pi / 2 + u * 0.3),
            cy + 300 * math.sin(i * 2 * math.pi / n - math.pi / 2 + u * 0.3)) for i in range(n)]
    for i, (x, y) in enumerate(pts):
        p = ease_in_out(prog(u, 0.45 + i * 0.08, 0.3))
        if p > 0:
            d.line((cx, cy, cx + (x - cx) * p, cy + (y - cy) * p), fill=GOLD + (200,), width=6)
    pulse = (u * 2) % 1
    r = 130 + pulse * 260
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD + (int(150 * (1 - pulse)),), width=6)
    s = 150 * max(0.0, ease_out_back(prog(u, 0.05, 0.4)))
    if s > 1:
        person(d, cx, cy, s, TEAL_BOT, ring=GOLD)
    for i, (x, y) in enumerate(pts):
        p = prog(u, 0.45 + i * 0.08, 0.35)
        if p > 0:
            person(d, x, y, 90 * max(0.0, ease_out_back(p)), TEAL_BOT, ring=AVATAR_COLORS[(i + 1) % 6])


def star_pts(cx, cy, ro, ri, n=5, rot=-math.pi / 2):
    return [(cx + (ro if j % 2 == 0 else ri) * math.cos(rot + j * math.pi / n),
             cy + (ro if j % 2 == 0 else ri) * math.sin(rot + j * math.pi / n)) for j in range(2 * n)]


def icon_sponsors(fg, d, u, cx, cy):
    """03 — dönen ışınlar, kalkan + yıldız, yükselen oklar."""
    a0 = u * 0.6
    for i in range(12):
        a = a0 + i * math.pi / 6
        p = ease_out_expo(prog(u, 0.05, 0.5))
        r = 420 * p
        d.polygon([(cx, cy), (cx + r * math.cos(a - 0.09), cy + r * math.sin(a - 0.09)),
                   (cx + r * math.cos(a + 0.09), cy + r * math.sin(a + 0.09))], fill=GOLD + (45,))
    s = max(0.0, ease_out_back(prog(u, 0.1, 0.45)))
    if s > 0.02:
        k = 2.6 * s
        sh = [(cx, cy - 110 * k), (cx + 90 * k, cy - 75 * k), (cx + 85 * k, cy + 20 * k),
              (cx, cy + 110 * k), (cx - 85 * k, cy + 20 * k), (cx - 90 * k, cy - 75 * k)]
        d.polygon(sh, fill=GOLD)
        inner = [(cx + (x - cx) * 0.82, cy + (y - cy) * 0.82) for x, y in sh]
        d.polygon(inner, fill=TEAL_BOT)
        d.polygon(star_pts(cx, cy - 5 * k, 55 * k, 23 * k), fill=GOLD)
    for i in range(3):
        p = prog(u, 0.6 + i * 0.15, 0.6)
        if p <= 0:
            continue
        x = cx + (i - 1) * 300
        y = cy + 380 - 80 * ease_out_expo(p) - (i % 2) * 40
        a = int(255 * min(1, p * 3))
        d.line([(x - 40, y + 30), (x, y - 10), (x + 40, y + 30)], fill=TEAL_LT + (a,), width=14)
        d.line([(x - 40, y + 70), (x, y + 30), (x + 40, y + 70)], fill=TEAL_LT + (a // 2,), width=14)


DAYS = ["P", "S", "Ç", "P", "C", "C", "P"]


def icon_online(fg, d, u, cx, cy):
    """04 — telefon ekranında canlı eğitim + haftanın 7 günü."""
    s = max(0.0, ease_out_back(prog(u, 0.05, 0.4)))
    if s > 0.02:
        pw, ph = 330 * s, 560 * s
        py = cy - 60
        d.rounded_rectangle((cx - pw / 2, py - ph / 2, cx + pw / 2, py + ph / 2), radius=int(50 * s), fill=WHITE)
        d.rounded_rectangle((cx - pw / 2 + 16 * s, py - ph / 2 + 16 * s, cx + pw / 2 - 16 * s, py + ph / 2 - 16 * s),
                            radius=int(36 * s), fill=TEAL)
        # oynat tuşu
        r = 70 * s * (1 + 0.06 * math.sin(u * 2 * math.pi * 2))
        d.ellipse((cx - r, py - r, cx + r, py + r), fill=GOLD)
        d.polygon([(cx - 22 * s, py - 35 * s), (cx - 22 * s, py + 35 * s), (cx + 38 * s, py)], fill=TEAL_BOT)
        # ilerleme çubuğu
        bw = pw - 80 * s
        d.rounded_rectangle((cx - bw / 2, py + 180 * s, cx + bw / 2, py + 192 * s), radius=6, fill=(255, 255, 255, 90))
        d.rounded_rectangle((cx - bw / 2, py + 180 * s, cx - bw / 2 + bw * (0.15 + 0.6 * u / 2), py + 192 * s),
                            radius=6, fill=GOLD)
        if s > 0.9 and int(u * 4) % 2 == 0 or u > 1.6:
            put(fg, pill_img("● CANLI", 40, WHITE, RED, padx=26, pady=14), cx + pw / 2 - 30, py - ph / 2 + 10)
    for i, dl in enumerate(DAYS):
        x = cx + (i - 3) * 128
        y = cy + 330
        on = u >= 0.45 + i * 0.13
        p = prog(u, 0.45 + i * 0.13, 0.25)
        r = 46 * (1 + 0.25 * math.sin(math.pi * p) if on else 1)
        d.ellipse((x - r, y - r, x + r, y + r), fill=GOLD if on else None,
                  outline=GOLD if on else (255, 255, 255, 110), width=5)
        put(fg, text_img(dl, 42, TEAL_BOT if on else WHITE), x, y)


def gear(d, cx, cy, r, teeth, rot, color, hole_r):
    pts = []
    for i in range(teeth):
        a = rot + i * 2 * math.pi / teeth
        st = 2 * math.pi / teeth
        for da, rr in ((0, r * 0.82), (st * 0.15, r), (st * 0.45, r), (st * 0.6, r * 0.82)):
            pts.append((cx + rr * math.cos(a + da), cy + rr * math.sin(a + da)))
    d.polygon(pts, fill=color)
    d.ellipse((cx - hole_r, cy - hole_r, cx + hole_r, cy + hole_r), fill=(0, 0, 0, 0))


def icon_team(fg, d, u, cx, cy):
    """05 — birbirine kenetlenip dönen dişliler."""
    spin = u * 2.2
    gears = [(cx - 120, cy - 70, 190, 12, spin, GOLD, 0.0),
             (cx + 190, cy - 230, 125, 8, -spin * 1.5 + 0.2, TEAL_LT, 0.15),
             (cx + 170, cy + 200, 140, 9, -spin * 1.36 + 0.1, WHITE, 0.3)]
    for x, y, r, n, rot, c, t0 in gears:
        s = max(0.0, ease_out_back(prog(u, 0.05 + t0, 0.4)))
        if s > 0.02:
            gear(d, x, y, r * s, n, rot, c, r * 0.32 * s)
    # alt: el sıkışan iki kişi yerine birleşen üç halka
    for i in range(3):
        p = ease_out_expo(prog(u, 0.7 + i * 0.12, 0.4))
        if p <= 0:
            continue
        x = cx + (i - 1) * 105 * p
        d.ellipse((x - 70, cy + 330 - 70, x + 70, cy + 330 + 70), outline=AVATAR_COLORS[i] + (230,), width=12)


def icon_results(fg, d, u, cx, cy):
    """06 — yükselen grafik, ok ve onay rozeti."""
    base = cy + 300
    heights = [140, 230, 300, 420, 560]
    bw = 120
    tops = []
    for i, hgt in enumerate(heights):
        p = ease_out_expo(prog(u, 0.1 + i * 0.1, 0.45))
        x = cx - 2 * 170 + i * 170
        top = base - hgt * p
        tops.append((x, top))
        d.rounded_rectangle((x - bw / 2, top, x + bw / 2, base), radius=18,
                            fill=(GOLD if i == len(heights) - 1 else TEAL_LT + (200,)))
    d.line((cx - 440, base + 6, cx + 440, base + 6), fill=WHITE + (160,), width=6)
    # yükselen ok
    p = ease_in_out(prog(u, 0.6, 0.6))
    if p > 0:
        pts = [(x, y - 70) for x, y in tops]
        seg = p * (len(pts) - 1)
        k = int(seg)
        drawn = pts[: k + 1]
        if k < len(pts) - 1:
            f = seg - k
            drawn.append((pts[k][0] + (pts[k + 1][0] - pts[k][0]) * f, pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f))
        d.line(drawn, fill=WHITE, width=14, joint="curve")
        hx, hy = drawn[-1]
        px, py = drawn[-2] if len(drawn) > 1 else (hx - 1, hy)
        a = math.atan2(hy - py, hx - px)
        d.polygon([(hx + 40 * math.cos(a), hy + 40 * math.sin(a)),
                   (hx + 34 * math.cos(a + 2.4), hy + 34 * math.sin(a + 2.4)),
                   (hx + 34 * math.cos(a - 2.4), hy + 34 * math.sin(a - 2.4))], fill=WHITE)
    s = max(0.0, ease_out_back(prog(u, 1.2, 0.35)))
    if s > 0.02:
        bx, by, r = cx - 250, cy - 230, 95 * s
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=GOLD)
        d.line([(bx - 42 * s, by + 2 * s), (bx - 10 * s, by + 34 * s), (bx + 46 * s, by - 30 * s)],
               fill=TEAL_BOT, width=int(20 * s), joint="curve")


# ---------------------------------------------------------------- sahneler
HEADINGS = [
    (["EKİBİMİZDE", "BİZİMLE", "BAŞLAYANLAR"], icon_starters),
    (["YALNIZ", "DEĞİLSİNİZ"], icon_not_alone),
    (["GÜÇLÜ", "SPONSORLAR"], icon_sponsors),
    (["HER GÜN", "ONLINE EĞİTİMLER"], icon_online),
    (["TAKIM", "ÇALIŞMASI"], icon_team),
    (["SONUÇ VEREN", "YÖNTEMLER"], icon_results),
]
RECAP = ["Bizimle başlayanlar", "Yalnız değilsiniz", "Güçlü sponsorlar", "Her gün online eğitim",
         "Takım çalışması", "Sonuç veren yöntemler"]


def scene_intro(t, fg):
    d = ImageDraw.Draw(fg)
    reveal(fg, text_img("NEDEN", 130, WHITE), W / 2, 560, prog(t, 0.05, 0.35))
    reveal(fg, text_img("BİZİM EKİBİMİZ?", 120, WHITE), W / 2, 710, prog(t, 0.3, 0.35))
    if t >= 0.9:
        p = prog(t, 0.9, 1.1)
        s = 0.6 + 0.5 * ease_in_out(p)
        put(fg, text_img("6", 520, GOLD), W / 2, 1150, scale=s, alpha=clamp(p * 4))
        put(fg, text_img("SEBEP", 110, GOLD), W / 2, 1480, alpha=prog(t, 1.2, 0.3))
    # dönen halka
    p = ease_out_expo(prog(t, 0.6, 0.6))
    r = 330 * p
    d.arc((W / 2 - r, 1150 - r, W / 2 + r, 1150 + r), t * 220, t * 220 + 260 * p, fill=GOLD, width=10)


def scene_heading(i, u, fg):
    lines, icon = HEADINGS[i]
    d = ImageDraw.Draw(fg)
    # büyük numara (dış çizgi)
    num = f"0{i + 1}"
    p = ease_out_expo(prog(u, 0.0, 0.4))
    put(fg, text_img(num, 260, GOLD, outline=5), 200 + (1 - p) * 200, 360, alpha=p)
    put(fg, text_img("/ 06", 56, (255, 255, 255), path=FONT_MED), 420, 400, alpha=prog(u, 0.15, 0.3) * 0.6)
    icon(fg, d, u, W / 2, 820)
    # başlık satırları
    y0 = 1380 if len(lines) == 2 else 1340
    for j, ln in enumerate(lines):
        col = GOLD if j == len(lines) - 1 else WHITE
        size = 115 if len(lines) == 3 else 140
        reveal(fg, text_img(ln, size, col), W / 2, y0 + j * (size + 25), prog(u, 0.12 + j * 0.12, 0.35))
    # alt çizgi
    lw = 300 * ease_out_expo(prog(u, 0.45, 0.4))
    yl = y0 + len(lines) * (150 if len(lines) == 2 else 140) + 5
    d.rounded_rectangle((W / 2 - lw / 2, yl, W / 2 + lw / 2, yl + 12), radius=6, fill=GOLD)


def scene_recap(t, fg):
    d = ImageDraw.Draw(fg)
    reveal(fg, text_img("HEPSİ BU EKİPTE", 110, GOLD), W / 2, 380, prog(t, 14.0, 0.35))
    for i, txt in enumerate(RECAP):
        y = 600 + i * 150
        t0 = 14.0 + i * 0.25
        p = prog(t, t0, 0.3)
        if p <= 0:
            continue
        x = 140 + (1 - ease_out_expo(p)) * -400
        r = 44 * max(0.0, ease_out_back(prog(t, t0 + 0.08, 0.3)))
        d.ellipse((x - 44, y - 44, x + 44, y + 44), outline=GOLD, width=6)
        if r > 2:
            d.ellipse((x - r, y - r, x + r, y + r), fill=GOLD)
            d.line([(x - 20, y + 2), (x - 5, y + 18), (x + 22, y - 14)], fill=TEAL_BOT, width=10, joint="curve")
        img = text_img(txt, 64, WHITE, path=FONT_MED, maxw=820)
        put(fg, img, x + 80 + img.width / 2, y, alpha=p)


def scene_outro(t, fg):
    d = ImageDraw.Draw(fg)
    slam(fg, text_img("SEN DE", 150, WHITE), W / 2, 420, t, 16.0)
    slam(fg, text_img("ARAMIZA", 170, WHITE), W / 2, 590, t, 16.25)
    slam(fg, text_img("KATIL!", 280, GOLD), W / 2, 820, t, 16.5, rot=-3)
    # ekip sırası
    for i in range(7):
        t0 = 17.0 + i * 0.07
        p = prog(t, t0, 0.35)
        if p <= 0:
            continue
        x = W / 2 + (i - 3) * 140
        bob = 10 * math.sin(t * 2 * math.pi + i)
        person(d, x, 1130 + bob, 80 * max(0.0, ease_out_back(p)), TEAL_BOT, ring=AVATAR_COLORS[i % 6])
    if t >= 17.5:
        pp = ease_out_back(prog(t, 17.5, 0.35))
        pulse = 1 + 0.035 * math.sin((t - 17.5) * math.pi * 4)
        put(fg, pill_img("BİLGİ İÇİN DM", 88, TEAL_BOT, GOLD, padx=70, pady=36), W / 2, 1360,
            scale=max(0.01, pp) * pulse)
        reveal(fg, text_img("Hemen yaz, birlikte başlayalım", 56, WHITE, path=FONT_MED), W / 2, 1520,
               prog(t, 17.9, 0.35))


def content(t):
    """Belirli bir andaki içerik katmanı (arka plansız)."""
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t < 2.0:
        scene_intro(t, fg)
    elif t < 14.0:
        i = int((t - 2.0) // 2)
        scene_heading(i, t - 2.0 - i * 2, fg)
    elif t < 16.0:
        scene_recap(t, fg)
    else:
        scene_outro(t, fg)
    return fg


BOUNDS = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0]
PUSH = 0.3


def progress_dots(frame, t):
    if not 2.0 <= t < 14.0:
        return
    d = ImageDraw.Draw(frame)
    cur = int((t - 2.0) // 2)
    for i in range(6):
        x = W / 2 + (i - 2.5) * 70
        y = 170
        if i == cur:
            d.rounded_rectangle((x - 26, y - 9, x + 26, y + 9), radius=9, fill=GOLD)
        elif i < cur:
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=GOLD + (200,))
        else:
            d.ellipse((x - 9, y - 9, x + 9, y + 9), outline=(255, 255, 255, 120), width=3)


HITS = [(2.0, 26), (16.0, 34), (16.25, 14), (16.5, 22), (17.5, 10)] + [(b, 10) for b in BOUNDS[1:6]]
FLASHES = [(2.0, 0.85), (16.0, 0.85)] + [(b, 0.25) for b in BOUNDS[1:7]]


def shake(t):
    dx = dy = 0.0
    for t0, s in HITS:
        if t >= t0:
            e = s * math.exp(-(t - t0) * 14)
            dx += e * math.sin(t * 97 + t0)
            dy += e * math.cos(t * 83 + t0 * 2)
    return dx, dy


def zoom_punch(t):
    return 1 + sum((s / 420) * math.exp(-(t - t0) * 10) for t0, s in HITS if t >= t0)


def flash(t):
    return max([s * math.exp(-(t - t0) * 9) for t0, s in FLASHES if t >= t0] + [0])


def render_frame(t):
    frame = background(t)
    # panel itme geçişi: önceki içerik sola çıkar, yeni içerik sağdan gelir
    b = next((b for b in BOUNDS if b <= t < b + PUSH), None)
    cur = content(t)
    if b is not None:
        e = ease_in_out((t - b) / PUSH)
        prev = content(b - 1 / FPS)
        tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        tmp.alpha_composite(prev.crop((int(e * W), 0, W, H)), (0, 0))
        off = int((1 - e) * W)
        if off < W:
            tmp.alpha_composite(cur.crop((0, 0, W - off, H)), (off, 0))
        cur = tmp
    small = cur.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6))
    glow = small.resize((W, H), Image.BILINEAR)
    frame.alpha_composite(glow)
    frame.alpha_composite(cur)
    progress_dots(frame, t)

    z = zoom_punch(t)
    dx, dy = shake(t)
    if z > 1.002 or abs(dx) > 0.5 or abs(dy) > 0.5:
        cw, ch = W / z, H / z
        x0 = (W - cw) / 2 - dx / z
        y0 = (H - ch) / 2 - dy / z
        frame = frame.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)
    arr = np.asarray(frame.convert("RGB")).astype(np.float32)
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
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        proc.stdin.write(render_frame(i / FPS).tobytes())
    proc.stdin.close()
    proc.wait()


if __name__ == "__main__":
    main()
