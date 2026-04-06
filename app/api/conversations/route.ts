import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db';
import { ApiResponse } from '@/lib/types';

export async function GET(request: NextRequest): Promise<NextResponse<ApiResponse<unknown>>> {
  try {
    const conversations = await prisma.conversation.findMany({
      include: {
        customer: true,
        messages: {
          orderBy: { timestamp: 'desc' },
          take: 1,
        },
      },
      orderBy: { updated_at: 'desc' },
    });

    return NextResponse.json(
      {
        success: true,
        data: conversations,
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Conversations error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Internal server error',
      },
      { status: 500 }
    );
  }
}
