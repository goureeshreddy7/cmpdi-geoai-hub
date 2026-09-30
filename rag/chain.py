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
    # Step 1: Retrieve relevant chunks
    chunks = similarity_search(query, top_k=top_k)

    # Optional: filter by source document
    if source_filter and source_filter != "All Documents":
        chunks = [c for c in chunks if c["source"] == source_filter]

    if not chunks:
        return "⚠️ No documents indexed yet, or no relevant content found. Please upload a document first.", []

    # Step 2: Build prompt
    prompt = build_prompt(query, chunks, history_text)

    # Step 3: Call Gemini via REST
    answer = generate(prompt, model=model_name)
    return answer, chunks
