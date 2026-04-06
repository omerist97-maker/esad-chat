# 🚀 ESAD CHAT PRODUCTION DEPLOYMENT REHBERI

**Tarih:** 2026-04-06
**Status:** Production'a Hazır
**Estimated Time:** 30 dakika

---

## 📋 PRE-DEPLOYMENT CHECKLIST

Başlamadan önce kontrol et:

- [ ] `.env.local` dosyası var ve doğru bilgiler içeriyor
- [ ] `npm run dev` çalışıyor (local test geçmiş)
- [ ] Database migration'ları başarılı (`npx prisma db push`)
- [ ] Mock veri yüklenmiş (`npm run db:seed`)
- [ ] Git repository'de commit yapmışsın

---

## 🎯 DEPLOYMENT SEÇENEKLERI

### Option 1: **VERCEL** (Recommended) ⭐
- En hızlı (Next.js için optimized)
- Free tier available
- Auto SSL, CDN, analytics
- Deploy: 2 dakika

### Option 2: **Railway**
- Kolay PostgreSQL integration
- Pay-as-you-go pricing
- Deploy: 5 dakika

### Option 3: **Heroku**
- Klasik seçenek
- Free tier artık yok ama ucuz
- Deploy: 10 dakika

### Option 4: **Self-Hosted (VPS)**
- Full kontrol
- Daha pahalı
- Deploy: 45 dakika

---

# 🌟 VERCEL'E DEPLOY (EN KOLAY)

## STEP 1: Projeyi GitHub'a Push Et

```bash
cd c:\Users\omerz\Deneme\esad-chat

# Git initialize et (eğer hali hazırda yoksa)
git init
git add .
git commit -m "Initial commit: Esad Chat Dashboard"

# GitHub'a push et
git remote add origin https://github.com/YOUR_USERNAME/esad-chat.git
git branch -M main
git push -u origin main
```

**Not:** GitHub'da `esad-chat` repo'sunu oluştur (https://github.com/new)

---

## STEP 2: Vercel'e Bağlan

1. **https://vercel.com/** aç
2. **"Sign Up"** → GitHub ile sign up yap
3. **"New Project"** butonuna tıkla
4. `esad-chat` repo'sunu seç
5. **"Import"** butonuna tıkla

---

## STEP 3: Environment Variables Ekle

Vercel dashboard'da:
1. **Settings** → **Environment Variables**
2. Aşağıdaki değişkenleri ekle:

```env
DATABASE_URL=postgresql://user:password@host:5432/esad_chat_db
NEXT_PUBLIC_API_URL=https://your-app.vercel.app
```

**DATABASE_URL nasıl bulunur?**

### Option A: PostgreSQL Vercel ile
1. Vercel Storage → **Create Database** → PostgreSQL
2. `.env.local` kopyala → Vercel'e yapıştır
3. **Done!** ✅

### Option B: External Database (Recommended)
PostgreSQL hosting hizmetlerinden birini seç:
- **Supabase** (PostgreSQL hosting)
- **Railway PostgreSQL**
- **AWS RDS**
- **Render**

**Supabase Örneği:**
1. https://supabase.com/ aç
2. **New Project** oluştur
3. Connection string kopyala → Vercel'e yapıştır

---

## STEP 4: Build Settings Kontrol

Vercel dashboard'da **Settings** → **Build & Development Settings**

Şu değerler otomatik yapılmış olmalı:
- **Framework Preset:** Next.js ✅
- **Build Command:** `next build` ✅
- **Output Directory:** `.next` ✅

---

## STEP 5: Deploy!

1. **"Deploy"** butonuna tıkla
2. Vercel kurulum yapacak (2 dakika)
3. Başarılı olursa URL görünecek:

```
✅ Production: https://esad-chat.vercel.app
```

---

## STEP 6: Production Database'i Migrate Et

Deploy başarılı olur olmaz:

```bash
# Production migrations'ı çalıştır
npx prisma db push --skip-generate

# Production seed'i çalıştır (opsiyonel)
npm run db:seed
```

---

## ✅ Testing

1. Browser'ı aç: **https://esad-chat.vercel.app/dashboard**
2. Müşterileri görüyor musun? ✅
3. Bir müşteriye tıkla → Mesajlar gözüküyor mu? ✅
4. Webhook test et (aşağıda)

---

---

# 🚂 RAILWAY'E DEPLOY (ALTERNATIVF)

## STEP 1-2: GitHub & Railway Connect

```bash
# GitHub'a push et (üstteki gibi)
git push origin main
```

1. https://railway.app/ aç
2. **GitHub ile sign up** yap
3. **New Project** → **Deploy from GitHub repo**
4. `esad-chat` seç

---

## STEP 3: PostgreSQL Ekle

Railway dashboard'da:
1. **Add Service** → **PostgreSQL**
2. Otomatik bağlanacak
3. **DATABASE_URL** otomatik eklenecek

---

## STEP 4: Variables Ekle

**Variables** section'da ekle:
```
NODE_ENV=production
```

---

## STEP 5: Deploy!

Push etersen otomatik deploy olur! 🎉

---

---

# 🔧 SELF-HOSTED VPS'E DEPLOY (İleri)

## STEP 1: VPS Kiraları

- **Hetzner** (€5/ay)
- **DigitalOcean** ($6/ay)
- **Linode** ($5/ay)
- **AWS Lightsail** ($5/ay)

---

## STEP 2: Server Kurulumu

SSH ile bağlan:
```bash
ssh root@your_server_ip
```

Güncellemeleri yap:
```bash
apt update && apt upgrade -y
```

---

## STEP 3: Node.js Kur

```bash
# Node.js kurulum script
curl -sL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs git postgresql postgresql-contrib
```

---

## STEP 4: PostgreSQL Kur & Başlat

```bash
systemctl start postgresql
systemctl enable postgresql

# Database oluştur
sudo -u postgres createdb esad_chat_db
```

---

## STEP 5: Projeyi Deploy Et

```bash
cd /var/www
git clone https://github.com/YOUR_USERNAME/esad-chat.git
cd esad-chat

npm install
npx prisma db push
npm run build
```

---

## STEP 6: PM2 ile Server Başlat

```bash
npm install -g pm2

pm2 start npm --name "esad-chat" -- start
pm2 startup
pm2 save
```

---

## STEP 7: Nginx Reverse Proxy Kur

```bash
apt install -y nginx

# /etc/nginx/sites-available/esad-chat dosyasını oluştur:
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Aktifleştir:
```bash
ln -s /etc/nginx/sites-available/esad-chat /etc/nginx/sites-enabled/
systemctl restart nginx
```

---

## STEP 8: SSL Sertifikası (Let's Encrypt)

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

---

---

# 🔗 N8N WEBHOOK INTEGRATION (CanlıYa)

## STEP 1: Webhook URL'ini Kaydet

Production URL'in:
```
https://your-app.vercel.app/api/webhook/n8n
```

---

## STEP 2: N8N Workflow Oluştur

N8N'de:
1. **New Workflow** oluştur
2. **Webhook trigger** ekle:
   - Method: POST
   - Path: `/customer-message`

3. **HTTP Request** node'u ekle:
```
Method: POST
URL: https://your-app.vercel.app/api/webhook/n8n

Body:
{
  "customer_name": "{{$json.name}}",
  "customer_email": "{{$json.email}}",
  "customer_phone": "{{$json.phone}}",
  "message": "{{$json.message}}",
  "sender": "customer"
}
```

4. **Save & Activate** tıkla

---

## STEP 3: Test Et

```bash
curl -X POST https://your-app.vercel.app/api/webhook/n8n \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test Kullanıcı",
    "customer_email": "test@example.com",
    "customer_phone": "+90 555 123 4567",
    "message": "Bu bir test mesajıdır!",
    "sender": "customer"
  }'
```

Expected Response:
```json
{
  "success": true,
  "data": {
    "customer_id": "...",
    "conversation_id": "...",
    "message_id": "..."
  }
}
```

---

---

# 📊 MONITORING & LOGGING

## Vercel Logs
```bash
vercel logs
```

## Railway Logs
Dashboard → **Logs** tab'ı

## Self-Hosted Logs
```bash
pm2 logs esad-chat
```

---

---

# 🔒 SECURITY CHECKLIST

- [ ] `.env.local` dosyası `.gitignore`'da var
- [ ] DATABASE_URL gizli (environment variables'ta)
- [ ] HTTPS aktif (SSL)
- [ ] CORS configured
- [ ] Rate limiting (opsiyonel)
- [ ] Input validation aktif
- [ ] Error messages production'da expose etmiyor

---

---

# 🎯 QUICK START SUMMARY

**İlk kez production'a almak için:**

1. ✅ **GitHub'a push et** (5 min)
2. ✅ **Vercel'de sign up** (2 min)
3. ✅ **Repository import et** (2 min)
4. ✅ **Database URL ekle** (5 min)
5. ✅ **Deploy tıkla** (2 min)
6. ✅ **https://your-app.vercel.app/dashboard aç** (1 min)

**Total: 17 dakika** ⏱️

---

---

# ❓ PRODUCTION AFTER DEPLOYMENT

### Daily Operations
- ✅ Logs kontrol et
- ✅ Analytics izle
- ✅ Errors kontrol et

### Weekly Tasks
- ✅ Performance metrics bak
- ✅ Database backup kodu çalıştır
- ✅ Security updates

### Monthly Tasks
- ✅ Cost review
- ✅ Capacity planning
- ✅ Feature updates deploy et

---

---

# 🚨 TROUBLESHOOTING

### "Build failed" hatası?
1. Local'de `npm run build` çalıştır
2. Hata çıkarsa düzelt
3. Git push et
4. Vercel re-trigger yapacak

### "Connection refused" (Database)?
1. DATABASE_URL'nin doğru olduğunu kontrol et
2. Database IP whitelist'i kontrol et
3. PostgreSQL'in çalıştığını kontrol et

### "500 Internal Server Error"?
1. Logs'a bak (`vercel logs`)
2. Environment variables kontrol et
3. Database connectivity kontrol et

---

---

# 📞 NEXT STEPS

1. **Hangi platform seçeceksin?** Vercel / Railway / VPS?
2. **Domain adın var mı?** (your-domain.com)
3. **Database hosting nereye?** (Supabase / Railway / AWS)

---

**Hazır mısın? 🚀**

En hızlı yol: **VERCEL** (15-20 dakika)
