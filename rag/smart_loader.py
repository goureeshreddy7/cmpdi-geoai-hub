"""
smart_loader.py
Routes uploaded files to the correct text extractor based on file type.
Supports: PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx), Images, TXT
"""

import os
import io
from typing import List, Dict


def load_document(file_bytes: bytes, filename: str) -> List[Dict]:
    """
    Auto-detect file type and extract text from it.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        filename: Original filename (used to detect extension).

    Returns:
        List of page/slide dicts: [{"page": int, "text": str, "source": str}, ...]
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return _load_pdf(file_bytes, filename)
    elif ext == ".docx":
        return _load_docx(file_bytes, filename)
    elif ext == ".pptx":
        return _load_pptx(file_bytes, filename)
    elif ext in (".xlsx", ".xls"):
        return _load_excel(file_bytes, filename)
    elif ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"):
        return _load_image(file_bytes, filename)
    elif ext == ".txt":
        return _load_txt(file_bytes, filename)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ── PDF ───────────────────────────────────────────────────────────────────────

def _load_pdf(file_bytes: bytes, filename: str) -> List[Dict]:
    import pymupdf as fitz
    pages = []
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for i in range(len(doc)):
        text = doc[i].get_text("text").strip()
        if text:
            pages.append({"page": i + 1, "text": text, "source": filename})
    doc.close()
    return pages


# ── Word (.docx) ──────────────────────────────────────────────────────────────

def _load_docx(file_bytes: bytes, filename: str) -> List[Dict]:
    from docx import Document
    doc = Document(io.BytesIO(file_bytes))
    pages = []
    chunk_texts = []

    for para in doc.paragraphs:
        if para.text.strip():
            chunk_texts.append(para.text.strip())

    # Also extract tables
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                chunk_texts.append(row_text)

    # Group into "pages" of ~1500 chars each
    current, page_num = [], 1
    current_len = 0
    for text in chunk_texts:
        current.append(text)
        current_len += len(text)
        if current_len >= 1500:
            pages.append({"page": page_num, "text": "\n".join(current), "source": filename})
            current, current_len, page_num = [], 0, page_num + 1
    if current:
        pages.append({"page": page_num, "text": "\n".join(current), "source": filename})

    return pages


# ── PowerPoint (.pptx) ───────────────────────────────────────────────────────

def _load_pptx(file_bytes: bytes, filename: str) -> List[Dict]:
    from pptx import Presentation
    prs = Presentation(io.BytesIO(file_bytes))
    pages = []

    for i, slide in enumerate(prs.slides):
        texts = []
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                texts.append(shape.text.strip())
            # Extract table data from slides
            if shape.has_table:
                for row in shape.table.rows:
                    row_text = " | ".join(
                        cell.text.strip() for cell in row.cells if cell.text.strip()
                    )
                    if row_text:
                        texts.append(row_text)

        slide_text = "\n".join(texts)
        if slide_text:
            pages.append({
                "page": i + 1,
                "text": f"[Slide {i + 1}]\n{slide_text}",
                "source": filename,
            })

    return pages


# ── Excel (.xlsx/.xls) ───────────────────────────────────────────────────────

def _load_excel(file_bytes: bytes, filename: str) -> List[Dict]:
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    pages = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows_text = []
        for row in ws.iter_rows(values_only=True):
            row_str = " | ".join(str(cell) for cell in row if cell is not None)
            if row_str.strip():
                rows_text.append(row_str)

        if rows_text:
            pages.append({
                "page": 1,
                "text": f"[Sheet: {sheet_name}]\n" + "\n".join(rows_text),
                "source": filename,
            })

    return pages


# ── Image (via Gemini Vision) ────────────────────────────────────────────────

def _load_image(file_bytes: bytes, filename: str) -> List[Dict]:
    """Use Gemini Vision SDK to extract text/content from an image."""
    from google.genai import types as gtypes
    from rag.gemini_client import _get_client, find_working_model

    client = _get_client()
    model = find_working_model()

    ext = os.path.splitext(filename)[1].lower().strip(".")
    mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                "webp": "image/webp", "bmp": "image/bmp", "tiff": "image/tiff"}
    mime_type = mime_map.get(ext, "image/png")

    resp = client.models.generate_content(
        model=model,
        contents=[
            gtypes.Part.from_bytes(data=file_bytes, mime_type=mime_type),
            "Please extract and describe ALL text, data, charts, tables, and key information in this image. Be thorough and structured.",
        ],
    )
    return [{"page": 1, "text": resp.text.strip(), "source": filename}]


# ── Plain Text ───────────────────────────────────────────────────────────────

def _load_txt(file_bytes: bytes, filename: str) -> List[Dict]:
    text = file_bytes.decode("utf-8", errors="ignore").strip()
    pages = []
    # Split into chunks of 1500 chars per "page"
    for i, start in enumerate(range(0, len(text), 1500)):
        chunk = text[start:start + 1500].strip()
        if chunk:
            pages.append({"page": i + 1, "text": chunk, "source": filename})
    return pages


# ── Supported extensions (for UI display) ───────────────────────────────────

SUPPORTED_EXTENSIONS = ["pdf", "docx", "pptx", "xlsx", "xls", "png", "jpg", "jpeg", "webp", "txt"]
