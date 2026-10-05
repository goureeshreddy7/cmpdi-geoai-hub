/**
 * @file reportsRepository.js
 * @description Single Data Access Layer interface and implementations for RSHPS Reports Center.
 * UI components NEVER access mock data directly — they only call this repository interface.
 */

class IReportsRepository {
    /**
     * List all coal subsidiaries
     * @returns {Promise<Subsidiary[]>}
     */
    async listSubsidiaries() { throw new Error('Not implemented'); }

    /**
     * List areas within a subsidiary
     * @param {string} subsidiaryId
     * @returns {Promise<Area[]>}
     */
    async listAreas(subsidiaryId) { throw new Error('Not implemented'); }

    /**
     * List mines with optional hierarchy and metadata filters
     * @param {Object} [filter]
     * @param {string[]} [filter.subsidiaryIds]
     * @param {string[]} [filter.areaIds]
     * @param {string} [filter.coalfield]
     * @param {string} [filter.mineType]
     * @param {string} [filter.search]
     * @returns {Promise<Mine[]>}
     */
    async listMines(filter) { throw new Error('Not implemented'); }

    /**
     * Retrieve time-series metric data for selected mines
     * @param {Object} params
     * @param {string[]} params.mineIds
     * @param {string[]} params.metrics - e.g. ['production', 'offtake', 'ob_removal', 'stripping_ratio', 'hemm_utilisation', 'oms', 'accidents']
     * @param {string} [params.period] - e.g. 'FY24-25', 'Q1', 'Month', 'Custom'
     * @param {string} [params.startDate] - YYYY-MM
     * @param {string} [params.endDate] - YYYY-MM
     * @returns {Promise<Record<string, Record<string, MetricPoint[]>>>}
     */
    async getMineMetrics(params) { throw new Error('Not implemented'); }

    /**
     * List indexed technical documents and reports
     * @param {Object} [params]
     * @param {string[]} [params.mineIds]
     * @param {string[]} [params.subsidiaryIds]
     * @param {string} [params.type]
     * @param {string} [params.search]
     * @returns {Promise<Document[]>}
     */
    async listDocuments(params) { throw new Error('Not implemented'); }

    /**
     * Fetch document by ID
     * @param {string} id
     * @returns {Promise<Document|null>}
     */
    async getDocument(id) { throw new Error('Not implemented'); }

    /**
     * Compute data coverage, detect missing periods and stale reporting
     * @param {Object} params
     * @param {string[]} params.mineIds
     * @param {string[]} [params.metrics]
     * @param {string} [params.startDate]
     * @param {string} [params.endDate]
     * @returns {Promise<CoverageReport>}
     */
    async getDataCoverage(params) { throw new Error('Not implemented'); }

    /**
     * Save a report configuration template
     * @param {ReportConfig} config
     * @returns {Promise<ReportConfig>}
     */
    async saveReportConfig(config) { throw new Error('Not implemented'); }

    /**
     * List all saved report configuration templates
     * @returns {Promise<ReportConfig[]>}
     */
    async listReportConfigs() { throw new Error('Not implemented'); }

    /**
     * Delete a saved report configuration template
     * @param {string} id
     * @returns {Promise<boolean>}
     */
    async deleteReportConfig(id) { throw new Error('Not implemented'); }
}

/**
 * Mock implementation of ReportsRepository reading from in-memory fixtures.
 */
class MockReportsRepository extends IReportsRepository {
    constructor() {
        super();
        this.dataSource = 'mock';
        this.storageKey = 'cmpdi_saved_report_configs';
    }

    async listSubsidiaries() {
        await this._simulateDelay(20);
        return [...MOCK_SUBSIDIARIES];
    }

    async listAreas(subsidiaryId) {
        await this._simulateDelay(20);
        if (!subsidiaryId || subsidiaryId === 'ALL') {
            return [...MOCK_AREAS];
        }
        return MOCK_AREAS.filter(a => a.subsidiaryId === subsidiaryId);
    }

    async listMines(filter = {}) {
        await this._simulateDelay(30);
        let results = [...MOCK_MINES];

        if (filter.subsidiaryIds && filter.subsidiaryIds.length > 0 && !filter.subsidiaryIds.includes('ALL')) {
            results = results.filter(m => filter.subsidiaryIds.includes(m.subsidiary));
        }

        if (filter.areaIds && filter.areaIds.length > 0) {
            results = results.filter(m => filter.areaIds.includes(m.area));
        }

        if (filter.coalfield && filter.coalfield !== 'ALL') {
            results = results.filter(m => m.coalfield.toLowerCase().includes(filter.coalfield.toLowerCase()));
        }

        if (filter.mineType && filter.mineType !== 'ALL') {
            results = results.filter(m => m.type.toLowerCase() === filter.mineType.toLowerCase());
        }

        if (filter.search && filter.search.trim()) {
            const q = filter.search.toLowerCase().trim();
            results = results.filter(m => 
                m.name.toLowerCase().includes(q) ||
                m.id.toLowerCase().includes(q) ||
                m.area.toLowerCase().includes(q) ||
                m.coalfield.toLowerCase().includes(q)
            );
        }

        return results;
    }

    async getMineMetrics({ mineIds = [], metrics = [], startDate = '2024-04', endDate = '2025-03' }) {
        await this._simulateDelay(40);
        const output = {};
        const targetMines = mineIds.length > 0 ? mineIds : MOCK_MINES.map(m => m.id);

        targetMines.forEach(mineId => {
            const mineData = MOCK_METRICS_TIME_SERIES[mineId] || {};
            output[mineId] = {};

            const requestedMetrics = metrics.length > 0 ? metrics : Object.keys(mineData);

            requestedMetrics.forEach(mKey => {
                const series = mineData[mKey] || [];
                // Filter by date range
                output[mineId][mKey] = series.filter(pt => {
                    return (!startDate || pt.period >= startDate) && (!endDate || pt.period <= endDate);
                });
            });
        });

        return output;
    }

    async listDocuments(params = {}) {
        await this._simulateDelay(30);
        let docs = [...MOCK_DOCUMENTS];

        if (params.subsidiaryIds && params.subsidiaryIds.length > 0 && !params.subsidiaryIds.includes('ALL')) {
            docs = docs.filter(d => params.subsidiaryIds.includes(d.subsidiary) || d.subsidiary === 'CIL' || d.subsidiary === 'CMPDI');
        }

        if (params.mineIds && params.mineIds.length > 0) {
            docs = docs.filter(d => !d.mineId || params.mineIds.includes(d.mineId));
        }

        if (params.type && params.type !== 'ALL') {
            docs = docs.filter(d => d.type.toLowerCase().includes(params.type.toLowerCase()));
        }

        if (params.search && params.search.trim()) {
            const q = params.search.toLowerCase().trim();
            docs = docs.map(d => {
                const matches = (d.extractedText.toLowerCase().match(new RegExp(q, 'g')) || []).length;
                const titleMatch = d.title.toLowerCase().includes(q) ? 5 : 0;
                return {
                    ...d,
                    exactMatchCount: matches + titleMatch
                };
            }).filter(d => d.exactMatchCount > 0);
            
            docs.sort((a, b) => (b.exactMatchCount || 0) - (a.exactMatchCount || 0));
        }

        return docs;
    }

    async getDocument(id) {
        await this._simulateDelay(20);
        return MOCK_DOCUMENTS.find(d => d.id === id) || null;
    }

    async getDataCoverage({ mineIds = [], startDate = '2024-04', endDate = '2025-03' }) {
        await this._simulateDelay(35);
        const targetMineIds = mineIds.length > 0 ? mineIds : MOCK_MINES.map(m => m.id);
        
        // Generate expected months list in date range
        const expectedMonths = MONTHS_24.filter(m => (!startDate || m >= startDate) && (!endDate || m <= endDate));
        const items = [];
        const summaryWarnings = [];

        let completeCount = 0;
        let partialCount = 0;
        let staleCount = 0;

        targetMineIds.forEach(mId => {
            const mine = MOCK_MINES.find(m => m.id === mId);
            if (!mine) return;

            const timeSeries = MOCK_METRICS_TIME_SERIES[mId]?.production || [];
            const availableMonths = timeSeries
                .filter(pt => expectedMonths.includes(pt.period))
                .map(pt => pt.period);

            const missingMonths = expectedMonths.filter(m => !availableMonths.includes(m));
            const isStale = !!mine.isStale || (mine.lastReportedMonth && mine.lastReportedMonth < '2024-12');

            let warning = null;
            if (missingMonths.length > 0 && isStale) {
                warning = `Missing ${missingMonths.length} months (${missingMonths.join(', ')}). Reporting stale since ${mine.lastReportedMonth}.`;
                staleCount++;
                partialCount++;
            } else if (missingMonths.length > 0) {
                warning = `Missing data for: ${missingMonths.join(', ')}`;
                partialCount++;
            } else if (isStale) {
                warning = `Reporting stale. Last synchronized ${mine.lastReportedMonth} (over 3 months old).`;
                staleCount++;
            } else {
                completeCount++;
            }

            items.push({
                mineId: mine.id,
                mineName: mine.name,
                subsidiary: mine.subsidiary,
                expectedMonths: expectedMonths.length,
                availableMonths: availableMonths.length,
                missingMonths,
                isStale,
                lastReported: mine.lastReportedMonth,
                warning
            });
        });

        if (partialCount > 0) {
            const affectedMines = items.filter(i => i.missingMonths.length > 0).map(i => i.mineName);
            summaryWarnings.push(`Data gaps detected across ${partialCount} mine(s): ${affectedMines.join(', ')}.`);
        }

        if (staleCount > 0) {
            const staleMines = items.filter(i => i.isStale).map(i => i.mineName);
            summaryWarnings.push(`${staleCount} mine(s) have stale reporting (>90 days without telemetry): ${staleMines.join(', ')}.`);
        }

        return {
            totalMines: targetMineIds.length,
            completeMines: completeCount,
            partialMines: partialCount,
            staleMines: staleCount,
            items,
            summaryWarnings,
            isClean: partialCount === 0 && staleCount === 0
        };
    }

    async saveReportConfig(config) {
        await this._simulateDelay(25);
        const configs = await this.listReportConfigs();
        const id = config.id || `cfg-${Date.now()}`;
        const newConfig = {
            ...config,
            id,
            createdAt: config.createdAt || new Date().toISOString()
        };

        const existingIdx = configs.findIndex(c => c.id === id);
        if (existingIdx >= 0) {
            configs[existingIdx] = newConfig;
        } else {
            configs.unshift(newConfig);
        }

        try {
            localStorage.setItem(this.storageKey, JSON.stringify(configs));
        } catch (e) {
            console.warn('LocalStorage save failed, using memory state:', e);
        }

        return newConfig;
    }

    async listReportConfigs() {
        await this._simulateDelay(20);
        try {
            const raw = localStorage.getItem(this.storageKey);
            if (raw) {
                return JSON.parse(raw);
            }
        } catch (e) {
            console.warn('LocalStorage read failed:', e);
        }
        return [...MOCK_SAVED_CONFIGS];
    }

    async deleteReportConfig(id) {
        await this._simulateDelay(20);
        const configs = (await this.listReportConfigs()).filter(c => c.id !== id);
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(configs));
        } catch (e) {
            console.warn('LocalStorage delete failed:', e);
        }
        return true;
    }

    _simulateDelay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

/**
 * Production Database Stub.
 * When REPORTS_DATA_SOURCE='database', this class connects to real backend APIs / SQL tables.
 */
class DatabaseReportsRepository extends IReportsRepository {
    constructor(apiBase = '/api/reports') {
        super();
        this.apiBase = apiBase;
        this.dataSource = 'database';
    }

    async listSubsidiaries() {
        // TODO: SELECT subsidiary_id, name, hq, state, count(mine_id) FROM subsidiaries GROUP BY subsidiary_id
        const resp = await fetch(`${this.apiBase}/subsidiaries`);
        if (!resp.ok) throw new Error('Failed to fetch subsidiaries from database');
        return resp.json();
    }

    async listAreas(subsidiaryId) {
        // TODO: SELECT area_id, subsidiary_id, area_name, coalfield FROM areas WHERE subsidiary_id = :subsidiaryId
        const resp = await fetch(`${this.apiBase}/areas?subsidiary_id=${encodeURIComponent(subsidiaryId || '')}`);
        if (!resp.ok) throw new Error('Failed to fetch areas from database');
        return resp.json();
    }

    async listMines(filter = {}) {
        // TODO: Query `mines` table joined with `seams` and `telemetry_status`
        const queryParams = new URLSearchParams(filter).toString();
        const resp = await fetch(`${this.apiBase}/mines?${queryParams}`);
        if (!resp.ok) throw new Error('Failed to fetch mines from database');
        return resp.json();
    }

    async getMineMetrics(params) {
        // TODO: Query time-series table `monthly_mine_metrics` with WHERE mine_id IN (...) AND period BETWEEN ...
        const resp = await fetch(`${this.apiBase}/metrics`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        if (!resp.ok) throw new Error('Failed to fetch metrics from database');
        return resp.json();
    }

    async listDocuments(params = {}) {
        // TODO: Query full-text search PostgreSQL `tsvector` or SQLite FTS5 table `technical_documents`
        const queryParams = new URLSearchParams(params).toString();
        const resp = await fetch(`${this.apiBase}/documents?${queryParams}`);
        if (!resp.ok) throw new Error('Failed to fetch documents from database');
        return resp.json();
    }

    async getDocument(id) {
        // TODO: SELECT * FROM technical_documents WHERE document_id = :id
        const resp = await fetch(`${this.apiBase}/documents/${encodeURIComponent(id)}`);
        if (!resp.ok) throw new Error(`Document ${id} not found in database`);
        return resp.json();
    }

    async getDataCoverage(params) {
        // TODO: Execute coverage verification query comparing expected date range vs COUNT(DISTINCT period) per mine
        const resp = await fetch(`${this.apiBase}/coverage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        if (!resp.ok) throw new Error('Failed to fetch data coverage report');
        return resp.json();
    }

    async saveReportConfig(config) {
        // TODO: INSERT INTO saved_report_configs (config_id, user_id, config_json, created_at) VALUES (...)
        const resp = await fetch(`${this.apiBase}/configs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        if (!resp.ok) throw new Error('Failed to save report configuration');
        return resp.json();
    }

    async listReportConfigs() {
        // TODO: SELECT * FROM saved_report_configs ORDER BY created_at DESC
        const resp = await fetch(`${this.apiBase}/configs`);
        if (!resp.ok) throw new Error('Failed to list report configurations');
        return resp.json();
    }

    async deleteReportConfig(id) {
        // TODO: DELETE FROM saved_report_configs WHERE config_id = :id
        const resp = await fetch(`${this.apiBase}/configs/${encodeURIComponent(id)}`, { method: 'DELETE' });
        return resp.ok;
    }
}

// ── REPOSITORY FACTORY ──
let activeReportsRepositoryInstance = null;

function getReportsRepository() {
    if (!activeReportsRepositoryInstance) {
        const sourceMode = (typeof window !== 'undefined' && window.REPORTS_DATA_SOURCE) || 'mock';
        if (sourceMode === 'database') {
            activeReportsRepositoryInstance = new DatabaseReportsRepository();
            console.info('[ReportsRepository] Initialized with Live Database Provider.');
        } else {
            activeReportsRepositoryInstance = new MockReportsRepository();
            console.info('[ReportsRepository] Initialized with Mock Provider (MOCK DATA).');
        }
    }
    return activeReportsRepositoryInstance;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        IReportsRepository,
        MockReportsRepository,
        DatabaseReportsRepository,
        getReportsRepository
    };
}
