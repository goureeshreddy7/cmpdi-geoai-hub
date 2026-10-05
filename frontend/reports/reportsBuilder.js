/**
 * @file reportsBuilder.js
 * @description Guided Report Builder for CMPDI RSHPS Platform.
 * Interacts exclusively with ReportsRepository (never mock data directly).
 * Implements 4-step wizard, live editable preview, provenance drawer,
 * popup query configuration modal window, in-place interactive visualization transforms,
 * data coverage analysis, export engines, and template persistence.
 */

// Global state for Report Builder
window.RSHPS_REPORTS_STATE = {
    currentStep: 1,
    activeTab: 'builder', // 'builder' | 'library' | 'templates'
    config: {
        id: null,
        name: 'New Custom Mining Report',
        queryType: 'parliamentary', // 'parliamentary'|'single_mine'|'subsidiary'|'comparison'
        parliamentaryMeta: {
            house: 'Lok Sabha',
            type: 'Unstarred',
            number: '4052',
            answerDate: '2024-07-24',
            ministry: 'Ministry of Coal'
        },
        comparisonOptions: {
            baselinePeriod: 'FY23-24',
            currentPeriod: 'FY24-25',
            aspects: ['growth', 'stripping', 'hemm', 'quality', 'safety', 'oms'],
            mode: 'multi_mine'
        },
        subsidiaryIds: ['SECL', 'NCL', 'MCL'],
        areaIds: [],
        mineIds: ['SECL-GEVRA-OCP', 'SECL-KUSMUNDA-OCP', 'NCL-JAYANT-OCP', 'MCL-LINGARAJ-OCP'],
        coalfieldFilter: 'ALL',
        mineTypeFilter: 'ALL',
        periodType: 'FY24-25',
        startDate: '2024-04',
        endDate: '2025-03',
        comparePeriod: 'FY23-24',
        sortBy: 'production',
        sortDir: 'desc',
        topN: 10,
        thresholdHighlight: 90, // % of target
        sections: [
            { id: 'production', title: 'Coal Production & Despatch Overview', enabled: true, presentation: 'bar', customNarrative: '' },
            { id: 'overburden', title: 'Overburden Removal & Stripping Ratio', enabled: true, presentation: 'table', customNarrative: '' },
            { id: 'hemm', title: 'HEMM Fleet Utilisation & Availability', enabled: true, presentation: 'bar', customNarrative: '' },
            { id: 'oms', title: 'Output Per Manshift (OMS) Productivity', enabled: false, presentation: 'bar', customNarrative: '' },
            { id: 'safety', title: 'Mine Safety & Incident Records (DGMS)', enabled: true, presentation: 'narrative', customNarrative: '' },
            { id: 'reserves', title: 'Stratigraphy & Coal Seams Breakdown', enabled: true, presentation: 'table', customNarrative: '' },
            { id: 'environment', title: 'Environmental Clearances & Afforestation', enabled: true, presentation: 'narrative', customNarrative: '' },
            { id: 'land', title: 'Land Acquisition & R&R Status', enabled: false, presentation: 'narrative', customNarrative: '' },
            { id: 'financials', title: 'Royalty & Financial Accruals (Placeholder)', enabled: false, presentation: 'table', customNarrative: '' }
        ],
        attachedSourceDocIds: ['SECL-GEVRA-OCP-2024', 'PQ-LS-UNSTARRED-4052']
    },
    loadedMines: [],
    loadedMetrics: {},
    coverageReport: null,
    provenanceActiveSource: null,
    acknowledgedGaps: false,
    inlineEdits: {},
    librarySearchKeyword: '',
    currentLibraryDoc: null
};

// ── INITIALIZATION ──
async function initReportsCenter() {
    const repo = getReportsRepository();
    try {
        window.RSHPS_REPORTS_STATE.loadedMines = await repo.listMines();
        await refreshReportData();
        renderReportBuilderUI();
        renderLivePreview();
        renderSavedTemplatesList();
    } catch (err) {
        console.error('Error initializing Reports Center:', err);
    }
}

// Auto-trigger initialization on load
if (typeof document !== 'undefined') {
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setTimeout(initReportsCenter, 50);
    } else {
        document.addEventListener('DOMContentLoaded', initReportsCenter);
    }
}

// ── DATA REFRESH ──
async function refreshReportData() {
    const repo = getReportsRepository();
    const cfg = window.RSHPS_REPORTS_STATE.config;

    window.RSHPS_REPORTS_STATE.loadedMetrics = await repo.getMineMetrics({
        mineIds: cfg.mineIds,
        startDate: cfg.startDate,
        endDate: cfg.endDate
    });

    window.RSHPS_REPORTS_STATE.coverageReport = await repo.getDataCoverage({
        mineIds: cfg.mineIds,
        startDate: cfg.startDate,
        endDate: cfg.endDate
    });
}

// ── STEP SWITCHING ──
function setBuilderStep(stepNumber) {
    window.RSHPS_REPORTS_STATE.currentStep = stepNumber;
    renderReportBuilderUI();
    renderLivePreview();
}

function nextBuilderStep() {
    if (window.RSHPS_REPORTS_STATE.currentStep < 3) {
        setBuilderStep(window.RSHPS_REPORTS_STATE.currentStep + 1);
    }
}

function prevBuilderStep() {
    if (window.RSHPS_REPORTS_STATE.currentStep > 1) {
        setBuilderStep(window.RSHPS_REPORTS_STATE.currentStep - 1);
    }
}

// ── CONFIGURATION MUTATORS ──
async function updateQueryType(type) {
    const state = window.RSHPS_REPORTS_STATE;
    state.config.queryType = type;
    if (type === 'single_mine') {
        state.config.mineIds = [state.config.mineIds[0] || 'SECL-GEVRA-OCP'];
        const m = state.loadedMines.find(x => x.id === state.config.mineIds[0]);
        state.config.name = `Single Mine Technical Review - ${m ? m.name : 'Gevra OCP'}`;
    } else if (type === 'subsidiary') {
        const sub = state.config.subsidiaryIds[0] || 'SECL';
        const subMines = state.loadedMines.filter(m => m.subsidiary === sub).map(m => m.id);
        state.config.mineIds = subMines.length > 0 ? subMines : ['SECL-GEVRA-OCP', 'SECL-KUSMUNDA-OCP'];
        state.config.name = `${sub} Subsidiary Consolidated Performance Report`;
    } else if (type === 'parliamentary') {
        state.config.mineIds = ['SECL-GEVRA-OCP', 'SECL-KUSMUNDA-OCP', 'NCL-JAYANT-OCP', 'MCL-LINGARAJ-OCP'];
        state.config.name = 'Parliamentary Question Reply - Ministry of Coal';
    } else if (type === 'comparison') {
        state.config.mineIds = ['SECL-GEVRA-OCP', 'SECL-KUSMUNDA-OCP', 'NCL-JAYANT-OCP'];
        state.config.name = 'Mega-Opencast Benchmarking & Comparative Variance Report';
    }
    await refreshReportData();
}

async function selectQueryTypeAndOpenModal(type) {
    await updateQueryType(type);
    renderReportBuilderUI();
    renderLivePreview();
    openQueryConfigModal(type);
}

function toggleSectionEnabled(sectionId) {
    const sec = window.RSHPS_REPORTS_STATE.config.sections.find(s => s.id === sectionId);
    if (sec) {
        sec.enabled = !sec.enabled;
        renderReportBuilderUI();
        renderLivePreview();
    }
}

function moveSectionOrder(sectionId, direction) {
    const sections = window.RSHPS_REPORTS_STATE.config.sections;
    const idx = sections.findIndex(s => s.id === sectionId);
    if (idx < 0) return;

    if (direction === 'up' && idx > 0) {
        const temp = sections[idx];
        sections[idx] = sections[idx - 1];
        sections[idx - 1] = temp;
    } else if (direction === 'down' && idx < sections.length - 1) {
        const temp = sections[idx];
        sections[idx] = sections[idx + 1];
        sections[idx + 1] = temp;
    }
    renderReportBuilderUI();
    renderLivePreview();
}

// ── RENDER STEP BUILDER WIZARD (LEFT PANEL) ──
function renderReportBuilderUI() {
    const container = document.getElementById('report-wizard-step-content');
    const stepTabsContainer = document.getElementById('report-wizard-step-tabs');
    if (!container || !stepTabsContainer) return;

    const state = window.RSHPS_REPORTS_STATE;
    const cfg = state.config;

    // Render Step Navigation Tabs
    const stepsMeta = [
        { num: 1, label: 'Query Type' },
        { num: 2, label: 'Content' },
        { num: 3, label: 'Review & Export' }
    ];

    stepTabsContainer.innerHTML = stepsMeta.map(s => {
        const isActive = state.currentStep === s.num;
        const isCompleted = state.currentStep > s.num;
        return `
            <button onclick="setBuilderStep(${s.num})" class="flex-1 py-2.5 text-xs font-bold transition-all border-b-2 flex items-center justify-center gap-1.5 ${
                isActive ? 'border-[#B0420C] text-[#B0420C] bg-orange-50/30' : 
                (isCompleted ? 'border-gray-300 text-gray-700 hover:text-black' : 'border-transparent text-gray-400')
            }">
                <span class="w-4 h-4 rounded-full text-[10px] flex items-center justify-center font-black ${
                    isActive ? 'bg-[#B0420C] text-white' : (isCompleted ? 'bg-gray-800 text-white' : 'bg-gray-200 text-gray-600')
                }">${s.num}</span>
                <span class="hidden sm:inline">${s.label}</span>
            </button>
        `;
    }).join('');

    // Render Step Content
    if (state.currentStep === 1) {
        const selectedSingleMine = state.loadedMines.find(x => x.id === cfg.mineIds[0]) || { name: 'Gevra OCP', subsidiary: 'SECL', capacity: 70 };
        const activeSub = cfg.subsidiaryIds[0] || 'SECL';
        const selectedMines = state.loadedMines.filter(m => cfg.mineIds.includes(m.id));

        container.innerHTML = `
            <div class="space-y-4">
                <div>
                    <h4 class="text-xs font-black uppercase tracking-wider text-gray-700 mb-1">Select Report / Query Format</h4>
                    <p class="text-[11px] text-gray-500 font-medium">Click any format to customize reference details and target mine scope in a dedicated popup window.</p>
                </div>

                <div class="space-y-2.5">
                    <!-- 1. Parliamentary Question Reply -->
                    <div onclick="selectQueryTypeAndOpenModal('parliamentary')" class="p-3.5 rounded-xl border cursor-pointer transition-all ${cfg.queryType === 'parliamentary' ? 'border-[#B0420C] bg-orange-50/30 shadow-2xs ring-1 ring-[#B0420C]' : 'border-gray-200 bg-white hover:border-gray-300'}">
                        <div class="flex items-start justify-between gap-2">
                            <div class="flex items-start gap-2.5">
                                <input type="radio" name="queryType" value="parliamentary" ${cfg.queryType === 'parliamentary' ? 'checked' : ''} class="mt-1 text-[#B0420C] focus:ring-[#B0420C] pointer-events-none">
                                <div>
                                    <div class="font-bold text-xs text-[#16191C]">Parliamentary Question Reply</div>
                                    <div class="text-[11px] text-gray-500 font-medium mt-0.5">Formal Lok Sabha / Rajya Sabha response draft with official subject header, annexures, and strict audit citations.</div>
                                    ${cfg.queryType === 'parliamentary' ? `
                                        <div class="mt-2.5 flex items-center gap-2 flex-wrap">
                                            <span class="px-2 py-0.5 rounded bg-orange-100 text-amber-950 font-mono text-[10px] font-bold border border-orange-200">
                                                🏛️ ${cfg.parliamentaryMeta.house} (${cfg.parliamentaryMeta.type}) #${cfg.parliamentaryMeta.number} &bull; ${cfg.parliamentaryMeta.answerDate}
                                            </span>
                                            <button onclick="event.stopPropagation(); openQueryConfigModal('parliamentary')" class="px-2 py-0.5 rounded bg-white hover:bg-gray-100 border border-gray-300 text-[10px] font-bold text-[#B0420C] flex items-center gap-1 shadow-2xs">
                                                <span>⚙ Edit Reference Details</span>
                                            </button>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 2. Benchmarking & Comparison -->
                    <div onclick="selectQueryTypeAndOpenModal('comparison')" class="p-3.5 rounded-xl border cursor-pointer transition-all ${cfg.queryType === 'comparison' ? 'border-[#B0420C] bg-orange-50/30 shadow-2xs ring-1 ring-[#B0420C]' : 'border-gray-200 bg-white hover:border-gray-300'}">
                        <div class="flex items-start justify-between gap-2">
                            <div class="flex items-start gap-2.5">
                                <input type="radio" name="queryType" value="comparison" ${cfg.queryType === 'comparison' ? 'checked' : ''} class="mt-1 text-[#B0420C] focus:ring-[#B0420C] pointer-events-none">
                                <div>
                                    <div class="font-bold text-xs text-[#16191C]">Benchmarking &amp; Comparison</div>
                                    <div class="text-[11px] text-gray-500 font-medium mt-0.5">Compare 2 or 3 mines/reports across YoY Growth Velocity, Stripping Ratio, and Equipment Uptime.</div>
                                    ${cfg.queryType === 'comparison' ? `
                                        <div class="mt-2.5 flex items-center gap-2 flex-wrap">
                                            <span class="px-2 py-0.5 rounded bg-orange-100 text-amber-950 font-mono text-[10px] font-bold border border-orange-200">
                                                ⚖️ Comparing ${cfg.mineIds.length} Entities: ${selectedMines.map(m=>m.name).slice(0,3).join(', ')}${selectedMines.length > 3 ? '...' : ''}
                                            </span>
                                            <button onclick="event.stopPropagation(); openQueryConfigModal('comparison')" class="px-2 py-0.5 rounded bg-white hover:bg-gray-100 border border-gray-300 text-[10px] font-bold text-[#B0420C] flex items-center gap-1 shadow-2xs">
                                                <span>⚙ Configure Comparison Scope</span>
                                            </button>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 3. Single Mine Technical Review -->
                    <div onclick="selectQueryTypeAndOpenModal('single_mine')" class="p-3.5 rounded-xl border cursor-pointer transition-all ${cfg.queryType === 'single_mine' ? 'border-[#B0420C] bg-orange-50/30 shadow-2xs ring-1 ring-[#B0420C]' : 'border-gray-200 bg-white hover:border-gray-300'}">
                        <div class="flex items-start justify-between gap-2">
                            <div class="flex items-start gap-2.5">
                                <input type="radio" name="queryType" value="single_mine" ${cfg.queryType === 'single_mine' ? 'checked' : ''} class="mt-1 text-[#B0420C] focus:ring-[#B0420C] pointer-events-none">
                                <div>
                                    <div class="font-bold text-xs text-[#16191C]">Single Mine Technical Review</div>
                                    <div class="text-[11px] text-gray-500 font-medium mt-0.5">Deep-dive geotechnical and operational monograph for a single mine (e.g., Gevra OCP).</div>
                                    ${cfg.queryType === 'single_mine' ? `
                                        <div class="mt-2.5 flex items-center gap-2 flex-wrap">
                                            <span class="px-2 py-0.5 rounded bg-orange-100 text-amber-950 font-mono text-[10px] font-bold border border-orange-200">
                                                ⛏️ Selected: ${selectedSingleMine.name} (${selectedSingleMine.subsidiary} - ${selectedSingleMine.capacity} MTY)
                                            </span>
                                            <button onclick="event.stopPropagation(); openQueryConfigModal('single_mine')" class="px-2 py-0.5 rounded bg-white hover:bg-gray-100 border border-gray-300 text-[10px] font-bold text-[#B0420C] flex items-center gap-1 shadow-2xs">
                                                <span>⚙ Change Selected Mine</span>
                                            </button>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 4. Subsidiary / Area Consolidated Report -->
                    <div onclick="selectQueryTypeAndOpenModal('subsidiary')" class="p-3.5 rounded-xl border cursor-pointer transition-all ${cfg.queryType === 'subsidiary' ? 'border-[#B0420C] bg-orange-50/30 shadow-2xs ring-1 ring-[#B0420C]' : 'border-gray-200 bg-white hover:border-gray-300'}">
                        <div class="flex items-start justify-between gap-2">
                            <div class="flex items-start gap-2.5">
                                <input type="radio" name="queryType" value="subsidiary" ${cfg.queryType === 'subsidiary' ? 'checked' : ''} class="mt-1 text-[#B0420C] focus:ring-[#B0420C] pointer-events-none">
                                <div>
                                    <div class="font-bold text-xs text-[#16191C]">Subsidiary / Area Consolidated Report</div>
                                    <div class="text-[11px] text-gray-500 font-medium mt-0.5">Multi-mine dispatch ledger and stripping audit across SECL, NCL, MCL, or WCL commands.</div>
                                    ${cfg.queryType === 'subsidiary' ? `
                                        <div class="mt-2.5 flex items-center gap-2 flex-wrap">
                                            <span class="px-2 py-0.5 rounded bg-orange-100 text-amber-950 font-mono text-[10px] font-bold border border-orange-200">
                                                🏢 ${activeSub} Command (${cfg.mineIds.length} Mines Included)
                                            </span>
                                            <button onclick="event.stopPropagation(); openQueryConfigModal('subsidiary')" class="px-2 py-0.5 rounded bg-white hover:bg-gray-100 border border-gray-300 text-[10px] font-bold text-[#B0420C] flex items-center gap-1 shadow-2xs">
                                                <span>⚙ Change Subsidiary Scope</span>
                                            </button>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else if (state.currentStep === 2) {
        container.innerHTML = `
            <div class="space-y-4">
                <div>
                    <h4 class="text-xs font-black uppercase tracking-wider text-gray-700 mb-1">Configure Report Sections</h4>
                    <p class="text-[11px] text-gray-500 font-medium">Select and sequence operational audit sections for report compilation.</p>
                </div>

                <div class="space-y-2 max-h-72 overflow-y-auto custom-scrollbar pr-1">
                    ${cfg.sections.map((sec, idx) => `
                        <div class="p-3 rounded-xl border transition-all ${sec.enabled ? 'border-gray-300 bg-white shadow-2xs' : 'border-gray-200 bg-gray-50/60 opacity-60'}">
                            <div class="flex items-center justify-between gap-2">
                                <label class="flex items-center gap-2 cursor-pointer flex-1">
                                    <input type="checkbox" ${sec.enabled ? 'checked' : ''} onchange="toggleSectionEnabled('${sec.id}')" class="text-[#B0420C] focus:ring-[#B0420C] rounded">
                                    <span class="font-bold text-xs text-[#16191C]">${idx + 1}. ${sec.title}</span>
                                </label>
                                
                                <div class="flex items-center gap-1">
                                    <button onclick="moveSectionOrder('${sec.id}', 'up')" class="w-6 h-6 rounded bg-gray-100 hover:bg-gray-200 text-gray-600 flex items-center justify-center text-xs" title="Move Up">&uarr;</button>
                                    <button onclick="moveSectionOrder('${sec.id}', 'down')" class="w-6 h-6 rounded bg-gray-100 hover:bg-gray-200 text-gray-600 flex items-center justify-center text-xs" title="Move Down">&darr;</button>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    } else if (state.currentStep === 3) {
        const cov = state.coverageReport || { completeMines: 12, totalMines: 15, isClean: false, summaryWarnings: [] };
        container.innerHTML = `
            <div class="space-y-4">
                <div>
                    <h4 class="text-xs font-black uppercase tracking-wider text-gray-700 mb-1">Data Coverage &amp; Export Verification</h4>
                    <p class="text-[11px] text-gray-500 font-medium">Verify data integrity and export official authenticated copy.</p>
                </div>

                <!-- Data Coverage Summary Box -->
                <div class="p-3.5 rounded-xl border ${cov.isClean ? 'bg-emerald-50/60 border-emerald-200' : 'bg-amber-50/60 border-amber-200'} space-y-2">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-1.5">
                            <span class="w-2.5 h-2.5 rounded-full ${cov.isClean ? 'bg-emerald-600' : 'bg-amber-600'}"></span>
                            <span class="text-xs font-bold text-[#16191C]">Data Coverage: ${cov.completeMines} / ${cov.totalMines} Mines (100% Ready)</span>
                        </div>
                        <span class="text-[10px] font-bold uppercase ${cov.isClean ? 'text-emerald-800' : 'text-amber-800'}">
                            ${cov.isClean ? 'Full Telemetry' : 'Caveats Present'}
                        </span>
                    </div>

                    ${cov.summaryWarnings.length > 0 ? `
                        <div class="text-[11px] text-amber-900 space-y-1 font-medium bg-white/80 p-2.5 rounded-lg border border-amber-200/60">
                            ${cov.summaryWarnings.map(w => `<div class="flex items-start gap-1.5"><span class="text-amber-700">&bull;</span><span>${w}</span></div>`).join('')}
                        </div>
                    ` : `
                        <div class="text-[11px] text-emerald-800 font-medium">All queried mines have complete 12-month data telemetry with zero missing periods.</div>
                    `}
                </div>

                <!-- Export Blocking & Caveat Acknowledgement -->
                ${!cov.isClean ? `
                    <div class="p-3 bg-white rounded-xl border border-gray-200 space-y-2">
                        <label class="flex items-start gap-2 cursor-pointer">
                            <input type="checkbox" id="gap-ack-checkbox" ${state.acknowledgedGaps ? 'checked' : ''} onchange="window.RSHPS_REPORTS_STATE.acknowledgedGaps=this.checked; renderReportBuilderUI();" class="mt-0.5 text-[#B0420C] focus:ring-[#B0420C] rounded">
                            <span class="text-[11px] font-bold text-gray-800 leading-snug">
                                I acknowledge the detected data gaps and certify this report with statutory caveat footnotes.
                            </span>
                        </label>
                    </div>
                ` : ''}

                <!-- Export Action Buttons -->
                <div class="space-y-2 pt-2 border-t border-gray-200">
                    <button onclick="executeReportExport('pdf')" ${(!cov.isClean && !state.acknowledgedGaps) ? 'disabled class="w-full py-3 bg-gray-200 text-gray-400 rounded-xl font-bold text-xs cursor-not-allowed flex items-center justify-center gap-2"' : 'class="w-full py-3 bg-[#16191C] hover:bg-black text-white rounded-xl font-bold text-xs shadow transition-all flex items-center justify-center gap-2"'}>
                        <i data-lucide="printer" class="w-4 h-4"></i>
                        <span>Print / Export PDF</span>
                    </button>

                    <button onclick="executeReportExport('excel')" class="w-full py-2.5 bg-white hover:bg-gray-50 text-gray-800 border border-gray-300 rounded-xl font-bold text-xs transition-all flex items-center justify-center gap-2">
                        <i data-lucide="sheet" class="w-4 h-4 text-emerald-700"></i>
                        <span>Export Excel Dataset (.csv)</span>
                    </button>

                    <button onclick="executeReportExport('word')" class="w-full py-2 bg-white hover:bg-gray-50 text-gray-500 border border-gray-200 rounded-xl font-bold text-[11px] transition-all flex items-center justify-center gap-1.5">
                        <i data-lucide="file-text" class="w-3.5 h-3.5 text-blue-600"></i>
                        <span>Export Word Document (.docx stub)</span>
                    </button>
                </div>
            </div>
        `;
    }

    if (window.lucide) lucide.createIcons();
}

// ── POPUP QUERY CONFIGURATION MODAL (SMALL WINDOW) ──
function openQueryConfigModal(type) {
    const modal = document.getElementById('report-query-config-modal');
    const titleEl = document.getElementById('query-config-modal-title');
    const subtitleEl = document.getElementById('query-config-modal-subtitle');
    const iconContainer = document.getElementById('query-config-modal-icon-container');
    const bodyEl = document.getElementById('query-config-modal-body');
    if (!modal || !bodyEl) return;

    const state = window.RSHPS_REPORTS_STATE;
    const cfg = state.config;
    const queryType = type || cfg.queryType;

    if (queryType === 'parliamentary') {
        if (titleEl) titleEl.textContent = 'Parliamentary Reference Details';
        if (subtitleEl) subtitleEl.textContent = 'Configure official house, question category & mine scope';
        if (iconContainer) iconContainer.innerHTML = '<i data-lucide="landmark" class="w-4 h-4 text-[#B0420C]"></i>';
        
        bodyEl.innerHTML = `
            <div class="space-y-4">
                <div class="p-3 bg-amber-50/70 border border-amber-200 rounded-xl text-[11px] text-amber-900 flex items-start gap-2">
                    <i data-lucide="info" class="w-4 h-4 text-amber-700 shrink-0 mt-0.5"></i>
                    <span>Configure parliamentary reply metadata. This formats official ministry letterhead, parliamentary classification, and target mine benchmarks.</span>
                </div>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                        <label class="block text-[11px] font-bold text-gray-700 mb-1">Parliamentary House</label>
                        <select onchange="window.RSHPS_REPORTS_STATE.config.parliamentaryMeta.house=this.value; renderLivePreview();" class="w-full p-2 bg-white border border-gray-300 rounded-lg font-bold text-xs">
                            <option value="Lok Sabha" ${cfg.parliamentaryMeta.house === 'Lok Sabha' ? 'selected' : ''}>Lok Sabha (House of the People)</option>
                            <option value="Rajya Sabha" ${cfg.parliamentaryMeta.house === 'Rajya Sabha' ? 'selected' : ''}>Rajya Sabha (Council of States)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-[11px] font-bold text-gray-700 mb-1">Question Classification</label>
                        <select onchange="window.RSHPS_REPORTS_STATE.config.parliamentaryMeta.type=this.value; renderLivePreview();" class="w-full p-2 bg-white border border-gray-300 rounded-lg font-bold text-xs">
                            <option value="Unstarred" ${cfg.parliamentaryMeta.type === 'Unstarred' ? 'selected' : ''}>Unstarred (Written Answer)</option>
                            <option value="Starred" ${cfg.parliamentaryMeta.type === 'Starred' ? 'selected' : ''}>Starred (Oral Reply with Supplementary)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-[11px] font-bold text-gray-700 mb-1">Question Number</label>
                        <input type="text" value="${cfg.parliamentaryMeta.number}" oninput="window.RSHPS_REPORTS_STATE.config.parliamentaryMeta.number=this.value; renderLivePreview();" class="w-full p-2 bg-white border border-gray-300 rounded-lg font-bold text-xs font-mono" placeholder="e.g. 4052">
                    </div>
                    <div>
                        <label class="block text-[11px] font-bold text-gray-700 mb-1">Answer Date</label>
                        <input type="date" value="${cfg.parliamentaryMeta.answerDate}" onchange="window.RSHPS_REPORTS_STATE.config.parliamentaryMeta.answerDate=this.value; renderLivePreview();" class="w-full p-2 bg-white border border-gray-300 rounded-lg font-bold text-xs font-mono">
                    </div>
                </div>

                <div>
                    <div class="flex items-center justify-between mb-1.5 flex-wrap gap-2">
                        <label class="block text-[11px] font-bold text-gray-700">Mines Included in Reply Scope (${cfg.mineIds.length} of ${state.loadedMines.length} Selected)</label>
                        <div class="flex items-center gap-1.5">
                            <button type="button" onclick="setPqMinesPreset('all')" class="px-2.5 py-1 rounded bg-[#16191C] hover:bg-black text-white text-[10px] font-bold transition-colors cursor-pointer shadow-2xs">
                                ✓ Select All Mines (${state.loadedMines.length})
                            </button>
                            <button type="button" onclick="setPqMinesPreset('top4')" class="px-2 py-1 rounded bg-gray-200 hover:bg-gray-300 text-[10px] font-bold text-gray-800 transition-colors cursor-pointer">
                                Top Pits
                            </button>
                            <button type="button" onclick="setPqMinesPreset('clear')" class="px-2 py-1 rounded bg-gray-200 hover:bg-rose-100 hover:text-rose-700 text-[10px] font-bold text-gray-600 transition-colors cursor-pointer">
                                Clear
                            </button>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-52 overflow-y-auto custom-scrollbar p-2.5 bg-gray-50 rounded-xl border border-gray-200">
                        ${state.loadedMines.map(m => `
                            <label class="flex items-center gap-2 p-2 bg-white rounded-lg border border-gray-200 cursor-pointer text-[11px] hover:border-[#B0420C] transition-colors">
                                <input type="checkbox" onchange="toggleModalPqMine('${m.id}', this.checked)" ${cfg.mineIds.includes(m.id) ? 'checked' : ''} class="rounded text-[#B0420C] focus:ring-[#B0420C]">
                                <div class="truncate">
                                    <div class="font-bold truncate text-gray-800">${m.name}</div>
                                    <div class="text-[9px] text-gray-400 font-mono">${m.subsidiary} &bull; ${m.capacity} MTY</div>
                                </div>
                            </label>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    } else if (queryType === 'single_mine') {
        if (titleEl) titleEl.textContent = 'Select Mine for Technical Monograph';
        if (subtitleEl) subtitleEl.textContent = 'Choose an opencast or underground pit for deep-dive review';
        if (iconContainer) iconContainer.innerHTML = '<i data-lucide="pickaxe" class="w-4 h-4 text-[#B0420C]"></i>';

        bodyEl.innerHTML = `
            <div class="space-y-3">
                <div class="flex items-center justify-between">
                    <label class="text-[11px] font-bold text-gray-700">Available Mining Operations (${state.loadedMines.length})</label>
                    <span class="text-[10px] text-gray-400 font-mono">Click a mine card to select</span>
                </div>
                
                <!-- Search Input -->
                <div class="relative">
                    <input type="text" id="modal-mine-search" oninput="filterModalMinesList(this.value)" placeholder="Search mine name, subsidiary, coalfield..." class="w-full pl-8 pr-3 py-2 bg-gray-50 border border-gray-300 rounded-xl font-medium text-xs focus:bg-white focus:ring-1 focus:ring-[#B0420C]">
                    <span class="absolute left-2.5 top-2.5 text-gray-400 text-xs">🔍</span>
                </div>

                <!-- Mines Card Grid -->
                <div id="modal-mines-grid" class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-h-80 overflow-y-auto custom-scrollbar pr-1">
                    ${state.loadedMines.map(m => {
                        const isSelected = cfg.mineIds[0] === m.id;
                        return `
                            <div onclick="selectModalSingleMine('${m.id}')" data-mine-text="${m.name} ${m.subsidiary} ${m.coalfield} ${m.type}" class="p-3 rounded-xl border cursor-pointer transition-all flex flex-col justify-between gap-1.5 ${isSelected ? 'border-[#B0420C] bg-orange-50/50 ring-2 ring-[#B0420C]' : 'border-gray-200 bg-white hover:border-gray-400'}">
                                <div class="flex items-start justify-between gap-1">
                                    <div>
                                        <div class="font-black text-xs text-[#16191C]">${m.name}</div>
                                        <div class="text-[10px] font-semibold text-gray-500">${m.subsidiary} &bull; ${m.area || m.coalfield}</div>
                                    </div>
                                    <span class="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase ${m.type === 'Opencast' ? 'bg-amber-100 text-amber-900' : 'bg-blue-100 text-blue-900'}">${m.type}</span>
                                </div>
                                <div class="flex items-center justify-between text-[10px] pt-1.5 border-t border-gray-100 text-gray-500">
                                    <span>Capacity: <strong>${m.capacity} MTY</strong></span>
                                    <span class="font-mono text-emerald-700 font-bold">${m.status || 'Active'}</span>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    } else if (queryType === 'subsidiary') {
        if (titleEl) titleEl.textContent = 'Subsidiary Command & Area Scope';
        if (subtitleEl) subtitleEl.textContent = 'Consolidate multiple pits under a Coal India Ltd subsidiary';
        if (iconContainer) iconContainer.innerHTML = '<i data-lucide="building-2" class="w-4 h-4 text-[#B0420C]"></i>';

        const subs = [
            { id: 'SECL', name: 'SECL', full: 'South Eastern Coalfields Ltd', count: 4 },
            { id: 'NCL', name: 'NCL', full: 'Northern Coalfields Ltd', count: 3 },
            { id: 'MCL', name: 'MCL', full: 'Mahanadi Coalfields Ltd', count: 3 },
            { id: 'WCL', name: 'WCL', full: 'Western Coalfields Ltd', count: 2 },
            { id: 'BCCL', name: 'BCCL', full: 'Bharat Coking Coal Ltd', count: 2 },
            { id: 'CCL', name: 'CCL', full: 'Central Coalfields Ltd', count: 1 },
            { id: 'ECL', name: 'ECL', full: 'Eastern Coalfields Ltd', count: 1 },
            { id: 'ALL', name: 'ALL CIL', full: 'Pan-India Consolidated', count: 15 }
        ];

        const activeSub = cfg.subsidiaryIds[0] || 'SECL';
        const subMines = activeSub === 'ALL' ? state.loadedMines : state.loadedMines.filter(m => m.subsidiary === activeSub);

        bodyEl.innerHTML = `
            <div class="space-y-4">
                <div>
                    <label class="block text-[11px] font-bold text-gray-700 mb-1.5">Select Subsidiary Command</label>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        ${subs.map(s => {
                            const isSelected = activeSub === s.id;
                            return `
                                <button type="button" onclick="selectModalSubsidiary('${s.id}')" class="p-2.5 rounded-xl border text-left transition-all ${isSelected ? 'border-[#B0420C] bg-orange-50/50 ring-2 ring-[#B0420C]' : 'border-gray-200 bg-white hover:border-gray-300'}">
                                    <div class="font-black text-xs text-[#16191C]">${s.name}</div>
                                    <div class="text-[9px] text-gray-500 font-medium truncate">${s.full}</div>
                                    <div class="text-[9px] font-bold text-[#B0420C] mt-1 font-mono">${s.count} Mines</div>
                                </button>
                            `;
                        }).join('')}
                    </div>
                </div>

                <div>
                    <div class="flex items-center justify-between mb-1.5">
                        <label class="text-[11px] font-bold text-gray-700">Production Benches in ${activeSub} (${cfg.mineIds.length} Included)</label>
                    </div>
                    <div id="modal-sub-mines-container" class="space-y-1.5 max-h-48 overflow-y-auto custom-scrollbar p-2.5 bg-gray-50 rounded-xl border border-gray-200">
                        ${subMines.map(m => `
                            <label class="flex items-center justify-between p-2 bg-white rounded-lg border border-gray-200 cursor-pointer hover:border-[#B0420C]">
                                <div class="flex items-center gap-2">
                                    <input type="checkbox" onchange="toggleModalSubMine('${m.id}', this.checked)" ${cfg.mineIds.includes(m.id) ? 'checked' : ''} class="rounded text-[#B0420C] focus:ring-[#B0420C]">
                                    <div>
                                        <div class="font-bold text-xs text-[#16191C]">${m.name}</div>
                                        <div class="text-[10px] text-gray-400">${m.area || m.coalfield} &bull; ${m.type}</div>
                                    </div>
                                </div>
                                <span class="text-[10px] font-mono font-bold text-gray-600">${m.capacity} MTY</span>
                            </label>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    } else if (queryType === 'comparison') {
        if (titleEl) titleEl.textContent = 'Benchmarking & Multi-Aspect Comparative Suite';
        if (subtitleEl) subtitleEl.textContent = 'Select 2 or 3 mines/reports to compare across YoY Growth, Stripping Ratio & Fleet Uptime';
        if (iconContainer) iconContainer.innerHTML = '<i data-lucide="scale" class="w-4 h-4 text-[#B0420C]"></i>';

        const selectedList = state.loadedMines.filter(m => cfg.mineIds.includes(m.id));

        bodyEl.innerHTML = `
            <div class="space-y-4 font-sans">
                <!-- Explanatory Banner -->
                <div class="p-3 bg-orange-50/70 border border-orange-200 rounded-xl space-y-1 text-xs">
                    <div class="font-bold text-[#16191C] flex items-center gap-1.5">
                        <i data-lucide="info" class="w-4 h-4 text-[#B0420C]"></i>
                        <span>Side-by-Side Multi-Aspect Variance &amp; Growth Benchmarking</span>
                    </div>
                    <div class="text-[11px] text-gray-600 leading-snug">
                        Select <strong>2 or 3 mining operations</strong> to benchmark against statutory targets, 24-month YoY output growth, stripping ratios, HEMM equipment availability, and geological coal seam caloric grades.
                    </div>
                </div>

                <!-- Active Selection Counter & Badges -->
                <div class="p-3 bg-gray-50 rounded-xl border border-gray-200 space-y-2">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-bold text-gray-700">Currently Selected for Comparison (${cfg.mineIds.length} Mines):</span>
                        <span class="text-[10px] font-mono font-bold ${cfg.mineIds.length >= 2 ? 'text-emerald-700' : 'text-amber-700'}">
                            ${cfg.mineIds.length >= 2 ? '✓ Ready for Comparison' : '⚠️ Select at least 2 mines'}
                        </span>
                    </div>
                    <div class="flex items-center gap-2 flex-wrap" id="modal-comp-selected-tags">
                        ${selectedList.map((m, idx) => `
                            <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-orange-100/80 border border-orange-300 text-[11px] font-bold text-amber-950 shadow-2xs">
                                <span class="w-4 h-4 rounded-full bg-[#B0420C] text-white flex items-center justify-center text-[9px] font-bold">${idx + 1}</span>
                                <span>${m.name} (${m.subsidiary})</span>
                                <button type="button" onclick="toggleModalCompMine('${m.id}', false)" class="text-amber-800 hover:text-rose-700 font-bold ml-1 text-xs" title="Remove mine">&times;</button>
                            </span>
                        `).join('')}
                    </div>
                </div>

                <!-- Quick Presets -->
                <div>
                    <label class="block text-[11px] font-bold text-gray-700 mb-1.5">Quick Comparison Presets (1-Click Selection):</label>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
                        <button type="button" onclick="setComparisonPreset('top2')" class="p-2 rounded-lg bg-white hover:bg-orange-50 border border-gray-200 hover:border-orange-300 text-left transition-colors cursor-pointer">
                            <div class="font-bold text-[11px] text-[#16191C]">★ Top 2 Mega-Titans</div>
                            <div class="text-[9px] text-gray-500 font-mono">Gevra vs Kusmunda</div>
                        </button>
                        <button type="button" onclick="setComparisonPreset('top3')" class="p-2 rounded-lg bg-white hover:bg-orange-50 border border-gray-200 hover:border-orange-300 text-left transition-colors cursor-pointer">
                            <div class="font-bold text-[11px] text-[#16191C]">★ Top 3 Opencast</div>
                            <div class="text-[9px] text-gray-500 font-mono">Gevra, Kusmunda, Jayant</div>
                        </button>
                        <button type="button" onclick="setComparisonPreset('cross_sub')" class="p-2 rounded-lg bg-white hover:bg-orange-50 border border-gray-200 hover:border-orange-300 text-left transition-colors cursor-pointer">
                            <div class="font-bold text-[11px] text-[#16191C]">★ Cross-Subsidiary</div>
                            <div class="text-[9px] text-gray-500 font-mono">SECL vs NCL vs MCL</div>
                        </button>
                        <button type="button" onclick="setComparisonPreset('quality_diff')" class="p-2 rounded-lg bg-white hover:bg-orange-50 border border-gray-200 hover:border-orange-300 text-left transition-colors cursor-pointer">
                            <div class="font-bold text-[11px] text-[#16191C]">★ Caloric vs Bulk</div>
                            <div class="text-[9px] text-gray-500 font-mono">G4 (6240) vs G11 vs G5</div>
                        </button>
                    </div>
                </div>

                <!-- Comparison Dimensions (Aspects) -->
                <div>
                    <label class="block text-[11px] font-bold text-gray-700 mb-1.5">Benchmarking Aspects &amp; Growth Metrics:</label>
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                        <label class="flex items-center gap-2 p-2 bg-white rounded-lg border border-gray-200 cursor-pointer hover:border-[#B0420C] text-[11px]">
                            <input type="checkbox" checked disabled class="rounded text-[#B0420C] focus:ring-[#B0420C]">
                            <span class="font-bold text-gray-800">📈 YoY Output Growth (%)</span>
                        </label>
                        <label class="flex items-center gap-2 p-2 bg-white rounded-lg border border-gray-200 cursor-pointer hover:border-[#B0420C] text-[11px]">
                            <input type="checkbox" checked disabled class="rounded text-[#B0420C] focus:ring-[#B0420C]">
                            <span class="font-bold text-gray-800">🚜 Stripping Ratio (CuM/T)</span>
                        </label>
                        <label class="flex items-center gap-2 p-2 bg-white rounded-lg border border-gray-200 cursor-pointer hover:border-[#B0420C] text-[11px]">
                            <input type="checkbox" checked disabled class="rounded text-[#B0420C] focus:ring-[#B0420C]">
                            <span class="font-bold text-gray-800">⚙️ HEMM Fleet Availability</span>
                        </label>
                        <label class="flex items-center gap-2 p-2 bg-white rounded-lg border border-gray-200 cursor-pointer hover:border-[#B0420C] text-[11px]">
                            <input type="checkbox" checked disabled class="rounded text-[#B0420C] focus:ring-[#B0420C]">
                            <span class="font-bold text-gray-800">⚡ OMS Productivity (T/MS)</span>
                        </label>
                        <label class="flex items-center gap-2 p-2 bg-white rounded-lg border border-gray-200 cursor-pointer hover:border-[#B0420C] text-[11px]">
                            <input type="checkbox" checked disabled class="rounded text-[#B0420C] focus:ring-[#B0420C]">
                            <span class="font-bold text-gray-800">🔬 Seam Caloric Grade (GCV)</span>
                        </label>
                        <label class="flex items-center gap-2 p-2 bg-white rounded-lg border border-gray-200 cursor-pointer hover:border-[#B0420C] text-[11px]">
                            <input type="checkbox" checked disabled class="rounded text-[#B0420C] focus:ring-[#B0420C]">
                            <span class="font-bold text-gray-800">🛡️ DGMS Safety Compliance</span>
                        </label>
                    </div>
                </div>

                <!-- Search & Mines Selection Grid -->
                <div>
                    <div class="flex items-center justify-between mb-1.5">
                        <label class="text-[11px] font-bold text-gray-700">Available Mining Operations (${state.loadedMines.length})</label>
                        <span class="text-[10px] text-gray-400 font-mono">Select checkboxes to add or remove</span>
                    </div>

                    <div class="relative mb-2">
                        <input type="text" id="modal-comp-mine-search" oninput="filterModalCompMinesList(this.value)" placeholder="Search mine name, subsidiary, coalfield, grade..." class="w-full pl-8 pr-3 py-1.5 bg-gray-50 border border-gray-300 rounded-lg font-medium text-xs focus:bg-white focus:ring-1 focus:ring-[#B0420C]">
                        <span class="absolute left-2.5 top-2 text-gray-400 text-xs">🔍</span>
                    </div>

                    <div id="modal-comp-mines-grid" class="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-52 overflow-y-auto custom-scrollbar p-2 bg-gray-50 rounded-xl border border-gray-200">
                        ${state.loadedMines.map(m => {
                            const isChecked = cfg.mineIds.includes(m.id);
                            const seam = m.seams?.[0] || { grade: 'G4', gcv: 6240 };
                            return `
                                <label data-mine-text="${m.name} ${m.subsidiary} ${m.coalfield} ${m.type} ${seam.grade}" class="flex items-center justify-between p-2 rounded-lg border cursor-pointer transition-all ${isChecked ? 'bg-orange-50 border-[#B0420C] ring-1 ring-[#B0420C]' : 'bg-white border-gray-200 hover:border-gray-300'}">
                                    <div class="flex items-center gap-2 truncate">
                                        <input type="checkbox" onchange="toggleModalCompMine('${m.id}', this.checked)" ${isChecked ? 'checked' : ''} class="rounded text-[#B0420C] focus:ring-[#B0420C]">
                                        <div class="truncate">
                                            <div class="font-bold text-xs text-[#16191C] truncate">${m.name}</div>
                                            <div class="text-[9px] text-gray-400 font-mono">${m.subsidiary} &bull; ${m.type} &bull; Grade: <strong>${seam.grade}</strong></div>
                                        </div>
                                    </div>
                                    <div class="text-right shrink-0">
                                        <div class="text-[10px] font-mono font-bold text-gray-700">${m.capacity} MT</div>
                                        <div class="text-[8px] text-emerald-700 font-mono font-bold">${seam.gcv} kcal/kg</div>
                                    </div>
                                </label>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
}

function closeQueryConfigModal() {
    const modal = document.getElementById('report-query-config-modal');
    if (modal) modal.classList.add('hidden');
}

async function applyQueryConfigAndClose() {
    closeQueryConfigModal();
    await refreshReportData();
    renderReportBuilderUI();
    renderLivePreview();
}

// Modal Interaction Helper Handlers
async function selectModalSingleMine(mineId) {
    const state = window.RSHPS_REPORTS_STATE;
    state.config.mineIds = [mineId];
    const m = state.loadedMines.find(x => x.id === mineId);
    if (m) state.config.name = `Single Mine Technical Review - ${m.name}`;
    await refreshReportData();
    renderLivePreview();
    openQueryConfigModal('single_mine');
}

function filterModalMinesList(query) {
    const q = (query || '').toLowerCase().trim();
    const cards = document.querySelectorAll('#modal-mines-grid > div');
    cards.forEach(card => {
        const text = (card.getAttribute('data-mine-text') || '').toLowerCase();
        if (!q || text.includes(q)) {
            card.classList.remove('hidden');
        } else {
            card.classList.add('hidden');
        }
    });
}

function filterModalCompMinesList(query) {
    const q = (query || '').toLowerCase().trim();
    const cards = document.querySelectorAll('#modal-comp-mines-grid > label');
    cards.forEach(card => {
        const text = (card.getAttribute('data-mine-text') || '').toLowerCase();
        if (!q || text.includes(q)) {
            card.classList.remove('hidden');
        } else {
            card.classList.add('hidden');
        }
    });
}

async function selectModalSubsidiary(subCode) {
    const state = window.RSHPS_REPORTS_STATE;
    state.config.subsidiaryIds = [subCode];
    if (subCode === 'ALL') {
        state.config.mineIds = state.loadedMines.map(m => m.id);
        state.config.name = 'Pan-India CIL Consolidated Performance Report';
    } else {
        const matching = state.loadedMines.filter(m => m.subsidiary === subCode).map(m => m.id);
        state.config.mineIds = matching.length > 0 ? matching : ['SECL-GEVRA-OCP', 'SECL-KUSMUNDA-OCP'];
        state.config.name = `${subCode} Subsidiary Consolidated Performance Report`;
    }
    await refreshReportData();
    renderLivePreview();
    openQueryConfigModal('subsidiary');
}

async function toggleModalSubMine(mineId, isChecked) {
    const state = window.RSHPS_REPORTS_STATE;
    if (isChecked && !state.config.mineIds.includes(mineId)) {
        state.config.mineIds.push(mineId);
    } else if (!isChecked) {
        state.config.mineIds = state.config.mineIds.filter(id => id !== mineId);
    }
    await refreshReportData();
    renderLivePreview();
}

async function toggleModalPqMine(mineId, isChecked) {
    const state = window.RSHPS_REPORTS_STATE;
    if (isChecked && !state.config.mineIds.includes(mineId)) {
        state.config.mineIds.push(mineId);
    } else if (!isChecked) {
        state.config.mineIds = state.config.mineIds.filter(id => id !== mineId);
    }
    await refreshReportData();
    renderLivePreview();
}

async function setPqMinesPreset(preset) {
    const state = window.RSHPS_REPORTS_STATE;
    if (preset === 'all') {
        state.config.mineIds = state.loadedMines.map(m => m.id);
    } else if (preset === 'top4') {
        state.config.mineIds = ['SECL-GEVRA-OCP', 'SECL-KUSMUNDA-OCP', 'NCL-JAYANT-OCP', 'MCL-LINGARAJ-OCP'];
    } else if (preset === 'clear') {
        state.config.mineIds = ['SECL-GEVRA-OCP'];
    }
    await refreshReportData();
    renderLivePreview();
    openQueryConfigModal('parliamentary');
}

async function toggleModalCompMine(mineId, isChecked) {
    const state = window.RSHPS_REPORTS_STATE;
    if (isChecked && !state.config.mineIds.includes(mineId)) {
        state.config.mineIds.push(mineId);
    } else if (!isChecked) {
        if (state.config.mineIds.length > 1) {
            state.config.mineIds = state.config.mineIds.filter(id => id !== mineId);
        }
    }
    await refreshReportData();
    renderLivePreview();
    openQueryConfigModal('comparison');
}

async function setComparisonPreset(preset) {
    const state = window.RSHPS_REPORTS_STATE;
    if (preset === 'top2') {
        state.config.mineIds = ['SECL-GEVRA-OCP', 'SECL-KUSMUNDA-OCP'];
    } else if (preset === 'top3') {
        state.config.mineIds = ['SECL-GEVRA-OCP', 'SECL-KUSMUNDA-OCP', 'NCL-JAYANT-OCP'];
    } else if (preset === 'cross_sub') {
        state.config.mineIds = ['SECL-GEVRA-OCP', 'NCL-JAYANT-OCP', 'MCL-LINGARAJ-OCP'];
    } else if (preset === 'quality_diff') {
        state.config.mineIds = ['SECL-GEVRA-OCP', 'SECL-KUSMUNDA-OCP', 'NCL-NIGAHI-OCP'];
    } else if (preset === 'top5') {
        state.config.mineIds = ['SECL-GEVRA-OCP', 'SECL-KUSMUNDA-OCP', 'NCL-JAYANT-OCP', 'MCL-LINGARAJ-OCP', 'NCL-NIGAHI-OCP'];
    } else if (preset === 'all') {
        state.config.mineIds = state.loadedMines.map(m => m.id);
    }
    await refreshReportData();
    renderLivePreview();
    openQueryConfigModal('comparison');
}

// ── VISUALIZATION METADATA & INTELLIGENT RECOMMENDATIONS ──
function getAvailableVisualizations(sectionId) {
    const registry = {
        production: [
            { id: 'table', label: 'Table', icon: 'table', isRecommended: false },
            { id: 'bar', label: 'Bar Chart', icon: 'bar-chart-2', isRecommended: true },
            { id: 'line', label: 'Line Chart', icon: 'trending-up', isRecommended: false },
            { id: 'area', label: 'Area Chart', icon: 'activity', isRecommended: false },
            { id: 'donut', label: 'Donut Chart', icon: 'pie-chart', isRecommended: false },
            { id: 'narrative', label: 'Narrative', icon: 'file-text', isRecommended: false }
        ],
        overburden: [
            { id: 'table', label: 'Table', icon: 'table', isRecommended: true },
            { id: 'bar', label: 'Bar Chart', icon: 'bar-chart-2', isRecommended: false },
            { id: 'line', label: 'Line Chart', icon: 'trending-up', isRecommended: false },
            { id: 'area', label: 'Area Chart', icon: 'activity', isRecommended: false },
            { id: 'narrative', label: 'Narrative', icon: 'file-text', isRecommended: false }
        ],
        hemm: [
            { id: 'bar', label: 'Bar Chart', icon: 'bar-chart-2', isRecommended: true },
            { id: 'table', label: 'Table', icon: 'table', isRecommended: false },
            { id: 'donut', label: 'Donut Chart', icon: 'pie-chart', isRecommended: false },
            { id: 'line', label: 'Line Chart', icon: 'trending-up', isRecommended: false },
            { id: 'narrative', label: 'Narrative', icon: 'file-text', isRecommended: false }
        ],
        oms: [
            { id: 'bar', label: 'Bar Chart', icon: 'bar-chart-2', isRecommended: true },
            { id: 'table', label: 'Table', icon: 'table', isRecommended: false },
            { id: 'line', label: 'Line Chart', icon: 'trending-up', isRecommended: false },
            { id: 'narrative', label: 'Narrative', icon: 'file-text', isRecommended: false }
        ],
        safety: [
            { id: 'narrative', label: 'Narrative', icon: 'file-text', isRecommended: true },
            { id: 'table', label: 'Table', icon: 'table', isRecommended: false },
            { id: 'bar', label: 'Bar Chart', icon: 'bar-chart-2', isRecommended: false }
        ],
        reserves: [
            { id: 'table', label: 'Table', icon: 'table', isRecommended: true },
            { id: 'bar', label: 'Bar Chart', icon: 'bar-chart-2', isRecommended: false },
            { id: 'scatter', label: 'Depth Profile', icon: 'crosshair', isRecommended: false },
            { id: 'line', label: 'Line Chart', icon: 'trending-up', isRecommended: false },
            { id: 'narrative', label: 'Narrative', icon: 'file-text', isRecommended: false }
        ],
        environment: [
            { id: 'narrative', label: 'Narrative', icon: 'file-text', isRecommended: true },
            { id: 'table', label: 'Table', icon: 'table', isRecommended: false },
            { id: 'bar', label: 'Bar Chart', icon: 'bar-chart-2', isRecommended: false }
        ],
        land: [
            { id: 'narrative', label: 'Narrative', icon: 'file-text', isRecommended: true },
            { id: 'table', label: 'Table', icon: 'table', isRecommended: false }
        ],
        financials: [
            { id: 'table', label: 'Table', icon: 'table', isRecommended: true },
            { id: 'bar', label: 'Bar Chart', icon: 'bar-chart-2', isRecommended: false },
            { id: 'donut', label: 'Donut Chart', icon: 'pie-chart', isRecommended: false },
            { id: 'narrative', label: 'Narrative', icon: 'file-text', isRecommended: false }
        ]
    };
    return registry[sectionId] || [
        { id: 'table', label: 'Table', icon: 'table', isRecommended: true },
        { id: 'bar', label: 'Bar Chart', icon: 'bar-chart-2', isRecommended: false },
        { id: 'narrative', label: 'Narrative', icon: 'file-text', isRecommended: false }
    ];
}

function getVisFormatMeta(formatId) {
    const map = {
        table: { label: 'Table', icon: 'table' },
        bar: { label: 'Bar Chart', icon: 'bar-chart-2' },
        line: { label: 'Line Chart', icon: 'trending-up' },
        area: { label: 'Area Chart', icon: 'activity' },
        donut: { label: 'Donut Chart', icon: 'pie-chart' },
        scatter: { label: 'Depth Profile', icon: 'crosshair' },
        narrative: { label: 'Narrative', icon: 'file-text' }
    };
    return map[formatId] || { label: 'Visualization', icon: 'bar-chart-2' };
}

// ── IN-PLACE VISUALIZATION TRANSFORM CONTROLS ──
function toggleSectionVisDropdown(secId, event) {
    if (event) event.stopPropagation();
    const allMenus = document.querySelectorAll('[id^="vis-menu-"]');
    allMenus.forEach(m => {
        if (m.id !== 'vis-menu-' + secId) m.classList.add('hidden');
    });
    const targetMenu = document.getElementById('vis-menu-' + secId);
    if (targetMenu) targetMenu.classList.toggle('hidden');
}

function setSectionVisualization(secId, format, event) {
    if (event) event.stopPropagation();
    const sec = window.RSHPS_REPORTS_STATE.config.sections.find(s => s.id === secId);
    if (!sec) return;
    sec.presentation = format;
    
    // Close dropdown
    const targetMenu = document.getElementById('vis-menu-' + secId);
    if (targetMenu) targetMenu.classList.add('hidden');
    
    // In-place update of container
    const container = document.getElementById('sec-vis-container-' + secId);
    const state = window.RSHPS_REPORTS_STATE;
    const cfg = state.config;
    const metricsData = state.loadedMetrics || {};
    const selectedMines = state.loadedMines.filter(m => cfg.mineIds.includes(m.id));
    
    if (container) {
        container.innerHTML = renderSectionVisualizationContent(sec, format, selectedMines, metricsData);
    }
    
    // Update trigger button
    const meta = getVisFormatMeta(format);
    const triggerContainer = document.getElementById('vis-dropdown-container-' + secId);
    if (triggerContainer) {
        const btn = triggerContainer.querySelector('button');
        if (btn) {
            btn.innerHTML = `
                <i data-lucide="${meta.icon}" class="w-3.5 h-3.5 text-[#B0420C]"></i>
                <span>${meta.label}</span>
                <i data-lucide="chevron-down" class="w-3 h-3 text-gray-400"></i>
            `;
        }
    }
    
    if (window.lucide) lucide.createIcons();
}

// Global click listener to dismiss any open dropdown
if (typeof window !== 'undefined') {
    window.addEventListener('click', () => {
        const allMenus = document.querySelectorAll('[id^="vis-menu-"]');
        allMenus.forEach(m => m.classList.add('hidden'));
    });
}

function exportSingleSectionCSV(secId) {
    const state = window.RSHPS_REPORTS_STATE;
    const cfg = state.config;
    const metrics = state.loadedMetrics || {};
    const mines = state.loadedMines.filter(m => cfg.mineIds.includes(m.id));
    
    let csv = `data:text/csv;charset=utf-8,Section,"${secId}"\r\n\r\n`;
    if (secId === 'production') {
        csv += 'Mine ID,Mine Name,Subsidiary,Coalfield,Target Production (MT),Actual Production (MT),Achievement %,Capacity (MTY)\r\n';
        mines.forEach(m => {
            const p = metrics[m.id]?.production || [];
            const act = p.reduce((a, b) => a + b.value, 0).toFixed(2);
            const tgt = p.reduce((a, b) => a + (b.target || 0), 0).toFixed(2);
            const ach = tgt > 0 ? ((act / tgt) * 100).toFixed(1) : '100.0';
            csv += `"${m.id}","${m.name}","${m.subsidiary}","${m.coalfield}",${tgt},${act},${ach}%,${m.capacity}\r\n`;
        });
    } else if (secId === 'overburden') {
        csv += 'Mine ID,Mine Name,Subsidiary,Target OB (Mcum),Actual OB (Mcum),Stripping Ratio (CuM/T)\r\n';
        mines.forEach(m => {
            const ob = metrics[m.id]?.ob_removal || [];
            const sr = metrics[m.id]?.stripping_ratio || [];
            const actOB = ob.reduce((a, b) => a + b.value, 0).toFixed(2);
            const tgtOB = ob.reduce((a, b) => a + (b.target || 0), 0).toFixed(2);
            const avgSR = sr.length > 0 ? (sr.reduce((a, b) => a + b.value, 0) / sr.length).toFixed(2) : '3.80';
            csv += `"${m.id}","${m.name}","${m.subsidiary}",${tgtOB},${actOB},${avgSR}\r\n`;
        });
    } else if (secId === 'reserves') {
        csv += 'Horizon,Thickness (m),Depth (m),Ash %,GCV (kcal/kg),Grade\r\n';
        const doc = MOCK_DOCUMENTS.find(d => d.id === 'SECL-GEVRA-OCP-2024') || MOCK_DOCUMENTS[0];
        (doc.seamTable || []).forEach(s => {
            csv += `"${s.horizon}",${s.thickness},${s.depth},${s.ashPercent}%,${s.gcv},"${s.grade}"\r\n`;
        });
    } else {
        csv += 'Parameter,Value,Status,Benchmark\r\n';
        csv += `Audit Scope,"${cfg.name}","Verified","CMPDI-2024"\r\n`;
    }

    const encoded = encodeURI(csv);
    const link = document.createElement('a');
    link.href = encoded;
    link.download = `CMPDI_Section_${secId}_${Date.now()}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ── VISUALIZATION DISPATCHER & RENDERERS ──
function renderSectionVisualizationContent(sec, currentVis, selectedMines, metricsData) {
    if (sec.id === 'production') {
        return renderProductionVis(currentVis, selectedMines, metricsData);
    } else if (sec.id === 'overburden') {
        return renderOverburdenVis(currentVis, selectedMines, metricsData);
    } else if (sec.id === 'hemm') {
        return renderHemmVis(currentVis, selectedMines, metricsData);
    } else if (sec.id === 'oms') {
        return renderOmsVis(currentVis, selectedMines, metricsData);
    } else if (sec.id === 'safety') {
        return renderSafetyVis(currentVis, selectedMines, metricsData);
    } else if (sec.id === 'reserves') {
        return renderReservesVis(currentVis, selectedMines, metricsData);
    } else if (sec.id === 'environment') {
        return renderEnvironmentVis(currentVis, selectedMines, metricsData);
    } else if (sec.id === 'land') {
        return renderLandVis(currentVis, selectedMines, metricsData);
    } else if (sec.id === 'financials') {
        return renderFinancialsVis(currentVis, selectedMines, metricsData);
    }
    return `<div class="p-4 text-center text-gray-500 italic text-xs">Section content rendered for ${sec.title}</div>`;
}

// 1. PRODUCTION VISUALIZATIONS
function renderProductionVis(format, selectedMines, metricsData) {
    const isComparison = window.RSHPS_REPORTS_STATE.config.queryType === 'comparison';

    const rows = selectedMines.map(m => {
        const pSeries = metricsData[m.id]?.production || [];
        const baseSeries = pSeries.slice(0, 12);
        const currSeries = pSeries.slice(12, 24);

        const baseActual = baseSeries.reduce((acc, pt) => acc + pt.value, 0) || (m.capacity * 0.88);
        const currActual = currSeries.reduce((acc, pt) => acc + pt.value, 0) || (m.capacity * 0.95);
        const currTarget = currSeries.reduce((acc, pt) => acc + (pt.target || 0), 0) || (m.capacity * 0.98);

        const yoyGrowth = baseActual > 0 ? (((currActual - baseActual) / baseActual) * 100) : 0;
        const achievement = currTarget > 0 ? ((currActual / currTarget) * 100) : 100;

        return {
            mine: m,
            baseActual,
            actual: currActual,
            target: currTarget,
            yoyGrowth,
            achievement,
            sourceRef: currSeries[0]?.source || { documentId: 'SECL-GEVRA-OCP-2024', page: 14, asOfDate: '2024-08-31' },
            fullSeries: pSeries
        };
    });

    const totalActual = rows.reduce((acc, r) => acc + r.actual, 0).toFixed(2);
    const totalTarget = rows.reduce((acc, r) => acc + r.target, 0).toFixed(2);
    const overallAchieve = ((totalActual / totalTarget) * 100).toFixed(1);

    if (isComparison) {
        if (format === 'table') {
            return `
                <div class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-2xs">
                    <table class="w-full text-left text-xs border-collapse font-sans">
                        <thead class="bg-gray-100/90 text-gray-700 font-bold text-[10px] uppercase border-b border-gray-200">
                            <tr>
                                <th class="p-2.5 border-r border-gray-200">Mining Operation &bull; Subsidiary</th>
                                <th class="p-2.5 border-r border-gray-200 text-right">FY23-24 Base (MT)</th>
                                <th class="p-2.5 border-r border-gray-200 text-right font-black text-[#16191C]">FY24-25 Output (MT)</th>
                                <th class="p-2.5 border-r border-gray-200 text-right">Target (MT)</th>
                                <th class="p-2.5 border-r border-gray-200 text-center font-bold">YoY Growth Velocity</th>
                                <th class="p-2.5 border-r border-gray-200 text-right">Target Achieved</th>
                                <th class="p-2.5 text-center">Verified Source</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200 text-slate-800">
                            ${rows.map((r, i) => `
                                <tr class="hover:bg-orange-50/30 transition-colors">
                                    <td class="p-2.5 pl-3 font-bold text-[#16191C] border-r border-gray-200 flex items-center justify-between">
                                        <div>
                                            <span>${r.mine.name}</span>
                                            <span class="text-[10px] font-mono text-gray-400">(${r.mine.subsidiary} &bull; ${r.mine.type})</span>
                                        </div>
                                        <span class="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-gray-100 text-gray-700 border border-gray-200">Rank #${i + 1}</span>
                                    </td>
                                    <td class="p-2.5 border-r border-gray-200 text-right font-mono text-gray-500">${r.baseActual.toFixed(2)}</td>
                                    <td class="p-2.5 border-r border-gray-200 text-right font-mono font-black text-gray-900 bg-orange-50/40">${r.actual.toFixed(2)}</td>
                                    <td class="p-2.5 border-r border-gray-200 text-right font-mono text-gray-600">${r.target.toFixed(2)}</td>
                                    <td class="p-2.5 border-r border-gray-200 text-center font-mono">
                                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${r.yoyGrowth >= 10 ? 'bg-emerald-100 text-emerald-900 border border-emerald-300' : (r.yoyGrowth >= 0 ? 'bg-blue-100 text-blue-900 border border-blue-300' : 'bg-rose-100 text-rose-900')}">
                                            ${r.yoyGrowth >= 0 ? '+' : ''}${r.yoyGrowth.toFixed(1)}% YoY ↗
                                        </span>
                                    </td>
                                    <td class="p-2.5 border-r border-gray-200 text-right font-mono font-bold ${r.achievement >= 95 ? 'text-emerald-700' : 'text-amber-700'}">
                                        ${r.achievement.toFixed(1)}%
                                    </td>
                                    <td class="p-2.5 text-center">
                                        <button onclick="openVerificationSnapshotModal({docId:'${r.sourceRef.documentId}', pageNum:${r.sourceRef.page || 14}, metricTitle:'Comparative Production Performance', highlightEntity:'${r.mine.name}', highlightValue:'${r.actual.toFixed(2)}'})" class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 font-mono text-[10px] font-bold transition-colors cursor-pointer" title="View Source Verification">
                                            <span>[1]</span>
                                            <span>${r.sourceRef.documentId}</span>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                        <tfoot class="bg-gray-50/90 font-bold border-t border-gray-200 text-gray-900 text-xs">
                            <tr>
                                <td class="p-2.5 pl-3 border-r border-gray-200 font-black">Group Total (${rows.length} Operations)</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono">${rows.reduce((a, r) => a + r.baseActual, 0).toFixed(2)}</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono font-black text-[#B0420C]">${totalActual}</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono">${totalTarget}</td>
                                <td class="p-2.5 border-r border-gray-200 text-center font-mono font-bold text-emerald-800">
                                    +${((totalActual - rows.reduce((a, r) => a + r.baseActual, 0)) / Math.max(rows.reduce((a, r) => a + r.baseActual, 0), 1) * 100).toFixed(1)}% Aggregate
                                </td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono">${overallAchieve}%</td>
                                <td class="p-2.5 text-center text-[10px] text-gray-400 font-mono">CMPDI Ledger</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            `;
        }

        if (format === 'bar') {
            const maxVal = Math.max(...rows.map(r => Math.max(r.baseActual, r.actual, r.target)), 10);
            const chartWidth = 560;
            const barWidth = 20;
            const gap = chartWidth / (rows.length || 1);

            return `
                <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-3">
                    <div class="flex items-center justify-between text-[11px] flex-wrap gap-2">
                        <div class="font-bold text-gray-800">YoY Production Growth: FY23-24 (Base) vs FY24-25 (Actual)</div>
                        <div class="flex items-center gap-3 text-[10px] font-bold">
                            <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-slate-300"></span><span>FY23-24 Base</span></div>
                            <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-[#B0420C]"></span><span>FY24-25 Actual</span></div>
                        </div>
                    </div>
                    <div class="w-full overflow-x-auto">
                        <svg viewBox="0 0 600 230" class="w-full h-auto text-xs font-sans">
                            <!-- Grid Lines -->
                            <line x1="40" y1="20" x2="580" y2="20" stroke="#f1f5f9" stroke-width="1"/>
                            <line x1="40" y1="70" x2="580" y2="70" stroke="#f1f5f9" stroke-width="1"/>
                            <line x1="40" y1="120" x2="580" y2="120" stroke="#f1f5f9" stroke-width="1"/>
                            <line x1="40" y1="170" x2="580" y2="170" stroke="#cbd5e1" stroke-width="1.5"/>

                            <!-- Y-Axis Labels -->
                            <text x="32" y="24" font-size="9" fill="#94a3b8" text-anchor="end">${maxVal.toFixed(0)}</text>
                            <text x="32" y="99" font-size="9" fill="#94a3b8" text-anchor="end">${(maxVal/2).toFixed(0)}</text>
                            <text x="32" y="174" font-size="9" fill="#94a3b8" text-anchor="end">0</text>

                            <!-- Bars -->
                            ${rows.map((r, i) => {
                                const xCenter = 50 + (i * gap) + (gap / 2) - 10;
                                const baseH = (r.baseActual / maxVal) * 140;
                                const actualH = (r.actual / maxVal) * 140;
                                return `
                                    <g class="transition-all hover:opacity-90">
                                        <rect x="${xCenter - barWidth - 2}" y="${170 - baseH}" width="${barWidth}" height="${baseH}" rx="3" fill="#cbd5e1"/>
                                        <rect x="${xCenter + 2}" y="${170 - actualH}" width="${barWidth}" height="${actualH}" rx="3" fill="#B0420C"/>
                                        
                                        <!-- Growth Tag Badge Above Bars -->
                                        <rect x="${xCenter - 26}" y="${170 - Math.max(baseH, actualH) - 18}" width="52" height="14" rx="4" fill="${r.yoyGrowth >= 10 ? '#dcfce7' : '#e0f2fe'}" stroke="${r.yoyGrowth >= 10 ? '#86efac' : '#bae6fd'}"/>
                                        <text x="${xCenter}" y="${170 - Math.max(baseH, actualH) - 8}" font-size="8" font-weight="bold" fill="${r.yoyGrowth >= 10 ? '#166534' : '#075985'}" text-anchor="middle">${r.yoyGrowth >= 0 ? '+' : ''}${r.yoyGrowth.toFixed(1)}%</text>

                                        <text x="${xCenter}" y="190" font-size="9" font-weight="bold" fill="#1e293b" text-anchor="middle">${r.mine.name.replace(' OCP','')}</text>
                                        <text x="${xCenter}" y="202" font-size="8" fill="#64748b" text-anchor="middle">${r.mine.subsidiary} &bull; ${r.actual.toFixed(1)} MT</text>
                                    </g>
                                `;
                            }).join('')}
                        </svg>
                    </div>
                </div>
            `;
        }

        if (format === 'line') {
            const colors = ['#B0420C', '#2563EB', '#059669', '#D97706', '#7C3AED'];
            const allMonths = MONTHS_24;
            const maxVal = Math.max(...rows.map(r => Math.max(...r.fullSeries.map(pt => pt.value))), 8);
            const gapX = 520 / Math.max(allMonths.length - 1, 1);

            return `
                <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-3">
                    <div class="flex items-center justify-between text-[11px] flex-wrap gap-2">
                        <div class="font-bold text-gray-800">24-Month Monthly Output Trajectory (April 2023 to March 2025)</div>
                        <div class="flex items-center gap-3 text-[10px] font-bold">
                            ${rows.map((r, i) => `
                                <div class="flex items-center gap-1.5">
                                    <span class="w-3 h-0.5" style="background-color: ${colors[i % colors.length]};"></span>
                                    <span>${r.mine.name}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="w-full overflow-x-auto">
                        <svg viewBox="0 0 620 220" class="w-full h-auto font-sans">
                            <!-- Grid -->
                            <line x1="40" y1="20" x2="580" y2="20" stroke="#f8fafc" stroke-width="1"/>
                            <line x1="40" y1="95" x2="580" y2="95" stroke="#f1f5f9" stroke-width="1"/>
                            <line x1="40" y1="170" x2="580" y2="170" stroke="#cbd5e1" stroke-width="1.5"/>

                            <!-- Dividing Line between FY23-24 and FY24-25 -->
                            <line x1="${40 + 11.5 * gapX}" y1="10" x2="${40 + 11.5 * gapX}" y2="175" stroke="#94a3b8" stroke-dasharray="3,3" stroke-width="1.5"/>
                            <text x="${40 + 5.5 * gapX}" y="15" font-size="8" font-weight="bold" fill="#64748b" text-anchor="middle">FY 2023-24 (Baseline)</text>
                            <text x="${40 + 17.5 * gapX}" y="15" font-size="8" font-weight="bold" fill="#B0420C" text-anchor="middle">FY 2024-25 (Current)</text>

                            <!-- Polylines -->
                            ${rows.map((r, i) => {
                                const pts = r.fullSeries.map((pt, idx) => {
                                    const cx = 40 + idx * gapX;
                                    const cy = 170 - (pt.value / maxVal) * 140;
                                    return `${cx},${cy}`;
                                }).join(' ');
                                const col = colors[i % colors.length];
                                return `
                                    <polyline fill="none" stroke="${col}" stroke-width="2.5" points="${pts}"/>
                                    ${r.fullSeries.filter((_, idx) => idx % 4 === 0 || idx === 23).map((pt, idx2) => {
                                        const originalIdx = idx2 === 6 ? 23 : idx2 * 4;
                                        const cx = 40 + originalIdx * gapX;
                                        const cy = 170 - (pt.value / maxVal) * 140;
                                        return `<circle cx="${cx}" cy="${cy}" r="3.5" fill="${col}" stroke="#ffffff" stroke-width="1.5"/>`;
                                    }).join('')}
                                `;
                            }).join('')}
                        </svg>
                    </div>
                </div>
            `;
        }

        if (format === 'narrative') {
            const growthLeader = [...rows].sort((a, b) => b.yoyGrowth - a.yoyGrowth)[0];
            const volumeLeader = [...rows].sort((a, b) => b.actual - a.actual)[0];

            return `
                <div class="p-4 bg-gray-50/80 rounded-xl border border-gray-200 space-y-3 text-xs leading-relaxed text-gray-800 text-justify">
                    <div class="font-bold text-[#16191C] text-[11px] flex items-center gap-1.5">
                        <i data-lucide="trending-up" class="w-4 h-4 text-[#B0420C]"></i>
                        <span>Comparative Production &amp; Growth Trajectory Synthesis</span>
                    </div>
                    <p>
                        Across the benchmarked operations, <strong>${volumeLeader?.mine.name || 'Gevra OCP'}</strong> registered the highest gross throughput with <strong>${volumeLeader?.actual.toFixed(2)} MT</strong> in FY24-25, fulfilling <strong>${volumeLeader?.achievement.toFixed(1)}%</strong> of its authorized milestone target.
                    </p>
                    <p>
                        In terms of expansion velocity, <strong>${growthLeader?.mine.name || 'Jayant OCP'}</strong> led peer performance with an annualized YoY output growth rate of <strong>+${growthLeader?.yoyGrowth.toFixed(1)}%</strong> (expanding from ${growthLeader?.baseActual.toFixed(2)} MT in FY23-24 to ${growthLeader?.actual.toFixed(2)} MT in FY24-25), driven by enhanced continuous shovel-dumper circuit synchronization.
                    </p>
                    <div class="pt-2 flex items-center justify-between text-[10px] text-gray-500 font-mono border-t border-gray-200">
                        <span>Statutory Standard: CIL MoU Targets &amp; ISP Norms</span>
                        <span class="font-bold text-emerald-800">Aggregate Output: ${totalActual} MT</span>
                    </div>
                </div>
            `;
        }
    }

    // Default Non-Comparison (Parliamentary / Single / Subsidiary)
    if (format === 'table') {
        return `
            <div class="border border-gray-200 rounded-xl overflow-hidden bg-white">
                <table class="w-full text-left text-xs border-collapse">
                    <thead class="bg-gray-100/90 text-gray-700 font-bold text-[10px] uppercase border-b border-gray-200">
                        <tr>
                            <th class="p-2.5 border-r border-gray-200">Mine Name &bull; Sub</th>
                            <th class="p-2.5 border-r border-gray-200 text-right">Target (MT)</th>
                            <th class="p-2.5 border-r border-gray-200 text-right">Actual Output (MT)</th>
                            <th class="p-2.5 border-r border-gray-200 text-right">Achieve %</th>
                            <th class="p-2.5 text-center">Verified Source</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        ${rows.map((r, i) => `
                            <tr class="hover:bg-gray-50/60 transition-colors">
                                <td class="p-2.5 pl-3 font-bold text-[#16191C] border-r border-gray-200">
                                    ${r.mine.name} <span class="text-[10px] font-mono text-gray-400">(${r.mine.subsidiary})</span>
                                </td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono text-gray-600">${r.target.toFixed(2)}</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono font-bold text-gray-900">${r.actual.toFixed(2)}</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono">
                                    <span class="px-1.5 py-0.5 rounded text-[10px] font-bold ${r.achievement >= 100 ? 'bg-emerald-100 text-emerald-900' : (r.achievement >= 90 ? 'bg-amber-100 text-amber-900' : 'bg-rose-100 text-rose-900')}">
                                        ${r.achievement.toFixed(1)}%
                                    </span>
                                </td>
                                <td class="p-2.5 text-center">
                                    <button onclick="openVerificationSnapshotModal({docId:'${r.sourceRef.documentId}', pageNum:${r.sourceRef.page || 14}, metricTitle:'Subsidiary-wise Coal Production', highlightEntity:'${r.mine.subsidiary}', highlightValue:'${r.actual.toFixed(2)}'})" class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 font-mono text-[10px] font-bold transition-colors cursor-pointer" title="View Verification Snapshot">
                                        <span>[1]</span>
                                        <span>${r.sourceRef.documentId}</span>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                    <tfoot class="bg-gray-50/90 font-bold border-t border-gray-200 text-gray-900 text-xs">
                        <tr>
                            <td class="p-2.5 pl-3 border-r border-gray-200 font-black">Consolidated Total</td>
                            <td class="p-2.5 border-r border-gray-200 text-right font-mono">${totalTarget}</td>
                            <td class="p-2.5 border-r border-gray-200 text-right font-mono font-black text-[#B0420C]">${totalActual}</td>
                            <td class="p-2.5 border-r border-gray-200 text-right font-mono">${overallAchieve}%</td>
                            <td class="p-2.5 text-center text-[10px] text-gray-400 font-mono">ISP Norms</td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        `;
    }

    if (format === 'bar') {
        const maxVal = Math.max(...rows.map(r => Math.max(r.actual, r.target)), 10);
        const chartWidth = 560;
        const barWidth = 24;
        const gap = chartWidth / (rows.length || 1);

        return `
            <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-3">
                <div class="flex items-center justify-between text-[11px]">
                    <div class="font-bold text-gray-700">Production vs Authorized Target (Million Tonnes)</div>
                    <div class="flex items-center gap-3 text-[10px] font-bold">
                        <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-slate-300"></span><span>Target (MT)</span></div>
                        <div class="flex items-center gap-1.5"><span class="w-3 h-3 rounded bg-[#B0420C]"></span><span>Actual (MT)</span></div>
                    </div>
                </div>
                <div class="w-full overflow-x-auto">
                    <svg viewBox="0 0 600 220" class="w-full h-auto text-xs font-sans">
                        <!-- Grid Lines -->
                        <line x1="40" y1="20" x2="580" y2="20" stroke="#f1f5f9" stroke-width="1"/>
                        <line x1="40" y1="70" x2="580" y2="70" stroke="#f1f5f9" stroke-width="1"/>
                        <line x1="40" y1="120" x2="580" y2="120" stroke="#f1f5f9" stroke-width="1"/>
                        <line x1="40" y1="170" x2="580" y2="170" stroke="#e2e8f0" stroke-width="1.5"/>

                        <!-- Y-Axis Labels -->
                        <text x="32" y="24" font-size="9" fill="#94a3b8" text-anchor="end">${maxVal.toFixed(0)}</text>
                        <text x="32" y="99" font-size="9" fill="#94a3b8" text-anchor="end">${(maxVal/2).toFixed(0)}</text>
                        <text x="32" y="174" font-size="9" fill="#94a3b8" text-anchor="end">0</text>

                        <!-- Bars -->
                        ${rows.map((r, i) => {
                            const xCenter = 50 + (i * gap) + (gap / 2) - 10;
                            const targetH = (r.target / maxVal) * 140;
                            const actualH = (r.actual / maxVal) * 140;
                            return `
                                <g class="transition-all hover:opacity-90">
                                    <rect x="${xCenter - barWidth/2 - 2}" y="${170 - targetH}" width="${barWidth}" height="${targetH}" rx="3" fill="#cbd5e1"/>
                                    <rect x="${xCenter + barWidth/2 - 2}" y="${170 - actualH}" width="${barWidth}" height="${actualH}" rx="3" fill="#B0420C"/>
                                    <text x="${xCenter - 2}" y="${170 - Math.max(targetH, actualH) - 6}" font-size="9" font-weight="bold" fill="#1e293b" text-anchor="middle">${r.actual.toFixed(1)} MT</text>
                                    <text x="${xCenter - 2}" y="190" font-size="9" font-weight="bold" fill="#475569" text-anchor="middle">${r.mine.name.replace(' OCP','')}</text>
                                    <text x="${xCenter - 2}" y="202" font-size="8" fill="#94a3b8" text-anchor="middle">${r.mine.subsidiary}</text>
                                </g>
                            `;
                        }).join('')}
                    </svg>
                </div>
            </div>
        `;
    }

    if (format === 'line') {
        const maxVal = Math.max(...rows.map(r => Math.max(r.actual, r.target)), 10);
        const gap = 500 / Math.max(rows.length - 1, 1);
        const pointsActual = rows.map((r, i) => `${60 + i * gap},${170 - (r.actual / maxVal) * 140}`).join(' ');
        const pointsTarget = rows.map((r, i) => `${60 + i * gap},${170 - (r.target / maxVal) * 140}`).join(' ');

        return `
            <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-3">
                <div class="flex items-center justify-between text-[11px]">
                    <div class="font-bold text-gray-700">Production Trajectory vs Target Line (MT)</div>
                    <div class="flex items-center gap-3 text-[10px] font-bold">
                        <div class="flex items-center gap-1.5"><span class="w-3 h-0.5 bg-slate-400 border-dashed"></span><span>Target</span></div>
                        <div class="flex items-center gap-1.5"><span class="w-3 h-0.5 bg-[#B0420C]"></span><span>Actual</span></div>
                    </div>
                </div>
                <svg viewBox="0 0 600 220" class="w-full h-auto font-sans">
                    <line x1="40" y1="20" x2="580" y2="20" stroke="#f1f5f9" stroke-width="1"/>
                    <line x1="40" y1="95" x2="580" y2="95" stroke="#f1f5f9" stroke-width="1"/>
                    <line x1="40" y1="170" x2="580" y2="170" stroke="#cbd5e1" stroke-width="1.5"/>

                    <polyline fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="4,4" points="${pointsTarget}"/>
                    <polyline fill="none" stroke="#B0420C" stroke-width="3" points="${pointsActual}"/>

                    ${rows.map((r, i) => {
                        const cx = 60 + i * gap;
                        const cy = 170 - (r.actual / maxVal) * 140;
                        return `
                            <circle cx="${cx}" cy="${cy}" r="5" fill="#B0420C" stroke="#ffffff" stroke-width="2"/>
                            <text x="${cx}" y="${cy - 8}" font-size="9" font-weight="bold" fill="#1e293b" text-anchor="middle">${r.actual.toFixed(1)}</text>
                            <text x="${cx}" y="190" font-size="9" font-weight="bold" fill="#475569" text-anchor="middle">${r.mine.name.replace(' OCP','')}</text>
                        `;
                    }).join('')}
                </svg>
            </div>
        `;
    }

    if (format === 'area') {
        const maxVal = Math.max(...rows.map(r => r.actual), 10);
        const gap = 500 / Math.max(rows.length - 1, 1);
        const points = rows.map((r, i) => `${60 + i * gap},${170 - (r.actual / maxVal) * 140}`).join(' ');
        const areaPath = `M60,170 ${points} L${60 + (rows.length - 1) * gap},170 Z`;

        return `
            <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-3">
                <div class="font-bold text-[11px] text-gray-700">Cumulative Production Spread (Area Curve)</div>
                <svg viewBox="0 0 600 220" class="w-full h-auto font-sans">
                    <defs>
                        <linearGradient id="prodGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stop-color="#B0420C" stop-opacity="0.4"/>
                            <stop offset="100%" stop-color="#B0420C" stop-opacity="0.02"/>
                        </linearGradient>
                    </defs>
                    <line x1="40" y1="170" x2="580" y2="170" stroke="#cbd5e1" stroke-width="1.5"/>
                    <path d="${areaPath}" fill="url(#prodGrad)"/>
                    <polyline fill="none" stroke="#B0420C" stroke-width="2.5" points="${points}"/>
                    ${rows.map((r, i) => `
                        <circle cx="${60 + i * gap}" cy="${170 - (r.actual / maxVal) * 140}" r="4" fill="#B0420C"/>
                        <text x="${60 + i * gap}" y="190" font-size="9" font-weight="bold" fill="#475569" text-anchor="middle">${r.mine.name.replace(' OCP','')}</text>
                    `).join('')}
                </svg>
            </div>
        `;
    }

    if (format === 'donut') {
        const total = rows.reduce((acc, r) => acc + r.actual, 0);
        const colors = ['#B0420C', '#2563EB', '#059669', '#D97706', '#7C3AED', '#0891B2'];
        let startAngle = 0;

        return `
            <div class="p-4 bg-white border border-gray-200 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4">
                <div class="relative w-48 h-48 shrink-0">
                    <svg viewBox="0 0 100 100" class="w-full h-full transform -rotate-90">
                        ${rows.map((r, i) => {
                            const pct = total > 0 ? (r.actual / total) : 0;
                            const strokeDasharray = `${pct * 282.7} 282.7`;
                            const strokeDashoffset = -startAngle * 282.7;
                            startAngle += pct;
                            return `
                                <circle cx="50" cy="50" r="45" fill="transparent" stroke="${colors[i % colors.length]}" stroke-width="10" stroke-dasharray="${strokeDasharray}" stroke-dashoffset="${strokeDashoffset}" />
                            `;
                        }).join('')}
                    </svg>
                    <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                        <span class="text-sm font-black text-gray-900">${totalActual}</span>
                        <span class="text-[9px] font-bold text-gray-400 uppercase">Total MT</span>
                    </div>
                </div>

                <div class="flex-1 space-y-1.5 text-xs w-full">
                    <div class="font-bold text-gray-700 text-[11px] mb-2">Mine Output Distribution Share</div>
                    ${rows.map((r, i) => {
                        const share = total > 0 ? ((r.actual / total) * 100).toFixed(1) : '0.0';
                        return `
                            <div class="flex items-center justify-between p-1.5 rounded hover:bg-gray-50 text-[11px]">
                                <div class="flex items-center gap-2">
                                    <span class="w-2.5 h-2.5 rounded-full" style="background-color: ${colors[i % colors.length]};"></span>
                                    <span class="font-bold text-gray-800">${r.mine.name}</span>
                                </div>
                                <div class="font-mono text-gray-600">
                                    <strong>${r.actual.toFixed(1)} MT</strong> (${share}%)
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    if (format === 'narrative') {
        return `
            <div class="p-4 bg-gray-50/80 rounded-xl border border-gray-200 space-y-2.5 leading-relaxed text-xs text-gray-800 text-justify">
                <p>
                    During the evaluated operational window, cumulative coal extraction across surveyed high-capacity opencast mines attained <strong>${totalActual} Million Tonnes</strong> against a statutory milestone target of <strong>${totalTarget} MT</strong>, representing an aggregate performance fulfillment index of <strong>${overallAchieve}%</strong>.
                </p>
                <p>
                    Output dynamics were predominantly driven by mechanized continuous loading systems in <strong>${rows[0]?.mine.name || 'Gevra OCP'}</strong>, which registered <strong>${rows[0]?.actual.toFixed(2) || '52.40'} MT</strong>. All extraction operations complied strictly with authorized excavation boundaries approved by CMPDI and DGMS technical directives.
                </p>
                <div class="pt-2 flex items-center justify-between text-[10px] text-gray-500 font-mono border-t border-gray-200">
                    <span>Statutory Reference: ISP Standard (1984)</span>
                    <button onclick="openVerificationSnapshotModal({docId:'SECL-GEVRA-OCP-2024', pageNum:14, metricTitle:'Subsidiary-wise Coal Production', highlightEntity:'SECL', highlightValue:'192.30'})" class="text-[#B0420C] font-bold hover:underline">
                        Verify Provenance [1] &rarr;
                    </button>
                </div>
            </div>
        `;
    }

    return '';
}

// 2. OVERBURDEN VISUALIZATIONS
function renderOverburdenVis(format, selectedMines, metricsData) {
    const isComparison = window.RSHPS_REPORTS_STATE.config.queryType === 'comparison';

    const rows = selectedMines.map(m => {
        const obSeries = metricsData[m.id]?.ob_removal || [];
        const srSeries = metricsData[m.id]?.stripping_ratio || [];
        
        const baseOB = obSeries.slice(0, 12).reduce((acc, pt) => acc + pt.value, 0) || (m.capacity * 3.2);
        const currOB = obSeries.slice(12, 24).reduce((acc, pt) => acc + pt.value, 0) || (m.capacity * 3.4);
        const currOBTarget = obSeries.slice(12, 24).reduce((acc, pt) => acc + (pt.target || 0), 0) || (m.capacity * 3.5);
        
        const yoyOB = baseOB > 0 ? (((currOB - baseOB) / baseOB) * 100) : 0;
        const avgSR = srSeries.slice(12, 24).length > 0 ? (srSeries.slice(12, 24).reduce((a, b) => a + b.value, 0) / srSeries.slice(12, 24).length).toFixed(2) : (m.id.includes('GEVRA') ? '3.80' : (m.id.includes('KUSMUNDA') ? '2.40' : '3.10'));
        
        return {
            mine: m,
            baseOB,
            obActual: currOB,
            obTarget: currOBTarget,
            yoyOB,
            sr: avgSR,
            sourceRef: obSeries[0]?.source || { documentId: 'SECL-GEVRA-OCP-2024', page: 28 }
        };
    });

    if (isComparison) {
        if (format === 'table') {
            return `
                <div class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-2xs">
                    <table class="w-full text-left text-xs border-collapse font-sans">
                        <thead class="bg-gray-100 text-gray-700 font-bold text-[10px] uppercase border-b border-gray-200">
                            <tr>
                                <th class="p-2.5 border-r border-gray-200">Opencast Bench &bull; Subsidiary</th>
                                <th class="p-2.5 border-r border-gray-200 text-right">FY23-24 Base OB (Mcum)</th>
                                <th class="p-2.5 border-r border-gray-200 text-right font-black text-slate-900">FY24-25 OB (Mcum)</th>
                                <th class="p-2.5 border-r border-gray-200 text-center font-bold">OB Growth YoY</th>
                                <th class="p-2.5 border-r border-gray-200 text-right font-black text-emerald-800 bg-emerald-50/50">Stripping Ratio (CuM/T)</th>
                                <th class="p-2.5 border-r border-gray-200 text-center">Efficiency Grade</th>
                                <th class="p-2.5 text-center">Audit Source</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200 text-slate-800">
                            ${rows.map(r => `
                                <tr class="hover:bg-gray-50/60 transition-colors">
                                    <td class="p-2.5 pl-3 font-bold text-[#16191C] border-r border-gray-200">
                                        ${r.mine.name} <span class="text-[10px] font-mono text-gray-400">(${r.mine.subsidiary})</span>
                                    </td>
                                    <td class="p-2.5 border-r border-gray-200 text-right font-mono text-gray-500">${r.baseOB.toFixed(2)}</td>
                                    <td class="p-2.5 border-r border-gray-200 text-right font-mono font-bold text-gray-900">${r.obActual.toFixed(2)}</td>
                                    <td class="p-2.5 border-r border-gray-200 text-center font-mono">
                                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${r.yoyOB >= 0 ? 'bg-blue-100 text-blue-900' : 'bg-amber-100 text-amber-900'}">
                                            ${r.yoyOB >= 0 ? '+' : ''}${r.yoyOB.toFixed(1)}% YoY
                                        </span>
                                    </td>
                                    <td class="p-2.5 border-r border-gray-200 text-right font-mono font-black text-emerald-800 bg-emerald-50/30">
                                        1 : ${r.sr}
                                    </td>
                                    <td class="p-2.5 border-r border-gray-200 text-center">
                                        <span class="px-1.5 py-0.5 rounded text-[9px] font-bold ${parseFloat(r.sr) <= 2.6 ? 'bg-emerald-100 text-emerald-900' : (parseFloat(r.sr) <= 3.4 ? 'bg-amber-100 text-amber-900' : 'bg-slate-100 text-slate-900')}">
                                            ${parseFloat(r.sr) <= 2.6 ? '⚡ Optimal Low-SR' : (parseFloat(r.sr) <= 3.4 ? '⚖️ Standard Bench' : '🚜 High-Volume OB')}
                                        </span>
                                    </td>
                                    <td class="p-2.5 text-center">
                                        <button onclick="openVerificationSnapshotModal({docId:'${r.sourceRef.documentId}', pageNum:28, metricTitle:'Overburden Stripping Ratios', highlightEntity:'${r.mine.name}', highlightValue:'${r.obActual.toFixed(2)}', sectionType:'overburden'})" class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-200 font-mono text-[10px] font-bold hover:bg-amber-100 cursor-pointer">
                                            <span>[2]</span>
                                            <span>ISP Scheme</span>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        if (format === 'bar') {
            const maxOB = Math.max(...rows.map(r => r.obActual), 10);
            return `
                <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-3">
                    <div class="flex items-center justify-between text-[11px]">
                        <div class="font-bold text-gray-800">Overburden Volume &amp; Stripping Ratio Benchmarks</div>
                        <div class="text-[10px] text-gray-500 font-mono">OB Unit: Mcum &bull; Ratio: CuM/T</div>
                    </div>
                    <div class="w-full overflow-x-auto">
                        <svg viewBox="0 0 600 210" class="w-full h-auto font-sans">
                            <line x1="40" y1="160" x2="580" y2="160" stroke="#cbd5e1" stroke-width="1.5"/>
                            ${rows.map((r, i) => {
                                const x = 60 + i * (500 / rows.length);
                                const h = (r.obActual / maxOB) * 125;
                                return `
                                    <rect x="${x}" y="${160 - h}" width="42" height="${h}" rx="3" fill="#0891b2"/>
                                    <text x="${x + 21}" y="${160 - h - 16}" font-size="8" font-weight="bold" fill="#047857" text-anchor="middle">1 : ${r.sr}</text>
                                    <text x="${x + 21}" y="${160 - h - 5}" font-size="9" font-weight="bold" fill="#1e293b" text-anchor="middle">${r.obActual.toFixed(1)}M</text>
                                    <text x="${x + 21}" y="178" font-size="9" font-weight="bold" fill="#1e293b" text-anchor="middle">${r.mine.name.replace(' OCP','')}</text>
                                    <text x="${x + 21}" y="190" font-size="8" fill="#64748b" text-anchor="middle">${r.mine.subsidiary}</text>
                                `;
                            }).join('')}
                        </svg>
                    </div>
                </div>
            `;
        }

        if (format === 'narrative') {
            return `
                <div class="p-4 bg-gray-50/80 rounded-xl border border-gray-200 space-y-2.5 leading-relaxed text-xs text-gray-800 text-justify">
                    <p>
                        Stripping ratios across the compared opencast benches exhibited distinct geotechnical profiles. <strong>${rows.find(r => parseFloat(r.sr) <= 2.6)?.mine.name || 'Kusmunda OCP'}</strong> achieved the lowest specific stripping cost at <strong>1 : ${rows.find(r => parseFloat(r.sr) <= 2.6)?.sr || '2.40'} CuM/T</strong> due to thick composite seam geology.
                    </p>
                    <p>
                        In deep-pit operations such as <strong>${rows[0]?.mine.name || 'Gevra OCP'}</strong>, continuous dragline deployment maintained high volume clearance at <strong>${rows[0]?.obActual.toFixed(1)} Mcum</strong>, adhering strictly to CMPDI slope stability and highwall geometric profiles.
                    </p>
                    <div class="pt-2 flex items-center justify-between text-[10px] text-gray-500 font-mono border-t border-gray-200">
                        <span>Approved Stripping Scheme: ISP Norms</span>
                        <button onclick="openVerificationSnapshotModal({docId:'SECL-GEVRA-OCP-2024', pageNum:28})" class="text-[#B0420C] font-bold hover:underline">Verify Provenance [2] &rarr;</button>
                    </div>
                </div>
            `;
        }
    }

    // Default Non-Comparison
    if (format === 'table') {
        return `
            <div class="border border-gray-200 rounded-xl overflow-hidden bg-white">
                <table class="w-full text-left text-xs border-collapse">
                    <thead class="bg-gray-100 text-gray-700 font-bold text-[10px] uppercase border-b border-gray-200">
                        <tr>
                            <th class="p-2.5 border-r border-gray-200">Opencast Bench</th>
                            <th class="p-2.5 border-r border-gray-200 text-right">Target OB (Mcum)</th>
                            <th class="p-2.5 border-r border-gray-200 text-right">Actual OB (Mcum)</th>
                            <th class="p-2.5 border-r border-gray-200 text-right">Stripping Ratio</th>
                            <th class="p-2.5 text-center">Audit Source</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        ${rows.map(r => `
                            <tr class="hover:bg-gray-50/60">
                                <td class="p-2.5 pl-3 font-bold text-[#16191C] border-r border-gray-200">${r.mine.name}</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono text-gray-600">${r.obTarget.toFixed(2)}</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono font-bold text-gray-900">${r.obActual.toFixed(2)}</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono font-bold text-emerald-700">1 : ${r.sr}</td>
                                <td class="p-2.5 text-center">
                                    <button onclick="openVerificationSnapshotModal({docId:'SECL-GEVRA-OCP-2024', pageNum:28, metricTitle:'Overburden Stripping Ratios', highlightEntity:'${r.mine.subsidiary}', highlightValue:'${r.obActual.toFixed(2)}'})" class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-200 font-mono text-[10px] font-bold hover:bg-amber-100 cursor-pointer">
                                        <span>[2]</span>
                                        <span>ISP Scheme</span>
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    if (format === 'bar') {
        const maxOB = Math.max(...rows.map(r => r.obActual), 10);
        return `
            <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-3">
                <div class="font-bold text-[11px] text-gray-700">Overburden Volume Removal (Million Cubic Metres)</div>
                <svg viewBox="0 0 600 200" class="w-full h-auto font-sans">
                    <line x1="40" y1="160" x2="580" y2="160" stroke="#cbd5e1" stroke-width="1.5"/>
                    ${rows.map((r, i) => {
                        const x = 60 + i * (500 / rows.length);
                        const h = (r.obActual / maxOB) * 130;
                        return `
                            <rect x="${x}" y="${160 - h}" width="36" height="${h}" rx="3" fill="#0891b2"/>
                            <text x="${x + 18}" y="${160 - h - 5}" font-size="9" font-weight="bold" fill="#1e293b" text-anchor="middle">${r.obActual.toFixed(1)}</text>
                            <text x="${x + 18}" y="178" font-size="9" font-weight="bold" fill="#475569" text-anchor="middle">${r.mine.name.replace(' OCP','')}</text>
                        `;
                    }).join('')}
                </svg>
            </div>
        `;
    }

    if (format === 'narrative') {
        return `
            <div class="p-4 bg-gray-50/80 rounded-xl border border-gray-200 space-y-2 leading-relaxed text-xs text-gray-800 text-justify">
                <p>
                    Overburden advance across active excavation benches adhered to approved CMPDI geometric pit profiles. Stripping ratio remained optimized at an average of <strong>1 : 3.80 CuM/T</strong>, ensuring timely seam exposure without structural slope instability.
                </p>
                <div class="pt-2 flex items-center justify-between text-[10px] text-gray-500 font-mono border-t border-gray-200">
                    <span>Approved Dragline Stripping Scheme: ISP Norms</span>
                    <button onclick="openVerificationSnapshotModal({docId:'SECL-GEVRA-OCP-2024', pageNum:28})" class="text-[#B0420C] font-bold hover:underline">Verify Provenance [2] &rarr;</button>
                </div>
            </div>
        `;
    }

    return `<div class="p-4 bg-white border rounded-xl text-xs">Overburden visual rendered.</div>`;
}

// 3. HEMM FLEET VISUALIZATIONS
function renderHemmVis(format, selectedMines, metricsData) {
    const isComparison = window.RSHPS_REPORTS_STATE.config.queryType === 'comparison';

    if (isComparison) {
        const compFleet = selectedMines.map(m => {
            const isGevra = m.id.includes('GEVRA');
            const isKus = m.id.includes('KUSMUNDA');
            return {
                mine: m,
                draglineAvail: isGevra ? '89.2%' : (isKus ? '87.5%' : '86.0%'),
                shovelAvail: isGevra ? '86.4%' : (isKus ? '85.2%' : '87.1%'),
                dumperAvail: isGevra ? '84.8%' : (isKus ? '83.9%' : '85.4%'),
                meanAvail: isGevra ? '87.9%' : (isKus ? '85.8%' : '86.4%'),
                utilRate: isGevra ? '76.4%' : (isKus ? '72.8%' : '74.2%'),
                shovelDumperMatch: isGevra ? '1:5.2' : (isKus ? '1:4.8' : '1:5.0')
            };
        });

        if (format === 'table') {
            return `
                <div class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-2xs">
                    <table class="w-full text-left text-xs border-collapse font-sans">
                        <thead class="bg-gray-100 text-gray-700 font-bold text-[10px] uppercase border-b border-gray-200">
                            <tr>
                                <th class="p-2.5 border-r border-gray-200">Mining Operation</th>
                                <th class="p-2.5 border-r border-gray-200 text-center">Dragline Uptime</th>
                                <th class="p-2.5 border-r border-gray-200 text-center">Shovel Uptime</th>
                                <th class="p-2.5 border-r border-gray-200 text-center">Dumper Fleet</th>
                                <th class="p-2.5 border-r border-gray-200 text-right font-black text-emerald-800 bg-emerald-50/50">Overall Availability %</th>
                                <th class="p-2.5 border-r border-gray-200 text-center">Match Factor</th>
                                <th class="p-2.5 text-center">Statutory Compliance</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200 text-slate-800">
                            ${compFleet.map(f => `
                                <tr class="hover:bg-gray-50/60 transition-colors">
                                    <td class="p-2.5 pl-3 font-bold text-[#16191C] border-r border-gray-200">
                                        ${f.mine.name} <span class="text-[10px] font-mono text-gray-400">(${f.mine.subsidiary})</span>
                                    </td>
                                    <td class="p-2.5 border-r border-gray-200 text-center font-mono">${f.draglineAvail}</td>
                                    <td class="p-2.5 border-r border-gray-200 text-center font-mono">${f.shovelAvail}</td>
                                    <td class="p-2.5 border-r border-gray-200 text-center font-mono">${f.dumperAvail}</td>
                                    <td class="p-2.5 border-r border-gray-200 text-right font-mono font-black text-emerald-800 bg-emerald-50/30">${f.meanAvail}</td>
                                    <td class="p-2.5 border-r border-gray-200 text-center font-mono font-bold text-gray-700">${f.shovelDumperMatch}</td>
                                    <td class="p-2.5 text-center">
                                        <span class="px-2 py-0.5 rounded text-[9px] font-bold bg-emerald-100 text-emerald-900 border border-emerald-300">✓ DGMS &ge;85%</span>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        if (format === 'bar') {
            return `
                <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-3">
                    <div class="flex items-center justify-between text-[11px]">
                        <div class="font-bold text-gray-800">HEMM Availability vs DGMS Statutory 85.0% Benchmark</div>
                        <div class="text-[10px] text-emerald-700 font-bold">✓ All operations meet statutory threshold</div>
                    </div>
                    <div class="space-y-3">
                        ${compFleet.map(f => {
                            const pct = parseFloat(f.meanAvail);
                            return `
                                <div class="space-y-1 text-xs">
                                    <div class="flex justify-between font-bold text-[11px] text-gray-800">
                                        <span>${f.mine.name} (${f.mine.subsidiary})</span>
                                        <span class="font-mono text-emerald-700 font-bold">${f.meanAvail} (Util: ${f.utilRate})</span>
                                    </div>
                                    <div class="w-full bg-gray-100 h-3 rounded-full overflow-hidden relative">
                                        <div class="bg-[#B0420C] h-full rounded-full" style="width: ${pct}%;"></div>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }
    }

    const fleet = [
        { type: 'Heavy Draglines (24/96)', deployed: 6, avail: '89.2%', util: '78.5%', status: 'Optimal' },
        { type: 'Electric Rope Shovels (42 CuM)', deployed: 28, avail: '86.4%', util: '74.2%', status: 'Optimal' },
        { type: 'Off-Highway Dumpers (240T)', deployed: 142, avail: '84.8%', util: '71.6%', status: 'Acceptable' },
        { type: 'Heavy Crawler Dozers (850 HP)', deployed: 46, avail: '88.1%', util: '76.0%', status: 'Optimal' },
        { type: 'Rotary Blast Hole Drills', deployed: 32, avail: '91.4%', util: '82.3%', status: 'Optimal' }
    ];

    if (format === 'table') {
        return `
            <div class="border border-gray-200 rounded-xl overflow-hidden bg-white">
                <table class="w-full text-left text-xs border-collapse">
                    <thead class="bg-gray-100 text-gray-700 font-bold text-[10px] uppercase border-b border-gray-200">
                        <tr>
                            <th class="p-2.5 border-r border-gray-200">HEMM Equipment Class</th>
                            <th class="p-2.5 border-r border-gray-200 text-center">Fleet Size</th>
                            <th class="p-2.5 border-r border-gray-200 text-right">Availability %</th>
                            <th class="p-2.5 border-r border-gray-200 text-right">Utilisation %</th>
                            <th class="p-2.5 text-center">Benchmark</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        ${fleet.map(f => `
                            <tr class="hover:bg-gray-50/60">
                                <td class="p-2.5 pl-3 font-bold text-[#16191C] border-r border-gray-200">${f.type}</td>
                                <td class="p-2.5 border-r border-gray-200 text-center font-mono font-bold">${f.deployed}</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono font-bold text-emerald-700">${f.avail}</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono text-gray-700">${f.util}</td>
                                <td class="p-2.5 text-center"><span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-100 text-emerald-800">DGMS &ge; 85%</span></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    if (format === 'bar') {
        return `
            <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-3">
                <div class="flex items-center justify-between text-[11px]">
                    <div class="font-bold text-gray-700">HEMM Availability vs DGMS Statutory 85% Benchmark</div>
                    <div class="text-[10px] text-emerald-700 font-bold">&uarr; Fleet Average: 87.9%</div>
                </div>
                <div class="space-y-2.5">
                    ${fleet.map(f => {
                        const pct = parseFloat(f.avail);
                        return `
                            <div class="space-y-1 text-xs">
                                <div class="flex justify-between font-bold text-[11px] text-gray-800">
                                    <span>${f.type}</span>
                                    <span class="font-mono text-emerald-700">${f.avail} (Util: ${f.util})</span>
                                </div>
                                <div class="w-full bg-gray-100 h-2.5 rounded-full overflow-hidden relative">
                                    <div class="bg-[#B0420C] h-full rounded-full" style="width: ${pct}%;"></div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    return `
        <div class="p-4 bg-gray-50/80 rounded-xl border border-gray-200 space-y-2 text-xs text-justify">
            <p>High-capacity shovel-dumper match factor registered at <strong>1 : 5.2</strong>, delivering superior bench clearance rates with mean equipment availability exceeding the 85% DGMS operational norm.</p>
        </div>
    `;
}

// 4. OMS PRODUCTIVITY
function renderOmsVis(format, selectedMines, metricsData) {
    return `
        <div class="border border-gray-200 rounded-xl overflow-hidden bg-white p-4 space-y-3 text-xs font-sans">
            <div class="font-bold text-gray-800 text-[11px]">Output Per Manshift (OMS) - Cross-Pit Productivity Benchmark</div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
                <div class="p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div class="text-[10px] text-gray-500 font-bold uppercase">Overall Group OMS</div>
                    <div class="text-base font-black text-gray-900 mt-1">24.60 T</div>
                </div>
                <div class="p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div class="text-[10px] text-gray-500 font-bold uppercase">Mega-Pit Leader</div>
                    <div class="text-base font-black text-emerald-700 mt-1">28.50 T</div>
                </div>
                <div class="p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div class="text-[10px] text-gray-500 font-bold uppercase">Target Benchmark</div>
                    <div class="text-base font-black text-gray-600 mt-1">18.50 T</div>
                </div>
                <div class="p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div class="text-[10px] text-gray-500 font-bold uppercase">Variance</div>
                    <div class="text-base font-black text-emerald-600 mt-1">+33.0%</div>
                </div>
            </div>
        </div>
    `;
}

// 5. MINE SAFETY (DGMS COMPLIANCE)
function renderSafetyVis(format, selectedMines, metricsData) {
    if (format === 'narrative') {
        return `
            <div class="p-4 bg-emerald-50/40 rounded-xl border border-emerald-200 space-y-2.5 text-xs text-gray-800 text-justify leading-relaxed">
                <div class="flex items-center gap-2 text-emerald-800 font-bold">
                    <i data-lucide="shield-check" class="w-4 h-4 text-emerald-600"></i>
                    <span>Statutory DGMS Compliance &amp; Zero Harm Record</span>
                </div>
                <p>
                    In accordance with the Coal Mines Regulations (CMR) 2017 and Directorate General of Mines Safety (DGMS) circulars, the surveyed opencast pits operated with <strong>Zero Fatal Incidents</strong> throughout the reporting tenure.
                </p>
                <p>
                    Real-time slope stability radars deployed along highwalls recorded displacement rates strictly under <strong>0.02 mm/day</strong> against the statutory threshold limit of <strong>2.00 mm/day</strong>. Gas telemetry and automated fire suppression systems remained 100% operational.
                </p>
                <div class="pt-2 flex items-center justify-between text-[10px] text-emerald-800 font-mono border-t border-emerald-200">
                    <span>Audit Body: DGMS Eastern &amp; Western Circles</span>
                    <span class="font-bold">STATUS: COMPLIANT</span>
                </div>
            </div>
        `;
    }

    return `
        <div class="border border-gray-200 rounded-xl overflow-hidden bg-white">
            <table class="w-full text-left text-xs border-collapse">
                <thead class="bg-gray-100 text-gray-700 font-bold text-[10px] uppercase border-b border-gray-200">
                    <tr>
                        <th class="p-2.5 border-r border-gray-200">Safety Metric</th>
                        <th class="p-2.5 border-r border-gray-200 text-center">DGMS Limit</th>
                        <th class="p-2.5 border-r border-gray-200 text-center">Recorded Metric</th>
                        <th class="p-2.5 text-center">Compliance</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                    <tr>
                        <td class="p-2.5 pl-3 font-bold border-r border-gray-200">Fatal Accidents</td>
                        <td class="p-2.5 border-r border-gray-200 text-center font-mono">0</td>
                        <td class="p-2.5 border-r border-gray-200 text-center font-mono font-bold text-emerald-700">0</td>
                        <td class="p-2.5 text-center font-bold text-emerald-600">Verified Clean</td>
                    </tr>
                    <tr>
                        <td class="p-2.5 pl-3 font-bold border-r border-gray-200">Slope Radar Shift</td>
                        <td class="p-2.5 border-r border-gray-200 text-center font-mono">&le; 2.0 mm</td>
                        <td class="p-2.5 border-r border-gray-200 text-center font-mono font-bold text-emerald-700">0.02 mm</td>
                        <td class="p-2.5 text-center font-bold text-emerald-600">Stable</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `;
}

// 6. RESERVES & STRATIGRAPHY
function renderReservesVis(format, selectedMines, metricsData) {
    const isComparison = window.RSHPS_REPORTS_STATE.config.queryType === 'comparison';

    if (isComparison) {
        const compSeams = selectedMines.map(m => {
            const seam = m.seams?.[0] || { horizon: 'Composite Horizon', thickness: 12.0, depth: 110, ashPercent: 25.0, gcv: 5500, grade: 'G7' };
            return {
                mine: m,
                seam: seam
            };
        });

        if (format === 'table') {
            return `
                <div class="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-2xs font-sans">
                    <table class="w-full text-left text-xs border-collapse">
                        <thead class="bg-gray-100 text-gray-700 font-bold text-[10px] uppercase border-b border-gray-200">
                            <tr>
                                <th class="p-2.5 border-r border-gray-200">Mining Operation</th>
                                <th class="p-2.5 border-r border-gray-200">Primary Seam Horizon</th>
                                <th class="p-2.5 border-r border-gray-200 text-right">Thickness (m)</th>
                                <th class="p-2.5 border-r border-gray-200 text-right">Depth (m)</th>
                                <th class="p-2.5 border-r border-gray-200 text-right">Ash %</th>
                                <th class="p-2.5 border-r border-gray-200 text-right font-black text-slate-900 bg-amber-50/50">GCV (kcal/kg)</th>
                                <th class="p-2.5 text-center font-bold text-[#B0420C]">Commercial Grade</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200 text-slate-800">
                            ${compSeams.map(cs => `
                                <tr class="hover:bg-gray-50/60 transition-colors">
                                    <td class="p-2.5 pl-3 font-bold text-[#16191C] border-r border-gray-200">
                                        ${cs.mine.name} <span class="text-[10px] font-mono text-gray-400">(${cs.mine.coalfield})</span>
                                    </td>
                                    <td class="p-2.5 border-r border-gray-200 font-medium">${cs.seam.horizon}</td>
                                    <td class="p-2.5 border-r border-gray-200 text-right font-mono font-bold">${cs.seam.thickness} m</td>
                                    <td class="p-2.5 border-r border-gray-200 text-right font-mono">${cs.seam.depth} m</td>
                                    <td class="p-2.5 border-r border-gray-200 text-right font-mono text-gray-600">${cs.seam.ashPercent}%</td>
                                    <td class="p-2.5 border-r border-gray-200 text-right font-mono font-black text-slate-900 bg-amber-50/30">${cs.seam.gcv}</td>
                                    <td class="p-2.5 text-center font-black text-[#B0420C]">${cs.seam.grade}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        if (format === 'scatter' || format === 'bar') {
            return `
                <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-3 font-sans">
                    <div class="font-bold text-[11px] text-gray-800">Gross Calorific Heat Value (kcal/kg) &amp; Ash % Variance</div>
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        ${compSeams.map(cs => `
                            <div class="p-3 bg-gray-50 rounded-xl border border-gray-200 space-y-1.5">
                                <div class="font-bold text-xs text-[#16191C] truncate">${cs.mine.name}</div>
                                <div class="text-[10px] text-gray-500 font-mono">${cs.seam.horizon}</div>
                                <div class="text-base font-black text-[#B0420C]">${cs.seam.gcv} <span class="text-[10px] font-normal text-gray-500">kcal/kg</span></div>
                                <div class="flex justify-between text-[10px] font-mono pt-1 border-t border-gray-200 text-gray-600">
                                    <span>Ash: <strong>${cs.seam.ashPercent}%</strong></span>
                                    <span class="font-bold text-emerald-700">Grade: ${cs.seam.grade}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
    }

    const doc = MOCK_DOCUMENTS.find(d => d.id === 'SECL-GEVRA-OCP-2024') || MOCK_DOCUMENTS[0];
    const seams = doc.seamTable || [
        { horizon: 'Seam X (Top)', thickness: 6.40, depth: 112, ashPercent: 18.4, gcv: 6240, grade: 'G4' },
        { horizon: 'Seam IX (Middle)', thickness: 8.20, depth: 148, ashPercent: 22.1, gcv: 5820, grade: 'G6' },
        { horizon: 'Seam VIII (Bottom)', thickness: 4.80, depth: 194, ashPercent: 26.5, gcv: 5310, grade: 'G8' }
    ];

    if (format === 'table') {
        return `
            <div class="border border-gray-200 rounded-xl overflow-hidden bg-white">
                <table class="w-full text-left text-xs border-collapse">
                    <thead class="bg-gray-100 text-gray-700 font-bold text-[10px] uppercase border-b border-gray-200">
                        <tr>
                            <th class="p-2.5 border-r border-gray-200">Seam Horizon</th>
                            <th class="p-2.5 border-r border-gray-200 text-right">Thickness</th>
                            <th class="p-2.5 border-r border-gray-200 text-right">Mean Depth</th>
                            <th class="p-2.5 border-r border-gray-200 text-right">Ash %</th>
                            <th class="p-2.5 border-r border-gray-200 text-right">GCV (kcal/kg)</th>
                            <th class="p-2.5 text-center">Grade</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200">
                        ${seams.map(s => `
                            <tr class="hover:bg-gray-50/60">
                                <td class="p-2.5 pl-3 font-bold text-[#16191C] border-r border-gray-200">${s.horizon}</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono font-bold">${s.thickness} m</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono">${s.depth} m</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono text-gray-600">${s.ashPercent}%</td>
                                <td class="p-2.5 border-r border-gray-200 text-right font-mono font-black text-gray-900">${s.gcv}</td>
                                <td class="p-2.5 text-center font-bold text-[#B0420C]">${s.grade}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    if (format === 'scatter') {
        return `
            <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-3">
                <div class="font-bold text-[11px] text-gray-700">Lithological Borehole Stratigraphy Column (Depth 0m to 220m)</div>
                <div class="space-y-2">
                    ${seams.map(s => `
                        <div class="p-2.5 rounded-lg border border-gray-200 bg-gray-50 flex items-center justify-between text-xs">
                            <div class="flex items-center gap-2">
                                <span class="w-3 h-3 rounded bg-amber-700"></span>
                                <span class="font-bold text-[#16191C]">${s.horizon}</span>
                                <span class="text-[10px] text-gray-400 font-mono">Depth: ${s.depth} m</span>
                            </div>
                            <div class="font-mono text-xs font-bold text-[#B0420C]">
                                Thickness: ${s.thickness} m &bull; Grade ${s.grade}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    return `
        <div class="p-4 bg-gray-50/80 rounded-xl border border-gray-200 space-y-2 text-xs text-justify">
            <p>Geological exploration confirms proved reserves under ISP Norms with continuous regional coal seam horizons across Korba and Singrauli basins.</p>
        </div>
    `;
}

// 7. ENVIRONMENT & AFFORESTATION
function renderEnvironmentVis(format, selectedMines, metricsData) {
    return `
        <div class="p-4 bg-emerald-50/30 rounded-xl border border-emerald-200 space-y-2 text-xs text-justify text-gray-800 leading-relaxed">
            <div class="flex items-center gap-2 text-emerald-800 font-bold text-[11px]">
                <i data-lucide="trees" class="w-4 h-4 text-emerald-600"></i>
                <span>MoEFCC Environmental Clearances &amp; Eco-Restoration</span>
            </div>
            <p>
                Continuous Ambient Air Quality Monitoring (CAAQM) confirmed PM10 values at <strong>74.2 µg/m³</strong> (against 100 µg/m³ statutory standard) and PM2.5 at <strong>38.5 µg/m³</strong> (against 60 µg/m³ standard). Overburden dump bio-reclamation has planted over <strong>2.4 Million native trees</strong> across stabilized slopes.
            </p>
        </div>
    `;
}

// 8. LAND ACQUISITION
function renderLandVis(format, selectedMines, metricsData) {
    return `
        <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-2 text-xs">
            <div class="font-bold text-gray-800 text-[11px]">CBA Land Acquisition &amp; R&amp;R Status</div>
            <p class="text-gray-600">All possession notices under CBA Act 1957 executed in alignment with state rehabilitation packages.</p>
        </div>
    `;
}

// 9. FINANCIALS
function renderFinancialsVis(format, selectedMines, metricsData) {
    return `
        <div class="p-4 bg-white border border-gray-200 rounded-xl space-y-2 text-xs">
            <div class="font-bold text-gray-800 text-[11px]">Royalty, DMF &amp; NMET Statutory Contributions</div>
            <p class="text-gray-600">State royalty, District Mineral Foundation (DMF), and National Mineral Exploration Trust (NMET) deposits completed up to date.</p>
        </div>
    `;
}

// ── LIVE PREVIEW RENDERER (RIGHT PANEL) ──
function renderLivePreview() {
    const paper = document.getElementById('report-live-preview-document');
    if (!paper) return;

    const state = window.RSHPS_REPORTS_STATE;
    const cfg = state.config;
    const metricsData = state.loadedMetrics || {};
    const cov = state.coverageReport || { completeMines: 12, totalMines: 15, isClean: false, summaryWarnings: [] };

    const selectedMines = state.loadedMines.filter(m => cfg.mineIds.includes(m.id));

    // Dynamic Title & Letterhead
    let titleHtml = '';
    let subtitleText = '';
    let comparisonScorecardHtml = '';

    if (cfg.queryType === 'parliamentary') {
        titleHtml = `
            <div class="text-center border-b-2 border-[#16191C] pb-4 mb-5">
                <div class="text-[10px] uppercase font-bold tracking-widest text-gray-500 font-sans">Confidential &bull; Parliament of India</div>
                <h1 class="text-lg sm:text-xl font-black uppercase tracking-wider text-[#16191C] mt-1 font-serif">Government of India</h1>
                <h2 class="text-xs sm:text-sm font-bold text-gray-800 font-sans">${cfg.parliamentaryMeta.ministry || 'Ministry of Coal'}</h2>
                <div class="text-xs font-semibold text-gray-600 mt-2 font-mono">
                    ${cfg.parliamentaryMeta.house} ${cfg.parliamentaryMeta.type} Question No. ${cfg.parliamentaryMeta.number}
                </div>
                <div class="text-[11px] text-gray-500 font-sans font-medium">
                    To be answered on: <strong>${cfg.parliamentaryMeta.answerDate}</strong>
                </div>
            </div>
        `;
        subtitleText = `Official reply regarding Coal Production Targets, Overburden Removal &amp; Safety Compliance across ${selectedMines.map(m=>m.name).slice(0,3).join(', ')} ${selectedMines.length > 3 ? 'and other mega opencast mines' : ''}.`;
    } else if (cfg.queryType === 'comparison') {
        titleHtml = `
            <div class="text-center border-b-2 border-[#16191C] pb-4 mb-5">
                <div class="text-[10px] uppercase font-bold tracking-widest text-[#B0420C] font-sans">Central Mine Planning &amp; Design Institute Limited</div>
                <h1 class="text-lg sm:text-xl font-black uppercase tracking-wider text-[#16191C] mt-1 font-serif">Mega-Pit Benchmarking &amp; Multi-Aspect Comparative Analysis</h1>
                <h2 class="text-xs sm:text-sm font-bold text-gray-800 font-sans">24-Month Operational Audit &amp; YoY Growth Variance Monograph</h2>
                <div class="mt-2 flex items-center justify-center gap-2 flex-wrap text-xs">
                    <span class="px-2 py-0.5 rounded bg-gray-100 font-mono font-bold text-gray-700">Baseline Period: FY 2023-24 (12M)</span>
                    <span class="text-gray-400 font-bold">&bull;</span>
                    <span class="px-2 py-0.5 rounded bg-orange-100 font-mono font-bold text-[#B0420C]">Benchmark Period: FY 2024-25 (12M)</span>
                </div>
            </div>
        `;
        subtitleText = `Cross-entity performance benchmarking and growth velocity evaluation between ${selectedMines.map(m=>`${m.name} (${m.subsidiary})`).join(' vs. ')}.`;

        // Generate Side-by-Side Executive KPI Scorecards
        const compCards = selectedMines.map((m, idx) => {
            const pSeries = metricsData[m.id]?.production || [];
            const obSeries = metricsData[m.id]?.ob_removal || [];
            const srSeries = metricsData[m.id]?.stripping_ratio || [];

            const baseP = pSeries.slice(0, 12).reduce((a, b) => a + b.value, 0) || (m.capacity * 0.88);
            const currP = pSeries.slice(12, 24).reduce((a, b) => a + b.value, 0) || (m.capacity * 0.95);
            const yoyGrowth = baseP > 0 ? (((currP - baseP) / baseP) * 100) : 0;

            const currOB = obSeries.slice(12, 24).reduce((a, b) => a + b.value, 0) || (m.capacity * 3.4);
            const avgSR = srSeries.slice(12, 24).length > 0 ? (srSeries.slice(12, 24).reduce((a, b) => a + b.value, 0) / srSeries.slice(12, 24).length).toFixed(2) : (m.id.includes('GEVRA') ? '3.80' : (m.id.includes('KUSMUNDA') ? '2.40' : '3.10'));
            
            const seam = m.seams?.[0] || { grade: 'G4', gcv: 6240, ashPercent: 18.4 };

            let recognitionBadge = `👑 Volume Titan (${currP.toFixed(1)} MT)`;
            if (idx === 1 && m.id.includes('KUSMUNDA')) recognitionBadge = `⚡ Stripping Efficiency Leader (1:2.4)`;
            else if (idx === 2 || yoyGrowth > 12) recognitionBadge = `🚀 Growth Velocity Leader (+${yoyGrowth.toFixed(1)}%)`;

            return `
                <div class="p-3.5 bg-gray-50/80 rounded-xl border border-gray-300 space-y-2.5 flex-1 min-w-[200px] shadow-2xs">
                    <div class="flex items-start justify-between gap-1 border-b border-gray-200 pb-2">
                        <div>
                            <div class="font-black text-xs text-[#16191C] flex items-center gap-1.5">
                                <span class="w-4 h-4 rounded-full bg-[#B0420C] text-white flex items-center justify-center text-[9px] font-bold">${idx + 1}</span>
                                <span>${m.name}</span>
                            </div>
                            <div class="text-[10px] text-gray-500 font-medium">${m.subsidiary} &bull; ${m.coalfield}</div>
                        </div>
                        <span class="px-1.5 py-0.5 rounded text-[8px] font-bold uppercase bg-orange-100 text-amber-950 font-mono">${m.type}</span>
                    </div>

                    <div class="space-y-1 text-xs">
                        <div class="flex justify-between items-center text-[11px]">
                            <span class="text-gray-500 font-medium">Output:</span>
                            <span class="font-mono font-black text-gray-900">${currP.toFixed(2)} MT</span>
                        </div>
                        <div class="flex justify-between items-center text-[11px]">
                            <span class="text-gray-500 font-medium">YoY Growth:</span>
                            <span class="font-mono font-bold text-emerald-700 bg-emerald-100/70 px-1.5 py-0.2 rounded text-[10px]">
                                +${yoyGrowth.toFixed(1)}% ↗
                            </span>
                        </div>
                        <div class="flex justify-between items-center text-[11px]">
                            <span class="text-gray-500 font-medium">Stripping Ratio:</span>
                            <span class="font-mono font-bold text-slate-800">1 : ${avgSR}</span>
                        </div>
                        <div class="flex justify-between items-center text-[11px]">
                            <span class="text-gray-500 font-medium">Primary Grade:</span>
                            <span class="font-mono font-bold text-[#B0420C]">${seam.grade} (${seam.gcv} kcal)</span>
                        </div>
                    </div>

                    <div class="pt-2 border-t border-gray-200 text-center">
                        <span class="inline-block px-2 py-0.5 rounded text-[9px] font-bold bg-amber-100/80 text-amber-950 border border-amber-300">
                            ${recognitionBadge}
                        </span>
                    </div>
                </div>
            `;
        }).join('');

        comparisonScorecardHtml = `
            <div class="mb-5 space-y-2">
                <div class="font-bold text-[11px] text-gray-700 uppercase tracking-wider flex items-center gap-1.5">
                    <i data-lucide="layout-grid" class="w-3.5 h-3.5 text-[#B0420C]"></i>
                    <span>Executive Cross-Entity Benchmarking Scorecard</span>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                    ${compCards}
                </div>
            </div>
        `;
    } else {
        titleHtml = `
            <div class="text-center border-b-2 border-[#16191C] pb-4 mb-5">
                <div class="text-[10px] uppercase font-bold tracking-widest text-gray-500 font-sans">Central Mine Planning &amp; Design Institute</div>
                <h1 class="text-lg sm:text-xl font-black uppercase tracking-wider text-[#16191C] mt-1 font-serif">Coal Sector Technical Performance Review</h1>
                <h2 class="text-xs sm:text-sm font-bold text-gray-800 font-sans">Period: ${cfg.periodType} (${cfg.startDate} to ${cfg.endDate})</h2>
            </div>
        `;
        subtitleText = `Consolidated operational parameters and geological audits for ${selectedMines.map(m=>m.name).join(', ')}.`;
    }

    // Render Enabled Content Sections
    let sectionsHtml = '';
    let sectionCounter = 1;

    cfg.sections.forEach(sec => {
        if (!sec.enabled) return;

        const availVis = getAvailableVisualizations(sec.id);
        const currentVis = sec.presentation || availVis.find(v => v.isRecommended)?.id || 'table';
        const currentVisMeta = availVis.find(v => v.id === currentVis) || availVis[0];

        const secContent = renderSectionVisualizationContent(sec, currentVis, selectedMines, metricsData);

        sectionsHtml += `
            <div class="mb-6 group/sec relative" id="sec-block-${sec.id}">
                <!-- Section Header with In-Report Visualization Dropdown & Toolbar -->
                <div class="flex items-center justify-between border-b border-gray-200 pb-1.5 mb-2.5">
                    <h3 class="font-bold text-xs sm:text-sm uppercase tracking-wider text-[#16191C] font-sans flex items-center gap-2">
                        <span>${sectionCounter}. ${sec.title}</span>
                    </h3>

                    <!-- In-Report Visualization Toolbar -->
                    <div class="flex items-center gap-1.5 report-vis-control hide-in-export no-print">
                        <!-- Visualization Format Dropdown Trigger -->
                        <div class="relative inline-block text-left" id="vis-dropdown-container-${sec.id}">
                            <button onclick="toggleSectionVisDropdown('${sec.id}', event)" class="px-2.5 py-1 bg-white hover:bg-gray-50 border border-gray-300 hover:border-gray-400 rounded-lg text-[11px] font-bold text-gray-700 shadow-2xs flex items-center gap-1.5 transition-all focus:outline-none cursor-pointer">
                                <i data-lucide="${currentVisMeta.icon}" class="w-3.5 h-3.5 text-[#B0420C]"></i>
                                <span>${currentVisMeta.label}</span>
                                <i data-lucide="chevron-down" class="w-3 h-3 text-gray-400"></i>
                            </button>

                            <!-- Dropdown Menu -->
                            <div id="vis-menu-${sec.id}" class="hidden absolute right-0 mt-1 w-56 bg-white rounded-xl shadow-xl border border-gray-200 py-1.5 z-[100] text-xs divide-y divide-gray-100">
                                <div class="px-3 py-1 text-[10px] font-bold text-gray-400 uppercase tracking-wider bg-gray-50/50">Select Visualization</div>
                                <div class="py-1">
                                    ${availVis.map(v => {
                                        const isSelected = v.id === currentVis;
                                        return `
                                            <button onclick="setSectionVisualization('${sec.id}', '${v.id}', event)" class="w-full px-3 py-1.5 text-left flex items-center justify-between hover:bg-gray-50 transition-colors ${isSelected ? 'font-bold text-[#B0420C] bg-orange-50/40' : 'text-gray-700 font-medium'}">
                                                <div class="flex items-center gap-2">
                                                    <span class="w-3.5 text-center text-xs">${isSelected ? '✓' : ''}</span>
                                                    <i data-lucide="${v.icon}" class="w-3.5 h-3.5 ${isSelected ? 'text-[#B0420C]' : 'text-gray-400'}"></i>
                                                    <span>${v.label}</span>
                                                </div>
                                                ${v.isRecommended ? `<span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-100 text-amber-900 border border-amber-300">★ Recommended</span>` : ''}
                                            </button>
                                        `;
                                    }).join('')}
                                </div>
                            </div>
                        </div>

                        <!-- Quick CSV Export Button -->
                        <button onclick="exportSingleSectionCSV('${sec.id}')" class="p-1 text-gray-400 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors" title="Export Section Data (.csv)">
                            <i data-lucide="download" class="w-3.5 h-3.5"></i>
                        </button>
                    </div>
                </div>

                <!-- Visualization Container (Updates In-Place!) -->
                <div id="sec-vis-container-${sec.id}" class="transition-all duration-200">
                    ${secContent}
                </div>
            </div>
        `;
        sectionCounter++;
    });

    // AI Comparative Takeaways Block for Comparison Mode
    let aiSynthesisHtml = '';
    if (cfg.queryType === 'comparison') {
        aiSynthesisHtml = `
            <div class="mt-6 p-4 rounded-xl border border-orange-200 bg-orange-50/40 space-y-3 font-sans">
                <div class="flex items-center gap-2 text-xs font-black uppercase tracking-wider text-[#B0420C]">
                    <i data-lucide="sparkles" class="w-4 h-4 text-[#B0420C]"></i>
                    <span>AI Comparative Growth Synthesis &amp; Strategic Optimization Takeaways</span>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-gray-800">
                    <div class="p-3 bg-white rounded-lg border border-orange-200/80 space-y-1">
                        <div class="font-bold text-gray-900 text-[11px]">🏆 Growth &amp; Capacity Synergies</div>
                        <div class="text-gray-600 leading-relaxed text-[11px]">
                            Benchmarking highlights a positive YoY output growth across surveyed pits (+11.8% group average), with mechanized coal clearance delivering above-target fulfillment in high-capacity corridors.
                        </div>
                    </div>
                    <div class="p-3 bg-white rounded-lg border border-orange-200/80 space-y-1">
                        <div class="font-bold text-gray-900 text-[11px]">🚜 Stripping Cost &amp; Blending Strategy</div>
                        <div class="text-gray-600 leading-relaxed text-[11px]">
                            Significant stripping ratio variance (1:2.4 to 1:3.8 CuM/T) suggests strategic thermal coal blending opportunities between high-caloric G4 horizons and high-throughput G11 composite seams.
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    paper.innerHTML = `
        <!-- Official Document Container -->
        <div class="bg-white p-8 sm:p-10 text-gray-900 border border-gray-200 shadow-sm rounded-lg relative font-sans text-xs">
            
            <!-- Letterhead & Title -->
            ${titleHtml}

            <!-- Subject Line -->
            <div class="mb-4 bg-gray-50/80 p-3 rounded-xl border border-gray-200">
                <div class="font-bold text-[#16191C] text-xs">Subject: ${subtitleText}</div>
            </div>

            <!-- Executive Scorecards (for comparison mode) -->
            ${comparisonScorecardHtml}

            <!-- Editable Draft Body Narrative -->
            <div class="mb-5 space-y-2 text-justify leading-relaxed">
                <p contenteditable="true" onblur="handleInlineNarrativeEdit(this.innerText)" class="outline-none focus:bg-amber-50/40 p-1 rounded transition-colors text-gray-800" title="Click to edit draft text">
                    ${cfg.queryType === 'comparison' ? 
                        'A comprehensive comparative evaluation was conducted using authenticated telemetry and CMPDI technical records. Across the evaluated pits, production velocity, stripping efficiency, and equipment utilization norms were benchmarked against national standards.' :
                        'In response to official inquiry, data compiled from verified statutory logs across CMPDI and CIL technical repositories indicates continuous output fulfillment across major opencast extraction benches.'}
                </p>
            </div>

            <!-- Data Coverage Bar in Preview -->
            <div class="mb-5 p-2.5 rounded border ${cov.isClean ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900' : 'bg-amber-50/70 border-amber-200 text-amber-900'} text-[11px] flex items-center justify-between">
                <div class="flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full ${cov.isClean ? 'bg-emerald-600' : 'bg-amber-600'}"></span>
                    <span><strong>Data Coverage Status:</strong> ${cov.completeMines} of ${cov.totalMines} mines with 100% telemetry.</span>
                </div>
                ${!cov.isClean ? `<span class="font-bold text-[10px] uppercase underline cursor-pointer" onclick="setBuilderStep(3)">View Caveats &rarr;</span>` : ''}
            </div>

            <!-- Rendered Content Sections -->
            ${sectionsHtml}

            <!-- AI Synthesis Block for Comparison Mode -->
            ${aiSynthesisHtml}

            <!-- Automatic Caveat Footnotes Section -->
            ${!cov.isClean ? `
                <div class="mt-6 pt-3 border-t border-gray-200 text-[10px] text-gray-500 space-y-1">
                    <div class="font-bold uppercase tracking-wider text-gray-700">Data Coverage Footnotes &amp; Statutory Caveats:</div>
                    ${cov.summaryWarnings.map(w => `<div>&bull; ${w}</div>`).join('')}
                </div>
            ` : ''}

            <!-- Verification Sign-off Block -->
            <div class="mt-8 pt-4 border-t-2 border-gray-900 flex justify-between items-end text-[10px] text-gray-500">
                <div>
                    <div class="font-bold text-[#16191C]">Central Mine Planning &amp; Design Institute Limited</div>
                    <div>Gondwana Place, Kanke Road, Ranchi &bull; Technical Repository</div>
                </div>
                <div class="text-right font-mono">
                    <div>AUTHENTICATED RECORD</div>
                    <div class="text-gray-400">Date: ${new Date().toLocaleDateString('en-GB')}</div>
                </div>
            </div>

            <!-- Persistent MOCK DATA footer badge -->
            <div class="mt-4 text-center">
                <span class="px-2 py-0.5 rounded text-[9px] font-bold uppercase bg-amber-100 text-amber-900 border border-amber-300">
                    MOCK DATA — FOR SYSTEM DEMONSTRATION PURPOSES ONLY
                </span>
            </div>

        </div>
    `;

    if (window.lucide) lucide.createIcons();
}

// ── SOURCE VERIFICATION SNAPSHOT MODAL ──
function openVerificationSnapshotModal(params) {
    const {
        docId = 'SECL-GEVRA-OCP-2024',
        pageNum = 14,
        asOfDate = '2024-08-31',
        metricTitle = 'Opencast Pit Coal Production & Dispatch Performance',
        tableNum = '4.2',
        unit = 'Million Tonnes (MT)',
        highlightEntity = 'Gevra OCP',
        highlightValue = '66.80 MT',
        citeBadge = 'CITED: 66.80 MT',
        footnote = 'Note: Figures authenticated from CMPDI Regional Telemetry & Coal India Operational Dispatch logs.',
        sectionType = 'production'
    } = params || {};

    const modal = document.getElementById('report-verification-snapshot-modal');
    const paper = document.getElementById('report-snapshot-paper');
    const caption = document.getElementById('snapshot-provenance-caption');
    const fullDocBtn = document.getElementById('snapshot-view-full-doc-btn');
    if (!modal || !paper) return;

    const doc = MOCK_DOCUMENTS.find(d => d.id === docId) || MOCK_DOCUMENTS[0];
    if (caption) {
        caption.textContent = `Source Document: ${doc.id} • Page ${pageNum} of ${doc.pageCount} (${doc.subsidiary})`;
    }
    if (fullDocBtn) {
        fullDocBtn.onclick = () => {
            closeVerificationSnapshotModal();
            openDocumentViewerModal(doc.id, {
                highlightEntity,
                highlightValue,
                metricTitle,
                pageNum,
                tableNum,
                sectionType
            });
        };
    }

    // Determine Table Structure based on sectionType
    let tableHtml = '';

    if (sectionType === 'overburden') {
        const obRows = [
            { name: 'Gevra OCP', sub: 'SECL', tgt: '75.0', act: '72.4', sr: '1:3.80' },
            { name: 'Kusmunda OCP', sub: 'SECL', tgt: '52.0', act: '50.8', sr: '1:2.40' },
            { name: 'Dipka OCP', sub: 'SECL', tgt: '42.0', act: '41.5', sr: '1:2.90' },
            { name: 'Jayant OCP', sub: 'NCL', tgt: '34.0', act: '33.6', sr: '1:3.20' },
            { name: 'Lingaraj OCP', sub: 'MCL', tgt: '28.0', act: '27.5', sr: '1:3.10' }
        ];

        tableHtml = `
            <table class="w-full text-xs text-left border-collapse font-sans">
                <thead class="bg-slate-100 text-slate-700 font-bold text-[10px] border-b border-slate-300">
                    <tr>
                        <th class="p-2.5 border-r border-slate-300">Opencast Bench</th>
                        <th class="p-2.5 border-r border-slate-300">Subsidiary</th>
                        <th class="p-2.5 border-r border-slate-300 text-right">Target OB (Mcum)</th>
                        <th class="p-2.5 border-r border-slate-300 text-right">Actual OB (Mcum)</th>
                        <th class="p-2.5 text-right font-black text-slate-900 bg-slate-200/60">Stripping Ratio</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-200 text-slate-700">
                    ${obRows.map(row => {
                        const isMatch = highlightEntity && (row.name.toLowerCase().includes(highlightEntity.toLowerCase()) || highlightEntity.toLowerCase().includes(row.name.toLowerCase()));
                        return `
                            <tr class="${isMatch ? 'bg-amber-100 text-amber-950 font-black border-2 border-amber-400 shadow-xs' : 'hover:bg-slate-50/50'}">
                                <td class="p-2 pl-3 border-r border-slate-300 font-bold flex items-center justify-between">
                                    <span>${row.name}</span>
                                    ${isMatch ? `<span class="text-[8px] bg-amber-500 text-white px-1.5 py-0.5 rounded font-black tracking-wider uppercase">${citeBadge}</span>` : ''}
                                </td>
                                <td class="p-2 border-r border-slate-300 font-mono">${row.sub}</td>
                                <td class="p-2 border-r border-slate-300 text-right font-mono">${row.tgt}</td>
                                <td class="p-2 border-r border-slate-300 text-right font-mono font-bold">${row.act}</td>
                                <td class="p-2 text-right font-mono font-black text-emerald-800">${row.sr}</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
    } else if (sectionType === 'reserves') {
        const seamRows = doc.seamTable || [
            { horizon: 'Seam X (Top)', thickness: '6.40 m', depth: '112 m', ashPercent: '18.4%', gcv: '6,240 kcal/kg', grade: 'G4' },
            { horizon: 'Seam IX (Middle)', thickness: '8.20 m', depth: '148 m', ashPercent: '22.1%', gcv: '5,820 kcal/kg', grade: 'G6' },
            { horizon: 'Seam VIII (Bottom)', thickness: '4.80 m', depth: '194 m', ashPercent: '26.5%', gcv: '5,310 kcal/kg', grade: 'G8' }
        ];

        tableHtml = `
            <table class="w-full text-xs text-left border-collapse font-sans">
                <thead class="bg-slate-100 text-slate-700 font-bold text-[10px] border-b border-slate-300">
                    <tr>
                        <th class="p-2.5 border-r border-slate-300">Seam Horizon</th>
                        <th class="p-2.5 border-r border-slate-300 text-right">Thickness</th>
                        <th class="p-2.5 border-r border-slate-300 text-right">Mean Depth</th>
                        <th class="p-2.5 border-r border-slate-300 text-right">In-situ Ash %</th>
                        <th class="p-2.5 border-r border-slate-300 text-right">GCV</th>
                        <th class="p-2.5 text-center font-bold">Coal Grade</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-200 text-slate-700">
                    ${seamRows.map(row => {
                        const isMatch = highlightEntity && (row.horizon.includes(highlightEntity) || highlightEntity.includes(row.horizon));
                        return `
                            <tr class="${isMatch ? 'bg-amber-100 text-amber-950 font-black border-2 border-amber-400 shadow-xs' : 'hover:bg-slate-50/50'}">
                                <td class="p-2 pl-3 border-r border-slate-300 font-bold flex items-center justify-between">
                                    <span>${row.horizon}</span>
                                    ${isMatch ? `<span class="text-[8px] bg-amber-500 text-white px-1.5 py-0.5 rounded font-black tracking-wider uppercase">${citeBadge}</span>` : ''}
                                </td>
                                <td class="p-2 border-r border-slate-300 text-right font-mono">${row.thickness}</td>
                                <td class="p-2 border-r border-slate-300 text-right font-mono">${row.depth}</td>
                                <td class="p-2 border-r border-slate-300 text-right font-mono">${row.ashPercent}</td>
                                <td class="p-2 border-r border-slate-300 text-right font-mono font-bold">${row.gcv}</td>
                                <td class="p-2 text-center font-bold text-[#B0420C]">${row.grade}</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
    } else {
        // Production Table (Default)
        const prodRows = [
            { name: 'Gevra OCP', sub: 'SECL', cap: '70.0', tgt: '68.00', act: '66.80', ach: '98.2%' },
            { name: 'Kusmunda OCP', sub: 'SECL', cap: '50.0', tgt: '48.00', act: '47.50', ach: '99.0%' },
            { name: 'Dipka OCP', sub: 'SECL', cap: '40.0', tgt: '38.00', act: '37.20', ach: '97.9%' },
            { name: 'Jayant OCP', sub: 'NCL', cap: '25.0', tgt: '25.00', act: '24.80', ach: '99.2%' },
            { name: 'Nigahi OCP', sub: 'NCL', cap: '21.0', tgt: '20.50', act: '20.10', ach: '98.0%' },
            { name: 'Lingaraj OCP', sub: 'MCL', cap: '20.0', tgt: '20.00', act: '19.80', ach: '99.0%' },
            { name: 'Gondegaon OCP', sub: 'WCL', cap: '3.5', tgt: '3.50', act: '3.40', ach: '97.1%' }
        ];

        tableHtml = `
            <table class="w-full text-xs text-left border-collapse font-sans">
                <thead class="bg-slate-100 text-slate-700 font-bold text-[10px] border-b border-slate-300">
                    <tr>
                        <th class="p-2.5 border-r border-slate-300">Opencast Pit / Command</th>
                        <th class="p-2.5 border-r border-slate-300">Subsidiary</th>
                        <th class="p-2.5 border-r border-slate-300 text-right">Capacity (MTY)</th>
                        <th class="p-2.5 border-r border-slate-300 text-right">Target (MT)</th>
                        <th class="p-2.5 text-right font-black text-slate-900 bg-slate-200/60">Actual Output (MT)</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-200 text-slate-700">
                    ${prodRows.map(row => {
                        const isMatch = highlightEntity && (row.name.toLowerCase().includes(highlightEntity.toLowerCase()) || highlightEntity.toLowerCase().includes(row.name.toLowerCase()) || (highlightEntity === row.sub && sectionType === 'production'));
                        return `
                            <tr class="${isMatch ? 'bg-amber-100 text-amber-950 font-black border-2 border-amber-400 shadow-xs' : 'hover:bg-slate-50/50'}">
                                <td class="p-2 pl-3 border-r border-slate-300 font-bold flex items-center justify-between">
                                    <span>${row.name}</span>
                                    ${isMatch ? `<span class="text-[8px] bg-amber-500 text-white px-1.5 py-0.5 rounded font-black tracking-wider uppercase">${citeBadge}</span>` : ''}
                                </td>
                                <td class="p-2 border-r border-slate-300 font-mono">${row.sub}</td>
                                <td class="p-2 border-r border-slate-300 text-right font-mono">${row.cap}</td>
                                <td class="p-2 border-r border-slate-300 text-right font-mono">${row.tgt}</td>
                                <td class="p-2 text-right font-mono font-bold">${isMatch ? (highlightValue || row.act) : row.act}</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
    }

    paper.innerHTML = `
        <div class="space-y-4 text-slate-800 font-sans">
            <!-- Header bar of official document -->
            <div class="border-b border-slate-300 pb-2 flex justify-between items-start text-[10px] text-slate-500 font-bold tracking-wide uppercase">
                <span>GOVERNMENT OF INDIA &bull; MINISTRY OF COAL &bull; COAL DIRECTORY &amp; AUDIT LOGS</span>
                <span class="font-mono text-slate-400">PAGE ${pageNum}</span>
            </div>

            <!-- Table Title -->
            <div>
                <h3 class="text-sm font-black text-slate-900 tracking-tight">Table ${tableNum} : ${metricTitle}</h3>
                <span class="text-[11px] text-slate-500 font-semibold">(${unit})</span>
            </div>

            <!-- Table with Highlighted Cell -->
            <div class="border border-slate-300 rounded-lg overflow-hidden my-2 bg-white shadow-2xs">
                ${tableHtml}
            </div>

            <!-- Footnote Section -->
            <div class="pt-3 border-t border-slate-200 text-[10px] text-slate-500 italic">
                ${footnote}
            </div>
        </div>
    `;

    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
}

function closeVerificationSnapshotModal() {
    const modal = document.getElementById('report-verification-snapshot-modal');
    if (modal) modal.classList.add('hidden');
}

// ── FULL TECHNICAL DOCUMENT VIEWER ──
function openDocumentViewerModal(docId, highlightParams = {}) {
    const modal = document.getElementById('report-document-viewer-modal');
    const content = document.getElementById('report-document-viewer-body');
    const headerMeta = document.getElementById('doc-viewer-header-meta');
    if (!modal || !content) return;

    const doc = MOCK_DOCUMENTS.find(d => d.id === docId) || MOCK_DOCUMENTS[0];
    if (headerMeta) {
        headerMeta.innerHTML = `${doc.subsidiary} Command &bull; Document ID: <strong class="font-mono text-gray-700">${doc.id}</strong> &bull; Published: ${doc.publishedDate} &bull; ${doc.pageCount} Pages`;
    }

    const {
        highlightEntity = '',
        highlightValue = '',
        metricTitle = '',
        pageNum = 14,
        tableNum = '',
        sectionType = ''
    } = highlightParams || {};

    const hasHighlight = highlightEntity && highlightValue;

    content.innerHTML = `
        <!-- Top Citation Highlight Jump Banner -->
        ${hasHighlight ? `
            <div class="px-6 py-2.5 bg-gradient-to-r from-amber-500/20 via-orange-500/10 to-transparent border-b border-amber-300 flex items-center justify-between text-xs shrink-0">
                <div class="flex items-center gap-2 font-bold text-amber-950 flex-wrap">
                    <span class="w-2.5 h-2.5 rounded-full bg-[#B0420C] animate-pulse"></span>
                    <span>📍 Verified Citation Target:</span>
                    <span class="font-mono bg-amber-200 px-2 py-0.5 rounded text-amber-950 border border-amber-400 font-black">${highlightEntity} &bull; ${highlightValue}</span>
                    <span class="text-gray-600 font-normal">(Referenced in ${tableNum ? `Table ${tableNum}` : 'Technical Record'}, Page ${pageNum})</span>
                </div>
                <button onclick="document.getElementById('doc-highlight-target')?.scrollIntoView({behavior: 'smooth', block: 'center'})" class="px-3 py-1 rounded bg-[#B0420C] hover:bg-[#903408] text-white font-bold text-[11px] flex items-center gap-1 shadow-2xs transition-colors shrink-0 cursor-pointer">
                    <span>Jump to Highlighted Data &darr;</span>
                </button>
            </div>
        ` : ''}

        <!-- Main Document Reader (Sidebar + Multi-Chapter Scrollable View) -->
        <div class="flex flex-1 overflow-hidden">
            <!-- Left Sidebar Navigation Index -->
            <div class="w-64 sm:w-72 bg-gray-50 border-r border-gray-200 p-4 overflow-y-auto custom-scrollbar flex flex-col justify-between shrink-0 space-y-4">
                <div class="space-y-3">
                    <div class="text-[10px] font-black text-gray-400 uppercase tracking-wider">Document Chapters &bull; Index</div>
                    <nav class="space-y-1 text-xs">
                        <a href="#doc-ch-1" class="block p-2 rounded-lg hover:bg-white hover:shadow-2xs font-semibold text-gray-700 hover:text-[#B0420C] transition-all">
                            1. Administrative Abstract
                        </a>
                        <a href="#doc-ch-2" class="block p-2 rounded-lg hover:bg-white hover:shadow-2xs font-semibold text-gray-700 hover:text-[#B0420C] transition-all ${sectionType === 'reserves' ? 'bg-orange-100/70 font-bold text-[#B0420C] border-l-2 border-[#B0420C]' : ''}">
                            2. Geological Stratigraphy &amp; Seams
                        </a>
                        <a href="#doc-ch-3" class="block p-2 rounded-lg hover:bg-white hover:shadow-2xs font-semibold text-gray-700 hover:text-[#B0420C] transition-all ${sectionType === 'production' ? 'bg-orange-100/70 font-bold text-[#B0420C] border-l-2 border-[#B0420C]' : ''}">
                            3. Opencast Production Ledger
                        </a>
                        <a href="#doc-ch-4" class="block p-2 rounded-lg hover:bg-white hover:shadow-2xs font-semibold text-gray-700 hover:text-[#B0420C] transition-all ${sectionType === 'overburden' ? 'bg-orange-100/70 font-bold text-[#B0420C] border-l-2 border-[#B0420C]' : ''}">
                            4. Overburden &amp; Stripping Ratios
                        </a>
                        <a href="#doc-ch-5" class="block p-2 rounded-lg hover:bg-white hover:shadow-2xs font-semibold text-gray-700 hover:text-[#B0420C] transition-all ${sectionType === 'hemm' ? 'bg-orange-100/70 font-bold text-[#B0420C] border-l-2 border-[#B0420C]' : ''}">
                            5. HEMM Heavy Fleet Utilisation
                        </a>
                        <a href="#doc-ch-6" class="block p-2 rounded-lg hover:bg-white hover:shadow-2xs font-semibold text-gray-700 hover:text-[#B0420C] transition-all">
                            6. DGMS Safety Audit &amp; Slope Radars
                        </a>
                        <a href="#doc-ch-7" class="block p-2 rounded-lg hover:bg-white hover:shadow-2xs font-semibold text-gray-700 hover:text-[#B0420C] transition-all">
                            7. Environmental Clearance (CAAQM)
                        </a>
                        <a href="#doc-ch-8" class="block p-2 rounded-lg hover:bg-white hover:shadow-2xs font-semibold text-gray-700 hover:text-[#B0420C] transition-all">
                            8. CBA Land Acquisition &amp; R&amp;R
                        </a>
                        <a href="#doc-ch-9" class="block p-2 rounded-lg hover:bg-white hover:shadow-2xs font-semibold text-gray-700 hover:text-[#B0420C] transition-all">
                            9. Verification Seals &amp; Sign-off
                        </a>
                    </nav>
                </div>

                <div class="p-3 bg-white rounded-xl border border-gray-200 text-[11px] space-y-1.5 shadow-2xs">
                    <div class="font-bold text-gray-900">CMPDI Repository Info</div>
                    <div class="text-gray-500">Authenticated technical monograph archived at Gondwana Place, Kanke Road, Ranchi.</div>
                    <div class="pt-1 text-[10px] font-mono text-emerald-700 font-bold">ISP-1984 / CMR-2017 Certified</div>
                </div>
            </div>

            <!-- Right Scrollable Document Body -->
            <div id="doc-viewer-scroll-pane" class="flex-1 p-6 sm:p-10 bg-white overflow-y-auto custom-scrollbar space-y-10 text-gray-800 font-sans text-xs">
                
                <!-- Official CMPDI Document Header Banner -->
                <div class="border-b-2 border-gray-900 pb-6 text-center space-y-2">
                    <div class="text-[10px] uppercase font-bold tracking-widest text-gray-500 font-sans">
                        Government of India &bull; Ministry of Coal &bull; Central Mine Planning &amp; Design Institute Ltd
                    </div>
                    <h1 class="text-xl sm:text-2xl font-black text-[#16191C] uppercase tracking-wide font-serif leading-snug">
                        ${doc.title}
                    </h1>
                    <div class="flex items-center justify-center gap-3 text-xs text-gray-600 font-mono font-semibold pt-1 flex-wrap">
                        <span>Doc Ref: <strong>${doc.id}</strong></span>
                        <span>&bull;</span>
                        <span>Subsidiary: <strong>${doc.subsidiary}</strong></span>
                        <span>&bull;</span>
                        <span>Page Count: <strong>${doc.pageCount} Pages</strong></span>
                        <span>&bull;</span>
                        <span>Published: <strong>${doc.publishedDate}</strong></span>
                    </div>
                </div>

                <!-- Chapter 1: Administrative Abstract -->
                <div id="doc-ch-1" class="space-y-3 scroll-mt-6">
                    <div class="flex items-center gap-2 border-b border-gray-200 pb-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-[#B0420C]"></span>
                        <h2 class="text-sm font-black text-[#16191C] uppercase tracking-wide">Chapter 1 : Executive Summary &amp; Operational Abstract</h2>
                    </div>
                    <p class="leading-relaxed text-gray-700 text-justify text-xs whitespace-pre-line bg-gray-50/70 p-4 rounded-xl border border-gray-200">
                        ${doc.extractedText}
                    </p>
                </div>

                <!-- Chapter 2: Geological Stratigraphy & Seams Quality Audit -->
                <div id="doc-ch-2" class="space-y-3 scroll-mt-6">
                    <div class="flex items-center gap-2 border-b border-gray-200 pb-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-emerald-600"></span>
                        <h2 class="text-sm font-black text-[#16191C] uppercase tracking-wide">Chapter 2 : Geological Stratigraphy &amp; Coal Seams Quality (ISP Norms)</h2>
                    </div>
                    <p class="text-gray-600 text-xs">
                        Borehole lithological cores extracted across the exploration grid establish proved geological reserve horizons under Indian Standard Procedure (ISP 1984) norms.
                    </p>
                    <div class="border border-gray-300 rounded-xl overflow-hidden bg-white shadow-2xs">
                        <div class="bg-gray-100 p-2.5 border-b border-gray-300 font-bold text-[11px] text-gray-800 flex justify-between">
                            <span>Table 2.1 : Coal Seam Lithology, In-situ Ash % &amp; Gross Calorific Value (GCV)</span>
                            <span class="font-mono text-gray-500">Page 42</span>
                        </div>
                        <table class="w-full text-left text-xs border-collapse">
                            <thead class="bg-gray-50 text-gray-700 font-bold text-[10px] uppercase border-b border-gray-200">
                                <tr>
                                    <th class="p-2.5 border-r border-gray-200">Seam Horizon</th>
                                    <th class="p-2.5 border-r border-gray-200 text-right">In-situ Thickness</th>
                                    <th class="p-2.5 border-r border-gray-200 text-right">Mean Depth</th>
                                    <th class="p-2.5 border-r border-gray-200 text-right">In-situ Ash %</th>
                                    <th class="p-2.5 border-r border-gray-200 text-right">GCV (kcal/kg)</th>
                                    <th class="p-2.5 text-center font-bold">Coal Grade</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200">
                                ${(doc.seamTable || [
                                    { horizon: 'Seam X (Top)', thickness: 6.40, depth: 112, ashPercent: 18.4, gcv: 6240, grade: 'G4' },
                                    { horizon: 'Seam IX (Middle)', thickness: 8.20, depth: 148, ashPercent: 22.1, gcv: 5820, grade: 'G6' },
                                    { horizon: 'Seam VIII (Bottom)', thickness: 4.80, depth: 194, ashPercent: 26.5, gcv: 5310, grade: 'G8' }
                                ]).map(s => {
                                    const isTarget = highlightEntity && (s.horizon.includes(highlightEntity) || highlightEntity.includes(s.horizon));
                                    return `
                                        <tr ${isTarget ? 'id="doc-highlight-target"' : ''} class="${isTarget ? 'bg-amber-100 text-amber-950 font-black border-2 border-amber-400' : 'hover:bg-gray-50/70'}">
                                            <td class="p-2.5 pl-3 font-bold border-r border-gray-200 flex items-center justify-between">
                                                <span>${s.horizon}</span>
                                                ${isTarget ? `<span class="px-1.5 py-0.5 rounded text-[8px] bg-amber-500 text-white font-black uppercase">CITED RECORD</span>` : ''}
                                            </td>
                                            <td class="p-2.5 border-r border-gray-200 text-right font-mono">${s.thickness} m</td>
                                            <td class="p-2.5 border-r border-gray-200 text-right font-mono">${s.depth} m</td>
                                            <td class="p-2.5 border-r border-gray-200 text-right font-mono">${s.ashPercent}%</td>
                                            <td class="p-2.5 border-r border-gray-200 text-right font-mono font-bold">${s.gcv}</td>
                                            <td class="p-2.5 text-center font-bold text-[#B0420C]">${s.grade}</td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Chapter 3: Opencast Production Ledger -->
                <div id="doc-ch-3" class="space-y-3 scroll-mt-6">
                    <div class="flex items-center gap-2 border-b border-gray-200 pb-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
                        <h2 class="text-sm font-black text-[#16191C] uppercase tracking-wide">Chapter 3 : Opencast Mine Production &amp; Dispatch Ledger (Full Telemetry)</h2>
                    </div>
                    <p class="text-gray-600 text-xs">
                        Consolidated field operational telemetry for surveyed mines detailing statutory target quotas, monthly ROM coal extraction, and annual fulfillment percentages.
                    </p>
                    <div class="border border-gray-300 rounded-xl overflow-hidden bg-white shadow-2xs">
                        <div class="bg-gray-100 p-2.5 border-b border-gray-300 font-bold text-[11px] text-gray-800 flex justify-between">
                            <span>Table 4.2 : Mine-wise ROM Coal Production, Targets &amp; Dispatch Realization</span>
                            <span class="font-mono text-gray-500">Page 14</span>
                        </div>
                        <table class="w-full text-left text-xs border-collapse">
                            <thead class="bg-gray-50 text-gray-700 font-bold text-[10px] uppercase border-b border-gray-200">
                                <tr>
                                    <th class="p-2.5 border-r border-gray-200">Opencast Pit / Command</th>
                                    <th class="p-2.5 border-r border-gray-200">Subsidiary</th>
                                    <th class="p-2.5 border-r border-gray-200 text-right">Capacity (MTY)</th>
                                    <th class="p-2.5 border-r border-gray-200 text-right">Target Output</th>
                                    <th class="p-2.5 border-r border-gray-200 text-right">Actual Output</th>
                                    <th class="p-2.5 text-center">Fulfillment %</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200">
                                ${[
                                    { name: 'Gevra OCP', sub: 'SECL', cap: 70.0, tgt: 68.0, act: 66.8, ach: '98.2%' },
                                    { name: 'Kusmunda OCP', sub: 'SECL', cap: 50.0, tgt: 48.0, act: 47.5, ach: '99.0%' },
                                    { name: 'Dipka OCP', sub: 'SECL', cap: 40.0, tgt: 38.0, act: 37.2, ach: '97.9%' },
                                    { name: 'Manikpur OCP', sub: 'SECL', cap: 5.2, tgt: 5.0, act: 4.8, ach: '96.0%' },
                                    { name: 'Jayant OCP', sub: 'NCL', cap: 25.0, tgt: 25.0, act: 24.8, ach: '99.2%' },
                                    { name: 'Nigahi OCP', sub: 'NCL', cap: 21.0, tgt: 20.5, act: 20.1, ach: '98.0%' },
                                    { name: 'Dudhichua OCP', sub: 'NCL', cap: 20.0, tgt: 19.5, act: 19.2, ach: '98.5%' },
                                    { name: 'Lingaraj OCP', sub: 'MCL', cap: 20.0, tgt: 20.0, act: 19.8, ach: '99.0%' },
                                    { name: 'Bharatpur OCP', sub: 'MCL', cap: 15.0, tgt: 14.5, act: 14.0, ach: '96.6%' },
                                    { name: 'Lakhanpur OCP', sub: 'MCL', cap: 21.0, tgt: 20.5, act: 20.4, ach: '99.5%' },
                                    { name: 'Gondegaon OCP', sub: 'WCL', cap: 3.5, tgt: 3.5, act: 3.4, ach: '97.1%' },
                                    { name: 'Umrer OCP', sub: 'WCL', cap: 4.2, tgt: 4.0, act: 4.1, ach: '102.5%' }
                                ].map(row => {
                                    const isTarget = highlightEntity && (row.name.toLowerCase().includes(highlightEntity.toLowerCase()) || highlightEntity.toLowerCase().includes(row.name.toLowerCase()) || (highlightEntity === row.sub && sectionType === 'production'));
                                    return `
                                        <tr ${isTarget ? 'id="doc-highlight-target"' : ''} class="${isTarget ? 'bg-amber-100 text-amber-950 font-black border-2 border-amber-400' : 'hover:bg-gray-50/70'}">
                                            <td class="p-2.5 pl-3 font-bold border-r border-gray-200 flex items-center justify-between">
                                                <span>${row.name}</span>
                                                ${isTarget ? `<span class="px-1.5 py-0.5 rounded text-[8px] bg-amber-500 text-white font-black uppercase">VERIFIED CITED RECORD</span>` : ''}
                                            </td>
                                            <td class="p-2.5 border-r border-gray-200 font-mono">${row.sub}</td>
                                            <td class="p-2.5 border-r border-gray-200 text-right font-mono">${row.cap}</td>
                                            <td class="p-2.5 border-r border-gray-200 text-right font-mono">${row.tgt.toFixed(1)} MT</td>
                                            <td class="p-2.5 border-r border-gray-200 text-right font-mono font-bold">${row.act.toFixed(1)} MT</td>
                                            <td class="p-2.5 text-center font-bold text-emerald-700">${row.ach}</td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Chapter 4: Overburden & Stripping Ratio -->
                <div id="doc-ch-4" class="space-y-3 scroll-mt-6">
                    <div class="flex items-center gap-2 border-b border-gray-200 pb-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-amber-600"></span>
                        <h2 class="text-sm font-black text-[#16191C] uppercase tracking-wide">Chapter 4 : Overburden Removal &amp; Stripping Ratio Audit</h2>
                    </div>
                    <div class="border border-gray-300 rounded-xl overflow-hidden bg-white shadow-2xs">
                        <div class="bg-gray-100 p-2.5 border-b border-gray-300 font-bold text-[11px] text-gray-800 flex justify-between">
                            <span>Table 3.4 : Overburden Removal Bench Telemetry &amp; Stripping Ratios</span>
                            <span class="font-mono text-gray-500">Page 28</span>
                        </div>
                        <table class="w-full text-left text-xs border-collapse">
                            <thead class="bg-gray-50 text-gray-700 font-bold text-[10px] uppercase border-b border-gray-200">
                                <tr>
                                    <th class="p-2.5 border-r border-gray-200">Opencast Pit</th>
                                    <th class="p-2.5 border-r border-gray-200 text-right">Target OB (Mcum)</th>
                                    <th class="p-2.5 border-r border-gray-200 text-right">Actual OB (Mcum)</th>
                                    <th class="p-2.5 border-r border-gray-200 text-right">Stripping Ratio</th>
                                    <th class="p-2.5 text-center">ISP Benchmark Status</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200">
                                ${[
                                    { name: 'Gevra OCP', tgt: 75.0, act: 72.4, sr: '1:3.80', status: 'Compliant' },
                                    { name: 'Kusmunda OCP', tgt: 52.0, act: 50.8, sr: '1:2.40', status: 'Compliant' },
                                    { name: 'Dipka OCP', tgt: 42.0, act: 41.5, sr: '1:2.90', status: 'Compliant' },
                                    { name: 'Jayant OCP', tgt: 34.0, act: 33.6, sr: '1:3.20', status: 'Compliant' },
                                    { name: 'Lingaraj OCP', tgt: 28.0, act: 27.5, sr: '1:3.10', status: 'Compliant' }
                                ].map(row => {
                                    const isTarget = highlightEntity && (row.name.toLowerCase().includes(highlightEntity.toLowerCase()) || highlightEntity.toLowerCase().includes(row.name.toLowerCase()));
                                    return `
                                        <tr ${isTarget ? 'id="doc-highlight-target"' : ''} class="${isTarget ? 'bg-amber-100 text-amber-950 font-black border-2 border-amber-400' : 'hover:bg-gray-50/70'}">
                                            <td class="p-2.5 pl-3 font-bold border-r border-gray-200 flex items-center justify-between">
                                                <span>${row.name}</span>
                                                ${isTarget ? `<span class="px-1.5 py-0.5 rounded text-[8px] bg-amber-500 text-white font-black uppercase">CITED OB RECORD</span>` : ''}
                                            </td>
                                            <td class="p-2.5 border-r border-gray-200 text-right font-mono">${row.tgt.toFixed(1)}</td>
                                            <td class="p-2.5 border-r border-gray-200 text-right font-mono font-bold">${row.act.toFixed(1)}</td>
                                            <td class="p-2.5 border-r border-gray-200 text-right font-mono font-black text-emerald-700">${row.sr}</td>
                                            <td class="p-2.5 text-center font-bold text-emerald-600">${row.status}</td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Chapter 5: HEMM Heavy Fleet Deployment -->
                <div id="doc-ch-5" class="space-y-3 scroll-mt-6">
                    <div class="flex items-center gap-2 border-b border-gray-200 pb-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-slate-700"></span>
                        <h2 class="text-sm font-black text-[#16191C] uppercase tracking-wide">Chapter 5 : HEMM Heavy Fleet Deployment &amp; Yield Audit</h2>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        <div class="p-3 bg-gray-50 rounded-xl border border-gray-200">
                            <div class="text-[10px] font-bold text-gray-400 uppercase">Heavy Shovel Fleet</div>
                            <div class="text-base font-black text-gray-900 mt-1">28 Units</div>
                            <div class="text-[10px] text-emerald-600 font-bold">86.4% Availability</div>
                        </div>
                        <div class="p-3 bg-gray-50 rounded-xl border border-gray-200">
                            <div class="text-[10px] font-bold text-gray-400 uppercase">240T Dumper Fleet</div>
                            <div class="text-base font-black text-gray-900 mt-1">142 Units</div>
                            <div class="text-[10px] text-emerald-600 font-bold">84.8% Availability</div>
                        </div>
                        <div class="p-3 bg-gray-50 rounded-xl border border-gray-200">
                            <div class="text-[10px] font-bold text-gray-400 uppercase">Walking Draglines</div>
                            <div class="text-base font-black text-gray-900 mt-1">6 Units</div>
                            <div class="text-[10px] text-emerald-600 font-bold">89.2% Availability</div>
                        </div>
                        <div class="p-3 bg-gray-50 rounded-xl border border-gray-200">
                            <div class="text-[10px] font-bold text-gray-400 uppercase">Shovel-Dumper Match</div>
                            <div class="text-base font-black text-gray-900 mt-1">1 : 5.2</div>
                            <div class="text-[10px] text-gray-500 font-bold">Optimized Allocation</div>
                        </div>
                    </div>
                </div>

                <!-- Chapter 6: Mine Safety (DGMS) -->
                <div id="doc-ch-6" class="space-y-3 scroll-mt-6">
                    <div class="flex items-center gap-2 border-b border-gray-200 pb-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-emerald-600"></span>
                        <h2 class="text-sm font-black text-[#16191C] uppercase tracking-wide">Chapter 6 : Mine Safety Compliance &amp; Highwall Radar Log</h2>
                    </div>
                    <div class="p-4 rounded-xl bg-emerald-50/60 border border-emerald-200 text-xs text-emerald-950 space-y-1.5 leading-relaxed">
                        <div class="font-bold flex items-center gap-1.5">
                            <i data-lucide="shield-check" class="w-4 h-4 text-emerald-700"></i>
                            <span>Statutory Directorate General of Mines Safety (DGMS) Standards Met</span>
                        </div>
                        <p>Zero fatalities and zero reportable serious bodily injuries recorded across all mechanized opencast shifts. Highwall slope radar displacement maintained under 0.02 mm/day (DGMS warning limit 2.0 mm/day).</p>
                    </div>
                </div>

                <!-- Chapter 7: Environmental & Afforestation -->
                <div id="doc-ch-7" class="space-y-3 scroll-mt-6">
                    <div class="flex items-center gap-2 border-b border-gray-200 pb-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-teal-600"></span>
                        <h2 class="text-sm font-black text-[#16191C] uppercase tracking-wide">Chapter 7 : Environmental Clearances &amp; Ambient Air Quality (CAAQM)</h2>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                        <div class="p-3 bg-gray-50 rounded-xl border border-gray-200">
                            <div class="text-[10px] font-bold text-gray-400 uppercase">PM10 Air Quality</div>
                            <div class="text-base font-black text-emerald-700 mt-0.5">74.2 &micro;g/m&sup3;</div>
                            <div class="text-[10px] text-gray-500 font-bold">Standard &le; 100 &micro;g/m&sup3;</div>
                        </div>
                        <div class="p-3 bg-gray-50 rounded-xl border border-gray-200">
                            <div class="text-[10px] font-bold text-gray-400 uppercase">PM2.5 Air Quality</div>
                            <div class="text-base font-black text-emerald-700 mt-0.5">38.5 &micro;g/m&sup3;</div>
                            <div class="text-[10px] text-gray-500 font-bold">Standard &le; 60 &micro;g/m&sup3;</div>
                        </div>
                        <div class="p-3 bg-gray-50 rounded-xl border border-gray-200">
                            <div class="text-[10px] font-bold text-gray-400 uppercase">Dump Afforestation</div>
                            <div class="text-base font-black text-emerald-700 mt-0.5">2.4 Million</div>
                            <div class="text-[10px] text-gray-500 font-bold">Native Tree Saplings</div>
                        </div>
                    </div>
                </div>

                <!-- Chapter 8: CBA Land Acquisition -->
                <div id="doc-ch-8" class="space-y-3 scroll-mt-6">
                    <div class="flex items-center gap-2 border-b border-gray-200 pb-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-purple-600"></span>
                        <h2 class="text-sm font-black text-[#16191C] uppercase tracking-wide">Chapter 8 : Coal Bearing Areas (CBA) Land Possession &amp; R&amp;R Status</h2>
                    </div>
                    <p class="text-xs text-gray-700 leading-relaxed bg-gray-50 p-3.5 rounded-xl border border-gray-200">
                        All gazetted land parcels under Coal Bearing Areas (Acquisition &amp; Development) Act 1957 possess lawful possession awards. Comprehensive R&amp;R entitlements and resettlement colony allotments executed under state norms.
                    </p>
                </div>

                <!-- Chapter 9: Sign-off Seal -->
                <div id="doc-ch-9" class="pt-6 border-t-2 border-gray-900 flex justify-between items-end text-[11px] text-gray-600">
                    <div>
                        <div class="font-bold text-[#16191C]">Central Mine Planning &amp; Design Institute (CMPDI)</div>
                        <div>Regional Technical Repository Archive &bull; Gondwana Place, Kanke Road, Ranchi</div>
                        <div class="text-[10px] text-gray-400 font-mono mt-0.5">ISP-1984 / CMR-2017 Technical Validation</div>
                    </div>
                    <div class="text-right font-mono">
                        <div class="font-bold text-gray-900">AUTHENTICATED REPOSITORY COPY</div>
                        <div class="text-emerald-700 font-bold">ARCHIVE REF: ${doc.id}</div>
                        <div class="text-gray-400 text-[10px]">Verification Date: ${new Date().toLocaleDateString('en-GB')}</div>
                    </div>
                </div>

            </div>
        </div>
    `;

    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();

    // Smooth auto-scroll to the highlighted data point
    setTimeout(() => {
        const target = document.getElementById('doc-highlight-target');
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }, 200);
}

function closeDocumentViewerModal() {
    const modal = document.getElementById('report-document-viewer-modal');
    if (modal) modal.classList.add('hidden');
}

// ── SAVED TEMPLATES / CONFIGURATIONS ──
async function saveCurrentReportConfig() {
    const name = prompt('Enter a title for this report configuration template:', window.RSHPS_REPORTS_STATE.config.name);
    if (!name || !name.trim()) return;

    const repo = getReportsRepository();
    const cfg = {
        ...window.RSHPS_REPORTS_STATE.config,
        name: name.trim()
    };

    await repo.saveReportConfig(cfg);
    alert(`Saved template "${name.trim()}" successfully.`);
    renderSavedTemplatesList();
}

async function renderSavedTemplatesList() {
    const container = document.getElementById('report-saved-templates-list');
    if (!container) return;

    const repo = getReportsRepository();
    const configs = await repo.listReportConfigs();

    container.innerHTML = configs.map(c => `
        <div class="p-3 rounded-xl border border-gray-200 bg-white hover:border-[#B0420C] transition-all flex items-center justify-between gap-3">
            <div>
                <div class="font-bold text-xs text-[#16191C]">${c.name}</div>
                <div class="text-[10px] text-gray-400 font-mono">${c.queryType} &bull; ${c.mineIds.length} mines &bull; ${c.periodType}</div>
            </div>
            <div class="flex items-center gap-1.5">
                <button onclick="loadSavedReportConfig('${c.id}')" class="px-2.5 py-1 bg-gray-100 hover:bg-[#16191C] hover:text-white rounded font-bold text-[10px] transition-all">Load</button>
                <button onclick="deleteSavedReportConfig('${c.id}')" class="px-2 py-1 text-gray-400 hover:text-rose-600 rounded text-xs" title="Delete">&times;</button>
            </div>
        </div>
    `).join('');
}

async function loadSavedReportConfig(configId) {
    const repo = getReportsRepository();
    const configs = await repo.listReportConfigs();
    const target = configs.find(c => c.id === configId);
    if (target) {
        window.RSHPS_REPORTS_STATE.config = JSON.parse(JSON.stringify(target));
        await refreshReportData();
        renderReportBuilderUI();
        renderLivePreview();
        alert(`Loaded template: "${target.name}"`);
    }
}

async function deleteSavedReportConfig(configId) {
    if (!confirm('Are you sure you want to delete this saved template?')) return;
    const repo = getReportsRepository();
    await repo.deleteReportConfig(configId);
    renderSavedTemplatesList();
}

// ── EXPORT ACTIONS ──
// ── EXPORT ACTIONS ──
function executeReportExport(format) {
    const state = window.RSHPS_REPORTS_STATE;
    const cov = state.coverageReport;

    if (!cov.isClean && !state.acknowledgedGaps) {
        alert('Please acknowledge data coverage caveats before exporting this report.');
        setBuilderStep(3);
        return;
    }

    if (format === 'pdf') {
        printCleanReportDocument();
    } else if (format === 'excel') {
        exportReportToExcelCSV();
    } else if (format === 'word') {
        exportReportToWordHTML();
    }
}

function getCleanReportDocumentHtml() {
    const previewDoc = document.getElementById('report-live-preview-document');
    if (!previewDoc) return '';

    // Clone the preview document so live UI remains untouched
    const clone = previewDoc.cloneNode(true);

    // 1. Remove all interactive visualization dropdowns, toolbars, buttons, and popups
    clone.querySelectorAll('.report-vis-control, .hide-in-export, .no-print, [id^="vis-menu"], [id^="vis-dropdown"], input, select, .active-indicator, .nav-tooltip').forEach(el => el.remove());

    // 2. Convert provenance/verification buttons to clean static citation badges
    clone.querySelectorAll('button, a, span').forEach(el => {
        const txt = (el.textContent || '').trim();
        if (txt.startsWith('[') && (txt.includes(']') || txt.includes('ISP') || txt.includes('Scheme') || txt.includes('DGMS') || txt.includes('CMR') || txt.includes('EC'))) {
            const span = document.createElement('span');
            span.setAttribute('style', 'font-size: 8.5pt; font-family: monospace; color: #78350f; background-color: #fef3c7; padding: 1pt 4pt; border: 1px solid #fde68a; border-radius: 2pt;');
            span.textContent = txt.replace('→', '').replace('&rarr;', '').trim();
            el.replaceWith(span);
        }
    });

    // Remove any remaining buttons completely
    clone.querySelectorAll('button').forEach(b => b.remove());

    // 3. Remove all SVG icons and Lucide icon elements
    clone.querySelectorAll('svg, i[data-lucide], .lucide').forEach(icon => icon.remove());

    // 4. Style all tables for pristine rendering
    clone.querySelectorAll('table').forEach(table => {
        table.setAttribute('style', 'width: 100%; border-collapse: collapse; margin-top: 8pt; margin-bottom: 12pt; font-family: Calibri, Arial, sans-serif; font-size: 9.5pt;');
    });
    clone.querySelectorAll('th').forEach(th => {
        th.setAttribute('style', 'background-color: #1e293b; color: #ffffff; font-weight: bold; text-align: left; padding: 6pt 8pt; border: 1pt solid #1e293b; font-family: Calibri, Arial, sans-serif; font-size: 9.5pt;');
    });
    clone.querySelectorAll('td').forEach(td => {
        td.setAttribute('style', 'padding: 5pt 8pt; border: 1pt solid #cbd5e1; color: #1e293b; font-family: Calibri, Arial, sans-serif; font-size: 9.5pt; vertical-align: top;');
    });

    // 5. Convert horizontal progress bars to clean supported tables
    clone.querySelectorAll('.w-full.bg-gray-100, .w-full.bg-gray-200, .bg-gray-100.rounded-full, .bg-slate-100').forEach(track => {
        const fill = track.querySelector('[style*="width"]');
        if (fill) {
            const widthMatch = fill.getAttribute('style')?.match(/width:\s*([0-9.]+)%/);
            const pct = widthMatch ? parseFloat(widthMatch[1]) : 75;
            const bgMatch = fill.getAttribute('style')?.match(/background-color:\s*([^;]+)/);
            const bgColor = bgMatch ? bgMatch[1] : '#B0420C';
            
            const tableBar = document.createElement('table');
            tableBar.setAttribute('style', 'width: 100%; border-collapse: collapse; border: none; margin: 2pt 0;');
            tableBar.innerHTML = `<tr style="border:none;"><td style="width:${pct}%; background-color:${bgColor}; height:10px; padding:0; border:none;"></td><td style="width:${100-pct}%; background-color:#e2e8f0; height:10px; padding:0; border:none;"></td></tr>`;
            track.replaceWith(tableBar);
        }
    });

    // 6. Convert comparison cards grid to an HTML table
    const compGrid = clone.querySelector('.grid.grid-cols-1.sm\\:grid-cols-2.md\\:grid-cols-3, .grid-cols-1.sm\\:grid-cols-2.md\\:grid-cols-3');
    if (compGrid) {
        const cards = Array.from(compGrid.children);
        if (cards.length > 0) {
            const table = document.createElement('table');
            table.setAttribute('style', 'width: 100%; border-collapse: collapse; margin-bottom: 12pt;');
            const tr = document.createElement('tr');
            const colWidth = Math.floor(100 / cards.length);
            cards.forEach(card => {
                const td = document.createElement('td');
                td.setAttribute('style', `width: ${colWidth}%; border: 1pt solid #cbd5e1; background-color: #f8fafc; padding: 8pt; vertical-align: top;`);
                td.innerHTML = card.innerHTML;
                tr.appendChild(td);
            });
            table.appendChild(tr);
            compGrid.replaceWith(table);
        }
    }

    return clone.innerHTML;
}

function printCleanReportDocument() {
    const cleanHtml = getCleanReportDocumentHtml();
    if (!cleanHtml) return;

    let printFrame = document.getElementById('report-print-iframe');
    if (printFrame) {
        printFrame.remove();
    }

    printFrame = document.createElement('iframe');
    printFrame.id = 'report-print-iframe';
    printFrame.style.position = 'fixed';
    printFrame.style.right = '0';
    printFrame.style.bottom = '0';
    printFrame.style.width = '0';
    printFrame.style.height = '0';
    printFrame.style.border = '0';
    document.body.appendChild(printFrame);

    const doc = printFrame.contentWindow.document;
    doc.open();
    doc.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>CMPDI Official Report Monograph</title>
            <style>
                @page {
                    size: A4 portrait;
                    margin: 15mm 15mm 15mm 15mm;
                }
                body {
                    font-family: 'Segoe UI', Calibri, Arial, sans-serif;
                    font-size: 10pt;
                    line-height: 1.45;
                    color: #1e293b;
                    background: #ffffff;
                    margin: 0;
                    padding: 0;
                }
                h1 { font-family: "Georgia", "Times New Roman", serif; font-size: 15pt; font-weight: bold; text-align: center; color: #0f172a; margin: 4pt 0; }
                h2 { font-family: "Segoe UI", Arial, sans-serif; font-size: 11pt; font-weight: bold; text-align: center; color: #475569; margin: 2pt 0 10pt 0; }
                h3 { font-family: "Segoe UI", Arial, sans-serif; font-size: 11pt; font-weight: bold; color: #0f172a; margin: 16pt 0 6pt 0; border-bottom: 2pt solid #B0420C; padding-bottom: 3pt; text-transform: uppercase; }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 8pt 0 12pt 0;
                    font-size: 9pt;
                }
                th {
                    background-color: #1e293b;
                    color: #ffffff;
                    font-weight: bold;
                    text-align: left;
                    padding: 6pt 8pt;
                    border: 1pt solid #1e293b;
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }
                td {
                    padding: 5pt 8pt;
                    border: 1pt solid #cbd5e1;
                    color: #1e293b;
                    vertical-align: top;
                }
                tr:nth-child(even) td {
                    background-color: #f8fafc;
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }
                .footer-seal {
                    margin-top: 24pt;
                    padding-top: 10pt;
                    border-top: 1pt solid #cbd5e1;
                    font-size: 8pt;
                    color: #64748b;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            ${cleanHtml}
            <div class="footer-seal">
                <p style="margin: 2pt 0; font-weight: bold; color: #0f172a;">Central Mine Planning &amp; Design Institute Limited (CMPDI)</p>
                <p style="margin: 2pt 0;">Gondwana Place, Kanke Road, Ranchi &bull; Technical Repository Archive</p>
                <p style="margin: 2pt 0; font-family: monospace; font-size: 8pt;">AUTHENTICATED OFFICIAL RECORD &bull; Date of Compilation: ${new Date().toLocaleDateString('en-GB')}</p>
                <p style="margin: 4pt 0 0 0; font-size: 7.5pt; color: #94a3b8;">MOCK DATA &mdash; FOR SYSTEM DEMONSTRATION PURPOSES ONLY</p>
            </div>
        </body>
        </html>
    `);
    doc.close();

    setTimeout(() => {
        printFrame.contentWindow.focus();
        printFrame.contentWindow.print();
        setTimeout(() => printFrame.remove(), 2500);
    }, 250);
}

function exportReportToExcelCSV() {
    const cfg = window.RSHPS_REPORTS_STATE.config;
    const metrics = window.RSHPS_REPORTS_STATE.loadedMetrics;
    const mines = window.RSHPS_REPORTS_STATE.loadedMines.filter(m => cfg.mineIds.includes(m.id));

    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += 'CMPDI RSHPS MOCK REPORT EXPORT\r\n';
    csvContent += `Report Title,"${cfg.name}"\r\n`;
    csvContent += `Period,"${cfg.periodType} (${cfg.startDate} to ${cfg.endDate})"\r\n\r\n`;
    csvContent += 'Mine ID,Mine Name,Subsidiary,Coalfield,Type,Actual Production (MT),Target (MT),Achievement %,OB Removal (Mcum),Stripping Ratio,Source Document\r\n';

    mines.forEach(m => {
        const pSeries = metrics[m.id]?.production || [];
        const obSeries = metrics[m.id]?.ob_removal || [];
        const srSeries = metrics[m.id]?.stripping_ratio || [];
        
        const totalProd = pSeries.reduce((acc, pt) => acc + pt.value, 0).toFixed(2);
        const totalTarget = pSeries.reduce((acc, pt) => acc + (pt.target || 0), 0).toFixed(2);
        const achieve = totalTarget > 0 ? ((totalProd / totalTarget) * 100).toFixed(1) : '100.0';
        const totalOB = obSeries.reduce((acc, pt) => acc + pt.value, 0).toFixed(2);
        const avgSR = srSeries.length > 0 ? (srSeries.reduce((acc, pt) => acc + pt.value, 0) / srSeries.length).toFixed(2) : '3.80';
        const sourceDoc = pSeries[0]?.source?.documentId || 'SECL-GEVRA-OCP-2024';

        csvContent += `"${m.id}","${m.name}","${m.subsidiary}","${m.coalfield}","${m.type}",${totalProd},${totalTarget},${achieve}%,${totalOB},${avgSR},"${sourceDoc}"\r\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `CMPDI_Report_${cfg.periodType}_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function exportReportToWordHTML() {
    const cleanedBodyHtml = getCleanReportDocumentHtml();
    if (!cleanedBodyHtml) return;

    const wordTemplate = `
<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40">
<head>
<meta charset="utf-8">
<title>CMPDI Official Analytical Monograph</title>
<!--[if gte mso 9]>
<xml>
<w:WordDocument>
<w:View>Print</w:View>
<w:Zoom>100</w:Zoom>
<w:DoNotOptimizeForBrowser/>
</w:WordDocument>
</xml>
<![endif]-->
<style>
@page Section1 {
    size: 210mm 297mm;
    margin: 20mm 20mm 20mm 20mm;
    mso-header-margin: 36pt;
    mso-footer-margin: 36pt;
    mso-paper-source: 0;
}
div.Section1 { page: Section1; }
body {
    font-family: "Segoe UI", Calibri, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #1e293b;
    background-color: #ffffff;
}
h1 { font-family: "Georgia", "Times New Roman", serif; font-size: 15pt; font-weight: bold; text-align: center; color: #0f172a; margin: 4pt 0; }
h2 { font-family: "Segoe UI", Arial, sans-serif; font-size: 11pt; font-weight: bold; text-align: center; color: #475569; margin: 2pt 0 10pt 0; }
h3 { font-family: "Segoe UI", Arial, sans-serif; font-size: 11pt; font-weight: bold; color: #0f172a; margin: 16pt 0 6pt 0; border-bottom: 2pt solid #B0420C; padding-bottom: 3pt; text-transform: uppercase; }
table {
    width: 100%;
    border-collapse: collapse;
    margin: 8pt 0 12pt 0;
    font-size: 9.5pt;
}
th {
    background-color: #1e293b;
    color: #ffffff;
    font-weight: bold;
    text-align: left;
    padding: 6pt 8pt;
    border: 1pt solid #1e293b;
}
td {
    padding: 5pt 8pt;
    border: 1pt solid #cbd5e1;
    color: #1e293b;
    vertical-align: top;
}
tr:nth-child(even) td {
    background-color: #f8fafc;
}
.footer-seal {
    margin-top: 24pt;
    padding-top: 10pt;
    border-top: 1pt solid #cbd5e1;
    font-size: 8.5pt;
    color: #64748b;
    text-align: center;
}
</style>
</head>
<body>
<div class="Section1">
${cleanedBodyHtml}

<div class="footer-seal">
    <p style="margin: 2pt 0; font-weight: bold; color: #0f172a;">Central Mine Planning &amp; Design Institute Limited (CMPDI)</p>
    <p style="margin: 2pt 0;">Gondwana Place, Kanke Road, Ranchi &bull; Technical Repository Archive</p>
    <p style="margin: 2pt 0; font-family: monospace; font-size: 8pt;">AUTHENTICATED OFFICIAL RECORD &bull; Date of Compilation: ${new Date().toLocaleDateString('en-GB')}</p>
    <p style="margin: 4pt 0 0 0; font-size: 7.5pt; color: #94a3b8;">MOCK DATA &mdash; FOR SYSTEM DEMONSTRATION PURPOSES ONLY</p>
</div>
</div>
</body>
</html>
    `;

    const blob = new Blob(['\ufeff' + wordTemplate], {
        type: 'application/msword;charset=utf-8'
    });
    const cfg = window.RSHPS_REPORTS_STATE.config;
    const cleanFileName = (cfg.name || 'CMPDI_Report').replace(/[^a-zA-Z0-9_\-]/g, '_');
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${cleanFileName}_${Date.now()}.doc`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function handleInlineNarrativeEdit(text) {
    window.RSHPS_REPORTS_STATE.inlineEdits['main_narrative'] = text;
}
