"""
gemini_client.py
Hard-coded to use gemini-3.6-flash with your API key.
Key is loaded from .env file automatically — no manual entry needed.
"""

import os
import time
from pathlib import Path
from typing import Optional
from google import genai
from google.genai import types

# ── Load .env automatically ───────────────────────────────────────────────────
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# ── Fixed config ───────────────────────────────────────────────────────────────
FIXED_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

_client: Optional[genai.Client] = None


def get_api_key() -> str:
    """Return API key — from environment or .env file."""
    return os.getenv("GEMINI_API_KEY", "").strip()



def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=get_api_key())
    return _client


def reset():
    """Reset client (called if key changes at runtime)."""
    global _client
    _client = None


def find_working_model() -> str:
    """Always returns the fixed working model."""
    return FIXED_MODEL


def generate(prompt: str, model: Optional[str] = None, max_tokens: int = 2048) -> str:
    """
    Generate text using gemini-3.6-flash.
    Retries up to 5 times with backoff on 503 (server busy).
    """
    client = _get_client()
    use_model = FIXED_MODEL  # Always use the fixed model — ignore any passed model arg

    for attempt in range(5):
        try:
            resp = client.models.generate_content(
                model=use_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=max_tokens,
                ),
            )
            return resp.text.strip()

        except Exception as e:
            err = str(e)

            if "503" in err or "UNAVAILABLE" in err:
                wait = (attempt + 1) * 4  # 4s, 8s, 12s, 16s, 20s
                print(f"[Gemini] Server busy (503) — retrying in {wait}s... (attempt {attempt+1}/5)")
                time.sleep(wait)
                continue

            elif "429" in err or "RESOURCE_EXHAUSTED" in err:
                wait = (attempt + 1) * 5
                print(f"[Gemini] Rate limited (429) — retrying in {wait}s...")
                time.sleep(wait)
                continue

            else:
                raise RuntimeError(f"Gemini error with {use_model}: {e}")

    raise RuntimeError(
        "Gemini is currently overloaded (503). Please wait 30 seconds and try again."
    )
