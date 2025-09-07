import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { chatAPI } from '../services/api';
import { Chat, Message } from '../types';
import ChatSidebar from './ChatSidebar';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const ChatInterface: React.FC = () => {
  const { user, logout } = useAuth();
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChat, setCurrentChat] = useState<Chat | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 채팅 목록 가져오기
  const fetchChats = async () => {
    try {
      const response = await chatAPI.getUserChats();
      setChats(response.data);
      if (response.data.length > 0 && !currentChat) {
        setCurrentChat(response.data[0]);
      }
    } catch (error: any) {
      setError('채팅 목록을 가져오는데 실패했습니다.');
    }
  };

  // 새 채팅 생성
  const createNewChat = async () => {
    try {
      const response = await chatAPI.createChat({
        title: `새 채팅 ${chats.length + 1}`,
        user_id: user!.id,
      });
      const newChat = response.data;
      setChats(prev => [newChat, ...prev]);
      setCurrentChat(newChat);
    } catch (error: any) {
      setError('새 채팅을 생성하는데 실패했습니다.');
    }
  };

  // 메시지 전송
  const sendMessage = async (content: string) => {
    if (!currentChat || !user) return;

    try {
      setLoading(true);
      setError('');

      // 새로운 send-message API 사용
      const response = await chatAPI.sendMessage(currentChat.id, { content });
      const { user_message, assistant_message } = response.data;

      // 현재 채팅에 두 메시지 모두 추가
      setCurrentChat(prev =>
        prev
          ? {
              ...prev,
              messages: [...prev.messages, user_message, assistant_message],
            }
          : null,
      );

      // 채팅 목록 업데이트
      setChats(prev =>
        prev.map(chat =>
          chat.id === currentChat.id
            ? { ...chat, messages: [...chat.messages, user_message, assistant_message] }
            : chat,
        ),
      );
    } catch (error: any) {
      setError('메시지 전송에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 채팅 선택
  const selectChat = async (chat: Chat) => {
    setCurrentChat(chat);

    // 선택한 채팅의 메시지 로드
    try {
      const response = await chatAPI.getChatMessages(chat.id);
      const messages = response.data;

      // 현재 채팅에 메시지 업데이트
      setCurrentChat(prev => (prev ? { ...prev, messages } : null));

      // 채팅 목록의 해당 채팅도 업데이트
      setChats(prev => prev.map(c => (c.id === chat.id ? { ...c, messages } : c)));
    } catch (error: any) {
      setError('메시지를 불러오는데 실패했습니다.');
    }
  };

  // 채팅 삭제
  const deleteChat = async (chatId: number) => {
    try {
      await chatAPI.deleteChat(chatId);
      setChats(prev => prev.filter(chat => chat.id !== chatId));
      if (currentChat?.id === chatId) {
        setCurrentChat(chats.length > 1 ? chats.find(c => c.id !== chatId) || null : null);
      }
    } catch (error: any) {
      setError('채팅 삭제에 실패했습니다.');
    }
  };

  useEffect(() => {
    fetchChats();
  }, []);

  if (!user) {
    return <div>로그인이 필요합니다.</div>;
  }

  return (
    <div className='flex h-screen bg-gray-100'>
      {/* 사이드바 */}
      <ChatSidebar
        chats={chats}
        currentChat={currentChat}
        onSelectChat={selectChat}
        onCreateChat={createNewChat}
        onDeleteChat={deleteChat}
      />

      {/* 메인 채팅 영역 */}
      <div className='flex-1 flex flex-col'>
        {/* 헤더 */}
        <div className='bg-white border-b border-gray-200 px-6 py-4'>
          <div className='flex items-center justify-between'>
            <h1 className='text-xl font-semibold text-gray-900'>
              {currentChat?.title || '새 채팅'}
            </h1>
            <div className='flex items-center space-x-4'>
              <span className='text-sm text-gray-500'>{user.username}님</span>
              <button onClick={logout} className='text-sm text-red-600 hover:text-red-800'>
                로그아웃
              </button>
            </div>
          </div>
        </div>

        {/* 메시지 영역 */}
        <div className='flex-1 flex flex-col min-h-0'>
          {currentChat ? (
            <>
              <div className='flex-1 min-h-0'>
                <MessageList messages={currentChat.messages} />
              </div>
              <div className='flex-shrink-0'>
                <MessageInput onSendMessage={sendMessage} />
              </div>
            </>
          ) : (
            <div className='flex items-center justify-center h-full'>
              <div className='text-center'>
                <h3 className='text-lg font-medium text-gray-900 mb-2'>
                  채팅을 선택하거나 새로 만들어보세요
                </h3>
                <button
                  onClick={createNewChat}
                  className='bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700'
                >
                  새 채팅 시작
                </button>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className='bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 mx-4'>
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
