from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT

from model.database import Base, engine
from model.user import User, RefreshToken
from model.conversation import Conversation
from model.message import Message
from config.settings import Settings

print(Settings().dict())

Base.metadata.create_all(bind=engine)

@AuthJWT.load_config
def get_config():
    return Settings()

app = FastAPI()

from api.auth_router import router as auth_router
app.include_router(auth_router)
from api.conversation_router import router as conversation_router
app.include_router(conversation_router)
