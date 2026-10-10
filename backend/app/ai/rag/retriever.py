# ============================================
# NEXORA AI - RAG Retriever
# ============================================
# Retrieval-Augmented Generation এর মূল logic।
# 1. Query দিয়ে relevant chunks খোঁজো
# 2. Chunks কে context হিসেবে LLM কে দাও
# 3. Context-aware response তৈরি করো

from typing import List, Dict, Optional
from app.ai.rag.vector_store import search_similar_chunks
from app.ai.llm.router import llm_router
from app.core.logger import logger


# =====================================================================
# NEXORA AI - Custom RAG System Prompt Template
# =====================================================================
# এই প্রম্পটটি লোকাল মডেলের হ্যালুসিনেশন ও মনগড়া তথ্য দেওয়া সম্পূর্ণ বন্ধ করবে।

RAG_PROMPT_TEMPLATE = """You are NEXORA AI, an intelligent AI Knowledge & Productivity Copilot.

Answer the user's question using ONLY the provided context documents.

## Context Documents:
{context}

## User Question:
{question}

## Instructions:
- Strictly use ONLY the information available in the context.
- Do NOT add assumptions, external knowledge, or hallucinated information.
- If the answer is not explicitly found in the context, respond exactly:
  "এই তথ্য আপলোড করা document এ পাওয়া যাচ্ছে না।"
- Keep the answer concise, factual, and professional.
- Mention relevant document sections, headings, or snippets when possible.
- Support both Bengali and English responses.
- If multiple documents contain relevant information, combine them clearly.
- Preserve numerical values, dates, and names exactly as written in the documents.

## Answer:
"""


async def retrieve_and_generate(
    query: str,
    doc_ids: Optional[List[str]] = None,
    top_k: int = 5,
    min_similarity: float = 0.3,
) -> Dict:
    """
    RAG pipeline - retrieve করো, তারপর generate করো।
    
    Parameters:
        query: User এর প্রশ্ন
        doc_ids: কোন documents থেকে search করবে
        top_k: কতটি chunks retrieve করবে
        min_similarity: Minimum similarity threshold
    
    Returns:
        {
            "answer": str,          # AI এর উত্তর
            "sources": List[Dict],  # ব্যবহৃত sources
            "chunks_used": int,     # কতটি chunk ব্যবহার হয়েছে
            "provider": str         # কোন AI ব্যবহার হয়েছে
        }
    """
    logger.info(f"🔍 RAG Query: {query[:100]}...")

    # Step 1: Relevant chunks retrieve করা
    similar_chunks = search_similar_chunks(
        query=query,
        top_k=top_k,
        doc_ids=doc_ids
    )

    # Minimum similarity দিয়ে filter করা
    relevant_chunks = [
        chunk for chunk in similar_chunks
        if chunk["similarity"] >= min_similarity
    ]

    if not relevant_chunks:
        return {
            "answer": "আপলোড করা documents এ এই প্রশ্নের সাথে প্রাসঙ্গিক তথ্য পাওয়া যায়নি। "
                     "অনুগ্রহ করে সংশ্লিষ্ট document আপলোড করুন।",
            "sources": [],
            "chunks_used": 0,
            "provider": "none"
        }

    # Step 2: Context তৈরি করা
    context_parts = []
    for i, chunk in enumerate(relevant_chunks[:3]):   # Top 3 chunks নেওয়া
        source = chunk["metadata"].get("source", "Document")
        context_parts.append(
            f"[Source {i+1} - {source}]:\n{chunk['text']}"
        )

    context = "\n\n---\n\n".join(context_parts)

    # Step 3: RAG prompt তৈরি করা
    rag_prompt = RAG_PROMPT_TEMPLATE.format(
        context=context,
        question=query
    )

    # Step 4: LLM দিয়ে answer generate করা
    result = await llm_router.generate(
        prompt=rag_prompt,
        temperature=0.3,    # Lower temperature - more factual
        max_tokens=600,
    )

    # Sources format করা
    sources = []
    for chunk in relevant_chunks[:3]:
        sources.append({
            "source": chunk["metadata"].get("source", "Unknown"),
            "doc_id": chunk["metadata"].get("doc_id", ""),
            "similarity": chunk["similarity"],
            "text_preview": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"]
        })

    logger.info(f"✅ RAG complete: used {len(relevant_chunks)} chunks")

    return {
        "answer": result["content"],
        "sources": sources,
        "chunks_used": len(relevant_chunks),
        "provider": result["provider"]
    }
