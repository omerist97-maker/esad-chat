"""47,5 sn, 96 BPM duygusal piyano + lo-fi ritim.

❌ bölümlerinde karanlık/boğuk (minör, sadece kalp atışı), ✅ bölümlerinde aydınlık (majör, tam ritim).
Zaman çizelgesi render.py ile aynıdır.
"""
import sys
import wave
import numpy as np

SR = 44100
BEAT = 0.625
DUR = 47.5
N = int(SR * DUR)
rng = np.random.default_rng(4)
L = np.zeros(N)
R = np.zeros(N)

HOOK2 = 2.5
PAIRS = [6.25, 13.75, 21.25, 28.75]
CLOSE = 36.25
END = 43.75


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


# ---------- sesler ----------
def piano(n, d=1.2, bright=1.0):
    t = tt(d)
    f = note(n)
    s = np.zeros_like(t)
    for k, a in ((1, 1.0), (2, 0.5 * bright), (3, 0.25 * bright), (4, 0.12 * bright), (5, 0.06 * bright)):
        s += a * np.sin(2 * np.pi * f * k * t * (1 + 0.0006 * k)) * np.exp(-t * (1.6 + 1.4 * k))
    return s * np.minimum(1, t / 0.004) * np.minimum(1, (d - t) / 0.05)


def pad(notes, d, gain, dark=False):
    t = tt(d)
    out = np.zeros_like(t)
    for n in notes:
        for det in (-0.07, 0.0, 0.07):
            f = note(n + det)
            out += np.sin(2 * np.pi * f * t) + (0 if dark else 0.3 * np.sin(2 * np.pi * 2 * f * t))
    env = np.minimum(1, t / 0.5) * np.minimum(1, (d - t) / 0.5)
    return out * env * gain / (len(notes) * 3)


def kick(soft=1.0):
    t = tt(0.35)
    f = 45 + 80 * np.exp(-t * 30)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    return np.tanh(s * 1.8) * soft


def snap():
    t = tt(0.15)
    nz = rng.uniform(-1, 1, len(t))
    nz = nz - lowpass(nz, 6)
    return nz * np.exp(-t * 40) * 0.6


def shaker():
    t = tt(0.06)
    nz = rng.uniform(-1, 1, len(t))
    nz = np.diff(nz, prepend=0)
    return nz * np.exp(-t * 60) * 0.3


def chime(n):
    t = tt(1.5)
    f = note(n)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t * 3)


def whoosh(d=0.6):
    t = tt(d)
    nz = rng.uniform(-1, 1, len(t))
    env = (t / d) ** 2
    return lowpass(nz, 6) * env * 0.8


def scratch():
    """Üstü çizilirken kısa 'kalem' sesi."""
    t = tt(0.4)
    nz = rng.uniform(-1, 1, len(t))
    nz = nz - lowpass(nz, 4)
    return nz * np.exp(-((t - 0.15) / 0.12) ** 2) * 0.5


def crumple():
    """Kâğıt buruşturma: rastgele kısa çıtırtılar."""
    out = np.zeros(int(0.45 * SR))
    for _ in range(40):
        i = rng.integers(0, len(out) - 400)
        g = rng.uniform(0.2, 1.0)
        burst = rng.uniform(-1, 1, 300) * np.exp(-np.arange(300) / 60)
        out[i:i + 300] += burst * g
    return (out - lowpass(out, 5)) * 0.5


def thud():
    t = tt(0.6)
    return np.tanh(np.sin(2 * np.pi * (40 + 60 * np.exp(-t * 20)) * t) * np.exp(-t * 6) * 2.2)


CH = {  # akor notaları (piyano ortası) + bas
    "Am": ([57, 60, 64, 69], 45), "F": ([53, 57, 60, 65], 41), "C": ([55, 60, 64, 67], 48),
    "G": ([55, 59, 62, 67], 43), "Dm": ([53, 57, 62, 65], 38), "E": ([56, 59, 64, 68], 40),
}


def bright_bar(t0, d, chord, beat=True):
    notes, bass = CH[chord]
    add(pad(notes, d, 0.55), t0, 1.0)
    add(piano(bass - 12, d, 0.6), t0, 0.35)
    # piyano: akor + yukarı arpej
    for j, n in enumerate(notes):
        add(piano(n, 1.6), t0 + j * 0.02, 0.16, pan=(-0.3, 0.3)[j % 2])
    arp = notes + [notes[1] + 12, notes[2] + 12, notes[3] + 12, notes[2] + 12]
    steps = int(d / (BEAT / 2))
    for i in range(1, steps):
        add(piano(arp[i % len(arp)] + 12, 0.9, 0.7), t0 + i * BEAT / 2, 0.07, pan=0.4 if i % 2 else -0.4)
    if beat:
        nb = int(round(d / BEAT))
        for q in range(nb):
            tb = t0 + q * BEAT
            if q % 2 == 0:
                add(kick(), tb, 0.6)
            else:
                add(snap(), tb, 0.35)
            add(shaker(), tb + BEAT / 2, 0.5, pan=0.3)
            add(shaker(), tb, 0.25, pan=-0.3)


def dark_bar(t0, d, chord):
    notes, bass = CH[chord]
    p = pad([n - 12 for n in notes], d, 0.6, dark=True)
    add(lowpass(p, 30), t0, 1.0)
    add(pad([bass - 12], d, 0.5, dark=True), t0, 1.0)
    add(lowpass(piano(notes[0], d, 0.3), 25), t0, 0.18)
    # kalp atışı
    nb = int(round(d / (BEAT * 2)))
    for q in range(nb):
        add(kick(0.7), t0 + q * BEAT * 2, 0.55)
        add(kick(0.5), t0 + q * BEAT * 2 + 0.2, 0.4)


# 0 - 2.5: kanca 1 — yumuşak arpej
for i, n in enumerate([57, 60, 64, 69, 64, 60, 57, 64]):
    add(piano(n + 12, 1.2, 0.6), i * BEAT / 2, 0.12, pan=0.3 if i % 2 else -0.3)
add(pad(CH["Am"][0], 2.5, 0.35), 0.0)

# 2.5 - 6.25: kanca 2 — soru
bright_bar(2.5, 1.25, "Am")
bright_bar(3.75, 1.25, "F")
bright_bar(5.0, 1.25, "G", beat=True)
add(whoosh(0.8), 5.45, 0.3)

# çiftler
BRIGHT = [("F", "C"), ("F", "G"), ("F", "C"), ("F", "G")]
DARK = ["Am", "Dm", "Am", "Dm"]
for k, s in enumerate(PAIRS):
    dark_bar(s, 2.5, DARK[k])
    add(scratch(), s + 1.6, 0.6)
    add(crumple(), s + 2.05, 0.7)
    add(whoosh(0.6), s + 1.9, 0.35)
    a, b = BRIGHT[k]
    bright_bar(s + 2.5, 2.5, a)
    bright_bar(s + 5.0, 2.5, b)
    add(chime(84), s + 2.55, 0.12, pan=-0.3)
    add(chime(91), s + 2.62, 0.1, pan=0.3)
    add(chime(96), s + 3.9, 0.08)  # onay rozeti

# kapanış — gerilim
dark_bar(CLOSE, 2.5, "Dm")
dark_bar(CLOSE + 2.5, 2.5, "Am")
dark_bar(CLOSE + 5.0, 2.5, "E")
for tw in (37.2, 37.8, 38.4):
    add(thud(), tw, 0.6)
add(whoosh(1.2), CLOSE + 6.3, 0.35)

# son — C majör çözülme
add(scratch(), END, 0.4)
bright_bar(END, 2.5, "C")
bright_bar(END + 2.5, 1.25, "C", beat=False)
for i, n in enumerate((84, 88, 91, 96)):
    add(chime(n), END + 0.4 + i * 0.12, 0.1, pan=(-0.4, 0.4)[i % 2])


def reverb(x, seed):
    r = np.random.default_rng(seed)
    t = tt(2.0)
    ir = r.uniform(-1, 1, len(t)) * np.exp(-t / 0.6)
    ir[0] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    n = len(x) + len(ir)
    return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]


L = L + reverb(L, 1) * 0.28
R = R + reverb(R, 2) * 0.28
mix = np.tanh(np.stack([L, R], axis=1) * 1.2)
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
