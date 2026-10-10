# ============================================
# NEXORA AI - RAG Routes
# ============================================
# PDF upload, processing, Q&A endpoints।

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
from datetime import datetime

from app.database.postgres_db import get_db
from app.models.document import Document
from app.models.analytics import Analytics
from app.ai.rag.retriever import retrieve_and_generate
from app.ai.rag.chunking import chunk_by_paragraph
from app.ai.rag.vector_store import store_document_chunks, delete_document_chunks
from app.utils.pdf_reader import extract_text_from_pdf
from app.core.security import get_current_user_id
from app.core.config import settings
from app.core.logger import logger

router = APIRouter(prefix="/api/rag", tags=["RAG - Document Q&A"])

# Upload directory তৈরি করা
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


# ============================================
# Upload PDF
# ============================================
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    PDF ফাইল upload করে এবং RAG এর জন্য process করে।
    
    Steps:
    1. File save করো
    2. Text extract করো
    3. Chunks তৈরি করো
    4. Embeddings generate করো
    5. ChromaDB তে store করো
    6. PostgreSQL এ metadata save করো
    """
    # File type validation
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="শুধুমাত্র PDF ফাইল upload করা যাবে।")

    # File size check
    file_content = await file.read()
    file_size = len(file_content)
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"ফাইলের আকার {settings.MAX_FILE_SIZE_MB}MB এর বেশি হওয়া যাবে না।"
        )

    # Unique filename তৈরি করা
    file_uuid = str(uuid.uuid4())
    saved_filename = f"{file_uuid}.pdf"
    file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)

    # File disk এ save করা
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Database এ document record তৈরি করা
    document = Document(
        user_id=user_id,
        filename=saved_filename,
        original_name=file.filename,
        file_size=file_size,
        file_path=file_path,
        description=description,
        is_processed=False,
    )
    db.add(document)
    await db.flush()
    doc_id = str(document.id)

    try:
        # PDF থেকে text extract করা
        logger.info(f"📄 Extracting text from: {file.filename}")
        pdf_data = extract_text_from_pdf(file_path)

        if not pdf_data["full_text"]:
            raise HTTPException(status_code=400, detail="PDF থেকে text extract করা যায়নি।")

        # Text কে chunks এ ভাগ করা
        logger.info(f"✂️ Chunking document: {file.filename}")
        chunks = chunk_by_paragraph(
            text=pdf_data["full_text"],
            max_chunk_size=500,
            doc_id=doc_id,
            source=file.filename,
        )

        # ChromaDB তে embeddings store করা
        logger.info(f"🔢 Storing {len(chunks)} chunks in vector store...")
        success = store_document_chunks(chunks, doc_id)

        if not success:
            raise Exception("Vector store এ save করা যায়নি।")

        # Document record update করা
        document.is_processed = True
        document.chunk_count = len(chunks)
        document.page_count = pdf_data["total_pages"]
        document.word_count = pdf_data["word_count"]
        document.processed_at = datetime.utcnow()

        # Analytics log
        db.add(Analytics(
            user_id=user_id,
            event_type="upload",
            model_used="embedding",
            success=1,
        ))

        logger.info(f"✅ Document processed: {file.filename} - {len(chunks)} chunks")

        return {
            "document_id": document.id,
            "filename": file.filename,
            "pages": pdf_data["total_pages"],
            "words": pdf_data["word_count"],
            "chunks": len(chunks),
            "status": "processed",
            "message": f"Document successfully processed! {len(chunks)} chunks created."
        }

    except Exception as e:
        # Error হলে document mark করা
        document.is_processed = False
        logger.error(f"❌ Document processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# ============================================
# Ask Question from Documents (RAG)
# ============================================
class RAGQueryRequest(BaseModel):
    question: str
    doc_ids: Optional[List[int]] = None    # Specific docs, None = all
    top_k: int = 5


@router.post("/query")
async def query_documents(
    request: RAGQueryRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Uploaded documents থেকে প্রশ্নের উত্তর দেয়।
    RAG (Retrieval-Augmented Generation) ব্যবহার করে।
    """
    # User এর documents check করা
    doc_query = select(Document).where(
        Document.user_id == user_id,
        Document.is_processed == True
    )

    if request.doc_ids:
        doc_query = doc_query.where(Document.id.in_(request.doc_ids))

    result = await db.execute(doc_query)
    documents = result.scalars().all()

    if not documents:
        raise HTTPException(
            status_code=404,
            detail="কোনো processed document পাওয়া যায়নি। আগে PDF upload করুন।"
        )

    # String doc_ids তৈরি করা
    doc_id_strings = [str(doc.id) for doc in documents]

    # RAG pipeline চালানো
    rag_result = await retrieve_and_generate(
        query=request.question,
        doc_ids=doc_id_strings,
        top_k=request.top_k,
    )

    # Analytics log
    db.add(Analytics(
        user_id=user_id,
        event_type="rag",
        model_used=rag_result.get("provider", "unknown"),
        success=1,
    ))

    return {
        "question": request.question,
        "answer": rag_result["answer"],
        "sources": rag_result["sources"],
        "chunks_used": rag_result["chunks_used"],
        "provider": rag_result["provider"],
        "documents_searched": len(documents),
    }


# ============================================
# Get User Documents
# ============================================
@router.get("/documents")
async def get_documents(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """User এর সব uploaded documents পায়।"""
    result = await db.execute(
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
    )
    documents = result.scalars().all()

    return [
        {
            "id": d.id,
            "filename": d.original_name,
            "file_size": d.file_size,
            "is_processed": d.is_processed,
            "chunk_count": d.chunk_count,
            "page_count": d.page_count,
            "word_count": d.word_count,
            "created_at": d.created_at,
        }
        for d in documents
    ]


# ============================================
# Delete Document
# ============================================
@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Document delete করে (file + embeddings + DB record)।"""
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.user_id == user_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # ChromaDB থেকে embeddings delete
    delete_document_chunks(str(doc_id))

    # File disk থেকে delete
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # DB থেকে delete
    await db.delete(document)

    return {"message": "Document successfully deleted"}
