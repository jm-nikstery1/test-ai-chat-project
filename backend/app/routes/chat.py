from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
from app.database import get_db
from app.models.user import User
from app.models.chat import Chat, Message
from app.schemas.chat import ChatCreate, Chat as ChatSchema, ChatUpdate, MessageCreate, Message as MessageSchema, SendMessageRequest, SendMessageResponse
from app.auth import get_current_active_user

# --- [수정 1] 스팀 에이전트와 Gemini 관련 모듈 임포트 ---
import google.generativeai as genai
from app.ai_chat import config
from app.ai_chat.agent import SteamGameAgent


# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatSchema)
def create_chat(chat: ChatCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_chat = Chat(
        title=chat.title,
        user_id=current_user.id
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

@router.get("/", response_model=List[ChatSchema])
def get_user_chats(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    chats = db.query(Chat).filter(Chat.user_id == current_user.id, Chat.is_active == True).all()
    return chats

@router.get("/{chat_id}", response_model=ChatSchema)
def get_chat(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.put("/{chat_id}", response_model=ChatSchema)
def update_chat(chat_id: int, chat_update: ChatUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not db_chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    for field, value in chat_update.dict(exclude_unset=True).items():
        setattr(db_chat, field, value)
    
    db.commit()
    db.refresh(db_chat)
    return db_chat

@router.delete("/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat.is_active = False
    db.commit()
    return {"message": "Chat deleted successfully"}

@router.post("/{chat_id}/messages", response_model=MessageSchema)
def create_message(chat_id: int, message: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    # 채팅이 존재하고 사용자 소유인지 확인
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db_message = Message(
        content=message.content,
        role=message.role,
        chat_id=chat_id,
        user_id=current_user.id
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.get("/{chat_id}/messages", response_model=List[MessageSchema])
def get_chat_messages(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    # 채팅이 존재하고 사용자 소유인지 확인
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
    return messages

@router.post("/{chat_id}/send-message", response_model=SendMessageResponse)
def send_message(chat_id: int, message_request: SendMessageRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    사용자 메시지를 전송하고 AI 응답을 생성하여 둘 다 저장합니다.
    """
    # 채팅이 존재하고 사용자 소유인지 확인
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # 1. 사용자 메시지 저장
    user_message = Message(
        content=message_request.content,
        role="user",
        chat_id=chat_id,
        user_id=current_user.id
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # 2. AI 응답 생성 (임시적으로 간단한 응답)
    ai_response_content = generate_ai_response(message_request.content)
    
    # 3. AI 응답 메시지 저장
    assistant_message = Message(
        content=ai_response_content,
        role="assistant",
        chat_id=chat_id,
        user_id=current_user.id
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    
    return SendMessageResponse(
        user_message=user_message,
        assistant_message=assistant_message
    )

def generate_ai_response(user_message: str) -> str:
    """
    AI 응답 생성 함수
    - Steam 관련 질문: SteamGameAgent 사용 (MySQL, Qdrant, Neo4j 연동)
    - 일반 대화: Gemini API 사용
    """
    try:
        # Steam 관련 키워드가 있는지 확인
        if "스팀" in user_message or "steam" in user_message.lower():
            logger.info("Steam 관련 질문 감지, SteamGameAgent 사용")
            return _generate_steam_response(user_message)
        else:
            # 일반 대화는 Gemini API 사용
            logger.info("일반 대화, Gemini API 사용")
            return _generate_general_response(user_message)
            
    except Exception as e:
        logger.error(f"AI 응답 생성 중 오류: {e}")
        return f"죄송합니다. 현재 AI 서비스에 연결할 수 없습니다. 사용자님의 메시지: '{user_message}'"

def _generate_steam_response(user_message: str) -> str:
    """Steam 관련 질문에 대한 응답 생성"""
    try:
        # SteamGameAgent 초기화 및 실행 (이미 상단에서 import됨)
        steam_agent = SteamGameAgent()
        response, tool_name = steam_agent.route_query(user_message)
        steam_agent.close_connections()  # 연결 정리
        
        logger.info(f"SteamGameAgent 응답 생성 완료 (도구: {tool_name})")
        return response
        
    except Exception as e:
        logger.error(f"SteamGameAgent 실행 중 오류: {e}")
        return f"Steam 게임 정보 처리 중 오류가 발생했습니다. 일반 대화로 전환합니다."

def _generate_general_response(user_message: str) -> str:
    """일반 대화에 대한 응답 생성 (Gemini API 사용)"""
    try:
        # Gemini API 설정
        genai.configure(api_key=config.GOOGLE_API_KEY)
        model = genai.GenerativeModel(config.GEMINI_MODEL_NAME)
        
        logger.info(f"Gemini API에 메시지 전송: {user_message[:50]}...")
        
        # Gemini API로 채팅 요청
        response = model.generate_content(user_message)
        
        ai_response = response.text
        logger.info(f"Gemini API 응답 수신: {ai_response[:50]}...")
        
        return ai_response
        
    except Exception as e:
        logger.error(f"Gemini API 연결 실패: {e}")
        return f"죄송합니다. 현재 AI 서비스에 연결할 수 없습니다. 사용자님의 메시지: '{user_message}'"
