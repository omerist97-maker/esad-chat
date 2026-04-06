#!/bin/bash

# Esad Chat - Otomatik Kurulum Script
# Windows (Git Bash / WSL) veya Linux/Mac'te çalışır

set -e

PROJECT_DIR="c:/Users/omerz/Deneme/esad-chat"
cd "$PROJECT_DIR"

echo "🚀 Esad Chat Dashboard - Kurulum Başlıyor..."
echo "================================================"

# Step 1: Clean node_modules
echo "📦 Step 1: Eski bağımlılıkları temizleniyor..."
rm -rf node_modules package-lock.json
echo "✓ Temizleme tamamlandı"

# Step 2: Install dependencies
echo ""
echo "📥 Step 2: Dependencies yükleniyor..."
npm install
echo "✓ Dependencies yüklendi"

# Step 3: Prisma setup
echo ""
echo "🗄️  Step 3: Prisma yapılandırılıyor..."
npx prisma generate
echo "✓ Prisma client oluşturuldu"

# Step 4: Database migration
echo ""
echo "🔄 Step 4: Database migration çalıştırılıyor..."
echo ""
echo "⚠️  Önemli: .env.local dosyasında DATABASE_URL ayarlı mı?"
echo "   Örnek: postgresql://user:password@localhost:5432/esad_chat_db"
echo ""
read -p "   Devam etmek istiyor musun? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    npx prisma db push
    echo "✓ Database migration tamamlandı"
else
    echo "⚠️  Migration atlandı. Manual olarak çalıştır: npx prisma db push"
fi

# Step 5: Seed mock data
echo ""
echo "🌱 Step 5: Mock veri yükleniyor..."
npm run db:seed
echo "✓ Mock veri yüklendi (5 müşteri, 100+ mesaj)"

# Step 6: Build check
echo ""
echo "🔨 Step 6: TypeScript kontrol..."
npx tsc --noEmit
echo "✓ TypeScript kontrol başarılı"

echo ""
echo "================================================"
echo "✅ Kurulum Başarılı!"
echo ""
echo "📍 Dev sunucuyu başlat:"
echo "   npm run dev"
echo ""
echo "🌐 Dashboard açılacak:"
echo "   http://localhost:3000/dashboard"
echo ""
echo "📚 Daha fazla bilgi: SETUP.md dosyasını oku"
echo "================================================"
