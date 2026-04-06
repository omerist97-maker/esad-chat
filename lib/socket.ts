import { io, Socket } from 'socket.io-client';

let socketInstance: Socket | null = null;

/**
 * Get or create Socket.io instance (singleton pattern)
 * Ensures only one WebSocket connection exists
 */
export function getSocket(): Socket {
  if (!socketInstance) {
    socketInstance = io(process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:3000', {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
      transports: ['websocket', 'polling'], // Fallback to polling if WebSocket fails
      path: '/api/socket.io/',
    });
  }

  return socketInstance;
}

/**
 * Close and reset Socket.io connection
 */
export function closeSocket(): void {
  if (socketInstance) {
    socketInstance.disconnect();
    socketInstance = null;
  }
}

/**
 * Check if socket is connected
 */
export function isSocketConnected(): boolean {
  return socketInstance?.connected ?? false;
}
