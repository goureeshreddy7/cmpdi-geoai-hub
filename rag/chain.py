"""
chain.py  — RAG pipeline using direct Gemini REST API (no SDK)
"""

from typing import List, Dict, Tuple, Optional
from rag.vector_store import similarity_search
from rag.gemini_client import generate, reset

SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on uploaded documents.

Rules:
- Answer using the provided document context below.
- Use conversation history for follow-up questions.
- If the context doesn't have enough info, say: "I couldn't find relevant information in the uploaded documents."
- Be concise, accurate, and cite the source file and page number when possible.
- Never hallucinate or make up facts.
"""


def reset_client():
    reset()


def build_prompt(query: str, context_chunks: List[Dict], history_text: str = "") -> str:
    context_text = "\n\n---\n\n".join(
        f"[Source: {c['source']} | Page {c['page']}]\n{c['text']}"
        for c in context_chunks
    )
    history_section = ""
    if history_text.strip():
        history_section = f"\n## Conversation History:\n{history_text}\n"

    return f"""{SYSTEM_PROMPT}

## Retrieved Document Context:
{context_text}
{history_section}
## Current Question:
{query}

## Answer:"""


def answer_query(
    query: str,
    top_k: int = 5,
    model_name: str = None,
    history_text: str = "",
    source_filter: Optional[str] = None,
) -> Tuple[str, List[Dict]]:
    """
    Full RAG pipeline: retrieve context → build prompt → call Gemini → return answer.
    """
    # Step 1: Retrieve relevant chunks from custom vector store
    chunks = similarity_search(query, top_k=top_k)

    # Optional: filter by source document
    if source_filter and source_filter != "All Documents":
        chunks = [c for c in chunks if c["source"] == source_filter]

    # Step 1b: If vector store has no chunks, check institutional reports from spatial DB
    if not chunks:
        try:
            from spatial.database import SessionLocal
            from spatial.models import Mine, Report

            db = SessionLocal()
            words = [w.strip() for w in query.replace("?", " ").replace(",", " ").split() if len(w.strip()) >= 4]
            spatial_chunks = []
            for word in words[:3]:
                reps = (
                    db.query(Report, Mine)
                    .join(Mine, Report.mine_id == Mine.mine_id)
                    .filter(
                        (Report.title.ilike(f"%{word}%")) |
                        (Report.content.ilike(f"%{word}%")) |
                        (Mine.name.ilike(f"%{word}%")) |
                        (Mine.subsidiary.ilike(f"%{word}%"))
                    )
                    .limit(top_k)
                    .all()
                )
                for rep, mine in reps:
                    spatial_chunks.append({
                        "text": rep.content[:1200] if rep.content else rep.title,
                        "source": f"{rep.title} ({mine.name} - {mine.subsidiary})",
                        "page": rep.year,
                        "subsidiary": mine.subsidiary,
                        "score": round(float(rep.confidence_score or 0.95), 3),
                    })
                if spatial_chunks:
                    break
            db.close()
            chunks = spatial_chunks
        except Exception as ex:
            print(f"[RAG] Spatial fallback error: {ex}")

    # Step 2: Build prompt
    if chunks:
        prompt = build_prompt(query, chunks, history_text)
    else:
        # Grounded domain prompt without uploaded PDFs
        hist_part = f"Conversation History:\n{history_text}\n\n" if history_text.strip() else ""
        prompt = f"""You are the CMPDI GeoAI Hub Mining & Geological Intelligence Assistant.
Answer the following technical question accurately and concisely regarding Indian coal geology, mining engineering, CMPDI, or Coal India subsidiaries.
{hist_part}Question: {query}
Answer:"""

    # Step 3: Call Gemini
    answer = generate(prompt, model=model_name)
    return answer, chunks
