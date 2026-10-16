"""20 sn, 120 BPM, G majör motivasyonel piano-house müziği — numpy ile sentezlenir."""
import sys
import wave
import numpy as np

SR = 44100
DUR = 20.0
BEAT = 0.5
BAR = 2.0
S16 = BEAT / 4
N = int(SR * DUR)
rng = np.random.default_rng(21)
L = np.zeros(N)
R = np.zeros(N)
SL = np.zeros(N)   # sidechain uygulanacak synth kanalı
SR_ = np.zeros(N)


def tt(d):
    return np.arange(int(d * SR)) / SR


def note(n):
    return 440 * 2 ** ((n - 69) / 12)


def lowpass(x, w):
    return np.convolve(x, np.ones(w) / w, mode="same")


def _add(bl, br, sig, t0, gain, pan):
    i = int(round(t0 * SR))
    if i >= N:
        return
    sig = sig[: N - i]
    bl[i:i + len(sig)] += sig * gain * (1 - max(pan, 0))
    br[i:i + len(sig)] += sig * gain * (1 + min(pan, 0))


def add(sig, t0, gain=1.0, pan=0.0):
    _add(L, R, sig, t0, gain, pan)


def adds(sig, t0, gain=1.0, pan=0.0):
    _add(SL, SR_, sig, t0, gain, pan)


def kick():
    t = tt(0.4)
    f = 48 + 120 * np.exp(-t * 32)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)
    s[:180] += rng.uniform(-1, 1, 180) * np.linspace(0.5, 0, 180)
    return np.tanh(s * 2.2)


def clap():
    t = tt(0.3)
    nz = rng.uniform(-1, 1, len(t))
    nz = nz - lowpass(nz, 5)
    env = np.exp(-t * 16)
    for off in (0.0, 0.01, 0.02):
        env += 0.7 * np.exp(-np.maximum(t - off, 0) * 110) * (t >= off)
    return nz * env * 0.8


def hat(open_=False):
    t = tt(0.22 if open_ else 0.05)
    nz = rng.uniform(-1, 1, len(t))
    nz = np.diff(np.diff(nz, prepend=0), prepend=0) * 0.5
    return nz * np.exp(-t * (16 if open_ else 80))


def piano(n, d=0.45):
    """Parlak 'house piano' tonu: hızlı sönen üst harmonikler."""
    t = tt(d)
    f = note(n)
    s = np.zeros_like(t)
    for k, a in ((1, 1.0), (2, 0.6), (3, 0.35), (4, 0.25), (5, 0.12), (6, 0.08)):
        s += a * np.sin(2 * np.pi * f * k * t * (1 + 0.0007 * k)) * np.exp(-t * (3 + 3.5 * k))
    return s * np.minimum(1, t / 0.003)


def pluck(n, d=0.2):
    t = tt(d)
    f = note(n)
    s = sum(np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (10 + 6 * k)) for k in range(1, 8))
    return s


def bass(n, d):
    t = tt(d)
    f = note(n)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.15 * np.sin(2 * np.pi * 3 * f * t)
    return np.tanh(s * 1.6) * np.exp(-t * 4) * np.minimum(1, (d - t) / 0.01)


def riser(d):
    t = tt(d)
    ramp = (t / d) ** 2.3
    nz = rng.uniform(-1, 1, len(t))
    f = 220 * (8 ** (t / d))
    sw = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    return ((nz - lowpass(nz, 10)) * 0.5 + sw * 0.2) * ramp


def impact():
    t = tt(2.5)
    boom = np.sin(2 * np.pi * np.cumsum(32 + 55 * np.exp(-t * 3.5)) / SR) * np.exp(-t * 1.6)
    nz = rng.uniform(-1, 1, len(t))
    return np.tanh((boom * 1.4 + (nz - lowpass(nz, 3)) * np.exp(-t * 2.4) * 0.3) * 1.2)


def chime(t0):
    """Başlık geçişlerinde kısa parıltı sesi."""
    for i, n in enumerate((86, 91, 95)):
        adds(pluck(n, 0.4) * 0.6, t0 + i * 0.04, 0.12, pan=(-0.5, 0, 0.5)[i])


# G - D - Em - C   (I - V - vi - IV)
PROG = [(43, [67, 71, 74, 79]), (38, [66, 69, 74, 78]), (40, [67, 71, 76, 79]), (36, [64, 67, 72, 76])]
PIANO_POS = [0, 3, 6, 8, 10, 13]          # 16'lık senkoplu akor ritmi
ARP = [0, 1, 2, 3, 2, 1, 2, 3]


def groove_bar(t0, bi, full=True, lead=False):
    root, ch = PROG[bi % 4]
    for q in range(4):
        tb = t0 + q * BEAT
        add(kick(), tb, 0.9)
        if q in (1, 3):
            add(clap(), tb, 0.42)
        add(hat(True), tb + BEAT / 2, 0.16, pan=0.2)
        add(hat(), tb + BEAT / 4, 0.1, pan=-0.3)
        add(hat(), tb + 3 * BEAT / 4, 0.1, pan=-0.3)
        # offbeat bas
        add(bass(root, BEAT / 2 * 0.9), tb + BEAT / 2, 0.5)
        if full:
            add(bass(root + 12, BEAT / 4 * 0.9), tb + 3 * BEAT / 4, 0.25)
    for p in PIANO_POS:
        for j, n in enumerate(ch):
            adds(piano(n, 0.4), t0 + p * S16, 0.13, pan=(-0.35, 0.35)[j % 2])
    if lead:
        for i in range(16):
            n = ch[ARP[i % 8]] + 12
            adds(pluck(n), t0 + i * S16, 0.1, pan=0.4 if i % 2 else -0.4)


# 0-2: intro — piyano akorları + riser
for p in (0, 3, 6, 10, 13):
    for n in PROG[0][1]:
        adds(piano(n, 0.5), p * S16, 0.11)
add(riser(2.0), 0, 0.35)
for i in range(8):
    add(clap(), 1.0 + i * S16, 0.06 + 0.04 * i)

# 2-14: ana bölüm (6 ölçü) — her başlıkta chime
add(impact(), 2.0, 0.8)
for b in range(6):
    groove_bar(2.0 + b * BAR, b, lead=(b >= 2))
    chime(2.0 + b * BAR)

# 14-16: recap build — kick devam, snare rulosu, riser
for q in range(4):
    add(kick(), 14.0 + q * BEAT, 0.7)
for p in PIANO_POS:
    for n in PROG[3][1]:
        adds(piano(n, 0.4), 14.0 + p * S16, 0.1)
roll = [14.0 + i * BEAT / 2 for i in range(4)] + [15.0 + i * S16 for i in range(4)] + \
       [15.5 + i * S16 / 2 for i in range(8)]
for i, tr in enumerate(roll):
    add(clap(), tr, 0.1 + 0.3 * i / len(roll))
add(riser(2.0), 14.0, 0.45)
for i in range(6):  # her tik işaretinde ding
    adds(pluck(79 + [0, 2, 4, 5, 7, 9][i], 0.3), 14.0 + i * 0.25, 0.18)

# 16-19.5: final drop
add(impact(), 16.0, 1.0)
for b in range(2):
    groove_bar(16.0 + b * BAR, b, lead=True)
for n in PROG[0][1] + [55]:
    adds(piano(n, 1.0), 19.0, 0.16)

# sidechain + reverb
kicks = [2.0 + i * BEAT for i in range(24)] + [16.0 + i * BEAT for i in range(8)] + [14.0 + i * BEAT for i in range(4)]
sc = np.ones(N)
tn = np.arange(N) / SR
for kt in kicks:
    i = int(kt * SR)
    seg = tn[i:i + int(0.3 * SR)] - kt
    sc[i:i + len(seg)] = np.minimum(sc[i:i + len(seg)], 1 - 0.6 * np.exp(-seg / 0.08))


def reverb(x, seed):
    r = np.random.default_rng(seed)
    t = tt(1.6)
    ir = r.uniform(-1, 1, len(t)) * np.exp(-t / 0.45)
    ir[0] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    n = len(x) + len(ir)
    return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]


sl, sr2 = SL * sc, SR_ * sc
L += sl + reverb(sl, 1) * 0.3
R += sr2 + reverb(sr2, 2) * 0.3
mix = np.tanh(np.stack([L, R], axis=1) * 1.1)
fade = np.ones(N)
fade[-int(0.8 * SR):] = np.linspace(1, 0, int(0.8 * SR))
mix *= fade[:, None]
mix /= np.max(np.abs(mix)) / 0.78

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("ok", out)
