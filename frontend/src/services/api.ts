import axios from 'axios';
import {
  User,
  Chat,
  Message,
  ChatCreate,
  MessageCreate,
  LoginCredentials,
  RegisterData,
  AuthResponse,
  SendMessageRequest,
  SendMessageResponse,
} from '../types';

const API_BASE_URL = '/api';

// axios 인스턴스 생성
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 - 토큰 추가
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  },
);

// 응답 인터셉터 - 토큰 만료 처리
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

// 인증 관련 API
export const authAPI = {
  register: (data: RegisterData) => api.post<User>('/auth/register', data),

  login: (data: LoginCredentials) => api.post<AuthResponse>('/auth/login', data),

  getCurrentUser: () => api.get<User>('/auth/me'),
};

// 채팅 관련 API
export const chatAPI = {
  createChat: (data: ChatCreate) => api.post<Chat>('/chat/', data),

  getUserChats: () => api.get<Chat[]>('/chat/'),

  getChat: (chatId: number) => api.get<Chat>(`/chat/${chatId}`),

  updateChat: (chatId: number, data: Partial<Chat>) => api.put<Chat>(`/chat/${chatId}`, data),

  deleteChat: (chatId: number) => api.delete(`/chat/${chatId}`),

  createMessage: (chatId: number, data: MessageCreate) =>
    api.post<Message>(`/chat/${chatId}/messages`, data),

  getChatMessages: (chatId: number) => api.get<Message[]>(`/chat/${chatId}/messages`),

  sendMessage: (chatId: number, data: SendMessageRequest) =>
    api.post<SendMessageResponse>(`/chat/${chatId}/send-message`, data),
};

export default api;
