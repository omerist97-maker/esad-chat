# Esad Chat Dashboard - Kurulum Rehberi

## 📋 Proje Özeti
- **Next.js 14+** (App Router) ile modern chat dashboard
- **Tailwind CSS** + **Lucide Icons** ile UI
- **Prisma ORM** + **PostgreSQL** ile veri yönetimi
- **n8n Webhook** entegrasyonu hazır
- **3-kolon layout**: Sol (Müşteri Listesi) | Orta (Sohbet) | Sağ (CRM Detayları)

---

## 🚀 Başlangıç

### 1. **PostgreSQL Kurulumu**

Eğer PostgreSQL'e sahip değilseniz:
- **Windows**: https://www.postgresql.org/download/windows/
- Docker kullanıyorsanız:
  ```bash
  docker run --name esad-postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15
  ```

Veya **Supabase** (yönetilen PostgreSQL):
1. https://supabase.com adresine git
2. Yeni proje oluştur
3. Connection string'i kopyala

### 2. **.env.local Düzenleme**

`c:\Users\omerz\Deneme\esad-chat\.env.local` dosyasını aç ve DATABASE_URL'i güncelle:

```env
# PostgreSQL bağlantı stringi örneği:
# Lokal: postgresql://postgres:password@localhost:5432/esad_chat_db
# Supabase: postgresql://user:password@host:5432/db_name

DATABASE_URL="postgresql://postgres:password@localhost:5432/esad_chat_db"
NODE_ENV="development"
```

### 3. **Dependencies Kurulumu**

Ağ bağlantı sorunları olabilir, bu durumda:

```bash
cd c:\Users\omerz\Deneme\esad-chat

# Seçenek 1: Standard npm install
npm install

# Seçenek 2: Registry değiştir (sorun olursa)
npm config set registry https://registry.npmjs.org/
npm install

# Seçenek 3: NPM cache temizle
npm cache clean --force
npm install
```

### 4. **Prisma Kurulumu**

```bash
# Database migration'ı çalıştır
npx prisma db push

# Veya migrate dev
npx prisma migrate dev --name init

# Seed ile mock veri yükle
npx prisma db seed
```

### 5. **Dev Server'ı Başlat**

```bash
npm run dev
```

Dashboard şu adreste açılıyor:
👉 **http://localhost:3000/dashboard**

---

## 📁 Proje Yapısı

```
esad-chat/
├── app/
│   ├── api/
│   │   ├── webhook/n8n/route.ts          ← n8n Webhook handler
│   │   ├── conversations/route.ts        ← Sohbet listesi
│   │   └── conversations/[id]/messages/  ← Mesajlar
│   │
│   ├── dashboard/
│   │   ├── layout.tsx                    ← 3-kolon grid layout
│   │   ├── page.tsx                      ← Ana dashboard
│   │   └── components/
│   │       ├── ChatList.tsx              ← Müşteri listesi
│   │       ├── ChatWindow.tsx            ← Sohbet penceresі
│   │       └── CustomerDetails.tsx       ← CRM detayları
│   │
│   ├── layout.tsx                        ← Root layout
│   └── globals.css                       ← Tailwind & global stiller
│
├── lib/
│   ├── db.ts                             ← Prisma client
│   └── types.ts                          ← TypeScript interfaces
│
├── prisma/
│   ├── schema.prisma                     ← Database schema
│   └── seed.ts                           ← Mock veri
│
├── .env.local                            ← Database bağlantısı
├── package.json
├── tsconfig.json
└── next.config.ts
```

---

## 🔌 n8n Webhook Entegrasyonu

### Webhook Endpoint
```
POST http://localhost:3000/api/webhook/n8n
```

### Payload Formatı
```json
{
  "customer_name": "Ahmet Yılmaz",
  "customer_email": "ahmet@example.com",
  "customer_phone": "+90 532 123 4567",
  "message": "Satın almak istediğim ürün hakkında soru var.",
  "sender": "customer",  // veya "agent"
  "timestamp": "2024-04-04T12:30:00Z"
}
```

### Test Komutu (cURL)
```bash
curl -X POST http://localhost:3000/api/webhook/n8n \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test Müşteri",
    "customer_email": "test@example.com",
    "customer_phone": "+90 555 123 4567",
    "message": "Test mesajı",
    "sender": "customer"
  }'
```

### n8n Workflow Örneği

n8n'de şu adımları takip et:

1. **Trigger**: Webhook (POST)
2. **Set Webhook URL**: `http://your-domain:3000/api/webhook/n8n`
3. **Process Data**: Customer bilgileri ve mesaj birleştir
4. **Send HTTP Request**:
   - Method: POST
   - URL: `http://localhost:3000/api/webhook/n8n`
   - Body: Müşteri ve mesaj data'sı

---

## ✨ Özellikler

### ✅ Tamamlanan
- Modern 3-kolon dashboard layout
- Müşteri listesi (ChatList)
- Sohbet penceresi (ChatWindow)
- CRM müşteri detayları (CustomerDetails)
- n8n Webhook handler
- PostgreSQL entegrasyonu
- Mock veri (5 müşteri, 100+ mesaj)
- Lucide Icons UI
- Responsive Tailwind CSS

### 🚧 Gelecek Özellikleri
- Real-time mesaj updates (WebSocket/SSE)
- Agent yanıt gönderme
- Dosya/Media yükleme
- Müşteri bul/ara
- Chat geçmişi export
- Notification/Bell icon
- Offline desteği

---

## 🧪 Test Adımları

### 1. Dashboard Görünüm
```bash
npm run dev
# http://localhost:3000/dashboard ziyaret et
```
Kontrol listesi:
- ✓ Sol panel: 5 müşteri görsün
- ✓ Orta panel: Seçilen müşterinin mesajları
- ✓ Sağ panel: Müşteri detayları (email, telefon vb)
- ✓ Tıkla ve sohbet değiştir

### 2. Webhook Testi
```bash
# Terminal'den test gönder (Postman veya cURL)
curl -X POST http://localhost:3000/api/webhook/n8n \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Yeni Müşteri",
    "customer_email": "yeni@example.com",
    "customer_phone": "+90 555 000 0000",
    "message": "Webhook test mesajı",
    "sender": "customer"
  }'
```
Kontrol listesi:
- ✓ Response 200 OK dönmeli
- ✓ PostgreSQL'de yeni customer + message oluşmalı
- ✓ Dashboard yenilenince yeni müşteri görülmeli

### 3. API Endpoints Testi
```bash
# Tüm sohbetleri getir
curl http://localhost:3000/api/conversations

# Belirli sohbetin mesajlarını getir
curl http://localhost:3000/api/conversations/{conversation_id}/messages
```

---

## 📚 Komutlar

```bash
# Dev sunucuyu başlat
npm run dev

# Production build
npm run build
npm start

# Prisma tools
npx prisma studio                    # Web UI ile database görüntüle
npx prisma migrate dev               # Yeni migration oluştur
npx prisma db seed                   # Mock veri yükle
npx prisma db push                   # Schema değişiklikleri push et

# TypeScript check
npx tsc --noEmit

# ESLint
npm run lint
```

---

## 🛠️ Troubleshooting

### Database bağlantı hatası
```
Hata: "Error: P1000: Authentication failed"

Çözüm:
1. PostgreSQL servisinin çalışıp çalışmadığını kontrol et
2. DATABASE_URL'deki user/password doğru mu?
3. Database var mı? (CREATE DATABASE esad_chat_db)
```

### Prisma migration hatası
```
Hata: "Error: The database schema is not in sync with the Prisma schema"

Çözüm:
npx prisma migrate reset  # Uyarı: Verileri siler!
```

### Next.js build hatası
```
Hata: "Module not found: @/lib/..."

Çözüm:
1. tsconfig.json'ın paths doğru mu?
2. Dosyaların path'leri kontrol et
3. "npm run build" yeniden çalıştır
```

---

## 📞 n8n Entegrasyonu Detayları

### Customer Email Unique Constraint
Webhook, email'e göre müşteri arama yaptığı için, email alanı unique olmalı.

**Eğer email yok ya n8n'de aynı customer düzenli mesaj gönderiyorsa:**
- `customer_email` alanını boş bırakma
- Her çağrıda aynı email gönder (tekrarlanan müşteri olması için)

### Workflow Örneği (n8n)

```
1. Webhook Trigger (POST /webhook/n8n)
   ↓
2. Process Variables
   - Extract: customer_name, message
   - Map to: Customer data
   ↓
3. HTTP Request
   - POST: http://localhost:3000/api/webhook/n8n
   - Body: Formatted data
   ↓
4. Response
   - Success: 200 OK
   - Error handling
```

---

## 📝 Notlar

- **Database**: PostgreSQL 12+
- **Node.js**: 18+ önerilir
- **Browser**: Chrome/Edge/Firefox (Safari desteklenir)
- **Üretim Dağıtımı**: Vercel, Netlify, Railway, Heroku vs.

---

## ✍️ Sonraki Adımlar

1. PostgreSQL kur ve Webhook test et
2. [Optional] Supabase kullanıyorsan Real-time enable et
3. n8n Workflow'unu kur
4. Real-time updates ekle (WebSocket)
5. Agent cevap gönderme özelliği ekle

**Sorularınız var mı? Webhook test ederken hata alsan bana yaz!** 🚀
