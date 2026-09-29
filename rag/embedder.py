"""
embedder.py
Generates vector embeddings using Google Gemini's embedding API.
- Zero local RAM usage (API call, no model loaded into server memory)
- Uses gemini-embedding-001 model with output_dimensionality=768
- Supports batch embedding
"""

import os
import time
from typing import List
from google import genai
from google.genai import types

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM   = 768

_client = None


def _get_client():
    global _client
    if _client is None:
        from rag.gemini_client import get_api_key
        api_key = get_api_key()
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set.")
        _client = genai.Client(api_key=api_key)
    return _client


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of texts using Gemini gemini-embedding-001 (768 dim).
    Batches automatically.
    """
    client = _get_client()
    results = []
    batch_size = 20

    for i in range(0, len(texts), batch_size):
        batch = texts[i: i + batch_size]
        for attempt in range(3):
            try:
                response = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT",
                        output_dimensionality=EMBEDDING_DIM,
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
    Embed a single query string using Gemini gemini-embedding-001 (768 dim).
    """
    client = _get_client()
    for attempt in range(3):
        try:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=[query],
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY",
                    output_dimensionality=EMBEDDING_DIM,
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
