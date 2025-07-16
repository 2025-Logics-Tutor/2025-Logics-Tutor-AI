from typing import List
import json
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from model.conversation import Conversation
from model.database import get_db
from model.schema import ChatRequest, ChatResponse, ConversationResponse, ConversationsResponse
from service.gpt_service import GPTService
from model.message import Message
from model.user import User

router = APIRouter(prefix="/api/conversations")
gpt_service = GPTService()


# GET /api/conversations
@router.get("", response_model=List[ConversationsResponse])
async def get_conversations(
        Authorize: AuthJWT = Depends(),
        db: Session = Depends(get_db)
):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()

    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    conversations = db.query(Conversation).filter_by(user_id=user.id).all()
    return [
        ConversationsResponse(
            conversation_id=c.id,
            title=(c.messages[0].content[:20] if c.messages else "새 대화")
        )
        for c in conversations
    ]


# GET /api/conversations/{conversationId}
@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
        conversation_id: int,
        Authorize: AuthJWT = Depends(),
        db: Session = Depends(get_db)
):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()

    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    conversation = db.query(Conversation).filter_by(id=conversation_id, user_id=user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="해당 대화를 찾을 수 없습니다")

    messages = db.query(Message).filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).all()

    return ConversationResponse(
        conversation_id=conversation.id,
        conversation_title=(messages[0].content[:20] if messages else "대화"),
        messages=[
            ChatResponse(
                message_id=m.id,
                role=m.role.lower(),
                content=m.content,
                created_at=m.created_at
            ) for m in messages
        ]
    )


# POST /api/conversations/chat/new
@router.post("/chat/new")
async def start_new_chat(
        request: ChatRequest,
        Authorize: AuthJWT = Depends(),
        db: Session = Depends(get_db)
):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    async def stream_response():
        # ① 대화 객체 생성
        conversation = Conversation(user_id=user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        # ② 사용자 메시지 저장
        user_msg = Message(
            conversation_id=conversation.id,
            role="USER",
            content=request.message,
        )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)

        # ③ 첫 응답에 conversationId 포함
        yield f"data: {json.dumps({'conversationId': conversation.id})}\n\n"

        # ④ GPT 응답을 스트리밍하며 전송 + 저장
        buffer = ""
        async for chunk in gpt_service.stream_chat([{"role": "user", "content": request.message}]):
            buffer += chunk
            yield f"data: {chunk}\n\n"

        assistant_msg = Message(
            conversation_id=conversation.id,
            role="ASSISTANT",
            content=buffer
        )
        db.add(assistant_msg)
        db.commit()

    return StreamingResponse(stream_response(), media_type="text/event-stream")


# POST /api/conversations/{conversationId}/chat
@router.post("/{conversation_id}/chat")
async def chat_existing(
        conversation_id: int,
        request: ChatRequest,
        Authorize: AuthJWT = Depends(),
        db: Session = Depends(get_db)
):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    conversation = db.query(Conversation).filter_by(id=conversation_id, user_id=user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    async def stream_response():
        user_msg = Message(
            conversation_id=conversation_id,
            role="USER",
            content=request.message,
        )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)

        history = db.query(Message).filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).all()
        messages = [{"role": msg.role.lower(), "content": msg.content} for msg in history]
        messages.append({"role": "user", "content": request.message})

        buffer = ""
        async for chunk in gpt_service.stream_chat(messages):
            buffer += chunk
            yield f"data: {chunk}\n\n"

        assistant_msg = Message(
            conversation_id=conversation_id,
            role="ASSISTANT",
            content=buffer
        )
        db.add(assistant_msg)
        db.commit()

    return StreamingResponse(stream_response(), media_type="text/event-stream")


# DELETE /api/conversations/{conversation_id}
@router.delete("/{conversation_id}")
async def delete_conversation(
        conversation_id: int,
        Authorize: AuthJWT = Depends(),
        db: Session = Depends(get_db)
):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    conversation = db.query(Conversation).filter_by(id=conversation_id, user_id=user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="해당 대화를 찾을 수 없습니다")

    db.delete(conversation)
    db.commit()

    return {"message": "삭제 완료"}