"""
db/models.py
SQLAlchemy models for CMPDI GeoAI Hub:
- User (Email/Password, Google OAuth, Role: admin/user, Subsidiary)
- Document (Filename, Filepath/URL, Metadata, Extraction stats, Uploaded by)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from db.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Null if signed in via Google only
    name = Column(String(255), nullable=True)
    role = Column(String(50), default="user")  # 'admin' or 'user'
    subsidiary = Column(String(100), default="General")
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="uploader")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    storage_path = Column(String(500), nullable=False)  # local relative path or cloud storage URL
    subsidiary = Column(String(100), default="General", index=True)
    category = Column(String(100), default="Other", index=True)
    financial_year = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    pages = Column(Integer, default=1)
    chunks = Column(Integer, default=0)
    file_size_kb = Column(Float, default=0.0)
    ocr_method = Column(String(50), default="native")
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    uploader = relationship("User", back_populates="documents")
