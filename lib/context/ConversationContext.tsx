'use client';

import React, { ReactNode, createContext, useContext, useState, useCallback, useEffect } from 'react';
import { Socket } from 'socket.io-client';
import { Customer, Conversation, Message } from '@/lib/types';
import { useSocket } from '@/lib/hooks/useSocket';

interface ConversationContextType {
  // State
  conversations: Conversation[];
  selectedConversation: Conversation | null;
  selectedCustomer: Customer | null;
  messages: Message[];
  isLoading: boolean;
  socket: Socket | null;

  // Actions
  setSelectedConversation: (conv: Conversation) => void;
  setSelectedCustomer: (cust: Customer) => void;
  addMessage: (msg: Message) => void;
  updateConversation: (conv: Conversation) => void;
  sendMessage: (content: string) => Promise<void>;
  updateMessages: (msgs: Message[]) => void;
  updateConversations: (convs: Conversation[]) => void;
}

const ConversationContext = createContext<ConversationContextType | undefined>(undefined);

export const ConversationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { socket, isConnected } = useSocket();

  // Main state
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch initial conversations on mount
  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const res = await fetch('/api/conversations');
        const result = await res.json();
        if (result.success && result.data) {
          setConversations(result.data);
        }
      } catch (error) {
        console.error('Failed to fetch conversations:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchConversations();
  }, []);

  // Fetch messages when conversation selected
  useEffect(() => {
    if (!selectedConversation?.id) {
      setMessages([]);
      return;
    }

    const fetchMessages = async () => {
      try {
        const res = await fetch(`/api/conversations/${selectedConversation.id}/messages`);
        const result = await res.json();
        if (result.success && result.data) {
          setMessages(result.data);
        }
      } catch (error) {
        console.error('Failed to fetch messages:', error);
      }
    };

    fetchMessages();
  }, [selectedConversation?.id]);

  // Listen to WebSocket events
  useEffect(() => {
    if (!socket) return;

    // Handle new messages
    const handleNewMessage = (message: Message) => {
      setMessages((prev) => {
        // Avoid duplicates
        if (prev.find((m) => m.id === message.id)) {
          return prev;
        }
        return [...prev, message];
      });

      // Update conversation's last message
      if (message.conversation_id === selectedConversation?.id) {
        setConversations((prev) =>
          prev.map((c) =>
            c.id === message.conversation_id
              ? { ...c, updated_at: new Date(), messages: [message] }
              : c
          )
        );
      }
    };

    // Handle conversation updates
    const handleConversationUpdate = (updatedConv: Conversation) => {
      setConversations((prev) =>
        prev.map((c) => (c.id === updatedConv.id ? updatedConv : c))
      );

      // Update selected conversation if it's the one being updated
      if (selectedConversation?.id === updatedConv.id) {
        setSelectedConversation(updatedConv);
      }
    };

    socket.on('message:new', handleNewMessage);
    socket.on('conversation:update', handleConversationUpdate);

    return () => {
      socket.off('message:new', handleNewMessage);
      socket.off('conversation:update', handleConversationUpdate);
    };
  }, [socket, selectedConversation?.id]);

  // Join room when conversation selected
  useEffect(() => {
    if (!socket || !isConnected || !selectedConversation?.id) return;

    socket.emit('rooms:join', selectedConversation.id);

    return () => {
      if (selectedConversation?.id) {
        socket.emit('rooms:leave', selectedConversation.id);
      }
    };
  }, [socket, isConnected, selectedConversation?.id]);

  // Action: Update selected conversation
  const handleSetSelectedConversation = useCallback((conv: Conversation) => {
    setSelectedConversation(conv);
    setSelectedCustomer(conv.customer || null);
  }, []);

  // Action: Add message
  const handleAddMessage = useCallback((msg: Message) => {
    setMessages((prev) => {
      if (prev.find((m) => m.id === msg.id)) {
        return prev;
      }
      return [...prev, msg];
    });
  }, []);

  // Action: Update conversation
  const handleUpdateConversation = useCallback((conv: Conversation) => {
    setConversations((prev) =>
      prev.map((c) => (c.id === conv.id ? conv : c))
    );
  }, []);

  // Action: Send message
  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!selectedConversation?.id || !socket) {
        throw new Error('No conversation selected or socket not connected');
      }

      // Create optimistic message
      const optimisticMessage: Message = {
        id: `optimistic-${Date.now()}`,
        conversation_id: selectedConversation.id,
        sender_type: 'agent',
        content,
        timestamp: new Date(),
        _isOptimistic: true,
      };

      // Add optimistic message to UI
      setMessages((prev) => [...prev, optimisticMessage]);

      // Emit to server
      socket.emit('message:send', {
        conversationId: selectedConversation.id,
        content,
      });

      // Server will broadcast message:new with real ID
      // which will replace the optimistic one
    },
    [selectedConversation?.id, socket]
  );

  // Action: Update messages directly (from API)
  const handleUpdateMessages = useCallback((msgs: Message[]) => {
    setMessages(msgs);
  }, []);

  // Action: Update conversations directly (from API)
  const handleUpdateConversations = useCallback((convs: Conversation[]) => {
    setConversations(convs);
  }, []);

  const value: ConversationContextType = {
    conversations,
    selectedConversation,
    selectedCustomer,
    messages,
    isLoading,
    socket,

    setSelectedConversation: handleSetSelectedConversation,
    setSelectedCustomer,
    addMessage: handleAddMessage,
    updateConversation: handleUpdateConversation,
    sendMessage: handleSendMessage,
    updateMessages: handleUpdateMessages,
    updateConversations: handleUpdateConversations,
  };

  return (
    <ConversationContext.Provider value={value}>
      {children}
    </ConversationContext.Provider>
  );
};

/**
 * Hook to use ConversationContext
 * Must be called within ConversationProvider
 */
export function useConversation(): ConversationContextType {
  const context = useContext(ConversationContext);
  if (context === undefined) {
    throw new Error(
      'useConversation must be used within a ConversationProvider'
    );
  }
  return context;
}
