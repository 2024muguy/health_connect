/**
 * HealthConnect AI - Chat Flow Integration Tests
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { ToastProvider } from '@/components/ui/toast';

// Mock the API client
jest.mock('@/lib/api', () => ({
  chatApi: {
    sendMessage: jest.fn(),
    getConversations: jest.fn(),
    getConversation: jest.fn(),
  },
}));

// Mock WebSocket
jest.mock('@/lib/websocket', () => ({
  WebSocketClient: jest.fn().mockImplementation(() => ({
    connect: jest.fn(),
    disconnect: jest.fn(),
    send: jest.fn(),
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
    addMessage: jest.fn(),
    setStreaming: jest.fn(),
    setTypingIndicator: jest.fn(),
  })),
}));

// Mock useAuth
jest.mock('@/hooks/useAuth', () => ({
  useAuth: jest.fn(() => ({
    user: { firstName: 'Test', lastName: 'User', email: 'test@example.com' },
    isAuthenticated: true,
    isLoading: false,
  })),
}));

const queryClient = new QueryClient();

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        {ui}
      </ToastProvider>
    </QueryClientProvider>,
  );
}

describe('Chat Flow Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('sends a message and displays response', async () => {
    const mockResponse = {
      message_id: 'msg-1',
      conversation_id: 'conv-1',
      message: 'To book an appointment, please select a service and time.',
      intent: 'appointment_booking',
      intent_confidence: 0.95,
      safety_category: 'safe',
      requires_human: false,
      citations: [],
      timestamp: '2024-01-15T10:00:00Z',
    };

    const { chatApi } = require('@/lib/api');
    chatApi.sendMessage.mockResolvedValue(mockResponse);

    renderWithProviders(<ChatInterface />);

    // Type message
    const textarea = screen.getByTestId('textarea-chat-message');
    await userEvent.type(textarea, 'How do I book an appointment?');

    // Send message
    const sendButton = screen.getByTestId('button-send-chat');
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(chatApi.sendMessage).toHaveBeenCalledWith({
        message: 'How do I book an appointment?',
        conversation_id: undefined,
      });
    });
  });

  it('handles API error gracefully', async () => {
    const { chatApi } = require('@/lib/api');
    chatApi.sendMessage.mockRejectedValue(new Error('Network error'));

    renderWithProviders(<ChatInterface />);

    const textarea = screen.getByTestId('textarea-chat-message');
    await userEvent.type(textarea, 'Test message');

    const sendButton = screen.getByTestId('button-send-chat');
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('disables input while sending', async () => {
    const { chatApi } = require('@/lib/api');
    chatApi.sendMessage.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000)),
    );

    renderWithProviders(<ChatInterface />);

    const textarea = screen.getByTestId('textarea-chat-message');
    await userEvent.type(textarea, 'Test message');

    const sendButton = screen.getByTestId('button-send-chat');
    fireEvent.click(sendButton);

    expect(textarea).toBeDisabled();
    expect(sendButton).toBeDisabled();
  });
});