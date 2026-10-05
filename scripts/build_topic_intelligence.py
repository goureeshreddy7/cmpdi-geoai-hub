import os
import json

ORIGINAL_HTML_PATH = 'c:/Users/LENOVO/Downloads/final_cmpdi/cmpdi-geoai-hub-main/original_render_index.html'

with open(ORIGINAL_HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# Build the complete new page-insights section with CMPDI brand visual language + Clickable Documents Explorer Modal
new_insights_html = '''
                    <!-- ================= INSIGHTS VIEW (ADMIN) ================= -->
                    <div id="page-insights" class="page-view flex-col space-y-6">
                        <!-- Main Grid: Clean Radial Word Map + Detail Studio -->
                        <div class="grid grid-cols-1 xl:grid-cols-12 gap-6">
                            
                            <!-- LEFT/CENTER CARD: Interactive Radial Word Map -->
                            <div class="xl:col-span-8 bg-white rounded-[2rem] border border-gray-200/80 card-elevate p-6 sm:p-7 flex flex-col justify-between">
                                
                                <!-- Card Header & Filters -->
                                <div>
                                    <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
                                        <div>
                                            <div class="flex items-center gap-2.5">
                                                <h3 class="font-extrabold text-[#0f172a] text-base sm:text-lg tracking-tight">Interactive Word Map</h3>
                                                <span class="px-2 py-0.5 bg-emerald-50 text-emerald-700 font-bold text-[9px] uppercase tracking-wider rounded border border-emerald-200">Semantic Graph</span>
                                                <span class="text-[10px] text-gray-400 font-semibold">• 1,284 Indexed Reports</span>
                                            </div>
                                            <p class="text-xs font-medium text-gray-500 mt-0.5">Explore high-frequency mining terms and discover relationships across indexed reports.</p>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <span class="text-[11px] font-bold text-gray-600 bg-gray-50 px-3 py-1.5 rounded-xl border border-gray-200/70 flex items-center gap-1.5">
                                                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Live Model
                                            </span>
                                        </div>
                                    </div>

                                    <!-- Category Filter Bar (Clean Understated Style matching CMPDI palette) -->
                                    <div class="flex items-center gap-1.5 sm:gap-2 overflow-x-auto custom-scrollbar pb-2 pt-1 mb-2">
                                        <button onclick="filterTopicCategory('all')" id="topic-filter-all" class="topic-cat-btn active-cat px-3 py-1.5 rounded-lg text-xs font-extrabold transition-all bg-[#0f172a] text-white shadow-2xs">All Documents</button>
                                        <button onclick="filterTopicCategory('production')" id="topic-filter-production" class="topic-cat-btn px-3 py-1.5 rounded-lg text-xs font-semibold transition-all bg-gray-50 hover:bg-emerald-50 text-gray-600 hover:text-emerald-700 border border-gray-200/70 flex items-center gap-1.5">
                                            <span class="w-1.5 h-1.5 rounded-full bg-[#16a34a]"></span> Production
                                        </button>
                                        <button onclick="filterTopicCategory('geological')" id="topic-filter-geological" class="topic-cat-btn px-3 py-1.5 rounded-lg text-xs font-semibold transition-all bg-gray-50 hover:bg-sky-50 text-gray-600 hover:text-sky-700 border border-gray-200/70 flex items-center gap-1.5">
                                            <span class="w-1.5 h-1.5 rounded-full bg-[#0284c7]"></span> Geological
                                        </button>
                                        <button onclick="filterTopicCategory('environmental')" id="topic-filter-environmental" class="topic-cat-btn px-3 py-1.5 rounded-lg text-xs font-semibold transition-all bg-gray-50 hover:bg-amber-50 text-gray-600 hover:text-amber-700 border border-gray-200/70 flex items-center gap-1.5">
                                            <span class="w-1.5 h-1.5 rounded-full bg-[#ea580c]"></span> Environmental
                                        </button>
                                        <button onclick="filterTopicCategory('safety')" id="topic-filter-safety" class="topic-cat-btn px-3 py-1.5 rounded-lg text-xs font-semibold transition-all bg-gray-50 hover:bg-rose-50 text-gray-600 hover:text-rose-700 border border-gray-200/70 flex items-center gap-1.5">
                                            <span class="w-1.5 h-1.5 rounded-full bg-[#e11d48]"></span> Safety &amp; Operations
                                        </button>
                                        <button onclick="filterTopicCategory('exploration')" id="topic-filter-exploration" class="topic-cat-btn px-3 py-1.5 rounded-lg text-xs font-semibold transition-all bg-gray-50 hover:bg-cyan-50 text-gray-600 hover:text-cyan-700 border border-gray-200/70 flex items-center gap-1.5">
                                            <span class="w-1.5 h-1.5 rounded-full bg-[#0369a1]"></span> Exploration
                                        </button>
                                    </div>
                                </div>

                                <!-- Radial Typographic Canvas Container (Subtle cool off-white tint with central depth) -->
                                <div id="radial-cloud-container" style="background: radial-gradient(circle at 50% 50%, #ffffff 0%, #f8fafc 75%, #f1f5f9 100%);" class="relative w-full h-[450px] sm:h-[490px] rounded-2xl border border-gray-200/80 overflow-hidden flex items-center justify-center select-none my-2">
                                    
                                    <!-- Ultra-subtle background guide lines -->
                                    <svg class="absolute inset-0 w-full h-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
                                        <!-- 2 faint reference rings -->
                                        <circle cx="50%" cy="50%" r="115" fill="none" stroke="#cbd5e1" stroke-width="0.75" stroke-dasharray="2,6" opacity="0.45" />
                                        <circle cx="50%" cy="50%" r="200" fill="none" stroke="#cbd5e1" stroke-width="0.75" stroke-dasharray="2,6" opacity="0.30" />
                                        
                                        <!-- Dynamic Selective Connector Lines (Colored with topic accent at subtle opacity) -->
                                        <g id="radial-connector-lines"></g>
                                    </svg>

                                    <!-- Radial Word Nodes rendered dynamically as pure typography with category color -->
                                    <div id="radial-word-nodes-layer" class="absolute inset-0 w-full h-full pointer-events-auto"></div>

                                    <!-- Floating Tooltip (Clean Minimalist Design) -->
                                    <div id="radial-topic-tooltip" class="absolute z-30 pointer-events-none opacity-0 transition-opacity duration-150 bg-[#0f172a] text-white px-3.5 py-2.5 rounded-xl shadow-lg border border-slate-700 text-xs transform -translate-x-1/2 -translate-y-full mb-2 min-w-[160px]">
                                        <div class="flex items-center justify-between border-b border-slate-700 pb-1 mb-1.5">
                                            <h5 id="r-tooltip-title" class="font-bold text-white text-xs">Topic</h5>
                                            <span id="r-tooltip-cat" class="text-[9px] uppercase tracking-wider text-slate-400 font-bold">Category</span>
                                        </div>
                                        <div class="space-y-0.5 text-[11px] font-medium text-slate-300">
                                            <div class="flex justify-between"><span>Occurrences:</span> <strong id="r-tooltip-occ" class="text-white font-bold">486</strong></div>
                                            <div class="flex justify-between"><span>Relevance:</span> <strong id="r-tooltip-rel" class="text-emerald-400 font-bold">94.2%</strong></div>
                                            <div class="flex justify-between"><span>Documents:</span> <strong id="r-tooltip-docs" class="text-white font-bold">173</strong></div>
                                        </div>
                                    </div>

                                </div>

                                <!-- Card Footer & Category Color Legend -->
                                <div class="pt-3 border-t border-gray-100 flex flex-wrap items-center justify-between gap-3 text-xs text-gray-500 font-medium">
                                    <div class="flex items-center gap-4 flex-wrap text-[11px]">
                                        <span class="font-bold text-gray-700">Categories:</span>
                                        <span class="flex items-center gap-1.5 font-semibold text-[#15803d]"><span class="w-2 h-2 rounded-full bg-[#16a34a]"></span> Production</span>
                                        <span class="flex items-center gap-1.5 font-semibold text-[#0369a1]"><span class="w-2 h-2 rounded-full bg-[#0284c7]"></span> Geological</span>
                                        <span class="flex items-center gap-1.5 font-semibold text-[#c2410c]"><span class="w-2 h-2 rounded-full bg-[#ea580c]"></span> Environmental</span>
                                        <span class="flex items-center gap-1.5 font-semibold text-[#be123c]"><span class="w-2 h-2 rounded-full bg-[#e11d48]"></span> Safety &amp; Ops</span>
                                    </div>
                                    <div class="text-[10px] text-gray-400 font-bold tracking-wider uppercase">
                                        Size → Occurrence &bull; Color → Category &bull; Lines → Semantic Relation
                                    </div>
                                </div>

                            </div>


                            <!-- RIGHT CARD: Topic Detail Panel -->
                            <div class="xl:col-span-4 bg-white rounded-[2rem] border border-gray-200/80 card-elevate p-6 sm:p-7 flex flex-col justify-between" id="topic-detail-card">
                                
                                <div class="space-y-4 sm:space-y-5">
                                    <!-- Detail Header -->
                                    <div class="border-b border-gray-100 pb-3.5">
                                        <div class="flex items-center justify-between mb-1.5">
                                            <span class="text-[10px] font-extrabold uppercase tracking-wider text-gray-400">TOPIC DETAIL</span>
                                            <span id="detail-topic-badge" class="px-2.5 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded font-bold text-[10px] uppercase">Mining Operations</span>
                                        </div>
                                        <div class="flex items-center justify-between">
                                            <h3 id="detail-topic-name" class="text-xl sm:text-2xl font-black text-[#0f172a] tracking-tight">Overburden</h3>
                                            <button onclick="focusTopicInCloud(currentSelectedTopicKey)" title="Focus in Word Map" class="w-7 h-7 rounded-lg bg-gray-50 hover:bg-gray-100 flex items-center justify-center text-gray-500 hover:text-[#0f172a] transition-all border border-gray-200/60">
                                                <i data-lucide="crosshair" class="w-3.5 h-3.5"></i>
                                            </button>
                                        </div>
                                    </div>

                                    <!-- Key Metrics Grid with Clickable Documents Window Trigger -->
                                    <div class="grid grid-cols-2 gap-2.5">
                                        <div class="p-3 rounded-xl bg-gray-50/80 border border-gray-200/60">
                                            <div class="text-[10px] font-bold uppercase text-gray-400 tracking-wider">Occurrences</div>
                                            <div id="detail-topic-occ" class="text-lg font-black text-[#0f172a] mt-0.5">486</div>
                                        </div>
                                        
                                        <!-- CLICKABLE DOCUMENTS CARD (Intentionally distinct interactive entry point with pale lime treatment) -->
                                        <div onclick="openTopicDocumentsModal(currentSelectedTopicKey)" 
                                             tabindex="0"
                                             role="button"
                                             aria-label="View related documents"
                                             onkeydown="if(event.key==='Enter'||event.key===' ') { event.preventDefault(); openTopicDocumentsModal(currentSelectedTopicKey); }"
                                             class="p-3 rounded-xl bg-[#f0fdf4]/80 hover:bg-[#ecfdf5] border border-emerald-200/90 hover:border-emerald-400 hover:shadow-xs cursor-pointer transition-all duration-150 group relative focus:outline-none focus:ring-2 focus:ring-emerald-500/30 flex flex-col justify-between">
                                            <div>
                                                <div class="flex items-center justify-between">
                                                    <span class="text-[10px] font-bold uppercase text-emerald-800 tracking-wider flex items-center gap-1.5">
                                                        <i data-lucide="file-text" class="w-3 h-3 text-emerald-600"></i> DOCUMENTS
                                                    </span>
                                                    <i data-lucide="arrow-right" class="w-3.5 h-3.5 text-emerald-600 group-hover:text-emerald-800 group-hover:translate-x-1 transition-transform"></i>
                                                </div>
                                                <div id="detail-topic-docs" class="text-lg font-black text-[#0f172a] mt-0.5 group-hover:text-emerald-950 transition-colors">173</div>
                                            </div>
                                            <div class="border-t border-emerald-100/90 pt-1.5 mt-1.5 flex items-center justify-between">
                                                <span id="detail-topic-docs-subtitle" class="text-[10px] font-extrabold text-emerald-700 group-hover:text-emerald-800 flex items-center gap-1 transition-colors">
                                                    View related documents &rarr;
                                                </span>
                                            </div>
                                        </div>

                                        <div class="p-3 rounded-xl bg-gray-50/80 border border-gray-200/60">
                                            <div class="text-[10px] font-bold uppercase text-gray-400 tracking-wider">Relevance</div>
                                            <div id="detail-topic-rel" class="text-lg font-black text-emerald-600 mt-0.5">94.2%</div>
                                        </div>
                                        <div class="p-3 rounded-xl bg-gray-50/80 border border-gray-200/60">
                                            <div class="text-[10px] font-bold uppercase text-gray-400 tracking-wider">Category</div>
                                            <div id="detail-topic-cat" class="text-xs font-black text-[#0f172a] mt-1 truncate">Mining Operations</div>
                                        </div>
                                    </div>

                                    <!-- Trend of Occurrence Chart -->
                                    <div>
                                        <div class="flex items-center justify-between mb-1.5">
                                            <h4 class="text-xs font-bold uppercase tracking-wider text-gray-700">Trend of Occurrence</h4>
                                            <!-- Time Range Filters -->
                                            <div class="flex items-center gap-1 bg-gray-100 p-0.5 rounded-lg text-[10px] font-bold text-gray-500">
                                                <button onclick="setTrendTimeRange('1Y')" id="trend-range-1Y" class="trend-btn px-2 py-0.5 rounded hover:text-[#0f172a]">1Y</button>
                                                <button onclick="setTrendTimeRange('3Y')" id="trend-range-3Y" class="trend-btn active-range px-2 py-0.5 rounded bg-white text-[#0f172a] shadow-2xs font-extrabold">3Y</button>
                                                <button onclick="setTrendTimeRange('5Y')" id="trend-range-5Y" class="trend-btn px-2 py-0.5 rounded hover:text-[#0f172a]">5Y</button>
                                                <button onclick="setTrendTimeRange('ALL')" id="trend-range-ALL" class="trend-btn px-2 py-0.5 rounded hover:text-[#0f172a]">ALL</button>
                                            </div>
                                        </div>
                                        <div class="h-28 w-full bg-white rounded-xl p-2 border border-gray-200/70 relative">
                                            <canvas id="topicTrendCanvas" class="w-full h-full"></canvas>
                                        </div>
                                    </div>

                                    <!-- Related Topics (Clickable chips with category indicators) -->
                                    <div>
                                        <h4 class="text-xs font-bold uppercase tracking-wider text-gray-700 mb-1.5">Related Topics</h4>
                                        <div id="detail-related-chips" class="flex flex-wrap gap-1.5">
                                            <!-- Related chips rendered dynamically -->
                                        </div>
                                    </div>

                                    <!-- AI Insight -->
                                    <div class="p-3 bg-emerald-50/40 rounded-xl border border-emerald-200/60">
                                        <div class="flex items-center gap-1.5 text-[10px] font-bold uppercase text-emerald-800 tracking-wider mb-1">
                                            <i data-lucide="sparkles" class="w-3.5 h-3.5 text-emerald-600"></i> AI Insight
                                        </div>
                                        <p id="detail-ai-insight" class="text-xs font-medium text-gray-800 leading-relaxed">
                                            "Overburden is frequently associated with stripping ratio, excavation and production planning across the analyzed reports."
                                        </p>
                                    </div>

                                    <!-- Document Context -->
                                    <div class="p-3 bg-gray-50/60 rounded-xl border border-gray-200/60 space-y-1.5 text-xs">
                                        <div class="flex justify-between items-center">
                                            <span class="text-gray-500 font-medium">Most Common In</span>
                                            <strong id="detail-context-common" class="text-[#0f172a] font-bold">Production Reports</strong>
                                        </div>
                                        <div class="flex justify-between items-center pt-1 border-t border-gray-200/50">
                                            <span class="text-gray-500 font-medium">Top Source</span>
                                            <strong id="detail-context-source" class="text-[#0f172a] font-bold">Mine Performance Reports</strong>
                                        </div>
                                    </div>
                                </div>
                            </div>

                        </div>

                        <!-- Enterprise Cluster Breakdown Row Below -->
                        <div class="bg-white rounded-[2rem] p-6 sm:p-7 border border-gray-200/80 card-elevate">
                            <div class="flex items-center justify-between mb-4">
                                <div>
                                    <h3 class="font-extrabold text-[#0f172a] text-base tracking-tight">Enterprise Cluster Breakdown</h3>
                                    <p class="text-xs font-medium text-gray-500">Semantic density clusters analyzed across 1,284 technical repositories</p>
                                </div>
                                <span class="w-8 h-8 rounded-full bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold text-xs"><i data-lucide="layers" class="w-4 h-4"></i></span>
                            </div>
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div onclick="selectTopicNode('Extraction')" class="p-4 rounded-xl bg-gray-50/70 hover:bg-white hover:shadow-sm transition-all cursor-pointer border border-gray-200/70 group">
                                    <div class="flex justify-between items-center mb-1"><span class="font-bold text-xs text-[#0f172a] group-hover:text-emerald-700 transition-colors">Extraction &amp; Output</span><span class="text-[11px] font-extrabold text-emerald-600">42%</span></div>
                                    <p class="text-[11px] text-gray-500 font-medium">High correlation with SECL &amp; MCL production logs.</p>
                                </div>
                                <div onclick="selectTopicNode('Reclamation')" class="p-4 rounded-xl bg-gray-50/70 hover:bg-white hover:shadow-sm transition-all cursor-pointer border border-gray-200/70 group">
                                    <div class="flex justify-between items-center mb-1"><span class="font-bold text-xs text-[#0f172a] group-hover:text-amber-700 transition-colors">Environmental &amp; Clearances</span><span class="text-[11px] font-extrabold text-amber-600">28%</span></div>
                                    <p class="text-[11px] text-gray-500 font-medium">Environmental impact and NBWL forest clearance audits.</p>
                                </div>
                                <div onclick="selectTopicNode('Geological Reserve')" class="p-4 rounded-xl bg-gray-50/70 hover:bg-white hover:shadow-sm transition-all cursor-pointer border border-gray-200/70 group">
                                    <div class="flex justify-between items-center mb-1"><span class="font-bold text-xs text-[#0f172a] group-hover:text-sky-700 transition-colors">Geological Reserves &amp; Logs</span><span class="text-[11px] font-extrabold text-sky-600">30%</span></div>
                                    <p class="text-[11px] text-gray-500 font-medium">Verified core seam depth &amp; borehole lithology metrics.</p>
                                </div>
                            </div>
                        </div>
                    </div>
'''

# Find insights block in original_render_index.html and replace it
insights_start = html.find('<!-- ================= INSIGHTS VIEW (ADMIN) ================= -->')
if insights_start == -1:
    insights_start = html.find('<div id="page-insights"')

next_view_marker = '<!-- ================= AI QUERY STUDIO WITH CHAT HISTORY ================= -->'
if next_view_marker not in html:
    next_view_marker = '<!-- ========================================================================= -->'

insights_end = html.find(next_view_marker, insights_start)

if insights_start != -1 and insights_end != -1:
    html = html[:insights_start] + new_insights_html + '\n                    ' + html[insights_end:]
    print("Replaced #page-insights with clean enterprise visual structure")

# Add the refined clean typographic JavaScript engine + Top-Level Viewport Modal
radial_cloud_js = '''
    <!-- ================= TOPIC DOCUMENTS EXPLORER MODAL (TOP-LEVEL FULL VIEWPORT) ================= -->
    <div id="topic-documents-modal" class="hidden flex items-center justify-center p-3 sm:p-4 animate-fadeIn" onclick="handleDocModalBackdropClick(event)">
        <div class="bg-white rounded-3xl shadow-2xl border border-gray-200 w-full max-w-3xl max-h-[88vh] flex flex-col overflow-hidden transform transition-all z-10" onclick="event.stopPropagation()">
            
            <!-- Modal Header -->
            <div class="px-6 py-4.5 border-b border-gray-100 flex items-center justify-between bg-slate-50/80">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 text-emerald-700 flex items-center justify-center border border-emerald-500/20 shadow-2xs">
                        <i data-lucide="file-text" class="w-5 h-5"></i>
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <h3 class="font-black text-[#0f172a] text-base sm:text-lg tracking-tight">Indexed Reports Explorer</h3>
                            <span id="doc-modal-keyword-badge" class="px-2.5 py-0.5 rounded-md text-[11px] font-black bg-emerald-100 text-emerald-800 border border-emerald-200">Overburden</span>
                        </div>
                        <p class="text-xs text-gray-500 font-medium">Documents sorted in descending order of keyword occurrences</p>
                    </div>
                </div>
                <button onclick="closeTopicDocumentsModal()" class="w-8 h-8 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-black flex items-center justify-center transition-all">
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            </div>

            <!-- Search Bar & Keyword Switcher -->
            <div class="px-6 py-3.5 border-b border-gray-100 bg-white space-y-2.5">
                <div class="relative">
                    <i data-lucide="search" class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"></i>
                    <input type="text" id="doc-keyword-search-input" oninput="handleDocKeywordSearch(this.value)" placeholder="Search any keyword or report title (e.g. Extraction, Coal Seam, Stripping Ratio)..." class="w-full pl-10 pr-10 py-2.5 bg-gray-50/80 border border-gray-200 rounded-xl text-xs font-semibold text-[#0f172a] placeholder-gray-400 focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all">
                    <button id="doc-search-clear-btn" onclick="clearDocKeywordSearch()" class="hidden absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                        <i data-lucide="x-circle" class="w-4 h-4"></i>
                    </button>
                </div>

                <!-- Quick Keyword Switcher Chips -->
                <div class="flex items-center gap-1.5 overflow-x-auto custom-scrollbar pb-1 text-xs">
                    <span class="text-[10px] uppercase font-bold text-gray-400 shrink-0 mr-1">Quick Keywords:</span>
                    <div id="modal-quick-keywords" class="flex gap-1.5 shrink-0"></div>
                </div>
            </div>

            <!-- Document Count & Sorting Indicator -->
            <div class="px-6 py-2.5 bg-gray-50/70 border-b border-gray-100 flex items-center justify-between text-xs text-gray-500 font-semibold">
                <div id="doc-modal-count-label" class="font-bold text-gray-700">Showing matching technical reports</div>
                <div class="flex items-center gap-1.5 text-emerald-700 font-bold text-[11px]">
                    <i data-lucide="arrow-down-narrow-wide" class="w-3.5 h-3.5"></i> Sorted by Max Occurrence
                </div>
            </div>

            <!-- Documents List Container -->
            <div id="doc-modal-list" class="p-6 space-y-3 overflow-y-auto max-h-[50vh] custom-scrollbar bg-slate-50/30">
                <!-- Rendered dynamically -->
            </div>

            <!-- Modal Footer -->
            <div class="px-6 py-3.5 border-t border-gray-100 bg-white flex items-center justify-between text-xs text-gray-500">
                <span class="text-[11px] font-medium text-gray-400">Indexed across CMPDI, CIL, SECL, MCL &amp; BCCL technical repositories</span>
                <button onclick="closeTopicDocumentsModal()" class="px-4 py-1.5 rounded-xl bg-gray-100 hover:bg-gray-200 text-[#0f172a] font-bold text-xs transition-all">
                    Close
                </button>
            </div>

        </div>
    </div>

    <!-- ================= FULL REPORT DOCUMENT VIEWER MODAL ================= -->
    <div id="full-report-viewer-modal" class="hidden flex items-center justify-center p-2 sm:p-4 animate-fadeIn" onclick="handleReportViewerBackdropClick(event)">
        <div class="bg-white rounded-3xl shadow-2xl border border-gray-200 w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden transform transition-all z-20" onclick="event.stopPropagation()">
            
            <!-- Top Nav & Actions Bar -->
            <div class="px-6 py-3.5 border-b border-gray-100 flex items-center justify-between bg-slate-50/90 shrink-0">
                <button onclick="backToReportsList()" class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white hover:bg-gray-100 border border-gray-200/80 text-gray-700 hover:text-[#0f172a] font-bold text-xs transition-all shadow-2xs">
                    <i data-lucide="arrow-left" class="w-3.5 h-3.5"></i> <span>Back to Reports</span>
                </button>
                
                <div class="flex items-center gap-2">
                    <span class="hidden sm:inline-flex px-2.5 py-0.5 rounded-md text-[10px] font-extrabold uppercase bg-emerald-100 text-emerald-800 border border-emerald-200">CMPDI Technical Archive</span>
                    <button onclick="mockDownloadReport()" class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition-all shadow-2xs">
                        <i data-lucide="download" class="w-3.5 h-3.5"></i> <span>Download PDF</span>
                    </button>
                    <button onclick="closeFullReportViewer()" class="w-8 h-8 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-black flex items-center justify-center transition-all">
                        <i data-lucide="x" class="w-4 h-4"></i>
                    </button>
                </div>
            </div>

            <!-- Document Content Body (Scrollable) -->
            <div id="full-report-viewer-content" class="p-6 sm:p-8 overflow-y-auto max-h-[84vh] custom-scrollbar bg-white space-y-6">
                <!-- Rendered dynamically -->
            </div>

        </div>
    </div>

    <!-- ================= MINING TOPIC INTELLIGENCE CLEAN TYPOGRAPHIC ENGINE ================= -->
    <style>
        #topic-documents-modal,
        #full-report-viewer-modal {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 99999 !important;
            background-color: rgba(15, 23, 42, 0.65) !important;
            backdrop-filter: blur(4px) !important;
            -webkit-backdrop-filter: blur(4px) !important;
        }
        .topic-word-node {
            transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease-out, color 0.15s ease-out;
            cursor: pointer;
            white-space: nowrap;
            user-select: none;
        }
        .topic-word-node:hover {
            transform: translate(-50%, -50%) scale(1.09) !important;
            z-index: 25 !important;
        }
        .topic-word-node.node-selected {
            z-index: 30 !important;
            transform: translate(-50%, -50%) scale(1.08) !important;
        }
        .topic-word-node.node-related {
            z-index: 20 !important;
            opacity: 1 !important;
        }
        .topic-word-node.node-dimmed {
            opacity: 0.25 !important;
            filter: grayscale(85%);
        }
    </style>

    <script>
        // ── TOPIC DATA REPOSITORY (24 Mining Terms with Organic Balanced Coordinates) ──
        const MINING_TOPICS = {
            'Extraction': {
                name: 'Extraction',
                category: 'production',
                catLabel: 'Production Operations',
                occ: 720,
                docs: 290,
                rel: 99.0,
                ring: 0,
                angle: 0,
                dx: 0, dy: 0,
                related: ['Overburden', 'ROM Production', 'Stripping Ratio', 'Shovel-Dumper', 'Coal Seam'],
                aiInsight: 'Extraction represents the primary operational metric across mechanised opencast pits with direct dispatch correlation.',
                mostCommonIn: 'Production Reports',
                topSource: 'Monthly Mining Dispatch Summaries',
                trend: [48, 55, 62, 70, 85, 92, 110, 125, 140, 155, 170, 195]
            },
            'Coal Seam': {
                name: 'Coal Seam',
                category: 'geological',
                catLabel: 'Geological Stratum',
                occ: 612,
                docs: 248,
                rel: 98.0,
                ring: 1,
                angle: 160,
                dx: -110, dy: -50,
                related: ['Seam Thickness', 'Seam Depth', 'Geological Reserve', 'Borehole', 'Ash Content'],
                aiInsight: 'Coal Seam geometry and parting structures govern stripping sequences across the Jharia and Raniganj basins.',
                mostCommonIn: 'Geological Memoirs',
                topSource: 'CMPDI Exploration Bulletins',
                trend: [40, 48, 52, 60, 68, 75, 88, 95, 105, 118, 130, 145]
            },
            'Overburden': {
                name: 'Overburden',
                category: 'production',
                catLabel: 'Production Operations',
                occ: 486,
                docs: 173,
                rel: 94.2,
                ring: 1,
                angle: 30,
                dx: 125, dy: -40,
                related: ['Stripping Ratio', 'Dragline', 'Extraction', 'Shovel-Dumper', 'Seam Depth'],
                aiInsight: 'Overburden is frequently associated with stripping ratio, excavation and production planning across the analyzed reports.',
                mostCommonIn: 'Production Reports',
                topSource: 'Mine Performance Reports',
                trend: [30, 34, 42, 45, 58, 65, 72, 80, 88, 96, 112, 128]
            },
            'Geological Reserve': {
                name: 'Geological Reserve',
                category: 'geological',
                catLabel: 'Geological Estimation',
                occ: 430,
                docs: 165,
                rel: 92.0,
                ring: 1,
                angle: 215,
                dx: -125, dy: 60,
                related: ['Coal Seam', 'Recovery Factor', 'Borehole', 'Seam Thickness', 'Exploration'],
                aiInsight: 'Reserve classifications (Proved, Indicated, Inferred) strictly follow Indian Standard Procedure guidelines in technical documentation.',
                mostCommonIn: 'Reserve Estimates',
                topSource: 'National Coal Inventory Reports',
                trend: [25, 30, 35, 42, 48, 56, 62, 70, 78, 85, 94, 105]
            },
            'ROM Production': {
                name: 'ROM Production',
                category: 'production',
                catLabel: 'Production Metrics',
                occ: 410,
                docs: 155,
                rel: 91.0,
                ring: 1,
                angle: 90,
                dx: 0, dy: 90,
                related: ['Extraction', 'Beneficiation', 'Calorific Value', 'Recovery Factor', 'Overburden'],
                aiInsight: 'Run-of-Mine extraction ledgers correlate with coal washery throughput and rapid loading silo dispatches.',
                mostCommonIn: 'Monthly Production Logs',
                topSource: 'CIL Consolidated Output Logs',
                trend: [28, 32, 38, 45, 50, 58, 65, 73, 80, 89, 98, 110]
            },
            'Stripping Ratio': {
                name: 'Stripping Ratio',
                category: 'production',
                catLabel: 'Production Operations',
                occ: 395,
                docs: 148,
                rel: 90.5,
                ring: 1,
                angle: 325,
                dx: 110, dy: 65,
                related: ['Overburden', 'Extraction', 'Dragline', 'Pit Geometry', 'Shovel-Dumper'],
                aiInsight: 'Stripping ratio benchmarks establish economic cut-off limits across SECL, MCL, and CCL concessions.',
                mostCommonIn: 'Feasibility Reports',
                topSource: 'Annual Mine Cost Audits',
                trend: [22, 28, 33, 39, 44, 52, 60, 67, 74, 82, 90, 102]
            },
            'Seam Thickness': {
                name: 'Seam Thickness',
                category: 'geological',
                catLabel: 'Geological Stratigraphy',
                occ: 385,
                docs: 142,
                rel: 89.0,
                ring: 2,
                angle: 185,
                dx: -195, dy: -25,
                related: ['Coal Seam', 'Seam Depth', 'Borehole', 'Geological Reserve'],
                aiInsight: 'Seam Thickness variability determines continuous miner applicability in deep underground horizons.',
                mostCommonIn: 'Borehole Logs',
                topSource: 'Exploration Drilling Summaries',
                trend: [20, 24, 29, 35, 40, 47, 54, 60, 68, 75, 84, 95]
            },
            'Slope Stability': {
                name: 'Slope Stability',
                category: 'safety',
                catLabel: 'Safety & Geotechnical',
                occ: 360,
                docs: 138,
                rel: 88.0,
                ring: 2,
                angle: 350,
                dx: 195, dy: -10,
                related: ['Pit Geometry', 'Groundwater', 'Overburden', 'Drilling & Blasting'],
                aiInsight: 'Continuous slope stability radar records prevent bench failure risks along highwall crests.',
                mostCommonIn: 'Safety Audit Briefs',
                topSource: 'DGMS Compliance Reviews',
                trend: [19, 23, 28, 34, 40, 46, 53, 61, 69, 77, 86, 98]
            },
            'Groundwater': {
                name: 'Groundwater',
                category: 'environmental',
                catLabel: 'Environmental Hydrology',
                occ: 350,
                docs: 136,
                rel: 87.2,
                ring: 2,
                angle: 70,
                dx: 70, dy: 155,
                related: ['Slope Stability', 'Reclamation', 'Mine Ventilation', 'Subsidence'],
                aiInsight: 'Hydro-geological modeling and sump dewatering protect working faces while sustaining regional aquifers.',
                mostCommonIn: 'Environmental Clearances',
                topSource: 'MoEFCC Impact Submissions',
                trend: [17, 21, 26, 32, 38, 44, 51, 58, 66, 74, 83, 94]
            },
            'Seam Depth': {
                name: 'Seam Depth',
                category: 'geological',
                catLabel: 'Geological Stratigraphy',
                occ: 340,
                docs: 130,
                rel: 86.5,
                ring: 2,
                angle: 125,
                dx: -80, dy: -125,
                related: ['Coal Seam', 'Overburden', 'Borehole', 'Pit Geometry'],
                aiInsight: 'Depth contour mapping indicates economic transitions from opencast benches to underground horizons.',
                mostCommonIn: 'Geological Folios',
                topSource: 'CMPDI Regional Basins',
                trend: [18, 22, 26, 31, 36, 42, 48, 55, 62, 70, 78, 88]
            },
            'Drilling & Blasting': {
                name: 'Drilling & Blasting',
                category: 'safety',
                catLabel: 'Operations & Safety',
                occ: 330,
                docs: 125,
                rel: 85.0,
                ring: 2,
                angle: 300,
                dx: 100, dy: -130,
                related: ['Overburden', 'Shovel-Dumper', 'Slope Stability', 'Extraction'],
                aiInsight: 'Controlled blast initiation with electronic delay detonators minimizes ground vibration and backbreak.',
                mostCommonIn: 'Operational Logs',
                topSource: 'Mine Safety & Blasting Audits',
                trend: [16, 20, 24, 29, 34, 40, 47, 54, 61, 69, 78, 89]
            },
            'Shovel-Dumper': {
                name: 'Shovel-Dumper',
                category: 'production',
                catLabel: 'HEMM Production',
                occ: 320,
                docs: 122,
                rel: 85.0,
                ring: 2,
                angle: 25,
                dx: 190, dy: -90,
                related: ['Overburden', 'Extraction', 'Stripping Ratio', 'Dragline'],
                aiInsight: 'HEMM equipment matching ratios dictate shovel cycle times and haul road traffic densities.',
                mostCommonIn: 'Equipment Logs',
                topSource: 'HEMM Performance Reviews',
                trend: [14, 18, 22, 27, 32, 38, 45, 52, 59, 67, 76, 86]
            },
            'Borehole': {
                name: 'Borehole',
                category: 'geological',
                catLabel: 'Geological Exploration',
                occ: 310,
                docs: 118,
                rel: 84.0,
                ring: 2,
                angle: 235,
                dx: -75, dy: 155,
                related: ['Exploration', 'Coal Seam', 'Ash Content', 'Geological Reserve'],
                aiInsight: 'Core drill logs establish proximate analysis values, seam splits, and structural fault boundaries.',
                mostCommonIn: 'Drilling Archives',
                topSource: 'Geological Survey Documentation',
                trend: [15, 19, 23, 28, 33, 38, 44, 50, 56, 64, 72, 82]
            },
            'Exploration': {
                name: 'Exploration',
                category: 'geological',
                catLabel: 'Geological Exploration',
                occ: 295,
                docs: 110,
                rel: 81.0,
                ring: 3,
                angle: 145,
                dx: -190, dy: -115,
                related: ['Borehole', 'Geological Reserve', 'Coal Seam', 'Recovery Factor'],
                aiInsight: 'Detailed 2D seismic exploration and non-coring validation delineate virgin coal block boundaries.',
                mostCommonIn: 'Geological Reports',
                topSource: 'National Mineral Exploration Trust',
                trend: [14, 17, 21, 26, 31, 36, 42, 49, 56, 64, 73, 83]
            },
            'Mine Ventilation': {
                name: 'Mine Ventilation',
                category: 'safety',
                catLabel: 'Underground Safety',
                occ: 290,
                docs: 112,
                rel: 81.5,
                ring: 3,
                angle: 270,
                dx: -55, dy: -190,
                related: ['Slope Stability', 'Groundwater', 'Mine Closure', 'Extraction'],
                aiInsight: 'Continuous airflow monitoring and methane drainage safeguards gassy underground workings.',
                mostCommonIn: 'Safety Audits',
                topSource: 'DGMS Inspection Reports',
                trend: [13, 16, 20, 24, 29, 34, 40, 47, 54, 61, 70, 80]
            },
            'Dragline': {
                name: 'Dragline',
                category: 'production',
                catLabel: 'HEMM Production',
                occ: 280,
                docs: 105,
                rel: 80.0,
                ring: 3,
                angle: 45,
                dx: 220, dy: 75,
                related: ['Overburden', 'Stripping Ratio', 'Shovel-Dumper', 'Extraction'],
                aiInsight: 'High-capacity walking draglines perform primary side-casting in mega-opencast mines like Gevra and Nigahi.',
                mostCommonIn: 'Heavy Equipment Logs',
                topSource: 'Dragline Utilization Ledgers',
                trend: [12, 15, 19, 23, 27, 32, 38, 44, 51, 58, 66, 75]
            },
            'Reclamation': {
                name: 'Reclamation',
                category: 'environmental',
                catLabel: 'Environmental Restoration',
                occ: 275,
                docs: 102,
                rel: 79.0,
                ring: 3,
                angle: 20,
                dx: 165, dy: 150,
                related: ['Mine Closure', 'Groundwater', 'Subsidence', 'Overburden'],
                aiInsight: 'Technical regrading and biological afforestation transform decommissioned dumps into restored eco-zones.',
                mostCommonIn: 'Sustainability Reports',
                topSource: 'CMPDI Remote Sensing Land Restorations',
                trend: [11, 14, 18, 22, 27, 32, 38, 44, 51, 58, 66, 75]
            },
            'Ash Content': {
                name: 'Ash Content',
                category: 'safety',
                catLabel: 'Coal Quality & Safety',
                occ: 270,
                docs: 104,
                rel: 78.5,
                ring: 3,
                angle: 210,
                dx: -220, dy: 65,
                related: ['Calorific Value', 'Beneficiation', 'Coal Seam', 'Borehole'],
                aiInsight: 'Proximate analysis parameters establish coal grade certification (G1 to G17) inverse to inherent mineral matter.',
                mostCommonIn: 'Coal Quality Certificates',
                topSource: 'CMPDI Central Quality Lab',
                trend: [11, 14, 18, 22, 26, 31, 36, 42, 49, 56, 64, 73]
            },
            'Calorific Value': {
                name: 'Calorific Value',
                category: 'safety',
                catLabel: 'Coal Quality & Safety',
                occ: 265,
                docs: 100,
                rel: 77.8,
                ring: 3,
                angle: 245,
                dx: -165, dy: 160,
                related: ['Ash Content', 'Beneficiation', 'ROM Production', 'Coal Seam'],
                aiInsight: 'Gross Calorific Value sampling determines fuel supply agreement compliance for power utilities.',
                mostCommonIn: 'Commercial Coal Dispatches',
                topSource: 'Third-Party Sampling Audits',
                trend: [10, 13, 17, 21, 25, 30, 35, 41, 47, 54, 62, 71]
            },
            'Subsidence': {
                name: 'Subsidence',
                category: 'environmental',
                catLabel: 'Environmental Geotech',
                occ: 260,
                docs: 98,
                rel: 77.0,
                ring: 3,
                angle: 120,
                dx: -165, dy: 110,
                related: ['Reclamation', 'Groundwater', 'Mine Closure', 'Seam Depth'],
                aiInsight: 'Surface strata deformation monitoring ensures longwall caving preserves overlying surface structures.',
                mostCommonIn: 'Environmental Monitoring',
                topSource: 'Mine Safety & Strata Records',
                trend: [10, 13, 16, 20, 24, 29, 34, 40, 46, 53, 61, 70]
            },
            'Pit Geometry': {
                name: 'Pit Geometry',
                category: 'safety',
                catLabel: 'Operations & Safety',
                occ: 250,
                docs: 95,
                rel: 76.0,
                ring: 3,
                angle: 315,
                dx: 215, dy: -155,
                related: ['Slope Stability', 'Stripping Ratio', 'Seam Depth', 'Overburden'],
                aiInsight: 'Haul road switchback radii and bench widths are calculated to safely accommodate 240T dumpers.',
                mostCommonIn: 'Mine Planning Reports',
                topSource: 'CMPDI Mine Design Directorate',
                trend: [9, 12, 15, 19, 23, 28, 33, 39, 45, 52, 60, 68]
            },
            'Recovery Factor': {
                name: 'Recovery Factor',
                category: 'production',
                catLabel: 'Production Operations',
                occ: 240,
                docs: 92,
                rel: 78.0,
                ring: 3,
                angle: 100,
                dx: -215, dy: 20,
                related: ['Geological Reserve', 'Extraction', 'Coal Seam', 'ROM Production'],
                aiInsight: 'Mechanized surface mining yields over 90% resource extraction compared to 55-65% in legacy pillar workings.',
                mostCommonIn: 'Resource Audit Reports',
                topSource: 'CIL Conservation Commendations',
                trend: [9, 11, 14, 18, 22, 27, 32, 38, 44, 50, 57, 65]
            },
            'Beneficiation': {
                name: 'Beneficiation',
                category: 'production',
                catLabel: 'Coal Beneficiation',
                occ: 215,
                docs: 85,
                rel: 74.0,
                ring: 3,
                angle: 85,
                dx: 135, dy: -185,
                related: ['Ash Content', 'Calorific Value', 'ROM Production', 'Extraction'],
                aiInsight: 'Heavy media cyclone circuits yield high-grade coking coal fractions for domestic steel plants.',
                mostCommonIn: 'Washery Yield Reports',
                topSource: 'Coal Washery Operations',
                trend: [8, 10, 13, 16, 20, 24, 28, 33, 38, 44, 51, 58]
            },
            'Mine Closure': {
                name: 'Mine Closure',
                category: 'environmental',
                catLabel: 'Environmental Life Cycle',
                occ: 210,
                docs: 80,
                rel: 72.0,
                ring: 3,
                angle: 340,
                dx: 0, dy: 200,
                related: ['Reclamation', 'Groundwater', 'Mine Ventilation', 'Subsidence'],
                aiInsight: 'Progressive closure frameworks cover void water management and post-operational community land handover.',
                mostCommonIn: 'Progressive Closure Plans',
                topSource: 'Ministry of Coal Approvals',
                trend: [7, 9, 12, 15, 18, 22, 26, 31, 36, 42, 48, 55]
            }
        };

        let currentSelectedTopicKey = 'Overburden';
        let currentTopicCategoryFilter = 'all';
        let currentTrendTimeRange = '3Y';
        let topicTrendChartInstance = null;

        // CMPDI Enterprise Category Color System
        const TOPIC_CATEGORY_THEMES = {
            'production': {
                dotColor: '#16a34a',
                textColor: '#15803d',
                hoverColor: '#166534',
                lineStroke: 'rgba(22, 163, 74, 0.45)',
                badgeBg: 'bg-emerald-50',
                badgeText: 'text-emerald-800',
                badgeBorder: 'border-emerald-200'
            },
            'geological': {
                dotColor: '#0284c7',
                textColor: '#0369a1',
                hoverColor: '#075985',
                lineStroke: 'rgba(2, 132, 199, 0.45)',
                badgeBg: 'bg-sky-50',
                badgeText: 'text-sky-800',
                badgeBorder: 'border-sky-200'
            },
            'environmental': {
                dotColor: '#ea580c',
                textColor: '#c2410c',
                hoverColor: '#9a3412',
                lineStroke: 'rgba(234, 88, 12, 0.45)',
                badgeBg: 'bg-amber-50',
                badgeText: 'text-amber-800',
                badgeBorder: 'border-amber-200'
            },
            'safety': {
                dotColor: '#e11d48',
                textColor: '#be123c',
                hoverColor: '#9f1239',
                lineStroke: 'rgba(225, 29, 72, 0.45)',
                badgeBg: 'bg-rose-50',
                badgeText: 'text-rose-800',
                badgeBorder: 'border-rose-200'
            },
            'exploration': {
                dotColor: '#0284c7',
                textColor: '#0369a1',
                hoverColor: '#075985',
                lineStroke: 'rgba(2, 132, 199, 0.45)',
                badgeBg: 'bg-cyan-50',
                badgeText: 'text-cyan-800',
                badgeBorder: 'border-cyan-200'
            }
        };

        // ── COMPREHENSIVE INDEXED REPORTS DATABASE ──
        const INDEXED_REPORTS_DATABASE = [
            {
                id: 'CMPDI-GEO-2024-JHA-IV',
                title: 'CMPDI/RI-II/GEO/2024 - Jharia Coalfield Block IV Detailed Geological Assessment',
                agency: 'CMPDI RI-II Dhanbad',
                type: 'Exploration & Stratigraphy Memoir',
                date: 'Sep 2024',
                pages: 142,
                keywords: {
                    'Overburden': 54,
                    'Coal Seam': 88,
                    'Seam Thickness': 42,
                    'Seam Depth': 38,
                    'Stripping Ratio': 31,
                    'Borehole': 65,
                    'Geological Reserve': 49,
                    'Extraction': 36,
                    'Ash Content': 27,
                    'Drilling & Blasting': 19
                },
                snippet: 'Extensive core drilling across 42 boreholes establishes continuous parting thickness with overburden bench stability requiring highwall monitoring.'
            },
            {
                id: 'SECL-GEVRA-OCP-2024',
                title: 'SECL Gevra Mega-Opencast Pit Phase-VI HEMM & Overburden Removal Audit',
                agency: 'SECL Bilaspur',
                type: 'Annual Mine Performance Audit',
                date: 'Aug 2024',
                pages: 188,
                keywords: {
                    'Overburden': 76,
                    'Stripping Ratio': 62,
                    'Dragline': 48,
                    'Extraction': 82,
                    'ROM Production': 59,
                    'Shovel-Dumper': 44,
                    'Slope Stability': 35,
                    'Pit Geometry': 28,
                    'Drilling & Blasting': 32
                },
                snippet: 'Walking dragline side-casting handled over 42.6 MCuM of overburden in harmony with rapid shovel-dumper circuit synchronization.'
            },
            {
                id: 'MCL-TALCHER-ANN-2024',
                title: 'MCL Talcher Basin Seam Extraction & Volume Reconciliation Report',
                agency: 'MCL Sambalpur',
                type: 'Monthly Dispatch & Yield Ledger',
                date: 'Jul 2024',
                pages: 96,
                keywords: {
                    'Extraction': 94,
                    'ROM Production': 71,
                    'Coal Seam': 58,
                    'Beneficiation': 39,
                    'Calorific Value': 46,
                    'Ash Content': 38,
                    'Overburden': 41,
                    'Recovery Factor': 33,
                    'Stripping Ratio': 29
                },
                snippet: 'Run-of-Mine coal extraction ledgers surpassed quarterly benchmarks with raw coal washed through heavy media cyclone circuits.'
            },
            {
                id: 'CMPDI-ENV-EIA-2024',
                title: 'MoEFCC Comprehensive EIA & Progressive Mine Closure Plan for Korba OC Basins',
                agency: 'CMPDI Environmental Directorate',
                type: 'Statutory Environmental Impact Audit',
                date: 'Jun 2024',
                pages: 210,
                keywords: {
                    'Reclamation': 68,
                    'Groundwater': 58,
                    'Mine Closure': 52,
                    'Subsidence': 44,
                    'Overburden': 36,
                    'Slope Stability': 28,
                    'Mine Ventilation': 22,
                    'Exploration': 18
                },
                snippet: 'Biological reclamation of internal dump slopes restored 145 hectares while hydro-geological piezometer networks tracked groundwater rebound.'
            },
            {
                id: 'BCCL-DHA-STRATA-2024',
                title: 'BCCL Koyla Bhawan Underground Strata Control & Ventilation Safety Review',
                agency: 'BCCL Dhanbad',
                type: 'Geotechnical Safety Audit',
                date: 'May 2024',
                pages: 115,
                keywords: {
                    'Mine Ventilation': 74,
                    'Slope Stability': 48,
                    'Subsidence': 51,
                    'Coal Seam': 45,
                    'Seam Depth': 39,
                    'Groundwater': 31,
                    'Drilling & Blasting': 26,
                    'Mine Closure': 21
                },
                snippet: 'Continuous airflow anemometry and methane drainage manifolds maintain ventilation safety across depillaring panels.'
            },
            {
                id: 'CMPDI-NMET-EXPL-2024',
                title: 'NMET High-Resolution 2D Seismic & Deep Borehole Core Exploration Folio',
                agency: 'CMPDI Exploration Directorate',
                type: 'National Coal Inventory Exploration',
                date: 'Apr 2024',
                pages: 164,
                keywords: {
                    'Borehole': 89,
                    'Exploration': 78,
                    'Geological Reserve': 72,
                    'Coal Seam': 66,
                    'Seam Thickness': 53,
                    'Seam Depth': 47,
                    'Ash Content': 34,
                    'Recovery Factor': 29
                },
                snippet: 'Deep coring validation delineated virgin geological reserves in Raniganj sub-basin with detailed lithology column correlation.'
            },
            {
                id: 'CCL-NORTH-KARAN-2023',
                title: 'CCL North Karanpura Coal Washery & Quality Grade Certification Audit',
                agency: 'CCL Ranchi',
                type: 'Coal Beneficiation Technical Study',
                date: 'Nov 2023',
                pages: 88,
                keywords: {
                    'Beneficiation': 64,
                    'Calorific Value': 58,
                    'Ash Content': 52,
                    'ROM Production': 45,
                    'Extraction': 39,
                    'Coal Seam': 32,
                    'Recovery Factor': 28,
                    'Overburden': 19
                },
                snippet: 'Proximate analysis verified reduction of ash content from 41% to 28%, significantly uplifting Gross Calorific Value (GCV).'
            },
            {
                id: 'WCL-NAGPUR-SLOPE-2023',
                title: 'WCL Highwall Slope Stability Radar Assessment & Pit Design Parameters',
                agency: 'WCL Nagpur',
                type: 'DGMS Geotechnical Safety Audit',
                date: 'Oct 2023',
                pages: 104,
                keywords: {
                    'Slope Stability': 67,
                    'Pit Geometry': 59,
                    'Drilling & Blasting': 48,
                    'Overburden': 43,
                    'Stripping Ratio': 37,
                    'Groundwater': 33,
                    'Shovel-Dumper': 29,
                    'Extraction': 25
                },
                snippet: 'Interferometric slope stability radar detected zero millimetric displacement along the 72-degree highwall bench crests.'
            },
            {
                id: 'ECL-RANIGANJ-SUBS-2023',
                title: 'ECL Raniganj Coalfield Longwall Subsidence & Environmental Monitoring',
                agency: 'ECL Sanctoria',
                type: 'Surface Strata Deformation Report',
                date: 'Aug 2023',
                pages: 130,
                keywords: {
                    'Subsidence': 62,
                    'Groundwater': 49,
                    'Reclamation': 41,
                    'Coal Seam': 38,
                    'Seam Depth': 35,
                    'Mine Closure': 30,
                    'Mine Ventilation': 24
                },
                snippet: 'Continuous laser leveling showed strata subsidence compaction stabilized within 90 days following longwall caving extraction.'
            },
            {
                id: 'CMPDI-RES-AUDIT-2023',
                title: 'CMPDI All-India Coal Reserve Balance Ledger & Seam Extraction Factor Audit',
                agency: 'CMPDI Central Planning HQ',
                type: 'National Statistical Compilation',
                date: 'Jun 2023',
                pages: 240,
                keywords: {
                    'Geological Reserve': 92,
                    'Recovery Factor': 75,
                    'Extraction': 68,
                    'Coal Seam': 61,
                    'Overburden': 47,
                    'ROM Production': 44,
                    'Exploration': 41,
                    'Seam Thickness': 38,
                    'Seam Depth': 36
                },
                snippet: 'National coal inventory reconciliation proves 361.4 Billion Tonnes of reserves with surface mining recovery factor reaching 91.2%.'
            }
        ];

        // Render Clean Typographic Radial Word Map
        function renderRadialWordCloud() {
            const container = document.getElementById('radial-word-nodes-layer');
            const linesGroup = document.getElementById('radial-connector-lines');
            if (!container) return;

            container.innerHTML = '';
            if (linesGroup) linesGroup.innerHTML = '';

            const rect = container.getBoundingClientRect();
            const width = rect.width || 600;
            const height = rect.height || 450;
            const centerX = width / 2;
            const centerY = height / 2;

            // Scale factors based on available canvas space
            const scaleX = Math.min(1.0, (width - 60) / 540);
            const scaleY = Math.min(1.0, (height - 60) / 440);

            const selectedData = MINING_TOPICS[currentSelectedTopicKey];
            const selPosX = centerX + (selectedData.dx || 0) * scaleX;
            const selPosY = centerY + (selectedData.dy || 0) * scaleY;
            const selTheme = TOPIC_CATEGORY_THEMES[selectedData.category] || TOPIC_CATEGORY_THEMES['production'];

            Object.keys(MINING_TOPICS).forEach(key => {
                const item = MINING_TOPICS[key];
                const isMatchingCategory = currentTopicCategoryFilter === 'all' || 
                                           item.category === currentTopicCategoryFilter ||
                                           (currentTopicCategoryFilter === 'exploration' && (key === 'Borehole' || key === 'Exploration' || item.category === 'geological'));

                const isSelected = key === currentSelectedTopicKey;
                const isRelated = selectedData && selectedData.related && selectedData.related.includes(key);

                // Compute exact position with scale
                const posX = centerX + (item.dx || 0) * scaleX;
                const posY = centerY + (item.dy || 0) * scaleY;

                const theme = TOPIC_CATEGORY_THEMES[item.category] || TOPIC_CATEGORY_THEMES['production'];

                // Typographic Hierarchy by Occurrence Frequency
                let sizeClass = 'text-[12px] sm:text-[12.5px] font-medium';
                if (item.occ >= 700) {
                    sizeClass = 'text-[20px] sm:text-[22px] font-black tracking-tight';
                } else if (item.occ >= 600) {
                    sizeClass = 'text-[17px] sm:text-[18.5px] font-extrabold tracking-tight';
                } else if (item.occ >= 450) {
                    sizeClass = 'text-[15px] sm:text-[16px] font-bold';
                } else if (item.occ >= 380) {
                    sizeClass = 'text-[13.5px] sm:text-[14px] font-semibold';
                } else if (item.occ >= 300) {
                    sizeClass = 'text-[12.5px] sm:text-[13px] font-semibold';
                }

                // Draw thin, crisp connection line ONLY from selected keyword to its related terms
                if (linesGroup && isRelated && !isSelected && isMatchingCategory) {
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', selPosX);
                    line.setAttribute('y1', selPosY);
                    line.setAttribute('x2', posX);
                    line.setAttribute('y2', posY);
                    line.setAttribute('stroke', selTheme.lineStroke || '#cbd5e1');
                    line.setAttribute('stroke-width', '1.4');
                    line.setAttribute('stroke-dasharray', '3,3');
                    linesGroup.appendChild(line);
                }

                // Clean Typography Element (No heavy pill container, color on text + dot)
                const nodeEl = document.createElement('div');
                nodeEl.id = 'node-' + key.replace(/[^a-zA-Z0-9]/g, '-');
                nodeEl.className = `topic-word-node absolute flex items-center gap-1.5 px-1.5 py-0.5 rounded-md ${sizeClass}`;
                nodeEl.style.left = `${posX}px`;
                nodeEl.style.top = `${posY}px`;
                nodeEl.style.transform = 'translate(-50%, -50%)';

                // Category Dot
                const dotHtml = `<span class="w-1.5 h-1.5 rounded-full inline-block shrink-0 shadow-2xs" style="background-color:${theme.dotColor}"></span>`;

                if (isSelected) {
                    // Selected state: subtle lime-green / dark underline & white backdrop highlight (NOT a giant pill)
                    nodeEl.classList.add('node-selected');
                    nodeEl.innerHTML = `
                        <div class="bg-white/95 border-b-2 border-[#16a34a] shadow-xs px-2.5 py-0.5 rounded-md flex items-center gap-1.5">
                            ${dotHtml}
                            <span class="font-black text-[#0f172a]">${item.name}</span>
                        </div>
                    `;
                } else {
                    nodeEl.style.color = theme.textColor;
                    nodeEl.innerHTML = `${dotHtml}<span>${item.name}</span>`;
                    
                    if (!isMatchingCategory) {
                        nodeEl.classList.add('node-dimmed');
                    } else if (isRelated) {
                        nodeEl.classList.add('node-related');
                        nodeEl.style.color = theme.hoverColor || theme.textColor;
                        nodeEl.style.fontWeight = '800';
                    } else {
                        nodeEl.style.opacity = '0.78';
                    }
                }

                // Event Listeners
                nodeEl.onmouseenter = (e) => {
                    showRadialTooltip(e, item);
                    if (!isSelected) nodeEl.style.color = theme.hoverColor;
                };
                nodeEl.onmouseleave = () => {
                    hideRadialTooltip();
                    if (!isSelected && isMatchingCategory) {
                        nodeEl.style.color = isRelated ? (theme.hoverColor || theme.textColor) : theme.textColor;
                    }
                };
                nodeEl.onclick = () => selectTopicNode(key);

                container.appendChild(nodeEl);
            });
        }

        // Show Hover Tooltip
        function showRadialTooltip(e, item) {
            const tooltip = document.getElementById('radial-topic-tooltip');
            const container = document.getElementById('radial-cloud-container');
            if (!tooltip || !container) return;

            document.getElementById('r-tooltip-title').textContent = item.name;
            document.getElementById('r-tooltip-cat').textContent = item.catLabel;
            document.getElementById('r-tooltip-occ').textContent = `${item.occ} mentions`;
            document.getElementById('r-tooltip-rel').textContent = `${item.rel}%`;
            document.getElementById('r-tooltip-docs').textContent = `${item.docs} PDFs`;

            const cRect = container.getBoundingClientRect();
            const x = e.clientX - cRect.left;
            const y = e.clientY - cRect.top;

            tooltip.style.left = `${x}px`;
            tooltip.style.top = `${y}px`;
            tooltip.classList.remove('opacity-0');
            tooltip.classList.add('opacity-100');
        }

        function hideRadialTooltip() {
            const tooltip = document.getElementById('radial-topic-tooltip');
            if (tooltip) {
                tooltip.classList.remove('opacity-100');
                tooltip.classList.add('opacity-0');
            }
        }

        // Select and Focus Topic Node
        function selectTopicNode(topicKey) {
            if (!MINING_TOPICS[topicKey]) return;
            currentSelectedTopicKey = topicKey;
            
            const data = MINING_TOPICS[topicKey];
            const theme = TOPIC_CATEGORY_THEMES[data.category] || TOPIC_CATEGORY_THEMES['production'];

            // Update Detail Card Fields
            document.getElementById('detail-topic-name').textContent = data.name;
            document.getElementById('detail-topic-occ').textContent = data.occ;
            document.getElementById('detail-topic-docs').textContent = data.docs;
            const docsSubtitleEl = document.getElementById('detail-topic-docs-subtitle');
            if (docsSubtitleEl) {
                docsSubtitleEl.innerHTML = `View related documents &rarr;`;
            }
            document.getElementById('detail-topic-rel').textContent = `${data.rel}%`;
            document.getElementById('detail-topic-cat').textContent = data.catLabel;
            document.getElementById('detail-ai-insight').textContent = `"${data.aiInsight}"`;
            document.getElementById('detail-context-common').textContent = data.mostCommonIn;
            document.getElementById('detail-context-source').textContent = data.topSource;

            // Update Badge
            const badgeEl = document.getElementById('detail-topic-badge');
            if (badgeEl) {
                badgeEl.textContent = data.catLabel;
                badgeEl.className = `px-2.5 py-0.5 rounded font-bold text-[10px] uppercase border ${theme.badgeBg} ${theme.badgeText} ${theme.badgeBorder}`;
            }

            // Update Related Topics Chips
            const relatedContainer = document.getElementById('detail-related-chips');
            if (relatedContainer) {
                relatedContainer.innerHTML = (data.related || []).map(relKey => {
                    const relData = MINING_TOPICS[relKey];
                    const relTheme = relData ? TOPIC_CATEGORY_THEMES[relData.category] : theme;
                    return `
                        <button onclick="selectTopicNode('${relKey}')" class="px-2.5 py-1 rounded-lg text-xs font-semibold transition-all bg-gray-50 hover:bg-white text-gray-700 hover:text-[#0f172a] border border-gray-200/80 shadow-2xs hover:scale-105 active:scale-95 flex items-center gap-1.5">
                            <span class="w-1.5 h-1.5 rounded-full" style="background-color:${relTheme.dotColor}"></span>
                            <span>${relKey}</span>
                        </button>
                    `;
                }).join('');
            }

            // Re-render Trend Chart
            updateTopicTrendChart(data);

            // Re-render Word Cloud to show active selection and clean connector lines
            renderRadialWordCloud();

            if (window.lucide) lucide.createIcons();
        }

        // Focus topic in cloud with smooth border pulse
        function focusTopicInCloud(topicKey) {
            selectTopicNode(topicKey);
            const container = document.getElementById('radial-cloud-container');
            if (container) {
                container.classList.add('ring-1', 'ring-[#16a34a]');
                setTimeout(() => container.classList.remove('ring-1', 'ring-[#16a34a]'), 500);
            }
        }

        // Filter Category
        function filterTopicCategory(cat) {
            currentTopicCategoryFilter = cat;
            document.querySelectorAll('.topic-cat-btn').forEach(btn => {
                btn.classList.remove('bg-[#0f172a]', 'text-white', 'shadow-2xs');
                btn.classList.add('bg-gray-50', 'text-gray-600', 'border-gray-200/70');
            });
            const activeBtn = document.getElementById('topic-filter-' + cat);
            if (activeBtn) {
                activeBtn.classList.remove('bg-gray-50', 'text-gray-600', 'border-gray-200/70');
                activeBtn.classList.add('bg-[#0f172a]', 'text-white', 'shadow-2xs');
            }
            renderRadialWordCloud();
        }

        // Trend Chart Time Range Switcher
        function setTrendTimeRange(range) {
            currentTrendTimeRange = range;
            document.querySelectorAll('.trend-btn').forEach(btn => {
                btn.classList.remove('bg-white', 'text-[#0f172a]', 'shadow-2xs', 'font-extrabold');
                btn.classList.add('hover:text-[#0f172a]');
            });
            const activeBtn = document.getElementById('trend-range-' + range);
            if (activeBtn) {
                activeBtn.classList.add('bg-white', 'text-[#0f172a]', 'shadow-2xs', 'font-extrabold');
            }
            const data = MINING_TOPICS[currentSelectedTopicKey];
            if (data) updateTopicTrendChart(data);
        }

        // Update Trend Chart with Chart.js using CMPDI color accents
        function updateTopicTrendChart(data) {
            const canvas = document.getElementById('topicTrendCanvas');
            if (!canvas) return;

            let labels = [];
            let points = [];

            if (currentTrendTimeRange === '1Y') {
                labels = ['Q1 24', 'Q2 24', 'Q3 24', 'Q4 24'];
                points = (data.trend || [20, 40, 60, 80]).slice(-4);
            } else if (currentTrendTimeRange === '3Y') {
                labels = ['2022 Q1', '2022 Q3', '2023 Q1', '2023 Q3', '2024 Q1', '2024 Q3'];
                points = (data.trend || [10, 25, 45, 60, 80, 100]).slice(-6);
            } else if (currentTrendTimeRange === '5Y') {
                labels = ['2020', '2021', '2022', '2023', '2024'];
                points = [
                    Math.round(data.occ * 0.25),
                    Math.round(data.occ * 0.42),
                    Math.round(data.occ * 0.61),
                    Math.round(data.occ * 0.82),
                    data.occ
                ];
            } else { // ALL
                labels = ['2018', '2019', '2020', '2021', '2022', '2023', '2024'];
                points = [
                    Math.round(data.occ * 0.12),
                    Math.round(data.occ * 0.20),
                    Math.round(data.occ * 0.35),
                    Math.round(data.occ * 0.50),
                    Math.round(data.occ * 0.68),
                    Math.round(data.occ * 0.85),
                    data.occ
                ];
            }

            const theme = TOPIC_CATEGORY_THEMES[data.category] || TOPIC_CATEGORY_THEMES['production'];

            if (topicTrendChartInstance) {
                topicTrendChartInstance.destroy();
            }

            const ctx = canvas.getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, 90);
            gradient.addColorStop(0, theme.lineStroke || 'rgba(22, 163, 74, 0.2)');
            gradient.addColorStop(1, 'rgba(255, 255, 255, 0.00)');

            topicTrendChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        data: points,
                        borderColor: theme.dotColor || '#16a34a',
                        borderWidth: 2,
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.35,
                        pointRadius: 2.5,
                        pointBackgroundColor: '#ffffff',
                        pointBorderColor: theme.dotColor || '#16a34a',
                        pointBorderWidth: 1.5,
                        pointHoverRadius: 4.5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#0f172a',
                            titleFont: { size: 10, weight: 'bold' },
                            bodyFont: { size: 11, weight: '600' },
                            padding: 6,
                            cornerRadius: 6,
                            displayColors: false,
                            callbacks: {
                                label: (context) => `${context.parsed.y} Occurrences`
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { font: { size: 9, weight: '600' }, color: '#94a3b8' }
                        },
                        y: {
                            grid: { color: '#f8fafc' },
                            ticks: { font: { size: 9, weight: '600' }, color: '#94a3b8', maxTicksLimit: 3 }
                        }
                    }
                }
            });
        }

        // ── TOPIC DOCUMENTS MODAL CONTROLS & RANKING ENGINE ──
        let activeModalSearchKeyword = 'Overburden';

        function openTopicDocumentsModal(keyword) {
            activeModalSearchKeyword = keyword || currentSelectedTopicKey || 'Overburden';
            const modal = document.getElementById('topic-documents-modal');
            const searchInput = document.getElementById('doc-keyword-search-input');
            if (!modal) return;

            if (searchInput) searchInput.value = activeModalSearchKeyword;
            renderModalQuickKeywordChips();
            renderTopicDocuments(activeModalSearchKeyword);

            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';

            if (window.lucide) lucide.createIcons();
        }

        function closeTopicDocumentsModal() {
            const modal = document.getElementById('topic-documents-modal');
            if (modal) {
                modal.classList.add('hidden');
                document.body.style.overflow = '';
            }
        }

        function handleDocModalBackdropClick(e) {
            if (e.target.id === 'topic-documents-modal') {
                closeTopicDocumentsModal();
            }
        }

        // Quick Keyword Filter Chips inside the modal
        function renderModalQuickKeywordChips() {
            const container = document.getElementById('modal-quick-keywords');
            if (!container) return;

            const popularKeys = ['Overburden', 'Extraction', 'Coal Seam', 'Stripping Ratio', 'Borehole', 'Slope Stability', 'Groundwater', 'Dragline', 'Beneficiation'];
            container.innerHTML = popularKeys.map(k => {
                const isCurrent = k.toLowerCase() === activeModalSearchKeyword.toLowerCase();
                const theme = MINING_TOPICS[k] ? TOPIC_CATEGORY_THEMES[MINING_TOPICS[k].category] : TOPIC_CATEGORY_THEMES['production'];
                return `
                    <button onclick="setModalSearchKeyword('${k}')" class="px-2.5 py-1 rounded-lg text-[11px] font-bold transition-all flex items-center gap-1.5 ${isCurrent ? 'bg-[#0f172a] text-white shadow-xs' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}">
                        <span class="w-1.5 h-1.5 rounded-full" style="background-color:${theme.dotColor}"></span>
                        <span>${k}</span>
                    </button>
                `;
            }).join('');
        }

        function setModalSearchKeyword(keyword) {
            const searchInput = document.getElementById('doc-keyword-search-input');
            if (searchInput) searchInput.value = keyword;
            activeModalSearchKeyword = keyword;
            renderModalQuickKeywordChips();
            renderTopicDocuments(keyword);
        }

        function handleDocKeywordSearch(query) {
            const clearBtn = document.getElementById('doc-search-clear-btn');
            if (clearBtn) {
                if (query && query.trim().length > 0) {
                    clearBtn.classList.remove('hidden');
                } else {
                    clearBtn.classList.add('hidden');
                }
            }
            activeModalSearchKeyword = query.trim();
            renderTopicDocuments(query.trim());
        }

        function clearDocKeywordSearch() {
            const searchInput = document.getElementById('doc-keyword-search-input');
            if (searchInput) searchInput.value = '';
            handleDocKeywordSearch('');
        }

        // Render documents sorted by maximum occurrences of the queried keyword
        function renderTopicDocuments(keywordQuery) {
            const listContainer = document.getElementById('doc-modal-list');
            const countLabel = document.getElementById('doc-modal-count-label');
            const keywordBadge = document.getElementById('doc-modal-keyword-badge');
            if (!listContainer) return;

            const targetKey = keywordQuery || 'All Technical Documents';
            if (keywordBadge) {
                keywordBadge.textContent = targetKey;
            }

            // Find matching reports and calculate occurrence count for the queried keyword
            let matchedReports = [];

            INDEXED_REPORTS_DATABASE.forEach(doc => {
                let occurrenceCount = 0;
                let isMatch = false;

                if (!keywordQuery) {
                    // Show all documents with highest topic count
                    const counts = Object.values(doc.keywords || {});
                    occurrenceCount = counts.length > 0 ? Math.max(...counts) : 10;
                    isMatch = true;
                } else {
                    // Search in explicit keywords map (case-insensitive exact & fuzzy match)
                    const normalizedQuery = keywordQuery.toLowerCase();
                    Object.keys(doc.keywords || {}).forEach(k => {
                        if (k.toLowerCase().includes(normalizedQuery) || normalizedQuery.includes(k.toLowerCase())) {
                            occurrenceCount = Math.max(occurrenceCount, doc.keywords[k]);
                            isMatch = true;
                        }
                    });

                    // Search in title/snippet/agency if not in explicit keywords
                    if (!isMatch && (doc.title.toLowerCase().includes(normalizedQuery) || doc.snippet.toLowerCase().includes(normalizedQuery))) {
                        occurrenceCount = Math.floor(Math.random() * 18) + 12; // Simulated occurrence
                        isMatch = true;
                    }
                }

                if (isMatch) {
                    matchedReports.push({
                        ...doc,
                        occ: occurrenceCount
                    });
                }
            });

            // ── CRITICAL: SORT IN DESCENDING ORDER BY MAXIMUM NUMBER OF OCCURRENCES ──
            matchedReports.sort((a, b) => b.occ - a.occ);

            if (countLabel) {
                countLabel.innerHTML = `Found <span class="font-extrabold text-[#0f172a]">${matchedReports.length} Indexed Reports</span> matching "<span class="text-emerald-700">${targetKey}</span>"`;
            }

            if (matchedReports.length === 0) {
                listContainer.innerHTML = `
                    <div class="py-12 text-center">
                        <div class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 mx-auto mb-3">
                            <i data-lucide="file-search" class="w-6 h-6"></i>
                        </div>
                        <h4 class="font-bold text-gray-700 text-sm">No Indexed Documents Found</h4>
                        <p class="text-xs text-gray-400 mt-1 max-w-sm mx-auto">Try searching for high-frequency terms like "Extraction", "Coal Seam", "Overburden", or "Drilling".</p>
                    </div>
                `;
                if (window.lucide) lucide.createIcons();
                return;
            }

            // Render Document Cards (Entire Card is Clickable)
            listContainer.innerHTML = matchedReports.map((report, idx) => {
                const maxOcc = matchedReports[0]?.occ || 1;
                const occPercent = Math.min(100, Math.round((report.occ / maxOcc) * 100));

                // Highlight keyword in snippet
                let snippetHtml = report.snippet;
                if (keywordQuery && keywordQuery.length > 2) {
                    const cleanQuery = keywordQuery.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
                    const regex = new RegExp(`(${cleanQuery})`, 'gi');
                    snippetHtml = snippetHtml.replace(regex, '<span class="bg-amber-100 text-amber-900 font-bold px-1 rounded">$1</span>');
                }

                return `
                    <div onclick="openFullReportViewer('${report.id}', '${targetKey}')" class="p-4.5 rounded-2xl bg-white border border-gray-200/90 hover:border-emerald-500 hover:shadow-md cursor-pointer transition-all duration-150 group">
                        
                        <!-- Top Meta & Occurrences Count -->
                        <div class="flex items-start justify-between gap-3 mb-2">
                            <div class="flex items-center gap-2 flex-wrap">
                                <span class="w-5 h-5 rounded-md bg-slate-900 text-white font-black text-[10px] flex items-center justify-center">#${idx + 1}</span>
                                <span class="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 text-[10px] font-bold uppercase tracking-wider">${report.agency}</span>
                                <span class="text-[11px] font-semibold text-gray-400">• ${report.date}</span>
                                <span class="text-[11px] font-semibold text-gray-400">• ${report.pages} Pages</span>
                            </div>
                            
                            <!-- Occurrence Frequency Badge -->
                            <div class="flex items-center gap-2 shrink-0">
                                <div class="text-right">
                                    <div class="text-xs font-black text-[#0f172a] group-hover:text-emerald-700 transition-colors flex items-center gap-1 justify-end">
                                        <i data-lucide="hash" class="w-3 h-3 text-emerald-600"></i> ${report.occ} <span class="text-[10px] font-semibold text-gray-400">Mentions</span>
                                    </div>
                                    <div class="w-20 h-1.5 bg-gray-100 rounded-full overflow-hidden mt-0.5">
                                        <div class="h-full bg-emerald-500 rounded-full" style="width:${occPercent}%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Report Title -->
                        <h4 class="font-extrabold text-[#0f172a] text-sm leading-snug group-hover:text-emerald-800 transition-colors mb-1.5">
                            ${report.title}
                        </h4>

                        <!-- Snippet with Keyword Context -->
                        <p class="text-xs font-medium text-gray-600 leading-relaxed bg-gray-50/80 p-2.5 rounded-xl border border-gray-100 mb-3">
                            ${snippetHtml}
                        </p>

                        <!-- Bottom Action & Tags -->
                        <div class="flex items-center justify-between pt-2 border-t border-gray-100 text-[11px]">
                            <div class="flex items-center gap-2">
                                <span class="text-gray-400 font-medium">Top Correlated Terms:</span>
                                <div class="flex gap-1 flex-wrap">
                                    ${Object.keys(report.keywords || {}).slice(0, 3).map(k => `
                                        <button onclick="event.stopPropagation(); setModalSearchKeyword('${k}')" class="px-2 py-0.5 bg-gray-100 hover:bg-emerald-50 hover:text-emerald-700 rounded text-[10px] font-bold text-gray-600 transition-colors">
                                            ${k} (${report.keywords[k]})
                                        </button>
                                    `).join('')}
                                </div>
                            </div>
                            <div class="flex items-center gap-1 font-bold text-xs text-emerald-700 group-hover:text-emerald-800 transition-colors">
                                <span>Open Full Report</span>
                                <i data-lucide="arrow-right" class="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform"></i>
                            </div>
                        </div>

                    </div>
                `;
            }).join('');

            if (window.lucide) lucide.createIcons();
        }

        // ── FULL REPORT DOCUMENT VIEWER ENGINE ──
        let currentFullViewingReportId = null;

        function openFullReportViewer(reportId, targetKeyword) {
            const report = INDEXED_REPORTS_DATABASE.find(r => r.id === reportId) || INDEXED_REPORTS_DATABASE[0];
            currentFullViewingReportId = report.id;
            
            const viewerModal = document.getElementById('full-report-viewer-modal');
            const viewerContent = document.getElementById('full-report-viewer-content');
            if (!viewerModal || !viewerContent) return;

            const focusKey = targetKeyword || activeModalSearchKeyword || 'Mining Operations';
            const mentionsCount = report.keywords[focusKey] || report.occ || 24;

            viewerContent.innerHTML = `
                <!-- Document Header Section -->
                <div class="border-b border-gray-200 pb-5">
                    <div class="flex items-center gap-2 flex-wrap mb-2">
                        <span class="px-2.5 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-md font-bold text-[10px] uppercase tracking-wider">${report.agency}</span>
                        <span class="px-2.5 py-0.5 bg-slate-100 text-slate-700 border border-slate-200 rounded-md font-bold text-[10px] uppercase tracking-wider">Doc ID: ${report.id}</span>
                        <span class="px-2.5 py-0.5 bg-sky-50 text-sky-800 border border-sky-200 rounded-md font-bold text-[10px] uppercase tracking-wider">${report.type}</span>
                        <span class="text-xs font-semibold text-gray-400">• Published: ${report.date}</span>
                        <span class="text-xs font-semibold text-gray-400">• ${report.pages} Pages</span>
                    </div>
                    <h2 class="text-xl sm:text-2xl font-black text-[#0f172a] leading-tight tracking-tight">
                        ${report.title}
                    </h2>
                    <p class="text-xs text-gray-500 font-medium mt-1">
                        Central Mine Planning &amp; Design Institute &bull; Coal India Limited Technical Repository
                    </p>
                </div>

                <!-- Active Focus Keyword & Frequency Callout Banner -->
                <div class="p-3.5 bg-emerald-50/70 border border-emerald-200/80 rounded-2xl flex items-center justify-between gap-3">
                    <div class="flex items-center gap-2.5">
                        <div class="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-black text-xs">
                            <i data-lucide="target" class="w-4 h-4"></i>
                        </div>
                        <div>
                            <div class="text-[10px] font-bold uppercase text-emerald-900 tracking-wider">Semantic Query Match</div>
                            <div class="text-xs font-bold text-emerald-950">
                                "${focusKey}" appears <strong class="text-emerald-700 font-black">${mentionsCount} times</strong> across this technical document
                            </div>
                        </div>
                    </div>
                    <span class="px-2.5 py-1 bg-white text-emerald-800 rounded-xl text-[11px] font-extrabold border border-emerald-200 shadow-2xs">
                        98.4% Confidence
                    </span>
                </div>

                <!-- Key Project Parameters Grid -->
                <div>
                    <h4 class="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2.5">1. Key Project Metadata</h4>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        <div class="p-3 rounded-xl bg-gray-50/80 border border-gray-200/70">
                            <div class="text-[10px] font-bold uppercase text-gray-400 tracking-wider">Coalfield Basin</div>
                            <div class="text-xs font-extrabold text-[#0f172a] mt-0.5">Jharia / Raniganj / Korba</div>
                        </div>
                        <div class="p-3 rounded-xl bg-gray-50/80 border border-gray-200/70">
                            <div class="text-[10px] font-bold uppercase text-gray-400 tracking-wider">Mining Method</div>
                            <div class="text-xs font-extrabold text-[#0f172a] mt-0.5">Mechanized Opencast</div>
                        </div>
                        <div class="p-3 rounded-xl bg-gray-50/80 border border-gray-200/70">
                            <div class="text-[10px] font-bold uppercase text-gray-400 tracking-wider">Stripping Ratio</div>
                            <div class="text-xs font-extrabold text-[#0f172a] mt-0.5">1 : 3.8 CuM/T</div>
                        </div>
                        <div class="p-3 rounded-xl bg-gray-50/80 border border-gray-200/70">
                            <div class="text-[10px] font-bold uppercase text-gray-400 tracking-wider">Reserve Status</div>
                            <div class="text-xs font-extrabold text-emerald-700 mt-0.5">Proved (ISP Norms)</div>
                        </div>
                    </div>
                </div>

                <!-- Stratigraphy & Seams Breakdown Table -->
                <div>
                    <h4 class="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2.5">2. Stratigraphy &amp; Coal Seam Analysis</h4>
                    <div class="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-2xs">
                        <table class="w-full text-left text-xs">
                            <thead class="bg-gray-50 border-b border-gray-200 text-gray-600 font-bold text-[11px]">
                                <tr>
                                    <th class="p-2.5 pl-3">Seam Horizon</th>
                                    <th class="p-2.5">Thickness (m)</th>
                                    <th class="p-2.5">Mean Depth (m)</th>
                                    <th class="p-2.5">Ash Content (%)</th>
                                    <th class="p-2.5">Gross Calorific Value</th>
                                    <th class="p-2.5 pr-3">Grade</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100 font-medium text-gray-800 text-[11px]">
                                <tr class="hover:bg-gray-50/80">
                                    <td class="p-2.5 pl-3 font-bold text-[#0f172a]">Seam X (Top)</td>
                                    <td class="p-2.5">6.40 m</td>
                                    <td class="p-2.5">112 m</td>
                                    <td class="p-2.5">18.4%</td>
                                    <td class="p-2.5 font-bold text-emerald-700">6,240 kcal/kg</td>
                                    <td class="p-2.5 pr-3"><span class="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded font-bold">G4</span></td>
                                </tr>
                                <tr class="hover:bg-gray-50/80">
                                    <td class="p-2.5 pl-3 font-bold text-[#0f172a]">Seam IX (Middle)</td>
                                    <td class="p-2.5">8.20 m</td>
                                    <td class="p-2.5">148 m</td>
                                    <td class="p-2.5">22.1%</td>
                                    <td class="p-2.5 font-bold text-emerald-700">5,820 kcal/kg</td>
                                    <td class="p-2.5 pr-3"><span class="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded font-bold">G6</span></td>
                                </tr>
                                <tr class="hover:bg-gray-50/80">
                                    <td class="p-2.5 pl-3 font-bold text-[#0f172a]">Seam VIII (Bottom)</td>
                                    <td class="p-2.5">4.80 m</td>
                                    <td class="p-2.5">194 m</td>
                                    <td class="p-2.5">26.5%</td>
                                    <td class="p-2.5 font-bold text-sky-700">5,310 kcal/kg</td>
                                    <td class="p-2.5 pr-3"><span class="px-2 py-0.5 bg-sky-50 text-sky-700 rounded font-bold">G8</span></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Full Report Technical Narrative Sections -->
                <div class="space-y-4">
                    <h4 class="text-xs font-bold uppercase tracking-wider text-gray-500">3. Technical Narrative &amp; Operational Observations</h4>
                    
                    <div class="p-4 bg-gray-50/80 rounded-2xl border border-gray-200 space-y-2">
                        <h5 class="font-bold text-[#0f172a] text-xs">Section 1: Overburden Removal &amp; Dragline Scheduling</h5>
                        <p class="text-xs text-gray-700 leading-relaxed font-medium">
                            The upper strata consists of medium to coarse-grained sandstone requiring systematic drilling and blasting with electronic delay detonators. Walking draglines handle primary overburden casting while shovel-dumper fleets evacuate interburden partings to prevent bench slope instability.
                        </p>
                    </div>

                    <div class="p-4 bg-gray-50/80 rounded-2xl border border-gray-200 space-y-2">
                        <h5 class="font-bold text-[#0f172a] text-xs">Section 2: Hydrogeological &amp; Environmental Clearance Compliance</h5>
                        <p class="text-xs text-gray-700 leading-relaxed font-medium">
                            Comprehensive piezometer monitoring networks established across 12 perimeter locations confirm groundwater table stability. Sump dewatering systems channel drainage through modular multi-tier settling ponds with zero untreated effluent discharge outside concession limits.
                        </p>
                    </div>

                    <div class="p-4 bg-gray-50/80 rounded-2xl border border-gray-200 space-y-2">
                        <h5 class="font-bold text-[#0f172a] text-xs">Section 3: Progressive Land Reclamation &amp; Mine Closure Status</h5>
                        <p class="text-xs text-gray-700 leading-relaxed font-medium">
                            Biological reclamation of decommissioned internal overburden dumps has restored over 145 hectares with native mixed afforestation. Satellite remote sensing validates canopy density growth complying with MoEFCC clearance stipulations.
                        </p>
                    </div>
                </div>

                <!-- Document Verification & Sign-off Footer -->
                <div class="p-4 bg-slate-50 rounded-2xl border border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
                    <div>
                        <div class="font-bold text-[#0f172a]">CMPDI Central Geo-Data Repository</div>
                        <div class="text-[11px] text-gray-400 font-medium">Verified by Regional Technical Advisory Committee (RTAC)</div>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="px-2.5 py-1 bg-emerald-100 text-emerald-900 rounded-lg font-bold text-[10px] uppercase">Digitally Authenticated</span>
                    </div>
                </div>
            `;

            viewerModal.classList.remove('hidden');
            if (window.lucide) lucide.createIcons();
        }

        function closeFullReportViewer() {
            const viewerModal = document.getElementById('full-report-viewer-modal');
            if (viewerModal) viewerModal.classList.add('hidden');
        }

        function backToReportsList() {
            closeFullReportViewer();
        }

        function handleReportViewerBackdropClick(e) {
            if (e.target.id === 'full-report-viewer-modal') {
                closeFullReportViewer();
            }
        }

        function mockDownloadReport() {
            const reportId = currentFullViewingReportId || 'CMPDI-REPORT-2024';
            alert(`Initiating download for technical document: [${reportId}.pdf]\n\nDocument authenticated by CMPDI Geological Archive.`);
        }

        function mockPrintReport() {
            window.print();
        }

        // Close modals on Escape key
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeFullReportViewer();
                closeTopicDocumentsModal();
            }
        });

        // Initialize when insights page is displayed or on window resize
        function initTopicIntelligence() {
            renderRadialWordCloud();
            selectTopicNode(currentSelectedTopicKey);
        }

        window.addEventListener('resize', () => {
            if (window.location.hash === '#insights' || document.getElementById('page-insights')?.classList.contains('active')) {
                renderRadialWordCloud();
            }
        });

        // Hook into handleRouting for #insights initialization
        setTimeout(() => {
            initTopicIntelligence();
        }, 300);
    </script>
'''

# Replace JS engine before </body>
js_marker = '<!-- ================= MINING TOPIC INTELLIGENCE'
js_start = html.find(js_marker)
if js_start != -1:
    body_pos = html.find('</body>', js_start)
    if body_pos != -1:
        html = html[:js_start] + radial_cloud_js + '\n' + html[body_pos:]
        print("Updated JavaScript engine with CMPDI brand color typographic renderer & Documents Explorer")
else:
    html = html.replace('</body>', f'{radial_cloud_js}\n</body>')
    print("Appended JavaScript engine before </body>")

with open(ORIGINAL_HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully updated original_render_index.html with Clickable Documents Explorer and Search!")
