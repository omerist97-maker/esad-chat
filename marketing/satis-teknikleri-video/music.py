"""30 sn, 120 BPM, E Dorian funky groove (slap bas, Rhodes, gitar 'chop') — numpy ile sentezlenir."""
import sys
import wave
import numpy as np

SR = 44100
DUR = 30.0
BEAT = 0.5
BAR = 2.0
S16 = BEAT / 4
N = int(SR * DUR)
rng = np.random.default_rng(31)
L = np.zeros(N)
R = np.zeros(N)
TIPS = [4.0, 8.0, 12.0, 16.0, 20.0]
OUTRO = 24.0


def tt(d):
    return np.arange(int(d * SR)) / SR


def note(n):
    return 440 * 2 ** ((n - 69) / 12)


def lowpass(x, w):
    return np.convolve(x, np.ones(w) / w, mode="same")


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(round(t0 * SR))
    if i >= N or i < 0:
        return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * (1 - max(pan, 0))
    R[i:i + len(sig)] += sig * gain * (1 + min(pan, 0))


def swing(s):  # 16'lıklarda hafif swing
    return s * S16 + (0.022 if s % 2 else 0.0)


# ---------- sesler ----------
def kick():
    t = tt(0.3)
    f = 50 + 110 * np.exp(-t * 35)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
    return np.tanh(s * 2.0)


def snare():
    t = tt(0.25)
    nz = rng.uniform(-1, 1, len(t))
    nz = nz - lowpass(nz, 4)
    body = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 30)
    return np.tanh((nz * np.exp(-t * 20) * 0.9 + body * 0.6) * 1.4)


def hat(open_=False):
    t = tt(0.18 if open_ else 0.04)
    nz = rng.uniform(-1, 1, len(t))
    nz = np.diff(np.diff(nz, prepend=0), prepend=0) * 0.5
    return nz * np.exp(-t * (18 if open_ else 95))


def slap(n, d=0.2):
    t = tt(d)
    f = note(n)
    s = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (6 + 9 * k)) / k ** 0.7 for k in range(1, 9))
    s[:120] += rng.uniform(-1, 1, 120) * np.linspace(0.4, 0, 120)
    return np.tanh(s * 1.8) * np.minimum(1, (d - t) / 0.01)


def rhodes(n, d=0.6):
    t = tt(d)
    f = note(n)
    s = np.sin(2 * np.pi * f * t + 0.8 * np.sin(2 * np.pi * f * t) * np.exp(-t * 6)) * np.exp(-t * 3)
    trem = 1 + 0.15 * np.sin(2 * np.pi * 5 * t)
    return s * trem * np.minimum(1, (d - t) / 0.04)


def chop(n, d=0.09):
    """Muted gitar vuruşu."""
    t = tt(d)
    f = note(n)
    s = sum(np.sign(np.sin(2 * np.pi * f * k * t)) / k for k in (1, 2, 3))
    s = s - lowpass(s, 10)
    return s * np.exp(-t * 45) * 0.5


def whoosh(d=0.45):
    t = tt(d)
    nz = rng.uniform(-1, 1, len(t))
    env = np.sin(np.pi * t / d) ** 2
    return lowpass(nz, 5) * env * 0.7


def ding(n=88):
    t = tt(0.8)
    f = note(n)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 3.01 * t)) * np.exp(-t * 5)


def buzz():
    t = tt(0.22)
    return np.sign(np.sin(2 * np.pi * 110 * t)) * np.exp(-t * 12) * 0.35


def riser(d):
    t = tt(d)
    nz = rng.uniform(-1, 1, len(t))
    f = 300 * (6 ** (t / d))
    return ((nz - lowpass(nz, 8)) * 0.5 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.2) * (t / d) ** 2.3


def impact():
    t = tt(2.0)
    boom = np.sin(2 * np.pi * np.cumsum(35 + 60 * np.exp(-t * 4)) / SR) * np.exp(-t * 2)
    nz = rng.uniform(-1, 1, len(t))
    return np.tanh((boom * 1.3 + (nz - lowpass(nz, 3)) * np.exp(-t * 3) * 0.3) * 1.2)


# Em7 - A7 (Dorian vamp), bas riff (16'lık adımlar)
CHORDS = [(40, [55, 59, 62, 66]), (45, [55, 57, 61, 64])]  # E, A kökleri; Rhodes voicing
BASS_RIFF = {0: 0, 3: 12, 4: 0, 6: 10, 7: 12, 10: 0, 11: 3, 12: 5, 14: 7}


def groove_bar(t0, bi, drums=True, keys=True, bass=True, gtr=True):
    root, voicing = CHORDS[bi % 2]
    if drums:
        for s in (0, 6, 8):
            add(kick(), t0 + swing(s), 0.85)
        for s in (4, 12):
            add(snare(), t0 + swing(s), 0.45)
        for s in range(16):
            add(hat(s == 14), t0 + swing(s), 0.16 if s % 2 == 0 else 0.09, pan=0.25)
    if bass:
        for s, iv in BASS_RIFF.items():
            add(slap(root + iv - 12), t0 + swing(s), 0.42)
    if keys:
        for s in (2, 7, 10):
            for j, n in enumerate(voicing):
                add(rhodes(n, 0.45), t0 + swing(s), 0.07, pan=(-0.4, 0.4)[j % 2])
    if gtr:
        for s in (4, 12, 13):
            add(chop(voicing[-1] + 12), t0 + swing(s), 0.25, pan=0.5)


# 0 - 4: kanca — 1. ölçü bas + hat, 2. ölçü buzzer + build
for s in range(16):
    add(hat(), swing(s), 0.1, pan=0.25)
for s, iv in BASS_RIFF.items():
    add(slap(40 + iv - 12), swing(s), 0.42)
add(buzz(), 1.0, 0.5)                # "ÇALIŞMA." vurgusu
groove_bar(2.0, 1, drums=True, gtr=False)
add(riser(1.5), 2.5, 0.3)

# 4 - 24: 5 teknik, her biri 2 ölçü
add(impact(), 4.0, 0.7)
for k, s in enumerate(TIPS):
    groove_bar(s, 0)
    groove_bar(s + 2.0, 1)
    add(whoosh(), s - 0.2, 0.35)
    add(buzz(), s + 1.2, 0.35)       # ❌ satırı
    add(ding(88), s + 1.9, 0.18)     # ✅ satırı
    add(ding(95), s + 1.95, 0.1)

# 24 - 30: kapanış
add(whoosh(), OUTRO - 0.2, 0.4)
add(impact(), OUTRO, 0.8)
groove_bar(24.0, 0)
groove_bar(26.0, 1)
groove_bar(28.0, 0, drums=False, gtr=False)
add(kick(), 28.0, 0.8)
for n in CHORDS[0][1]:
    add(rhodes(n, 2.0), 28.0, 0.1)


def reverb(x, seed):
    r = np.random.default_rng(seed)
    t = tt(1.0)
    ir = r.uniform(-1, 1, len(t)) * np.exp(-t / 0.25)
    ir[0] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    n = len(x) + len(ir)
    return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]


L = L + reverb(L, 1) * 0.12
R = R + reverb(R, 2) * 0.12
mix = np.tanh(np.stack([L, R], axis=1) * 1.15)
fade = np.ones(N)
fade[-int(1.2 * SR):] = np.linspace(1, 0, int(1.2 * SR))
mix *= fade[:, None]
mix /= np.max(np.abs(mix)) / 0.8

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("ok", out)
