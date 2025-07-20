import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from starlette.middleware.cors import CORSMiddleware

from model.database import Base, engine
from model.user import User, RefreshToken
from model.conversation import Conversation
from model.message import Message
from config.settings import Settings

# ✅ RAG 인덱싱 관련 추가
import asyncio
from service.rag_ingest_service import ingest_csv_to_vectorstore

print(Settings().dict())

Base.metadata.create_all(bind=engine)

@AuthJWT.load_config
def get_config():
    return Settings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 또는 ["*"] 개발 중일 땐 전체 허용
    allow_credentials=True,
    allow_methods=["*"],  # ✅ OPTIONS 포함해서 전부 허용
    allow_headers=["*"],
    expose_headers=["X-Conversation-Id"],
)

# ✅ 서버 시작 시 RAG 데이터 ingest
@app.on_event("startup")
async def load_rag_data():
    try:
        count = await ingest_csv_to_vectorstore("data/myfile.csv")
        print(f"✅ RAG 벡터 저장 완료: {count}건")
    except Exception as e:
        print(f"❌ RAG 벡터 저장 실패: {e}")

# ✅ 라우터 등록
from api.auth_router import router as auth_router
app.include_router(auth_router)

from api.conversation_router import router as conversation_router
app.include_router(conversation_router)
