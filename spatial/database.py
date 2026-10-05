"""
Database connection and session management for CMPDIPS spatial module.
Supports PostgreSQL (with PostGIS) or SQLite (fallback for local dev).
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Auto-detect: use PostgreSQL if configured, else fall back to SQLite
if DATABASE_URL and DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1) if DATABASE_URL.startswith("postgresql://") else DATABASE_URL, echo=False, pool_pre_ping=True)
    DB_TYPE = "postgresql"
else:
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(ROOT_DIR, "data", "cmpdips.db")
    root_path = os.path.join(ROOT_DIR, "cmpdips.db")
    if os.path.exists(data_path):
        SQLITE_PATH = data_path
    elif os.path.exists(root_path):
        SQLITE_PATH = root_path
    else:
        SQLITE_PATH = data_path
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
    engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
    DB_TYPE = "sqlite"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency â€” yields a DB session and auto-closes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

