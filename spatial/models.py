"""
SQLAlchemy ORM models for CMPDIPS spatial mine intelligence — mines and reports.
Supports both PostgreSQL (with PostGIS geometry) and SQLite (lat/lon only).
"""

from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, Double
from sqlalchemy.orm import relationship
from spatial.database import Base, DB_TYPE

# Only use GeoAlchemy2 geometry if on PostgreSQL
if DB_TYPE == "postgresql":
    try:
        from geoalchemy2 import Geometry
        location_col = Column(Geometry("POINT", srid=4326))
    except ImportError:
        location_col = None
else:
    location_col = None


class Mine(Base):
    __tablename__ = "mines"

    mine_id    = Column(String(64), primary_key=True)
    name       = Column(String(255), nullable=False)
    subsidiary = Column(String(64))
    state      = Column(String(128))
    district   = Column(String(128))
    type       = Column(String(32))
    latitude   = Column(Double, nullable=False)
    longitude  = Column(Double, nullable=False)

    reports = relationship("Report", back_populates="mine", cascade="all, delete-orphan")


# Add geometry column only for PostgreSQL
if DB_TYPE == "postgresql" and location_col is not None:
    try:
        from geoalchemy2 import Geometry
        Mine.location = Column(Geometry("POINT", srid=4326))
    except Exception:
        pass


class Report(Base):
    __tablename__ = "reports"

    report_id        = Column(String(64), primary_key=True)
    mine_id          = Column(String(64), ForeignKey("mines.mine_id", ondelete="CASCADE"), nullable=False)
    title            = Column(String(512), nullable=False)
    year             = Column(Integer, nullable=False)
    format           = Column(String(128))
    confidence_score = Column(Float, default=0.95)
    production_ytd   = Column(String(64))
    content          = Column(Text)

    mine = relationship("Mine", back_populates="reports")
