# 🚀 HOSTINGER VPS'E DEPLOY - HIZLI REHBER

**Sub Domain:** chat.your-domain.com
**Hosting:** Hostinger VPS
**Setup Time:** ~30 dakika

---

## ⚡ STEP BY STEP

### STEP 1: Projeyi GitHub'a Push Et

```bash
cd c:\Users\omerz\Deneme\esad-chat

# Eğer git init'li değilse:
git init

# Tüm dosyaları ekle
git add .
git commit -m "Initial commit: Esad Chat Dashboard"

# GitHub'a push et
git remote add origin https://github.com/YOUR_USERNAME/esad-chat.git
git branch -M main
git push -u origin main
```

**Not:** https://github.com/new'da repo oluştur

---

### STEP 2: Hostinger Panel'de Sub Domain Oluştur

1. **Hostinger Control Panel** aç
2. **Addons** → **Subdomains**
3. **Create Subdomain:**
   - Name: `chat`
   - Root: `/public_html/chat` (otomatik olacak)
4. **Create** tıkla

```
✅ Sub domain oluşturuldu: chat.your-domain.com
```

---

### STEP 3: VPS'e SSH Bağlan

Hostinger'dan:
1. **VPS** → **Access**
2. SSH credentials'ı kopyala

Terminal/CMD aç:

```bash
ssh root@YOUR_VPS_IP
# Veya
ssh root@your-vps-ip.hostinger-vps.com
```

Password iste, gir.

✅ **VPS'ye bağlanmışsın!**

---

### STEP 4: Gerekli Paketleri Yükle

```bash
# Güncellemeleri yap
apt update && apt upgrade -y

# Git, Node.js, PostgreSQL kur
apt install -y git nodejs npm postgresql postgresql-contrib nginx curl

# Node version kontrol
node --version  # v20+ olmalı
npm --version   # v10+ olmalı
```

---

### STEP 5: PostgreSQL Database Kur

```bash
# PostgreSQL başlat
systemctl start postgresql
systemctl enable postgresql

# Database oluştur
sudo -u postgres createdb esad_chat_db

# Password ekle (isteğe bağlı)
sudo -u postgres psql
# ALTER USER postgres WITH PASSWORD 'strong_password';
# \q
```

---

### STEP 6: Projeyi Deploy Et

```bash
# /var/www klasörüne git
cd /var/www

# Repository clone et
git clone https://github.com/YOUR_USERNAME/esad-chat.git
cd esad-chat

# Dependencies yükle
npm install

# Prisma setup
npx prisma generate
npx prisma db push

# Mock data yükle
npm run db:seed

# Production build
npm run build
```

✅ **Build başarılı olmalı!**

---

### STEP 7: .env Production Dosyası Oluştur

```bash
nano .env.production
```

Ekle:

```env
DATABASE_URL="postgresql://postgres:password@localhost:5432/esad_chat_db"
NODE_ENV="production"
NEXT_PUBLIC_API_URL="https://chat.your-domain.com"
```

**Ctrl+X → Y → Enter** ile kaydet

---

### STEP 8: PM2 ile Server Başlat

```bash
# PM2 kur
npm install -g pm2

# Projeyi PM2'de start et
cd /var/www/esad-chat
pm2 start npm --name "esad-chat" -- start

# Startup'ta otomatik başlat
pm2 startup
pm2 save

# Status kontrol
pm2 status
```

✅ **Server çalışıyor!** (http://localhost:3000)

---

### STEP 9: Nginx Reverse Proxy Kur

```bash
# Eski site config'i sil (Hostinger default'ı)
rm /etc/nginx/sites-enabled/default

# Yeni config oluştur
nano /etc/nginx/sites-available/chat
```

Yapıştır:

```nginx
server {
    listen 80;
    server_name chat.your-domain.com;
    client_max_body_size 20M;

    # Redirect HTTP → HTTPS (sonra eklenecek)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';

        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

**Ctrl+X → Y → Enter**

---

### STEP 10: Nginx Aktifleştir

```bash
# Config aktifleştir
ln -s /etc/nginx/sites-available/chat /etc/nginx/sites-enabled/

# Test et
nginx -t
# Output: "test is successful" ✅

# Restart et
systemctl restart nginx
systemctl enable nginx
```

---

### STEP 11: Browser'da Test Et

```
http://chat.your-domain.com/dashboard
```

Açılıyor mu? ✅

Müşteriler ve mesajlar gözüküyor mu? ✅

---

### STEP 12: SSL Sertifikası (HTTPs)

```bash
# Certbot kur
apt install -y certbot python3-certbot-nginx

# SSL oluştur
certbot --nginx -d chat.your-domain.com
```

Sorularına cevap ver:
- Email: Senin email
- Terms: `y`
- Sharing: `n`
- Redirect HTTP → HTTPS: `2` (Evet)

✅ **SSL kuruldu! HTTPS aktif!**

---

## ✅ TEST LISTESI

- [ ] `https://chat.your-domain.com/dashboard` açılıyor
- [ ] Müşteri listesi gözüküyor (sol panel)
- [ ] Bir müşteriye tıkla → Mesajlar açılıyor (orta panel)
- [ ] Müşteri detayları gözüküyor (sağ panel)

---

## 🧪 WEBHOOK TEST

```bash
curl -X POST https://chat.your-domain.com/api/webhook/n8n \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test Müşteri",
    "customer_email": "test@example.com",
    "customer_phone": "+90 555 123 4567",
    "message": "Canlı deployment test mesajı",
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

## 📊 MONITORING

### Server Status
```bash
pm2 status
pm2 logs esad-chat
```

### PostgreSQL Status
```bash
sudo systemctl status postgresql
```

### Nginx Status
```bash
sudo systemctl status nginx
```

---

## 🔧 GÜNLÜK OPERASYONLAR

### Deploy'ı Güncelle (yeni kod push ettiysen)
```bash
cd /var/www/esad-chat
git pull origin main
npm install
npm run build
pm2 restart esad-chat
```

### Server Restart
```bash
systemctl reboot
# PM2 otomatik startup yapacak
```

### Logs Kontrol
```bash
pm2 logs esad-chat | tail -50
```

---

## 🚨 TROUBLESHOOTING

### "Connection refused" (3000)
```bash
pm2 logs esad-chat
# Hata mesajını oku ve düzelt

pm2 restart esad-chat
```

### "502 Bad Gateway"
```bash
# Nginx config test et
nginx -t

# PM2 restart et
pm2 restart esad-chat

# Nginx restart et
systemctl restart nginx
```

### "Database connection error"
```bash
# PostgreSQL çalışıyor mu?
sudo systemctl status postgresql

# Database var mı?
sudo -u postgres psql -l | grep esad_chat_db

# Yeniden kur
sudo -u postgres createdb esad_chat_db
```

### SSL Error
```bash
# Sertifikayı renew et
certbot renew --dry-run

# Force renew
certbot renew --force-renewal
```

---

## 📈 PERFORMANCE TIPS

### Cron Job ile Günlük Backup
```bash
# PM2 logları temizle (haftalık)
pm2 flush

# Backup script ekle (~/.backup.sh)
```

### Resource Monitoring
```bash
# PM2 ile memory/cpu monitoring
pm2 monit

# VPS resources
free -h  # Ram
df -h    # Disk
```

---

## 🔒 SECURITY

✅ Yapılandırma checklist:
- [ ] SSH key auth aktif (password login deaktif)
- [ ] Firewall aktif (UFW)
- [ ] Fail2ban kurulu (brute-force protection)
- [ ] Regular backups
- [ ] SSL çalışıyor (HTTPS)

---

## 📍 ÖZET

```
✅ GitHub'a push
✅ VPS'e SSH bağlantısı
✅ Node.js, npm, PostgreSQL kur
✅ Repository clone et
✅ npm install & build
✅ PM2 start
✅ Nginx reverse proxy
✅ SSL sertifikası
✅ Test et
✅ Live! 🎉
```

**Total Time:** 25-30 dakika

---

## 📞 SONRAKI ADIMLAR

1. ✅ Production'da çalışıyor
2. ⏭️ n8n Webhook'u konfigure et
3. ⏭️ Monitoring setup (PM2+, Uptime Robot, etc)
4. ⏭️ Regular backups otomatize et

---

**Hazır mısın? Başlayalım! 🚀**
