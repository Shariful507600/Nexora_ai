# ============================================
# NEXORA AI - Vector Store Operations
# ============================================
# ChromaDB তে documents store ও retrieve করা।
# Embeddings সংরক্ষণ এবং semantic search।

from typing import List, Dict, Optional
from app.database.chroma_db import get_or_create_collection
from app.ai.rag.embeddings import generate_embeddings_batch, generate_embedding
from app.core.logger import logger


def store_document_chunks(
    chunks: List[Dict],
    doc_id: str,
    collection_name: Optional[str] = None
) -> bool:
    """
    Document chunks ChromaDB তে store করে।
    
    Parameters:
        chunks: chunk_text() থেকে পাওয়া chunks
        doc_id: Document এর unique identifier
        collection_name: কোন collection এ store করবে
    
    Returns:
        True if successful, False otherwise
    """
    if not chunks:
        logger.warning("No chunks to store")
        return False

    try:
        collection = get_or_create_collection(collection_name)

        # সব chunk এর text বের করা
        texts = [chunk["text"] for chunk in chunks]

        # Batch embeddings generate করা (efficient)
        logger.info(f"🔢 Generating embeddings for {len(texts)} chunks...")
        embeddings = generate_embeddings_batch(texts)

        # ChromaDB এ add করার জন্য data prepare করা
        ids = [chunk["id"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]

        # Batch এ store করা
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            batch_documents = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]

            collection.add(
                ids=batch_ids,
                embeddings=batch_embeddings,
                documents=batch_documents,
                metadatas=batch_metadatas
            )

        logger.info(f"✅ Stored {len(chunks)} chunks for doc_id: {doc_id}")
        return True

    except Exception as e:
        logger.error(f"❌ Vector store error: {e}")
        return False


def search_similar_chunks(
    query: str,
    top_k: int = 5,
    doc_ids: Optional[List[str]] = None,
    collection_name: Optional[str] = None
) -> List[Dict]:
    """
    Query এর সাথে সবচেয়ে similar chunks খোঁজে।
    এটাই RAG এর Retrieval অংশ।
    
    Parameters:
        query: User এর প্রশ্ন
        top_k: কতটি similar chunk চাই
        doc_ids: শুধু নির্দিষ্ট documents থেকে search করতে
    
    Returns:
        List of similar chunks with similarity scores
    """
    try:
        collection = get_or_create_collection(collection_name)

        # Query এর embedding তৈরি করা
        query_embedding = generate_embedding(query)

        # ChromaDB query parameters
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, collection.count() or 1),
            "include": ["documents", "metadatas", "distances"]
        }

        # Specific documents থেকে filter করা
        if doc_ids:
            query_params["where"] = {"doc_id": {"$in": doc_ids}}

        # Semantic search execute করা
        results = collection.query(**query_params)

        # Results format করা
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, (doc, metadata, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                # Distance → Similarity score (0-1 range)
                similarity = 1 - distance

                formatted_results.append({
                    "text": doc,
                    "metadata": metadata,
                    "similarity": round(similarity, 4),
                    "rank": i + 1
                })

        logger.info(f"🔍 Found {len(formatted_results)} relevant chunks for query")
        return formatted_results

    except Exception as e:
        logger.error(f"❌ Vector search error: {e}")
        return []


def delete_document_chunks(doc_id: str, collection_name: Optional[str] = None) -> bool:
    """
    Document এর সব chunks ChromaDB থেকে মুছে ফেলে।
    Document delete করার সময় ব্যবহার হয়।
    """
    try:
        collection = get_or_create_collection(collection_name)

        # doc_id দিয়ে সব chunks delete করা
        collection.delete(where={"doc_id": doc_id})

        logger.info(f"🗑️ Deleted chunks for doc_id: {doc_id}")
        return True

    except Exception as e:
        logger.error(f"❌ Delete chunks error: {e}")
        return False


def get_collection_stats(collection_name: Optional[str] = None) -> Dict:
    """
    Collection এর statistics বের করে।
    Dashboard এ দেখানোর জন্য।
    """
    try:
        collection = get_or_create_collection(collection_name)
        count = collection.count()

        return {
            "total_chunks": count,
            "collection_name": collection.name,
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"total_chunks": 0, "collection_name": "unknown"}
