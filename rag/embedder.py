"""
embedder.py
Generates dense vector embeddings for text using
sentence-transformers (all-MiniLM-L6-v2) — runs fully locally, no API cost.
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

# Load model once at module level (cached after first load)
_MODEL_NAME = "all-MiniLM-L6-v2"
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text strings.

    Args:
        texts: List of strings to embed.

    Returns:
        List of embedding vectors (each a list of floats).
    """
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """
    Generate an embedding for a single query string.

    Args:
        query: The question or search string.

    Returns:
        Embedding vector as list of floats.
    """
    model = _get_model()
    embedding = model.encode([query], normalize_embeddings=True)
    return embedding[0].tolist()
