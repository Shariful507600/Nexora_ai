# ============================================
# NEXORA AI - Main Application Entry Point
# ============================================
# FastAPI app তৈরি, middleware, routes সব এখানে।

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logger import logger
from app.database.postgres_db import init_db, check_db_connection
from app.database.chroma_db import init_chroma

# Routes import
from app.api.auth_routes import router as auth_router
from app.api.ai_routes import router as ai_router
from app.api.rag_routes import router as rag_router
from app.api.voice_routes import router as voice_router
from app.api.analytics_routes import router as analytics_router


# ============================================
# Application Lifecycle
# ============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    App startup ও shutdown এর lifecycle management।
    Startup: DB init, ChromaDB init, model pre-load।
    Shutdown: Clean resource release।
    """
    # ===== STARTUP =====
    logger.info("=" * 50)
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 50)

    # Uploads directory তৈরি
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # PostgreSQL initialize
    logger.info("📦 Initializing PostgreSQL...")
    try:
        await init_db()
        db_ok = await check_db_connection()
        if db_ok:
            logger.info("✅ PostgreSQL connected")
        else:
            logger.error("❌ PostgreSQL connection failed")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        logger.warning("⚠️ Continuing without database...")

    # ChromaDB initialize
    logger.info("🗄️ Initializing ChromaDB...")
    try:
        chroma_ok = init_chroma()
        if chroma_ok:
            logger.info("✅ ChromaDB ready")
    except Exception as e:
        logger.error(f"❌ ChromaDB error: {e}")

    logger.info("✅ NEXORA AI is ready!")
    logger.info(f"📍 API Docs: http://localhost:8000/docs")
    logger.info("=" * 50)

    yield  # App running...

    # ===== SHUTDOWN =====
    logger.info("🛑 Shutting down NEXORA AI...")


# ============================================
# FastAPI App Instance
# ============================================
app = FastAPI(
    title="NEXORA AI",
    description="""
    ## NEXORA AI - Knowledge & Productivity Copilot
    
    **Features:**
    - 🤖 AI Chat with multiple agents
    - 📄 RAG - Ask questions from your PDF documents
    - 🎙️ Voice input/output
    - 📊 Usage analytics dashboard
    - 🔐 JWT Authentication
    
    **AI Agents:**
    - General Assistant
    - Tutor Agent (Educational)
    - Planner Agent (Productivity)
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# ============================================
# CORS Middleware
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Register All Routes
# ============================================
app.include_router(auth_router)
app.include_router(ai_router)
app.include_router(rag_router)
app.include_router(voice_router)
app.include_router(analytics_router)


# ============================================
# Root & Health Check
# ============================================
@app.get("/", tags=["Health"])
async def root():
    """API root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "message": "Welcome to NEXORA AI API! 🚀"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    System health check।
    Database, ChromaDB, Ollama status।
    """
    from app.database.postgres_db import check_db_connection
    from app.ai.llm.ollama_service import ollama_service

    db_status = await check_db_connection()
    ollama_status = await ollama_service.is_available()

    overall = "healthy" if db_status else "degraded"

    return {
        "status": overall,
        "services": {
            "database": "connected" if db_status else "disconnected",
            "ollama": "running" if ollama_status else "not running",
            "chromadb": "ready",
        },
        "version": settings.APP_VERSION,
    }


# ============================================
# Run Server (Direct execution)
# ============================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,          # Development mode - auto reload
        log_level="info",
    )
