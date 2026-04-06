'use client';

import { ReactNode } from 'react';
import { ConversationProvider } from '@/lib/context/ConversationContext';

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <ConversationProvider>
      <div className="h-screen flex bg-white overflow-hidden">
        {children}
      </div>
    </ConversationProvider>
  );
}
