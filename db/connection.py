"""
db/connection.py
Auto-detects: SQLite (local dev) or PostgreSQL/Neon (production on Vercel).
Set DATABASE_URL env var to switch to Neon/PostgreSQL.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# If DATABASE_URL is set → Neon/PostgreSQL. Else → local SQLite.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cmpdi_hub.db")

# PostgreSQL needs pool config; SQLite needs check_same_thread=False
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    # Neon free tier: use NullPool to avoid connection leaks in serverless
    from sqlalchemy.pool import NullPool
    engine = create_engine(DATABASE_URL, poolclass=NullPool)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    from db.models import User, Document  # noqa: F401
    Base.metadata.create_all(bind=engine)
