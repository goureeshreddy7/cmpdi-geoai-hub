"""
storage/store.py
Storage manager for document files:
- Default: Local disk storage in ./uploads/ (Zero configuration, completely free)
- Cloud (Vercel deployment): Supabase Storage (Free tier) if SUPABASE_URL & SUPABASE_KEY are provided.
"""
import os
import shutil
from pathlib import Path
from typing import Tuple

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "cil-documents")


def save_file(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """
    Save uploaded file bytes.
    Returns: (storage_path_or_url, storage_type: 'local' | 'cloud')
    """
    # Cloud mode (Supabase) if env vars are present
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            import requests
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/octet-stream",
            }
            upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}"
            resp = requests.post(upload_url, headers=headers, data=file_bytes, timeout=15)
            if resp.status_code in (200, 201):
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
                return public_url, "cloud"
        except Exception as e:
            print(f"[Supabase Upload Fallback] {e}")

    # Local fallback
    save_path = UPLOAD_DIR / filename
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    return str(save_path), "local"


def delete_file(filename: str):
    """Delete a stored file from local disk or cloud."""
    local_path = UPLOAD_DIR / filename
    if local_path.exists():
        try:
            local_path.unlink()
        except Exception:
            pass

    if SUPABASE_URL and SUPABASE_KEY:
        try:
            import requests
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
            }
            del_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}"
            requests.delete(del_url, headers=headers, timeout=10)
        except Exception:
            pass
