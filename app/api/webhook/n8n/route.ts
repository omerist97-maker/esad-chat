import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db';
import { N8nWebhookPayload, ApiResponse } from '@/lib/types';
import { broadcastNewMessage, broadcastConversationUpdate } from '@/lib/socket-server';

export async function POST(request: NextRequest): Promise<NextResponse<ApiResponse<unknown>>> {
  try {
    const payload: N8nWebhookPayload = await request.json();

    // Validate required fields
    if (!payload.customer_name || !payload.message) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields: customer_name, message' },
        { status: 400 }
      );
    }

    // Create or find customer
    let customer = await prisma.customer.findUnique({
      where: { email: payload.customer_email || '' },
    }).catch(() => null);

    if (!customer && payload.customer_email) {
      customer = await prisma.customer.create({
        data: {
          name: payload.customer_name,
          email: payload.customer_email,
          phone: payload.customer_phone,
        },
      });
    } else if (!customer) {
      customer = await prisma.customer.create({
        data: {
          name: payload.customer_name,
          phone: payload.customer_phone,
        },
      });
    }

    // Find or create conversation
    const conversations = await prisma.conversation.findMany({
      where: { customer_id: customer.id },
      orderBy: { updated_at: 'desc' },
      take: 1,
    });

    let conversation = conversations[0];
    if (!conversation) {
      conversation = await prisma.conversation.create({
        data: {
          customer_id: customer.id,
        },
      });
    }

    // Create message
    const message = await prisma.message.create({
      data: {
        conversation_id: conversation.id,
        sender_type: payload.sender || 'customer',
        content: payload.message,
        timestamp: payload.timestamp ? new Date(payload.timestamp) : new Date(),
      },
    });

    // Update customer's last_message_at
    await prisma.customer.update({
      where: { id: customer.id },
      data: { last_message_at: new Date() },
    });

    // Broadcast to WebSocket clients (if server is running with custom server.ts)
    try {
      await broadcastNewMessage(message);

      // Get updated conversation for broadcast
      const updatedConversation = await prisma.conversation.findUnique({
        where: { id: conversation.id },
        include: {
          customer: true,
          messages: {
            orderBy: { timestamp: 'desc' },
            take: 1,
          },
        },
      });

      if (updatedConversation) {
        await broadcastConversationUpdate(updatedConversation);
      }
    } catch (socketError) {
      // WebSocket might not be available in polling-only mode
      console.warn('WebSocket broadcast not available:', socketError);
    }

    return NextResponse.json(
      {
        success: true,
        data: {
          customer_id: customer.id,
          conversation_id: conversation.id,
          message_id: message.id,
        },
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Webhook error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Internal server error',
      },
      { status: 500 }
    );
  }
}

