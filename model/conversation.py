from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from model.database import Base

class Conversation(Base):
    __tablename__ = "conversation"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    # 관계
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete")
