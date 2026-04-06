import { Server as HTTPServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import { IncomingMessage } from 'http';
import { Socket } from 'net';

// Store the I/O instance globally to prevent multiple instances
let io: SocketIOServer | null = null;

// Socket.IO event handlers
function setupSocketHandlers(io: SocketIOServer) {
  io.on('connection', (socket) => {
    console.log(`[Socket] Client connected: ${socket.id}`);

    // Send connection confirmation
    socket.emit('connection:confirmed');

    // Handle room join
    socket.on('rooms:join', (conversationId: string) => {
      socket.join(`conversation:${conversationId}`);
      console.log(`[Socket] ${socket.id} joined conversation:${conversationId}`);
    });

    // Handle room leave
    socket.on('rooms:leave', (conversationId: string) => {
      socket.leave(`conversation:${conversationId}`);
      console.log(`[Socket] ${socket.id} left conversation:${conversationId}`);
    });

    // Event listeners will be handled by socket-server.ts broadcast functions
    socket.on('disconnect', () => {
      console.log(`[Socket] Client disconnected: ${socket.id}`);
    });
  });
}

// Next.js handler for WebSocket upgrade
export async function GET(
  req: Request,
  { params }: { params: Record<string, unknown> }
): Promise<Response> {
  // This is a fallback for HTTP long-polling
  return new Response('WebSocket endpoint - upgrade required', { status: 426 });
}

// Export the Socket.IO instance via custom handler
// Note: Next.js doesn't have native WebSocket support in the app directory yet
// You need to use a custom server (next.config.js) or external service

export const config = {
  api: {
    bodyParser: false,
  },
};

// Store socket instance globally for use in other API routes
export function getGlobalSocketIO(): SocketIOServer | null {
  return io;
}

export function setGlobalSocketIO(ioInstance: SocketIOServer): void {
  io = ioInstance;
}
