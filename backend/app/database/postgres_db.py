# ============================================
# NEXORA AI - PostgreSQL Database Setup
# ============================================
# SQLAlchemy async engine দিয়ে PostgreSQL connection।
# Connection pooling এবং session management।

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.core.config import settings
from app.core.logger import logger


# ============================================
# Base Model Class
# ============================================
class Base(DeclarativeBase):
    """
    সব database model এই class থেকে inherit করবে।
    SQLAlchemy এর declarative base pattern।
    """
    pass


# ============================================
# Async Database Engine
# ============================================
# asyncpg driver দিয়ে async PostgreSQL connection
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,          # Debug mode এ SQL queries print হবে
    pool_size=10,                  # Connection pool এ ১০টি connection
    max_overflow=20,               # Extra ২০টি connection overflow এ
    pool_pre_ping=True,            # Connection alive কিনা check করে
    pool_recycle=3600,             # ১ ঘণ্টা পর connection refresh
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,       # Commit এর পর objects expire হবে না
    autocommit=False,
    autoflush=False,
)


# ============================================
# Database Session Dependency
# ============================================
async def get_db() -> AsyncSession:
    """
    FastAPI dependency injection এর জন্য।
    প্রতিটি API request এ নতুন session তৈরি হয়।
    Request শেষে automatically close হয়।
    
    ব্যবহার: async def route(db: AsyncSession = Depends(get_db))
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


# ============================================
# Database Initialization
# ============================================
async def init_db():
    """
    App startup এ database tables তৈরি করে।
    যদি tables আগে থেকেই থাকে, skip করে।
    """
    try:
        async with engine.begin() as conn:
            # সব models import করতে হবে যাতে Base.metadata তে থাকে
            from app.models.user import User
            from app.models.chat import Chat, Message
            from app.models.document import Document
            from app.models.analytics import Analytics

            # Tables তৈরি করা
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables created/verified successfully")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def check_db_connection():
    """
    Database connection সঠিকভাবে কাজ করছে কিনা যাচাই করে।
    Health check endpoint এ ব্যবহার হয়।
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
