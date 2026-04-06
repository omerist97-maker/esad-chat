# 🔌 WebSocket (Socket.IO) Integration - Setup Guide

## ✅ Tamamlanan Adımlar

### 1. **Server-Side Setup** ✓
- ✅ `server.ts` - Custom Next.js + Socket.IO HTTP server
- ✅ `lib/socket-server.ts` - Socket.IO event handlers & broadcast functions
- ✅ `app/api/socket/route.ts` - Socket upgrade endpoint
- ✅ `lib/socket.ts` - Client Socket.IO instance (singleton)

### 2. **Client-Side Setup** ✓
- ✅ `lib/hooks/useSocket.ts` - Custom hook for socket connection
- ✅ `lib/context/ConversationContext.tsx` - Full WebSocket integration
  - Listen to `message:new` events
  - Listen to `conversation:update` events
  - Emit `message:send` to server
  - Room join/leave: `rooms:join`, `rooms:leave`

### 3. **Components Updated** ✓
- ✅ `ChatWindow.tsx` - Optimistic messaging, auto-scroll
- ✅ `ChatList.tsx` - Real-time conversation updates
- ✅ `dashboard/layout.tsx` - Wrapped with ConversationProvider

### 4. **Package Configuration** ✓
- ✅ `package.json` - Added ts-node, socket.io, socket.io-client
- ✅ Scripts updated: `"dev": "node --require ts-node/register server.ts"`
- ✅ `.env.local` - Socket URL configured

### 5. **Webhook Integration** ✓
- ✅ `app/api/webhook/n8n/route.ts` - Broadcasts n8n messages via WebSocket

---

## 🚀 Kurulum & Çalıştırma (Step-by-Step)

### Adım 1: Dependencies Yükle
```bash
cd c:\Users\omerz\Deneme\esad-chat

# npm install çalıştır
npm install
```

**Beklenir:** Başarı çıkışı ile installed packages:
```
added XXX packages in XXXs
```

**Eğer hata alırsan:**
```bash
# Option 1: npm cache temizle
npm cache clean --force
npm install

# Option 2: Slower install
npm install --prefer-offline

# Option 3: ts-node manuel ekle
npm install --save-dev ts-node
```

---

### Adım 2: PostgreSQL Setup

#### A. PostgreSQL Yüklü mü?
```bash
psql --version
```

Değilse: https://www.postgresql.org/download/windows/

#### B. Database Yönetici Aç
```bash
# psql client'ını aç
psql -U postgres

# Parola sor (installation password)
```

#### C. Database Oluştur
```sql
-- PostgreSQL terminal'de:
CREATE DATABASE esad_chat_db;
CREATE USER esad_user WITH PASSWORD 'your_secure_password';
ALTER ROLE esad_user SET client_encoding TO 'utf8';
ALTER ROLE esad_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE esad_user SET default_transaction_deferrable TO on;
ALTER ROLE esad_user SET default_transaction_read_only TO off;
GRANT ALL PRIVILEGES ON DATABASE esad_chat_db TO esad_user;
\q
```

---

### Adım 3: .env.local Ayarla
**Dosya:** `c:\Users\omerz\Deneme\esad-chat\.env.local`

```env
# Database (PostgreSQL bağlantı stringi)
DATABASE_URL="postgresql://esad_user:your_secure_password@localhost:5432/esad_chat_db"

# Ortam
NODE_ENV="development"

# Socket.IO (development)
NEXT_PUBLIC_SOCKET_URL="http://localhost:3000"
NEXT_PUBLIC_APP_URL="http://localhost:3000"

# Production (aşağıdaki template'i daha sonra kullan)
# DATABASE_URL="postgresql://user:pass@prod.db.host:5432/esad_chat_db"
# NEXT_PUBLIC_SOCKET_URL="https://yourdomain.com"
```

**Kritik:**
- `localhost:5432` = PostgreSQL default port
- `esad_chat_db` = database adı (yukarıda oluşturduğun)
- `esad_user` = database user (yukarıda oluşturduğun)

---

### Adım 4: Prisma Migrations
```bash
# Prisma client oluştur
npx prisma generate

# Database schema'sını push et
npx prisma db push

# Mock data yükle (5 müşteri, 100+ mesaj)
npm run db:seed
```

**Beklenir:**
```
✓ Generated Prisma Client
✓ Prisma schema loaded
✓ Database connection established
✓ Migrations applied
```

---

### Adım 5: Dev Server Başlat
```bash
npm run dev
```

**Beklenir:**
```
╔════════════════════════════════════════╗
║  🚀 Esad Chat Server Started           ║
║  📍 URL: http://localhost:3000         ║
║  🔌 WebSocket: ws://localhost:3000     ║
║  🌍 Node: development                  ║
╚════════════════════════════════════════╝
```

---

### Adım 6: Dashboard'ı Aç
Browser'da aç:
```
http://localhost:3000/dashboard
```

**Görmen gerekenler:**
- ✅ Sol panel: 5 müşteri listesi
- ✅ Ortada: "Bir sohbet seçin" mesajı
- ✅ Sağda: "Müşteri detaylarını görüntülemek için bir sohbet seçin"

---

### Adım 7: WebSocket Test
**Terminal 2'de (aynı klasörde):**
```bash
# Webhook test et
curl -X POST http://localhost:3000/api/webhook/n8n \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "WebSocket Test Müşteri",
    "customer_email": "test@example.com",
    "customer_phone": "+90 555 123 4567",
    "message": "Bu mesaj WebSocket üzerinden broadcast edilmeli!",
    "sender": "customer"
  }'
```

**Beklenir - Terminal'de:**
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

**Beklenir - Dashboard'da:**
- ✅ Yeni müşteri anında ChatList'te görünmeli
- ✅ Mesaj anında ChatWindow'da görünmeli (refresh yok!)
- ✅ Last message time güncellenmeli

---

## 🔄 WebSocket Events Reference

### Client → Server (Emit)

```typescript
// Konuşmaya katıl
socket.emit('rooms:join', conversationId)

// Konuşmadan ayrıl
socket.emit('rooms:leave', conversationId)

// Mesaj gönder (agent reply)
socket.emit('message:send', {
  conversationId: string
  content: string
})
```

### Server → Client (Listen)

```typescript
// Yeni mesaj (n8n webhook veya agent reply)
socket.on('message:new', (message: Message) => {
  // ChatWindow'a mesaj ekle
})

// Konuşma güncellendi (yeni last_message_at, vb.)
socket.on('conversation:update', (conversation: Conversation) => {
  // ChatList'i güncelle
})

// Bağlantı confirmed
socket.on('connection:confirmed', () => {
  console.log('Socket connected & ready')
})

// Hata
socket.on('error', (error: string) => {
  console.error('Socket error:', error)
})
```

---

## 🧪 Manual Testing (2 Browser Tabs)

### Tab 1: Dashboard (open & keep open)
```
http://localhost:3000/dashboard
```

### Tab 2: Webhook Test
```bash
# Her 2 saniyede 1 tane mesaj gönder
for i in {1..5}; do
  curl -X POST http://localhost:3000/api/webhook/n8n \
    -H "Content-Type: application/json" \
    -d "{
      \"customer_name\": \"Müşteri $i\",
      \"customer_email\": \"test$i@example.com\",
      \"message\": \"Test mesaj #$i\"
    }"
  sleep 2
done
```

**Beklenir:**
- Tab 1'de mesajlar REAL-TIME görünmeli
- Refresh gerekmemeli
- ChatList order'ı güncellenmeli (en yeni en üstte)

---

## 📊 Architecture Summary

```
Browser (Client) ←→ WebSocket ←→ Custom Server (Node.js)
                      ↓
                  Socket.IO Handler
                      ↓
                  PostgreSQL
                      ↓
                  Prisma ORM
```

**Data Flow (Webhook):**
```
n8n POST /api/webhook/n8n
   ↓
Create/Find Customer
   ↓
Create/Find Conversation
   ↓
Create Message
   ↓
Socket.IO Broadcast (to all clients)
   ↓
Browser: ConversationContext UPDATE
   ↓
UI: ChatList & ChatWindow refresh ✨
```

---

## 🔍 Debugging

### WebSocket Bağlı mı?
Browser DevTools → Network tab:
- WebSocket connection görmelisin (`ws://localhost:3000/socket.io/`)
- Status: `101 Switching Protocols` OK

### Console'da test:
```javascript
// Browser console'da:
fetch('/api/socket.io/')
  .then(r => r.text())
  .then(console.log)

// Beklenir: WebSocket endpoint status mesajı
```

### Socket.IO errors:
```bash
# Terminal log'ları:
NODE_ENV=development npm run dev 2>&1 | grep -i socket
```

---

## ⚠️ Common Issues & Fixes

| Issue | Çözüm |
|-------|-------|
| **"Module not found: ts-node"** | `npm install --save-dev ts-node` |
| **"Error: connect ECONNREFUSED"** | PostgreSQL çalışmıyor: `psql --version` kontrol et |
| **"WebSocket error: 429 Too Many Requests"** | Normal - Socket.IO fallback'e geçmiş |
| **"Cannot find module 'socket.io'"** | `rm -rf node_modules && npm install` |
| **"Port 3000 already in use"** | `PORT=3001 npm run dev` |
| **"Prisma error: relationship error"** | `npx prisma generate && npm run db:seed` |

---

## 🎯 Success Indicators

✅ **Setup başarılı ise:**
- [ ] `npm run dev` server başladı (banner çıkdı)
- [ ] Dashboard yüklendi (localhost:3000/dashboard)
- [ ] ChatList 5 müşteri gösteriyor
- [ ] Webhook curl request 200 döndü
- [ ] Mesaj anında ChatList & ChatWindow'da görünmyor (refresh yok)
- [ ] Browser DevTools Network tab'da WebSocket connection görünüyor

---

## 📝 Next Steps

### Immediate (Testing)
1. ✅ npm install çalıştır
2. ✅ PostgreSQL setup (create database)
3. ✅ .env.local düzenle (DATABASE_URL)
4. ✅ npm run dev başlat
5. ✅ Dashboard'ı aç ve test et

### Short-term (Features)
- [ ] Typing indicators ekle
- [ ] Online status ekle
- [ ] Message read receipts
- [ ] User avatar ekle

### Medium-term (Production)
- [ ] HTTPS + WSS (secure WebSocket)
- [ ] Redis adapter (multiple servers)
- [ ] Message persistence optimization
- [ ] Rate limiting

---

## 📞 Support

**Kurulum adımlarında sorun olursa:**
- PostgreSQL connection: `.env.local` kontrol et
- Socket.IO issues: Browser console DevTools bak
- npm errors: `npm cache clean --force` sonra `npm install`

**Webhook test sorunları:**
- cURL komutunu kopyala/yapıştır (terminalde çalıştır)
- Terminal 1: dev server running
- Terminal 2: webhook curl
- Terminal'de hiç hata yoksa: Dashboard yeniparla

---

**Başarılar! WebSocket ready! 🚀**
