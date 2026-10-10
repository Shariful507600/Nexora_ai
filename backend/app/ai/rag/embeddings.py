# ============================================
# NEXORA AI - Embeddings Service
# ============================================
# Sentence Transformers দিয়ে text embeddings তৈরি।
# Embeddings হলো text এর numerical representation।
# Similar text এর embeddings কাছাকাছি থাকে।
# এটাই RAG এর semantic search এর মূল।

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.core.logger import logger

# Global model instance - একবার load হয়, বারবার ব্যবহার হয়
_embedding_model = None

# Lightweight model - low-end laptop এ চলে
# all-MiniLM-L6-v2: ~80MB, fast, accurate
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def get_embedding_model() -> SentenceTransformer:
    """
    Embedding model এর singleton instance।
    প্রথমবার call হলে model download + load হয়।
    পরের বার cached version ব্যবহার হয়।
    """
    global _embedding_model

    if _embedding_model is None:
        logger.info(f"📥 Loading embedding model: {EMBEDDING_MODEL_NAME}")
        logger.info("প্রথমবার ~80MB download হবে, একটু সময় লাগবে...")

        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

        logger.info("✅ Embedding model loaded successfully")

    return _embedding_model


def generate_embedding(text: str) -> List[float]:
    """
    Single text এর embedding vector তৈরি করে।
    
    Parameters:
        text: যে text এর embedding চাই
    
    Returns:
        384-dimensional float vector (list)
    
    উদাহরণ:
        "AI is amazing" → [0.12, -0.34, 0.56, ...]
    """
    if not text or not text.strip():
        # Empty text এর জন্য zero vector
        return [0.0] * 384

    try:
        model = get_embedding_model()

        # Text too long হলে truncate করা
        if len(text) > 512:
            text = text[:512]

        # Embedding generate করা
        embedding = model.encode(text, convert_to_numpy=True)

        # numpy array → Python list
        return embedding.tolist()

    except Exception as e:
        logger.error(f"❌ Embedding generation error: {e}")
        return [0.0] * 384


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Multiple texts এর embeddings একসাথে তৈরি করে।
    Batch processing - অনেক বেশি efficient।
    
    Large document এর সব chunks একসাথে process করতে ব্যবহার হয়।
    """
    if not texts:
        return []

    try:
        model = get_embedding_model()

        # Texts truncate করা
        truncated_texts = [t[:512] if len(t) > 512 else t for t in texts]

        # Batch encoding - GPU থাকলে automatically use করে
        embeddings = model.encode(
            truncated_texts,
            batch_size=32,              # ৩২টি করে batch এ process
            show_progress_bar=len(texts) > 50,  # বড় batch এ progress দেখায়
            convert_to_numpy=True,
        )

        logger.info(f"✅ Generated {len(embeddings)} embeddings")

        # numpy arrays → Python lists
        return [emb.tolist() for emb in embeddings]

    except Exception as e:
        logger.error(f"❌ Batch embedding error: {e}")
        return [[0.0] * 384 for _ in texts]


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    দুটি embedding vector এর মধ্যে similarity calculate করে।
    1.0 = identical, 0.0 = completely different
    RAG retrieval এ কোন documents সবচেয়ে relevant তা বের করতে ব্যবহার।
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    dot_product = np.dot(v1, v2)
    magnitude = np.linalg.norm(v1) * np.linalg.norm(v2)

    if magnitude == 0:
        return 0.0

    return float(dot_product / magnitude)
