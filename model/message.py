from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from model.database import Base

class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id"), nullable=False)
    role = Column(String, nullable=False)  # "USER" or "ASSISTANT"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_documented = Column(Boolean, nullable=True)

    # 관계
    conversation = relationship("Conversation", back_populates="messages")
