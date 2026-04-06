'use client';

import { useEffect, useState } from 'react';
import { Socket } from 'socket.io-client';
import { getSocket, closeSocket } from '@/lib/socket';

interface UseSocketReturn {
  socket: Socket | null;
  isConnected: boolean;
  isLoading: boolean;
  error: Error | null;
}

/**
 * Custom hook to manage Socket.io connection
 * Initializes connection on mount, cleans up on unmount
 * Handles reconnection and error states
 */
export function useSocket(): UseSocketReturn {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    try {
      const socketInstance = getSocket();

      // Handle connection events
      const handleConnect = () => {
        setIsConnected(true);
        setIsLoading(false);
        setError(null);
      };

      const handleDisconnect = (reason: string) => {
        setIsConnected(false);
        // Don't set error for normal disconnects
        if (reason !== 'io client namespace disconnect') {
          console.warn('WebSocket disconnected:', reason);
        }
      };

      const handleError = (errorData: unknown) => {
        const errorMessage =
          errorData instanceof Error ? errorData.message : String(errorData);
        setError(new Error(errorMessage));
        setIsLoading(false);
      };

      const handleConnectError = (errorData: unknown) => {
        const errorMessage =
          errorData instanceof Error ? errorData.message : String(errorData);
        console.error('Connection error:', errorMessage);
        setError(new Error(`Connection failed: ${errorMessage}`));
        // Don't set isLoading to false on connect error, will retry
      };

      // Attach event listeners
      socketInstance.on('connect', handleConnect);
      socketInstance.on('disconnect', handleDisconnect);
      socketInstance.on('error', handleError);
      socketInstance.on('connect_error', handleConnectError);

      // Set socket instance if already connected
      if (socketInstance.connected) {
        setIsConnected(true);
        setIsLoading(false);
      }

      setSocket(socketInstance);

      // Cleanup on unmount
      return () => {
        socketInstance.off('connect', handleConnect);
        socketInstance.off('disconnect', handleDisconnect);
        socketInstance.off('error', handleError);
        socketInstance.off('connect_error', handleConnectError);
        // Don't close the socket here - keep it alive for other hooks
      };
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      setIsLoading(false);
    }
  }, []);

  return { socket, isConnected, isLoading, error };
}

/**
 * Hook to safely disconnect Socket.io on component unmount
 * Typically used once at the app root level
 */
export function useSocketCleanup() {
  useEffect(() => {
    return () => {
      closeSocket();
    };
  }, []);
}
