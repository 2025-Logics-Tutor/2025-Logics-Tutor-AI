from typing import List, AsyncGenerator
import json
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import desc
from sqlalchemy.orm import Session

from model.conversation import Conversation
from model.database import get_db
from model.schema import ChatResponse, ConversationResponse, ConversationsResponse, Level
from service.gpt_service import GPTService
from model.message import Message
from model.user import User

router = APIRouter(prefix="/api/conversations")
gpt_service = GPTService()

def get_system_prompt(level: Level) -> str:
    return {
        Level.ELEMENTARY: "너는 초등학생에게 설명해주는 친절한 논리학 튜터야. 쉬운 말로 풀어서 설명해줘.",
        Level.UNIV: "너는 대학생에게 설명해주는 논리학 튜터야. 핵심 개념을 정확하게 전달해줘.",
        Level.GRAD: "너는 대학원생에게 설명해주는 전문 논리학 튜터야. 깊이 있는 설명과 예시를 포함해줘."
    }[level]


# ✅ GET /api/conversations - 대화 목록 가져오기
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

    conversations = db.query(Conversation).filter_by(user_id=user.id).order_by(desc(Conversation.id)).all()

    result = []
    for c in conversations:
        title = "새 대화"
        for m in c.messages:
            if m.role == "USER":
                title = m.content[:20]
                break
        result.append(ConversationsResponse(conversation_id=c.id, title=title))

    return result


# ✅ 새 대화 시작 (conversationId → 헤더)
@router.get("/chat-new")
async def start_new_chat_stream(
        message: str = Query(...),
        level: Level = Query(Level.UNIV),
        quote: str = Query(None),
        Authorize: AuthJWT = Depends(),
        db: Session = Depends(get_db)
):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    user = db.query(User).filter_by(email=user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    conversation = Conversation(user_id=user.id, title=message)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    db.add(Message(conversation_id=conversation.id, role="USER", content=message))
    db.commit()

    system_prompt = get_system_prompt(level)
    if quote:
        system_prompt = (
            f'당신은 논리학 전문 튜터입니다.\n\n'
            f'반드시 아래 인용구를 가장 중요한 맥락으로 삼아 질문에 답해야 합니다.\n'
            f'이 인용구는 사용자의 의도를 이해하는 데 결정적인 단서입니다.\n\n'
            f'[인용구]\n"{quote}"\n\n'
            f'이 내용을 중심에 두고, 관련된 질문에 대해 논리적으로 명확하게 설명하세요.\n\n'
            f'{system_prompt}'
        )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]

    async def stream_response() -> AsyncGenerator[str, None]:
        buffer = ""
        async for chunk in gpt_service.stream_chat(messages):
            buffer += chunk
            yield chunk
        buffer = buffer.replace("\\\\", "\\")
        db.add(Message(conversation_id=conversation.id, role="ASSISTANT", content=buffer))
        db.commit()

    headers = {"X-Conversation-Id": str(conversation.id)}
    return StreamingResponse(stream_response(), media_type="text/event-stream", headers=headers)


@router.get("/{conversation_id}/chat-stream")
async def stream_chat_existing(
        conversation_id: int,
        message: str = Query(...),
        level: Level = Query(Level.UNIV),
        quote: str = Query(None),
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

    db.add(Message(conversation_id=conversation_id, role="USER", content=message))
    db.commit()

    history = db.query(Message).filter_by(conversation_id=conversation_id).order_by(Message.created_at.asc()).all()

    system_prompt = get_system_prompt(level)
    if quote:
        system_prompt = (
            f'당신은 논리학 전문 튜터입니다.\n\n'
            f'반드시 아래 인용구를 가장 중요한 맥락으로 삼아 질문에 답해야 합니다.\n'
            f'이 인용구는 사용자의 의도를 이해하는 데 결정적인 단서입니다.\n\n'
            f'[인용구]\n"{quote}"\n\n'
            f'이 내용을 중심에 두고, 관련된 질문에 대해 논리적으로 명확하게 설명하세요.\n\n'
            f'{system_prompt}'
        )

    messages = [{"role": "system", "content": system_prompt}]
    messages += [{"role": msg.role.lower(), "content": msg.content} for msg in history]
    messages.append({"role": "user", "content": message})

    async def stream_response() -> AsyncGenerator[str, None]:
        buffer = ""
        async for chunk in gpt_service.stream_chat(messages):
            buffer += chunk
            yield chunk
        buffer = buffer.replace("\\\\", "\\")
        db.add(Message(conversation_id=conversation_id, role="ASSISTANT", content=buffer))
        db.commit()

    return StreamingResponse(stream_response(), media_type="text/event-stream")


# ✅ DELETE /api/conversations/{conversation_id} - 대화 삭제
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


# ✅ GET /api/conversations/{conversation_id} - 대화 내용 조회
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