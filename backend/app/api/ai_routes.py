# ============================================
# NEXORA AI - AI Chat Routes
# ============================================
# Chat, agent selection, streaming endpoints।

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
import json
import time

from app.database.postgres_db import get_db
from app.models.chat import Chat, Message, MessageRole, AgentType
from app.models.analytics import Analytics
from app.ai.llm.router import llm_router
from app.ai.agents.tutor_agent import tutor_agent
from app.ai.agents.planner_agent import planner_agent
from app.ai.agents.memory_agent import memory_agent
from app.core.security import get_current_user_id
from app.core.logger import logger
import os

router = APIRouter(prefix="/api/ai", tags=["AI Chat"])

# System prompt লোড করা
def load_system_prompt() -> str:
    try:
        prompt_path = os.path.join(
            os.path.dirname(__file__), "..", "ai", "prompts", "system_prompt.txt"
        )
        with open(prompt_path, "r") as f:
            return f.read()
    except:
        return "You are NEXORA AI, a helpful assistant."

SYSTEM_PROMPT = load_system_prompt()


# ============================================
# Request Schemas
# ============================================
class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[int] = None
    agent: str = "general"           # general, tutor, planner
    stream: bool = False


class NewChatRequest(BaseModel):
    title: str = "New Chat"


# ============================================
# Create New Chat
# ============================================
@router.post("/chats")
async def create_chat(
    request: NewChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """নতুন chat session তৈরি করে।"""
    chat = Chat(user_id=user_id, title=request.title)
    db.add(chat)
    await db.flush()
    await db.refresh(chat)

    return {"chat_id": chat.id, "title": chat.title, "created_at": chat.created_at}


# ============================================
# Get User's Chats
# ============================================
@router.get("/chats")
async def get_chats(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """User এর সব chat sessions পায়।"""
    result = await db.execute(
        select(Chat)
        .where(Chat.user_id == user_id, Chat.is_active == True)
        .order_by(Chat.created_at.desc())
        .limit(20)
    )
    chats = result.scalars().all()

    return [{"id": c.id, "title": c.title, "created_at": c.created_at} for c in chats]


# ============================================
# Get Chat Messages
# ============================================
@router.get("/chats/{chat_id}/messages")
async def get_messages(
    chat_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """নির্দিষ্ট chat এর সব messages পায়।"""
    # Chat ownership verify
    chat_result = await db.execute(
        select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id)
    )
    chat = chat_result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Messages load করা
    msg_result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
    )
    messages = msg_result.scalars().all()

    return [
        {
            "id": m.id,
            "role": m.role.value,
            "content": m.content,
            "agent_type": m.agent_type.value if m.agent_type else "general",
            "created_at": m.created_at,
        }
        for m in messages
    ]


# ============================================
# Send Message (Main Chat Endpoint)
# ============================================
@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    AI কে message পাঠায় এবং response পায়।
    Agent selection supported।
    """
    start_time = time.time()

    # Chat session নেওয়া বা তৈরি করা
    if request.chat_id:
        chat_result = await db.execute(
            select(Chat).where(Chat.id == request.chat_id, Chat.user_id == user_id)
        )
        chat = chat_result.scalar_one_or_none()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
    else:
        # Auto title from first message
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        chat = Chat(user_id=user_id, title=title)
        db.add(chat)
        await db.flush()

    # User message save
    user_msg = Message(
        chat_id=chat.id,
        role=MessageRole.USER,
        content=request.message,
    )
    db.add(user_msg)

    # Chat history লোড করা (memory এর জন্য)
    history_result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat.id)
        .order_by(Message.created_at.desc())
        .limit(10)
    )
    history_messages = [
        {"role": m.role.value, "content": m.content}
        for m in reversed(history_result.scalars().all())
    ]

    # Agent অনুযায়ী response generate করা
    response_data = {}

    if request.agent == "tutor":
        response_data = await tutor_agent.teach(
            topic=request.message,
            difficulty_level="intermediate"
        )
        agent_type = AgentType.TUTOR

    elif request.agent == "planner":
        response_data = await planner_agent.create_plan(goal=request.message)
        agent_type = AgentType.PLANNER

    else:
        # General chat with memory
        response_data = await memory_agent.generate_with_memory(
            current_message=request.message,
            chat_history=history_messages,
            system_prompt=SYSTEM_PROMPT,
        )
        agent_type = AgentType.GENERAL

    # Response time calculate
    response_time_ms = int((time.time() - start_time) * 1000)

    # AI response save
    ai_msg = Message(
        chat_id=chat.id,
        role=MessageRole.ASSISTANT,
        content=response_data.get("content", "দুঃখিত, উত্তর দিতে পারছি না।"),
        agent_type=agent_type,
        model_used=response_data.get("provider", "unknown"),
        response_time_ms=response_time_ms,
    )
    db.add(ai_msg)

    # Analytics save
    analytics = Analytics(
        user_id=user_id,
        event_type="chat",
        agent_used=request.agent,
        model_used=response_data.get("provider", "unknown"),
        response_time_ms=response_time_ms,
        success=1,
    )
    db.add(analytics)

    await db.flush()

    return {
        "chat_id": chat.id,
        "message_id": ai_msg.id,
        "response": response_data.get("content", ""),
        "agent": request.agent,
        "provider": response_data.get("provider", "unknown"),
        "response_time_ms": response_time_ms,
    }


# ============================================
# Streaming Chat Endpoint
# ============================================
@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
):
    """
    Streaming chat - real-time token by token response।
    Server-Sent Events (SSE) format।
    """
    async def generate():
        try:
            async for token in llm_router.generate_stream(
                prompt=request.message,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.7,
            ):
                # SSE format এ পাঠানো
                yield f"data: {json.dumps({'token': token})}\n\n"

            # Stream শেষ হলে done signal
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


# ============================================
# AI Status Check
# ============================================
@router.get("/status")
async def get_ai_status(user_id: int = Depends(get_current_user_id)):
    """AI provider গুলোর status।"""
    status = await llm_router.get_status()
    return status
