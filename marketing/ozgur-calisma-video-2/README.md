# Özgür Çalışma #2 — "Hayatına göre çalış"

`ozgur-calisma-network-marketing-2.mp4` — 20 sn, 1080x1920 (Reels / TikTok / Shorts), 30 fps, H.264 + AAC.
Görsel stil: açık krem zemin, kalın sert gölgeli (neo-brütalist) tipografi, hikâye ilerleme çubuğu, film greni.

| Süre | Sahne |
|---|---|
| 0–1,6 sn | Gri pazartesi: titreyen alarm, ekrana basılan damgalar "ALARM. TRAFİK. MESAİ. YETER!" |
| 1,6–4,8 sn | DROP — "TAKVİMİN SENİN." Haftalık takvimde 09:00–18:00 yerine SPOR, AİLE GÜNÜ, SEYAHAT… |
| 4,8–8 sn | "GÜNÜNÜ SEN TASARLA." Gün çizelgesine sürüklenip oturan bloklar |
| 8–9,6 sn | "LAPTOP + İNTERNET = OFİS." |
| 9,6–11,2 sn | "BUGÜN OFİSİN:" haritaya düşen pinler — İSTANBUL, BODRUM, KAPADOKYA, BALİ |
| 11,2–12,8 sn | "PATRONUN KİM Mİ?" ayna — "AYNAYA BAK." (gerilim) |
| 12,8–16 sn | DROP — "TEK BAŞINA DEĞİL." 1'den 25'e büyüyen ekip, "EKİBİNLE BÜYÜ." |
| 16–20 sn | "İŞİNE GÖRE DEĞİL, HAYATINA GÖRE ÇALIŞ." + "ŞİMDİ KATIL" / DM çağrısı |

Müzik: 150 BPM, D minör (Dm–B♭–Gm–A) trap/phonk — 808 bas, cowbell riff, alarm girişi. Telifsiz, `music.py` ile sentezlenir.

## Yeniden üretme

```bash
python3 music.py music.wav
python3 render.py music.wav ozgur-calisma-network-marketing-2.mp4
```

Gereksinimler: Python 3, numpy, Pillow, ffmpeg, Inter Display fontu.
