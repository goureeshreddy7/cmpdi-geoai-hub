"""
Database connection and session management for CMPDIPS spatial module.
Supports PostgreSQL (Neon) or SQLite (fallback for local dev).
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load .env if present
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL and DATABASE_URL.startswith("postgre"):
    db_url = DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    from sqlalchemy.pool import NullPool
    engine = create_engine(db_url, echo=False, poolclass=NullPool)
    DB_TYPE = "postgresql"
else:
    ROOT_DIR = Path(__file__).parent.parent
    data_path = ROOT_DIR / "cmpdi_hub.db"
    DATABASE_URL = f"sqlite:///{data_path}"
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
    DB_TYPE = "sqlite"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and auto-closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
