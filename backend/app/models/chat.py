# ============================================
# NEXORA AI - Chat & Message Models
# ============================================

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import relationship
import enum
from app.database.postgres_db import Base


class MessageRole(str, enum.Enum):
    """Message কে user বা assistant হিসেবে চিহ্নিত করা।"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AgentType(str, enum.Enum):
    """কোন agent response দিয়েছে।"""
    GENERAL = "general"
    TUTOR = "tutor"
    PLANNER = "planner"
    RAG = "rag"


class Chat(Base):
    """
    Chat session - একটি conversation thread।
    """
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), default="New Chat")
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan", order_by="Message.created_at")

    def __repr__(self):
        return f"<Chat(id={self.id}, title={self.title})>"


class Message(Base):
    """
    Individual message - chat এর একটি বার্তা।
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # AI Response metadata
    agent_type = Column(Enum(AgentType), default=AgentType.GENERAL)
    model_used = Column(String(100), nullable=True)     # কোন AI model ব্যবহার হয়েছে
    tokens_used = Column(Integer, default=0)             # Token count
    response_time_ms = Column(Integer, default=0)        # Response কত দ্রুত এলো

    # RAG related
    sources_used = Column(Text, nullable=True)           # JSON string of source docs

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    chat = relationship("Chat", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role})>"
