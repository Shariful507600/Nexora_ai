# ============================================
# NEXORA AI - Analytics Routes
# ============================================
# Dashboard এর জন্য usage statistics।

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta

from app.database.postgres_db import get_db
from app.models.analytics import Analytics
from app.models.chat import Chat, Message
from app.models.document import Document
from app.ai.rag.vector_store import get_collection_stats
from app.core.security import get_current_user_id

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard_stats(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Dashboard এর জন্য সব statistics একসাথে পায়।
    KPI cards ও charts এর data।
    """
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Total chats
    total_chats = await db.scalar(
        select(func.count(Chat.id)).where(Chat.user_id == user_id)
    ) or 0

    # Total messages
    total_messages = await db.scalar(
        select(func.count(Message.id))
        .join(Chat)
        .where(Chat.user_id == user_id)
    ) or 0

    # Total documents
    total_docs = await db.scalar(
        select(func.count(Document.id)).where(Document.user_id == user_id)
    ) or 0

    # This week's activity
    week_activity = await db.scalar(
        select(func.count(Analytics.id))
        .where(Analytics.user_id == user_id, Analytics.created_at >= week_ago)
    ) or 0

    # Daily activity for chart (last 7 days)
    daily_data = []
    for i in range(6, -1, -1):
        day_start = now - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        count = await db.scalar(
            select(func.count(Analytics.id)).where(
                Analytics.user_id == user_id,
                Analytics.created_at >= day_start,
                Analytics.created_at < day_end,
            )
        ) or 0

        daily_data.append({
            "date": day_start.strftime("%b %d"),
            "count": count
        })

    # Agent usage breakdown
    agent_stats_result = await db.execute(
        select(Analytics.agent_used, func.count(Analytics.id))
        .where(Analytics.user_id == user_id, Analytics.agent_used != None)
        .group_by(Analytics.agent_used)
    )
    agent_stats = {row[0]: row[1] for row in agent_stats_result.fetchall()}

    # Vector store stats
    vector_stats = get_collection_stats()

    # Average response time
    avg_response = await db.scalar(
        select(func.avg(Analytics.response_time_ms))
        .where(Analytics.user_id == user_id, Analytics.response_time_ms > 0)
    ) or 0

    return {
        "kpis": {
            "total_chats": total_chats,
            "total_messages": total_messages,
            "total_documents": total_docs,
            "week_activity": week_activity,
            "avg_response_ms": round(avg_response),
            "total_chunks": vector_stats.get("total_chunks", 0),
        },
        "charts": {
            "daily_activity": daily_data,
            "agent_usage": agent_stats,
        }
    }
