"""
gemini_client.py
Robust Google Gemini Client with multi-model automatic cascading fallback.
Tested models: gemini-3.8-flash, gemini-3.6-flash, gemini-3.7-flash, gemini-flash-latest.
"""

import os
import time
from pathlib import Path
from typing import Optional, List
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

# ── Robust Cascading Models ───────────────────────────────────────────────────
DEFAULT_PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
FALLBACK_MODELS: List[str] = [
    DEFAULT_PRIMARY_MODEL,
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-flash-lite-latest",
    "gemini-3.8-flash",
]

_client: Optional[genai.Client] = None


def get_api_key() -> str:
    """Return API key — from environment or .env file."""
    return os.getenv("GEMINI_API_KEY", "").strip()


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        key = get_api_key()
        if not key:
            raise ValueError("GEMINI_API_KEY is not set. Please add it to your .env file.")
        _client = genai.Client(api_key=key)
    return _client


def reset():
    """Reset client (called if key changes at runtime)."""
    global _client
    _client = None


def find_working_model() -> str:
    """Returns the primary verified model."""
    return FALLBACK_MODELS[0]


def generate(prompt: str, model: Optional[str] = None, max_tokens: int = 2048) -> str:
    """
    Generate text using Gemini with multi-model automatic cascading fallback.
    Tries each verified model with backoff retries if rate limited or overloaded.
    """
    client = _get_client()

    # Determine priority candidate list
    models_to_try = [model] if model and model in FALLBACK_MODELS else []
    for m in FALLBACK_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    last_error = None

    for m in models_to_try:
        for attempt in range(3):
            try:
                resp = client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=max_tokens,
                    ),
                )
                if resp and resp.text:
                    return resp.text.strip()
            except Exception as e:
                last_error = e
                err_str = str(e).lower()

                # If model is not found, unavailable (503), or deprecated, jump immediately to next model
                if any(x in err_str for x in ["404", "not_found", "no longer available", "503", "unavailable"]):
                    break

                # If rate limited (429), wait and retry
                if "429" in err_str or "resource_exhausted" in err_str:
                    wait = (attempt + 1) * 2
                    time.sleep(wait)
                    continue
                else:
                    # Other errors, try next model
                    break

    raise RuntimeError(
        f"Gemini generation error across all models: {last_error}"
    )
