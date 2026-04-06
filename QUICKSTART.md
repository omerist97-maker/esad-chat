# ⚡ Esad Chat - Hızlı Kurulum

## 📦 1. Dependencies Yükleme

```bash
cd c:\Users\omerz\Deneme\esad-chat
npm install
```

**Eğer hata alırsan:**
```bash
# Option 1: Cache temizle
npm cache clean --force
npm install

# Option 2: Registry değiştir
npm config set registry https://registry.npmjs.org/
npm install

# Option 3: node_modules sil
rm -rf node_modules package-lock.json
npm install
```

---

## 🗄️ 2. Database Kurulumu

### PostgreSQL Kurulu mı?
```bash
psql --version
```

Değilse:
- **Windows**: https://www.postgresql.org/download/windows/
- **Docker**: `docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15`

### Database Oluştur
```bash
# psql ile bağlan
psql -U postgres

# Database oluştur
CREATE DATABASE esad_chat_db;
\q
```

---

## 🔗 3. .env.local Düzenle

**Dosya:** `c:\Users\omerz\Deneme\esad-chat\.env.local`

```env
# PostgreSQL connection string
DATABASE_URL="postgresql://postgres:password@localhost:5432/esad_chat_db"

# Environment
NODE_ENV="development"
```

**Değiştirelecek yerler:**
- `postgres` → PostgreSQL kullanıcısı
- `password` → Senin postgresql password'ü
- `localhost:5432` → Database server adresi

---

## 🔄 4. Prisma Setup

```bash
# Prisma client oluştur
npx prisma generate

# Database schema'sını push et
npx prisma db push

# Mock veri yükle
npm run db:seed
```

---

## 🚀 5. Dev Server'ı Başlat

```bash
npm run dev
```

**Çıktı şöyle görülmeli:**
```
> next dev
  ▲ Next.js 16.2.2
  - Local:        http://localhost:3000
  - Environments: .env.local
  ✓ Ready in 2.5s
```

---

## 🌐 6. Dashboard'ı Aç

Browser'ı aç ve şu adrese git:

👉 **http://localhost:3000/dashboard**

**Görünmesi gereken:**
- Sol panel: 5 müşteri
- Orta panel: Sohbet penceresinde "Bir sohbet seçin" mesajı
- Sağ panel: "Müşteri detaylarını görüntülemek için bir sohbet seçin"

Bir müşteriye tıkla → Müşteri detayları görünmeli!

---

## 🧪 7. Webhook Testi

### cURL Komutu
```bash
curl -X POST http://localhost:3000/api/webhook/n8n \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Webhook Test",
    "customer_email": "webhook-test@example.com",
    "customer_phone": "+90 555 000 0000",
    "message": "Bu bir webhook test mesajıdır.",
    "sender": "customer"
  }'
```

### Expected Response
```json
{
  "success": true,
  "data": {
    "customer_id": "clv...",
    "conversation_id": "clv...",
    "message_id": "clv..."
  }
}
```

---

## 🎛️ 8. Faydalı Komutlar

```bash
# Database görüntüle (Web UI)
npx prisma studio

# Build et (production)
npm run build
npm start

# TypeScript kontrol
npx tsc --noEmit

# Database seed'i yeniden çalıştır
npm run db:seed

# Migration oluştur
npx prisma migrate dev --name your_migration_name
```

---

## ❌ Troubleshooting

### Error: "Unable to require database client"
```bash
# Çözüm: Prisma client oluştur
npx prisma generate
```

### Error: "Connection refused" (PostgreSQL)
```bash
# PostgreSQL çalışıyor mu kontrol et
psql -U postgres -d esad_chat_db

# Değilse başlat (Windows):
# Services > PostgreSQL başlat
```

### Error: "Database doesn't exist"
```bash
# Database oluştur
createdb -U postgres esad_chat_db

# Veya SQL'den:
psql -U postgres -c "CREATE DATABASE esad_chat_db;"
```

### npm install takes too long
```bash
# Registry değiştir
npm config set registry https://registry.npmmirror.com/

# Tekrar dene
npm install
```

---

## ✨ Success Indicators

✓ `npm install` başarılı → node_modules folder oluştu
✓ `npx prisma generate` → .prisma/client folder oluştu
✓ `npm run dev` başladı → "Ready in X.XXs" mesajı
✓ Dashboard açılı → 5 müşteri görünüyor
✓ Webhook test → 200 OK response

---

## 📍 Tamamlandı mı?

Eğer yukarıdaki tüm adımları başarıyla tamamladıysan:

🎉 **Esad Chat Dashboard Kurulumu %100 Tamamlandı!**

**Ne sırada?**
- Dashboard'ı keşfet (müşteri tıkla, mesajları gör)
- n8n Workflow'unu kur
- Real-time features ekle (opsiyonel)
- Produksyona deploy et

---

## 📞 İhtiyaç duyuyorsan

- **Setup sorunları**: Bana yaz, `npm install` sorunu çözerim
- **PostgreSQL**: Bana yaz, database setup yardımı yaparım
- **Webhook**: SETUP.md'deki örnekleri kullan

**Başarılar! 🚀**
