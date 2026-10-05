import os
import re

ORIGINAL_HTML_PATH = 'c:/Users/LENOVO/Downloads/final_cmpdi/cmpdi-geoai-hub-main/original_render_index.html'
AVATAR_B64_PATH = 'c:/Users/LENOVO/Downloads/final_cmpdi/cmpdi-geoai-hub-main/frontend/avatar_b64.txt'

with open(ORIGINAL_HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

with open(AVATAR_B64_PATH, 'r', encoding='utf-8') as f:
    avatar_b64 = f.read().strip()

# 1. Remove #nav-query from sidebar
nav_query_pattern = r'\s*<a href="#query" class="nav-btn admin-nav .*?id="nav-query">.*?</a>'
html = re.sub(nav_query_pattern, '', html, flags=re.DOTALL)

# 2. Remove #page-query
pq_start = html.find('<div id="page-query"')
if pq_start != -1:
    pq_comment = html.rfind('<!-- ================= AI QUERY VIEW', 0, pq_start)
    start_idx = pq_comment if pq_comment != -1 else pq_start
    next_comment = html.find('<!-- ========================================================================= -->', pq_start)
    if next_comment != -1:
        html = html[:start_idx] + html[next_comment:]
        print('Removed #page-query from original_render_index.html')

# 3. Remove inline user chat card from #page-user-upload
user_chat_str = '<!-- AI Chat for Users -->'
uc_start = html.find(user_chat_str)
if uc_start != -1:
    next_section = html.find('<!-- ================= VERIFY REPORTS VIEW (USER) ================= -->', uc_start)
    if next_section != -1:
        html = html[:uc_start] + html[next_section:]
        print('Removed inline user chat card from original_render_index.html')

# 4. Remove 'query' from pageMeta and router in original_render_index.html
html = re.sub(r"\s*'query': \{ title: 'GeoAI Query Assistant', subtitle: 'Talk directly to your institutional repositories' \},?", '', html)

# 5. Remove old chat functions from original_render_index.html
old_funcs_1 = r'async function handleUserChatSubmit\(e\) \{.*?async function clearUserChat\(\) \{.*?\n        \}'
html = re.sub(old_funcs_1, '', html, flags=re.DOTALL)

old_funcs_2 = r'// AI Chat Handlers \(Admin feature\).*?async function clearChat\(\) \{.*?\n        \}'
html = re.sub(old_funcs_2, '', html, flags=re.DOTALL)

# Remove any previous floating assistant markup if present before re-injecting
float_start = html.find('<!-- ================= FLOATING GEOAI ASSISTANT (NAMASTE BOT) ================= -->')
if float_start != -1:
    body_end = html.find('</body>', float_start)
    if body_end != -1:
        html = html[:float_start] + html[body_end:]

# Reposition alertBox so it appears at bottom-left and doesn't overlap the floating assistant
html = html.replace("box.className = 'fixed bottom-6 right-6 z-[150]", "box.className = 'fixed bottom-6 left-6 z-[150]")

# 6. Floating Assistant Widget HTML + CSS + JS to insert before </body>
floating_assistant_block = f'''
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

        /* Floating Window Expand Transitions */
        #geoai-floating-chat-window.chat-expanded {{
            width: 780px !important;
            height: 700px !important;
            max-width: calc(100vw - 32px) !important;
            max-height: calc(100vh - 40px) !important;
        }}

        #geoai-floating-chat-window {{
            transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1), 
                        height 0.3s cubic-bezier(0.16, 1, 0.3, 1), 
                        transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), 
                        opacity 0.25s ease-out;
        }}
    </style>

    <div id="geoai-floating-assistant-root" class="fixed bottom-6 right-6 z-[9999] font-['Inter',sans-serif] flex flex-col items-end pointer-events-none select-none">
        
        <!-- Floating Interactive Chat Window -->
        <div id="geoai-floating-chat-window" class="pointer-events-auto bg-white rounded-[2.25rem] border border-gray-200/90 shadow-[0_24px_70px_-15px_rgba(0,0,0,0.4),0_0_0_1px_rgba(0,0,0,0.06)] overflow-hidden flex flex-col origin-bottom-right mb-4 opacity-0 scale-95 translate-y-4 pointer-events-none" style="width: 420px; height: 580px; max-width: calc(100vw - 32px); max-height: calc(100vh - 110px); display: none;">
            
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

            <!-- Avatar Glowing Circle (Bigger 82px avatar) -->
            <div class="assistant-avatar-halo relative w-20 h-20 sm:w-[84px] sm:h-[84px] rounded-full border-[3.5px] border-[#a3e635] bg-white transition-all duration-300 group-hover:scale-105 group-active:scale-95 flex items-center justify-center p-0.5">
                <img src="{avatar_b64}" alt="GeoAI Assistant" class="w-full h-full object-cover rounded-full">
                
                <!-- Online status dot with inner white core -->
                <div class="absolute bottom-0.5 right-0.5 w-6 h-6 bg-[#84cc16] border-[2.5px] border-white rounded-full flex items-center justify-center shadow-md">
                    <div class="w-2 h-2 bg-white rounded-full"></div>
                </div>
            </div>

        </div>

    </div>

    <!-- Floating Assistant Core Controller Script -->
    <script>
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
            // Trigger animation frame
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
            if (!win) return;
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
            if (!win) return;
            isFloatingChatExpanded = !isFloatingChatExpanded;
            if (isFloatingChatExpanded) {{
                win.classList.add('chat-expanded');
                if (icon) icon.setAttribute('data-lucide', 'minimize-2');
            }} else {{
                win.classList.remove('chat-expanded');
                if (icon) icon.setAttribute('data-lucide', 'maximize-2');
            }}
            if (window.lucide) lucide.createIcons();
            const msgs = document.getElementById('floating-chat-messages');
            if (msgs) setTimeout(() => msgs.scrollTop = msgs.scrollHeight, 150);
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

            // Thinking / Pulsing Indicator
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
            
            if (chatWin && !chatWin.contains(event.target) && triggerBtn && !triggerBtn.contains(event.target)) {{
                closeFloatingChat();
            }}
        }});
    </script>
'''

html = html.replace('</body>', f'{floating_assistant_block}\n</body>')

with open(ORIGINAL_HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated original_render_index.html with adjusted sizes and adjacent positioning!")
