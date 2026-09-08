/**
 * HealthConnect AI - useChat Hook Tests
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useChat } from '@/hooks/useChat';
import { chatApi } from '@/lib/api';
import { WebSocketClient } from '@/lib/websocket';

// Mock API
jest.mock('@/lib/api', () => ({
  chatApi: {
    sendMessage: jest.fn(),
    getConversations: jest.fn(),
    getConversation: jest.fn(),
    deleteConversation: jest.fn(),
  },
}));

// Mock WebSocket
jest.mock('@/lib/websocket', () => ({
  WebSocketClient: jest.fn().mockImplementation(() => ({
    connect: jest.fn(),
    disconnect: jest.fn(),
    send: jest.fn(),
    sendChatMessage: jest.fn(),
    getStatus: jest.fn(() => 'connected'),
    isConnected: jest.fn(() => true),
  })),
}));

// Mock stores
jest.mock('@/stores/chat-store', () => ({
  useChatStore: jest.fn(() => ({
    conversations: [],
    activeConversationId: null,
    messages: {},
    isStreaming: false,
    setActiveConversation: jest.fn(),
    addConversation: jest.fn(),
    updateConversation: jest.fn(),
    removeConversation: jest.fn(),
    addMessage: jest.fn(),
    addMessages: jest.fn(),
    clearMessages: jest.fn(),
    setStreaming: jest.fn(),
    setTypingIndicator: jest.fn(),
  })),
}));

describe('useChat', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('initializes with empty state', () => {
    const { result } = renderHook(() => useChat());

    expect(result.current.messages).toEqual([]);
    expect(result.current.isSending).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('sends a message successfully', async () => {
    const mockResponse = {
      message_id: 'msg-1',
      conversation_id: 'conv-1',
      message: 'Response text',
      intent: 'appointment_booking',
      intent_confidence: 0.9,
      safety_category: 'safe',
      requires_human: false,
      citations: [],
      timestamp: '2024-01-15T10:00:00Z',
    };

    (chatApi.sendMessage as jest.Mock).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage('Test message');
    });

    expect(chatApi.sendMessage).toHaveBeenCalledWith({
      message: 'Test message',
      conversation_id: undefined,
    });
  });

  it('handles send message error', async () => {
    (chatApi.sendMessage as jest.Mock).mockRejectedValue(
      new Error('Network error'),
    );

    const { result } = renderHook(() => useChat());

    await act(async () => {
      try {
        await result.current.sendMessage('Test message');
      } catch {
        // Expected error
      }
    });

    expect(result.current.error).toBe('Network error');
  });

  it('loads conversations', async () => {
    const mockConversations = [
      {
        id: 'conv-1',
        conversation_code: 'CONV-1',
        title: 'Test conversation',
        preview: 'Preview text',
        status: 'active',
        started_at: '2024-01-15T10:00:00Z',
        updatedAt: '2024-01-15T10:05:00Z',
        messageCount: 2,
        messages: [],
      },
    ];

    (chatApi.getConversations as jest.Mock).mockResolvedValue(mockConversations);

    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.loadConversations();
    });

    expect(chatApi.getConversations).toHaveBeenCalled();
  });

  it('clears error', () => {
    const { result } = renderHook(() => useChat());

    act(() => {
      result.current.clearError();
    });

    expect(result.current.error).toBeNull();
  });
});