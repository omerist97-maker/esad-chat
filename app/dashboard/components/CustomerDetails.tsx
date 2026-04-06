'use client';

import { Mail, Phone, Calendar, UserCircle } from 'lucide-react';
import { Customer, Conversation } from '@/lib/types';
import { useEffect, useState } from 'react';

interface CustomerDetailsProps {
  customer?: Customer;
  conversationId?: string;
}

export default function CustomerDetails({
  customer,
  conversationId,
}: CustomerDetailsProps) {
  const [conversationCount, setConversationCount] = useState(0);

  useEffect(() => {
    // In practice, you'd fetch this from the conversations list
    // or pass it as a prop
    if (customer?.id) {
      // Count would be calculated client-side from parent component
    }
  }, [customer?.id]);

  if (!customer) {
    return (
      <div className="p-8 h-full flex items-center justify-center text-center">
        <div>
          <UserCircle className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500 text-sm">Müşteri detaylarını görmek için\nbir sohbet seçin</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col divide-y divide-slate-200">
      {/* Profile Header */}
      <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 flex-shrink-0">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-full bg-blue-500 text-white flex items-center justify-center text-xl font-bold flex-shrink-0">
            {customer.name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-xl font-bold text-slate-900">{customer.name}</h3>
            <p className="text-xs text-slate-500 mt-1">ID: {customer.id.slice(0, 12)}...</p>
          </div>
        </div>
      </div>

      {/* Details Section */}
      <div className="flex-1 overflow-y-auto p-6 space-y-5 bg-slate-50">
        {/* Contact Information */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
          <h4 className="font-semibold text-slate-900 mb-4 text-sm uppercase tracking-wide">
            İletişim Bilgileri
          </h4>

          <div className="space-y-4">
            {customer.email && (
              <div className="flex items-start gap-3">
                <Mail className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-slate-500 font-medium">E-POSTA</p>
                  <p className="text-sm text-slate-900 break-all mt-1">{customer.email}</p>
                </div>
              </div>
            )}

            {customer.phone && (
              <div className="flex items-start gap-3">
                <Phone className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="text-xs text-slate-500 font-medium">TELEFON</p>
                  <p className="text-sm text-slate-900 mt-1">{customer.phone}</p>
                </div>
              </div>
            )}

            {!customer.email && !customer.phone && (
              <p className="text-xs text-slate-500 italic">İletişim bilgisi yok</p>
            )}
          </div>
        </div>

        {/* Activity Information */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
          <h4 className="font-semibold text-slate-900 mb-4 text-sm uppercase tracking-wide">
            Aktivite
          </h4>

          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <Calendar className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-xs text-slate-500 font-medium">SON MESAJ</p>
                <p className="text-sm text-slate-900 mt-1">
                  {new Date(customer.last_message_at).toLocaleDateString('tr-TR')} {new Date(customer.last_message_at).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>

            <div className="border-t border-slate-100 pt-4">
              <p className="text-xs text-slate-500 font-medium">ÜYELİK TARİHİ</p>
              <p className="text-sm text-slate-900 mt-1">
                {new Date(customer.created_at).toLocaleDateString('tr-TR', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
          </div>
        </div>

        {/* CRM Notes */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
          <h4 className="font-semibold text-slate-900 mb-4 text-sm uppercase tracking-wide">Notlar</h4>
          <textarea
            className="w-full h-28 p-3 border border-slate-200 rounded-lg text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-slate-400"
            placeholder="CRM notları buraya yazın..."
          />
          <button className="mt-3 w-full px-4 py-2 bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-600 transition-colors">
            Kaydet
          </button>
        </div>
      </div>
    </div>
  );
}
