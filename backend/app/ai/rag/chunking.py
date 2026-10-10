# ============================================
# NEXORA AI - Text Chunking Strategy
# ============================================
# Document কে ছোট ছোট chunks এ ভাগ করা।
# RAG এর সবচেয়ে গুরুত্বপূর্ণ অংশ।
# Chunk size এবং overlap সঠিক হলে
# retrieval accuracy অনেক বাড়ে।

from typing import List, Dict
from app.core.logger import logger


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    doc_id: str = None,
    source: str = None,
) -> List[Dict]:
    """
    Text কে overlapping chunks এ ভাগ করে।
    
    Parameters:
        text: সম্পূর্ণ document text
        chunk_size: প্রতিটি chunk এ সর্বোচ্চ কতটি শব্দ
        chunk_overlap: পরপর দুটি chunk এ কতটি শব্দ মিলবে
        doc_id: Document এর unique ID
        source: Document এর নাম/path
    
    Returns: List of chunk dictionaries
    
    কেন overlap দরকার?
    → Context boundary তে information হারিয়ে যায়।
    → Overlap থাকলে সেই information ধরা পড়ে।
    """
    if not text or not text.strip():
        return []

    # শব্দ দিয়ে split করা (character নয়)
    words = text.split()
    chunks = []
    chunk_index = 0
    start = 0

    while start < len(words):
        # এই chunk এর শেষ position
        end = start + chunk_size

        # Chunk এর words নেওয়া
        chunk_words = words[start:end]
        chunk_text_content = " ".join(chunk_words)

        # Chunk metadata সহ তৈরি করা
        chunk = {
            "id": f"{doc_id}_{chunk_index}" if doc_id else f"chunk_{chunk_index}",
            "text": chunk_text_content,
            "chunk_index": chunk_index,
            "word_count": len(chunk_words),
            "char_count": len(chunk_text_content),
            "metadata": {
                "doc_id": doc_id,
                "source": source or "unknown",
                "chunk_index": chunk_index,
                "start_word": start,
                "end_word": min(end, len(words)),
            }
        }

        chunks.append(chunk)
        chunk_index += 1

        # Next chunk এর শুরু (overlap দিয়ে)
        start = end - chunk_overlap

        # যদি remaining words খুব কম হয়, loop বন্ধ
        if start >= len(words) or (len(words) - start) < 10:
            break

    logger.info(f"📄 Text chunked into {len(chunks)} chunks "
                f"(size={chunk_size}, overlap={chunk_overlap})")

    return chunks


def chunk_by_paragraph(
    text: str,
    max_chunk_size: int = 800,
    doc_id: str = None,
    source: str = None,
) -> List[Dict]:
    """
    Paragraph অনুযায়ী chunk করা।
    Natural boundaries respect করে - আরো contextual।
    
    ভালো works করে যখন:
    - Document ভালোভাবে formatted
    - Clear paragraph structure আছে
    """
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []
    current_chunk = []
    current_size = 0
    chunk_index = 0

    for para in paragraphs:
        para_words = len(para.split())

        # Paragraph বড় হলে force break
        if para_words > max_chunk_size:
            # আগের chunk save করা
            if current_chunk:
                chunks.append(_build_chunk(
                    " ".join(current_chunk), chunk_index, doc_id, source
                ))
                chunk_index += 1
                current_chunk = []
                current_size = 0

            # বড় paragraph কে fixed size chunks এ ভাগ করা
            sub_chunks = chunk_text(para, max_chunk_size, 30, doc_id, source)
            chunks.extend(sub_chunks)
            chunk_index += len(sub_chunks)
            continue

        # Current chunk এ para যোগ করা যাবে কিনা
        if current_size + para_words > max_chunk_size and current_chunk:
            chunks.append(_build_chunk(
                " ".join(current_chunk), chunk_index, doc_id, source
            ))
            chunk_index += 1
            current_chunk = []
            current_size = 0

        current_chunk.append(para)
        current_size += para_words

    # শেষ chunk
    if current_chunk:
        chunks.append(_build_chunk(
            " ".join(current_chunk), chunk_index, doc_id, source
        ))

    return chunks


def _build_chunk(text: str, index: int, doc_id: str, source: str) -> Dict:
    """Helper - chunk dictionary তৈরি করে।"""
    return {
        "id": f"{doc_id}_{index}" if doc_id else f"chunk_{index}",
        "text": text,
        "chunk_index": index,
        "word_count": len(text.split()),
        "char_count": len(text),
        "metadata": {
            "doc_id": doc_id,
            "source": source or "unknown",
            "chunk_index": index,
        }
    }
