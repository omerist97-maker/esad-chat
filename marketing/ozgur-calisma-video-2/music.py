"""20 sn, 150 BPM, D minör trap/phonk müziği (808 bas, cowbell riff) — numpy ile sentezlenir."""
import sys
import wave
import numpy as np

SR = 44100
DUR = 20.0
BEAT = 0.4               # 150 BPM
BAR = BEAT * 4           # 1.6 s
STEP = BEAT / 4          # 16'lık = 0.1 s
N = int(SR * DUR)
rng = np.random.default_rng(11)
L = np.zeros(N)
R = np.zeros(N)


def tt(d):
    return np.arange(int(d * SR)) / SR


def note(n):
    return 440 * 2 ** ((n - 69) / 12)


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(round(t0 * SR))
    if i >= N:
        return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * (1 - max(pan, 0))
    R[i:i + len(sig)] += sig * gain * (1 + min(pan, 0))


def lowpass(x, width):
    return np.convolve(x, np.ones(width) / width, mode="same")


# ---------- sesler ----------
def kick():
    t = tt(0.3)
    f = 50 + 140 * np.exp(-t * 40)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)
    s[:150] += rng.uniform(-1, 1, 150) * np.linspace(0.8, 0, 150)
    return np.tanh(s * 2.5)


def snare():
    t = tt(0.35)
    nz = rng.uniform(-1, 1, len(t))
    nz = nz - lowpass(nz, 4)
    body = np.sin(2 * np.pi * (180 + 60 * np.exp(-t * 50)) * t) * np.exp(-t * 25)
    clap = np.zeros_like(t)
    for off in (0.0, 0.008, 0.017):
        clap += np.exp(-np.maximum(t - off, 0) * 90) * (t >= off)
    return np.tanh((nz * (np.exp(-t * 14) * 0.8 + clap * 0.5) + body * 0.8) * 1.5)


def hat(d=0.05):
    t = tt(d)
    nz = rng.uniform(-1, 1, len(t))
    nz = np.diff(np.diff(nz, prepend=0), prepend=0) * 0.5
    return nz * np.exp(-t * 90)


def cowbell(n, d=0.22):
    t = tt(d)
    f = note(n)
    sq = np.sign(np.sin(2 * np.pi * f * t)) + np.sign(np.sin(2 * np.pi * f * 1.48 * t))
    sq = sq - lowpass(sq, 8)          # incelt
    return lowpass(sq, 3) * np.exp(-t * 16) * 0.5


def bass808(n, d, glide_from=None):
    t = tt(d)
    f = np.full_like(t, note(n))
    if glide_from is not None:
        g = np.exp(-t * 18)
        f = note(n) + (note(glide_from) - note(n)) * g
    f = f * (1 + 1.2 * np.exp(-t * 60))   # vuruş başı pitch
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.exp(-t * 1.2) * np.minimum(1, (d - t) / 0.03)
    return np.tanh(s * env * 3.0) * 0.8


def stamp():
    t = tt(0.5)
    thud = np.sin(2 * np.pi * (60 + 120 * np.exp(-t * 30)) * t) * np.exp(-t * 9)
    sn = np.zeros_like(t)
    sn[:len(snare())] = snare()[:len(t)]
    return np.tanh(thud * 2) * 0.9 + sn * 0.4


def alarm(d):
    t = tt(d)
    sq = np.sign(np.sin(2 * np.pi * 2100 * t)) * 0.3
    gate = ((t * 16) % 1 < 0.5).astype(float)
    return lowpass(sq * gate, 3)


def impact():
    t = tt(2.5)
    boom = np.sin(2 * np.pi * np.cumsum(30 + 60 * np.exp(-t * 4)) / SR) * np.exp(-t * 1.5)
    nz = rng.uniform(-1, 1, len(t))
    crash = (nz - lowpass(nz, 3)) * np.exp(-t * 2.5) * 0.3
    return np.tanh((boom * 1.5 + crash) * 1.2)


def riser(d):
    t = tt(d)
    ramp = (t / d) ** 2.5
    nz = rng.uniform(-1, 1, len(t))
    f = 200 * (10 ** (t / d))
    sw = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return ((nz - lowpass(nz, 10)) * 0.6 + sw * 0.25) * ramp


def pad(t0, d, notes, gain):
    for n in notes:
        for det, pan in ((-0.1, -0.7), (0.1, 0.7)):
            t = tt(d)
            f = note(n + det)
            s = sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 9))
            env = np.minimum(1, t / 0.2) * np.minimum(1, (d - t) / 0.3)
            add(lowpass(s, 20) * env, t0, gain / len(notes), pan)


# Dm - Bb - Gm - A
CHORDS = [("Dm", 38, [62, 65, 69]), ("Bb", 34, [58, 62, 65]), ("Gm", 31, [55, 58, 62]), ("A", 33, [57, 61, 64])]
KICK_STEPS = [0, 7, 10]
RIFF = {0: 74, 3: 74, 6: 77, 8: 74, 10: 79, 11: 77, 13: 76, 14: 72}


def trap_bar(t0, bi, cow_gain=0.35, rolls=False):
    name, root, notes = CHORDS[bi % 4]
    prev_root = CHORDS[(bi - 1) % 4][1]
    for i, s in enumerate(KICK_STEPS):
        add(kick(), t0 + s * STEP, 0.85)
        nxt = KICK_STEPS[i + 1] if i + 1 < len(KICK_STEPS) else 16
        add(bass808(root, (nxt - s) * STEP, glide_from=(prev_root if i == 0 else None)), t0 + s * STEP, 0.75)
    add(snare(), t0 + 8 * STEP, 0.55)
    for s in range(16):
        if rolls and s >= 12:
            for k in range(3):
                add(hat(0.03), t0 + s * STEP + k * STEP / 3, 0.14, pan=0.25)
        else:
            add(hat(), t0 + s * STEP, 0.18 if s % 2 == 0 else 0.1, pan=0.25)
    tr = {"Dm": 0, "Bb": -4, "Gm": -7, "A": -5}[name]
    for s, n in RIFF.items():
        add(cowbell(n + tr), t0 + s * STEP, cow_gain, pan=-0.2 if s % 2 else 0.2)
    pad(t0, BAR, notes, 0.08)


# 0 - 1.6: alarm + damga vuruşları + riser
add(alarm(1.2), 0.0, 0.18)
for i in range(4):
    add(stamp(), i * BEAT, 0.7)
add(riser(1.6), 0.0, 0.35)
for i in range(4):
    add(snare(), 1.2 + i * STEP, 0.12 + 0.07 * i)

# 1.6 - 11.2: ana bölüm (6 ölçü)
add(impact(), 1.6, 0.85)
for b in range(6):
    trap_bar(1.6 + b * BAR, b, rolls=(b % 2 == 1))

# 11.2 - 12.8: breakdown — 808 slide + riser + snare rulosu
pad(11.2, 1.6, [62, 65, 69], 0.16)
add(bass808(26, 1.4, glide_from=50), 11.2, 0.8)
add(riser(1.5), 11.2, 0.5)
roll = [11.2 + i * BEAT for i in range(2)] + [12.0 + i * STEP for i in range(4)] + \
       [12.4 + i * STEP / 2 for i in range(6)]
for i, tr in enumerate(roll):
    add(snare(), tr, 0.12 + 0.35 * i / len(roll))

# 12.8 - 17.6: ikinci drop (3 ölçü)
add(impact(), 12.8, 1.0)
for b in range(3):
    trap_bar(12.8 + b * BAR, b, cow_gain=0.45, rolls=(b == 2))

# 17.6: final
add(impact(), 17.6, 1.1)
add(kick(), 17.6, 1.0)
add(bass808(38, 2.3), 17.6, 0.85)
for n in (74, 77, 81):
    add(cowbell(n, 1.2), 17.6, 0.3)
pad(17.6, 2.3, [62, 65, 69], 0.14)


def reverb(x, seed):
    r = np.random.default_rng(seed)
    t = tt(1.2)
    ir = r.uniform(-1, 1, len(t)) * np.exp(-t / 0.3)
    ir[0] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    n = len(x) + len(ir)
    return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]


L = L + reverb(L, 1) * 0.12
R = R + reverb(R, 2) * 0.12
mix = np.tanh(np.stack([L, R], axis=1) * 1.1)
fade = np.ones(N)
fade[-int(0.5 * SR):] = np.linspace(1, 0, int(0.5 * SR))
mix *= fade[:, None]
mix /= np.max(np.abs(mix)) / 0.8

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("ok", out)
