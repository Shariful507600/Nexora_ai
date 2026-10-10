# ============================================
# NEXORA AI - Analytics Model
# ============================================

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Float, Text
from sqlalchemy.orm import relationship
from app.database.postgres_db import Base


class Analytics(Base):
    """
    Usage analytics - প্রতিটি AI interaction track করে।
    Dashboard এর জন্য data সংগ্রহ।
    """
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Event tracking
    event_type = Column(String(50), nullable=False)    # chat, rag, voice, upload
    agent_used = Column(String(50), nullable=True)     # general, tutor, planner
    model_used = Column(String(100), nullable=True)    # tinyllama, phi3, etc.

    # Performance metrics
    response_time_ms = Column(Integer, default=0)     # Response সময়
    tokens_used = Column(Integer, default=0)           # Token ব্যবহার
    success = Column(Integer, default=1)               # 1=success, 0=failed

    # Additional info
    metadata_json = Column(Text, nullable=True)        # Extra JSON data

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="analytics")

    def __repr__(self):
        return f"<Analytics(id={self.id}, event={self.event_type})>"
