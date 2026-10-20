"""Network marketingde 5 satış tekniği — Instagram Reels (1080x1920, 30 sn).

Açık zemin, lacivert tipografi, fosforlu yeşil 'vurgu kalemi'; her teknik ❌ Yapma / ✅ Yap karşılaştırmasıyla.
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
DUR = 30.0

FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"

BG = (243, 244, 248)
INK = (18, 22, 48)
BLUE = (45, 91, 255)
LIME = (198, 255, 61)
GRAY = (150, 154, 168)
LIGHT = (225, 227, 235)
RED = (240, 72, 72)
WHITE = (255, 255, 255)
LX = 80

TIPS_T = [4.0, 8.0, 12.0, 16.0, 20.0]
OUTRO_T = 24.0
TIP_D = 4.0

TIPS = [
    {"title": ["ÖNCE", "DİNLE"], "icon": "listen",
     "no": "Hemen ürünü anlatmak", "yes": "Soru sorup ihtiyacı keşfetmek"},
    {"title": ["ÜRÜNÜ DEĞİL,", "ÇÖZÜMÜ ANLAT"], "icon": "bulb",
     "no": "Özellikleri tek tek saymak", "yes": "Hayatına ne katacağını göstermek"},
    {"title": ["HİKÂYENİ", "PAYLAŞ"], "icon": "book",
     "no": "Ezber sunum yapmak", "yes": "Kendi deneyimini samimice anlatmak"},
    {"title": ["İTİRAZI", "KUCAKLA"], "icon": "chat",
     "steps": ["Seni anlıyorum.", "Ben de öyle hissetmiştim.", "Sonra şunu fark ettim…"]},
    {"title": ["TAKİBİ", "BIRAKMA"], "icon": "calendar",
     "no": "Bir kez sorup vazgeçmek", "yes": "Nazik ve düzenli takip etmek"},
]


# ---------------------------------------------------------------- yardımcılar
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, t0, d):
    return clamp((t - t0) / d)


def ease_out_expo(p):
    return 1 if p >= 1 else 1 - 2 ** (-10 * p)


def ease_out_back(p, s=1.8):
    p -= 1
    return 1 + p * p * ((s + 1) * p + s)


def ease_in_out(p):
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


@lru_cache(maxsize=None)
def font(size, path):
    return ImageFont.truetype(path, size)


@lru_cache(maxsize=None)
def text_img(text, size, color, path=FONT_BLACK, maxw=920):
    while True:
        f = font(size, path)
        x0, y0, x1, y1 = f.getbbox(text)
        if x1 - x0 <= maxw or size < 20:
            break
        size = int(size * 0.95)
    pad = 8
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
        img = img.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    x, y = int(cx - img.width / 2), int(cy - img.height / 2)
    sx, sy = max(0, -x), max(0, -y)
    ex, ey = min(img.width, layer.width - x), min(img.height, layer.height - y)
    if ex > sx and ey > sy:
        layer.alpha_composite(img.crop((sx, sy, ex, ey)), (x + sx, y + sy))


def put_left(layer, img, x, cy, **kw):
    put(layer, img, x + img.width / 2, cy, **kw)


def reveal_left(layer, img, x, cy, p):
    if p <= 0:
        return
    off = int((1 - ease_out_expo(p)) * img.height)
    tmp = Image.new("RGBA", img.size, (0, 0, 0, 0))
    tmp.paste(img, (0, off))
    put_left(layer, tmp, x, cy)


def marker(d, x, cy, w, h, p, color=LIME, skew=10):
    """Vurgu kalemi: soldan sağa çekilen, hafif eğik şerit."""
    if p <= 0:
        return
    e = ease_out_expo(p)
    x1 = x + w * e
    d.polygon([(x - 12, cy - h / 2 + 6), (x1 + 12, cy - h / 2), (x1 + 12 - skew, cy + h / 2),
               (x - 12 - skew, cy + h / 2 + 4)], fill=color)


def title_block(layer, d, lines, t, t0, y0=520, size=150, hl_line=-1):
    """Sola hizalı büyük başlık; son satırın arkasına vurgu kalemi."""
    hl_line = len(lines) - 1 if hl_line < 0 else hl_line
    for i, ln in enumerate(lines):
        img = text_img(ln, size, INK)
        y = y0 + i * (size + 10)
        if i == hl_line:
            marker(d, LX, y + 8, img.width - 10, size * 0.62, prog(t, t0 + 0.35 + 0.1 * i, 0.4))
        reveal_left(layer, img, LX, y, prog(t, t0 + 0.1 * i, 0.4))


# ---------------------------------------------------------------- ikonlar
def draw_icon(layer, d, kind, cx, cy, u):
    sp = max(0.0, ease_out_back(prog(u, 0.15, 0.45)))
    if sp < 0.02:
        return
    if kind == "listen":
        r = 110 * sp
        d.ellipse((cx - 120 - r, cy - r, cx - 120 + r, cy + r), fill=BLUE)
        put(layer, text_img("?", 160, WHITE), cx - 120, cy, scale=sp)
        for i in range(3):  # dinleme dalgaları
            p = (u * 1.4 + i / 3) % 1
            rr = 60 + p * 170
            a = int(255 * (1 - p))
            d.arc((cx + 40 - rr, cy - rr, cx + 40 + rr, cy + rr), -50, 50, fill=INK + (a,), width=12)
    elif kind == "bulb":
        r = 105 * sp
        glow = 0.5 + 0.5 * math.sin(u * 6)
        for i in range(9):
            a = -math.pi / 2 + (i - 4) * 0.36
            r1, r2 = 140 * sp, (175 + 20 * glow) * sp
            d.line((cx + r1 * math.cos(a), cy - 30 + r1 * math.sin(a), cx + r2 * math.cos(a),
                    cy - 30 + r2 * math.sin(a)), fill=BLUE, width=12)
        d.ellipse((cx - r, cy - 30 - r, cx + r, cy - 30 + r), fill=LIME, outline=INK, width=10)
        d.rounded_rectangle((cx - 50 * sp, cy + 70 * sp, cx + 50 * sp, cy + 130 * sp), radius=10, fill=INK)
        d.line((cx - 30 * sp, cy + 10, cx, cy + 50 * sp, cx + 30 * sp, cy + 10), fill=INK, width=8)
    elif kind == "book":
        w, h = 190 * sp, 230 * sp
        flip = (u * 1.2) % 1
        d.polygon([(cx, cy - h / 2 + 20), (cx - w, cy - h / 2), (cx - w, cy + h / 2), (cx, cy + h / 2 + 20)],
                  fill=WHITE, outline=INK)
        d.polygon([(cx, cy - h / 2 + 20), (cx + w, cy - h / 2), (cx + w, cy + h / 2), (cx, cy + h / 2 + 20)],
                  fill=WHITE, outline=INK)
        d.line((cx - w, cy - h / 2, cx, cy - h / 2 + 20, cx + w, cy - h / 2), fill=INK, width=10)
        d.line((cx - w, cy + h / 2, cx, cy + h / 2 + 20, cx + w, cy + h / 2), fill=INK, width=10)
        d.line((cx - w, cy - h / 2, cx - w, cy + h / 2), fill=INK, width=10)
        d.line((cx + w, cy - h / 2, cx + w, cy + h / 2), fill=INK, width=10)
        d.line((cx, cy - h / 2 + 20, cx, cy + h / 2 + 20), fill=INK, width=10)
        for i in range(4):
            y = cy - h / 2 + 60 + i * 40 * sp
            d.line((cx - w + 30, y, cx - 30, y + 6), fill=LIGHT if i else BLUE, width=10)
            d.line((cx + 30, y + 6, cx + w - 30, y), fill=LIGHT, width=10)
        # çevrilen sayfa
        fx = cx + w * math.cos(flip * math.pi)
        d.polygon([(cx, cy - h / 2 + 20), (fx, cy - h / 2 + 4), (fx, cy + h / 2 - 4), (cx, cy + h / 2 + 20)],
                  fill=LIME, outline=INK)
    elif kind == "chat":
        p1 = ease_out_back(prog(u, 0.15, 0.4))
        p2 = ease_out_back(prog(u, 0.55, 0.4))
        if p1 > 0.02:
            b = text_img("Ama…", 64, INK, FONT_BOLD)
            bw, bh = b.width + 70, b.height + 50
            img = Image.new("RGBA", (bw, bh + 30), (0, 0, 0, 0))
            id_ = ImageDraw.Draw(img)
            id_.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=40, fill=LIGHT)
            id_.polygon([(40, bh - 2), (90, bh - 2), (30, bh + 28)], fill=LIGHT)
            img.alpha_composite(b, (35, 25))
            put(layer, img, cx - 170, cy - 70, scale=p1)
        if p2 > 0.02:
            b = text_img("Anlıyorum.", 64, WHITE, FONT_BOLD)
            bw, bh = b.width + 70, b.height + 50
            img = Image.new("RGBA", (bw, bh + 30), (0, 0, 0, 0))
            id_ = ImageDraw.Draw(img)
            id_.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=40, fill=BLUE)
            id_.polygon([(bw - 40, bh - 2), (bw - 90, bh - 2), (bw - 30, bh + 28)], fill=BLUE)
            img.alpha_composite(b, (35, 25))
            put(layer, img, cx + 140, cy + 90, scale=p2)
    elif kind == "calendar":
        w, h = 400 * sp, 300 * sp
        x0, y0 = cx - w / 2, cy - h / 2
        d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=30, fill=WHITE, outline=INK, width=10)
        d.rounded_rectangle((x0, y0, x0 + w, y0 + 70 * sp), radius=30, fill=BLUE)
        d.rectangle((x0 + 5, y0 + 40 * sp, x0 + w - 5, y0 + 70 * sp), fill=BLUE)
        for i in (0.28, 0.72):
            d.line((x0 + w * i, y0 - 25 * sp, x0 + w * i, y0 + 25 * sp), fill=INK, width=14)
        cw, ch = w / 4, (h - 70 * sp) / 2
        for k in range(8):
            c, r = k % 4, k // 4
            x = x0 + cw * (c + 0.5)
            y = y0 + 70 * sp + ch * (r + 0.5)
            if k in (0, 2, 5, 7):  # düzenli takip günleri
                p = ease_out_back(prog(u, 0.6 + k * 0.08, 0.3), 2.5)
                if p > 0.02:
                    rr = 30 * p
                    d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=LIME, outline=INK, width=5)
                    d.line([(x - 13 * p, y), (x - 3 * p, y + 11 * p), (x + 15 * p, y - 11 * p)], fill=INK,
                           width=6)
            else:
                d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=LIGHT)


# ---------------------------------------------------------------- satırlar
@lru_cache(maxsize=None)
def row_img(kind, text):
    """❌ / ✅ satırı (kart)."""
    yes = kind == "yes"
    label = text_img("YAP" if yes else "YAPMA", 34, WHITE if yes else GRAY)
    body = text_img(text, 54, WHITE if yes else GRAY, FONT_BOLD, maxw=700)
    w, h = 920, max(150, body.height + 90)
    img = Image.new("RGBA", (w + 14, h + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if yes:
        d.rounded_rectangle((14, 14, w + 13, h + 13), radius=34, fill=INK)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=34, fill=BLUE if yes else WHITE,
                        outline=None if yes else LIGHT, width=4)
    # rozet
    r = 38
    cx, cy = 70, h / 2
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=LIME if yes else (RED + (230,)))
    if yes:
        d.line([(cx - 17, cy + 1), (cx - 4, cy + 15), (cx + 19, cy - 13)], fill=INK, width=9, joint="curve")
    else:
        d.line((cx - 13, cy - 13, cx + 13, cy + 13), fill=WHITE, width=8)
        d.line((cx - 13, cy + 13, cx + 13, cy - 13), fill=WHITE, width=8)
    img.alpha_composite(label, (140, int(h / 2 - body.height / 2 - label.height + 2)))
    img.alpha_composite(body, (140, int(h / 2 - body.height / 2 + 14)))
    if not yes:  # üstü çizili
        y = h / 2 + 22
        d.line((150, y, 140 + body.width - 10, y - 4), fill=GRAY, width=5)
    return img


@lru_cache(maxsize=None)
def step_img(i, text):
    num = text_img(str(i + 1), 52, INK)
    body = text_img(text, 54, INK, FONT_BOLD, maxw=720)
    w, h = 920, 130
    img = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((12, 12, w + 11, h + 11), radius=30, fill=INK)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=30, fill=WHITE, outline=INK, width=5)
    d.ellipse((30, h / 2 - 40, 110, h / 2 + 40), fill=LIME, outline=INK, width=4)
    img.alpha_composite(num, (int(70 - num.width / 2), int(h / 2 - num.height / 2)))
    img.alpha_composite(body, (140, int(h / 2 - body.height / 2)))
    return img


# ---------------------------------------------------------------- sahneler
def scene_hook(t, layer):
    d = ImageDraw.Draw(layer)
    if t < 2.0:
        reveal_left(layer, text_img("Network marketingde", 76, GRAY, FONT_BOLD), LX, 620, prog(t, 0.05, 0.35))
        reveal_left(layer, text_img("SATIŞ", 230, INK), LX, 820, prog(t, 0.2, 0.35))
        reveal_left(layer, text_img("YAPMAYA", 190, INK), LX, 1030, prog(t, 0.4, 0.35))
        p = prog(t, 1.0, 0.2)
        if p > 0:
            img = text_img("ÇALIŞMA.", 190, RED)
            put(layer, img, LX + img.width / 2, 1230, scale=1 + 1.2 * (1 - ease_out_expo(p)), rot=-3,
                alpha=clamp(p * 3))
    else:
        u = t - 2.0
        reveal_left(layer, text_img("Bunun yerine", 76, GRAY, FONT_BOLD), LX, 650, prog(u, 0.0, 0.3))
        img = text_img("BU 5 TEKNİĞİ", 140, INK)
        marker(d, LX, 830 + 8, img.width - 10, 90, prog(u, 0.35, 0.4))
        reveal_left(layer, img, LX, 830, prog(u, 0.1, 0.35))
        reveal_left(layer, text_img("UYGULA.", 140, INK), LX, 980, prog(u, 0.25, 0.35))
        for i in range(5):
            p = ease_out_back(prog(u, 0.8 + i * 0.12, 0.3), 2.5)
            if p > 0.02:
                x, y, r = LX + 45 + i * 120, 1200, 42 * p
                d.ellipse((x - r, y - r, x + r, y + r), fill=BLUE)
                put(layer, text_img(str(i + 1), 48, WHITE), x, y, scale=p)
        # aşağı ok
        a = clamp(prog(u, 1.4, 0.3))
        yy = 1340 + 14 * math.sin(u * 8)
        d.line([(W / 2 - 40, yy), (W / 2, yy + 36), (W / 2 + 40, yy)], fill=INK + (int(255 * a),), width=12)


def scene_tip(k, u, layer):
    tip = TIPS[k]
    d = ImageDraw.Draw(layer)
    # üst: TEKNİK k/5 + ilerleme
    put_left(layer, text_img(f"TEKNİK {k + 1}/5", 44, BLUE), LX, 250, alpha=prog(u, 0.0, 0.3))
    for i in range(5):
        x = LX + 360 + i * 110
        c = BLUE if i <= k else LIGHT
        d.rounded_rectangle((x, 244, x + 90, 256), radius=6, fill=c)
    title_block(layer, d, tip["title"], u, 0.05, y0=430, size=130)
    draw_icon(layer, d, tip["icon"], W / 2, 870, u)
    if "steps" in tip:
        for i, st in enumerate(tip["steps"]):
            p = prog(u, 1.2 + i * 0.55, 0.4)
            if p > 0:
                put(layer, step_img(i, st), W / 2 + (1 - ease_out_expo(p)) * 600, 1180 + i * 160,
                    alpha=clamp(p * 2))
    else:
        p1 = prog(u, 1.2, 0.4)
        if p1 > 0:
            put(layer, row_img("no", tip["no"]), W / 2 + (1 - ease_out_expo(p1)) * -700, 1200,
                alpha=clamp(p1 * 2))
        p2 = prog(u, 1.9, 0.4)
        if p2 > 0:
            put(layer, row_img("yes", tip["yes"]), W / 2, 1400, scale=max(0.01, ease_out_back(p2, 1.5)))


def scene_outro(t, layer):
    u = t - OUTRO_T
    d = ImageDraw.Draw(layer)
    reveal_left(layer, text_img("SATIŞ YAPMA,", 140, GRAY), LX, 500, prog(u, 0.0, 0.35))
    img = text_img("GÜVEN", 230, INK)
    marker(d, LX, 720 + 10, img.width - 10, 150, prog(u, 0.75, 0.45))
    reveal_left(layer, img, LX, 720, prog(u, 0.45, 0.35))
    reveal_left(layer, text_img("İNŞA ET.", 230, INK), LX, 940, prog(u, 0.7, 0.35))
    # kaydet kartı
    p = ease_out_back(prog(u, 2.0, 0.45), 1.5)
    if p > 0.02:
        w, h = 920, 300
        card = Image.new("RGBA", (w + 14, h + 14), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle((14, 14, w + 13, h + 13), radius=40, fill=INK)
        cd.rounded_rectangle((0, 0, w - 1, h - 1), radius=40, fill=BLUE)
        # yer imi ikonu
        bx, by = 120, h / 2
        cd.polygon([(bx - 45, by - 70), (bx + 45, by - 70), (bx + 45, by + 70), (bx, by + 35), (bx - 45, by + 70)],
                   fill=LIME)
        card.alpha_composite(text_img("KAYDET", 92, WHITE), (220, 70))
        card.alpha_composite(text_img("Bir sonraki görüşmende uygula.", 46, WHITE, FONT_BOLD, maxw=660),
                             (222, 180))
        pulse = 1 + 0.025 * math.sin(u * math.pi * 2)
        put(layer, card, W / 2, 1330, scale=max(0.01, p) * pulse)


def content(t):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t < TIPS_T[0]:
        scene_hook(t, layer)
    elif t < OUTRO_T:
        k = int((t - TIPS_T[0]) // TIP_D)
        scene_tip(k, t - TIPS_T[k], layer)
    else:
        scene_outro(t, layer)
    return layer


BOUNDS = TIPS_T + [OUTRO_T]
PUSH = 0.35


@lru_cache(maxsize=None)
def background():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)
    for y in range(0, H, 54):  # defter çizgileri
        d.line((0, y, W, y), fill=(232, 234, 241), width=2)
    return img


def render_frame(t):
    frame = background().copy()
    # dikey itme geçişi: önceki sahne yukarı kayar, yenisi alttan gelir
    b = next((b for b in BOUNDS if b <= t < b + PUSH), None)
    cur = content(t)
    if b is not None:
        e = ease_in_out((t - b) / PUSH)
        prev = content(b - 1 / FPS)
        tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        oy = int(e * H)
        tmp.alpha_composite(prev.crop((0, oy, W, H)), (0, 0))
        off = int((1 - e) * H)
        if off < H:
            tmp.alpha_composite(cur.crop((0, 0, W, H - off)), (0, off))
        cur = tmp
    frame.alpha_composite(cur)
    arr = np.asarray(frame.convert("RGB")).astype(np.float32)
    fade = min(prog(t, 0, 0.25), 1 - prog(t, DUR - 0.6, 0.6))
    arr = arr * fade  # siyahtan açılış / siyaha kapanış
    return np.clip(arr, 0, 255).astype(np.uint8)


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
