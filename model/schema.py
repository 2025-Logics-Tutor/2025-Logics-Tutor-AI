from pydantic import BaseModel, EmailStr
from enum import Enum


class Level(str, Enum):
    ELEMENTARY = "ELEMENTARY"
    UNIV = "UNIV"
    GRAD = "GRAD"


class ChatRequest(BaseModel):
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    nickname: str
    level: Level

from pydantic import BaseModel
from typing import List
from datetime import datetime


class ChatResponse(BaseModel):
    message_id: int
    role: str         # "user" or "assistant"
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    conversation_id: int
    conversation_title: str
    messages: List[ChatResponse]


class ConversationsResponse(BaseModel):
    conversation_id: int
    title: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
