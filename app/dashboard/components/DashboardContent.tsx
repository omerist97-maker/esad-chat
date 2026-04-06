'use client';

import { useConversation } from '@/lib/context/ConversationContext';
import ChatList from './ChatList';
import ChatWindow from './ChatWindow';
import CustomerDetails from './CustomerDetails';

export default function DashboardContent() {
  const {
    selectedConversation,
    selectedCustomer,
    conversations,
    setSelectedConversation,
    setSelectedCustomer,
  } = useConversation();

  const totalConversations = conversations.filter(
    (c) => c.customer_id === selectedCustomer?.id
  ).length;

  return (
    <div className="flex h-full w-full bg-slate-50">
      {/* Sol Panel - ChatList */}
      <div className="w-96 border-r border-slate-200 bg-white flex flex-col">
        <div className="border-b border-slate-200 p-5 bg-gradient-to-r from-blue-50 to-white">
          <h1 className="text-2xl font-bold text-slate-900">Esad Chat</h1>
          <p className="text-sm text-slate-500 mt-1">Aktif Sohbetler ({conversations.length})</p>
        </div>
        <div className="flex-1 overflow-y-auto">
          <ChatList
            selectedConversationId={selectedConversation?.id}
            onSelectConversation={(conv) => {
              setSelectedConversation(conv);
              setSelectedCustomer(conv.customer || null);
            }}
          />
        </div>
      </div>

      {/* Orta Panel - ChatWindow */}
      <div className="flex-1 flex flex-col bg-white">
        <ChatWindow
          conversationId={selectedConversation?.id}
          customer={selectedCustomer || undefined}
        />
      </div>

      {/* Sağ Panel - CustomerDetails */}
      <div className="w-96 border-l border-slate-200 bg-gradient-to-b from-slate-50 to-white flex flex-col">
        <div className="border-b border-slate-200 p-5 bg-white">
          <h2 className="text-xl font-bold text-slate-900">Müşteri Detayları</h2>
          {selectedCustomer && (
            <p className="text-sm text-slate-500 mt-2">
              📊 {totalConversations} sohbet | {conversations.filter(c => c.customer_id === selectedCustomer.id && c.messages && c.messages.length > 0).reduce((sum, c) => sum + (c.messages?.length || 0), 0)} mesaj
            </p>
          )}
        </div>
        <div className="flex-1 overflow-y-auto">
          <CustomerDetails
            customer={selectedCustomer || undefined}
            conversationId={selectedConversation?.id}
          />
        </div>
      </div>
    </div>
  );
}
