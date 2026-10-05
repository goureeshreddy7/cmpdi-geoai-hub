import os
import re

ORIGINAL_HTML_PATH = 'c:/Users/LENOVO/Downloads/final_cmpdi/cmpdi-geoai-hub-main/original_render_index.html'
AVATAR_B64_PATH = 'c:/Users/LENOVO/Downloads/final_cmpdi/cmpdi-geoai-hub-main/frontend/avatar_b64.txt'

with open(ORIGINAL_HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

with open(AVATAR_B64_PATH, 'r', encoding='utf-8') as f:
    avatar_b64 = f.read().strip()

# 1. Ensure #nav-query is in sidebar for Admin
if 'id="nav-query"' not in html:
    insights_nav_str = 'id="nav-insights">\n                    <i data-lucide="sparkles" class="w-6 h-6 stroke-[2.2]"></i>\n                    <span class="active-indicator absolute left-1 top-3.5 w-1.5 h-7 bg-[#a3e635] rounded-r-full shadow-[0_0_8px_#a3e635]"></span>\n                    <span class="nav-tooltip absolute left-20 bg-white text-[#111111] text-xs px-3 py-2 rounded-xl opacity-0 group-hover:opacity-100 pointer-events-none transition-all whitespace-nowrap z-[60] shadow-xl font-bold hidden lg:block border border-gray-100">Insights</span>\n                </a>'
    
    query_nav_btn = '''
                <a href="#query" class="nav-btn admin-nav w-12 h-12 lg:w-14 lg:h-14 rounded-2xl flex items-center justify-center relative z-10 group text-gray-400 hover:text-white hover:scale-105" id="nav-query">
                    <i data-lucide="bot" class="w-6 h-6 stroke-[2.2]"></i>
                    <span class="active-indicator absolute left-1 top-3.5 w-1.5 h-7 bg-[#a3e635] rounded-r-full shadow-[0_0_8px_#a3e635]"></span>
                    <span class="nav-tooltip absolute left-20 bg-white text-[#111111] text-xs px-3 py-2 rounded-xl opacity-0 group-hover:opacity-100 pointer-events-none transition-all whitespace-nowrap z-[60] shadow-xl font-bold hidden lg:block border border-gray-100">AI Query</span>
                </a>'''
    
    # Try inserting after insights nav
    if 'id="nav-insights"' in html:
        # Find closing </a> for nav-insights
        pos = html.find('id="nav-insights"')
        end_a = html.find('</a>', pos) + 4
        html = html[:end_a] + '\n' + query_nav_btn + html[end_a:]
        print("Restored #nav-query to sidebar navigation")

# 2. Add #page-query with Left Chat History Panel before <!-- ========================================================================= -->
if '<div id="page-query"' not in html:
    page_query_markup = '''
                    <!-- ================= AI QUERY STUDIO WITH CHAT HISTORY ================= -->
                    <div id="page-query" class="page-view flex-col max-w-7xl mx-auto w-full h-[620px] bg-white rounded-[2.5rem] shadow-sm border border-gray-200/80 overflow-hidden relative card-elevate">
                        <div class="flex h-full w-full">
                            
                            <!-- LEFT PANEL: Chat History & Query Threads -->
                            <div class="w-72 sm:w-80 border-r border-gray-200/80 bg-gray-50/70 flex flex-col shrink-0">
                                <!-- Top Action Header -->
                                <div class="p-4 px-5 border-b border-gray-200/70 flex items-center justify-between bg-white/60 backdrop-blur-xs">
                                    <div class="flex items-center gap-2">
                                        <div class="w-7 h-7 rounded-lg bg-[#111111] flex items-center justify-center">
                                            <i data-lucide="history" class="w-4 h-4 text-[#a3e635]"></i>
                                        </div>
                                        <h3 class="font-black text-xs text-[#111111] uppercase tracking-wider">Query History</h3>
                                    </div>
                                    <button onclick="startNewQuerySession()" title="Start New Query Session" class="px-3 py-1.5 bg-[#111111] hover:bg-black text-[#a3e635] rounded-xl text-[11px] font-black transition-all flex items-center gap-1.5 shadow-sm hover:scale-105 active:scale-95">
                                        <i data-lucide="plus" class="w-3.5 h-3.5 stroke-[2.5]"></i> <span>New</span>
                                    </button>
                                </div>
                                
                                <!-- Search History Box -->
                                <div class="p-3 border-b border-gray-200/60 bg-white/40">
                                    <div class="relative flex items-center bg-white rounded-xl border border-gray-200/80 px-3 py-2 focus-within:border-[#111111] focus-within:ring-2 focus-within:ring-[#a3e635]/30 transition-all shadow-2xs">
                                        <i data-lucide="search" class="w-3.5 h-3.5 text-gray-400 mr-2 shrink-0"></i>
                                        <input type="text" id="history-search-input" onkeyup="filterQueryHistory(this.value)" placeholder="Search query sessions..." class="w-full bg-transparent text-xs font-bold outline-none text-[#111111] placeholder:text-gray-400">
                                    </div>
                                </div>

                                <!-- Scrollable Session History List -->
                                <div id="query-history-list" class="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
                                    <!-- Dynamic history items loaded via JS -->
                                </div>

                                <!-- History Footer Stats -->
                                <div class="p-3 px-4 border-t border-gray-200/70 bg-white/80 flex items-center justify-between text-[10px] text-gray-400 font-bold">
                                    <span id="history-count-label">5 Recent Sessions</span>
                                    <button onclick="clearAllHistory()" class="text-gray-500 hover:text-red-600 font-extrabold transition-colors">Clear All</button>
                                </div>
                            </div>

                            <!-- RIGHT PANEL: Interactive GeoAI Assistant Chat Canvas -->
                            <div class="flex-1 flex flex-col h-full overflow-hidden bg-white">
                                <!-- Header inside card -->
                                <div class="p-4 sm:p-5 px-6 flex items-center justify-between border-b border-gray-200/70 bg-white/90 backdrop-blur-md z-10">
                                    <div class="flex items-center gap-3">
                                        <div class="w-11 h-11 rounded-2xl bg-[#111111] flex items-center justify-center shadow-md">
                                            <i data-lucide="cpu" class="w-5 h-5 text-[#a3e635]"></i>
                                        </div>
                                        <div>
                                            <div class="flex items-center gap-2">
                                                <h2 class="text-sm font-black text-[#111111] tracking-tight">GeoAI Assistant</h2>
                                                <span class="px-2.5 py-0.5 bg-[#eefcce] text-[#111111] font-extrabold text-[9px] rounded-full border border-[#d9f99d]">v2.4 PRO</span>
                                            </div>
                                            <p class="text-[11px] font-extrabold text-[#84cc16]">Connected to 1,284 Institutional Documents</p>
                                        </div>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <button onclick="clearChat()" class="text-xs font-bold text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 px-3.5 py-2 rounded-xl transition-colors flex items-center gap-1.5">
                                            <i data-lucide="rotate-ccw" class="w-3.5 h-3.5"></i> Clear Chat
                                        </button>
                                    </div>
                                </div>

                                <!-- Chat Messages Scrollable Area -->
                                <div id="chat-messages" class="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar bg-gray-50/50">
                                    <div class="flex gap-3 max-w-[85%]">
                                        <div class="w-9 h-9 rounded-xl bg-white flex items-center justify-center shrink-0 border border-gray-200 shadow-2xs"><i data-lucide="cpu" class="w-4 h-4 text-gray-500"></i></div>
                                        <div class="bg-white rounded-2xl rounded-tl-xs p-4 shadow-2xs border border-gray-200/70">
                                            <p class="text-gray-800 font-semibold text-xs sm:text-sm leading-relaxed">Hello Administrator! Ask any query regarding coal production, geological reserves, or clearance delays. Or select a quick preset prompt:</p>
                                        </div>
                                    </div>

                                    <div id="suggested-chips" class="flex flex-wrap gap-2 pl-12 pt-1">
                                        <button onclick="sendPresetPrompt('What is total coal production for Q3?')" class="px-4 py-2 bg-white hover:bg-[#eefcce] text-gray-800 hover:text-[#111111] border border-gray-200 rounded-full text-[11px] font-extrabold transition-all shadow-2xs hover:scale-105">📊 Q3 Total Coal Production?</button>
                                        <button onclick="sendPresetPrompt('Reasons for delay in Gevra expansion?')" class="px-4 py-2 bg-white hover:bg-[#ffebd6] text-gray-800 hover:text-[#111111] border border-gray-200 rounded-full text-[11px] font-extrabold transition-all shadow-2xs hover:scale-105">⚠️ Gevra Expansion Delays</button>
                                        <button onclick="sendPresetPrompt('List major coalfields and active opencast mines in Jharkhand')" class="px-4 py-2 bg-white hover:bg-[#eefcce] text-gray-800 hover:text-[#111111] border border-gray-200 rounded-full text-[11px] font-extrabold transition-all shadow-2xs hover:scale-105">🗺️ Jharkhand Coalfields</button>
                                    </div>

                                    <div class="flex gap-3 max-w-[85%] ml-auto flex-row-reverse">
                                        <div class="w-9 h-9 rounded-xl bg-[#111111] flex items-center justify-center shrink-0 text-white font-extrabold text-xs shadow-md">A</div>
                                        <div class="bg-[#111111] text-white rounded-2xl rounded-tr-xs p-4 shadow-md">
                                            <p class="font-medium text-xs sm:text-sm">Reasons for delay in Gevra expansion clearance?</p>
                                        </div>
                                    </div>

                                    <div class="flex gap-3 max-w-[85%]">
                                        <div class="w-9 h-9 rounded-xl bg-[#eefcce] flex items-center justify-center shrink-0 shadow-2xs border border-[#d9f99d]"><i data-lucide="cpu" class="w-4 h-4 text-[#111111]"></i></div>
                                        <div class="bg-white rounded-2xl rounded-tl-xs p-4 shadow-2xs border border-gray-200/70">
                                            <p class="text-gray-900 font-extrabold mb-2 text-xs sm:text-sm">Based on SECL communications (Jan-Oct 2023):</p>
                                            <ul class="list-disc list-inside text-gray-700 space-y-1 mb-2 text-xs sm:text-sm font-medium">
                                                <li>Pending wildlife clearance from NBWL.</li>
                                                <li>Hydrological impact assessments required in Block B.</li>
                                            </ul>
                                            <div class="flex items-center gap-2 pt-2 border-t border-gray-100 text-[10px] font-extrabold text-gray-400">
                                                <span>SECL_Clearance_2023.pdf</span> • <span class="text-[#84cc16]">99.1% Confidence</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Pinned Chat Input Box -->
                                <div class="p-4 bg-white border-t border-gray-200/80 z-10">
                                    <form onsubmit="handleChatSubmit(event)" class="relative flex items-center bg-gray-50 rounded-2xl border border-gray-200 focus-within:border-[#111111] focus-within:bg-white focus-within:ring-2 focus-within:ring-[#a3e635]/30 transition-all shadow-2xs p-1">
                                        <input type="text" id="chat-input" autocomplete="off" placeholder="Ask anything about reports or geological logs..." class="w-full bg-transparent border-none pl-4 pr-3 py-3 text-[#111111] font-semibold outline-none text-xs sm:text-sm placeholder:text-gray-400">
                                        <button type="submit" class="p-3 bg-[#a3e635] hover:bg-[#84cc16] text-[#111111] rounded-xl transition-all flex-shrink-0 hover:scale-105 active:scale-95 shadow-sm flex items-center justify-center">
                                            <i data-lucide="send" class="w-4 h-4 font-bold"></i>
                                        </button>
                                    </form>
                                </div>
                            </div>

                        </div>
                    </div>
'''
    insert_target = '<!-- ========================================================================= -->'
    html = html.replace(insert_target, page_query_markup + '\n                    ' + insert_target)
    print("Added #page-query with Left Chat History Panel")

# 3. Update pageMeta to ensure 'query' is configured
if "'query':" not in html:
    html = html.replace("'insights': { title: 'AI Insights & Topic Map', subtitle: 'Discover semantic trends and clusters' },", "'insights': { title: 'AI Insights & Topic Map', subtitle: 'Discover semantic trends and clusters' },\n            'query': { title: 'GeoAI Query Assistant', subtitle: 'Talk directly to your institutional repositories' },")
    print("Updated pageMeta with 'query' route")

# 4. Remove old floating assistant before injecting updated version
float_start = html.find('<!-- ================= FLOATING GEOAI ASSISTANT (NAMASTE BOT) ================= -->')
if float_start != -1:
    body_end = html.find('</body>', float_start)
    if body_end != -1:
        html = html[:float_start] + html[body_end:]

# 5. Floating Assistant Widget + Page Chat Controller + History Manager
page_and_floating_scripts = f'''
    <!-- ================= FLOATING GEOAI ASSISTANT (NAMASTE BOT) ================= -->
    <style>
        /* Glowing Ripple & Floating Animation */
        @keyframes avatarHaloGlow {{
            0%, 100% {{
                box-shadow: 0 0 0 0 rgba(163, 230, 53, 0.7), 0 0 24px rgba(163, 230, 53, 0.6), 0 8px 32px rgba(0,0,0,0.3);
            }}
            50% {{
                box-shadow: 0 0 0 12px rgba(163, 230, 53, 0), 0 0 42px rgba(163, 230, 53, 0.9), 0 14px 38px rgba(0,0,0,0.35);
            }}
        }}

        .assistant-avatar-halo {{
            animation: avatarHaloGlow 3.2s infinite;
        }}

        /* Speech Bubble Pointer Arrow */
        .namaste-speech-bubble {{
            position: absolute;
            right: calc(100% + 12px);
            top: 50%;
            transform: translateY(-50%) translateX(6px);
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.25s cubic-bezier(0.16, 1, 0.3, 1), transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            white-space: nowrap;
        }}

        .namaste-speech-bubble::after {{
            content: '';
            position: absolute;
            right: -8px;
            top: 50%;
            transform: translateY(-50%);
            width: 0;
            height: 0;
            border-top: 7px solid transparent;
            border-bottom: 7px solid transparent;
            border-left: 9px solid #111111;
        }}

        #geoai-floating-trigger-container:hover .namaste-speech-bubble {{
            opacity: 1;
            transform: translateY(-50%) translateX(0);
            pointer-events: auto;
        }}

        /* Floating Window Base Transition */
        #geoai-floating-chat-window {{
            width: min(420px, calc(100vw - 32px));
            height: min(520px, calc(100vh - 130px));
            max-height: calc(100vh - 130px);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            z-index: 10005;
        }}

        /* Viewport-Safe Expanded Center Studio Mode */
        #geoai-floating-chat-window.chat-expanded {{
            position: fixed !important;
            top: 50% !important;
            left: 50% !important;
            right: auto !important;
            bottom: auto !important;
            transform: translate(-50%, -50%) !important;
            width: min(860px, calc(100vw - 48px)) !important;
            height: min(650px, calc(100vh - 80px)) !important;
            max-height: calc(100vh - 80px) !important;
            margin: 0 !important;
            z-index: 10010 !important;
            box-shadow: 0 30px 90px -15px rgba(0,0,0,0.5), 0 0 0 1px rgba(0,0,0,0.1) !important;
        }}

        /* Query History Item Active / Hover styling */
        .history-item-btn {{
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .history-item-btn:hover {{
            background: #ffffff;
            border-color: #e5e7eb;
            transform: translateX(3px);
        }}
        .history-item-btn.active-session {{
            background: #ffffff;
            border-color: #a3e635;
            box-shadow: 0 4px 12px rgba(163, 230, 53, 0.15);
        }}
    </style>

    <!-- Expanded Backdrop Overlay (Strictly behind assistant window) -->
    <div id="geoai-chat-backdrop" class="fixed inset-0 bg-black/40 backdrop-blur-xs z-[9995] hidden opacity-0 transition-opacity duration-300 pointer-events-auto" onclick="toggleExpandFloatingChat(event)"></div>

    <div id="geoai-floating-assistant-root" class="fixed bottom-6 right-6 z-[10000] font-['Inter',sans-serif] flex flex-col items-end pointer-events-none select-none">
        
        <!-- Floating Interactive Chat Window -->
        <div id="geoai-floating-chat-window" class="pointer-events-auto bg-white rounded-[2.25rem] border border-gray-200/90 shadow-[0_24px_70px_-15px_rgba(0,0,0,0.4),0_0_0_1px_rgba(0,0,0,0.06)] overflow-hidden flex flex-col origin-bottom-right mb-3.5 opacity-0 scale-95 translate-y-4 pointer-events-none" style="display: none;">
            
            <!-- Chat Header -->
            <div class="px-5 py-4 bg-[#111111] text-white flex items-center justify-between border-b border-gray-800 shrink-0 select-none">
                <div class="flex items-center gap-3">
                    <div class="relative w-11 h-11 rounded-full border-2 border-[#a3e635] p-0.5 shadow-[0_0_12px_rgba(163,230,53,0.8)] shrink-0 bg-white">
                        <img src="{avatar_b64}" alt="GeoAI Assistant" class="w-full h-full object-cover rounded-full">
                        <span class="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-[#84cc16] border-2 border-[#111111] rounded-full flex items-center justify-center">
                            <span class="w-1 h-1 bg-white rounded-full"></span>
                        </span>
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <h3 class="font-extrabold text-sm text-white tracking-tight">GeoAI Assistant</h3>
                            <span class="px-2 py-0.5 bg-[#a3e635] text-[#111111] font-black text-[9px] uppercase tracking-wider rounded-full">PRO</span>
                        </div>
                        <p class="text-[11px] text-[#a3e635] font-bold flex items-center gap-1.5 mt-0.5">
                            <span class="w-1.5 h-1.5 rounded-full bg-[#a3e635] animate-pulse"></span> Connected to 1,284 Documents
                        </p>
                    </div>
                </div>
                <div class="flex items-center gap-1.5">
                    <!-- Clear Conversation -->
                    <button onclick="clearFloatingChat(event)" title="Clear conversation" class="w-8 h-8 rounded-xl bg-white/10 hover:bg-white/20 text-gray-300 hover:text-white flex items-center justify-center transition-colors">
                        <i data-lucide="rotate-ccw" class="w-3.5 h-3.5"></i>
                    </button>
                    <!-- Expand / Restore Toggle -->
                    <button id="floating-chat-expand-btn" onclick="toggleExpandFloatingChat(event)" title="Maximize / Restore window" class="w-8 h-8 rounded-xl bg-white/10 hover:bg-white/20 text-gray-300 hover:text-white flex items-center justify-center transition-colors">
                        <i data-lucide="maximize-2" id="floating-chat-expand-icon" class="w-3.5 h-3.5"></i>
                    </button>
                    <!-- Close Window Button -->
                    <button onclick="closeFloatingChat(event)" title="Close" class="w-8 h-8 rounded-xl bg-white/10 hover:bg-red-500/80 text-gray-300 hover:text-white flex items-center justify-center transition-colors ml-1">
                        <i data-lucide="x" class="w-4 h-4"></i>
                    </button>
                </div>
            </div>

            <!-- Chat Messages Scrollable Area -->
            <div id="floating-chat-messages" class="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4 bg-gray-50/70 custom-scrollbar">
                <!-- Initial Welcome Message from Assistant -->
                <div class="flex gap-3 max-w-[92%]">
                    <div class="w-9 h-9 rounded-full border border-[#a3e635] bg-white flex items-center justify-center shrink-0 overflow-hidden shadow-xs">
                        <img src="{avatar_b64}" alt="Bot" class="w-full h-full object-cover">
                    </div>
                    <div class="bg-white rounded-2xl rounded-tl-xs p-4 shadow-sm border border-gray-200/80 text-xs text-gray-800 leading-relaxed font-medium">
                        <p class="font-extrabold text-[#111111] mb-1.5 text-xs flex items-center gap-1.5">
                            <span class="text-sm">🙏</span> <span>Namaste! How may I help you?</span>
                        </p>
                        <p class="text-gray-600">I am your <strong>CMPDI GeoAI Assistant</strong>. Ask me anything about coalfields, borehole survey logs, monthly production summaries, parliamentary inquiries, or uploaded institutional documents.</p>
                    </div>
                </div>

                <!-- Suggested Query Chips -->
                <div id="floating-suggested-chips" class="flex flex-wrap gap-2 pl-12 pt-0.5">
                    <button onclick="sendFloatingPreset('What is the total coal production for Q3?')" class="px-3.5 py-1.5 bg-white hover:bg-[#eefcce] text-gray-800 hover:text-[#111111] border border-gray-200 rounded-full text-[11px] font-extrabold transition-all shadow-2xs hover:scale-105 text-left">📊 Q3 Production Summary</button>
                    <button onclick="sendFloatingPreset('Reasons for delay in Gevra expansion clearance?')" class="px-3.5 py-1.5 bg-white hover:bg-[#ffebd6] text-gray-800 hover:text-[#111111] border border-gray-200 rounded-full text-[11px] font-extrabold transition-all shadow-2xs hover:scale-105 text-left">⚠️ Gevra Expansion Delays</button>
                    <button onclick="sendFloatingPreset('List major coalfields and active opencast mines in Jharkhand')" class="px-3.5 py-1.5 bg-white hover:bg-[#eefcce] text-gray-800 hover:text-[#111111] border border-gray-200 rounded-full text-[11px] font-extrabold transition-all shadow-2xs hover:scale-105 text-left">🗺️ Jharkhand Coalfields & Mines</button>
                    <button onclick="sendFloatingPreset('Summarize environmental clearance status across SECL and MCL')" class="px-3.5 py-1.5 bg-white hover:bg-[#f1f5f9] text-gray-800 hover:text-[#111111] border border-gray-200 rounded-full text-[11px] font-extrabold transition-all shadow-2xs hover:scale-105 text-left">📑 EC Status SECL / MCL</button>
                </div>
            </div>

            <!-- Chat Input Area -->
            <div class="p-3 sm:p-3.5 bg-white border-t border-gray-200/80 shrink-0">
                <form onsubmit="handleFloatingChatSubmit(event)" class="relative flex items-center bg-gray-50 rounded-2xl border border-gray-200 focus-within:border-[#111111] focus-within:bg-white focus-within:ring-2 focus-within:ring-[#a3e635]/40 transition-all p-1">
                    <input type="text" id="floating-chat-input" autocomplete="off" placeholder="Ask about reports, coalfields, or documents..." class="w-full bg-transparent border-none pl-3.5 pr-2 py-2.5 text-[#111111] font-semibold outline-none text-xs sm:text-sm placeholder:text-gray-400">
                    <button type="submit" title="Send Query" class="p-2.5 bg-[#a3e635] hover:bg-[#84cc16] text-[#111111] rounded-xl transition-all flex-shrink-0 hover:scale-105 active:scale-95 shadow-sm flex items-center justify-center font-black">
                        <i data-lucide="send" class="w-4 h-4"></i>
                    </button>
                </form>
                <div class="flex items-center justify-between px-2 pt-2 text-[10px] text-gray-400 font-semibold">
                    <span>CMPDI GeoAI Engine</span>
                    <span>Press <kbd class="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded text-[9px] text-gray-700 font-bold">Enter ↵</kbd> to send</span>
                </div>
            </div>
        </div>

        <!-- Floating Avatar Button Trigger + Namaste Speech Bubble on Hover -->
        <div id="geoai-floating-trigger-container" class="pointer-events-auto relative inline-flex self-end items-center cursor-pointer group select-none" onclick="toggleFloatingChat(event)">
            
            <!-- Hover 'Namaste ! how may I help you?' Speech Bubble (Directly adjacent to avatar) -->
            <div class="namaste-speech-bubble bg-[#111111] text-white px-5 py-3 rounded-full text-xs sm:text-sm font-extrabold flex items-center gap-2.5 shadow-[0_14px_40px_rgba(0,0,0,0.55),0_0_0_1px_rgba(255,255,255,0.08)] z-50">
                <span class="w-2.5 h-2.5 rounded-full bg-[#a3e635] shadow-[0_0_10px_#a3e635] animate-pulse shrink-0"></span>
                <span class="tracking-tight text-gray-100">Namaste ! how may I help you?</span>
            </div>

            <!-- Avatar Glowing Circle (Bigger 84px avatar) -->
            <div class="assistant-avatar-halo relative w-20 h-20 sm:w-[84px] sm:h-[84px] rounded-full border-[3.5px] border-[#a3e635] bg-white transition-all duration-300 group-hover:scale-105 group-active:scale-95 flex items-center justify-center p-0.5">
                <img src="{avatar_b64}" alt="GeoAI Assistant" class="w-full h-full object-cover rounded-full">
                
                <!-- Online status dot with inner white core -->
                <div class="absolute bottom-0.5 right-0.5 w-6 h-6 bg-[#84cc16] border-[2.5px] border-white rounded-full flex items-center justify-center shadow-md">
                    <div class="w-2 h-2 bg-white rounded-full"></div>
                </div>
            </div>

        </div>

    </div>

    <!-- Page Query & Floating Assistant Controller Scripts -->
    <script>
        // ── CHAT HISTORY DATA & MANAGER ──
        let querySessionsHistory = [
            {{
                id: 'sess-1',
                title: 'Gevra Expansion Clearance Delays',
                query: 'Reasons for delay in Gevra expansion clearance?',
                category: 'Environmental Clearance',
                timestamp: '10 mins ago',
                icon: 'alert-triangle',
                badgeColor: 'bg-amber-100 text-amber-800'
            }},
            {{
                id: 'sess-2',
                title: 'Q3 Total Coal Production',
                query: 'What is total coal production for Q3?',
                category: 'Production Summary',
                timestamp: '2 hours ago',
                icon: 'bar-chart-2',
                badgeColor: 'bg-emerald-100 text-emerald-800'
            }},
            {{
                id: 'sess-3',
                title: 'Jharkhand Coalfield Reserves',
                query: 'List major coalfields and active opencast mines in Jharkhand',
                category: 'Geological Reserve',
                timestamp: 'Yesterday',
                icon: 'map-pin',
                badgeColor: 'bg-blue-100 text-blue-800'
            }},
            {{
                id: 'sess-4',
                title: 'Borehole Exploration Analysis Block B',
                query: 'Summarize core lithology logs for Jharia Block 4',
                category: 'Exploration Log',
                timestamp: '2 days ago',
                icon: 'file-text',
                badgeColor: 'bg-purple-100 text-purple-800'
            }},
            {{
                id: 'sess-5',
                title: 'SECL Environmental Compliance Brief',
                query: 'Summarize environmental clearance status across SECL and MCL',
                category: 'Compliance',
                timestamp: '3 days ago',
                icon: 'shield-check',
                badgeColor: 'bg-lime-100 text-lime-800'
            }}
        ];

        let activeSessionId = 'sess-1';

        function renderQueryHistoryList(filterText = '') {{
            const listEl = document.getElementById('query-history-list');
            if (!listEl) return;

            const filtered = querySessionsHistory.filter(s => 
                s.title.toLowerCase().includes(filterText.toLowerCase()) ||
                s.query.toLowerCase().includes(filterText.toLowerCase()) ||
                s.category.toLowerCase().includes(filterText.toLowerCase())
            );

            const countLabel = document.getElementById('history-count-label');
            if (countLabel) countLabel.textContent = `${{filtered.length}} Session${{filtered.length === 1 ? '' : 's'}}`;

            if (filtered.length === 0) {{
                listEl.innerHTML = `<p class="text-xs text-gray-400 font-semibold text-center py-8">No matching query sessions</p>`;
                return;
            }}

            listEl.innerHTML = filtered.map(item => `
                <div onclick="selectQuerySession('${{item.id}}')" class="history-item-btn p-3 rounded-2xl border border-gray-200/70 bg-white/70 cursor-pointer ${{item.id === activeSessionId ? 'active-session border-[#a3e635] shadow-xs' : ''}}">
                    <div class="flex items-center justify-between gap-1 mb-1">
                        <span class="px-2 py-0.5 rounded-md text-[9px] font-black uppercase tracking-wider ${{item.badgeColor}}">${{item.category}}</span>
                        <span class="text-[9px] text-gray-400 font-bold">${{item.timestamp}}</span>
                    </div>
                    <h4 class="text-xs font-black text-[#111111] line-clamp-1 mb-0.5">${{item.title}}</h4>
                    <p class="text-[10px] text-gray-500 font-medium line-clamp-1">${{item.query}}</p>
                </div>
            `).join('');

            if (window.lucide) lucide.createIcons();
        }}

        function filterQueryHistory(val) {{
            renderQueryHistoryList(val);
        }}

        function selectQuerySession(id) {{
            activeSessionId = id;
            renderQueryHistoryList(document.getElementById('history-search-input')?.value || '');
            const sess = querySessionsHistory.find(s => s.id === id);
            if (sess) {{
                sendPresetPrompt(sess.query);
            }}
        }}

        function startNewQuerySession() {{
            activeSessionId = null;
            renderQueryHistoryList();
            clearChat();
            const input = document.getElementById('chat-input');
            if (input) {{
                input.value = '';
                input.focus();
            }}
            alertBox('Started new AI Query Session');
        }}

        function clearAllHistory() {{
            querySessionsHistory = [];
            renderQueryHistoryList();
            alertBox('Query history cleared');
        }}

        // Initialize history list on DOM load
        setTimeout(() => {{
            renderQueryHistoryList();
        }}, 200);

        // ── DEDICATED PAGE CHAT HANDLERS (#page-query) ──
        function sendPresetPrompt(promptText) {{
            const input = document.getElementById('chat-input');
            if (input) {{
                input.value = promptText;
                const form = input.closest('form');
                if (form) {{
                    const evt = new Event('submit', {{ cancelable: true }});
                    form.dispatchEvent(evt);
                }}
            }}
        }}

        async function handleChatSubmit(e) {{
            e.preventDefault();
            const input = document.getElementById('chat-input');
            const query = input.value.trim();
            if (!query) return;

            const chatMessages = document.getElementById('chat-messages');
            const chips = document.getElementById('suggested-chips');
            if (chips) chips.style.display = 'none';

            // Add to query history if new
            const existing = querySessionsHistory.find(s => s.query.toLowerCase() === query.toLowerCase());
            if (!existing) {{
                const newSess = {{
                    id: 'sess-' + Date.now(),
                    title: query.length > 32 ? query.substring(0, 32) + '...' : query,
                    query: query,
                    category: 'General AI Query',
                    timestamp: 'Just now',
                    icon: 'message-square',
                    badgeColor: 'bg-lime-100 text-lime-800'
                }};
                querySessionsHistory.unshift(newSess);
                activeSessionId = newSess.id;
                renderQueryHistoryList();
            }}

            // User bubble
            const userMsg = document.createElement('div');
            userMsg.className = 'flex gap-3 max-w-[85%] ml-auto flex-row-reverse';
            userMsg.innerHTML = `<div class="w-9 h-9 rounded-xl bg-[#111111] flex items-center justify-center shrink-0 text-white font-extrabold text-xs shadow-md">A</div><div class="bg-[#111111] text-white rounded-2xl rounded-tr-xs p-4 shadow-md"><p class="font-medium text-xs sm:text-sm">${{query}}</p></div>`;
            chatMessages.appendChild(userMsg);
            input.value = '';
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Thinking bubble
            const thinkId = 'think-' + Date.now();
            const thinkMsg = document.createElement('div');
            thinkMsg.className = 'flex gap-3 max-w-[85%]';
            thinkMsg.id = thinkId;
            thinkMsg.innerHTML = `<div class="w-9 h-9 rounded-xl bg-[#eefcce] flex items-center justify-center shrink-0 shadow-2xs border border-[#d9f99d]"><i data-lucide="cpu" class="w-4 h-4 text-[#111111]"></i></div><div class="bg-white rounded-2xl rounded-tl-xs p-4 shadow-2xs border border-gray-200/70"><p class="text-gray-500 text-xs animate-pulse">🔍 Searching institutional documents...</p></div>`;
            chatMessages.appendChild(thinkMsg);
            if (window.lucide) lucide.createIcons();
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {{
                const resp = await fetch(`${{API_BASE}}/api/chat`, {{
                    method: 'POST', headers: authHeaders(),
                    body: JSON.stringify({{ query, top_k: 5 }})
                }});
                const data = await resp.json();
                document.getElementById(thinkId)?.remove();

                const answer = data.answer || 'No answer returned.';
                const citations = data.citations || [];
                let citHtml = '';
                if (citations.length > 0) {{
                    citHtml = `<div class="flex items-center gap-2 pt-2 border-t border-gray-100 text-[10px] font-extrabold text-gray-400 flex-wrap mt-2">` +
                        citations.slice(0,4).map(c => `<span class="bg-[#eefcce] text-[#111111] px-2 py-0.5 rounded-full border border-[#d9f99d]">${{c.source}} p.${{c.page}} • ${{Math.round((c.confidence||c.score||0.9)*100)}}%</span>`).join('') +
                    `</div>`;
                }}
                const aiMsg = document.createElement('div');
                aiMsg.className = 'flex gap-3 max-w-[85%]';
                aiMsg.innerHTML = `<div class="w-9 h-9 rounded-xl bg-[#eefcce] flex items-center justify-center shrink-0 shadow-2xs border border-[#d9f99d]"><i data-lucide="cpu" class="w-4 h-4 text-[#111111]"></i></div><div class="bg-white rounded-2xl rounded-tl-xs p-4 shadow-2xs border border-gray-200/70"><p class="text-gray-900 font-extrabold mb-1.5 text-xs sm:text-sm">GeoAI Response:</p><div class="text-gray-700 font-medium text-xs sm:text-sm mb-2 whitespace-pre-line">${{answer}}</div>${{citHtml}}</div>`;
                chatMessages.appendChild(aiMsg);
            }} catch(err) {{
                document.getElementById(thinkId)?.remove();
                const errMsg = document.createElement('div');
                errMsg.className = 'flex gap-3 max-w-[85%]';
                errMsg.innerHTML = `<div class="w-9 h-9 rounded-xl bg-red-100 flex items-center justify-center shrink-0"><i data-lucide="alert-circle" class="w-4 h-4 text-red-500"></i></div><div class="bg-white rounded-2xl p-4 border border-red-200"><p class="text-red-600 text-xs font-bold">❌ Could not reach AI backend. Please try again.</p></div>`;
                chatMessages.appendChild(errMsg);
            }}
            if (window.lucide) lucide.createIcons();
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}

        async function clearChat() {{
            try {{ await fetch(`${{API_BASE}}/api/chat/clear`, {{ method: 'POST', headers: authHeaders() }}); }} catch(e) {{}}
            const chatMessages = document.getElementById('chat-messages');
            if (chatMessages) {{
                chatMessages.innerHTML = `<div class="flex gap-3 max-w-[85%]"><div class="w-9 h-9 rounded-xl bg-white flex items-center justify-center shrink-0 border border-gray-200 shadow-2xs"><i data-lucide="cpu" class="w-4 h-4 text-gray-500"></i></div><div class="bg-white rounded-2xl rounded-tl-xs p-4 shadow-2xs border border-gray-200/70"><p class="text-gray-800 font-semibold text-xs sm:text-sm">Chat cleared. Ready for your next query.</p></div></div>`;
                if (window.lucide) lucide.createIcons();
            }}
        }}


        // ── FLOATING ASSISTANT CONTROLLER (BOTTOM RIGHT WIDGET) ──
        let isFloatingChatOpen = false;
        let isFloatingChatExpanded = false;

        function toggleFloatingChat(e) {{
            if (e) e.stopPropagation();
            if (isFloatingChatOpen) {{
                closeFloatingChat();
            }} else {{
                openFloatingChat();
            }}
        }}

        function openFloatingChat() {{
            const win = document.getElementById('geoai-floating-chat-window');
            if (!win) return;
            win.style.display = 'flex';
            requestAnimationFrame(() => {{
                win.classList.remove('opacity-0', 'scale-95', 'translate-y-4', 'pointer-events-none');
                win.classList.add('opacity-100', 'scale-100', 'translate-y-0');
            }});
            isFloatingChatOpen = true;
            setTimeout(() => {{
                const inp = document.getElementById('floating-chat-input');
                if (inp) inp.focus();
                const msgs = document.getElementById('floating-chat-messages');
                if (msgs) msgs.scrollTop = msgs.scrollHeight;
            }}, 150);
            if (window.lucide) lucide.createIcons();
        }}

        function closeFloatingChat(e) {{
            if (e) e.stopPropagation();
            const win = document.getElementById('geoai-floating-chat-window');
            const backdrop = document.getElementById('geoai-chat-backdrop');
            if (!win) return;
            
            if (isFloatingChatExpanded) {{
                toggleExpandFloatingChat();
            }}

            if (backdrop) {{
                backdrop.classList.add('opacity-0');
                setTimeout(() => backdrop.classList.add('hidden'), 250);
            }}

            win.classList.remove('opacity-100', 'scale-100', 'translate-y-0');
            win.classList.add('opacity-0', 'scale-95', 'translate-y-4', 'pointer-events-none');
            setTimeout(() => {{
                if (!isFloatingChatOpen) {{
                    win.style.display = 'none';
                }}
            }}, 280);
            isFloatingChatOpen = false;
        }}

        function toggleExpandFloatingChat(e) {{
            if (e) e.stopPropagation();
            const win = document.getElementById('geoai-floating-chat-window');
            const icon = document.getElementById('floating-chat-expand-icon');
            const backdrop = document.getElementById('geoai-chat-backdrop');
            if (!win) return;

            isFloatingChatExpanded = !isFloatingChatExpanded;
            if (isFloatingChatExpanded) {{
                win.classList.add('chat-expanded');
                if (icon) icon.setAttribute('data-lucide', 'minimize-2');
                if (backdrop) {{
                    backdrop.classList.remove('hidden');
                    requestAnimationFrame(() => backdrop.classList.remove('opacity-0'));
                }}
            }} else {{
                win.classList.remove('chat-expanded');
                if (icon) icon.setAttribute('data-lucide', 'maximize-2');
                if (backdrop) {{
                    backdrop.classList.add('opacity-0');
                    setTimeout(() => backdrop.classList.add('hidden'), 250);
                }}
            }}
            if (window.lucide) lucide.createIcons();
            const msgs = document.getElementById('floating-chat-messages');
            if (msgs) setTimeout(() => msgs.scrollTop = msgs.scrollHeight, 150);
            setTimeout(() => {{
                const inp = document.getElementById('floating-chat-input');
                if (inp) inp.focus();
            }}, 200);
        }}

        function sendFloatingPreset(promptText) {{
            const input = document.getElementById('floating-chat-input');
            if (input) {{
                input.value = promptText;
                const form = input.closest('form');
                if (form) {{
                    const evt = new Event('submit', {{ cancelable: true }});
                    form.dispatchEvent(evt);
                }}
            }}
        }}

        async function handleFloatingChatSubmit(e) {{
            e.preventDefault();
            const input = document.getElementById('floating-chat-input');
            const query = input.value.trim();
            if (!query) return;

            const chatMessages = document.getElementById('floating-chat-messages');
            const chips = document.getElementById('floating-suggested-chips');
            if (chips) chips.style.display = 'none';

            // User Message Bubble
            const userMsg = document.createElement('div');
            userMsg.className = 'flex gap-3 max-w-[88%] ml-auto flex-row-reverse';
            userMsg.innerHTML = `
                <div class="w-8 h-8 rounded-full bg-[#111111] flex items-center justify-center shrink-0 text-white font-extrabold text-xs shadow-md">U</div>
                <div class="bg-[#111111] text-white rounded-2xl rounded-tr-xs p-3.5 shadow-md">
                    <p class="font-medium text-xs sm:text-sm leading-relaxed">${{query}}</p>
                </div>
            `;
            chatMessages.appendChild(userMsg);
            input.value = '';
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Thinking Indicator
            const thinkId = 'fthink-' + Date.now();
            const thinkMsg = document.createElement('div');
            thinkMsg.className = 'flex gap-3 max-w-[88%]';
            thinkMsg.id = thinkId;
            thinkMsg.innerHTML = `
                <div class="w-8 h-8 rounded-full border border-[#a3e635] bg-white flex items-center justify-center shrink-0 overflow-hidden shadow-xs">
                    <img src="{avatar_b64}" alt="Bot" class="w-full h-full object-cover">
                </div>
                <div class="bg-white rounded-2xl rounded-tl-xs p-3.5 shadow-sm border border-gray-200/80">
                    <p class="text-gray-500 text-xs font-semibold animate-pulse flex items-center gap-2">
                        <i data-lucide="cpu" class="w-3.5 h-3.5 text-[#84cc16]"></i> Searching CMPDI knowledge repository...
                    </p>
                </div>
            `;
            chatMessages.appendChild(thinkMsg);
            if (window.lucide) lucide.createIcons();
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {{
                const resp = await fetch(`${{API_BASE}}/api/chat`, {{
                    method: 'POST',
                    headers: authHeaders(),
                    body: JSON.stringify({{ query, top_k: 5 }})
                }});
                const data = await resp.json();
                document.getElementById(thinkId)?.remove();

                const answer = data.answer || 'No specific answer found in indexed records.';
                const citations = data.citations || [];
                let citHtml = '';
                if (citations.length > 0) {{
                    citHtml = `<div class="flex items-center gap-1.5 pt-2 border-t border-gray-100 text-[10px] font-extrabold text-gray-400 flex-wrap mt-2">` +
                        citations.slice(0, 3).map(c => `<span class="bg-[#eefcce] text-[#111111] px-2 py-0.5 rounded-full border border-[#d9f99d]">${{c.source}} p.${{c.page}} • ${{Math.round((c.confidence||c.score||0.9)*100)}}%</span>`).join('') +
                    `</div>`;
                }}

                const aiMsg = document.createElement('div');
                aiMsg.className = 'flex gap-3 max-w-[88%]';
                aiMsg.innerHTML = `
                    <div class="w-8 h-8 rounded-full border border-[#a3e635] bg-white flex items-center justify-center shrink-0 overflow-hidden shadow-xs">
                        <img src="{avatar_b64}" alt="Bot" class="w-full h-full object-cover">
                    </div>
                    <div class="bg-white rounded-2xl rounded-tl-xs p-3.5 shadow-sm border border-gray-200/80">
                        <div class="text-gray-800 font-medium text-xs sm:text-sm leading-relaxed whitespace-pre-line">${{answer}}</div>
                        ${{citHtml}}
                    </div>
                `;
                chatMessages.appendChild(aiMsg);
            }} catch(err) {{
                document.getElementById(thinkId)?.remove();
                const errMsg = document.createElement('div');
                errMsg.className = 'flex gap-3 max-w-[88%]';
                errMsg.innerHTML = `
                    <div class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center shrink-0"><i data-lucide="alert-circle" class="w-4 h-4 text-red-500"></i></div>
                    <div class="bg-white rounded-2xl p-3.5 border border-red-200 shadow-sm">
                        <p class="text-red-600 text-xs font-bold">Could not connect to AI backend. Please verify server status.</p>
                    </div>
                `;
                chatMessages.appendChild(errMsg);
            }}
            if (window.lucide) lucide.createIcons();
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}

        async function clearFloatingChat(e) {{
            if (e) e.stopPropagation();
            try {{ await fetch(`${{API_BASE}}/api/chat/clear`, {{ method: 'POST', headers: authHeaders() }}); }} catch(err) {{}}
            const chatMessages = document.getElementById('floating-chat-messages');
            if (chatMessages) {{
                chatMessages.innerHTML = `
                    <div class="flex gap-3 max-w-[92%]">
                        <div class="w-8 h-8 rounded-full border border-[#a3e635] bg-white flex items-center justify-center shrink-0 overflow-hidden shadow-xs">
                            <img src="{avatar_b64}" alt="Bot" class="w-full h-full object-cover">
                        </div>
                        <div class="bg-white rounded-2xl rounded-tl-xs p-4 shadow-sm border border-gray-200/80 text-xs text-gray-800 leading-relaxed font-medium">
                            <p class="font-extrabold text-[#111111] mb-1">Conversation cleared.</p>
                            <p class="text-gray-500 text-xs">Ready for your next geological, production, or report query.</p>
                        </div>
                    </div>
                    <div id="floating-suggested-chips" class="flex flex-wrap gap-2 pl-11 pt-0.5">
                        <button onclick="sendFloatingPreset('What is the total coal production for Q3?')" class="px-3.5 py-1.5 bg-white hover:bg-[#eefcce] text-gray-800 hover:text-[#111111] border border-gray-200 rounded-full text-[11px] font-extrabold transition-all shadow-2xs hover:scale-105 text-left">📊 Q3 Production Summary</button>
                        <button onclick="sendFloatingPreset('Reasons for delay in Gevra expansion clearance?')" class="px-3.5 py-1.5 bg-white hover:bg-[#ffebd6] text-gray-800 hover:text-[#111111] border border-gray-200 rounded-full text-[11px] font-extrabold transition-all shadow-2xs hover:scale-105 text-left">⚠️ Gevra Expansion Delays</button>
                        <button onclick="sendFloatingPreset('List major coalfields and active opencast mines in Jharkhand')" class="px-3.5 py-1.5 bg-white hover:bg-[#eefcce] text-gray-800 hover:text-[#111111] border border-gray-200 rounded-full text-[11px] font-extrabold transition-all shadow-2xs hover:scale-105 text-left">🗺️ Jharkhand Coalfields & Mines</button>
                    </div>
                `;
                if (window.lucide) lucide.createIcons();
            }}
        }}

        // Click Outside Auto-Close Behavior
        document.addEventListener('click', function(event) {{
            if (!isFloatingChatOpen) return;
            const chatWin = document.getElementById('geoai-floating-chat-window');
            const triggerBtn = document.getElementById('geoai-floating-trigger-container');
            const backdrop = document.getElementById('geoai-chat-backdrop');
            
            if (chatWin && !chatWin.contains(event.target) && triggerBtn && !triggerBtn.contains(event.target)) {{
                closeFloatingChat();
            }}
        }});
    </script>
'''

html = html.replace('</body>', f'{page_and_floating_scripts}\n</body>')

with open(ORIGINAL_HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated original_render_index.html with Query Studio, Left Chat History Panel, and Floating Bot!")
