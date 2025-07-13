from fastapi import APIRouter, HTTPException
from asklogic_ai.model.schemas import AskRequest, AskResponse
from asklogic_ai.service.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()

@router.post("", response_model=AskResponse)
async def ask_question(request: AskRequest):
    try:
        return await rag_service.answer_question(request.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
