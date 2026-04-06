'use client';

import React, { ReactNode } from 'react';
import { AlertCircle, Wifi, WifiOff } from 'lucide-react';
import { useSocket } from '@/lib/hooks/useSocket';

interface SocketErrorBoundaryProps {
  children: ReactNode;
}

export function SocketErrorBoundary({ children }: SocketErrorBoundaryProps) {
  const { isConnected, error, isLoading } = useSocket();

  // Show error banner if connection fails
  if (error && !isLoading) {
    return (
      <div className="flex flex-col h-full">
        {/* Error Banner */}
        <div className="bg-amber-50 border-b border-amber-200 p-4 flex gap-3 items-start">
          <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-amber-900">
              WebSocket Connection Error
            </p>
            <p className="text-xs text-amber-700 mt-1">
              {error.message || 'Unable to establish real-time connection'}
            </p>
            <p className="text-xs text-amber-600 mt-2">
              💡 Tip: Polling fallback is active. Real-time updates may be delayed.
            </p>
          </div>
        </div>

        {/* Children rendered below error */}
        <div className="flex-1 overflow-hidden">
          {children}
        </div>
      </div>
    );
  }

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full bg-slate-50">
        <div className="text-center">
          <div className="animate-spin mb-4 flex justify-center">
            <Wifi className="w-8 h-8 text-slate-400" />
          </div>
          <p className="text-slate-600 text-sm">Connecting to server...</p>
        </div>
      </div>
    );
  }

  // Show connection status indicator
  return (
    <div className="flex flex-col h-full relative">
      {/* Connection Status Indicator */}
      <div
        className={`absolute top-4 right-4 flex items-center gap-2 px-3 py-2 rounded-full text-xs font-medium z-40 ${
          isConnected
            ? 'bg-green-50 text-green-700'
            : 'bg-yellow-50 text-yellow-700'
        }`}
      >
        {isConnected ? (
          <>
            <Wifi className="w-3 h-3" />
            Connected
          </>
        ) : (
          <>
            <WifiOff className="w-3 h-3" />
            Reconnecting...
          </>
        )}
      </div>

      {/* Children */}
      {children}
    </div>
  );
}

/**
 * Simple wrapper for status display in Dashboard
 */
export function ConnectionStatus() {
  const { isConnected } = useSocket();

  return (
    <div className="flex items-center gap-2 px-3 py-1 rounded-full text-xs bg-slate-100">
      <span
        className={`w-2 h-2 rounded-full ${
          isConnected ? 'bg-green-500' : 'bg-yellow-500'
        }`}
      />
      <span className="text-slate-600">
        {isConnected ? 'Connected' : 'Reconnecting...'}
      </span>
    </div>
  );
}
