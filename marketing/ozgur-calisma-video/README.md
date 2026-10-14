# Özgür Çalışma — Network Marketing Tanıtım Videosu

`ozgur-calisma-network-marketing.mp4` — 20 sn, 1080x1920 (Reels / TikTok / Shorts), 30 fps, H.264 + AAC.

| Süre | Sahne |
|---|---|
| 0–2 sn | "HER GÜN AYNI MESAİ?" — yanıp sönen 09:00, dolan mesai çubuğu |
| 2–4 sn | DROP — "09:00–18:00" üstü çizilir, "MESAİ YOK." |
| 4–7 sn | "SAATLERİNİ SEN BELİRLE" — dönen saat, 06:00 / 14:00 / 23:00 etiketleri |
| 7–10 sn | "OFİSİN:" EVİN → BİR KAFE → SAHİL → DÜNYANIN HER YERİ (her vuruşta) |
| 10–12 sn | "ÖZGÜR SAATLER + ÖZGÜR ORTAM" bölünmüş ekran, gerilim |
| 12–16 sn | DROP — "KENDİ İŞİNİN PATRONU OL", büyüyen ekip ağı |
| 16–20 sn | "ÖZGÜRLÜĞÜ SEÇ." + "HEMEN BAŞLA" / DM çağrısı |

Müzik 120 BPM, A minör (Am–F–C–G), telifsiz; `music.py` ile sentezlenir.

## Yeniden üretme

```bash
python3 music.py music.wav
python3 render.py music.wav ozgur-calisma-network-marketing.mp4
```

Gereksinimler: Python 3, numpy, Pillow, ffmpeg, Inter Display fontu.
Metinleri değiştirmek için `render.py` içindeki sahne fonksiyonlarını düzenleyin.
