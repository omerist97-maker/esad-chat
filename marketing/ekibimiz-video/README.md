# Ekibimiz — Network Marketing Reels Videosu

`ekibimiz-network-marketing.mp4` — 20 sn, 1080x1920 (Instagram Reels), 30 fps, H.264 + AAC.
Stil: zümrüt yeşili + altın, numaralı sahneler (01–05), sahneler arası panel itme geçişi, ilerleme noktaları.

| Süre | Sahne |
|---|---|
| 0–2 sn | Hitap: "EKİBİMİZDE BİZİMLE BAŞLAYANLAR," — ekibe katılan kişiler, "BU MESAJ SİZİN İÇİN" |
| 2–4 sn | "BİLMENİZİ İSTEDİĞİMİZ 5 ŞEY VAR" |
| 4–6 sn | 01 — YALNIZ DEĞİLSİNİZ (merkezdeki kişinin etrafında birleşen ekip) |
| 6–8 sn | 02 — GÜÇLÜ SPONSORLAR (ışınlı kalkan + yıldız, yükselen oklar) |
| 8–10 sn | 03 — HER GÜN ONLINE EĞİTİMLER (telefonda CANLI yayın, 7 günün yanması) |
| 10–12 sn | 04 — TAKIM ÇALIŞMASI (kenetlenip dönen dişliler) |
| 12–14 sn | 05 — SONUÇ VEREN YÖNTEMLER (yükselen grafik, ok, onay rozeti) |
| 14–16 sn | "HEPSİ BU EKİPTE" — 5 maddenin tek tek işaretlendiği özet |
| 16–20 sn | "İYİ Kİ BİZİMLE BAŞLADINIZ!" + "BİRLİKTE BÜYÜYORUZ" |

Müzik: 120 BPM, G majör (G–D–Em–C) motivasyonel piano-house; her başlıkta parıltı sesi. Telifsiz, `music.py` ile sentezlenir.

## Yeniden üretme

```bash
python3 music.py music.wav
python3 render.py music.wav ekibimiz-network-marketing.mp4
```

Gereksinimler: Python 3, numpy, Pillow, ffmpeg, Inter Display fontu.
Başlık metinleri `render.py` içindeki `HEADINGS` ve `RECAP` listelerindedir.
