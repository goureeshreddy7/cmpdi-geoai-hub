import os
import json

ORIGINAL_HTML_PATH = 'c:/Users/LENOVO/Downloads/final_cmpdi/cmpdi-geoai-hub-main/original_render_index.html'

with open(ORIGINAL_HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# Build the complete new page-insights section
new_insights_html = '''
                    <!-- ================= INSIGHTS VIEW (ADMIN) ================= -->
                    <div id="page-insights" class="page-view flex-col space-y-6">
                        <!-- Top Banner Header -->
                        <div class="bg-white rounded-[2rem] p-6 sm:p-8 border border-gray-200/80 card-elevate flex flex-col md:flex-row md:items-center justify-between gap-4">
                            <div>
                                <span class="px-3 py-1 bg-[#eefcce] text-[#111111] font-extrabold text-[11px] rounded-full inline-block mb-2 border border-[#d9f99d]">Semantic Intelligence</span>
                                <h2 class="text-2xl sm:text-3xl font-black text-[#111111] tracking-tight">Topic Insights & Semantic Map</h2>
                                <p class="text-gray-500 text-xs sm:text-sm font-medium mt-1">Explore high-frequency mining terms and discover relationships across indexed reports.</p>
                            </div>
                            <div class="flex items-center gap-3 shrink-0">
                                <div class="px-4 py-2.5 bg-gray-50 border border-gray-200/80 rounded-2xl text-center">
                                    <div class="text-[10px] text-gray-400 font-extrabold uppercase tracking-wider">Indexed Files</div>
                                    <div class="text-base font-black text-[#111111]">1,284</div>
                                </div>
                                <div class="px-4 py-2.5 bg-gray-50 border border-gray-200/80 rounded-2xl text-center">
                                    <div class="text-[10px] text-gray-400 font-extrabold uppercase tracking-wider">Confidence</div>
                                    <div class="text-base font-black text-[#84cc16]">98.2%</div>
                                </div>
                            </div>
                        </div>

                        <!-- Main Grid: Radial Word Map + Detail Studio -->
                        <div class="grid grid-cols-1 xl:grid-cols-12 gap-6">
                            
                            <!-- LEFT/CENTER CARD: Interactive Radial Word Map -->
                            <div class="xl:col-span-8 bg-white rounded-[2rem] border border-gray-200/80 card-elevate p-6 sm:p-7 flex flex-col justify-between">
                                
                                <!-- Card Header & Filters -->
                                <div>
                                    <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
                                        <div>
                                            <div class="flex items-center gap-2">
                                                <h3 class="font-extrabold text-[#111111] text-base sm:text-lg tracking-tight">Interactive Word Map</h3>
                                                <span class="px-2 py-0.5 bg-gray-100 text-gray-600 font-extrabold text-[9px] uppercase tracking-wider rounded-md border border-gray-200">Demo Dataset</span>
                                            </div>
                                            <p class="text-xs font-semibold text-gray-400 mt-0.5">Explore high-frequency mining terms and discover relationships across indexed reports.</p>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <span class="text-xs font-extrabold bg-[#eefcce] text-[#111111] px-3 py-1.5 rounded-xl flex items-center gap-1.5 border border-[#d9f99d]">
                                                <span class="w-2 h-2 rounded-full bg-[#84cc16] animate-pulse"></span> AI Live
                                            </span>
                                        </div>
                                    </div>

                                    <!-- Category Filter Bar -->
                                    <div class="flex items-center gap-1.5 sm:gap-2 overflow-x-auto custom-scrollbar pb-2 pt-1 mb-3">
                                        <button onclick="filterTopicCategory('all')" id="topic-filter-all" class="topic-cat-btn active-cat px-3.5 py-1.5 rounded-xl text-xs font-black transition-all bg-[#111111] text-[#a3e635] shadow-sm">All Documents</button>
                                        <button onclick="filterTopicCategory('geological')" id="topic-filter-geological" class="topic-cat-btn px-3 py-1.5 rounded-xl text-xs font-bold transition-all bg-gray-100 hover:bg-sky-50 hover:text-sky-800 text-gray-600 border border-transparent hover:border-sky-200">Geological</button>
                                        <button onclick="filterTopicCategory('production')" id="topic-filter-production" class="topic-cat-btn px-3 py-1.5 rounded-xl text-xs font-bold transition-all bg-gray-100 hover:bg-emerald-50 hover:text-emerald-800 text-gray-600 border border-transparent hover:border-emerald-200">Production</button>
                                        <button onclick="filterTopicCategory('environmental')" id="topic-filter-environmental" class="topic-cat-btn px-3 py-1.5 rounded-xl text-xs font-bold transition-all bg-gray-100 hover:bg-amber-50 hover:text-amber-800 text-gray-600 border border-transparent hover:border-amber-200">Environmental</button>
                                        <button onclick="filterTopicCategory('safety')" id="topic-filter-safety" class="topic-cat-btn px-3 py-1.5 rounded-xl text-xs font-bold transition-all bg-gray-100 hover:bg-rose-50 hover:text-rose-800 text-gray-600 border border-transparent hover:border-rose-200">Safety &amp; Operations</button>
                                        <button onclick="filterTopicCategory('exploration')" id="topic-filter-exploration" class="topic-cat-btn px-3 py-1.5 rounded-xl text-xs font-bold transition-all bg-gray-100 hover:bg-cyan-50 hover:text-cyan-800 text-gray-600 border border-transparent hover:border-cyan-200">Exploration</button>
                                    </div>
                                </div>

                                <!-- Radial Word Cloud Canvas Container -->
                                <div id="radial-cloud-container" class="relative w-full h-[430px] sm:h-[480px] rounded-2xl bg-gradient-to-b from-gray-50/90 to-gray-100/40 border border-gray-200/80 overflow-hidden flex items-center justify-center select-none my-2 shadow-inner">
                                    
                                    <!-- Radial SVG Orbital Grid Background -->
                                    <svg class="absolute inset-0 w-full h-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
                                        <defs>
                                            <radialGradient id="orbitGlow" cx="50%" cy="50%" r="50%">
                                                <stop offset="0%" stop-color="#a3e635" stop-opacity="0.12"/>
                                                <stop offset="60%" stop-color="#38bdf8" stop-opacity="0.04"/>
                                                <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
                                            </radialGradient>
                                        </defs>
                                        
                                        <!-- Ambient background glow -->
                                        <rect width="100%" height="100%" fill="url(#orbitGlow)" />
                                        
                                        <!-- Concentric Orbits centered at (50%, 50%) -->
                                        <g transform="translate(0, 0)">
                                            <circle cx="50%" cy="50%" r="55" fill="none" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="3,3" opacity="0.65" />
                                            <circle cx="50%" cy="50%" r="115" fill="none" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="4,4" opacity="0.6" />
                                            <circle cx="50%" cy="50%" r="175" fill="none" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="5,5" opacity="0.5" />
                                            <circle cx="50%" cy="50%" r="225" fill="none" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="6,6" opacity="0.4" />
                                            
                                            <!-- Crosshairs subtle -->
                                            <line x1="50%" y1="15%" x2="50%" y2="85%" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4" opacity="0.5" />
                                            <line x1="15%" y1="50%" x2="85%" y2="50%" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="4,4" opacity="0.5" />
                                        </g>

                                        <!-- Dynamic Radial Connector Lines -->
                                        <g id="radial-connector-lines" opacity="0.45"></g>
                                    </svg>

                                    <!-- Radial Word Nodes rendered dynamically by JS -->
                                    <div id="radial-word-nodes-layer" class="absolute inset-0 w-full h-full pointer-events-auto"></div>

                                    <!-- Floating Tooltip -->
                                    <div id="radial-topic-tooltip" class="absolute z-30 pointer-events-none opacity-0 transition-opacity duration-200 bg-[#111111] text-white p-3 rounded-2xl shadow-xl border border-gray-800 text-xs transform -translate-x-1/2 -translate-y-full mb-3 min-w-[170px]">
                                        <div class="flex items-center justify-between border-b border-gray-800 pb-1.5 mb-1.5">
                                            <h5 id="r-tooltip-title" class="font-extrabold text-[#a3e635] text-xs">Topic</h5>
                                            <span id="r-tooltip-cat" class="text-[9px] uppercase tracking-wider text-gray-400 font-black">Category</span>
                                        </div>
                                        <div class="space-y-1 text-[11px] font-semibold text-gray-300">
                                            <div class="flex justify-between"><span>Occurrences:</span> <strong id="r-tooltip-occ" class="text-white">486</strong></div>
                                            <div class="flex justify-between"><span>Relevance:</span> <strong id="r-tooltip-rel" class="text-[#a3e635]">94.2%</strong></div>
                                            <div class="flex justify-between"><span>Documents:</span> <strong id="r-tooltip-docs" class="text-white">173</strong></div>
                                        </div>
                                    </div>

                                </div>

                                <!-- Card Footer & Radial Legend -->
                                <div class="pt-3 border-t border-gray-100 flex flex-wrap items-center justify-between gap-3 text-[11px] font-bold text-gray-400">
                                    <div class="flex items-center gap-4 flex-wrap">
                                        <span class="tracking-wider uppercase font-black text-gray-500">Legend:</span>
                                        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Production</span>
                                        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-cyan-500"></span> Geological</span>
                                        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Environmental</span>
                                        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span> Safety</span>
                                    </div>
                                    <div class="tracking-wider uppercase font-extrabold text-[10px] text-gray-400">
                                        SIZE = OCCURRENCE &bull; DISTANCE = RELEVANCE &bull; COLOR = CATEGORY
                                    </div>
                                </div>

                            </div>


                            <!-- RIGHT CARD: Topic Detail Panel -->
                            <div class="xl:col-span-4 bg-white rounded-[2rem] border border-gray-200/80 card-elevate p-6 sm:p-7 flex flex-col justify-between" id="topic-detail-card">
                                
                                <div class="space-y-5">
                                    <!-- Detail Header -->
                                    <div class="border-b border-gray-100 pb-4">
                                        <div class="flex items-center justify-between mb-1.5">
                                            <span class="text-[10px] font-black uppercase tracking-wider text-gray-400">TOPIC DETAIL</span>
                                            <span id="detail-topic-badge" class="px-2.5 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-full font-extrabold text-[10px] uppercase">Mining Operations</span>
                                        </div>
                                        <div class="flex items-center justify-between">
                                            <h3 id="detail-topic-name" class="text-2xl font-black text-[#111111] tracking-tight">Overburden</h3>
                                            <button onclick="focusTopicInCloud(currentSelectedTopicKey)" title="Focus in Radial Map" class="w-7 h-7 rounded-xl bg-gray-100 hover:bg-[#eefcce] flex items-center justify-center text-gray-600 hover:text-[#111111] transition-all">
                                                <i data-lucide="crosshair" class="w-4 h-4"></i>
                                            </button>
                                        </div>
                                    </div>

                                    <!-- Key Metrics Grid -->
                                    <div class="grid grid-cols-2 gap-3">
                                        <div class="p-3.5 rounded-2xl bg-gray-50 border border-gray-200/70">
                                            <div class="text-[10px] font-extrabold uppercase text-gray-400 tracking-wider">Occurrences</div>
                                            <div id="detail-topic-occ" class="text-lg font-black text-[#111111] mt-0.5">486</div>
                                        </div>
                                        <div class="p-3.5 rounded-2xl bg-gray-50 border border-gray-200/70">
                                            <div class="text-[10px] font-extrabold uppercase text-gray-400 tracking-wider">Documents</div>
                                            <div id="detail-topic-docs" class="text-lg font-black text-[#111111] mt-0.5">173</div>
                                        </div>
                                        <div class="p-3.5 rounded-2xl bg-[#eefcce]/50 border border-[#d9f99d]">
                                            <div class="text-[10px] font-extrabold uppercase text-gray-600 tracking-wider">Relevance</div>
                                            <div id="detail-topic-rel" class="text-lg font-black text-[#111111] mt-0.5">94.2%</div>
                                        </div>
                                        <div class="p-3.5 rounded-2xl bg-gray-50 border border-gray-200/70">
                                            <div class="text-[10px] font-extrabold uppercase text-gray-400 tracking-wider">Category</div>
                                            <div id="detail-topic-cat" class="text-xs font-black text-gray-800 mt-1 truncate">Mining Operations</div>
                                        </div>
                                    </div>

                                    <!-- Trend of Occurrence Chart -->
                                    <div>
                                        <div class="flex items-center justify-between mb-2">
                                            <h4 class="text-xs font-black uppercase tracking-wider text-gray-700">Trend of Occurrence</h4>
                                            <!-- Time Range Filters -->
                                            <div class="flex items-center gap-1 bg-gray-100 p-0.5 rounded-lg text-[10px] font-extrabold text-gray-500">
                                                <button onclick="setTrendTimeRange('1Y')" id="trend-range-1Y" class="trend-btn px-2 py-0.5 rounded-md hover:text-[#111111]">1Y</button>
                                                <button onclick="setTrendTimeRange('3Y')" id="trend-range-3Y" class="trend-btn active-range px-2 py-0.5 rounded-md bg-white text-[#111111] shadow-2xs">3Y</button>
                                                <button onclick="setTrendTimeRange('5Y')" id="trend-range-5Y" class="trend-btn px-2 py-0.5 rounded-md hover:text-[#111111]">5Y</button>
                                                <button onclick="setTrendTimeRange('ALL')" id="trend-range-ALL" class="trend-btn px-2 py-0.5 rounded-md hover:text-[#111111]">ALL</button>
                                            </div>
                                        </div>
                                        <div class="h-28 w-full bg-gray-50 rounded-2xl p-2 border border-gray-200/60 relative">
                                            <canvas id="topicTrendCanvas" class="w-full h-full"></canvas>
                                        </div>
                                    </div>

                                    <!-- Related Topics -->
                                    <div>
                                        <h4 class="text-xs font-black uppercase tracking-wider text-gray-700 mb-2">Related Topics</h4>
                                        <div id="detail-related-chips" class="flex flex-wrap gap-1.5">
                                            <!-- Related chips rendered dynamically -->
                                        </div>
                                    </div>

                                    <!-- AI Insight -->
                                    <div class="p-3.5 bg-[#eefcce]/60 rounded-2xl border border-[#d9f99d]">
                                        <div class="flex items-center gap-1.5 text-[10px] font-black uppercase text-[#111111] tracking-wider mb-1">
                                            <i data-lucide="sparkles" class="w-3.5 h-3.5 text-[#84cc16]"></i> AI Insight
                                        </div>
                                        <p id="detail-ai-insight" class="text-xs font-medium text-gray-800 leading-relaxed">
                                            "Overburden is frequently associated with stripping ratio, excavation and production planning across the analyzed reports."
                                        </p>
                                    </div>

                                    <!-- Document Context -->
                                    <div class="p-3.5 bg-gray-50 rounded-2xl border border-gray-200/70 space-y-2 text-xs">
                                        <div class="flex justify-between items-center">
                                            <span class="text-gray-500 font-semibold">Most Common In</span>
                                            <strong id="detail-context-common" class="text-[#111111] font-bold">Production Reports</strong>
                                        </div>
                                        <div class="flex justify-between items-center pt-1.5 border-t border-gray-200/60">
                                            <span class="text-gray-500 font-semibold">Top Source</span>
                                            <strong id="detail-context-source" class="text-[#111111] font-bold">Mine Performance Reports</strong>
                                        </div>
                                    </div>
                                </div>

                                <!-- Action Button: Query in Assistant / Load in Reports -->
                                <div class="mt-5 pt-3 border-t border-gray-100 flex gap-2">
                                    <button onclick="queryTopicInAssistant(currentSelectedTopicKey)" class="flex-1 py-3 bg-[#111111] text-[#a3e635] rounded-xl font-extrabold text-xs shadow-md hover:bg-black hover:scale-[1.01] active:scale-95 transition-all flex items-center justify-center gap-1.5">
                                        <i data-lucide="bot" class="w-3.5 h-3.5"></i> <span>Query GeoAI</span>
                                    </button>
                                    <button onclick="selectKeyword(currentSelectedTopicKey)" class="py-3 px-4 bg-[#a3e635] text-[#111111] rounded-xl font-extrabold text-xs shadow-md hover:bg-[#84cc16] hover:scale-[1.01] active:scale-95 transition-all flex items-center justify-center gap-1.5" title="Load into Report Builder">
                                        <i data-lucide="file-text" class="w-3.5 h-3.5"></i> <span>Build Report</span>
                                    </button>
                                </div>

                            </div>

                        </div>

                        <!-- Cluster Breakdown Row Below -->
                        <div class="bg-white rounded-[2rem] p-6 sm:p-8 border border-gray-200/80 card-elevate">
                            <div class="flex items-center justify-between mb-4">
                                <div>
                                    <h3 class="font-extrabold text-[#111111] text-base tracking-tight">Enterprise Cluster Breakdown</h3>
                                    <p class="text-xs font-semibold text-gray-400">Semantic density clusters analyzed across 1,284 technical repositories</p>
                                </div>
                                <span class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-600"><i data-lucide="layers" class="w-4 h-4"></i></span>
                            </div>
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div onclick="selectTopicNode('Extraction')" class="p-4 rounded-2xl bg-gray-50 hover:bg-[#eefcce]/60 transition-all cursor-pointer border border-gray-200/70 hover:scale-[1.02]">
                                    <div class="flex justify-between items-center mb-1"><span class="font-extrabold text-xs text-[#111111]">Extraction &amp; Output</span><span class="text-[11px] font-black text-[#84cc16]">42%</span></div>
                                    <p class="text-[11px] text-gray-500 font-medium">High correlation with SECL &amp; MCL production logs.</p>
                                </div>
                                <div onclick="selectTopicNode('Reclamation')" class="p-4 rounded-2xl bg-gray-50 hover:bg-[#ffebd6]/60 transition-all cursor-pointer border border-gray-200/70 hover:scale-[1.02]">
                                    <div class="flex justify-between items-center mb-1"><span class="font-extrabold text-xs text-[#111111]">Environmental &amp; Clearances</span><span class="text-[11px] font-black text-[#fb923c]">28%</span></div>
                                    <p class="text-[11px] text-gray-500 font-medium">Environmental impact and NBWL forest clearance audits.</p>
                                </div>
                                <div onclick="selectTopicNode('Geological Reserve')" class="p-4 rounded-2xl bg-gray-50 hover:bg-sky-50 transition-all cursor-pointer border border-gray-200/70 hover:scale-[1.02]">
                                    <div class="flex justify-between items-center mb-1"><span class="font-extrabold text-xs text-[#111111]">Geological Reserves &amp; Logs</span><span class="text-[11px] font-black text-sky-700">30%</span></div>
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
    print("Replaced #page-insights with upgraded Radial Word Map & Topic Detail Panel")
else:
    print("ERROR: Could not locate #page-insights boundaries!")

# Add the JavaScript data structures and controllers for Radial Word Cloud
radial_cloud_js = '''
    <!-- ================= MINING TOPIC INTELLIGENCE RADIAL CLOUD ENGINE ================= -->
    <script>
        // ── TOPIC DATA REPOSITORY (24 Mining Terms) ──
        const MINING_TOPICS = {
            'Extraction': {
                name: 'Extraction',
                category: 'production',
                catLabel: 'Mining Operations',
                occ: 720,
                docs: 290,
                rel: 99.0,
                ring: 0, // center
                angle: 0,
                related: ['Overburden', 'ROM Production', 'Stripping Ratio', 'Shovel-Dumper', 'Coal Seam'],
                aiInsight: 'Extraction represents the core operational metric with direct correlation to dragline utilization and monthly subsidiary dispatch targets.',
                mostCommonIn: 'Production Reports',
                topSource: 'Monthly Mining Dispatch Summaries',
                trend: [48, 55, 62, 70, 85, 92, 110, 125, 140, 155, 170, 195]
            },
            'Overburden': {
                name: 'Overburden',
                category: 'production',
                catLabel: 'Mining Operations',
                occ: 486,
                docs: 173,
                rel: 94.2,
                ring: 1,
                angle: 35,
                related: ['Stripping Ratio', 'Dragline', 'Extraction', 'Shovel-Dumper', 'Seam Depth'],
                aiInsight: 'Overburden is frequently associated with stripping ratio, excavation and production planning across the analyzed reports.',
                mostCommonIn: 'Production Reports',
                topSource: 'Mine Performance Reports',
                trend: [30, 34, 42, 45, 58, 65, 72, 80, 88, 96, 112, 128]
            },
            'Coal Seam': {
                name: 'Coal Seam',
                category: 'geological',
                catLabel: 'Geological Structure',
                occ: 612,
                docs: 248,
                rel: 98.0,
                ring: 1,
                angle: 155,
                related: ['Seam Thickness', 'Seam Depth', 'Geological Reserve', 'Borehole', 'Ash Content'],
                aiInsight: 'Coal Seam lithology descriptions dictate stripping geometry and reserve extractability across the Jharia and Raniganj basins.',
                mostCommonIn: 'Geological Memoirs',
                topSource: 'CMPDI Exploration Bulletins',
                trend: [40, 48, 52, 60, 68, 75, 88, 95, 105, 118, 130, 145]
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
                related: ['Coal Seam', 'Recovery Factor', 'Borehole', 'Seam Thickness', 'Exploration'],
                aiInsight: 'Reserve classifications (Proved, Indicated, Inferred) strictly follow ISP code guidelines in CMPDI documentation.',
                mostCommonIn: 'Reserve Estimates',
                topSource: 'National Coal Inventory Reports',
                trend: [25, 30, 35, 42, 48, 56, 62, 70, 78, 85, 94, 105]
            },
            'Stripping Ratio': {
                name: 'Stripping Ratio',
                category: 'production',
                catLabel: 'Mine Economics',
                occ: 395,
                docs: 148,
                rel: 90.5,
                ring: 1,
                angle: 285,
                related: ['Overburden', 'Extraction', 'Dragline', 'Pit Geometry', 'Shovel-Dumper'],
                aiInsight: 'Stripping ratio benchmarks directly govern opencast economic cut-off limits across SECL, MCL, and CCL concessions.',
                mostCommonIn: 'Feasibility Reports',
                topSource: 'Annual Mine Cost Audits',
                trend: [22, 28, 33, 39, 44, 52, 60, 67, 74, 82, 90, 102]
            },
            'ROM Production': {
                name: 'ROM Production',
                category: 'production',
                catLabel: 'Production Metrics',
                occ: 410,
                docs: 155,
                rel: 91.0,
                ring: 1,
                angle: 95,
                related: ['Extraction', 'Beneficiation', 'Calorific Value', 'Recovery Factor', 'Overburden'],
                aiInsight: 'Run-of-Mine (ROM) extraction figures correlate with washery feed inputs and rake dispatch schedules.',
                mostCommonIn: 'Monthly Production Logs',
                topSource: 'CIL Consolidated Output Logs',
                trend: [28, 32, 38, 45, 50, 58, 65, 73, 80, 89, 98, 110]
            },
            'Seam Thickness': {
                name: 'Seam Thickness',
                category: 'geological',
                catLabel: 'Stratigraphy',
                occ: 385,
                docs: 142,
                rel: 89.0,
                ring: 2,
                angle: 180,
                related: ['Coal Seam', 'Seam Depth', 'Borehole', 'Geological Reserve'],
                aiInsight: 'Seam Thickness variability determines continuous miner vs. longwall applicability in underground horizons.',
                mostCommonIn: 'Borehole Logs',
                topSource: 'Exploration Drilling Summaries',
                trend: [20, 24, 29, 35, 40, 47, 54, 60, 68, 75, 84, 95]
            },
            'Seam Depth': {
                name: 'Seam Depth',
                category: 'geological',
                catLabel: 'Stratigraphy',
                occ: 340,
                docs: 130,
                rel: 86.5,
                ring: 2,
                angle: 125,
                related: ['Coal Seam', 'Overburden', 'Borehole', 'Pit Geometry'],
                aiInsight: 'Depth contour mapping delineates the transition boundary from opencast extraction to highwall or underground mining.',
                mostCommonIn: 'Geological Folios',
                topSource: 'CMPDI Regional Basins',
                trend: [18, 22, 26, 31, 36, 42, 48, 55, 62, 70, 78, 88]
            },
            'Borehole': {
                name: 'Borehole',
                category: 'exploration',
                catLabel: 'Exploration Survey',
                occ: 310,
                docs: 118,
                rel: 84.0,
                ring: 2,
                angle: 245,
                related: ['Exploration', 'Coal Seam', 'Ash Content', 'Geological Reserve'],
                aiInsight: 'Core drill logs establish proximate analysis values, seam splits, and structural fault boundaries.',
                mostCommonIn: 'Drilling Archives',
                topSource: 'Geological Survey Documentation',
                trend: [15, 19, 23, 28, 33, 38, 44, 50, 56, 64, 72, 82]
            },
            'Slope Stability': {
                name: 'Slope Stability',
                category: 'safety',
                catLabel: 'Safety & Geotechnical',
                occ: 360,
                docs: 138,
                rel: 88.0,
                ring: 2,
                angle: 10,
                related: ['Pit Geometry', 'Groundwater', 'Overburden', 'Drilling & Blasting'],
                aiInsight: 'Radar slope monitoring records in deep opencast benches ensure safety against bench failures and dump slides.',
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
                angle: 65,
                related: ['Slope Stability', 'Reclamation', 'Mine Ventilation', 'Subsidence'],
                aiInsight: 'Aquifer dewatering and hydro-geological modeling prevent pit inundation and preserve regional water tables.',
                mostCommonIn: 'Environmental Clearances',
                topSource: 'MoEFCC Impact Submissions',
                trend: [17, 21, 26, 32, 38, 44, 51, 58, 66, 74, 83, 94]
            },
            'Drilling & Blasting': {
                name: 'Drilling & Blasting',
                category: 'safety',
                catLabel: 'Mine Operations',
                occ: 330,
                docs: 125,
                rel: 85.0,
                ring: 2,
                angle: 315,
                related: ['Overburden', 'Shovel-Dumper', 'Slope Stability', 'Extraction'],
                aiInsight: 'Controlled blast designs with electronic detonators reduce ground vibration and optimize fragmentation.',
                mostCommonIn: 'Operational Logs',
                topSource: 'Mine Safety & Blasting Audits',
                trend: [16, 20, 24, 29, 34, 40, 47, 54, 61, 69, 78, 89]
            },
            'Shovel-Dumper': {
                name: 'Shovel-Dumper',
                category: 'production',
                catLabel: 'Heavy Earth Moving Machinery',
                occ: 320,
                docs: 122,
                rel: 85.0,
                ring: 2,
                angle: 345,
                related: ['Overburden', 'Extraction', 'Stripping Ratio', 'Dragline'],
                aiInsight: 'HEMM fleet availability and matching ratios form the backbone of overburden stripping in mechanised pits.',
                mostCommonIn: 'Equipment Logs',
                topSource: 'HEMM Performance Reviews',
                trend: [14, 18, 22, 27, 32, 38, 45, 52, 59, 67, 76, 86]
            },
            'Dragline': {
                name: 'Dragline',
                category: 'production',
                catLabel: 'Heavy Earth Moving Machinery',
                occ: 280,
                docs: 105,
                rel: 80.0,
                ring: 3,
                angle: 48,
                related: ['Overburden', 'Stripping Ratio', 'Shovel-Dumper', 'Extraction'],
                aiInsight: 'High-capacity walking draglines handle deep side-casting in mega-opencast horizons (e.g., Gevra, Nigahi).',
                mostCommonIn: 'Heavy Equipment Logs',
                topSource: 'Dragline Utilization Ledgers',
                trend: [12, 15, 19, 23, 27, 32, 38, 44, 51, 58, 66, 75]
            },
            'Ash Content': {
                name: 'Ash Content',
                category: 'safety',
                catLabel: 'Coal Quality & Chemistry',
                occ: 270,
                docs: 104,
                rel: 78.5,
                ring: 3,
                angle: 195,
                related: ['Calorific Value', 'Beneficiation', 'Coal Seam', 'Borehole'],
                aiInsight: 'Non-coking coal grading in India (G1 to G17) is determined by gross calorific value inverse to moisture/ash content.',
                mostCommonIn: 'Coal Quality Certificates',
                topSource: 'CMPDI Central Quality Lab',
                trend: [11, 14, 18, 22, 26, 31, 36, 42, 49, 56, 64, 73]
            },
            'Calorific Value': {
                name: 'Calorific Value',
                category: 'safety',
                catLabel: 'Coal Quality & Chemistry',
                occ: 265,
                docs: 100,
                rel: 77.8,
                ring: 3,
                angle: 228,
                related: ['Ash Content', 'Beneficiation', 'ROM Production', 'Coal Seam'],
                aiInsight: 'GCV testing results ensure supply agreements with NTPC and independent power producers are fulfilled accurately.',
                mostCommonIn: 'Commercial Coal Dispatches',
                topSource: 'Third-Party Sampling Audits',
                trend: [10, 13, 17, 21, 25, 30, 35, 41, 47, 54, 62, 71]
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
                related: ['Slope Stability', 'Groundwater', 'Mine Closure', 'Extraction'],
                aiInsight: 'Methane drainage and continuous airflow velocity monitoring safeguard gassy underground workings.',
                mostCommonIn: 'Safety Audits',
                topSource: 'DGMS Inspection Reports',
                trend: [13, 16, 20, 24, 29, 34, 40, 47, 54, 61, 70, 80]
            },
            'Pit Geometry': {
                name: 'Pit Geometry',
                category: 'safety',
                catLabel: 'Mine Design',
                occ: 250,
                docs: 95,
                rel: 76.0,
                ring: 3,
                angle: 300,
                related: ['Slope Stability', 'Stripping Ratio', 'Seam Depth', 'Overburden'],
                aiInsight: 'Bench widths, floor inclinations, and haul road gradients are optimized for 240T dumper safe haulage.',
                mostCommonIn: 'Mine Planning Reports',
                topSource: 'CMPDI Mine Design Directorate',
                trend: [9, 12, 15, 19, 23, 28, 33, 39, 45, 52, 60, 68]
            },
            'Exploration': {
                name: 'Exploration',
                category: 'exploration',
                catLabel: 'Geological Exploration',
                occ: 295,
                docs: 110,
                rel: 81.0,
                ring: 3,
                angle: 165,
                related: ['Borehole', 'Geological Reserve', 'Coal Seam', 'Recovery Factor'],
                aiInsight: 'Detailed 2D/3D seismic and non-coring exploration programs validate greenfield coal block allocations.',
                mostCommonIn: 'Geological Reports',
                topSource: 'National Mineral Exploration Trust',
                trend: [14, 17, 21, 26, 31, 36, 42, 49, 56, 64, 73, 83]
            },
            'Beneficiation': {
                name: 'Beneficiation',
                category: 'production',
                catLabel: 'Coal Processing',
                occ: 215,
                docs: 85,
                rel: 74.0,
                ring: 3,
                angle: 80,
                related: ['Ash Content', 'Calorific Value', 'ROM Production', 'Extraction'],
                aiInsight: 'Heavy media cyclone and dry beneficiation plants yield clean coal fractions for steel and power industries.',
                mostCommonIn: 'Washery Yield Reports',
                topSource: 'Coal Washery Operations',
                trend: [8, 10, 13, 16, 20, 24, 28, 33, 38, 44, 51, 58]
            },
            'Recovery Factor': {
                name: 'Recovery Factor',
                category: 'production',
                catLabel: 'Resource Efficiency',
                occ: 240,
                docs: 92,
                rel: 78.0,
                ring: 3,
                angle: 110,
                related: ['Geological Reserve', 'Extraction', 'Coal Seam', 'ROM Production'],
                aiInsight: 'Opencast extraction recovers upwards of 90% of in-situ reserves compared to 55-65% in bord-and-pillar workings.',
                mostCommonIn: 'Resource Audit Reports',
                topSource: 'CIL Conservation Commendations',
                trend: [9, 11, 14, 18, 22, 27, 32, 38, 44, 50, 57, 65]
            },
            'Subsidence': {
                name: 'Subsidence',
                category: 'environmental',
                catLabel: 'Geotechnical & Environment',
                occ: 260,
                docs: 98,
                rel: 77.0,
                ring: 3,
                angle: 140,
                related: ['Reclamation', 'Groundwater', 'Mine Closure', 'Seam Depth'],
                aiInsight: 'Surface subsidence monitoring above depillared panels prevents structural damage to civil infrastructure.',
                mostCommonIn: 'Environmental Monitoring',
                topSource: 'Mine Safety & Strata Records',
                trend: [10, 13, 16, 20, 24, 29, 34, 40, 46, 53, 61, 70]
            },
            'Reclamation': {
                name: 'Reclamation',
                category: 'environmental',
                catLabel: 'Environmental Restoration',
                occ: 275,
                docs: 102,
                rel: 79.0,
                ring: 3,
                angle: 25,
                related: ['Mine Closure', 'Groundwater', 'Subsidence', 'Overburden'],
                aiInsight: 'Technical and biological reclamation transforms overburden dumps into dense afforested eco-parks.',
                mostCommonIn: 'Sustainability Reports',
                topSource: 'CMPDI Remote Sensing Land Restorations',
                trend: [11, 14, 18, 22, 27, 32, 38, 44, 51, 58, 66, 75]
            },
            'Mine Closure': {
                name: 'Mine Closure',
                category: 'environmental',
                catLabel: 'Mine Life Cycle',
                occ: 210,
                docs: 80,
                rel: 72.0,
                ring: 3,
                angle: 330,
                related: ['Reclamation', 'Groundwater', 'Mine Ventilation', 'Subsidence'],
                aiInsight: 'Progressive and final mine closure plans outline water body creation, fencing, and post-mining land usage.',
                mostCommonIn: 'Progressive Closure Plans',
                topSource: 'Ministry of Coal Approvals',
                trend: [7, 9, 12, 15, 18, 22, 26, 31, 36, 42, 48, 55]
            }
        };

        let currentSelectedTopicKey = 'Overburden';
        let currentTopicCategoryFilter = 'all';
        let currentTrendTimeRange = '3Y';
        let topicTrendChartInstance = null;

        // Color Schemes per category
        const TOPIC_COLORS = {
            'production': {
                bg: 'bg-emerald-50/95',
                text: 'text-emerald-950',
                border: 'border-emerald-300',
                badgeBg: 'bg-emerald-50',
                badgeText: 'text-emerald-800',
                badgeBorder: 'border-emerald-200',
                stroke: '#10b981',
                activeRing: 'ring-emerald-400',
                accentHex: '#059669'
            },
            'geological': {
                bg: 'bg-sky-50/95',
                text: 'text-sky-950',
                border: 'border-sky-300',
                badgeBg: 'bg-sky-50',
                badgeText: 'text-sky-800',
                badgeBorder: 'border-sky-200',
                stroke: '#0ea5e9',
                activeRing: 'ring-sky-400',
                accentHex: '#0284c7'
            },
            'environmental': {
                bg: 'bg-amber-50/95',
                text: 'text-amber-950',
                border: 'border-amber-300',
                badgeBg: 'bg-amber-50',
                badgeText: 'text-amber-800',
                badgeBorder: 'border-amber-200',
                stroke: '#f59e0b',
                activeRing: 'ring-amber-400',
                accentHex: '#d97706'
            },
            'safety': {
                bg: 'bg-rose-50/95',
                text: 'text-rose-950',
                border: 'border-rose-300',
                badgeBg: 'bg-rose-50',
                badgeText: 'text-rose-800',
                badgeBorder: 'border-rose-200',
                stroke: '#f43f5e',
                activeRing: 'ring-rose-400',
                accentHex: '#e11d48'
            },
            'exploration': {
                bg: 'bg-cyan-50/95',
                text: 'text-cyan-950',
                border: 'border-cyan-300',
                badgeBg: 'bg-cyan-50',
                badgeText: 'text-cyan-800',
                badgeBorder: 'border-cyan-200',
                stroke: '#06b6d4',
                activeRing: 'ring-cyan-400',
                accentHex: '#0891b2'
            }
        };

        // Render the Radial Word Cloud
        function renderRadialWordCloud() {
            const container = document.getElementById('radial-word-nodes-layer');
            const linesGroup = document.getElementById('radial-connector-lines');
            if (!container) return;

            container.innerHTML = '';
            if (linesGroup) linesGroup.innerHTML = '';

            const rect = container.getBoundingClientRect();
            const width = rect.width || 600;
            const height = rect.height || 440;
            const centerX = width / 2;
            const centerY = height / 2;

            // Radii for concentric rings (proportional to container)
            const ringRadii = {
                0: 0,
                1: Math.min(width, height) * 0.22,
                2: Math.min(width, height) * 0.35,
                3: Math.min(width, height) * 0.44
            };

            const selectedData = MINING_TOPICS[currentSelectedTopicKey];

            Object.keys(MINING_TOPICS).forEach(key => {
                const item = MINING_TOPICS[key];
                const isMatchingCategory = currentTopicCategoryFilter === 'all' || 
                                           item.category === currentTopicCategoryFilter ||
                                           (currentTopicCategoryFilter === 'exploration' && (item.category === 'exploration' || key === 'Borehole' || key === 'Exploration'));

                const isSelected = key === currentSelectedTopicKey;
                const isRelated = selectedData && selectedData.related && selectedData.related.includes(key);

                // Compute polar position
                const r = ringRadii[item.ring];
                const angleRad = (item.angle * Math.PI) / 180;
                const posX = centerX + r * Math.cos(angleRad);
                const posY = centerY + r * Math.sin(angleRad);

                // Calculate font size & padding from occurrence
                let fontSize = 'text-xs';
                let padding = 'px-3 py-1.5';
                let weight = 'font-bold';

                if (item.occ >= 600) {
                    fontSize = 'text-sm sm:text-base';
                    padding = 'px-4 py-2';
                    weight = 'font-black';
                } else if (item.occ >= 400) {
                    fontSize = 'text-xs sm:text-sm';
                    padding = 'px-3.5 py-1.5';
                    weight = 'font-extrabold';
                } else if (item.occ < 250) {
                    fontSize = 'text-[11px]';
                    padding = 'px-2.5 py-1';
                    weight = 'font-semibold';
                }

                const colorConfig = TOPIC_COLORS[item.category] || TOPIC_COLORS['production'];

                // Draw connector line if related to currently selected topic
                if (linesGroup && (isRelated || isSelected) && !isSelected) {
                    const selR = ringRadii[selectedData.ring];
                    const selAngleRad = (selectedData.angle * Math.PI) / 180;
                    const selX = centerX + selR * Math.cos(selAngleRad);
                    const selY = centerY + selR * Math.sin(selAngleRad);

                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', selX);
                    line.setAttribute('y1', selY);
                    line.setAttribute('x2', posX);
                    line.setAttribute('y2', posY);
                    line.setAttribute('stroke', colorConfig.stroke);
                    line.setAttribute('stroke-width', '1.5');
                    line.setAttribute('stroke-dasharray', '3,3');
                    line.setAttribute('opacity', '0.65');
                    linesGroup.appendChild(line);
                }

                // Node element
                const nodeEl = document.createElement('div');
                nodeEl.id = 'node-' + key.replace(/[^a-zA-Z0-9]/g, '-');
                nodeEl.className = `absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer select-none rounded-2xl border shadow-xs transition-all duration-300 ease-out flex items-center gap-1.5 ${padding} ${fontSize} ${weight} ${colorConfig.bg} ${colorConfig.text} ${colorConfig.border}`;
                
                // Positioning
                nodeEl.style.left = `${posX}px`;
                nodeEl.style.top = `${posY}px`;

                // Filtering & Highlight visual states
                if (!isMatchingCategory) {
                    nodeEl.style.opacity = '0.18';
                    nodeEl.style.transform = 'translate(-50%, -50%) scale(0.85)';
                    nodeEl.style.filter = 'grayscale(60%)';
                } else {
                    nodeEl.style.opacity = '1';
                    if (isSelected) {
                        nodeEl.classList.add('ring-4', colorConfig.activeRing, 'shadow-lg', 'scale-110', 'z-20', 'bg-white');
                        nodeEl.style.transform = 'translate(-50%, -50%) scale(1.12)';
                    } else if (isRelated) {
                        nodeEl.classList.add('ring-2', 'ring-gray-300', 'shadow-sm', 'z-10');
                    }
                }

                // Center node special pulse
                if (item.ring === 0) {
                    nodeEl.innerHTML = `<span class="w-2 h-2 rounded-full bg-[#84cc16] animate-pulse shrink-0"></span><span>${item.name}</span>`;
                } else {
                    nodeEl.innerHTML = `<span>${item.name}</span>`;
                }

                // Event Listeners
                nodeEl.onmouseenter = (e) => showRadialTooltip(e, item);
                nodeEl.onmouseleave = hideRadialTooltip;
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
            const colorConfig = TOPIC_COLORS[data.category] || TOPIC_COLORS['production'];

            // Update Detail Card Fields
            document.getElementById('detail-topic-name').textContent = data.name;
            document.getElementById('detail-topic-occ').textContent = data.occ;
            document.getElementById('detail-topic-docs').textContent = data.docs;
            document.getElementById('detail-topic-rel').textContent = `${data.rel}%`;
            document.getElementById('detail-topic-cat').textContent = data.catLabel;
            document.getElementById('detail-ai-insight').textContent = `"${data.aiInsight}"`;
            document.getElementById('detail-context-common').textContent = data.mostCommonIn;
            document.getElementById('detail-context-source').textContent = data.topSource;

            // Update Badge
            const badgeEl = document.getElementById('detail-topic-badge');
            if (badgeEl) {
                badgeEl.textContent = data.catLabel;
                badgeEl.className = `px-2.5 py-0.5 rounded-full font-extrabold text-[10px] uppercase border ${colorConfig.badgeBg} ${colorConfig.badgeText} ${colorConfig.badgeBorder}`;
            }

            // Update Related Topics Chips
            const relatedContainer = document.getElementById('detail-related-chips');
            if (relatedContainer) {
                relatedContainer.innerHTML = (data.related || []).map(relKey => {
                    const relData = MINING_TOPICS[relKey];
                    const relColor = relData ? TOPIC_COLORS[relData.category] : colorConfig;
                    return `
                        <button onclick="selectTopicNode('${relKey}')" class="px-2.5 py-1 rounded-xl text-xs font-bold transition-all bg-gray-100 hover:bg-white text-gray-800 hover:text-[#111111] border border-gray-200 hover:border-gray-300 shadow-2xs hover:scale-105 active:scale-95 flex items-center gap-1">
                            <span class="w-1.5 h-1.5 rounded-full" style="background-color:${relColor.stroke}"></span>
                            <span>${relKey}</span>
                        </button>
                    `;
                }).join('');
            }

            // Re-render Trend Chart
            updateTopicTrendChart(data);

            // Re-render Word Cloud to show active selection and connectors
            renderRadialWordCloud();

            if (window.lucide) lucide.createIcons();
        }

        // Focus topic in cloud with smooth animation
        function focusTopicInCloud(topicKey) {
            selectTopicNode(topicKey);
            const container = document.getElementById('radial-cloud-container');
            if (container) {
                container.classList.add('ring-2', 'ring-[#a3e635]');
                setTimeout(() => container.classList.remove('ring-2', 'ring-[#a3e635]'), 600);
            }
        }

        // Filter Category
        function filterTopicCategory(cat) {
            currentTopicCategoryFilter = cat;
            document.querySelectorAll('.topic-cat-btn').forEach(btn => {
                btn.classList.remove('bg-[#111111]', 'text-[#a3e635]', 'shadow-sm');
                btn.classList.add('bg-gray-100', 'text-gray-600', 'border-transparent');
            });
            const activeBtn = document.getElementById('topic-filter-' + cat);
            if (activeBtn) {
                activeBtn.classList.remove('bg-gray-100', 'text-gray-600', 'border-transparent');
                activeBtn.classList.add('bg-[#111111]', 'text-[#a3e635]', 'shadow-sm');
            }
            renderRadialWordCloud();
        }

        // Trend Chart Time Range Switcher
        function setTrendTimeRange(range) {
            currentTrendTimeRange = range;
            document.querySelectorAll('.trend-btn').forEach(btn => {
                btn.classList.remove('bg-white', 'text-[#111111]', 'shadow-2xs');
                btn.classList.add('hover:text-[#111111]');
            });
            const activeBtn = document.getElementById('trend-range-' + range);
            if (activeBtn) {
                activeBtn.classList.add('bg-white', 'text-[#111111]', 'shadow-2xs');
            }
            const data = MINING_TOPICS[currentSelectedTopicKey];
            if (data) updateTopicTrendChart(data);
        }

        // Update Trend Chart with Chart.js
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

            const colorConfig = TOPIC_COLORS[data.category] || TOPIC_COLORS['production'];

            if (topicTrendChartInstance) {
                topicTrendChartInstance.destroy();
            }

            const ctx = canvas.getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, 100);
            gradient.addColorStop(0, colorConfig.stroke + '44');
            gradient.addColorStop(1, colorConfig.stroke + '00');

            topicTrendChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        data: points,
                        borderColor: colorConfig.accentHex || colorConfig.stroke,
                        borderWidth: 2.5,
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.38,
                        pointRadius: 3,
                        pointBackgroundColor: '#ffffff',
                        pointBorderColor: colorConfig.stroke,
                        pointBorderWidth: 2,
                        pointHoverRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#111111',
                            titleFont: { size: 10, weight: 'bold' },
                            bodyFont: { size: 11, weight: 'bold' },
                            padding: 8,
                            cornerRadius: 8,
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
                            grid: { color: '#f1f5f9' },
                            ticks: { font: { size: 9, weight: '600' }, color: '#94a3b8', maxTicksLimit: 3 }
                        }
                    }
                }
            });
        }

        // Query selected topic directly in GeoAI
        function queryTopicInAssistant(topicKey) {
            const data = MINING_TOPICS[topicKey] || { name: topicKey };
            const prompt = `Provide a comprehensive technical summary of "${data.name}" across CMPDI geological exploration and mine production reports.`;
            
            // If on page-query, send to page chat, otherwise open floating assistant
            if (window.location.hash === '#query') {
                sendPresetPrompt(prompt);
            } else {
                openFloatingChat();
                sendFloatingPreset(prompt);
            }
        }

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

# Add initTopicIntelligence to handleRouting
router_hook_target = "if (pageId === 'dashboard' && window.productionChartInstance) {"
if router_hook_target in html and 'initTopicIntelligence()' not in html:
    html = html.replace(router_hook_target, "if (pageId === 'insights') {\n                setTimeout(initTopicIntelligence, 100);\n            }\n            " + router_hook_target)
    print("Added router hook for #insights initialization")

# Append the JavaScript engine before </body>
html = html.replace('</body>', f'{radial_cloud_js}\n</body>')

with open(ORIGINAL_HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully injected Mining Topic Intelligence Radial Word Map & Detail Panel into original_render_index.html!")
