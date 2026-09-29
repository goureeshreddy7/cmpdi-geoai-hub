"""
vector_store.py
================
Vector store using PostgreSQL + pgvector (Neon cloud).
Replaces ChromaDB entirely — zero local RAM for vector indexing.
All embeddings stored in Neon database.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import execute_values

# ── Load .env if present ───────────────────────────────────────────────────────
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# ── Connection ────────────────────────────────────────────────────────────────

def _conn():
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL is not set.")
    return psycopg2.connect(url)


_table_checked = False

def _ensure_table():
    """Create pgvector table on first use."""
    global _table_checked
    if _table_checked:
        return
    url = os.getenv("DATABASE_URL", "").strip()
    if not url or "postgre" not in url:
        return
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS document_chunks (
                        id          TEXT PRIMARY KEY,
                        text        TEXT        NOT NULL,
                        source      TEXT        NOT NULL,
                        subsidiary  TEXT        DEFAULT 'General',
                        page        INTEGER     DEFAULT 1,
                        embedding   vector(768)
                    );
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source     ON document_chunks (source);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_subsidiary ON document_chunks (subsidiary);")
            conn.commit()
        _table_checked = True
    except Exception as e:
        print(f"[VectorStore] Table init warning: {e}")


# ── Write ─────────────────────────────────────────────────────────────────────

def add_chunks(chunks: List[Dict], subsidiary: str = "General") -> int:
    """
    Insert new chunks with their embeddings into Neon pgvector.
    Skips chunks whose IDs already exist.
    Returns number of newly inserted chunks.
    """
    _ensure_table()
    from rag.embedder import embed_texts
    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    ids   = [c["chunk_id"] for c in chunks]

    # Check existing IDs
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM document_chunks WHERE id = ANY(%s);", (ids,))
            existing = {row[0] for row in cur.fetchall()}

    new = [(c, i) for c, i in zip(chunks, ids) if i not in existing]
    if not new:
        return 0

    new_chunks, new_ids = zip(*new)
    new_texts = [c["text"] for c in new_chunks]
    embeddings = embed_texts(list(new_texts))

    rows = [
        (
            c["chunk_id"],
            c["text"],
            c["source"],
            subsidiary,
            c["page"],
            f"[{','.join(str(v) for v in emb)}]",
        )
        for c, emb in zip(new_chunks, embeddings)
    ]

    with _conn() as conn:
        with conn.cursor() as cur:
            execute_values(cur, """
                INSERT INTO document_chunks (id, text, source, subsidiary, page, embedding)
                VALUES %s
                ON CONFLICT (id) DO NOTHING;
            """, rows)
        conn.commit()

    return len(rows)


# ── Search ────────────────────────────────────────────────────────────────────

def similarity_search(
    query: str,
    top_k: int = 5,
    subsidiary: Optional[str] = None,
) -> List[Dict]:
    """
    Find top-k most relevant chunks using cosine similarity.
    Optionally filter by subsidiary.
    Returns list of {text, source, page, subsidiary, score}.
    """
    from rag.embedder import embed_query
    q_emb = embed_query(query)
    vec_str = f"[{','.join(str(v) for v in q_emb)}]"

    where = ""
    params: list = [vec_str, vec_str, top_k]
    if subsidiary and subsidiary.lower() not in ("all", "all subsidiaries", ""):
        where = "WHERE subsidiary = %s"
        params = [vec_str, vec_str, subsidiary, top_k]

    sql = f"""
        SELECT text, source, page, subsidiary,
               1 - (embedding <=> %s::vector) AS score
        FROM   document_chunks
        {where}
        ORDER  BY embedding <=> %s::vector
        LIMIT  %s;
    """

    # Rebuild params correctly
    if subsidiary and subsidiary.lower() not in ("all", "all subsidiaries", ""):
        sql = """
            SELECT text, source, page, subsidiary,
                   1 - (embedding <=> %s::vector) AS score
            FROM   document_chunks
            WHERE  subsidiary = %s
            ORDER  BY embedding <=> %s::vector
            LIMIT  %s;
        """
        params = [vec_str, subsidiary, vec_str, top_k]
    else:
        sql = """
            SELECT text, source, page, subsidiary,
                   1 - (embedding <=> %s::vector) AS score
            FROM   document_chunks
            ORDER  BY embedding <=> %s::vector
            LIMIT  %s;
        """
        params = [vec_str, vec_str, top_k]

    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
        return [
            {"text": r[0], "source": r[1], "page": r[2],
             "subsidiary": r[3], "score": round(float(r[4]), 4)}
            for r in rows
        ]
    except Exception as e:
        print(f"[VectorStore] Search error: {e}")
        return []


# ── Read helpers ──────────────────────────────────────────────────────────────

def get_indexed_sources() -> List[str]:
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT source FROM document_chunks ORDER BY source;")
            return [r[0] for r in cur.fetchall()]


def get_all_documents() -> List[Dict]:
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT source, subsidiary, COUNT(*) as chunks, MIN(text) as preview
                FROM   document_chunks
                GROUP  BY source, subsidiary
                ORDER  BY source;
            """)
            return [
                {"source": r[0], "subsidiary": r[1],
                 "chunks": r[2], "preview": (r[3] or "")[:300]}
                for r in cur.fetchall()
            ]


def get_stats_by_subsidiary() -> Dict:
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT subsidiary, COUNT(*) FROM document_chunks GROUP BY subsidiary;
            """)
            return {r[0]: r[1] for r in cur.fetchall()}


def get_document_preview(source: str) -> str:
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT text FROM document_chunks
                WHERE source = %s ORDER BY page LIMIT 3;
            """, (source,))
            rows = cur.fetchall()
    return " ".join(r[0] for r in rows)[:1500] if rows else "No preview available."


def get_collection_stats() -> Dict:
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM document_chunks;")
                return {"total": cur.fetchone()[0]}
    except Exception:
        return {"total": 0}


def delete_source(source_name: str):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM document_chunks WHERE source = %s;", (source_name,))
        conn.commit()


def clear_collection():
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM document_chunks;")
        conn.commit()


# ── Aliases ───────────────────────────────────────────────────────────────────
def list_sources() -> List[str]:
    return get_indexed_sources()

def index_chunks(chunks: List[Dict], source: str = "", subsidiary: str = "General") -> int:
    return add_chunks(chunks, subsidiary=subsidiary)
