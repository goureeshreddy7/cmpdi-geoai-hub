"""
pdf_loader.py
Extracts text from uploaded PDF files using PyMuPDF.
Each page is returned as a separate document dict with metadata.
"""

import pymupdf as fitz  # PyMuPDF (fitz is deprecated alias)
from typing import List, Dict


def extract_text_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Extract text from a PDF file, returning a list of page dicts.

    Args:
        pdf_path: Path to the PDF file on disk.

    Returns:
        List of dicts: [{"page": int, "text": str, "source": str}, ...]
    """
    pages = []
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()
        if text:  # Skip empty pages
            pages.append({
                "page": page_num + 1,
                "text": text,
                "source": pdf_path,
            })

    doc.close()
    return pages


def extract_text_from_bytes(pdf_bytes: bytes, filename: str) -> List[Dict]:
    """
    Extract text from PDF bytes (e.g., from Streamlit file uploader).

    Args:
        pdf_bytes: Raw bytes of the PDF.
        filename: Original filename for metadata.

    Returns:
        List of dicts: [{"page": int, "text": str, "source": str}, ...]
    """
    pages = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()
        if text:
            pages.append({
                "page": page_num + 1,
                "text": text,
                "source": filename,
            })

    doc.close()
    return pages
