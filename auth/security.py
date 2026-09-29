"""
auth/security.py
Authentication helpers:
- Password hashing with bcrypt
- JWT token creation and verification
- Firebase Google Auth token verification (free, no credit card)
- Legacy Google OAuth ID token verification (fallback)
"""
import os
import time
import bcrypt
import jwt
import requests
from typing import Optional, Dict

JWT_SECRET = os.getenv("JWT_SECRET", "cmpdi-geoai-hub-super-secret-key-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "72"))
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY", "")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(data: Dict, expires_hours: Optional[int] = None) -> str:
    """Generate a signed JWT token."""
    to_encode = data.copy()
    expire_time = time.time() + (expires_hours or JWT_EXPIRE_HOURS) * 3600
    to_encode.update({"exp": int(expire_time)})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict]:
    """Decode and verify a JWT token. Returns payload or None if invalid/expired."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        return None


def verify_firebase_token(id_token: str) -> Optional[Dict]:
    """
    Verify a Firebase ID token using Firebase's REST API.
    This is 100% FREE — no Google Cloud billing needed.
    Firebase handles Google OAuth sign-in internally.

    Returns user dict: {email, name, google_id, picture} or None.
    """
    if not FIREBASE_WEB_API_KEY:
        print("[Firebase] FIREBASE_WEB_API_KEY not set — skipping Firebase verification")
        return None
    try:
        # Use Firebase's token lookup endpoint
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_WEB_API_KEY}"
        resp = requests.post(url, json={"idToken": id_token}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            users = data.get("users", [])
            if not users:
                return None
            user = users[0]
            # Extract provider info (Google)
            provider_info = {}
            for p in user.get("providerUserInfo", []):
                if p.get("providerId") == "google.com":
                    provider_info = p
                    break
            return {
                "email": user.get("email", ""),
                "name": user.get("displayName") or provider_info.get("displayName") or user.get("email", "").split("@")[0],
                "google_id": user.get("localId"),
                "picture": user.get("photoUrl") or provider_info.get("photoUrl"),
            }
        else:
            print(f"[Firebase] Token verify failed: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[Firebase Auth Error] {e}")
    return None


def verify_google_token(id_token: str) -> Optional[Dict]:
    """
    Verify Google/Firebase ID token.
    Tries Firebase first (free, no card), then falls back to Google tokeninfo.
    Returns user dict: {email, name, google_id, picture} or None.
    """
    # Try Firebase first (free)
    if FIREBASE_WEB_API_KEY:
        result = verify_firebase_token(id_token)
        if result:
            return result

    # Fallback: Legacy Google OAuth tokeninfo (works if GOOGLE_CLIENT_ID is set)
    try:
        resp = requests.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}",
            timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            if GOOGLE_CLIENT_ID and data.get("aud") != GOOGLE_CLIENT_ID:
                return None
            return {
                "email": data.get("email"),
                "name": data.get("name") or data.get("email", "").split("@")[0],
                "google_id": data.get("sub"),
                "picture": data.get("picture"),
            }
    except Exception as e:
        print(f"[Google Auth Error] {e}")
    return None
