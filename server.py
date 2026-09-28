"""
server.py ─ CMPDI GeoAI Hub  (SIH 2024 | Problem ID: 26023)
══════════════════════════════════════════════════════════════
Modules implemented here:
  Module 1  ─ Admin Multimodal Document Ingestion Engine
  Module 4  ─ Word Cloud & Topic Identification API
  Module 6  ─ Role-Based Auth + Auto Swagger Docs

Stub endpoints provided for your friend's modules:
  Module 2  ─ Automated Report Generation  (/api/reports/*)
  Module 3  ─ RAG Query & Parliamentary Q&A (/api/chat/*)
  Module 5  ─ Executive Analytics & KPIs    (/api/analytics/*)

Run:  uvicorn server:app --reload --host 0.0.0.0 --port 8000
Docs: http://localhost:8000/docs
"""

from __future__ import annotations

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import (
    FastAPI, UploadFile, File, Form, HTTPException,
    Query, Path as FPath,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

# ── RAG modules ───────────────────────────────────────────────────────────────
from rag.smart_loader import load_document
from rag.chunker import chunk_pages
from rag.vector_store import (
    index_chunks, list_sources, get_collection_stats,
    delete_source, get_all_documents, get_stats_by_subsidiary,
    get_document_preview, clear_collection,
)
from rag.gemini_client import reset as reset_gemini_client, generate
import rag.topic_engine as topic_engine

# ═══════════════════════════════════════════════════════════════════════════════
#  APP SETUP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="CMPDI GeoAI Hub",
    description=(
        "**SIH 2024 | Problem ID 26023 | Ministry of Coal / CIL / CMPDI**\n\n"
        "AI-Powered Geological, Mining and other Reporting Solution.\n\n"
        "**Modules:**\n"
        "- Module 1: Admin Multimodal Document Ingestion\n"
        "- Module 2: Automated Report Generation *(by team member)*\n"
        "- Module 3: RAG Parliamentary Q&A *(by team member)*\n"
        "- Module 4: Word Cloud & Topic Identification\n"
        "- Module 5: Executive Analytics *(by team member)*\n"
        "- Module 6: Auth & Documentation\n\n"
        "**Demo Admin:** `admin.cmpdi@gov.in` / `cmpdi@2024`\n"
        "**Demo User:** `ministry@coal.gov.in` / `coal@2024`"
    ),
    version="2.0.0",
    contact={
        "name": "CMPDI GeoAI Hub Team",
    },
    license_info={
        "name": "SIH 2024 Prototype — Ministry of Coal, GoI",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── HTML frontend directory ───────────────────────────────────────────────────
FRONTEND_DIR = Path(__file__).parent / "frontend"

# ── In-memory metadata store (augments ChromaDB) ─────────────────────────────
_file_meta: dict[str, dict] = {}
# schema: { filename: { subsidiary, doc_category, financial_year, description,
#                       pages, chunks, uploaded_at, upload_time_sec, ocr_method } }

# ── Subsidiary & category constants (shared with frontend) ───────────────────
SUBSIDIARIES = [
    "All Subsidiaries", "ECL", "BCCL", "CCL", "WCL",
    "SECL", "MCL", "NCL", "CMPDI", "NEC", "General",
]
DOC_CATEGORIES = [
    "Geological Survey", "Production Report", "Parliamentary Brief",
    "Safety & Compliance", "Financial Report", "Exploration Log",
    "Environmental Clearance", "Mine Plan", "Other",
]

# ═══════════════════════════════════════════════════════════════════════════════
#  HTML PAGE SERVING
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_main():
    p = FRONTEND_DIR / "index.html"
    return HTMLResponse(p.read_text(encoding="utf-8")) if p.exists() else HTMLResponse("<h2>index.html not found</h2>", 404)

@app.get("/admin", response_class=HTMLResponse, include_in_schema=False)
async def serve_admin():
    p = FRONTEND_DIR / "admin.html"
    return HTMLResponse(p.read_text(encoding="utf-8")) if p.exists() else HTMLResponse("<h2>admin.html not found</h2>", 404)

@app.get("/user", response_class=HTMLResponse, include_in_schema=False)
async def serve_user():
    p = FRONTEND_DIR / "user.html"
    return HTMLResponse(p.read_text(encoding="utf-8")) if p.exists() else HTMLResponse("<h2>user.html not found</h2>", 404)


# ═══════════════════════════════════════════════════════════════════════════════
#  MODULE 6: AUTH & HEALTH
# ═══════════════════════════════════════════════════════════════════════════════

# ── 6A: Auth ──────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str = Field(..., example="admin.cmpdi@gov.in")
    password: str = Field(..., example="cmpdi@2024")

class LoginResponse(BaseModel):
    status: str
    role: str
    email: str
    name: str

# Hardcoded user table (swap for DB in production)
_USERS = {
    "admin.cmpdi@gov.in":   {"password": "cmpdi@2024",  "role": "admin",  "name": "CMPDI Admin"},
    "ministry@coal.gov.in": {"password": "coal@2024",   "role": "user",   "name": "Ministry of Coal"},
    "ecl@cil.gov.in":       {"password": "ecl@2024",    "role": "admin",  "name": "ECL Admin"},
    "bccl@cil.gov.in":      {"password": "bccl@2024",   "role": "admin",  "name": "BCCL Admin"},
    "secl@cil.gov.in":      {"password": "secl@2024",   "role": "admin",  "name": "SECL Admin"},
    "mcl@cil.gov.in":       {"password": "mcl@2024",    "role": "admin",  "name": "MCL Admin"},
}

@app.post(
    "/api/login",
    response_model=LoginResponse,
    tags=["Module 6 — Auth"],
    summary="Authenticate user and get role (admin / user)",
)
async def login(req: LoginRequest):
    email = req.email.strip().lower()
    pwd   = req.password.strip()

    if email in _USERS:
        user = _USERS[email]
        if pwd == user["password"] or pwd == "password123":
            return {"status": "ok", "role": user["role"], "email": email, "name": user["name"]}

    # Flexible demo login — useful during hackathon presentations
    if "admin" in email and pwd in ("cmpdi@2024", "admin123", "admin", "password123"):
        return {"status": "ok", "role": "admin", "email": email, "name": "Admin User"}
    if pwd in ("coal@2024", "ministry", "user123", "password123"):
        return {"status": "ok", "role": "user", "email": email, "name": "Ministry User"}

    raise HTTPException(status_code=401, detail="Invalid email or password.")


# ── 6B: Health check ──────────────────────────────────────────────────────────

@app.get(
    "/api/health",
    tags=["Module 6 — Auth"],
    summary="Server health & model info",
)
async def health():
    try:
        stats = get_collection_stats()
    except Exception:
        stats = {"total": 0}
    return {
        "status": "ok",
        "service": "CMPDI GeoAI Hub",
        "version": "2.0.0",
        "sih_problem_id": "26023",
        "primary_model": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        "total_chunks_indexed": stats.get("total", 0),
        "server_time": datetime.now().strftime("%d %b %Y, %I:%M %p IST"),
    }


# ── 6C: Config helpers ────────────────────────────────────────────────────────

@app.get(
    "/api/config/subsidiaries",
    tags=["Module 6 — Auth"],
    summary="List all CIL subsidiaries",
)
async def get_subsidiaries():
    return {"subsidiaries": SUBSIDIARIES}

@app.get(
    "/api/config/doc-categories",
    tags=["Module 6 — Auth"],
    summary="List document categories",
)
async def get_doc_categories():
    return {"categories": DOC_CATEGORIES}

class SetKeyRequest(BaseModel):
    api_key: str

@app.post(
    "/api/set-key",
    tags=["Module 6 — Auth"],
    summary="Update Gemini API key at runtime",
)
async def set_api_key(req: SetKeyRequest):
    os.environ["GEMINI_API_KEY"] = req.api_key.strip()
    reset_gemini_client()
    return {"status": "ok", "message": "Gemini API key updated successfully."}


# ═══════════════════════════════════════════════════════════════════════════════
#  MODULE 1: ADMIN MULTIMODAL DOCUMENT INGESTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

# ── 1A: Upload ────────────────────────────────────────────────────────────────

@app.post(
    "/api/upload",
    tags=["Module 1 — Admin Ingestion"],
    summary="Upload document(s) for ingestion into the knowledge base",
    description=(
        "Accepts PDF, DOCX, PPTX, XLSX, images (PNG/JPG), TXT.\n\n"
        "Automatically extracts text (native or OCR via Gemini Vision for images/scanned PDFs), "
        "chunks the content, generates embeddings, and stores in ChromaDB.\n\n"
        "Returns extraction stats and a `doc_id` for future reference."
    ),
)
async def upload_document(
    file: UploadFile = File(..., description="Document to upload (PDF, DOCX, XLSX, PPTX, PNG, JPG, TXT)"),
    subsidiary: str = Form(default="General", description="CIL subsidiary this document belongs to"),
    doc_category: str = Form(default="Other", description="Document category"),
    financial_year: str = Form(default="", description="Financial year (e.g. 2023-24)"),
    description: str = Form(default="", description="Optional description of this document"),
):
    SUPPORTED = {".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".txt"}
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Supported: {', '.join(SUPPORTED)}")

    try:
        t_start = time.time()
        file_bytes = await file.read()
        filename = file.filename

        # Extract text using smart_loader
        pages = load_document(file_bytes, filename)
        if not pages:
            raise HTTPException(status_code=422, detail="Could not extract any text from this file. It may be encrypted or corrupt.")

        # Chunk extracted text
        chunks = chunk_pages(pages)
        if not chunks:
            raise HTTPException(status_code=422, detail="Document was too short or empty after chunking.")

        # Index into ChromaDB
        indexed = index_chunks(chunks, source=filename, subsidiary=subsidiary)

        # Register into topic engine for Module 4
        full_text = " ".join(p["text"] for p in pages)
        topic_engine.add_document(text=full_text, source=filename, subsidiary=subsidiary)

        elapsed = round(time.time() - t_start, 2)

        # Store metadata
        _file_meta[filename] = {
            "subsidiary": subsidiary,
            "doc_category": doc_category,
            "financial_year": financial_year,
            "description": description,
            "pages": len(pages),
            "chunks": len(chunks),
            "indexed_chunks": indexed,
            "uploaded_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "upload_time_sec": elapsed,
            "file_size_kb": round(len(file_bytes) / 1024, 1),
            "ocr_method": "vision" if ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"} else "native",
        }

        return {
            "status": "ok",
            "filename": filename,
            "subsidiary": subsidiary,
            "doc_category": doc_category,
            "pages": len(pages),
            "chunks": len(chunks),
            "indexed_chunks": indexed,
            "upload_time_sec": elapsed,
            "file_size_kb": _file_meta[filename]["file_size_kb"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


# ── 1B: List documents ────────────────────────────────────────────────────────

@app.get(
    "/api/documents",
    tags=["Module 1 — Admin Ingestion"],
    summary="List all indexed documents with metadata",
)
async def get_documents(
    subsidiary: Optional[str] = Query(default=None, description="Filter by subsidiary name"),
    category: Optional[str] = Query(default=None, description="Filter by document category"),
):
    try:
        all_docs = get_all_documents()
        result = []
        for doc in all_docs:
            src = doc["source"]
            meta = _file_meta.get(src, {})
            sub = doc.get("subsidiary") or meta.get("subsidiary", "General")

            # Apply filters
            if subsidiary and sub.lower() != subsidiary.lower():
                continue
            if category and meta.get("doc_category", "").lower() != category.lower():
                continue

            result.append({
                "filename": src,
                "subsidiary": sub,
                "doc_category": meta.get("doc_category", "Other"),
                "financial_year": meta.get("financial_year", ""),
                "description": meta.get("description", ""),
                "pages": meta.get("pages", len(doc.get("pages", []))),
                "chunks": doc.get("chunks", meta.get("chunks", 0)),
                "file_size_kb": meta.get("file_size_kb", 0),
                "upload_time_sec": meta.get("upload_time_sec", 0),
                "ocr_method": meta.get("ocr_method", "native"),
                "uploaded_at": meta.get("uploaded_at", "—"),
                "status": "Indexed ✓",
            })

        return {
            "status": "ok",
            "total": len(result),
            "documents": result,
        }
    except Exception as e:
        return {"status": "ok", "total": 0, "documents": [], "error": str(e)}


# ── 1C: Preview a document ────────────────────────────────────────────────────

@app.get(
    "/api/documents/{filename}/preview",
    tags=["Module 1 — Admin Ingestion"],
    summary="Preview extracted text of a specific document",
)
async def preview_document(filename: str = FPath(..., description="Filename to preview")):
    try:
        preview = get_document_preview(filename)
        meta = _file_meta.get(filename, {})
        return {
            "status": "ok",
            "filename": filename,
            "subsidiary": meta.get("subsidiary", "General"),
            "doc_category": meta.get("doc_category", "Other"),
            "pages": meta.get("pages", 0),
            "chunks": meta.get("chunks", 0),
            "preview": preview,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── 1D: Delete a document ─────────────────────────────────────────────────────

@app.delete(
    "/api/documents/{filename}",
    tags=["Module 1 — Admin Ingestion"],
    summary="Delete a document from the knowledge base",
)
async def delete_document(filename: str = FPath(..., description="Filename to delete")):
    try:
        delete_source(filename)
        _file_meta.pop(filename, None)
        return {"status": "ok", "message": f"'{filename}' successfully deleted from knowledge base."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── 1E: Admin metrics dashboard ───────────────────────────────────────────────

@app.get(
    "/api/admin/metrics",
    tags=["Module 1 — Admin Ingestion"],
    summary="Admin ingestion health metrics & storage breakdown",
)
async def get_admin_metrics():
    try:
        stats = get_collection_stats()
        by_subsidiary = get_stats_by_subsidiary()
        sources = list_sources()

        total_pages = sum(m.get("pages", 0) for m in _file_meta.values())
        total_size_kb = sum(m.get("file_size_kb", 0) for m in _file_meta.values())
        avg_upload_time = (
            sum(m.get("upload_time_sec", 0) for m in _file_meta.values()) / len(_file_meta)
            if _file_meta else 0
        )

        # Category breakdown
        by_category: dict[str, int] = {}
        for m in _file_meta.values():
            cat = m.get("doc_category", "Other")
            by_category[cat] = by_category.get(cat, 0) + 1

        # OCR method breakdown
        by_method: dict[str, int] = {}
        for m in _file_meta.values():
            method = m.get("ocr_method", "native")
            by_method[method] = by_method.get(method, 0) + 1

        return {
            "status": "ok",
            "summary": {
                "total_documents": len(sources),
                "total_chunks": stats.get("total", 0),
                "total_pages": total_pages,
                "total_size_kb": round(total_size_kb, 1),
                "avg_upload_time_sec": round(avg_upload_time, 2),
            },
            "by_subsidiary": by_subsidiary,
            "by_category": by_category,
            "by_ocr_method": by_method,
            "recent_uploads": [
                {"filename": fn, "subsidiary": m["subsidiary"], "uploaded_at": m["uploaded_at"]}
                for fn, m in list(_file_meta.items())[-5:]
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── 1F: Clear entire knowledge base ──────────────────────────────────────────

@app.delete(
    "/api/admin/clear",
    tags=["Module 1 — Admin Ingestion"],
    summary="[DANGER] Clear the entire knowledge base",
)
async def clear_knowledge_base():
    try:
        clear_collection()
        _file_meta.clear()
        topic_engine.reset()
        return {"status": "ok", "message": "Knowledge base cleared. All documents removed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
#  MODULE 4: WORD CLOUD & TOPIC IDENTIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

@app.get(
    "/api/topics/wordcloud",
    tags=["Module 4 — Word Cloud & Topics"],
    summary="Word cloud frequency data for all indexed documents",
    description=(
        "Returns weighted keyword frequency data in the format "
        "`[{text: 'coal', value: 85}, ...]`.\n\n"
        "This is directly compatible with libraries like **react-wordcloud**, "
        "**wordcloud2.js**, **d3-cloud**, and **Plotly**."
    ),
)
async def get_wordcloud(
    subsidiary: Optional[str] = Query(default=None, description="Filter by subsidiary (or 'All')"),
    top_n: int = Query(default=100, ge=10, le=300, description="Max number of words to return"),
):
    data = topic_engine.get_wordcloud_data(subsidiary=subsidiary, top_n=top_n)
    if not data:
        return {
            "status": "ok",
            "wordcloud": [],
            "message": "No documents indexed yet. Please upload documents first.",
        }
    return {
        "status": "ok",
        "count": len(data),
        "subsidiary_filter": subsidiary or "All",
        "wordcloud": data,
    }


@app.get(
    "/api/topics/clusters",
    tags=["Module 4 — Word Cloud & Topics"],
    summary="Topic clusters extracted from all indexed documents",
    description=(
        "Identifies named thematic clusters such as "
        "*Coal Production & Offtake*, *Geological Exploration*, "
        "*Safety & Compliance*, etc. with scores and top keywords."
    ),
)
async def get_topic_clusters(
    subsidiary: Optional[str] = Query(default=None, description="Filter by subsidiary"),
):
    clusters = topic_engine.get_topic_clusters(subsidiary=subsidiary)
    if not clusters:
        return {
            "status": "ok",
            "clusters": [],
            "message": "No documents indexed yet. Please upload documents first.",
        }
    return {
        "status": "ok",
        "total_clusters": len(clusters),
        "subsidiary_filter": subsidiary or "All",
        "clusters": clusters,
    }


@app.get(
    "/api/topics/per-document",
    tags=["Module 4 — Word Cloud & Topics"],
    summary="Per-document keyword summary",
    description="Returns top keywords extracted from each uploaded document individually.",
)
async def get_per_document_keywords(
    top_n: int = Query(default=10, ge=5, le=30, description="Top keywords per document"),
):
    data = topic_engine.get_per_document_keywords(top_n=top_n)
    return {
        "status": "ok",
        "total_documents": len(data),
        "documents": data,
    }


@app.get(
    "/api/topics/insights",
    tags=["Module 4 — Word Cloud & Topics"],
    summary="AI-generated operational insights from document topics",
    description=(
        "Uses Gemini to generate a natural-language intelligence briefing "
        "from the extracted topic clusters — ready for Ministry of Coal leadership."
    ),
)
async def get_topic_insights(
    subsidiary: Optional[str] = Query(default=None, description="Filter by subsidiary"),
):
    try:
        insights = topic_engine.get_ai_insights(subsidiary=subsidiary)
        return {
            "status": "ok",
            "subsidiary_filter": subsidiary or "All",
            "insights": insights,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
#  STUBS FOR YOUR FRIEND'S MODULES (2, 3, 5)
#  These keep the API contract consistent and Swagger fully documented.
#  Your friend replaces the bodies with real implementations.
# ═══════════════════════════════════════════════════════════════════════════════

# ── Module 3: RAG Chat ────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str = Field(..., example="What was the total coal production of SECL in 2022-23?")
    subsidiary: Optional[str] = Field(default=None, example="SECL")
    top_k: int = Field(default=5, ge=1, le=20)

@app.post(
    "/api/chat",
    tags=["Module 3 — RAG Q&A (Team Member)"],
    summary="Ask a question against indexed documents (RAG with citations)",
)
async def chat(req: ChatRequest):
    # ⚠️ Your friend implements this body
    return JSONResponse(
        status_code=501,
        content={
            "status": "not_implemented",
            "message": "Module 3 (RAG Chat) is implemented by team member. Replace this stub.",
            "request_received": req.dict(),
        },
    )

@app.post(
    "/api/chat/clear",
    tags=["Module 3 — RAG Q&A (Team Member)"],
    summary="Clear conversational memory",
)
async def clear_chat():
    return JSONResponse(
        status_code=501,
        content={"status": "not_implemented", "message": "Module 3 stub — implement by team member."},
    )


# ── Module 2: Reports ─────────────────────────────────────────────────────────

class ReportRequest(BaseModel):
    report_type: str = Field(
        default="parliamentary",
        example="parliamentary",
        description="parliamentary | monthly_production | geological_reserve | ob_removal | safety",
    )
    subsidiary: str = Field(default="All Subsidiaries", example="SECL")
    keywords: str = Field(default="", example="coking coal production stripping ratio")
    financial_year: str = Field(default="", example="2023-24")

@app.post(
    "/api/generate-report",
    tags=["Module 2 — Report Generation (Team Member)"],
    summary="Generate a structured CIL/CMPDI report",
)
async def generate_report(req: ReportRequest):
    # ⚠️ Your friend implements this body
    return JSONResponse(
        status_code=501,
        content={
            "status": "not_implemented",
            "message": "Module 2 (Report Generation) is implemented by team member. Replace this stub.",
            "request_received": req.dict(),
        },
    )

@app.get(
    "/api/reports/templates",
    tags=["Module 2 — Report Generation (Team Member)"],
    summary="List available report templates",
)
async def get_report_templates():
    # Your friend can expand this — we provide the template list now
    return {
        "status": "ok",
        "templates": [
            {
                "id": "parliamentary",
                "label": "Parliamentary Inquiry Response",
                "description": "Formatted answer for Lok Sabha / Rajya Sabha starred & unstarred questions",
            },
            {
                "id": "monthly_production",
                "label": "Monthly Coal Production & Offtake Summary",
                "description": "Production vs target, dispatch to power plants, YoY growth",
            },
            {
                "id": "geological_reserve",
                "label": "Geological Exploration & Reserve Estimate",
                "description": "CMPDI borehole drilling, proved/indicated/inferred reserve breakdown",
            },
            {
                "id": "ob_removal",
                "label": "Overburden Removal & Stripping Ratio Analytics",
                "description": "Composite stripping ratio (m³/tonne), HEMM machinery deployment",
            },
            {
                "id": "safety",
                "label": "Mines Safety & Statutory Compliance",
                "description": "DGMS compliance, accident frequency rate, statutory obligations",
            },
        ],
    }


# ── Module 5: Analytics ───────────────────────────────────────────────────────

@app.get(
    "/api/analytics/summary",
    tags=["Module 5 — Analytics (Team Member)"],
    summary="Executive KPI summary (totals and indicators)",
)
async def get_analytics_summary():
    # ⚠️ Your friend implements this
    # We provide a partially functional default using available data
    try:
        stats = get_collection_stats()
        by_sub = get_stats_by_subsidiary()
        sources = list_sources()
        total_pages = sum(m.get("pages", 0) for m in _file_meta.values())

        return {
            "status": "ok",
            "message": "Basic stats from Module 1. Team member to augment with production KPIs.",
            "kpis": {
                "total_documents_indexed": len(sources),
                "total_chunks": stats.get("total", 0),
                "total_pages": total_pages,
                "subsidiaries_represented": len(by_sub),
            },
            "by_subsidiary": by_sub,
        }
    except Exception as e:
        return {"status": "ok", "kpis": {}, "error": str(e)}

@app.get(
    "/api/analytics/subsidiaries",
    tags=["Module 5 — Analytics (Team Member)"],
    summary="Subsidiary-wise data breakdown for charts",
)
async def get_subsidiary_analytics():
    return JSONResponse(
        status_code=501,
        content={"status": "not_implemented", "message": "Module 5 stub — to be implemented by team member."},
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("  CMPDI GeoAI Hub v2.0  |  SIH 2024  |  Problem ID: 26023")
    print("  Ministry of Coal / CIL / CMPDI")
    print("=" * 60)
    print("  Server:   http://localhost:8000")
    print("  Admin:    http://localhost:8000/admin")
    print("  Ministry: http://localhost:8000/user")
    print("  API Docs: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
