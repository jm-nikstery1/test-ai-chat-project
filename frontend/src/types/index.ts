export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Message {
  id: number;
  content: string;
  role: 'user' | 'assistant' | 'system';
  chat_id: number;
  user_id: number;
  created_at: string;
}

export interface Chat {
  id: number;
  title: string;
  user_id: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  messages: Message[];
}

export interface ChatCreate {
  title: string;
  user_id: number;
}

export interface MessageCreate {
  content: string;
  role: 'user' | 'assistant' | 'system';
  chat_id: number;
  user_id: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface SendMessageRequest {
  content: string;
}

export interface SendMessageResponse {
  user_message: Message;
  assistant_message: Message;
}
