from sqlalchemy import Column, String, Integer, Enum as SqlEnum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from model.database import Base
import enum

class LevelEnum(str, enum.Enum):
    ELEMENTARY = "ELEMENTARY"
    UNIV = "UNIV"
    GRAD = "GRAD"

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # 관계
    conversations = relationship("Conversation", back_populates="user")

class RefreshToken(Base):
    __tablename__ = "refresh_token"

    email = Column(String, primary_key=True)
    token = Column(String(512), nullable=False)