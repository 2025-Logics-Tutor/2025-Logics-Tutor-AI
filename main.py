from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from config.jwt import Settings

# JWT 설정 로드
@AuthJWT.load_config
def get_config():
    return Settings()

# DB 모델 등록 및 테이블 생성
from model.database import Base, engine
from model.user import User, RefreshToken
from model.conversation import Conversation
from model.message import Message

Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI()

# 라우터 등록
from api.auth_router import router as auth_router

app = FastAPI()
app.include_router(auth_router)
