# Tek Bir Cümle — Kilo Verme Sürecinde İç Ses (Reels)

`tek-cumle-kilo-verme.mp4` — 47,5 sn, 1080x1920 (Instagram Reels), 30 fps, H.264 + AAC.

Kurgu: ❌ cümle karanlık zeminde gri "iç ses" balonunda belirir → kırmızıyla üstü çizilir → balon buruşup düşer →
ekran sıcak renge döner → ✅ cümle kelime kelime yazılır, onay rozeti ve parıltılar.

| Süre | Sahne |
|---|---|
| 0–2,5 sn | "Tek bir cümleyi değiştirince ne olduğunu göstereyim…" |
| 2,5–6,25 sn | "Kilo verme sürecinde kendine en çok hangi cümleyi söylüyorsun?" |
| 6,25–36,25 sn | 4 çift: ❌ (2,5 sn) → ✅ (5 sn) |
| 36,25–43,75 sn | "Çünkü beynine sürekli 'Yapamıyorum', 'Başaramıyorum', 'Olmuyor' mesajları gönderdiğinde kendini daha da çaresiz hissedebilirsin." |
| 43,75–47,5 sn | Olumsuz balonlar çizilip kaybolur → "Cümleni değiştir, sürecin değişsin." |

Müzik: 96 BPM duygusal piyano + lo-fi ritim. ❌ bölümlerde minör ve boğuk (kalp atışı), ✅ bölümlerde majör ve aydınlık;
üstü çizme, kâğıt buruşturma ve parıltı efektleri. Telifsiz, `music.py` ile sentezlenir.

## Yeniden üretme

```bash
python3 music.py music.wav
python3 render.py music.wav tek-cumle-kilo-verme.mp4
```

Metinler `render.py` başındaki `HOOK1`, `HOOK2`, `PAIRS`, `CLOSE_*`, `END_*` sabitlerindedir
(`*` ile başlayan kelimeler vurgulanır).
