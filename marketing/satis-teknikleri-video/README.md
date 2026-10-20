# Network Marketingde 5 Satış Tekniği (Reels)

`satis-teknikleri.mp4` — 30 sn, 1080x1920 (Instagram Reels), 30 fps, H.264 + AAC.
Stil: açık defter zemini, lacivert tipografi, fosforlu yeşil vurgu kalemi, mavi kartlar; sahneler arası dikey kaydırma.

| Süre | Sahne |
|---|---|
| 0–2 sn | "Network marketingde SATIŞ YAPMAYA ÇALIŞMA." |
| 2–4 sn | "Bunun yerine BU 5 TEKNİĞİ UYGULA." |
| 4–8 sn | 1 — ÖNCE DİNLE · ❌ Hemen ürünü anlatmak · ✅ Soru sorup ihtiyacı keşfetmek |
| 8–12 sn | 2 — ÜRÜNÜ DEĞİL, ÇÖZÜMÜ ANLAT · ❌ Özellikleri tek tek saymak · ✅ Hayatına ne katacağını göstermek |
| 12–16 sn | 3 — HİKÂYENİ PAYLAŞ · ❌ Ezber sunum yapmak · ✅ Kendi deneyimini samimice anlatmak |
| 16–20 sn | 4 — İTİRAZI KUCAKLA · "Seni anlıyorum." → "Ben de öyle hissetmiştim." → "Sonra şunu fark ettim…" |
| 20–24 sn | 5 — TAKİBİ BIRAKMA · ❌ Bir kez sorup vazgeçmek · ✅ Nazik ve düzenli takip etmek |
| 24–30 sn | "SATIŞ YAPMA, GÜVEN İNŞA ET." + "KAYDET — Bir sonraki görüşmende uygula." |

Müzik: 120 BPM E Dorian funky groove (slap bas, Rhodes, gitar vuruşları); ❌ satırında buzzer, ✅ satırında "ding".
Telifsiz, `music.py` ile sentezlenir.

## Yeniden üretme

```bash
python3 music.py music.wav
python3 render.py music.wav satis-teknikleri.mp4
```

Metinler `render.py` içindeki `TIPS` listesindedir.
