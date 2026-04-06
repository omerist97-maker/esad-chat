'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Dashboard'a yönlendir
    router.push('/dashboard');
  }, [router]);

  return (
    <div className="flex items-center justify-center h-screen">
      <p className="text-slate-500">Dashboard'a yönlendiriliyor...</p>
    </div>
  );
}
