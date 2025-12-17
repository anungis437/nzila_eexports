import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

const API_BASE_URL = '/api/chat';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
}

export interface Vehicle {
  id: number;
  make: string;
  model: string;
  year: number;
  vin: string;
  price_cad?: number;
}

export interface Message {
  id: number;
  conversation: number;
  sender: number;
  sender_email: string;
  sender_name: string;
  content: string;
  attachment?: string;
  attachment_url?: string;
  created_at: string;
  is_read: boolean;
  read_at?: string;
  is_system_message: boolean;
}

export interface Conversation {
  id: number;
  participant_1: number;
  participant_2: number;
  participant_1_info?: User;
  participant_2_info?: User;
  other_participant?: {
    id: number;
    email: string;
    full_name: string;
    role: string;
  };
  vehicle?: number;
  vehicle_info?: Vehicle;
  deal?: number;
  subject: string;
  messages?: Message[];
  last_message?: {
    content: string;
    created_at: string;
    sender_email: string;
  };
  unread_count: number;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
}

export interface StartConversationRequest {
  participant_id: number;
  vehicle_id?: number;
  subject?: string;
  initial_message?: string;
}

export interface SendMessageRequest {
  conversation: number;
  content: string;
  attachment?: File;
}

// Fetch conversations list
export const useConversations = () => {
  return useQuery<Conversation[]>({
    queryKey: ['conversations'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/conversations/`, {
        withCredentials: true,
      });
      // Handle both paginated (DRF default) and direct array responses
      return response.data.results || response.data;
    },
    refetchInterval: 5000, // Poll every 5 seconds
  });
};

// Fetch single conversation with messages
export const useConversation = (conversationId: number | undefined) => {
  return useQuery<Conversation>({
    queryKey: ['conversation', conversationId],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/conversations/${conversationId}/`, {
        withCredentials: true,
      });
      return response.data;
    },
    enabled: !!conversationId,
    refetchInterval: 3000, // Poll every 3 seconds for new messages
  });
};

// Start a new conversation
export const useStartConversation = () => {
  const queryClient = useQueryClient();
  
  return useMutation<Conversation, Error, StartConversationRequest>({
    mutationFn: async (data) => {
      const response = await axios.post(`${API_BASE_URL}/conversations/start_conversation/`, data, {
        withCredentials: true,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
};

// Send a message
export const useSendMessage = () => {
  const queryClient = useQueryClient();
  
  return useMutation<Message, Error, SendMessageRequest>({
    mutationFn: async (data) => {
      const formData = new FormData();
      formData.append('conversation', data.conversation.toString());
      formData.append('content', data.content);
      if (data.attachment) {
        formData.append('attachment', data.attachment);
      }
      
      const response = await axios.post(`${API_BASE_URL}/messages/`, formData, {
        withCredentials: true,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['conversation', variables.conversation] });
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
};

// Mark conversation as read
export const useMarkConversationAsRead = () => {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error, number>({
    mutationFn: async (conversationId) => {
      await axios.post(`${API_BASE_URL}/conversations/${conversationId}/mark_as_read/`, {}, {
        withCredentials: true,
      });
    },
    onSuccess: (_, conversationId) => {
      queryClient.invalidateQueries({ queryKey: ['conversation', conversationId] });
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      queryClient.invalidateQueries({ queryKey: ['unread-count'] });
    },
  });
};

// Get unread message count
export const useUnreadCount = () => {
  return useQuery<{ unread_count: number }>({
    queryKey: ['unread-count'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/conversations/unread_count/`, {
        withCredentials: true,
      });
      return response.data;
    },
    refetchInterval: 10000, // Poll every 10 seconds
  });
};

// Archive conversation
export const useArchiveConversation = () => {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error, number>({
    mutationFn: async (conversationId) => {
      await axios.post(`${API_BASE_URL}/conversations/${conversationId}/archive/`, {}, {
        withCredentials: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
};
