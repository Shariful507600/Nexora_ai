# ============================================
# NEXORA AI - ChromaDB Vector Store Setup
# ============================================
# ChromaDB হলো vector database যেখানে
# document embeddings সংরক্ষণ করা হয়।
# RAG system এর মূল ভিত্তি।

import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.core.logger import logger

# Global ChromaDB client instance
_chroma_client = None
_collection = None


def get_chroma_client():
    """
    ChromaDB client এর singleton instance।
    একবার তৈরি হলে পুনরায় ব্যবহার করা হয়।
    """
    global _chroma_client

    if _chroma_client is None:
        try:
            # Local persistent ChromaDB - disk এ data সংরক্ষণ করে
            _chroma_client = chromadb.PersistentClient(
                path="./chroma_data",
                settings=ChromaSettings(
                    anonymized_telemetry=False,  # Telemetry বন্ধ
                    allow_reset=True,
                )
            )
            logger.info("✅ ChromaDB client initialized")
        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {e}")
            raise

    return _chroma_client


def get_or_create_collection(collection_name: str = None):
    """
    ChromaDB collection পায় অথবা নতুন তৈরি করে।
    Collection হলো vector database এর table এর মতো।
    """
    global _collection

    name = collection_name or settings.CHROMA_COLLECTION

    try:
        client = get_chroma_client()

        # Collection থাকলে পায়, না থাকলে তৈরি করে
        _collection = client.get_or_create_collection(
            name=name,
            metadata={
                "hnsw:space": "cosine",     # Cosine similarity ব্যবহার করে
                "description": "NEXORA AI document embeddings"
            }
        )

        logger.info(f"✅ ChromaDB collection '{name}' ready")
        return _collection

    except Exception as e:
        logger.error(f"❌ ChromaDB collection error: {e}")
        raise


def reset_collection(collection_name: str = None):
    """
    Collection এর সব data মুছে ফেলে।
    Testing বা reset এর জন্য ব্যবহার হয়।
    """
    name = collection_name or settings.CHROMA_COLLECTION
    client = get_chroma_client()

    try:
        client.delete_collection(name)
        logger.info(f"🗑️ Collection '{name}' deleted")
        return get_or_create_collection(name)
    except Exception as e:
        logger.error(f"❌ Reset collection error: {e}")
        raise


# App startup এ collection initialize করা
def init_chroma():
    """
    Application startup এ ChromaDB initialize করে।
    main.py থেকে call করা হয়।
    """
    try:
        collection = get_or_create_collection()
        count = collection.count()
        logger.info(f"✅ ChromaDB ready - {count} documents in collection")
        return True
    except Exception as e:
        logger.error(f"❌ ChromaDB init failed: {e}")
        return False
