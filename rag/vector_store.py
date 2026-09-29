"""
vector_store.py
Manages ChromaDB — supports subsidiary tagging and filtered search.
"""

import chromadb
from typing import List, Dict, Optional
from rag.embedder import embed_texts, embed_query

CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "pdf_chunks"

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    if _collection is None:
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine", "hnsw:M": 16},
        )
    return _collection


def add_chunks(chunks: List[Dict], subsidiary: str = "General") -> int:
    """Embed and store chunks with subsidiary metadata."""
    collection = _get_collection()

    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [{
        "page": c["page"],
        "source": c["source"],
        "subsidiary": subsidiary,
    } for c in chunks]

    existing = set(collection.get(ids=ids)["ids"])
    new_chunks = [(t, i, m) for t, i, m in zip(texts, ids, metadatas) if i not in existing]

    if not new_chunks:
        return 0

    new_texts, new_ids, new_metadatas = zip(*new_chunks)
    embeddings = embed_texts(list(new_texts))
    collection.add(
        documents=list(new_texts),
        embeddings=embeddings,
        ids=list(new_ids),
        metadatas=list(new_metadatas),
    )
    return len(new_ids)


def similarity_search(query: str, top_k: int = 5, subsidiary: Optional[str] = None) -> List[Dict]:
    """Find relevant chunks. Optionally filter by subsidiary."""
    collection = _get_collection()
    if collection.count() == 0:
        return []

    query_embedding = embed_query(query)

    where = {"subsidiary": subsidiary} if subsidiary and subsidiary != "All" else None

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
            where=where,
        )
    except Exception:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append({
            "text": doc,
            "source": meta.get("source", "Unknown"),
            "page": meta.get("page", "?"),
            "subsidiary": meta.get("subsidiary", "General"),
            "score": round(1 - dist, 4),
        })
    return output


def get_indexed_sources() -> List[str]:
    """Return unique source filenames."""
    collection = _get_collection()
    if collection.count() == 0:
        return []
    results = collection.get(include=["metadatas"])
    return sorted({m["source"] for m in results["metadatas"]})


def get_all_documents() -> List[Dict]:
    """Return all documents with metadata (source, subsidiary, page count)."""
    collection = _get_collection()
    if collection.count() == 0:
        return []
    results = collection.get(include=["metadatas", "documents"])
    seen = {}
    for meta, doc in zip(results["metadatas"], results["documents"]):
        src = meta.get("source", "Unknown")
        if src not in seen:
            seen[src] = {
                "source": src,
                "subsidiary": meta.get("subsidiary", "General"),
                "chunks": 0,
                "preview": doc[:300],
            }
        seen[src]["chunks"] += 1
    return list(seen.values())


def get_stats_by_subsidiary() -> Dict:
    """Return chunk count broken down by subsidiary."""
    collection = _get_collection()
    if collection.count() == 0:
        return {}
    results = collection.get(include=["metadatas"])
    stats = {}
    for meta in results["metadatas"]:
        sub = meta.get("subsidiary", "General")
        stats[sub] = stats.get(sub, 0) + 1
    return stats


def get_document_preview(source: str) -> str:
    """Get first ~1000 chars of text from a document."""
    collection = _get_collection()
    results = collection.get(include=["metadatas", "documents"])
    chunks = [
        doc for meta, doc in zip(results["metadatas"], results["documents"])
        if meta.get("source") == source
    ]
    return " ".join(chunks[:3])[:1500] if chunks else "No preview available."


def clear_collection():
    """Delete entire collection."""
    global _collection
    c = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    c.delete_collection(COLLECTION_NAME)
    _collection = None


# ── Aliases ────────────────────────────────────────────────────────────────────
def list_sources() -> List[str]:
    return get_indexed_sources()

def index_chunks(chunks: List[Dict], source: str = "", subsidiary: str = "General") -> int:
    return add_chunks(chunks, subsidiary=subsidiary)

def get_collection_stats() -> dict:
    try:
        return {"total": _get_collection().count()}
    except Exception:
        return {"total": 0}

def delete_source(source_name: str):
    collection = _get_collection()
    results = collection.get(include=["metadatas"])
    ids_to_delete = [
        id_ for id_, meta in zip(results["ids"], results["metadatas"])
        if meta.get("source") == source_name
    ]
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
