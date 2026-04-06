import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db';
import { ApiResponse } from '@/lib/types';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse<ApiResponse<unknown>>> {
  try {
    const { id } = await params;

    const messages = await prisma.message.findMany({
      where: { conversation_id: id },
      orderBy: { timestamp: 'asc' },
    });

    return NextResponse.json(
      {
        success: true,
        data: messages,
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Messages error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Internal server error',
      },
      { status: 500 }
    );
  }
}
