-- CMPDIPS Database Schema
-- Requires PostgreSQL with PostGIS extension

CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================
-- MINES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS mines (
    mine_id     VARCHAR(64) PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    subsidiary  VARCHAR(64),
    state       VARCHAR(128),
    district    VARCHAR(128),
    type        VARCHAR(32) CHECK (type IN ('Opencast', 'Underground', 'Mixed')),
    latitude    DOUBLE PRECISION NOT NULL,
    longitude   DOUBLE PRECISION NOT NULL,
    location    GEOMETRY(Point, 4326)
);

-- Spatial GIST index for fast geo-queries
CREATE INDEX IF NOT EXISTS idx_mines_location ON mines USING GIST (location);

-- B-tree indexes for filter columns
CREATE INDEX IF NOT EXISTS idx_mines_state ON mines (state);
CREATE INDEX IF NOT EXISTS idx_mines_subsidiary ON mines (subsidiary);
CREATE INDEX IF NOT EXISTS idx_mines_type ON mines (type);

-- ============================================
-- REPORTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS reports (
    report_id        VARCHAR(64) PRIMARY KEY,
    mine_id          VARCHAR(64) NOT NULL REFERENCES mines(mine_id) ON DELETE CASCADE,
    title            VARCHAR(512) NOT NULL,
    year             INTEGER NOT NULL,
    format           VARCHAR(128),
    confidence_score FLOAT DEFAULT 0.95,
    production_ytd   VARCHAR(64),
    content          TEXT
);

CREATE INDEX IF NOT EXISTS idx_reports_mine_id ON reports (mine_id);
CREATE INDEX IF NOT EXISTS idx_reports_year ON reports (year);

-- ============================================
-- TRIGGER: auto-populate location geometry
-- ============================================
CREATE OR REPLACE FUNCTION set_mine_location()
RETURNS TRIGGER AS $$
BEGIN
    NEW.location := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_mine_location ON mines;
CREATE TRIGGER trg_set_mine_location
    BEFORE INSERT OR UPDATE ON mines
    FOR EACH ROW
    EXECUTE FUNCTION set_mine_location();
