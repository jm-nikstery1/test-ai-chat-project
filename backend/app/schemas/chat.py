from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MessageBase(BaseModel):
    content: str
    role: str

class MessageCreate(MessageBase):
    chat_id: int
    user_id: int

class Message(MessageBase):
    id: int
    chat_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 새로운 스키마: 메시지 전송 및 AI 응답 생성
class SendMessageRequest(BaseModel):
    content: str

class SendMessageResponse(BaseModel):
    user_message: Message
    assistant_message: Message

class ChatBase(BaseModel):
    title: str

class ChatCreate(ChatBase):
    user_id: int

class ChatUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None

class Chat(ChatBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[Message] = []

    class Config:
        from_attributes = True

class ChatWithMessages(Chat):
    messages: List[Message]
