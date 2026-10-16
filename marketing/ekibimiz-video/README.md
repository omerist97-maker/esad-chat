# Ekibimiz — Network Marketing Reels Videosu

`ekibimiz-network-marketing.mp4` — 20 sn, 1080x1920 (Instagram Reels), 30 fps, H.264 + AAC.
Stil: zümrüt yeşili + altın, numaralı sahneler (01–06), sahneler arası panel itme geçişi, ilerleme noktaları.

| Süre | Sahne |
|---|---|
| 0–2 sn | "NEDEN BİZİM EKİBİMİZ?" → büyüyen "6 SEBEP" |
| 2–4 sn | 01 — EKİBİMİZDE BİZİMLE BAŞLAYANLAR (tek tek katılan kişiler, "+1") |
| 4–6 sn | 02 — YALNIZ DEĞİLSİNİZ (merkezdeki kişinin etrafında birleşen ekip) |
| 6–8 sn | 03 — GÜÇLÜ SPONSORLAR (ışınlı kalkan + yıldız, yükselen oklar) |
| 8–10 sn | 04 — HER GÜN ONLINE EĞİTİMLER (telefonda CANLI yayın, 7 günün yanması) |
| 10–12 sn | 05 — TAKIM ÇALIŞMASI (kenetlenip dönen dişliler) |
| 12–14 sn | 06 — SONUÇ VEREN YÖNTEMLER (yükselen grafik, ok, onay rozeti) |
| 14–16 sn | "HEPSİ BU EKİPTE" — 6 maddenin tek tek işaretlendiği özet |
| 16–20 sn | "SEN DE ARAMIZA KATIL!" + "BİLGİ İÇİN DM" |

Müzik: 120 BPM, G majör (G–D–Em–C) motivasyonel piano-house; her başlıkta parıltı sesi. Telifsiz, `music.py` ile sentezlenir.

## Yeniden üretme

```bash
python3 music.py music.wav
python3 render.py music.wav ekibimiz-network-marketing.mp4
```

Gereksinimler: Python 3, numpy, Pillow, ffmpeg, Inter Display fontu.
Başlık metinleri `render.py` içindeki `HEADINGS` ve `RECAP` listelerindedir.
