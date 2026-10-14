"""20 sn, 120 BPM, A minör 'drop' müziği — tamamen numpy ile sentezlenir."""
import sys
import wave
import numpy as np

SR = 44100
DUR = 20.0
BPM = 120
BEAT = 60 / BPM          # 0.5 s
BAR = BEAT * 4           # 2 s
S16 = BEAT / 4
N = int(SR * DUR)
rng = np.random.default_rng(7)

L = np.zeros(N)
R = np.zeros(N)


def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * (1 - max(pan, 0))
    R[i:i + len(sig)] += sig * gain * (1 + min(pan, 0))


def tt(d):
    return np.arange(int(d * SR)) / SR


def note(n):  # MIDI -> Hz
    return 440 * 2 ** ((n - 69) / 12)


def saw(freq, d, harmonics=24, decay=0.0, bright=0.0):
    t = tt(d)
    out = np.zeros_like(t)
    for k in range(1, harmonics + 1):
        if freq * k > 16000:
            break
        amp = 1 / k
        if decay:
            amp = amp * np.exp(-t * decay * (1 + k * bright))
        out += amp * np.sin(2 * np.pi * freq * k * t)
    return out


def lowpass(x, width):
    k = np.ones(width) / width
    return np.convolve(x, k, mode="same")


# ---------- davullar ----------
def kick():
    t = tt(0.45)
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7)
    s[:200] += rng.uniform(-1, 1, 200) * np.linspace(0.6, 0, 200)
    return np.tanh(s * 2.2)


def clap():
    t = tt(0.3)
    nz = rng.uniform(-1, 1, len(t))
    nz = nz - lowpass(nz, 6)
    env = np.exp(-t * 18)
    for off in (0.0, 0.011, 0.022):
        env += 0.6 * np.exp(-np.maximum(t - off, 0) * 120) * (t >= off)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.5
    return nz * env * 0.7 + tone


def hat(open_=False):
    t = tt(0.25 if open_ else 0.06)
    nz = rng.uniform(-1, 1, len(t))
    nz = np.diff(np.diff(nz, prepend=0), prepend=0) * 0.5
    return nz * np.exp(-t * (14 if open_ else 70))


def tick(hi):
    t = tt(0.04)
    return np.sin(2 * np.pi * (3200 if hi else 2400) * t) * np.exp(-t * 160)


def impact():
    t = tt(3.0)
    f = 28 + 50 * np.exp(-t * 3)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.4)
    nz = rng.uniform(-1, 1, len(t))
    crash = (nz - lowpass(nz, 3)) * np.exp(-t * 2.2) * 0.35
    body = lowpass(rng.uniform(-1, 1, len(t)), 40) * np.exp(-t * 6) * 2.5
    return np.tanh((boom * 1.4 + crash + body) * 1.3)


def riser(d):
    t = tt(d)
    ramp = (t / d) ** 2.2
    nz = rng.uniform(-1, 1, len(t))
    hp = nz - lowpass(nz, 12)
    f = 180 * (12 ** (t / d))
    sweep = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.01) / SR)
    return (hp * 0.6 + sweep * 0.25) * ramp


# ---------- akorlar ----------
CHORDS = {  # A minör: i - VI - III - VII
    "Am": [57, 60, 64], "F": [53, 57, 60], "C": [48, 52, 55], "G": [55, 59, 62],
}
ROOT = {"Am": 33, "F": 29, "C": 36, "G": 31}

synth_bus_L = np.zeros(N)
synth_bus_R = np.zeros(N)


def add_synth(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    sig = sig[: N - i]
    synth_bus_L[i:i + len(sig)] += sig * gain * (1 - max(pan, 0))
    synth_bus_R[i:i + len(sig)] += sig * gain * (1 + min(pan, 0))


STAB_POS = [0, 3, 6, 8, 11, 14]


def stab_bar(t0, chord, gain=0.22):
    for p in STAB_POS:
        for j, n in enumerate(CHORDS[chord] + [CHORDS[chord][0] + 12]):
            s = saw(note(n + 12), 0.28, decay=9, bright=0.35)
            add_synth(s, t0 + p * S16, gain * 0.5, pan=(-0.4 if j % 2 else 0.4))


def bass_bar(t0, chord, gain=0.5):
    f = note(ROOT[chord])
    for p in range(16):
        if p % 4 == 0:
            continue
        s = saw(f, S16 * 0.9, harmonics=10, decay=14, bright=0.25)
        s += np.sin(2 * np.pi * f * tt(S16 * 0.9)) * 0.8
        add(np.tanh(s * 1.5), t0 + p * S16, gain)


def pad(t0, d, chord, gain=0.12):
    for n in CHORDS[chord]:
        for det, pan in ((-0.08, -0.6), (0.0, 0.0), (0.08, 0.6)):
            s = saw(note(n + det), d, harmonics=12)
            s = lowpass(s, 30)
            env = np.minimum(1, tt(d) / 0.3) * np.minimum(1, (d - tt(d)) / 0.4)
            add_synth(s * env, t0, gain / 3, pan)


def full_beat(t0, bars, kick_on=True):
    for b in range(bars):
        for q in range(4):
            tb = t0 + b * BAR + q * BEAT
            if kick_on:
                add(kick(), tb, 0.95)
            if q in (1, 3):
                add(clap(), tb, 0.45)
            add(hat(), tb + BEAT / 2, 0.28, pan=0.3)
            add(hat(), tb + BEAT / 4, 0.12, pan=-0.3)
            add(hat(), tb + 3 * BEAT / 4, 0.12, pan=-0.3)


# 0-2 sn: intro — saat tik-takları + riser
for i in range(8):
    add(tick(i % 2 == 0), i * BEAT / 2, 0.35)
pad(0, 2.0, "Am", 0.08)
add(riser(2.0), 0, 0.35)
for i in range(4):  # son vuruşta snare rulosu
    add(clap(), 1.5 + i * S16, 0.15 + 0.08 * i)

# 2-10 sn: DROP 1
add(impact(), 2.0, 0.9)
for b, ch in enumerate(["Am", "F", "C", "G"]):
    t0 = 2.0 + b * BAR
    stab_bar(t0, ch)
    bass_bar(t0, ch)
full_beat(2.0, 4)

# 10-12 sn: breakdown + build
pad(10.0, 2.0, "Am", 0.16)
add(riser(2.0), 10.0, 0.45)
roll = [10.0 + i * BEAT for i in range(2)] + [11.0 + i * S16 for i in range(4)] + \
       [11.5 + i * S16 / 2 for i in range(8)]
for i, tr in enumerate(roll):
    add(clap(), tr, 0.12 + 0.3 * i / len(roll))
add(kick(), 10.0, 0.9)

# 12-18 sn: DROP 2
add(impact(), 12.0, 1.0)
for b, ch in enumerate(["Am", "F", "G"]):
    t0 = 12.0 + b * BAR
    stab_bar(t0, ch, 0.26)
    bass_bar(t0, ch, 0.55)
full_beat(12.0, 3)

# 18 sn: final vuruş
add(impact(), 18.0, 1.1)
add(kick(), 18.0, 1.0)
for j, n in enumerate(CHORDS["Am"] + [69]):
    s = saw(note(n + 12), 2.0, decay=1.6, bright=0.2)
    add_synth(s, 18.0, 0.18, pan=(-0.5 if j % 2 else 0.5))

# ---------- sidechain, reverb, master ----------
kick_times = [2.0 + i * BEAT for i in range(16)] + [12.0 + i * BEAT for i in range(12)]
sc = np.ones(N)
tN = np.arange(N) / SR
for kt in kick_times:
    i = int(kt * SR)
    seg = tN[i:i + int(0.3 * SR)] - kt
    sc[i:i + len(seg)] = np.minimum(sc[i:i + len(seg)], 1 - 0.75 * np.exp(-seg / 0.07))


def reverb(x, seed):
    r = np.random.default_rng(seed)
    t = tt(1.4)
    ir = r.uniform(-1, 1, len(t)) * np.exp(-t / 0.35)
    ir[0] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    n = len(x) + len(ir)
    y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]
    return y


sl = synth_bus_L * sc
sr_ = synth_bus_R * sc
L += sl + reverb(sl, 1) * 0.25
R += sr_ + reverb(sr_, 2) * 0.25
L[: int(2 * SR)] *= 1.0
mix = np.stack([L, R], axis=1)
mix = np.tanh(mix * 1.1)
fade = np.ones(N)
fade[-int(0.6 * SR):] = np.linspace(1, 0, int(0.6 * SR))
mix *= fade[:, None]
mix /= np.max(np.abs(mix)) / 0.8

out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("ok", out)
