// Database Models & API Types

export interface Customer {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  last_message_at: Date;
  created_at: Date;
}

export interface Conversation {
  id: string;
  customer_id: string;
  started_at: Date;
  updated_at: Date;
  customer?: Customer;
  messages?: Message[];
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_type: 'customer' | 'agent';
  content: string;
  timestamp: Date;
  _isOptimistic?: boolean; // Local UI-only optimistic message flag
}

// n8n Webhook Payload
export interface N8nWebhookPayload {
  customer_name: string;
  customer_email?: string;
  customer_phone?: string;
  message: string;
  sender?: 'customer' | 'agent';
  timestamp?: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// WebSocket / Socket.io Event Types
export interface SocketEvents {
  // Connection events
  connection: () => void;
  disconnect: (reason: string) => void;
  error: (error: string) => void;
  connect_error: (error: unknown) => void;

  // Client → Server events
  'rooms:join': (conversationId: string) => void;
  'rooms:leave': (conversationId: string) => void;
  'message:send': (data: { conversationId: string; content: string }) => void;

  // Server → Client events (broadcasts)
  'message:new': (message: Message) => void;
  'conversation:update': (conversation: Conversation) => void;
  'connection:confirmed': () => void;
}

// Message payload for sending
export interface MessageSendPayload {
  conversationId: string;
  content: string;
}

// Message response from server
export interface MessageResponse extends ApiResponse<Message> {}

