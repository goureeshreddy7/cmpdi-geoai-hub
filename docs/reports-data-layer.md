# RSHPS Reports Center: Data Access Layer Architecture (v1.0)

## 1. Overview & Core Architecture Rule
The Reports Center is engineered around a strict **Data Access Layer (DAL)** contract.
All UI components, builders, and live preview engines interact exclusively with the `ReportsRepository` interface.

```
┌────────────────────────────────────────────────────────┐
│               Report Builder UI Components             │
│   (Step Wizard, Live Preview, Provenance Drawer, Docs) │
└───────────────────────────┬────────────────────────────┘
                            │
               calls via ONE interface:
                  ReportsRepository
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
 ┌──────────────────────┐       ┌────────────────────────┐
 │ MockReportsRepository│       │DatabaseReportsRepository│
 │ (In-Memory Fixtures) │       │ (SQL Database / REST)  │
 └──────────────────────┘       └────────────────────────┘
```

> **Rule:** UI components **must never** import or reference mock fixtures directly. All data retrieval, filtering, and coverage calculations flow through `getReportsRepository()`.

---

## 2. Repository Interface Methods

| Method | Parameters | Returns | Description |
|---|---|---|---|
| `listSubsidiaries()` | `None` | `Promise<Subsidiary[]>` | Returns all CIL subsidiaries with metadata. |
| `listAreas(subsidiaryId)` | `subsidiaryId: string` | `Promise<Area[]>` | Lists operational areas belonging to a subsidiary. |
| `listMines(filter)` | `{ subsidiaryIds?, areaIds?, coalfield?, mineType?, search? }` | `Promise<Mine[]>` | Queries mines filtered by hierarchy and criteria. |
| `getMineMetrics(params)` | `{ mineIds, metrics, period?, startDate?, endDate? }` | `Promise<Record<mineId, Record<metric, MetricPoint[]>>>` | Time-series metrics with provenance `SourceRef`. |
| `listDocuments(params)` | `{ mineIds?, subsidiaryIds?, type?, search? }` | `Promise<Document[]>` | Full-text indexed documents with exact match counts. |
| `getDocument(id)` | `id: string` | `Promise<Document>` | Retrieves authenticating technical document. |
| `getDataCoverage(params)` | `{ mineIds, startDate?, endDate? }` | `Promise<CoverageReport>` | Identifies data completeness, missing months & stale telemetry. |
| `saveReportConfig(config)` | `config: ReportConfig` | `Promise<ReportConfig>` | Persists a report configuration template. |
| `listReportConfigs()` | `None` | `Promise<ReportConfig[]> | Lists saved report templates. |
| `deleteReportConfig(id)` | `id: string` | `Promise<boolean>` | Removes a saved template. |

---

## 3. Provenance & Source Tracking
Every numerical metric point returned carries a `SourceRef` object:
```javascript
{
  "period": "2024-08",
  "value": 5.85,
  "target": 5.72,
  "unit": "MT",
  "source": {
    "documentId": "SECL-GEVRA-OCP-2024",
    "page": 14,
    "asOfDate": "2024-08-28",
    "docTitle": "SECL Gevra Mega-Opencast Pit Phase-VI HEMM & Overburden Removal Audit",
    "table": "Section 4.1: Monthly Ledger for 2024-08"
  }
}
```
Clicking any number in the live preview opens the **Provenance Drawer**, showing the exact document title, page reference, and verification timestamp.

---

## 4. Switching from Mock to Database Provider

### Method A: Environment Variable / Server Switch
In production, set the environment variable:
```bash
REPORTS_DATA_SOURCE=database
```

### Method B: Runtime Frontend Toggle
Set the window variable before repository initialization:
```html
<script>
    window.REPORTS_DATA_SOURCE = 'database'; // or 'mock'
</script>
```

---

## 5. Database Schema Requirements for Production Deployment

To connect your live PostgreSQL / SQLite database to `DatabaseReportsRepository`, create or map the following tables:

### 1. `subsidiaries` Table
```sql
CREATE TABLE subsidiaries (
    subsidiary_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    hq VARCHAR(100),
    state VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. `areas` Table
```sql
CREATE TABLE areas (
    area_id VARCHAR(30) PRIMARY KEY,
    subsidiary_id VARCHAR(10) REFERENCES subsidiaries(subsidiary_id),
    name VARCHAR(100) NOT NULL,
    coalfield VARCHAR(100) NOT NULL
);
```

### 3. `mines` Table
```sql
CREATE TABLE mines (
    mine_id VARCHAR(30) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    subsidiary_id VARCHAR(10) REFERENCES subsidiaries(subsidiary_id),
    area_id VARCHAR(30) REFERENCES areas(area_id),
    coalfield VARCHAR(100) NOT NULL,
    type VARCHAR(20) CHECK (type IN ('Opencast', 'Underground', 'Mixed')),
    capacity_mty NUMERIC(6,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'Active',
    last_reported_month VARCHAR(7), -- Format: YYYY-MM
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. `mine_seams` Table
```sql
CREATE TABLE mine_seams (
    seam_id SERIAL PRIMARY KEY,
    mine_id VARCHAR(30) REFERENCES mines(mine_id),
    horizon_name VARCHAR(100) NOT NULL,
    thickness_m NUMERIC(5,2) NOT NULL,
    depth_m NUMERIC(6,2) NOT NULL,
    ash_percent NUMERIC(4,2) NOT NULL,
    gcv_kcal_kg INTEGER NOT NULL,
    grade VARCHAR(20) NOT NULL
);
```

### 5. `monthly_mine_metrics` Table (Time-Series)
```sql
CREATE TABLE monthly_mine_metrics (
    id BIGSERIAL PRIMARY KEY,
    mine_id VARCHAR(30) REFERENCES mines(mine_id),
    period VARCHAR(7) NOT NULL, -- Format: YYYY-MM
    metric_name VARCHAR(50) NOT NULL, -- 'production', 'offtake', 'ob_removal', 'stripping_ratio', 'hemm_utilisation', 'oms', 'accidents'
    value NUMERIC(12,4) NOT NULL,
    target NUMERIC(12,4),
    unit VARCHAR(20) NOT NULL,
    source_document_id VARCHAR(50),
    source_page INTEGER,
    as_of_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(mine_id, period, metric_name)
);
```

### 6. `technical_documents` Table
```sql
CREATE TABLE technical_documents (
    document_id VARCHAR(50) PRIMARY KEY,
    title TEXT NOT NULL,
    type VARCHAR(100) NOT NULL,
    subsidiary_id VARCHAR(10),
    mine_id VARCHAR(30),
    published_date VARCHAR(30),
    page_count INTEGER,
    extracted_text TEXT,
    file_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Optional Full Text Search Index:
CREATE INDEX idx_tech_docs_fts ON technical_documents USING gin(to_tsvector('english', extracted_text || ' ' || title));
```

### 7. `saved_report_configs` Table
```sql
CREATE TABLE saved_report_configs (
    config_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    query_type VARCHAR(30) NOT NULL,
    config_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 6. Non-Goals for V1 & Roadmap Extension Points
- **Approval Workflow**: Add multi-stage review (Draft -> Under Audit -> Signed by Advisor).
- **Scheduled Auto-Generation**: Cron pipeline to compile monthly briefs on the 1st of each month.
- **Multilingual Support (Hindi Output)**: Parliamentary questions bilingual export engine.
- **AI Narrative Synthesis**: Optional summarization layer with strict citation verification.
