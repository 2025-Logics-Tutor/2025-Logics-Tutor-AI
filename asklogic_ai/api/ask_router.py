from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from asklogic_ai.service.generator import stream_answer, generate_conversation_response
from asklogic_ai.model.schemas import AskRequest, ConversationRequest
import asyncio

router = APIRouter()

# 기존 대화에 메시지 추가 (스트리밍 응답)
@router.post("/stream")
async def ask_question_stream(request: AskRequest):
    async def token_stream():
        async for token in stream_answer(request.question):
            yield token  # 백엔드에 바로바로 전달

    return StreamingResponse(token_stream(), media_type="text/plain")


# 새 대화 생성 (title + answer 전부 받아서 통째로 전달)
@router.post("/new")
async def start_new_conversation(request: ConversationRequest):
    result = await generate_conversation_response(request.question)

    return JSONResponse({
        "title": result["title"],
        "answer": result["answer"]
    })