"""
server.py ─ CMPDI GeoAI Hub  (SIH 2024 | Problem ID: 26023)
══════════════════════════════════════════════════════════════
Modules:
  Module 1  ─ Admin Multimodal Document Ingestion & Persistent DB Storage
  Module 4  ─ Word Cloud & Topic Identification Engine
  Module 6  ─ Auth (JWT, Password, Google OAuth) + Auto Swagger Docs

Stubs for Team Members:
  Module 2  ─ Automated Report Generation  (/api/reports/*)
  Module 3  ─ RAG Query & Parliamentary Q&A (/api/chat/*)
  Module 5  ─ Executive Analytics & KPIs    (/api/analytics/*)

Works 100% Free locally (SQLite + ChromaDB + Local storage)
Ready for Free Cloud Deployment on Vercel (Neon PostgreSQL + Supabase)
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
    Query, Path as FPath, Depends, Header
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# ── Database & Auth ───────────────────────────────────────────────────────────
from db.connection import get_db, init_db
from db.models import User, Document
from auth.security import (
    hash_password, verify_password, create_access_token,
    decode_access_token, verify_google_token
)
from storage.store import save_file, delete_file

# ── RAG & AI modules ──────────────────────────────────────────────────────────
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
#  APP INITIALIZATION & LIFESPAN
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="CMPDI GeoAI Hub",
    description=(
        "**SIH 2024 | Problem ID 26023 | Ministry of Coal / CIL / CMPDI**\n\n"
        "AI-Powered Geological, Mining and other Reporting Solution.\n\n"
        "**Features:**\n"
        "- Persistent Document & User Storage (SQLite / Neon PostgreSQL)\n"
        "- JWT & Google OAuth 2.0 Authentication\n"
        "- Module 1: Admin Multimodal Ingestion (PDF, Scans, Excel, DOCX, Images)\n"
        "- Module 4: Topic Modeling & Dynamic Word Cloud\n"
        "- Module 6: Role-Based Access Control & Live API Docs\n\n"
        "**Demo Credentials:**\n"
        "- Admin: `admin.cmpdi@gov.in` / `cmpdi@2024`\n"
        "- Ministry: `ministry@coal.gov.in` / `coal@2024`"
    ),
    version="2.1.0",
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


# Initialize DB and seed default admin/ministry accounts on startup
@app.on_event("startup")
def on_startup():
    try:
        init_db()
        from db.connection import SessionLocal
        db = SessionLocal()

        # Seed default users if they don't exist
        defaults = [
            ("admin.cmpdi@gov.in", "cmpdi@2024", "CMPDI Admin", "admin", "CMPDI"),
            ("ministry@coal.gov.in", "coal@2024", "Ministry of Coal", "user", "General"),
            ("secl@cil.gov.in", "secl@2024", "SECL Data Officer", "admin", "SECL"),
            ("mcl@cil.gov.in", "mcl@2024", "MCL Data Officer", "admin", "MCL"),
            ("bccl@cil.gov.in", "bccl@2024", "BCCL Data Officer", "admin", "BCCL"),
        ]
        for email, pwd, name, role, sub in defaults:
            existing = db.query(User).filter(User.email == email).first()
            if not existing:
                u = User(
                    email=email,
                    password_hash=hash_password(pwd),
                    name=name,
                    role=role,
                    subsidiary=sub,
                )
                db.add(u)
        db.commit()

        # Sync existing docs into topic engine
        docs = db.query(Document).all()
        for doc in docs:
            preview = get_document_preview(doc.filename)
            if preview and preview != "No preview available.":
                topic_engine.add_document(text=preview, source=doc.filename, subsidiary=doc.subsidiary)
        db.close()
    except Exception as e:
        print(f"[Startup Warning] {e}")


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH DEPENDENCY
# ═══════════════════════════════════════════════════════════════════════════════

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Extract user from Bearer JWT token if provided."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    return db.query(User).filter(User.email == payload["sub"]).first()


# ═══════════════════════════════════════════════════════════════════════════════
#  HTML PAGES
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
#  MODULE 6: AUTHENTICATION & USERS
# ═══════════════════════════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    email: str = Field(..., example="admin.cmpdi@gov.in")
    password: str = Field(..., example="cmpdi@2024")

class RegisterRequest(BaseModel):
    email: str = Field(..., example="officer@secl.gov.in")
    password: str = Field(..., example="password123")
    name: str = Field(..., example="Mining Officer")
    role: Optional[str] = Field(default="user", example="user")
    subsidiary: Optional[str] = Field(default="SECL", example="SECL")

class GoogleLoginRequest(BaseModel):
    id_token: str = Field(..., description="Google OAuth ID token from Google Sign-In SDK")


@app.post(
    "/api/login",
    tags=["Module 6 — Auth"],
    summary="Email & Password Login (Returns JWT)",
)
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    pwd = req.password.strip()

    user = db.query(User).filter(User.email == email).first()

    # Verify password hash or allow fallback demo password for presentation convenience
    valid = False
    if user and user.password_hash:
        valid = verify_password(pwd, user.password_hash) or pwd == "password123"

    if not valid:
        # Fallback check for demo
        if "admin" in email and pwd in ("cmpdi@2024", "password123", "admin"):
            role = "admin"
            name = "CMPDI Admin"
            sub = "CMPDI"
        elif pwd in ("coal@2024", "password123", "user"):
            role = "user"
            name = "Ministry User"
            sub = "General"
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        # Ensure user exists in DB
        if not user:
            user = User(
                email=email,
                password_hash=hash_password(pwd),
                name=name,
                role=role,
                subsidiary=sub
            )
            db.add(user)
            db.commit()
            db.refresh(user)

    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})

    return {
        "status": "ok",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "subsidiary": user.subsidiary,
        }
    }


@app.post(
    "/api/auth/register",
    tags=["Module 6 — Auth"],
    summary="Register a new user",
)
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    new_user = User(
        email=email,
        password_hash=hash_password(req.password.strip()),
        name=req.name.strip(),
        role=req.role.strip() if req.role in ("admin", "user") else "user",
        subsidiary=req.subsidiary.strip() if req.subsidiary else "General",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.email, "role": new_user.role, "id": new_user.id})
    return {
        "status": "ok",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name,
            "role": new_user.role,
            "subsidiary": new_user.subsidiary,
        }
    }


@app.post(
    "/api/auth/google",
    tags=["Module 6 — Auth"],
    summary="Google 1-Tap / OAuth Sign-In (Returns JWT)",
)
async def google_login(req: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Verifies Google ID token, registers or logs in user, and returns JWT."""
    info = verify_google_token(req.id_token)
    if not info:
        raise HTTPException(status_code=400, detail="Invalid or expired Google token.")

    email = info["email"].lower()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # Determine role from email (or default user)
        role = "admin" if "admin" in email or "cmpdi" in email else "user"
        user = User(
            email=email,
            name=info.get("name") or email.split("@")[0],
            google_id=info.get("google_id"),
            avatar_url=info.get("picture"),
            role=role,
            subsidiary="General",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Link google_id if missing
        if not user.google_id:
            user.google_id = info.get("google_id")
            user.avatar_url = info.get("picture")
            db.commit()

    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return {
        "status": "ok",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "subsidiary": user.subsidiary,
            "avatar_url": user.avatar_url,
        }
    }


@app.get(
    "/api/auth/me",
    tags=["Module 6 — Auth"],
    summary="Get current user profile from JWT Bearer token",
)
async def get_me(current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated or token expired.")
    return {
        "status": "ok",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role,
            "subsidiary": current_user.subsidiary,
            "avatar_url": current_user.avatar_url,
        }
    }


@app.get(
    "/api/health",
    tags=["Module 6 — Auth"],
    summary="Server health & model info",
)
async def health(db: Session = Depends(get_db)):
    try:
        stats = get_collection_stats()
        doc_count = db.query(Document).count()
        user_count = db.query(User).count()
    except Exception:
        stats = {"total": 0}
        doc_count, user_count = 0, 0

    return {
        "status": "ok",
        "service": "CMPDI GeoAI Hub",
        "version": "2.1.0",
        "sih_problem_id": "26023",
        "primary_model": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        "total_chunks_indexed": stats.get("total", 0),
        "total_documents": doc_count,
        "total_users": user_count,
        "database": "postgresql/neon" if os.getenv("DATABASE_URL", "").startswith("postgre") else "sqlite",
        "storage": "supabase" if os.getenv("SUPABASE_URL") else "local",
        "server_time": datetime.now().strftime("%d %b %Y, %I:%M %p IST"),
    }


@app.get("/api/config/subsidiaries", tags=["Module 6 — Auth"], summary="List CIL subsidiaries")
async def get_subsidiaries():
    return {"subsidiaries": SUBSIDIARIES}


@app.get("/api/config/doc-categories", tags=["Module 6 — Auth"], summary="List document categories")
async def get_doc_categories():
    return {"categories": DOC_CATEGORIES}


class SetKeyRequest(BaseModel):
    api_key: str

@app.post("/api/set-key", tags=["Module 6 — Auth"], summary="Update Gemini API key at runtime")
async def set_api_key(req: SetKeyRequest):
    os.environ["GEMINI_API_KEY"] = req.api_key.strip()
    reset_gemini_client()
    return {"status": "ok", "message": "Gemini API key updated successfully."}


# ═══════════════════════════════════════════════════════════════════════════════
#  MODULE 1: ADMIN MULTIMODAL DOCUMENT INGESTION & STORAGE
# ═══════════════════════════════════════════════════════════════════════════════

@app.post(
    "/api/upload",
    tags=["Module 1 — Admin Ingestion"],
    summary="Upload & index document with persistent storage",
)
async def upload_document(
    file: UploadFile = File(...),
    subsidiary: str = Form(default="General"),
    doc_category: str = Form(default="Other"),
    financial_year: str = Form(default=""),
    description: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    SUPPORTED = {".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".txt"}
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Supported: {', '.join(SUPPORTED)}")

    try:
        t_start = time.time()
        file_bytes = await file.read()
        filename = file.filename

        # 1. Save file to storage (local disk or Supabase bucket)
        storage_path, storage_type = save_file(file_bytes, filename)

        # 2. Extract text (native or OCR via Gemini Vision)
        pages = load_document(file_bytes, filename)
        if not pages:
            raise HTTPException(status_code=422, detail="Could not extract text. File may be empty or corrupted.")

        # 3. Chunk text & store in Vector Store (ChromaDB)
        chunks = chunk_pages(pages)
        indexed = index_chunks(chunks, source=filename, subsidiary=subsidiary)

        # 4. Register into Topic Engine (Module 4)
        full_text = " ".join(p["text"] for p in pages)
        topic_engine.add_document(text=full_text, source=filename, subsidiary=subsidiary)

        elapsed = round(time.time() - t_start, 2)
        size_kb = round(len(file_bytes) / 1024, 1)
        ocr_method = "vision" if ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"} else "native"

        # 5. Persist record in Database
        existing_doc = db.query(Document).filter(Document.filename == filename).first()
        if existing_doc:
            existing_doc.storage_path = storage_path
            existing_doc.subsidiary = subsidiary
            existing_doc.category = doc_category
            existing_doc.financial_year = financial_year
            existing_doc.description = description
            existing_doc.pages = len(pages)
            existing_doc.chunks = len(chunks)
            existing_doc.file_size_kb = size_kb
            existing_doc.ocr_method = ocr_method
            existing_doc.uploaded_at = datetime.utcnow()
            doc_id = existing_doc.id
        else:
            new_doc = Document(
                filename=filename,
                storage_path=storage_path,
                subsidiary=subsidiary,
                category=doc_category,
                financial_year=financial_year,
                description=description,
                pages=len(pages),
                chunks=len(chunks),
                file_size_kb=size_kb,
                ocr_method=ocr_method,
                uploaded_by_id=current_user.id if current_user else None,
            )
            db.add(new_doc)
            db.commit()
            db.refresh(new_doc)
            doc_id = new_doc.id

        db.commit()

        return {
            "status": "ok",
            "doc_id": doc_id,
            "filename": filename,
            "subsidiary": subsidiary,
            "doc_category": doc_category,
            "pages": len(pages),
            "chunks": len(chunks),
            "indexed_chunks": indexed,
            "upload_time_sec": elapsed,
            "file_size_kb": size_kb,
            "storage_type": storage_type,
            "storage_path": storage_path,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.get(
    "/api/documents",
    tags=["Module 1 — Admin Ingestion"],
    summary="List all indexed documents with metadata from DB",
)
async def get_documents(
    subsidiary: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        q = db.query(Document)
        if subsidiary and subsidiary.lower() not in ("all", "all subsidiaries"):
            q = q.filter(Document.subsidiary == subsidiary)
        if category and category.lower() != "all":
            q = q.filter(Document.category == category)

        docs = q.order_by(Document.uploaded_at.desc()).all()
        result = [
            {
                "id": d.id,
                "filename": d.filename,
                "subsidiary": d.subsidiary,
                "doc_category": d.category,
                "financial_year": d.financial_year or "—",
                "description": d.description or "",
                "pages": d.pages,
                "chunks": d.chunks,
                "file_size_kb": d.file_size_kb,
                "ocr_method": d.ocr_method,
                "storage_path": d.storage_path,
                "uploaded_at": d.uploaded_at.strftime("%d %b %Y, %I:%M %p") if d.uploaded_at else "—",
                "status": "Indexed ✓",
            }
            for d in docs
        ]
        return {"status": "ok", "total": len(result), "documents": result}
    except Exception as e:
        return {"status": "ok", "total": 0, "documents": [], "error": str(e)}


@app.get(
    "/api/documents/{filename}/preview",
    tags=["Module 1 — Admin Ingestion"],
    summary="Preview extracted text of a document",
)
async def preview_document(filename: str = FPath(...), db: Session = Depends(get_db)):
    try:
        preview = get_document_preview(filename)
        doc = db.query(Document).filter(Document.filename == filename).first()
        return {
            "status": "ok",
            "filename": filename,
            "subsidiary": doc.subsidiary if doc else "General",
            "doc_category": doc.category if doc else "Other",
            "pages": doc.pages if doc else 0,
            "chunks": doc.chunks if doc else 0,
            "preview": preview,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/api/documents/{filename}",
    tags=["Module 1 — Admin Ingestion"],
    summary="Delete a document from DB, Vector Store, and Storage",
)
async def delete_document_endpoint(filename: str = FPath(...), db: Session = Depends(get_db)):
    try:
        # Delete from ChromaDB
        delete_source(filename)

        # Delete file from disk/cloud
        delete_file(filename)

        # Delete from Database
        doc = db.query(Document).filter(Document.filename == filename).first()
        if doc:
            db.delete(doc)
            db.commit()

        return {"status": "ok", "message": f"'{filename}' deleted from database and storage."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/admin/metrics",
    tags=["Module 1 — Admin Ingestion"],
    summary="Admin ingestion health metrics",
)
async def get_admin_metrics(db: Session = Depends(get_db)):
    try:
        docs = db.query(Document).all()
        stats = get_collection_stats()

        by_subsidiary: dict[str, int] = {}
        by_category: dict[str, int] = {}
        by_method: dict[str, int] = {}

        total_pages = 0
        total_size = 0.0

        for d in docs:
            by_subsidiary[d.subsidiary] = by_subsidiary.get(d.subsidiary, 0) + 1
            by_category[d.category] = by_category.get(d.category, 0) + 1
            by_method[d.ocr_method] = by_method.get(d.ocr_method, 0) + 1
            total_pages += d.pages or 0
            total_size += d.file_size_kb or 0.0

        return {
            "status": "ok",
            "summary": {
                "total_documents": len(docs),
                "total_chunks": stats.get("total", 0),
                "total_pages": total_pages,
                "total_size_kb": round(total_size, 1),
            },
            "by_subsidiary": by_subsidiary,
            "by_category": by_category,
            "by_ocr_method": by_method,
            "recent_uploads": [
                {
                    "filename": d.filename,
                    "subsidiary": d.subsidiary,
                    "uploaded_at": d.uploaded_at.strftime("%d %b %Y, %I:%M %p") if d.uploaded_at else "—"
                }
                for d in docs[-5:]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/admin/clear", tags=["Module 1 — Admin Ingestion"], summary="[DANGER] Clear knowledge base")
async def clear_knowledge_base(db: Session = Depends(get_db)):
    try:
        clear_collection()
        topic_engine.reset()
        db.query(Document).delete()
        db.commit()
        return {"status": "ok", "message": "Knowledge base and database documents cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
#  MODULE 4: WORD CLOUD & TOPIC IDENTIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

@app.get(
    "/api/topics/wordcloud",
    tags=["Module 4 — Word Cloud & Topics"],
    summary="Word cloud frequency data for all indexed documents",
)
async def get_wordcloud(
    subsidiary: Optional[str] = Query(default=None),
    top_n: int = Query(default=100, ge=10, le=300),
):
    data = topic_engine.get_wordcloud_data(subsidiary=subsidiary, top_n=top_n)
    return {
        "status": "ok",
        "count": len(data),
        "subsidiary_filter": subsidiary or "All",
        "wordcloud": data,
    }


@app.get(
    "/api/topics/clusters",
    tags=["Module 4 — Word Cloud & Topics"],
    summary="Thematic topic clusters across CIL documents",
)
async def get_topic_clusters(subsidiary: Optional[str] = Query(default=None)):
    clusters = topic_engine.get_topic_clusters(subsidiary=subsidiary)
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
)
async def get_per_document_keywords(top_n: int = Query(default=10, ge=5, le=30)):
    data = topic_engine.get_per_document_keywords(top_n=top_n)
    return {"status": "ok", "total_documents": len(data), "documents": data}


@app.get(
    "/api/topics/insights",
    tags=["Module 4 — Word Cloud & Topics"],
    summary="AI-generated intelligence briefing from topics",
)
async def get_topic_insights(subsidiary: Optional[str] = Query(default=None)):
    try:
        insights = topic_engine.get_ai_insights(subsidiary=subsidiary)
        return {"status": "ok", "subsidiary_filter": subsidiary or "All", "insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════════
#  TEAM MEMBER STUBS: MODULES 2, 3, 5
# ═══════════════════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    query: str = Field(..., example="What was the total coal production of SECL in 2022-23?")
    subsidiary: Optional[str] = Field(default=None, example="SECL")
    top_k: int = Field(default=5, ge=1, le=20)

@app.post("/api/chat", tags=["Module 3 — RAG Q&A (Team Member)"], summary="RAG Question & Answer with Citations")
async def chat(req: ChatRequest):
    return JSONResponse(
        status_code=501,
        content={"status": "not_implemented", "message": "Module 3 implemented by team member. Replace this stub."}
    )

@app.post("/api/chat/clear", tags=["Module 3 — RAG Q&A (Team Member)"], summary="Clear chat history")
async def clear_chat():
    return JSONResponse(status_code=501, content={"status": "not_implemented"})


class ReportRequest(BaseModel):
    report_type: str = Field(default="parliamentary")
    subsidiary: str = Field(default="All Subsidiaries")
    keywords: str = Field(default="")
    financial_year: str = Field(default="")

@app.post("/api/generate-report", tags=["Module 2 — Reports (Team Member)"], summary="Generate CIL Report")
async def generate_report(req: ReportRequest):
    return JSONResponse(
        status_code=501,
        content={"status": "not_implemented", "message": "Module 2 implemented by team member. Replace this stub."}
    )

@app.get("/api/reports/templates", tags=["Module 2 — Reports (Team Member)"], summary="Report templates")
async def get_report_templates():
    return {
        "status": "ok",
        "templates": [
            {"id": "parliamentary", "label": "Parliamentary Inquiry Response"},
            {"id": "monthly_production", "label": "Monthly Coal Production & Offtake Summary"},
            {"id": "geological_reserve", "label": "Geological Exploration & Reserve Estimate"},
            {"id": "ob_removal", "label": "Overburden Removal & Stripping Ratio Analytics"},
            {"id": "safety", "label": "Mines Safety & Statutory Compliance"},
        ]
    }


@app.get("/api/analytics/summary", tags=["Module 5 — Analytics (Team Member)"], summary="Executive KPIs")
async def get_analytics_summary(db: Session = Depends(get_db)):
    try:
        stats = get_collection_stats()
        docs = db.query(Document).all()
        return {
            "status": "ok",
            "kpis": {
                "total_documents_indexed": len(docs),
                "total_chunks": stats.get("total", 0),
                "total_pages": sum(d.pages or 0 for d in docs),
            },
        }
    except Exception as e:
        return {"status": "ok", "kpis": {}, "error": str(e)}

@app.get("/api/analytics/subsidiaries", tags=["Module 5 — Analytics (Team Member)"], summary="Subsidiary breakdown")
async def get_subsidiary_analytics():
    return JSONResponse(status_code=501, content={"status": "not_implemented"})


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("  CMPDI GeoAI Hub v2.1  |  SIH 2024  |  Problem ID: 26023")
    print("  Ministry of Coal / CIL / CMPDI")
    print("=" * 60)
    print("  Local API:   http://localhost:8000")
    print("  Swagger UI:  http://localhost:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
