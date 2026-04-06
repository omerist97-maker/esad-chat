'use client';

import { useEffect, useRef, useState } from 'react';
import { Send, Loader, MessageCircle } from 'lucide-react';
import { Message, Customer } from '@/lib/types';
import { useConversation } from '@/lib/context/ConversationContext';

interface ChatWindowProps {
  conversationId?: string;
  customer?: Customer;
}

export default function ChatWindow({ conversationId, customer }: ChatWindowProps) {
  const { messages, sendMessage } = useConversation();
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || !conversationId || isSending) return;

    setIsSending(true);
    try {
      await sendMessage(inputValue);
      setInputValue('');
    } catch (error) {
      console.error('Failed to send message:', error);
      // Error handling - message stays in input
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-slate-200 p-6 bg-gradient-to-r from-white via-white to-blue-50 flex-shrink-0">
        <h2 className="text-2xl font-bold text-slate-900">{customer?.name || 'Sohbet'}</h2>
        <div className="flex gap-4 mt-2 text-sm text-slate-600">
          {customer?.email && (
            <span className="flex items-center gap-2">
              📧 {customer.email}
            </span>
          )}
          {customer?.phone && (
            <span className="flex items-center gap-2">
              📱 {customer.phone}
            </span>
          )}
        </div>
      </div>

      {!conversationId ? (
        <div className="flex-1 flex items-center justify-center bg-slate-50">
          <div className="text-center">
            <MessageCircle className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500 text-lg">Bir sohbet seçin</p>
            <p className="text-slate-400 text-sm mt-2">Sol panelden bir müşteri seçerek başlayın</p>
          </div>
        </div>
      ) : (
        <>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 bg-slate-50 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-slate-500 text-sm py-12">
                <MessageCircle className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                Henüz mesaj yok
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.sender_type === 'customer' ? 'justify-start' : 'justify-end'}`}
                >
                  <div
                    className={`max-w-sm px-5 py-3 rounded-lg shadow-sm ${
                      msg.sender_type === 'customer'
                        ? 'bg-white text-slate-900 border border-slate-200'
                        : 'bg-blue-500 text-white'
                    }`}
                  >
                    <p className="text-sm break-words leading-relaxed">{msg.content}</p>
                    <p
                      className={`text-xs mt-2 ${
                        msg.sender_type === 'customer'
                          ? 'text-slate-400'
                          : 'text-blue-100'
                      }`}
                    >
                      {new Date(msg.timestamp).toLocaleTimeString('tr-TR', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                      {msg._isOptimistic && ' • Gönderiliyor...'}
                    </p>
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-slate-200 p-6 bg-white flex-shrink-0">
            <form onSubmit={handleSendMessage} className="flex gap-3">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Yanıtınızı yazın..."
                disabled={isSending}
                className="flex-1 px-4 py-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:bg-slate-50 text-sm"
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || isSending}
                className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 font-medium"
              >
                {isSending ? (
                  <Loader className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
                <span className="hidden sm:inline">Gönder</span>
              </button>
            </form>
          </div>
        </>
      )}
    </div>
  );
}

