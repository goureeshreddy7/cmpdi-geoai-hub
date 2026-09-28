"""
chunker.py
Splits extracted PDF page text into overlapping chunks
using LangChain's RecursiveCharacterTextSplitter.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict


def chunk_pages(
    pages: List[Dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Dict]:
    """
    Split page-level text into smaller overlapping chunks.

    Args:
        pages: List of page dicts from pdf_loader (with 'text', 'page', 'source').
        chunk_size: Max characters per chunk.
        chunk_overlap: Characters of overlap between consecutive chunks.

    Returns:
        List of chunk dicts:
        [{"chunk_id": str, "text": str, "page": int, "source": str}, ...]
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for page in pages:
        split_texts = splitter.split_text(page["text"])
        for i, chunk_text in enumerate(split_texts):
            chunks.append({
                "chunk_id": f"{page['source']}::p{page['page']}::c{i}",
                "text": chunk_text,
                "page": page["page"],
                "source": page["source"],
            })

    return chunks
