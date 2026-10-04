"""
chunker.py
Splits extracted document text into overlapping chunks using pure Python.
Zero dependency on external heavyweight ML libraries.
"""

from typing import List, Dict


def _split_text_recursive(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Recursively split text by paragraphs, newlines, sentences, and spaces."""
    if not text or not text.strip():
        return []
    
    separators = ["\n\n", "\n", ". ", " ", ""]
    
    def _split(s: str, seps: List[str]) -> List[str]:
        if len(s) <= chunk_size or not seps:
            return [s.strip()] if s.strip() else []
        
        sep = seps[0]
        splits = s.split(sep) if sep else list(s)
        
        chunks = []
        current = ""
        
        for piece in splits:
            candidate = current + (sep if current and sep else "") + piece
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current.strip())
                if len(piece) > chunk_size:
                    chunks.extend(_split(piece, seps[1:]))
                    current = ""
                else:
                    current = piece
        
        if current.strip():
            chunks.append(current.strip())
            
        return chunks

    raw_chunks = _split(text, separators)
    
    # Merge with overlap
    if chunk_overlap <= 0 or len(raw_chunks) <= 1:
        return raw_chunks
    
    merged = []
    for i, c in enumerate(raw_chunks):
        if i == 0:
            merged.append(c)
        else:
            prev = merged[-1]
            overlap_text = prev[-chunk_overlap:] if len(prev) > chunk_overlap else prev
            if overlap_text not in c:
                combined = (overlap_text + " " + c).strip()
                merged.append(combined if len(combined) <= chunk_size + chunk_overlap else c)
            else:
                merged.append(c)
    return merged


def chunk_pages(
    pages: List[Dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Dict]:
    """
    Split page-level text into smaller overlapping chunks.

    Args:
        pages: List of page dicts (with 'text', 'page', 'source').
        chunk_size: Max characters per chunk.
        chunk_overlap: Characters of overlap between consecutive chunks.

    Returns:
        List of chunk dicts:
        [{"chunk_id": str, "text": str, "page": int, "source": str}, ...]
    """
    chunks = []
    for page in pages:
        split_texts = _split_text_recursive(page.get("text", ""), chunk_size, chunk_overlap)
        for i, chunk_text in enumerate(split_texts):
            chunks.append({
                "chunk_id": f"{page.get('source', 'doc')}::p{page.get('page', 1)}::c{i}",
                "text": chunk_text,
                "page": page.get("page", 1),
                "source": page.get("source", "doc"),
            })

    return chunks

