# ============================================
# NEXORA AI - Document Model
# ============================================

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func, Float
from sqlalchemy.orm import relationship
from app.database.postgres_db import Base


class Document(Base):
    """
    Uploaded document - PDF ফাইলের তথ্য।
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # File information
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_size = Column(Integer, default=0)               # bytes
    file_path = Column(String(500), nullable=False)

    # Processing status
    is_processed = Column(Boolean, default=False)        # Embedding তৈরি হয়েছে কিনা
    chunk_count = Column(Integer, default=0)             # কতটি chunk তৈরি হয়েছে
    page_count = Column(Integer, default=0)              # PDF এর page সংখ্যা
    word_count = Column(Integer, default=0)

    # ChromaDB reference
    collection_id = Column(String(255), nullable=True)   # ChromaDB collection reference

    # Metadata
    description = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)            # Comma separated tags

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename})>"
