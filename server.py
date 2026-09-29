"""
server.py — CMPDI GeoAI Hub  (SIH 2024 | Problem ID: 26023)
════════════════════════════════════════════════════════════
Core Features:
  1. Document Ingestion  — Upload PDFs/Docs → OCR → ChromaDB + Supabase
  2. AI Chat + RAG       — Ask questions → retrieves chunks → Gemini answers with citations
  3. Word Cloud          — Topic clusters and keyword frequencies from indexed docs
  4. Report Generation   — AI-generated reports exported as PDF / DOCX / CSV
  5. Auth                — Email/Password login with JWT (role: admin / user)
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
    Query, Path as FPath, Depends, Header, Response
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# ── Database & Auth ────────────────────────────────────────────────────────────
from db.connection import get_db, init_db
from db.models import User, Document
from auth.security import (
    hash_password, verify_password, create_access_token, decode_access_token
)
from storage.store import save_file, delete_file

# ── RAG & AI modules ───────────────────────────────────────────────────────────
from rag.smart_loader import load_document
from rag.chunker import chunk_pages
from rag.vector_store import (
    index_chunks, get_collection_stats,
    delete_source, get_document_preview, clear_collection,
)
from rag.gemini_client import reset as reset_gemini_client, generate
from rag.chain import answer_query
from rag.memory import ConversationMemory
from rag.analyzer import analyze_document
from rag.report_exporter import export_to_pdf, export_to_docx, export_to_csv
import rag.topic_engine as topic_engine

# ══════════════════════════════════════════════════════════════════════════════
#  APP INIT
# ══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="CMPDI GeoAI Hub",
    description="AI-Powered Geological & Mining Intelligence Platform — SIH 2024 | Problem ID: 26023",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent / "frontend"

SUBSIDIARIES = [
    "All Subsidiaries", "ECL", "BCCL", "CCL", "WCL",
    "SECL", "MCL", "NCL", "CMPDI", "NEC", "General",
]

DOC_CATEGORIES = [
    "Geological Survey", "Production Report", "Parliamentary Brief",
    "Safety & Compliance", "Financial Report", "Exploration Log",
    "Environmental Clearance", "Mine Plan", "Other",
]

# In-memory per-server chat session (resets on server restart)
_chat_memory = ConversationMemory(max_history=8)


@app.on_event("startup")
def on_startup():
    """Create DB tables and seed default accounts on first run."""
    try:
        init_db()
        from db.connection import SessionLocal
        db = SessionLocal()
        defaults = [
            ("admin.cmpdi@gov.in",  "cmpdi@2024",  "CMPDI Admin",         "admin", "CMPDI"),
            ("ministry@coal.gov.in","coal@2024",   "Ministry of Coal",    "user",  "General"),
            ("secl@cil.gov.in",     "secl@2024",   "SECL Data Officer",   "admin", "SECL"),
            ("mcl@cil.gov.in",      "mcl@2024",    "MCL Data Officer",    "admin", "MCL"),
            ("bccl@cil.gov.in",     "bccl@2024",   "BCCL Data Officer",   "admin", "BCCL"),
        ]
        for email, pwd, name, role, sub in defaults:
            if not db.query(User).filter(User.email == email).first():
                db.add(User(
                    email=email, password_hash=hash_password(pwd),
                    name=name, role=role, subsidiary=sub,
                ))
        db.commit()

        # Sync existing docs into topic engine
        for doc in db.query(Document).all():
            preview = get_document_preview(doc.filename)
            if preview and preview != "No preview available.":
                topic_engine.add_document(text=preview, source=doc.filename, subsidiary=doc.subsidiary)
        db.close()
    except Exception as e:
        print(f"[Startup Warning] {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH DEPENDENCY
# ══════════════════════════════════════════════════════════════════════════════

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    return db.query(User).filter(User.email == payload["sub"]).first()


# ══════════════════════════════════════════════════════════════════════════════
#  FRONTEND PAGES
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_index():
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


# ══════════════════════════════════════════════════════════════════════════════
#  FEATURE 5: AUTH
# ══════════════════════════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: Optional[str] = "user"
    subsidiary: Optional[str] = "General"


@app.post("/api/login", tags=["Auth"])
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(req.password.strip(), user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return {
        "status": "ok",
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "name": user.name,
                 "role": user.role, "subsidiary": user.subsidiary},
    }


@app.post("/api/auth/register", tags=["Auth"])
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Account already exists.")
    user = User(
        email=email,
        password_hash=hash_password(req.password.strip()),
        name=req.name.strip(),
        role=req.role if req.role in ("admin", "user") else "user",
        subsidiary=req.subsidiary or "General",
    )
    db.add(user); db.commit(); db.refresh(user)
    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return {
        "status": "ok", "access_token": token, "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "name": user.name,
                 "role": user.role, "subsidiary": user.subsidiary},
    }


@app.get("/api/auth/me", tags=["Auth"])
async def get_me(current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return {"status": "ok", "user": {
        "id": current_user.id, "email": current_user.email,
        "name": current_user.name, "role": current_user.role,
        "subsidiary": current_user.subsidiary,
    }}


@app.get("/api/health", tags=["Auth"])
async def health(db: Session = Depends(get_db)):
    stats = get_collection_stats()
    return {
        "status": "ok",
        "service": "CMPDI GeoAI Hub v3.0",
        "chunks_indexed": stats.get("total", 0),
        "total_documents": db.query(Document).count(),
        "total_users": db.query(User).count(),
        "database": "postgresql" if os.getenv("DATABASE_URL", "").startswith("postgre") else "sqlite",
        "storage": "supabase" if os.getenv("SUPABASE_URL") else "local",
        "server_time": datetime.now().strftime("%d %b %Y, %I:%M %p IST"),
    }


@app.get("/api/config/subsidiaries", tags=["Auth"])
async def get_subsidiaries():
    return {"subsidiaries": SUBSIDIARIES}


@app.get("/api/config/doc-categories", tags=["Auth"])
async def get_doc_categories():
    return {"categories": DOC_CATEGORIES}


@app.post("/api/set-key", tags=["Auth"])
async def set_api_key(req: dict):
    os.environ["GEMINI_API_KEY"] = req.get("api_key", "").strip()
    reset_gemini_client()
    return {"status": "ok"}


# ══════════════════════════════════════════════════════════════════════════════
#  FEATURE 1: DOCUMENT INGESTION
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/upload", tags=["Ingestion"])
async def upload_document(
    file: UploadFile = File(...),
    subsidiary: str = Form(default="General"),
    doc_category: str = Form(default="Other"),
    financial_year: str = Form(default=""),
    description: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    SUPPORTED = {".pdf", ".docx", ".pptx", ".xlsx", ".xls",
                 ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".txt"}
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    try:
        t_start = time.time()
        file_bytes = await file.read()
        filename = file.filename

        storage_path, storage_type = save_file(file_bytes, filename)
        pages = load_document(file_bytes, filename)
        if not pages:
            raise HTTPException(422, "Could not extract text. File may be empty or corrupted.")

        chunks = chunk_pages(pages)
        indexed = index_chunks(chunks, source=filename, subsidiary=subsidiary)

        full_text = " ".join(p["text"] for p in pages)
        topic_engine.add_document(text=full_text, source=filename, subsidiary=subsidiary)

        size_kb = round(len(file_bytes) / 1024, 1)
        ocr_method = "vision" if ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"} else "native"

        existing = db.query(Document).filter(Document.filename == filename).first()
        if existing:
            existing.storage_path = storage_path
            existing.subsidiary = subsidiary
            existing.category = doc_category
            existing.financial_year = financial_year
            existing.description = description
            existing.pages = len(pages)
            existing.chunks = len(chunks)
            existing.file_size_kb = size_kb
            existing.ocr_method = ocr_method
            existing.uploaded_at = datetime.utcnow()
            doc_id = existing.id
        else:
            new_doc = Document(
                filename=filename, storage_path=storage_path,
                subsidiary=subsidiary, category=doc_category,
                financial_year=financial_year, description=description,
                pages=len(pages), chunks=len(chunks),
                file_size_kb=size_kb, ocr_method=ocr_method,
                uploaded_by_id=current_user.id if current_user else None,
            )
            db.add(new_doc); db.commit(); db.refresh(new_doc)
            doc_id = new_doc.id
        db.commit()

        return {
            "status": "ok", "doc_id": doc_id, "filename": filename,
            "subsidiary": subsidiary, "pages": len(pages),
            "chunks": len(chunks), "indexed_chunks": indexed,
            "upload_time_sec": round(time.time() - t_start, 2),
            "file_size_kb": size_kb, "storage_type": storage_type,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ingestion failed: {e}")


@app.get("/api/documents", tags=["Ingestion"])
async def get_documents(
    subsidiary: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Document)
    if subsidiary and subsidiary.lower() not in ("all", "all subsidiaries"):
        q = q.filter(Document.subsidiary == subsidiary)
    if category and category.lower() != "all":
        q = q.filter(Document.category == category)
    docs = q.order_by(Document.uploaded_at.desc()).all()
    return {"status": "ok", "total": len(docs), "documents": [
        {
            "id": d.id, "filename": d.filename, "subsidiary": d.subsidiary,
            "doc_category": d.category, "financial_year": d.financial_year or "—",
            "description": d.description or "", "pages": d.pages, "chunks": d.chunks,
            "file_size_kb": d.file_size_kb, "ocr_method": d.ocr_method,
            "uploaded_at": d.uploaded_at.strftime("%d %b %Y, %I:%M %p") if d.uploaded_at else "—",
        }
        for d in docs
    ]}


@app.delete("/api/documents/{filename}", tags=["Ingestion"])
async def delete_document(filename: str = FPath(...), db: Session = Depends(get_db)):
    delete_source(filename)
    delete_file(filename)
    doc = db.query(Document).filter(Document.filename == filename).first()
    if doc:
        db.delete(doc); db.commit()
    return {"status": "ok", "message": f"'{filename}' deleted."}


@app.delete("/api/admin/clear", tags=["Ingestion"])
async def clear_all(db: Session = Depends(get_db)):
    clear_collection()
    topic_engine.reset()
    db.query(Document).delete(); db.commit()
    return {"status": "ok", "message": "Knowledge base cleared."}


@app.get("/api/admin/metrics", tags=["Ingestion"])
async def get_metrics(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    stats = get_collection_stats()
    by_sub, by_cat = {}, {}
    total_pages, total_size = 0, 0.0
    for d in docs:
        by_sub[d.subsidiary] = by_sub.get(d.subsidiary, 0) + 1
        by_cat[d.category]   = by_cat.get(d.category, 0) + 1
        total_pages += d.pages or 0
        total_size  += d.file_size_kb or 0.0
    return {
        "status": "ok",
        "summary": {
            "total_documents": len(docs),
            "total_chunks": stats.get("total", 0),
            "total_pages": total_pages,
            "total_size_kb": round(total_size, 1),
        },
        "by_subsidiary": by_sub,
        "by_category": by_cat,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  FEATURE 2: AI CHAT + RAG + SOURCE CITATIONS
# ══════════════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    query: str
    subsidiary: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


@app.post("/api/chat", tags=["AI Chat"])
async def chat(req: ChatRequest):
    """
    RAG Question & Answer with full source citations.
    Returns the AI answer + the exact document chunks it used (source file, page, confidence).
    """
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty.")
    try:
        history_text = _chat_memory.get_history_text()
        _chat_memory.add_user(req.query)

        answer, sources = answer_query(
            query=req.query,
            top_k=req.top_k,
            history_text=history_text,
        )
        _chat_memory.add_assistant(answer)

        citations = [
            {
                "source": s["source"],
                "page": s["page"],
                "subsidiary": s["subsidiary"],
                "confidence": s["score"],
                "excerpt": s["text"][:300] + "..." if len(s["text"]) > 300 else s["text"],
            }
            for s in sources
        ]

        return {
            "status": "ok",
            "query": req.query,
            "answer": answer,
            "citations": citations,
            "total_sources": len(citations),
        }
    except Exception as e:
        raise HTTPException(500, f"Chat error: {e}")


@app.post("/api/chat/clear", tags=["AI Chat"])
async def clear_chat():
    _chat_memory.clear()
    return {"status": "ok", "message": "Chat history cleared."}


# ══════════════════════════════════════════════════════════════════════════════
#  FEATURE 3: WORD CLOUD + TOPIC CLUSTERS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/api/topics/wordcloud", tags=["Word Cloud"])
async def get_wordcloud(
    subsidiary: Optional[str] = Query(None),
    top_n: int = Query(default=100, ge=10, le=300),
):
    data = topic_engine.get_wordcloud_data(subsidiary=subsidiary, top_n=top_n)
    return {"status": "ok", "count": len(data), "wordcloud": data}


@app.get("/api/topics/clusters", tags=["Word Cloud"])
async def get_clusters(subsidiary: Optional[str] = Query(None)):
    clusters = topic_engine.get_topic_clusters(subsidiary=subsidiary)
    return {"status": "ok", "total_clusters": len(clusters), "clusters": clusters}


@app.get("/api/topics/insights", tags=["Word Cloud"])
async def get_insights(subsidiary: Optional[str] = Query(None)):
    insights = topic_engine.get_ai_insights(subsidiary=subsidiary)
    return {"status": "ok", "insights": insights}


# ══════════════════════════════════════════════════════════════════════════════
#  FEATURE 4: REPORT GENERATION (AI → PDF / DOCX / CSV)
# ══════════════════════════════════════════════════════════════════════════════

class ReportRequest(BaseModel):
    report_type: str = "parliamentary"   # parliamentary | monthly | geological | safety
    subsidiary:  str = "All Subsidiaries"
    keywords:    str = ""
    financial_year: str = ""
    export_format: str = "docx"         # pdf | docx | csv


@app.post("/api/generate-report", tags=["Reports"])
async def generate_report(req: ReportRequest, db: Session = Depends(get_db)):
    """
    AI-generated institutional report using RAG context from indexed documents.
    Returns a downloadable PDF, DOCX, or CSV file.
    """
    try:
        # Build a targeted query from the report parameters
        query_parts = [f"Generate a {req.report_type} report"]
        if req.subsidiary and req.subsidiary != "All Subsidiaries":
            query_parts.append(f"for {req.subsidiary}")
        if req.keywords:
            query_parts.append(f"focusing on: {req.keywords}")
        if req.financial_year:
            query_parts.append(f"for financial year {req.financial_year}")
        query = ". ".join(query_parts)

        # Get relevant context from vector store
        from rag.vector_store import similarity_search
        chunks = similarity_search(query, top_k=8)

        context = "\n\n---\n\n".join(
            f"[{c['source']} | Page {c['page']}]\n{c['text']}"
            for c in chunks
        ) if chunks else "No documents indexed yet."

        # Report type specific instructions
        report_prompts = {
            "parliamentary": "Draft a formal Parliamentary Inquiry Response with data-backed answers.",
            "monthly":       "Write a Monthly Coal Production & Despatch Summary report.",
            "geological":    "Prepare a Geological Exploration & Reserve Assessment report.",
            "safety":        "Generate a Mines Safety & Statutory Compliance report.",
        }
        instruction = report_prompts.get(req.report_type, "Generate a formal government report.")

        prompt = f"""You are a senior CMPDI/CIL official writing an official government report.

## Task:
{instruction}

## Parameters:
- Subsidiary: {req.subsidiary}
- Keywords/Focus: {req.keywords or 'General'}
- Financial Year: {req.financial_year or 'Latest available'}

## Document Context from Knowledge Base:
{context[:6000]}

## Instructions:
- Write in formal government report style
- Use ## for section headers
- Use bullet points for data
- Include source references where possible
- Keep it factual and concise
- Minimum 400 words

## Report:"""

        raw_report = generate(prompt, max_tokens=2048)

        report_data = {
            "filename": f"{req.report_type}_report_{req.subsidiary}.{req.export_format}",
            "raw_report": raw_report,
            "page_count": len(chunks),
            "char_count": len(raw_report),
        }

        # Export to requested format
        fmt = req.export_format.lower()
        if fmt == "pdf":
            content = export_to_pdf(report_data)
            media_type = "application/pdf"
            filename = f"CMPDI_{req.report_type}_{req.subsidiary}.pdf"
        elif fmt == "csv":
            content = export_to_csv(report_data)
            media_type = "text/csv"
            filename = f"CMPDI_{req.report_type}_{req.subsidiary}.csv"
        else:  # default docx
            content = export_to_docx(report_data)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            filename = f"CMPDI_{req.report_type}_{req.subsidiary}.docx"

        return StreamingResponse(
            iter([content]),
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except Exception as e:
        raise HTTPException(500, f"Report generation failed: {e}")


@app.get("/api/reports/templates", tags=["Reports"])
async def get_templates():
    return {"templates": [
        {"id": "parliamentary", "label": "Parliamentary Inquiry Response"},
        {"id": "monthly",       "label": "Monthly Coal Production Summary"},
        {"id": "geological",    "label": "Geological Reserve Estimate"},
        {"id": "safety",        "label": "Mines Safety & Compliance"},
    ]}


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print("=" * 60)
    print("  CMPDI GeoAI Hub v3.0  |  SIH 2024  |  Problem ID: 26023")
    print(f"  Starting server on port {port}...")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=port)
