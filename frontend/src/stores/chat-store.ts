/**
 * HealthConnect AI - Chat Store (Zustand)
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ChatMessage, Conversation } from '@/types';

interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  messages: Record<string, ChatMessage[]>;
  isStreaming: boolean;
  typingIndicator: boolean;
  
  setActiveConversation: (id: string | null) => void;
  addConversation: (conversation: Conversation) => void;
  updateConversation: (id: string, updates: Partial<Conversation>) => void;
  removeConversation: (id: string) => void;
  addMessage: (conversationId: string, message: ChatMessage) => void;
  addMessages: (conversationId: string, messages: ChatMessage[]) => void;
  clearMessages: (conversationId: string) => void;
  setStreaming: (isStreaming: boolean) => void;
  setTypingIndicator: (show: boolean) => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      conversations: [],
      activeConversationId: null,
      messages: {},
      isStreaming: false,
      typingIndicator: false,
      
      setActiveConversation: (id) =>
        set({ activeConversationId: id }),
      
      addConversation: (conversation) =>
        set((state) => ({
          conversations: [conversation, ...state.conversations.filter(c => c.id !== conversation.id)],
        })),
      
      updateConversation: (id, updates) =>
        set((state) => ({
          conversations: state.conversations.map((c) =>
            c.id === id ? { ...c, ...updates } : c,
          ),
        })),
      
      removeConversation: (id) =>
        set((state) => ({
          conversations: state.conversations.filter((c) => c.id !== id),
          messages: Object.fromEntries(
            Object.entries(state.messages).filter(([key]) => key !== id),
          ),
        })),
      
      addMessage: (conversationId, message) =>
        set((state) => ({
          messages: {
            ...state.messages,
            [conversationId]: [...(state.messages[conversationId] || []), message],
          },
        })),
      
      addMessages: (conversationId, messages) =>
        set((state) => ({
          messages: {
            ...state.messages,
            [conversationId]: [...(state.messages[conversationId] || []), ...messages],
          },
        })),
      
      clearMessages: (conversationId) =>
        set((state) => ({
          messages: {
            ...state.messages,
            [conversationId]: [],
          },
        })),
      
      setStreaming: (isStreaming) =>
        set({ isStreaming }),
      
      setTypingIndicator: (show) =>
        set({ typingIndicator: show }),
    }),
    {
      name: 'healthconnect-chat',
      partialize: (state) => ({
        conversations: state.conversations,
        activeConversationId: state.activeConversationId,
        messages: state.messages,
      }),
    },
  ),
);