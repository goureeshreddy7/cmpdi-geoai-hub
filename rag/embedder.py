"""
embedder.py
Generates vector embeddings using Google Gemini's text-embedding API.
- Zero local RAM usage (API call, no model loaded)
- Uses text-embedding-004 model (768-dim, production quality)
- Batch support for efficient indexing
"""

import os
import time
from typing import List
from google import genai
from google.genai import types

EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIM   = 768

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set.")
        _client = genai.Client(api_key=api_key)
    return _client


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of texts using Gemini text-embedding-004.
    Batches automatically to respect API limits.
    """
    client = _get_client()
    results = []
    batch_size = 20  # Gemini allows up to 100, keep conservative

    for i in range(0, len(texts), batch_size):
        batch = texts[i: i + batch_size]
        for attempt in range(3):
            try:
                response = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT",
                    ),
                )
                for emb in response.embeddings:
                    results.append(emb.values)
                break
            except Exception as e:
                err = str(e).lower()
                if "429" in err or "resource_exhausted" in err:
                    time.sleep((attempt + 1) * 2)
                    continue
                raise
    return results


def embed_query(query: str) -> List[float]:
    """
    Embed a single query string using Gemini text-embedding-004.
    Uses RETRIEVAL_QUERY task type for better search accuracy.
    """
    client = _get_client()
    for attempt in range(3):
        try:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=[query],
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY",
                ),
            )
            return response.embeddings[0].values
        except Exception as e:
            err = str(e).lower()
            if "429" in err or "resource_exhausted" in err:
                time.sleep((attempt + 1) * 2)
                continue
            raise
    raise RuntimeError("Gemini embedding failed after retries.")
