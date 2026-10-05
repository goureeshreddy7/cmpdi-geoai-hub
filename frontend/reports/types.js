/**
 * @file types.js
 * @description Data model definitions and TypeScript/JSDoc types for RSHPS Reports Center Data Access Layer.
 * Every metric carries a SourceRef provenance object { documentId, page, asOfDate }.
 */

/**
 * @typedef {Object} SourceRef
 * @property {string} documentId - ID of the authenticating document (e.g. 'SECL-GEVRA-OCP-2024')
 * @property {number} page - Page number in the source document
 * @property {string} asOfDate - Reporting cutoff date (e.g. '2024-08-31')
 * @property {string} [table] - Table reference or section in source document
 * @property {string} [docTitle] - Title of the source document
 */

/**
 * @typedef {Object} Subsidiary
 * @property {string} id - Subsidiary identifier (e.g. 'SECL', 'NCL', 'MCL')
 * @property {string} name - Full subsidiary name (e.g. 'South Eastern Coalfields Limited')
 * @property {string} hq - Headquarters location (e.g. 'Bilaspur, Chhattisgarh')
 * @property {number} mineCount - Total registered operational mines
 * @property {string} state - Primary operating state(s)
 */

/**
 * @typedef {Object} Area
 * @property {string} id - Area code (e.g. 'SECL-KORBA', 'NCL-SINGRAULI')
 * @property {string} subsidiaryId - Parent subsidiary ID
 * @property {string} name - Area name
 * @property {string} coalfield - Primary coalfield basin
 */

/**
 * @typedef {Object} SeamData
 * @property {string} horizon - Seam name/horizon (e.g. 'Seam X (Top)')
 * @property {number} thickness - Thickness in meters
 * @property {number} depth - Mean depth in meters
 * @property {number} ashPercent - Ash content percentage
 * @property {number} gcv - Gross Calorific Value (kcal/kg)
 * @property {string} grade - Coal quality grade (e.g. 'G4', 'G6', 'G8')
 */

/**
 * @typedef {Object} Mine
 * @property {string} id - Unique mine ID (e.g. 'SECL-GEVRA-OCP')
 * @property {string} name - Mine name (e.g. 'Gevra OCP')
 * @property {string} subsidiary - Subsidiary ID (e.g. 'SECL')
 * @property {string} area - Area name
 * @property {string} coalfield - Coalfield basin
 * @property {'Opencast'|'Underground'|'Mixed'} type - Mining methodology
 * @property {number} capacity - Rated capacity in MTY (Million Tonnes per Year)
 * @property {string} status - Operational status ('Active'|'Expansion'|'Stale')
 * @property {string} lastReportedMonth - Last submitted reporting period (e.g. '2025-03')
 * @property {SeamData[]} [seams] - Geological coal seams breakdown
 */

/**
 * @typedef {Object} MetricPoint
 * @property {string} period - Month in YYYY-MM format (e.g. '2024-08')
 * @property {number} value - Metric numerical value
 * @property {number} target - Assigned target/budget value for the period
 * @property {string} unit - Measurement unit ('MT', 'Mcum', 'CuM/T', '%', 'Tonnes', 'Count')
 * @property {SourceRef} source - Provenance citation for this specific metric
 */

/**
 * @typedef {Object} Document
 * @property {string} id - Document identifier (e.g. 'SECL-GEVRA-OCP-2024')
 * @property {string} title - Full document title
 * @property {string} type - Document category ('Annual Mine Performance Audit', 'Parliamentary Inquiry Response', etc.)
 * @property {string} subsidiary - Subsidiary ID or 'CIL' / 'CMPDI'
 * @property {string} [mineId] - Associated mine ID if mine-specific
 * @property {string} publishedDate - Publication date (e.g. 'Aug 2024')
 * @property {number} pageCount - Number of pages
 * @property {string} extractedText - Text summary / extract for search match indexing
 * @property {Record<string, number>} [keywords] - Correlated keyword occurrences
 * @property {SeamData[]} [seamTable] - Associated geological seam data
 * @property {string} [fileUrl] - Path or URI to download/view the document file
 */

/**
 * @typedef {Object} DataCoverageItem
 * @property {string} mineId - Mine identifier
 * @property {string} mineName - Mine name
 * @property {string} subsidiary - Subsidiary ID
 * @property {number} expectedMonths - Number of expected monthly data points
 * @property {number} availableMonths - Number of present data points
 * @property {string[]} missingMonths - List of missing months in YYYY-MM
 * @property {boolean} isStale - True if last reported date is > 3 months old
 * @property {string} lastReported - Last reported period
 * @property {string} warning - Human-readable caveat message
 */

/**
 * @typedef {Object} CoverageReport
 * @property {number} totalMines - Total mines in query scope
 * @property {number} completeMines - Mines with 100% data availability
 * @property {number} partialMines - Mines with missing months
 * @property {number} staleMines - Mines with outdated reporting
 * @property {DataCoverageItem[]} items - Granular breakdown per mine
 * @property {string[]} summaryWarnings - High-level warning bullet points
 * @property {boolean} isClean - True if no missing months or stale reporting
 */

/**
 * @typedef {Object} ReportSectionConfig
 * @property {string} id - Section ID ('production', 'offtake', 'overburden', 'hemm', 'oms', 'safety', 'reserves', 'land', 'environment', 'financials')
 * @property {string} title - Section heading
 * @property {boolean} enabled - Whether included in the report
 * @property {'table'|'chart'|'narrative'|'table_chart'} presentation - Display format
 * @property {number} [thresholdHighlight] - Threshold value to flag/highlight in red/warning
 * @property {string} [customNarrative] - User-edited text narrative
 */

/**
 * @typedef {Object} ReportConfig
 * @property {string} [id] - Config ID (for saved templates)
 * @property {string} [name] - Template name (e.g. 'Monthly Gevra Review')
 * @property {'parliamentary'|'single_mine'|'subsidiary'|'comparison'} queryType - Report type
 * @property {Object} [parliamentaryMeta] - Lok Sabha / Rajya Sabha metadata
 * @property {string[]} subsidiaryIds - Selected subsidiary IDs
 * @property {string[]} mineIds - Selected mine IDs
 * @property {string} [coalfieldFilter] - Coalfield filter
 * @property {string} [mineTypeFilter] - Opencast / Underground filter
 * @property {string} periodType - 'FY24-25'|'Q1'|'Q2'|'Q3'|'Q4'|'Month'|'YTD'|'Custom'
 * @property {string} [startDate] - Start month (YYYY-MM)
 * @property {string} [endDate] - End month (YYYY-MM)
 * @property {string} [comparePeriod] - Comparison baseline period
 * @property {string} [sortBy] - Metric to sort by
 * @property {'asc'|'desc'} [sortDir] - Sort direction
 * @property {number} [topN] - Top/Bottom N limit
 * @property {ReportSectionConfig[]} sections - Enabled sections and presentation styles
 * @property {string[]} attachedSourceDocIds - Manually or automatically attached source documents
 * @property {string} createdAt - ISO timestamp
 */

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {};
}
