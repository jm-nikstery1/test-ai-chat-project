import React from 'react';
import { Chat } from '../types';
import { Plus, Trash2 } from 'lucide-react';

interface ChatSidebarProps {
  chats: Chat[];
  currentChat: Chat | null;
  onSelectChat: (chat: Chat) => void;
  onCreateChat: () => void;
  onDeleteChat: (chatId: number) => void;
}

const ChatSidebar: React.FC<ChatSidebarProps> = ({
  chats,
  currentChat,
  onSelectChat,
  onCreateChat,
  onDeleteChat
}) => {
  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
      {/* 헤더 */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">채팅</h2>
          <button
            onClick={onCreateChat}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md"
            title="새 채팅"
          >
            <Plus size={20} />
          </button>
        </div>
      </div>

      {/* 채팅 목록 */}
      <div className="flex-1 overflow-y-auto">
        {chats.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <p>채팅이 없습니다.</p>
            <button
              onClick={onCreateChat}
              className="mt-2 text-indigo-600 hover:text-indigo-800 text-sm"
            >
              첫 번째 채팅을 만들어보세요
            </button>
          </div>
        ) : (
          <div className="p-2">
            {chats.map((chat) => (
              <div
                key={chat.id}
                className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
                  currentChat?.id === chat.id
                    ? 'bg-indigo-100 text-indigo-900'
                    : 'hover:bg-gray-100'
                }`}
                onClick={() => onSelectChat(chat)}
              >
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">
                    {chat.title}
                  </div>
                  <div className="text-xs text-gray-500 truncate">
                    {chat.messages.length > 0
                      ? chat.messages[chat.messages.length - 1]?.content
                      : '새 채팅'}
                  </div>
                </div>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-all"
                  title="채팅 삭제"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatSidebar;
