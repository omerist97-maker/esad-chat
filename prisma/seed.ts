import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Clear existing data
  await prisma.message.deleteMany();
  await prisma.conversation.deleteMany();
  await prisma.customer.deleteMany();

  // Create 5 customers with detailed info
  const customers = await Promise.all([
    prisma.customer.create({
      data: {
        name: 'Ahmet Yılmaz',
        email: 'ahmet.yilmaz@example.com',
        phone: '+90 532 123 4567',
        last_message_at: new Date(Date.now() - 1000 * 60 * 5), // 5 min ago
      },
    }),
    prisma.customer.create({
      data: {
        name: 'Fatma Özdemir',
        email: 'fatma.ozdemir@example.com',
        phone: '+90 533 234 5678',
        last_message_at: new Date(Date.now() - 1000 * 60 * 15), // 15 min ago
      },
    }),
    prisma.customer.create({
      data: {
        name: 'İbrahim Kaya',
        email: 'ibrahim.kaya@example.com',
        phone: '+90 534 345 6789',
        last_message_at: new Date(Date.now() - 1000 * 60 * 45), // 45 min ago
      },
    }),
    prisma.customer.create({
      data: {
        name: 'Zeynep Aydın',
        email: 'zeynep.aydin@example.com',
        phone: '+90 535 456 7890',
        last_message_at: new Date(Date.now() - 1000 * 60 * 120), // 2 hours ago
      },
    }),
    prisma.customer.create({
      data: {
        name: 'Mehmet Demir',
        email: 'mehmet.demir@example.com',
        phone: '+90 536 567 8901',
        last_message_at: new Date(Date.now() - 1000 * 60 * 240), // 4 hours ago
      },
    }),
  ]);

  console.log(`Created ${customers.length} customers`);

  // Create conversations and messages for each customer
  let totalMessages = 0;

  for (const customer of customers) {
    // Create 3-5 conversations per customer
    const convCount = Math.floor(Math.random() * 3) + 3;

    for (let c = 0; c < convCount; c++) {
      const conversation = await prisma.conversation.create({
        data: {
          customer_id: customer.id,
          started_at: new Date(Date.now() - 1000 * 60 * 60 * (convCount - c)),
        },
      });

      // Create 20-30 messages per conversation
      const msgCount = Math.floor(Math.random() * 11) + 20;
      const messages = [];

      for (let m = 0; m < msgCount; m++) {
        const isCustomerMsg = m % 2 === 0;
        const timestamp = new Date(
          conversation.started_at.getTime() + 1000 * 60 * m
        );

        messages.push({
          conversation_id: conversation.id,
          sender_type: isCustomerMsg ? 'customer' : 'agent',
          content: isCustomerMsg
            ? generateCustomerMessage()
            : generateAgentMessage(),
          timestamp,
        });
      }

      await prisma.message.createMany({
        data: messages,
      });

      totalMessages += messages.length;
    }
  }

  console.log(`Created ${totalMessages} messages across conversations`);
  console.log('Seed completed successfully! ✅');
}

function generateCustomerMessage(): string {
  const messages = [
    'Merhaba, sipariş hakkında soru var.',
    'Ürün hala stokta mı?',
    'Kargo takibi yapabilir miyim?',
    'Fiyatta indirim var mı?',
    'Şirket hakkında daha fazla bilgi alabilir miyim?',
    'Ödemesi nasıl yapabilirim?',
    'Teslimat süresi ne kadar?',
    'Ürün garantili mi?',
    'Renkli modeller var mı?',
    'Diğer şehirlere kargo gönderiyor musunuz?',
    'Müşteri hizmetleri 7/24 mi?',
  ];
  return messages[Math.floor(Math.random() * messages.length)];
}

function generateAgentMessage(): string {
  const messages = [
    'Merhaba! Size nasıl yardımcı olabilirim?',
    'Evet, hepimizde stok var. Kargo ücreti 50 TL.',
    'Kargo numarası: KRGO123456789 ile takip edebilirsiniz.',
    'Bu ay %20 indirim var, tüm ürünlere geçerli!',
    'Şirketimiz 15 yıldır sektörde faaliyet göstermektedir.',
    'Kredi kartı, banka transferi ve kapıda ödeme kabul ediyoruz.',
    'Standard kargo 2-3 iş günü, hızlı kargo 24 saat.',
    'Tüm ürünlerimiz 2 yıl garantili, üretim hatası için değişime sahibiz.',
    'Evet, mavi, kırmızı ve siyah renklerde mevcuttur.',
    'Evet, tüm Türkiye\'ye kargo göndeririz.',
    'Evet, saat 08:00-22:00 arasında hizmet veriyoruz.',
  ];
  return messages[Math.floor(Math.random() * messages.length)];
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (e) => {
    console.error(e);
    await prisma.$disconnect();
    process.exit(1);
  });
