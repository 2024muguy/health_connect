/**
 * HealthConnect AI - ChatInterface Component Tests
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { useChat } from '@/hooks/useChat';

// Mock the useChat hook
jest.mock('@/hooks/useChat', () => ({
  useChat: jest.fn(),
}));

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Sparkles: () => <span data-testid="icon-sparkles" />,
  Send: () => <span data-testid="icon-send" />,
  MessageCircle: () => <span data-testid="icon-message" />,
  FileText: () => <span data-testid="icon-file" />,
  MoreVertical: () => <span data-testid="icon-more" />,
  Trash2: () => <span data-testid="icon-trash" />,
}));

describe('ChatInterface', () => {
  const mockSendMessage = jest.fn();
  const mockSetActiveConversation = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useChat as jest.Mock).mockReturnValue({
      messages: [],
      isSending: false,
      isStreaming: false,
      connectionStatus: 'connected',
      error: null,
      sendMessage: mockSendMessage,
      setActiveConversation: mockSetActiveConversation,
    });
  });

  it('renders welcome state when no messages', () => {
    render(<ChatInterface />);

    expect(screen.getByText('Welcome to HealthConnect AI')).toBeInTheDocument();
    expect(
      screen.getByText(/Ask about appointments, services/),
    ).toBeInTheDocument();
  });

  it('renders messages correctly', () => {
    (useChat as jest.Mock).mockReturnValue({
      messages: [
        {
          id: 'msg-1',
          role: 'user',
          content: 'How do I book an appointment?',
          timestamp: '2024-01-15T10:00:00Z',
        },
        {
          id: 'msg-2',
          role: 'assistant',
          content: 'To book an appointment, please select a service.',
          timestamp: '2024-01-15T10:00:01Z',
        },
      ],
      isSending: false,
      isStreaming: false,
      connectionStatus: 'connected',
      error: null,
      sendMessage: mockSendMessage,
      setActiveConversation: mockSetActiveConversation,
    });

    render(<ChatInterface />);

    expect(screen.getByText('How do I book an appointment?')).toBeInTheDocument();
    expect(
      screen.getByText('To book an appointment, please select a service.'),
    ).toBeInTheDocument();
  });

  it('shows typing indicator when sending', () => {
    (useChat as jest.Mock).mockReturnValue({
      messages: [],
      isSending: true,
      isStreaming: false,
      connectionStatus: 'connected',
      error: null,
      sendMessage: mockSendMessage,
      setActiveConversation: mockSetActiveConversation,
    });

    render(<ChatInterface />);
    expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
  });

  it('shows error message when error exists', () => {
    (useChat as jest.Mock).mockReturnValue({
      messages: [],
      isSending: false,
      isStreaming: false,
      connectionStatus: 'connected',
      error: 'Failed to send message',
      sendMessage: mockSendMessage,
      setActiveConversation: mockSetActiveConversation,
    });

    render(<ChatInterface />);
    expect(screen.getByText('Failed to send message')).toBeInTheDocument();
  });

  it('shows quick replies when no messages', () => {
    render(<ChatInterface />);

    expect(screen.getByText('Book an appointment')).toBeInTheDocument();
    expect(screen.getByText('Check clinic hours')).toBeInTheDocument();
  });

  it('disables send button when not connected', () => {
    (useChat as jest.Mock).mockReturnValue({
      messages: [],
      isSending: false,
      isStreaming: false,
      connectionStatus: 'disconnected',
      error: null,
      sendMessage: mockSendMessage,
      setActiveConversation: mockSetActiveConversation,
    });

    render(<ChatInterface />);
    
    const textarea = screen.getByTestId('textarea-chat-message');
    expect(textarea).toBeDisabled();
  });
});