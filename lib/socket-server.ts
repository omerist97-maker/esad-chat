import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import { NextApiRequest, NextApiResponse } from 'next';
import { prisma } from '@/lib/db';
import { Message, Conversation } from '@/lib/types';

// Socket.io instance (singleton)
let io: SocketIOServer | null = null;

/**
 * Initialize Socket.io server
 * Called once when the app starts
 */
export function initializeSocket(httpServer: any): SocketIOServer {
  if (!io) {
    io = new SocketIOServer(httpServer, {
      cors: {
        origin: process.env.NODE_ENV === 'production'
          ? process.env.NEXT_PUBLIC_APP_URL || 'https://yourdomain.com'
          : ['http://localhost:3000', 'http://localhost:3001'],
        methods: ['GET', 'POST'],
      },
      path: '/api/socket.io/',
      transports: ['websocket', 'polling'],
    });

    setupSocketHandlers(io);
  }

  return io;
}

/**
 * Get Socket.io instance
 */
export function getSocketIO(): SocketIOServer | null {
  return io;
}

/**
 * Setup Socket.io event handlers
 */
function setupSocketHandlers(io: SocketIOServer) {
  io.on('connection', (socket) => {
    console.log(`[Socket] Client connected: ${socket.id}`);

    // Send connection confirmation
    socket.emit('connection:confirmed');

    // Handle room join (conversation-specific updates)
    socket.on('rooms:join', (conversationId: string) => {
      socket.join(`conversation:${conversationId}`);
      console.log(`[Socket] Client ${socket.id} joined conversation:${conversationId}`);
    });

    // Handle room leave
    socket.on('rooms:leave', (conversationId: string) => {
      socket.leave(`conversation:${conversationId}`);
      console.log(`[Socket] Client ${socket.id} left conversation:${conversationId}`);
    });

    // Handle incoming message from client (agent reply)
    socket.on('message:send', async (data: { conversationId: string; content: string }) => {
      try {
        const { conversationId, content } = data;

        // Validate
        if (!conversationId || !content.trim()) {
          socket.emit('error', 'Invalid message data');
          return;
        }

        // Save to database
        const message = await prisma.message.create({
          data: {
            conversation_id: conversationId,
            sender_type: 'agent',
            content: content.trim(),
            timestamp: new Date(),
          },
        });

        // Get full conversation to broadcast
        const conversation = await prisma.conversation.findUnique({
          where: { id: conversationId },
          include: {
            customer: true,
            messages: {
              orderBy: { timestamp: 'desc' },
              take: 1,
            },
          },
        });

        // Update customer's last_message_at
        if (conversation?.customer_id) {
          await prisma.customer.update({
            where: { id: conversation.customer_id },
            data: { last_message_at: new Date() },
          });
        }

        // Broadcast new message to all clients in the conversation room
        io?.to(`conversation:${conversationId}`).emit('message:new', message);

        // Broadcast conversation update to all clients (for conversation list)
        if (conversation) {
          io?.emit('conversation:update', conversation);
        }

        console.log(`[Socket] Message saved: ${message.id}`);
      } catch (error) {
        console.error('[Socket] Error sending message:', error);
        socket.emit('error', 'Failed to send message');
      }
    });

    // Handle disconnect
    socket.on('disconnect', () => {
      console.log(`[Socket] Client disconnected: ${socket.id}`);
      // Cleanup if needed
    });

    // Handle errors
    socket.on('error', (error) => {
      console.error(`[Socket] Client error: ${socket.id}`, error);
    });
  });
}

/**
 * Broadcast message to all connected clients
 * Used when WebHook receives message from n8n
 */
export async function broadcastNewMessage(message: Message) {
  if (!io) return;

  io.to(`conversation:${message.conversation_id}`).emit('message:new', message);

  // Also update conversation list
  const conversation = await prisma.conversation.findUnique({
    where: { id: message.conversation_id },
    include: {
      customer: true,
      messages: {
        orderBy: { timestamp: 'desc' },
        take: 1,
      },
    },
  });

  if (conversation) {
    io.emit('conversation:update', conversation);
  }
}

/**
 * Broadcast conversation update to all clients
 */
export function broadcastConversationUpdate(conversation: Conversation) {
  if (!io) return;
  io.emit('conversation:update', conversation);
}
