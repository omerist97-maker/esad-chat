"""Network Marketing — "Özgür saatler, özgür ortam" 20 sn dikey (1080x1920) motion graphics videosu.

Kullanım: python3 render.py music.wav out.mp4
Kareler PIL ile çizilir ve doğrudan ffmpeg'e aktarılır.
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

# Renk paleti
NAVY = (11, 11, 30)
INK = (8, 8, 16)
WHITE = (255, 255, 255)
YELLOW = (255, 212, 0)
MAGENTA = (255, 46, 136)
CYAN = (0, 229, 255)
PURPLE = (108, 52, 255)
RED = (255, 50, 70)


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


def ease_in(p):
    return p ** 3


# ---------------------------------------------------------------- metin
@lru_cache(maxsize=None)
def font(size, path=FONT):
    return ImageFont.truetype(path, size)


@lru_cache(maxsize=None)
def text_img(text, size, color, path=FONT, maxw=980):
    while True:
        f = font(size, path)
        x0, y0, x1, y1 = f.getbbox(text)
        if x1 - x0 <= maxw or size < 20:
            break
        size = int(size * 0.94)
    pad = 10
    img = Image.new("RGBA", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((pad - x0, pad - y0), text, font=f, fill=color + (255,))
    return img


def put(layer, img, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    if alpha <= 0.01 or scale <= 0.01:
        return
    if abs(scale - 1) > 0.005:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.BILINEAR)
    if abs(rot) > 0.1:
        img = img.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 0.99:
        a = img.getchannel("A").point(lambda v: int(v * alpha))
        img = img.copy()
        img.putalpha(a)
    x, y = int(cx - img.width / 2), int(cy - img.height / 2)
    # negatif koordinatlara kırpma
    sx, sy = max(0, -x), max(0, -y)
    ex, ey = min(img.width, W - x), min(img.height, H - y)
    if ex <= sx or ey <= sy:
        return
    layer.alpha_composite(img.crop((sx, sy, ex, ey)), (x + sx, y + sy))


def put_reveal(layer, img, cx, cy, p, from_below=True):
    """Maske içinden aşağıdan yukarı kayarak açılan metin."""
    if p <= 0:
        return
    e = ease_out_expo(p)
    off = int((1 - e) * img.height * (1 if from_below else -1))
    tmp = Image.new("RGBA", img.size, (0, 0, 0, 0))
    tmp.paste(img, (0, off))
    put(layer, tmp, cx, cy)


def slam(layer, text, size, color, cx, cy, t, t0, rot=0.0):
    """Büyükten küçüğe çarparak giren metin."""
    if t < t0:
        return
    p = prog(t, t0, 0.22)
    s = 1 + 1.6 * (1 - ease_out_expo(p))
    put(layer, text_img(text, size, color), cx, cy, scale=s, rot=rot, alpha=clamp(p * 3))


# ---------------------------------------------------------------- arka plan
@lru_cache(maxsize=None)
def gradient(c1, c2):
    y = np.linspace(0, 1, H)[:, None, None]
    g = np.array(c1)[None, None] * (1 - y) + np.array(c2)[None, None] * y
    return np.broadcast_to(g, (H, W, 3)).astype(np.uint8)


def vignette_mask():
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
    return np.clip(1.15 - d * 0.55, 0.35, 1)[:, :, None].astype(np.float32)


VIGNETTE = vignette_mask()

rng = np.random.default_rng(3)
PARTICLES = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(30, 140), rng.uniform(2, 6),
              rng.uniform(0.25, 0.8)) for _ in range(70)]


def draw_particles(d, t, color):
    for x0, y0, sp, r, a in PARTICLES:
        y = (y0 - sp * t) % H
        x = x0 + 20 * math.sin(t * 1.3 + y0)
        c = tuple(int(v * a) for v in color)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)


def draw_rings(d, t, cx, cy, color, start, every=BEAT, width=8):
    """Her vuruşta merkezden genişleyen halkalar."""
    k = math.floor((t - start) / every)
    for i in range(k - 2, k + 1):
        if i < 0:
            continue
        p = (t - start - i * every) / (every * 3)
        if not 0 <= p <= 1:
            continue
        r = 80 + ease_out_expo(p) * 900
        a = (1 - p) ** 2
        c = tuple(int(v * a) for v in color)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=c, width=width)


def draw_stripes(d, t, color, speed=300, gap=140, width=36):
    off = (t * speed) % gap
    for i in range(-20, 30):
        x = i * gap + off
        d.polygon([(x, 0), (x + width, 0), (x + width - H * 0.5, H), (x - H * 0.5, H)], fill=color)


# ---------------------------------------------------------------- ikonlar
def draw_clock(d, cx, cy, r, hour_a, min_a, color, width=14, ticks=True):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=width)
    if ticks:
        for i in range(12):
            a = i * math.pi / 6
            r1 = r * (0.78 if i % 3 == 0 else 0.86)
            d.line((cx + r1 * math.sin(a), cy - r1 * math.cos(a),
                    cx + r * 0.93 * math.sin(a), cy - r * 0.93 * math.cos(a)),
                   fill=color, width=max(3, width // 2))
    for a, ln, wd in ((hour_a, 0.5, width), (min_a, 0.75, int(width * 0.7))):
        d.line((cx, cy, cx + r * ln * math.sin(a), cy - r * ln * math.cos(a)), fill=color, width=wd)
    d.ellipse((cx - width, cy - width, cx + width, cy + width), fill=color)


def icon_house(d, cx, cy, s, c):
    w = 14 * s / 100
    d.line([(cx - 90 * s / 100, cy - 5 * s / 100), (cx, cy - 90 * s / 100), (cx + 90 * s / 100, cy - 5 * s / 100)],
           fill=c, width=int(w), joint="curve")
    d.rectangle((cx - 65 * s / 100, cy - 20 * s / 100, cx + 65 * s / 100, cy + 80 * s / 100), outline=c, width=int(w))
    d.rectangle((cx - 18 * s / 100, cy + 25 * s / 100, cx + 18 * s / 100, cy + 80 * s / 100), fill=c)


def icon_cup(d, cx, cy, s, c, t):
    k = s / 100
    w = int(14 * k)
    d.rounded_rectangle((cx - 60 * k, cy - 20 * k, cx + 45 * k, cy + 80 * k), radius=int(18 * k), outline=c, width=w)
    d.arc((cx + 20 * k, cy, cx + 85 * k, cy + 55 * k), -90, 90, fill=c, width=w)
    for i in range(3):
        x = cx - 35 * k + i * 30 * k
        pts = [(x + 10 * k * math.sin(t * 8 + j * 0.9 + i), cy - 40 * k - j * 14 * k) for j in range(6)]
        d.line(pts, fill=c, width=int(8 * k), joint="curve")


def icon_beach(d, cx, cy, s, c, t):
    k = s / 100
    w = int(12 * k)
    d.ellipse((cx - 40 * k, cy - 95 * k, cx + 40 * k, cy - 15 * k), fill=c)
    for i in range(8):
        a = i * math.pi / 4 + t * 1.5
        d.line((cx + 55 * k * math.cos(a), cy - 55 * k + 55 * k * math.sin(a),
                cx + 75 * k * math.cos(a), cy - 55 * k + 75 * k * math.sin(a)), fill=c, width=int(8 * k))
    for row in range(3):
        y0 = cy + 25 * k + row * 28 * k
        pts = [(cx - 100 * k + i * 10 * k, y0 + 9 * k * math.sin(i * 0.6 + t * 6 + row)) for i in range(21)]
        d.line(pts, fill=c, width=w, joint="curve")


def icon_globe(d, cx, cy, s, c, t):
    k = s / 100
    w = int(10 * k)
    r = 85 * k
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=c, width=w)
    d.line((cx - r, cy, cx + r, cy), fill=c, width=w)
    for i in range(3):
        ph = (t * 0.6 + i / 3) % 1
        ew = r * abs(math.cos(ph * math.pi))
        d.ellipse((cx - ew, cy - r, cx + ew, cy + r), outline=c, width=max(3, w // 2))
    # yörüngedeki uçak
    a = t * 3
    px, py = cx + 130 * k * math.cos(a), cy + 55 * k * math.sin(a)
    ang = math.atan2(55 * math.cos(a), -130 * math.sin(a))
    pts = [(14, 0), (-10, -9), (-6, 0), (-10, 9)]
    pts = [(px + 2.2 * k * (x * math.cos(ang) - y * math.sin(ang)),
            py + 2.2 * k * (x * math.sin(ang) + y * math.cos(ang))) for x, y in pts]
    d.polygon(pts, fill=c)


# ---------------------------------------------------------------- ağ grafiği
def build_network():
    nodes = [(0.0, 0.0, 0, None)]  # (açı, yarıçap, halka, ebeveyn)
    rings = [(6, 210), (12, 380), (24, 540)]
    prev = [0]
    for ri, (n, r) in enumerate(rings, 1):
        cur = []
        for i in range(n):
            a = i * 2 * math.pi / n + ri * 0.3
            parent = prev[int(i * len(prev) / n)]
            nodes.append((a, r, ri, parent))
            cur.append(len(nodes) - 1)
        prev = cur
    return nodes


NET = build_network()
RING_T = {1: 12.15, 2: 12.65, 3: 13.4}


def draw_network(d, t, cx, cy):
    rot = (t - 12) * 0.12
    pos = []
    for a, r, ri, _ in NET:
        pos.append((cx + r * math.cos(a + rot), cy + r * 0.9 * math.sin(a + rot)))
    # kenarlar
    for i, (a, r, ri, par) in enumerate(NET):
        if par is None:
            continue
        p = ease_in_out(prog(t, RING_T[ri], 0.45))
        if p <= 0:
            continue
        x0, y0 = pos[par]
        x1, y1 = pos[i]
        col = (YELLOW, MAGENTA, CYAN)[ri - 1]
        d.line((x0, y0, x0 + (x1 - x0) * p, y0 + (y1 - y0) * p), fill=col, width=6 - ri)
    # düğümler
    for i, (a, r, ri, _) in enumerate(NET):
        t0 = 12.0 if ri == 0 else RING_T[ri] + 0.35
        p = prog(t, t0, 0.35)
        if p <= 0:
            continue
        rr = (46, 26, 18, 13)[ri] * max(0, ease_out_back(p))
        pulse = 1 + 0.18 * math.exp(-((t - 12) % BEAT) * 8)
        rr *= pulse
        x, y = pos[i]
        col = (WHITE, YELLOW, MAGENTA, CYAN)[ri]
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col)


# ---------------------------------------------------------------- olaylar
SHAKES = [(2.0, 34), (2.5, 16), (4.5, 14), (7.5, 10), (8.0, 10), (8.5, 10), (9.0, 14),
          (12.0, 38), (12.5, 14), (16.0, 16), (16.5, 22), (18.0, 40)]
FLASHES = [(2.0, 1.0), (12.0, 1.0), (18.0, 0.9), (7.0, 0.35), (10.0, 0.3), (16.0, 0.45)]


def shake(t):
    dx = dy = 0.0
    for t0, s in SHAKES:
        if t >= t0:
            e = s * math.exp(-(t - t0) * 14)
            dx += e * math.sin(t * 97 + t0)
            dy += e * math.cos(t * 83 + t0 * 2)
    return int(dx), int(dy)


def flash(t):
    v = 0.0
    for t0, s in FLASHES:
        if t >= t0:
            v = max(v, s * math.exp(-(t - t0) * 9))
    return v


def zoom_punch(t):
    z = 1.0
    for t0, s in SHAKES:
        if t >= t0:
            z += (s / 400) * math.exp(-(t - t0) * 10)
    return z


# ---------------------------------------------------------------- sahneler
def scene_intro(t, bg, fg):
    """0-2 sn: 09:00 - 18:00 rutini."""
    bd = ImageDraw.Draw(bg)
    draw_particles(bd, t, (60, 20, 30))
    fd = ImageDraw.Draw(fg)
    blink = (int(t * 4) % 2 == 0) or t > 1.5
    jit = 0
    if t > 1.5:  # glitch
        jit = int(18 * math.sin(t * 140))
    put_reveal(fg, text_img("HER GÜN", 92, WHITE), W / 2, 520, prog(t, 0.05, 0.4))
    put_reveal(fg, text_img("AYNI MESAİ?", 120, WHITE), W / 2, 650, prog(t, 0.25, 0.4))
    if blink:
        c = RED
        put(fg, text_img("09:00", 300, c), W / 2 + jit, 1000, scale=1 + 0.04 * math.sin(t * 12))
    p = prog(t, 0.5, 0.4)
    put(fg, text_img("—  18:00  —", 120, (255, 120, 130)), W / 2 - jit, 1240, alpha=p)
    # alttaki ilerleme çubuğu (mesai dolumu)
    pw = 760 * ease_in_out(prog(t, 0.2, 1.7))
    fd.rounded_rectangle((W / 2 - 380, 1400, W / 2 + 380, 1430), radius=15, outline=(120, 40, 50), width=4)
    fd.rounded_rectangle((W / 2 - 380, 1400, W / 2 - 380 + max(30, pw), 1430), radius=15, fill=RED)


def scene_no_hours(t, bg, fg):
    """2-4 sn: MESAİ YOK."""
    bd = ImageDraw.Draw(bg)
    draw_rings(bd, t, W / 2, H / 2, (70, 60, 0), 2.0)
    fd = ImageDraw.Draw(fg)
    # üstü çizilen saatler
    put(fg, text_img("09:00 – 18:00", 130, (150, 150, 170)), W / 2, 560, alpha=1 - prog(t, 3.4, 0.4))
    p = ease_out_expo(prog(t, 2.05, 0.3))
    if p > 0:
        fd.line((W / 2 - 470, 610, W / 2 - 470 + 940 * p, 510), fill=YELLOW, width=26)
    slam(fg, "MESAİ", 250, WHITE, W / 2, 900, t, 2.0)
    slam(fg, "YOK.", 330, YELLOW, W / 2, 1180, t, 2.5, rot=-4)
    # alt bilgi
    put_reveal(fg, text_img("PATRON YOK • KART BASMA YOK", 52, WHITE, FONT_MED), W / 2, 1420, prog(t, 3.0, 0.4))


def scene_your_time(t, bg, fg):
    """4-7 sn: Saatlerini SEN belirle."""
    bd = ImageDraw.Draw(bg)
    draw_particles(bd, t, (80, 50, 160))
    fd = ImageDraw.Draw(fg)
    # yavaşlayarak dönen saat
    lt = t - 4.0
    spin = 34 * (1 - math.exp(-lt * 1.6)) / 1.6
    sp = ease_out_back(prog(t, 4.0, 0.45))
    r = 230 * max(0, sp)
    if r > 5:
        draw_clock(fd, W / 2, 1240, r, spin / 12 + 0.4, spin, WHITE, width=16)
        # zamanı gösteren yay (yörünge)
        fd.arc((W / 2 - r - 40, 1240 - r - 40, W / 2 + r + 40, 1240 + r + 40),
               -90, -90 + (spin * 57.3) % 360, fill=YELLOW, width=14)
    put_reveal(fg, text_img("SAATLERİNİ", 140, WHITE), W / 2, 430, prog(t, 4.0, 0.35))
    slam(fg, "SEN", 280, YELLOW, W / 2, 640, t, 4.5, rot=3)
    put_reveal(fg, text_img("BELİRLE", 160, WHITE), W / 2, 830, prog(t, 5.0, 0.35))
    # vuruşlarda saat etiketleri
    tags = [("06:00", -330, 1600, 5.5, CYAN), ("14:00", 0, 1660, 6.0, MAGENTA), ("23:00", 330, 1600, 6.5, YELLOW)]
    for txt, dx, y, t0, c in tags:
        if t >= t0:
            p = ease_out_back(prog(t, t0, 0.3))
            img = text_img(txt, 70, INK)
            pill = Image.new("RGBA", (img.width + 50, img.height + 30), (0, 0, 0, 0))
            ImageDraw.Draw(pill).rounded_rectangle((0, 0, pill.width - 1, pill.height - 1), radius=40, fill=c + (255,))
            pill.alpha_composite(img, (25, 15))
            put(fg, pill, W / 2 + dx, y, scale=max(0.01, p))


PLACES = [  # (zaman, kelime, arka plan, metin rengi, ikon)
    (7.5, "EVİN", MAGENTA, WHITE, "house"),
    (8.0, "BİR KAFE", CYAN, INK, "cup"),
    (8.5, "SAHİL", YELLOW, INK, "beach"),
    (9.0, "DÜNYANIN\nHER YERİ", PURPLE, WHITE, "globe"),
]


def scene_places(t, bg, fg):
    """7-10 sn: Ofisin neresi?"""
    cur = None
    for item in PLACES:
        if t >= item[0]:
            cur = item
    fd = ImageDraw.Draw(fg)
    bd = ImageDraw.Draw(bg)
    if cur is None:
        draw_stripes(bd, t, (24, 24, 60))
        put_reveal(fg, text_img("OFİSİN", 200, WHITE), W / 2, 820, prog(t, 7.0, 0.3))
        put_reveal(fg, text_img("NERESİ?", 200, YELLOW), W / 2, 1050, prog(t, 7.12, 0.3))
        return
    t0, word, bgc, tc, icon = cur
    # tam ekran renk bloğu, alttan yukarı silme
    p = ease_out_expo(prog(t, t0, 0.18))
    prev_bg = NAVY
    idx = PLACES.index(cur)
    if idx > 0:
        prev_bg = PLACES[idx - 1][2]
    bd.rectangle((0, 0, W, H), fill=prev_bg)
    bd.rectangle((0, H * (1 - p), W, H), fill=bgc)
    darker = tuple(int(v * 0.85) for v in bgc)
    if p >= 1:
        draw_stripes(bd, t, darker, speed=500)
    put(fg, text_img("OFİSİN:", 90, tc), W / 2, 420, alpha=p)
    # ikon
    s = 230 * max(0, ease_out_back(prog(t, t0 + 0.04, 0.3)))
    if s > 3:
        if icon == "house":
            icon_house(fd, W / 2, 800, s, tc)
        elif icon == "cup":
            icon_cup(fd, W / 2, 800, s, tc, t)
        elif icon == "beach":
            icon_beach(fd, W / 2, 800, s, tc, t)
        else:
            icon_globe(fd, W / 2, 800, s * 1.2, tc, t)
    lines = word.split("\n")
    for i, ln in enumerate(lines):
        slam(fg, ln, 200 if len(lines) == 1 else 150, tc, W / 2, 1230 + i * 170, t, t0 + i * 0.12)


def scene_split(t, bg, fg):
    """10-12 sn: ÖZGÜR SAATLER / ÖZGÜR ORTAM."""
    bd = ImageDraw.Draw(bg)
    fd = ImageDraw.Draw(fg)
    p1 = ease_out_expo(prog(t, 10.0, 0.4))
    p2 = ease_out_expo(prog(t, 10.5, 0.4))
    # üst yarı soldan, alt yarı sağdan
    bd.rectangle((-W + W * p1, 0, W * p1, H / 2), fill=MAGENTA)
    bd.rectangle((W - W * p2, H / 2, 2 * W - W * p2, H), fill=CYAN)
    off1 = (1 - p1) * -W
    off2 = (1 - p2) * W
    breathe = 1 + 0.03 * math.sin((t - 10) * math.pi * 2)
    if p1 > 0:
        draw_clock(fd, W / 2 + off1, 380, 150 * breathe, (t - 10) * 2, (t - 10) * 9, WHITE, width=14)
        put(fg, text_img("ÖZGÜR", 150, WHITE), W / 2 + off1, 640)
        put(fg, text_img("SAATLER", 150, YELLOW), W / 2 + off1, 790)
    if p2 > 0:
        icon_globe(fd, W / 2 + off2, 1260, 150 * breathe, INK, t)
        put(fg, text_img("ÖZGÜR", 150, INK), W / 2 + off2, 1500)
        put(fg, text_img("ORTAM", 150, WHITE), W / 2 + off2, 1650)
    # build: ortada büyüyen "+"
    if t > 11.0:
        k = ease_in(prog(t, 11.0, 1.0))
        s = 60 + 140 * k
        rot = k * 360
        img = text_img("+", 200, YELLOW)
        put(fg, img, W / 2, H / 2, scale=s / 140, rot=rot)


def scene_boss(t, bg, fg):
    """12-16 sn: Kendi işinin patronu ol + ağ."""
    bd = ImageDraw.Draw(bg)
    draw_rings(bd, t, W / 2, 1250, (40, 30, 90), 12.0, every=BEAT * 2, width=5)
    fd = ImageDraw.Draw(fg)
    draw_network(fd, t, W / 2, 1250)
    put_reveal(fg, text_img("KENDİ İŞİNİN", 120, WHITE), W / 2, 330, prog(t, 12.0, 0.35))
    slam(fg, "PATRONU OL", 165, YELLOW, W / 2, 500, t, 12.5)
    if t >= 14.0:
        put_reveal(fg, text_img("EKİBİNİ KUR • BİRLİKTE BÜYÜ", 54, WHITE, FONT_MED), W / 2, 640, prog(t, 14.0, 0.4))


def scene_outro(t, bg, fg):
    """16-20 sn: Özgürlüğü seç + CTA."""
    bd = ImageDraw.Draw(bg)
    fd = ImageDraw.Draw(fg)
    # sarı diyagonal silme
    p = ease_out_expo(prog(t, 16.0, 0.35))
    x = -H * 0.6 + (W + H * 1.2) * p
    bd.polygon([(-H, 0), (x, 0), (x - H * 0.6, H), (-H, H)], fill=YELLOW)
    if p >= 1:
        draw_stripes(bd, t, (245, 200, 0), speed=200, gap=200, width=60)
    slam(fg, "ÖZGÜRLÜĞÜ", 175, INK, W / 2, 640, t, 16.0)
    slam(fg, "SEÇ.", 380, INK, W / 2, 920, t, 16.5, rot=-5)
    if t >= 18.0:
        pp = ease_out_back(prog(t, 18.0, 0.35))
        img = text_img("HEMEN BAŞLA", 92, YELLOW)
        box = Image.new("RGBA", (img.width + 110, img.height + 70), (0, 0, 0, 0))
        ImageDraw.Draw(box).rounded_rectangle((0, 0, box.width - 1, box.height - 1), radius=60, fill=INK + (255,))
        box.alpha_composite(img, (55, 35))
        pulse = 1 + 0.04 * math.sin((t - 18) * math.pi * 4)
        put(fg, box, W / 2, 1270, scale=max(0.01, pp) * pulse)
        put_reveal(fg, text_img("Detaylı bilgi için DM'den yaz", 58, INK, FONT_MED), W / 2, 1440, prog(t, 18.3, 0.4))
        # aşağı oklar
        for i in range(3):
            a = clamp(math.sin((t * 4 - i * 0.5)) * 0.5 + 0.5) * prog(t, 18.5, 0.3)
            yy = 1540 + i * 45
            fd.line([(W / 2 - 40, yy), (W / 2, yy + 30), (W / 2 + 40, yy)], fill=INK + (int(255 * a),), width=12)


SCENES = [
    (0.0, 2.0, scene_intro, ((25, 6, 14), (8, 4, 10))),
    (2.0, 4.0, scene_no_hours, (NAVY, (20, 10, 40))),
    (4.0, 7.0, scene_your_time, ((40, 16, 110), (12, 8, 40))),
    (7.0, 10.0, scene_places, (NAVY, (20, 14, 60))),
    (10.0, 12.0, scene_split, (INK, INK)),
    (12.0, 16.0, scene_boss, ((14, 10, 40), (4, 4, 14))),
    (16.0, 20.01, scene_outro, (INK, INK)),
]


def render_frame(t):
    for t0, t1, fn, (c1, c2) in SCENES:
        if t0 <= t < t1:
            break
    bg = Image.fromarray(gradient(c1, c2)).convert("RGBA")
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(t, bg, fg)

    # parıltı (glow): yarım çözünürlükte bulanıklaştırılmış ön plan
    small = fg.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(7))
    glow = small.resize((W, H), Image.BILINEAR)
    frame = Image.alpha_composite(bg, glow)
    frame = Image.alpha_composite(frame, fg)

    # zoom punch + kamera sarsıntısı
    z = zoom_punch(t)
    dx, dy = shake(t)
    if z > 1.002 or dx or dy:
        cw, ch = W / z, H / z
        x0 = (W - cw) / 2 - dx / z
        y0 = (H - ch) / 2 - dy / z
        frame = frame.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BILINEAR)

    arr = np.asarray(frame.convert("RGB")).astype(np.float32)
    arr *= VIGNETTE
    # RGB ayrışması (chromatic aberration) vuruşlarda
    ca = int(14 * flash(t))
    if ca > 1:
        arr[:, ca:, 0] = arr[:, :-ca, 0]
        arr[:, :-ca, 2] = arr[:, ca:, 2]
    f = flash(t)
    if f > 0.01:
        arr = arr * (1 - f) + 255 * f
    return np.clip(arr, 0, 255).astype(np.uint8)


def main():
    music, out = sys.argv[1], sys.argv[2]
    start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    end = int(sys.argv[4]) if len(sys.argv) > 4 else int(DUR * FPS)
    if out.endswith(".png"):
        Image.fromarray(render_frame(start / FPS)).save(out)
        return
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", music,
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(start, end):
        proc.stdin.write(render_frame(i / FPS).tobytes())
    proc.stdin.close()
    proc.wait()


if __name__ == "__main__":
    main()
