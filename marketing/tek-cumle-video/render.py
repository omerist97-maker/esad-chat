"""Kilo verme sürecinde iç ses — "Tek bir cümleyi değiştirince" Reels videosu (1080x1920, ~47 sn).

❌ cümleler karanlık zeminde gri bir 'iç ses' balonunda belirir, üstü çizilip buruşarak düşer;
ardından ekran sıcak renge döner ve ✅ cümle kelime kelime yazılır.
Kullanım: python3 render.py music.wav out.mp4   |   python3 render.py x kare.png <saniye>
"""
import math
import subprocess
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
DUR = 47.5

FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FONT_SEMI = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"

DARK_TOP, DARK_BOT = (34, 36, 48), (14, 15, 21)
WARM_TOP, WARM_BOT = (255, 246, 237), (250, 210, 186)
NEG_BUBBLE = (56, 60, 74)
NEG_TEXT = (196, 200, 212)
RED = (235, 87, 87)
GREEN = (38, 168, 108)
INK = (40, 42, 52)
PEACH = (255, 170, 130)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- metin içeriği
HOOK1 = "Tek bir cümleyi değiştirince *ne *olduğunu *göstereyim…"
HOOK2 = "Kilo verme sürecinde kendine en çok *hangi *cümleyi söylüyorsun?"
PAIRS = [
    ("“Ben zaten kilo veremiyorum.”",
     "“Bedenime iyi gelen alışkanlıkları *her *gün biraz daha geliştiriyorum.”"),
    ("“Yine dayanamadım, her şeyi mahvettim.”",
     "“Bir öğün bütün sürecimi *belirlemez. Bir sonraki seçimimle *devam *edebilirim.”"),
    ("“Benim iradem zayıf.”",
     "“Kendime uygun bir düzen kurmayı ve bu düzene sadık kalmayı *öğreniyorum.”"),
    ("“Çok fazla kilom var, bunu nasıl vereceğim?”",
     "“Büyük değişimler, *küçük *ama *sürdürülebilir adımlarla başlar.”"),
]
CLOSE_A = "Çünkü beynine sürekli"
CLOSE_WORDS = ["“Yapamıyorum”", "“Başaramıyorum”", "“Olmuyor”"]
CLOSE_B = "mesajları gönderdiğinde kendini daha da *çaresiz hissedebilirsin."
END_A = "Cümleni değiştir,"
END_B = "sürecin değişsin."

# ---------------------------------------------------------------- zaman çizelgesi (müzikle aynı)
HOOK2_T = 2.5
PAIR_T = [6.25, 13.75, 21.25, 28.75]
CLOSE_T = 36.25
END_T = 43.75
NEG_D = 2.5   # ❌ süresi
PAIR_D = 7.5


# ---------------------------------------------------------------- yardımcılar
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, d):
    return clamp((t - t0) / d)


def ease_out_expo(p):
    return 1 if p >= 1 else 1 - 2 ** (-10 * p)


def ease_out_back(p, s=1.7):
    p -= 1
    return 1 + p * p * ((s + 1) * p + s)


def ease_in_out(p):
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


def ease_in(p):
    return p ** 3


@lru_cache(maxsize=None)
def font(size, path):
    return ImageFont.truetype(path, size)


@lru_cache(maxsize=None)
def word_img(word, size, color, path):
    f = font(size, path)
    x0, y0, x1, y1 = f.getbbox(word)
    asc, desc = f.getmetrics()
    img = Image.new("RGBA", (x1 + 6, asc + desc + 6), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((3, 3), word, font=f, fill=color + (255,))
    return img


@lru_cache(maxsize=None)
def layout(text, size, maxw, path):
    """Kelimeleri satırlara böler. '*' ile başlayan kelimeler vurgulanır.
    Dönen: [(kelime, vurgu, x, satır)], satır sayısı, satır yüksekliği."""
    f = font(size, path)
    space = f.getlength(" ")
    words = [(w[1:], True) if w.startswith("*") else (w, False) for w in text.split()]
    lines, cur, curw = [], [], 0.0
    for w, hl in words:
        ww = f.getlength(w)
        if cur and curw + space + ww > maxw:
            lines.append((cur, curw))
            cur, curw = [], 0.0
        curw = curw + (space if cur else 0) + ww
        cur.append((w, hl, ww))
    if cur:
        lines.append((cur, curw))
    out = []
    for li, (ws, lw) in enumerate(lines):
        x = -lw / 2
        for w, hl, ww in ws:
            out.append((w, hl, x, li))
            x += ww + space
    asc, desc = f.getmetrics()
    return tuple(out), len(lines), int((asc + desc) * 1.12)


def draw_words(layer, text, size, cx, cy, color, hl_color, path, t, t0, step=0.07, maxw=880, alpha=1.0,
               visible_all=False):
    """Kelime kelime (yukarı kayarak) açılan, ortalanmış paragraf."""
    items, nlines, lh = layout(text, size, maxw, path)
    top = cy - nlines * lh / 2
    for i, (w, hl, x, li) in enumerate(items):
        p = 1.0 if visible_all else prog(t, t0 + i * step, 0.35)
        if p <= 0:
            continue
        img = word_img(w, size, hl_color if hl else color, path)
        a = clamp(p * 2) * alpha
        dy = (1 - ease_out_expo(p)) * 26
        if a < 0.99:
            img = img.copy()
            img.putalpha(img.getchannel("A").point(lambda v: int(v * a)))
        layer.alpha_composite(img, (int(cx + x - 3), int(top + li * lh + dy)))
    return items, nlines, lh, top


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
    if ex > sx and ey > sy:
        layer.alpha_composite(img.crop((sx, sy, ex, ey)), (x + sx, y + sy))


# ---------------------------------------------------------------- arka planlar
def gradient(c1, c2):
    y = np.linspace(0, 1, H)[:, None, None]
    g = np.array(c1)[None, None] * (1 - y) + np.array(c2)[None, None] * y
    return Image.fromarray(np.broadcast_to(g, (H, W, 3)).astype(np.uint8)).convert("RGBA")


BG_DARK = gradient(DARK_TOP, DARK_BOT)
BG_WARM = gradient(WARM_TOP, WARM_BOT)


def mode_at(t):
    """'dark' / 'warm' zemin ve son geçişin zamanı."""
    events = [(0.0, "dark")]
    for s in PAIR_T:
        events += [(s, "dark"), (s + NEG_D, "warm")]
    events += [(CLOSE_T, "dark"), (END_T + 0.35, "warm")]
    prev, cur = "dark", events[0]
    for e in events:
        if t >= e[0]:
            prev, cur = cur[1], e
    return prev, cur[1], cur[0]


def background(t, cx=W / 2, cy=900):
    prev, cur, t0 = mode_at(t)
    new = BG_WARM if cur == "warm" else BG_DARK
    old = BG_WARM if prev == "warm" else BG_DARK
    p = prog(t, t0, 0.55)
    if p >= 1 or prev == cur:
        bg = new.copy()
    else:
        r = ease_in_out(p) * 2100
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
        bg = Image.composite(new, old, mask)
    return bg, cur


# yumuşak yüzen ışık lekeleri
def make_orbs(color, n, seed):
    rng = np.random.default_rng(seed)
    img = Image.new("RGBA", (W + 300, H + 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y, r = rng.uniform(0, W + 300), rng.uniform(0, H + 300), rng.uniform(60, 180)
        d.ellipse((x - r, y - r, x + r, y + r), fill=color + (int(rng.uniform(18, 40)),))
    return img.filter(ImageFilter.GaussianBlur(30))


ORBS_DARK = make_orbs((90, 100, 140), 14, 1)
ORBS_WARM = make_orbs((255, 255, 255), 16, 2)


def orbs(bg, t, mode):
    src = ORBS_WARM if mode == "warm" else ORBS_DARK
    ox = int(150 + 120 * math.sin(t * 0.21))
    oy = int(150 + 140 * math.cos(t * 0.17))
    bg.alpha_composite(src.crop((ox, oy, ox + W, oy + H)))


# ---------------------------------------------------------------- bileşenler
def icon_badge(kind, r):
    img = Image.new("RGBA", (2 * r + 4, 2 * r + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = r + 2
    d.ellipse((2, 2, 2 * r + 2, 2 * r + 2), fill=(RED if kind == "x" else GREEN) + (255,))
    w = max(4, r // 4)
    if kind == "x":
        k = r * 0.42
        d.line((c - k, c - k, c + k, c + k), fill=WHITE, width=w)
        d.line((c - k, c + k, c + k, c - k), fill=WHITE, width=w)
    else:
        d.line([(c - r * 0.45, c + r * 0.02), (c - r * 0.12, c + r * 0.35), (c + r * 0.48, c - r * 0.32)],
               fill=WHITE, width=w, joint="curve")
    return img


BADGE_X = icon_badge("x", 34)
BADGE_OK = icon_badge("ok", 34)
BADGE_OK_BIG = icon_badge("ok", 70)
BADGE_X_SMALL = icon_badge("x", 26)
BADGE_OK_HUGE = icon_badge("ok", 112)


@lru_cache(maxsize=None)
def label_img(kind, text, dark_bg):
    b = BADGE_X if kind == "x" else BADGE_OK
    col = (220, 222, 230) if dark_bg else INK
    t = word_img(text, 44, col, FONT_BOLD)
    w = b.width + 24 + t.width + 60
    h = max(b.height, t.height) + 30
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2,
                        fill=(255, 255, 255, 22) if dark_bg else (255, 255, 255, 170))
    img.alpha_composite(b, (16, (h - b.height) // 2))
    img.alpha_composite(t, (16 + b.width + 22, (h - t.height) // 2 + 2))
    return img


def bubble_img(text, positive, t, t0, strike_p=0.0, size=64):
    """Konuşma balonu + metin (kelime kelime). Balon görseli döner."""
    path = FONT_BOLD
    items, nlines, lh = layout(text, size, 800, path)
    bw = 920
    bh = nlines * lh + 120
    tail = 46
    img = Image.new("RGBA", (bw + 30, bh + tail + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fill = (255, 255, 255, 255) if positive else NEG_BUBBLE + (255,)
    if positive:  # yumuşak gölge
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((18, 26, bw + 12, bh + 20), radius=56, fill=(170, 90, 50, 70))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d.rounded_rectangle((0, 0, bw, bh), radius=56, fill=fill)
    d.polygon([(110, bh - 2), (180, bh - 2), (95, bh + tail)], fill=fill)
    color = INK if positive else NEG_TEXT
    hl = GREEN if positive else NEG_TEXT
    step = 0.085 if positive else 0.045
    _, _, _, top = draw_words(img, text, size, bw / 2, bh / 2 + 4, color, hl, path, t, t0, step=step, maxw=800)
    # kırmızı üstü çizme (satır satır)
    if strike_p > 0:
        for li in range(nlines):
            xs = [x for w, _, x, l in items if l == li]
            ws = [font(size, path).getlength(w) for w, _, x, l in items if l == li]
            x0 = bw / 2 + min(xs) - 10
            x1 = bw / 2 + max(x + ww for x, ww in zip(xs, ws)) + 10
            p = clamp(strike_p * nlines - li)
            if p > 0:
                y = top + li * lh + lh * 0.52
                d.line((x0, y, x0 + (x1 - x0) * ease_out_expo(p), y - 4), fill=RED, width=10)
    return img


# parıltı parçacıkları
SPARK_RNG = np.random.default_rng(8)
SPARKS = [(SPARK_RNG.uniform(0, 2 * math.pi), SPARK_RNG.uniform(260, 620), SPARK_RNG.uniform(10, 24),
           SPARK_RNG.uniform(0, 0.25)) for _ in range(22)]


def draw_sparks(d, t, t0, cx, cy, color):
    for a, dist, sz, delay in SPARKS:
        p = prog(t, t0 + delay, 1.1)
        if p <= 0 or p >= 1:
            continue
        r = 140 + dist * ease_out_expo(p)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a) * 1.25
        s = sz * (1 - p)
        al = int(255 * (1 - p))
        d.polygon([(x, y - s * 2), (x + s * 0.5, y - s * 0.5), (x + s * 2, y), (x + s * 0.5, y + s * 0.5),
                   (x, y + s * 2), (x - s * 0.5, y + s * 0.5), (x - s * 2, y), (x - s * 0.5, y - s * 0.5)],
                  fill=color + (al,))


# ---------------------------------------------------------------- sahneler
def scene_hook1(t, fg):
    out = prog(t, 2.2, 0.3)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    items, nl, lh, top = draw_words(layer, HOOK1, 100, W / 2, 900, WHITE, PEACH, FONT_BLACK, t, 0.1,
                                    step=0.12, maxw=900)
    # yanıp sönen imleç
    if int(t * 3) % 2 == 0:
        d = ImageDraw.Draw(layer)
        d.rounded_rectangle((W / 2 - 4, top + nl * lh + 30, W / 2 + 4, top + nl * lh + 100), radius=4,
                            fill=PEACH)
    put(fg, layer, W / 2, H / 2 - 40 * ease_in(out), alpha=1 - out)


def draw_thought(d, cx, cy, s, color):
    k = s / 100
    for dx, dy, r in ((-70, 10, 55), (0, -25, 70), (75, 5, 55), (20, 40, 50), (-40, 40, 45)):
        d.ellipse((cx + dx * k - r * k, cy + dy * k - r * k, cx + dx * k + r * k, cy + dy * k + r * k), fill=color)
    for dx, dy, r in ((-95, 95, 18), (-125, 135, 11)):
        d.ellipse((cx + dx * k - r * k, cy + dy * k - r * k, cx + dx * k + r * k, cy + dy * k + r * k), fill=color)


def scene_hook2(t, fg):
    u = t - HOOK2_T
    out = prog(u, 3.45, 0.3)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    s = 120 * max(0.0, ease_out_back(prog(u, 0.0, 0.5)))
    if s > 1:
        bob = 8 * math.sin(u * 3)
        draw_thought(d, W / 2, 560 + bob, s, (255, 255, 255, 40))
        for i in range(3):  # düşünen noktalar
            a = 0.35 + 0.65 * (math.sin(u * 6 - i * 0.8) * 0.5 + 0.5)
            d.ellipse((W / 2 - 70 + i * 60 - 14, 545 + bob - 14, W / 2 - 70 + i * 60 + 14, 545 + bob + 14),
                      fill=(255, 255, 255, int(220 * a)))
    draw_words(layer, HOOK2, 84, W / 2, 1030, WHITE, PEACH, FONT_BLACK, u, 0.2, step=0.1, maxw=900)
    put(fg, layer, W / 2, H / 2 - 40 * ease_in(out), alpha=1 - out)


def scene_pair(k, t, fg):
    s = PAIR_T[k]
    u = t - s
    neg, pos = PAIRS[k]
    d = ImageDraw.Draw(fg)
    # üst sayaç
    for i in range(4):
        x = W / 2 + (i - 1.5) * 56
        on = i <= k
        dark = u < NEG_D
        c = (255, 255, 255, 200 if on else 60) if dark else INK + (200 if on else 50,)
        d.rounded_rectangle((x - 20, 236, x + 20, 246), radius=5, fill=c)
    cy = 900
    if u < NEG_D:
        put(fg, label_img("x", "KENDİNE SÖYLEDİĞİN", True), W / 2, 380,
            scale=max(0.01, ease_out_back(prog(u, 0.1, 0.4))))
        img = bubble_img(neg, False, u, 0.25, strike_p=prog(u, 1.5, 0.45))
        pin = ease_out_back(prog(u, 0.05, 0.4))
        cr = ease_in(prog(u, 2.05, 0.42))
        jitter = 3 * math.sin(u * 40) if u < 1.5 else 0
        put(fg, img, W / 2 + jitter, cy + 500 * cr, scale=max(0.01, pin * (1 - 0.7 * cr)),
            rot=-22 * cr, alpha=1 - cr)
    else:
        v = u - NEG_D
        out = prog(v, 4.65, 0.35)
        put(fg, label_img("ok", "BUNUNLA DEĞİŞTİR", False), W / 2, 380,
            scale=max(0.01, ease_out_back(prog(v, 0.15, 0.4))), alpha=1 - out)
        draw_sparks(d, t, s + NEG_D + 0.1, W / 2, cy, (255, 255, 255))
        img = bubble_img(pos, True, v, 0.4)
        pin = ease_out_back(prog(v, 0.1, 0.5))
        put(fg, img, W / 2, cy - 60 * ease_in(out), scale=max(0.01, pin), alpha=1 - out)
        nwords = len(layout(pos, 64, 800, FONT_BOLD)[0])
        tb = 0.4 + nwords * 0.085 + 0.2
        bp = ease_out_back(prog(v, tb, 0.4), 2.2)
        _, nl, lh = layout(pos, 64, 800, FONT_BOLD)
        bh = nl * lh + 120
        put(fg, BADGE_OK_BIG, W / 2 + 430, cy - bh / 2 - 10, scale=max(0.01, bp), alpha=1 - out)


def scene_close(t, fg):
    u = t - CLOSE_T
    d = ImageDraw.Draw(fg)
    draw_words(fg, CLOSE_A, 82, W / 2, 420, WHITE, WHITE, FONT_BLACK, u, 0.1, step=0.12)
    positions = [(W / 2 - 120, 700, -4), (W / 2 + 90, 860, 3), (W / 2 - 60, 1020, -2)]
    for i, (word, (x, y, rot)) in enumerate(zip(CLOSE_WORDS, positions)):
        t0 = 37.2 + i * 0.6 - CLOSE_T
        p = prog(u, t0, 0.35)
        if p <= 0:
            continue
        txt = word_img(word, 66, NEG_TEXT, FONT_BOLD)
        bw, bh = txt.width + 120, txt.height + 50
        b = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        bd = ImageDraw.Draw(b)
        bd.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=bh // 2, fill=NEG_BUBBLE + (255,))
        b.alpha_composite(BADGE_X_SMALL, (20, (bh - BADGE_X_SMALL.height) // 2))
        b.alpha_composite(txt, (80, 25))
        shake = 4 * math.sin(u * 37 + i * 2) * (1 + prog(u, 3.0, 4.0))
        put(fg, b, x + shake, y, scale=max(0.01, ease_out_back(p, 2.2)), rot=rot)
    draw_words(fg, CLOSE_B, 66, W / 2, 1300, WHITE, RED, FONT_BOLD, u, 39.2 - CLOSE_T, step=0.11)


def scene_end(t, fg):
    u = t - END_T
    d = ImageDraw.Draw(fg)
    # kapanıştaki 'olumsuz' balonların hızla çizilip kaybolması
    if u < 0.5:
        positions = [(W / 2 - 120, 700, -4), (W / 2 + 90, 860, 3), (W / 2 - 60, 1020, -2)]
        for i, (word, (x, y, rot)) in enumerate(zip(CLOSE_WORDS, positions)):
            txt = word_img(word, 66, NEG_TEXT, FONT_BOLD)
            bw, bh = txt.width + 120, txt.height + 50
            b = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
            bd = ImageDraw.Draw(b)
            bd.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=bh // 2, fill=NEG_BUBBLE + (255,))
            b.alpha_composite(txt, (80, 25))
            sp = ease_out_expo(prog(u, i * 0.06, 0.2))
            bd.line((60, bh / 2, 60 + (bw - 100) * sp, bh / 2 - 3), fill=RED, width=9)
            q = ease_in(prog(u, 0.25, 0.25))
            put(fg, b, x, y + 300 * q, rot=rot - 20 * q, scale=1 - 0.5 * q, alpha=1 - q)
        return
    v = u - 0.35
    draw_sparks(d, t, END_T + 0.45, W / 2, 1330, (255, 255, 255))
    draw_words(fg, END_A, 120, W / 2, 640, INK, INK, FONT_BLACK, v, 0.15, step=0.15)
    draw_words(fg, END_B, 120, W / 2, 990, GREEN, GREEN, FONT_BLACK, v, 0.5, step=0.15)
    bp = ease_out_back(prog(v, 0.9, 0.45), 2.2)
    pulse = 1 + 0.04 * math.sin(v * math.pi * 2 / 1.25)
    put(fg, BADGE_OK_HUGE, W / 2, 1330, scale=max(0.01, bp * pulse))


def render_frame(t):
    bg, mode = background(t)
    orbs(bg, t, mode)
    fg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t < HOOK2_T:
        scene_hook1(t, fg)
    elif t < PAIR_T[0]:
        scene_hook2(t, fg)
    elif t < CLOSE_T:
        k = max(i for i, s in enumerate(PAIR_T) if t >= s)
        scene_pair(k, t, fg)
    elif t < END_T:
        scene_close(t, fg)
    else:
        scene_end(t, fg)
    bg.alpha_composite(fg)
    # kapanışta ekranı daraltan vinyet
    arr = np.asarray(bg.convert("RGB")).astype(np.float32)
    v = 0.45 * prog(t, CLOSE_T + 2.5, 5.0) if CLOSE_T <= t < END_T else 0.0
    if v > 0:
        arr *= VIG ** (v * 3)
    # siyahtan açılış / kapanış
    fade = min(prog(t, 0, 0.4), 1 - prog(t, DUR - 0.8, 0.8))
    arr *= fade
    return np.clip(arr, 0, 255).astype(np.uint8)


def _vig():
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.7)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    return np.clip(1.1 - d * 0.6, 0.3, 1)[:, :, None].astype(np.float32)


VIG = _vig()


def main():
    music, out = sys.argv[1], sys.argv[2]
    if out.endswith(".png"):
        Image.fromarray(render_frame(float(sys.argv[3]))).save(out)
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
