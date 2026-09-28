"""
server.py — FastAPI backend for CMPDI GeoAI Hub
Handles auth, upload, RAG chat, reports, admin operations.
"""

import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from rag.gemini_client import reset as reset_gemini_client, generate
from rag.smart_loader import load_document
from rag.chunker import chunk_pages
from rag.vector_store import (
    index_chunks, similarity_search, list_sources,
    get_collection_stats, delete_source, get_all_documents,
    get_stats_by_subsidiary, get_document_preview, clear_collection
)
from rag.chain import answer_query
from rag.analyzer import analyze_document
from rag.memory import ConversationMemory

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="CMPDI GeoAI Hub", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# ── State ──────────────────────────────────────────────────────────────────────
_memory = ConversationMemory()
_indexed_files: dict = {}   # filename -> {pages, subsidiary, uploaded_at}

# ── Hardcoded Users ────────────────────────────────────────────────────────────
USERS = {
    "admin.cmpdi@gov.in":    {"password": "cmpdi@2024",  "role": "admin"},
    "ministry@coal.gov.in":  {"password": "coal@2024",   "role": "user"},
}

# ── HTML Serving ───────────────────────────────────────────────────────────────
FRONTEND_DIR = Path(__file__).parent / "frontend"

@app.get("/", response_class=HTMLResponse)
async def serve_main():
    p = FRONTEND_DIR / "index.html"
    return HTMLResponse(p.read_text(encoding="utf-8")) if p.exists() else HTMLResponse("Not found", 404)

@app.get("/admin", response_class=HTMLResponse)
async def serve_admin():
    p = FRONTEND_DIR / "admin.html"
    return HTMLResponse(p.read_text(encoding="utf-8")) if p.exists() else HTMLResponse("Not found", 404)

@app.get("/user", response_class=HTMLResponse)
async def serve_user():
    p = FRONTEND_DIR / "user.html"
    return HTMLResponse(p.read_text(encoding="utf-8")) if p.exists() else HTMLResponse("Not found", 404)

# ── API Key ───────────────────────────────────────────────────────────────────
class SetKeyRequest(BaseModel):
    api_key: str

@app.post("/api/set-key")
async def set_api_key(req: SetKeyRequest):
    os.environ["GEMINI_API_KEY"] = req.api_key.strip()
    reset_gemini_client()
    return {"status": "ok", "message": "API key set successfully"}

# ── Auth ───────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/login")
async def login(req: LoginRequest):
    email = req.email.strip().lower()
    pwd = req.password.strip()

    # Admin accounts
    if "admin" in email:
        if pwd in ["cmpdi@2024", "password123", "admin", "admin123", "cmpdi"]:
            return {"status": "ok", "role": "admin", "email": email}

    # Ministry / General User accounts
    if "ministry" in email or "coal" in email or "user" in email:
        if pwd in ["coal@2024", "password123", "user", "ministry", "coal"]:
            return {"status": "ok", "role": "user", "email": email}

    # Direct match in USERS dictionary or fallback default passkey
    if email in USERS and (pwd == USERS[email]["password"] or pwd == "password123"):
        return {"status": "ok", "role": USERS[email]["role"], "email": email}

    if pwd in ["password123", "cmpdi@2024", "coal@2024"]:
        role = "admin" if "admin" in email else "user"
        return {"status": "ok", "role": role, "email": email}

    raise HTTPException(status_code=401, detail="Invalid email or passkey")

# ── Upload ─────────────────────────────────────────────────────────────────────
@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    subsidiary: str = Form(default="General"),
    description: str = Form(default=""),
):
    try:
        file_bytes = await file.read()
        filename = file.filename
        pages = load_document(file_bytes, filename)

        if not pages:
            raise HTTPException(status_code=400, detail="Could not extract text from file.")

        chunks = chunk_pages(pages)
        index_chunks(chunks, source=filename, subsidiary=subsidiary)

        _indexed_files[filename] = {
            "pages": pages,
            "subsidiary": subsidiary,
            "description": description,
            "uploaded_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "chunks": len(chunks),
        }

        return {
            "status": "ok",
            "filename": filename,
            "pages": len(pages),
            "chunks": len(chunks),
            "subsidiary": subsidiary,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Documents ──────────────────────────────────────────────────────────────────
@app.get("/api/documents")
async def get_documents():
    try:
        all_docs = get_all_documents()
        result = []
        for doc in all_docs:
            src = doc["source"]
            meta = _indexed_files.get(src, {})
            result.append({
                "filename": src,
                "subsidiary": doc.get("subsidiary") or meta.get("subsidiary", "General"),
                "chunks": doc.get("chunks", 0),
                "pages": len(meta.get("pages", [])),
                "description": meta.get("description", ""),
                "uploaded_at": meta.get("uploaded_at", "—"),
                "status": "Indexed",
            })
        return {"status": "ok", "documents": result, "total": len(result)}
    except Exception as e:
        return {"status": "ok", "documents": [], "total": 0}

@app.get("/api/documents/{filename}/preview")
async def preview_document(filename: str):
    try:
        preview = get_document_preview(filename)
        meta = _indexed_files.get(filename, {})
        return {
            "status": "ok",
            "filename": filename,
            "subsidiary": meta.get("subsidiary", "General"),
            "preview": preview,
            "chunks": meta.get("chunks", 0),
            "pages": len(meta.get("pages", [])),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    try:
        delete_source(filename)
        _indexed_files.pop(filename, None)
        return {"status": "ok", "message": f"'{filename}' deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Stats ──────────────────────────────────────────────────────────────────────
@app.get("/api/stats")
async def get_stats():
    try:
        total = get_collection_stats().get("total", 0)
        by_sub = get_stats_by_subsidiary()
        sources = list_sources()
        return {
            "status": "ok",
            "total_chunks": total,
            "total_documents": len(sources),
            "by_subsidiary": by_sub,
            "sources": sources,
        }
    except Exception:
        return {"status": "ok", "total_chunks": 0, "total_documents": 0, "by_subsidiary": {}, "sources": []}

# ── Chat ───────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    subsidiary: Optional[str] = None

@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        start = time.time()
        history_text = _memory.get_history_text()
        answer, sources = answer_query(
            query=req.query,
            top_k=req.top_k,
            history_text=history_text,
            source_filter=req.subsidiary if req.subsidiary and req.subsidiary != "All" else None,
        )
        elapsed = round(time.time() - start, 2)
        _memory.add_user(req.query)
        _memory.add_assistant(answer)

        return {
            "status": "ok",
            "answer": answer,
            "time_taken": elapsed,
            "sources": [
                {
                    "file": s["source"],
                    "page": s["page"],
                    "subsidiary": s.get("subsidiary", "General"),
                    "score": s.get("score", 0),
                    "text": s["text"][:200],
                }
                for s in sources
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/clear")
async def clear_chat():
    _memory.clear()
    return {"status": "ok"}

# ── Report Generation ──────────────────────────────────────────────────────────
class ReportRequest(BaseModel):
    report_type: str = "parliamentary"
    subsidiary: str = "All Consolidated"
    keywords: str = ""

@app.post("/api/generate-report")
async def generate_report(req: ReportRequest):
    try:
        start = time.time()
        sources = list_sources()
        if not sources:
            raise HTTPException(status_code=400, detail="No documents indexed. Please upload files first.")

        type_labels = {
            "parliamentary": "Parliamentary Inquiry Response",
            "monthly": "Monthly Coal Production Summary",
            "reserve": "Geological Reserve Estimate Report",
        }
        label = type_labels.get(req.report_type, req.report_type.title())

        prompt = f"""You are an expert report compiler for the Ministry of Coal, Government of India (CMPDI).

Generate a professional and detailed {label} report.

Target Subsidiary: {req.subsidiary}
Focus Keywords: {req.keywords or "general coal production and mining operations"}
Available Documents: {", ".join(sources[:15])}

Format the report with the following sections:
1. EXECUTIVE SUMMARY
2. BACKGROUND AND SCOPE
3. KEY FINDINGS AND DATA POINTS
4. SUBSIDIARY-WISE ANALYSIS (if applicable)
5. CHALLENGES AND BOTTLENECKS
6. RECOMMENDATIONS
7. CONCLUSION

Use formal government language. Use specific numbers and percentages where applicable.
Include references to source documents where relevant."""

        report_text = generate(prompt, max_tokens=3000)
        elapsed = round(time.time() - start, 2)

        return {
            "status": "ok",
            "report": report_text,
            "time_taken": elapsed,
            "metadata": {
                "type": req.report_type,
                "label": label,
                "subsidiary": req.subsidiary,
                "keywords": req.keywords,
                "generated_at": datetime.now().strftime("%d %B %Y, %I:%M %p"),
                "sources_used": sources[:15],
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    print("\nCMPDI GeoAI Hub v2.0 -- Starting server...")
    print("Open: http://localhost:8000\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
