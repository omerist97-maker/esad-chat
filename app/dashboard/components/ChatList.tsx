'use client';

import { MessageCircle, Calendar } from 'lucide-react';
import { Conversation } from '@/lib/types';
import { useConversation } from '@/lib/context/ConversationContext';

interface ChatListProps {
  selectedConversationId?: string;
  onSelectConversation: (conversation: Conversation) => void;
}

export default function ChatList({
  selectedConversationId,
  onSelectConversation,
}: ChatListProps) {
  const { conversations, isLoading } = useConversation();

  if (isLoading) {
    return (
      <div className="p-4">
        <div className="text-slate-500 text-sm">Yükleniyor...</div>
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className="p-4 text-center">
        <MessageCircle className="w-12 h-12 text-slate-300 mx-auto mb-2" />
        <p className="text-slate-500 text-sm">Henüz sohbet yok</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-slate-200">
      {conversations.length === 0 ? (
        <div className="p-8 text-center">
          <MessageCircle className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500 text-sm">Henüz sohbet yok</p>
        </div>
      ) : (
        conversations.map((conv) => {
          const customer = conv.customer!;
          const lastMessage = conv.messages?.[0];
          const isSelected = selectedConversationId === conv.id;

          return (
            <button
              key={conv.id}
              onClick={() => onSelectConversation(conv)}
              className={`w-full px-5 py-4 text-left hover:bg-slate-50 transition-colors flex flex-col gap-2 ${
                isSelected ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-slate-900 truncate text-base">
                    {customer.name}
                  </p>
                  <p className="text-xs text-slate-500 truncate mt-0.5">
                    {customer.phone || 'Telefon yok'}
                  </p>
                </div>
                {isSelected && (
                  <div className="w-2 h-2 mt-2 bg-blue-500 rounded-full flex-shrink-0" />
                )}
              </div>

              {lastMessage && (
                <p className="text-xs text-slate-600 truncate leading-relaxed">
                  <span className="font-medium">{lastMessage.sender_type === 'agent' ? 'Siz:' : 'Müşteri:'}</span> {lastMessage.content.substring(0, 45)}
                </p>
              )}

              <div className="flex items-center gap-1 text-xs text-slate-400">
                <Calendar className="w-3.5 h-3.5 flex-shrink-0" />
                <span>
                  {new Date(customer.last_message_at).toLocaleTimeString('tr-TR', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>
            </button>
          );
        })
      )}
    </div>
  );
}

