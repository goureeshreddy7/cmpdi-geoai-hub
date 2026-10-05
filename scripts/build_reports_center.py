"""
build_reports_center.py
Replaces the legacy 3-dropdown Reports view with the guided Report Builder
in original_render_index.html.
"""

import os
import re

ORIGINAL_HTML_PATH = os.path.join(os.path.dirname(__file__), '..', 'original_render_index.html')

with open(ORIGINAL_HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. New Guided Report Builder HTML for #page-reports
NEW_REPORTS_HTML = '''
                    <!-- ================= REPORTS CENTER (GUIDED ENTERPRISE BUILDER) ================= -->
                    <div id="page-reports" class="page-view flex-col space-y-5">
                        
                        <!-- Top Header & Action Controls Bar -->
                        <div class="bg-white rounded-2xl p-4 sm:p-5 border border-[#D9DCD8] shadow-2xs flex flex-wrap items-center justify-between gap-3">
                            <div>
                                <div class="flex items-center gap-2">
                                    <h2 class="text-base sm:text-lg font-black text-[#16191C] tracking-tight">Report Generator &amp; Parliamentary Brief Studio</h2>
                                    <span class="px-2 py-0.5 rounded text-[9px] font-bold uppercase bg-amber-100 text-amber-900 border border-amber-300">MOCK DATA V1</span>
                                </div>
                                <p class="text-xs text-[#4F565D] font-medium">Guided report compilation with provenance tracking for parliamentary replies, mine audits &amp; executive briefs.</p>
                            </div>

                            <div class="flex items-center gap-2 flex-wrap">
                                <button onclick="openDocumentViewerModal('SECL-GEVRA-OCP-2024')" class="px-3 py-1.5 rounded-lg bg-gray-100 hover:bg-gray-200 text-[#16191C] font-bold text-xs transition-all flex items-center gap-1.5 border border-gray-200">
                                    <i data-lucide="folder-search" class="w-3.5 h-3.5 text-[#B0420C]"></i>
                                    <span>Document Library (12)</span>
                                </button>
                                
                                <button onclick="saveCurrentReportConfig()" class="px-3 py-1.5 rounded-lg bg-white hover:bg-gray-50 text-[#16191C] font-bold text-xs transition-all flex items-center gap-1.5 border border-[#D9DCD8]">
                                    <i data-lucide="bookmark" class="w-3.5 h-3.5"></i>
                                    <span>Save Template</span>
                                </button>

                                <button onclick="executeReportExport('pdf')" class="px-3.5 py-1.5 rounded-lg bg-[#16191C] hover:bg-black text-white font-bold text-xs transition-all flex items-center gap-1.5 shadow-2xs">
                                    <i data-lucide="download" class="w-3.5 h-3.5"></i>
                                    <span>Export Report</span>
                                </button>
                            </div>
                        </div>

                        <!-- Main Two-Column Grid: Builder Wizard (Left) & Live Document Preview (Right) -->
                        <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
                            
                            <!-- LEFT COLUMN: 4-Step Builder Wizard -->
                            <div class="lg:col-span-5 flex flex-col space-y-3">
                                <div class="bg-white rounded-2xl border border-[#D9DCD8] shadow-2xs overflow-hidden flex flex-col h-full min-h-[640px]">
                                    
                                    <!-- Step Navigation Header -->
                                    <div id="report-wizard-step-tabs" class="flex border-b border-[#D9DCD8] bg-gray-50/70">
                                        <!-- Rendered dynamically -->
                                    </div>

                                    <!-- Step Body -->
                                    <div id="report-wizard-step-content" class="p-5 flex-1 overflow-y-auto custom-scrollbar">
                                        <!-- Rendered dynamically -->
                                    </div>

                                    <!-- Step Navigation Footer -->
                                    <div class="p-4 border-t border-[#D9DCD8] bg-gray-50/80 flex items-center justify-between">
                                        <button onclick="prevBuilderStep()" class="px-3.5 py-1.5 rounded-lg bg-white hover:bg-gray-100 border border-gray-300 text-gray-700 font-bold text-xs transition-all">
                                            &larr; Previous
                                        </button>
                                        <button onclick="nextBuilderStep()" class="px-4 py-1.5 rounded-lg bg-[#16191C] hover:bg-black text-white font-bold text-xs transition-all">
                                            Next Step &rarr;
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <!-- RIGHT COLUMN: Live Document Preview -->
                            <div class="lg:col-span-7 flex flex-col space-y-3">
                                <div class="bg-white rounded-2xl border border-[#D9DCD8] shadow-2xs overflow-hidden flex flex-col h-full min-h-[640px]">
                                    
                                    <!-- Preview Top Bar -->
                                    <div class="px-5 py-3 border-b border-[#D9DCD8] flex items-center justify-between bg-gray-50/80">
                                        <div class="flex items-center gap-2">
                                            <i data-lucide="file-text" class="w-4 h-4 text-[#B0420C]"></i>
                                            <h3 class="font-bold text-xs uppercase tracking-wider text-[#16191C]">Official Document Live Preview</h3>
                                        </div>
                                        
                                        <div class="flex items-center gap-1.5">
                                            <span class="text-[10px] font-mono text-gray-400">Click text to edit inline</span>
                                            <button onclick="executeReportExport('pdf')" class="px-2.5 py-1 rounded bg-white hover:bg-gray-100 border border-gray-300 text-gray-700 font-bold text-[11px] transition-all" title="Print/PDF">
                                                PDF
                                            </button>
                                            <button onclick="executeReportExport('excel')" class="px-2.5 py-1 rounded bg-white hover:bg-gray-100 border border-gray-300 text-gray-700 font-bold text-[11px] transition-all" title="Excel Dataset">
                                                Excel
                                            </button>
                                        </div>
                                    </div>

                                    <!-- Preview Scrollable Canvas -->
                                    <div class="p-6 overflow-y-auto max-h-[720px] custom-scrollbar bg-[#F5F6F4]">
                                        <div id="report-live-preview-document" class="max-w-2xl mx-auto">
                                            <!-- Rendered dynamically -->
                                        </div>
                                    </div>

                                </div>
                            </div>

                        </div>

                        <!-- Saved Configurations & Document Library Bar Below -->
                        <div class="bg-white rounded-2xl p-5 border border-[#D9DCD8] shadow-2xs space-y-3">
                            <div class="flex items-center justify-between border-b border-gray-200 pb-2">
                                <div>
                                    <h4 class="font-bold text-xs uppercase tracking-wider text-[#16191C]">Saved Report Templates</h4>
                                    <p class="text-[11px] text-gray-500 font-medium">Quick-load pre-configured parliamentary inquiries and monthly subsidiary review templates.</p>
                                </div>
                                <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-gray-100 text-gray-600">Local DAL Storage</span>
                            </div>
                            <div id="report-saved-templates-list" class="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <!-- Rendered dynamically -->
                            </div>
                        </div>

                    </div>

                    <!-- ================= VERIFICATION SOURCE SNAPSHOT MODAL ================= -->
                    <div id="report-verification-snapshot-modal" class="hidden fixed inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center p-3 sm:p-5 z-[99999]" onclick="closeVerificationSnapshotModal()">
                        <div class="bg-[#1E232A] rounded-2xl shadow-2xl border border-gray-700 w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden" onclick="event.stopPropagation()">
                            <div class="px-5 py-3.5 border-b border-gray-700/80 flex items-center justify-between bg-[#181C21]">
                                <div class="flex items-center gap-2">
                                    <span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                                    <span class="font-bold text-xs uppercase tracking-wider text-gray-200">Source Verification Snapshot</span>
                                    <span class="text-[10px] font-mono text-amber-300 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-600/40">Official Page Excerpt</span>
                                </div>
                                <button onclick="closeVerificationSnapshotModal()" class="w-7 h-7 rounded-full bg-gray-800 hover:bg-gray-700 flex items-center justify-center text-gray-400 hover:text-white font-bold">&times;</button>
                            </div>
                            <div id="report-snapshot-paper" class="p-5 sm:p-7 overflow-y-auto flex-1 custom-scrollbar bg-slate-100">
                                <!-- Rendered dynamically with official page replica and highlighted cited metric -->
                            </div>
                            <div class="px-5 py-3.5 border-t border-gray-700/80 bg-[#181C21] flex items-center justify-between">
                                <div class="text-[11px] text-gray-400 flex items-center gap-1.5 truncate max-w-[320px]">
                                    <i data-lucide="shield-check" class="w-3.5 h-3.5 text-emerald-400 shrink-0"></i>
                                    <span id="snapshot-provenance-caption" class="truncate font-mono">Authenticating Document: SECL-GEVRA-OCP-2024</span>
                                </div>
                                <div class="flex items-center gap-2">
                                    <button onclick="closeVerificationSnapshotModal()" class="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 font-bold text-xs transition-colors">
                                        Close
                                    </button>
                                    <button id="snapshot-view-full-doc-btn" class="px-4 py-2 rounded-xl bg-[#a3e635] hover:bg-[#bef264] text-black font-black text-xs transition-all flex items-center gap-2 shadow-md cursor-pointer">
                                        <i data-lucide="file-text" class="w-4 h-4"></i>
                                        <span>View Full Document &rarr;</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- ================= FULL TECHNICAL DOCUMENT VIEWER MODAL ================= -->
                    <div id="report-document-viewer-modal" class="hidden fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-2 sm:p-5 z-[99999]" onclick="closeDocumentViewerModal()">
                        <div class="bg-white rounded-2xl shadow-2xl border border-gray-300 w-full max-w-6xl h-[92vh] flex flex-col overflow-hidden" onclick="event.stopPropagation()">
                            <div class="px-6 py-3.5 border-b border-gray-200 flex items-center justify-between bg-gray-50/90 shrink-0">
                                <div class="flex items-center gap-2.5">
                                    <div class="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center text-[#B0420C]">
                                        <i data-lucide="book-open" class="w-4 h-4"></i>
                                    </div>
                                    <div>
                                        <div class="flex items-center gap-2">
                                            <span class="font-black text-xs uppercase tracking-wider text-[#16191C]">Technical Document Repository Archive</span>
                                            <span class="text-[9px] font-bold uppercase bg-amber-100 text-amber-900 border border-amber-300 px-2 py-0.5 rounded">AUTHENTIC RECORD</span>
                                        </div>
                                        <p id="doc-viewer-header-meta" class="text-[10px] text-gray-500 font-medium">CMPDI Regional Technical Repository &bull; Complete Verified Monograph</p>
                                    </div>
                                </div>
                                <div class="flex items-center gap-2">
                                    <button onclick="window.print()" class="px-3 py-1.5 rounded-lg bg-white hover:bg-gray-100 border border-gray-300 text-gray-700 font-bold text-xs transition-all flex items-center gap-1.5">
                                        <i data-lucide="printer" class="w-3.5 h-3.5"></i>
                                        <span>Print</span>
                                    </button>
                                    <button onclick="closeDocumentViewerModal()" class="w-8 h-8 rounded-lg hover:bg-gray-200 flex items-center justify-center text-gray-600 font-bold text-lg">&times;</button>
                                </div>
                            </div>
                            <div id="report-document-viewer-body" class="overflow-hidden flex-1 flex flex-col">
                                <!-- Rendered dynamically -->
                            </div>
                        </div>
                    </div>

                    <!-- ================= QUERY TYPE CONFIGURATION POPUP WINDOW MODAL ================= -->
                    <div id="report-query-config-modal" class="hidden fixed inset-0 bg-black/75 backdrop-blur-sm flex items-center justify-center p-3 sm:p-6 z-[99999]" onclick="closeQueryConfigModal()">
                        <div class="bg-white rounded-2xl shadow-2xl border border-gray-300 w-full max-w-xl max-h-[90vh] flex flex-col overflow-hidden" onclick="event.stopPropagation()">
                            <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50/90">
                                <div class="flex items-center gap-2.5">
                                    <div id="query-config-modal-icon-container" class="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center text-[#B0420C]">
                                        <i data-lucide="settings" class="w-4 h-4"></i>
                                    </div>
                                    <div>
                                        <h3 id="query-config-modal-title" class="font-bold text-xs uppercase tracking-wider text-[#16191C]">Configure Reference Details</h3>
                                        <p id="query-config-modal-subtitle" class="text-[10px] text-gray-500 font-medium">Customize statutory parameters and scope</p>
                                    </div>
                                </div>
                                <button onclick="closeQueryConfigModal()" class="w-7 h-7 rounded hover:bg-gray-200 flex items-center justify-center text-gray-600 font-bold">&times;</button>
                            </div>
                            <div id="query-config-modal-body" class="p-6 overflow-y-auto flex-1 custom-scrollbar space-y-4 text-xs">
                                <!-- Rendered dynamically -->
                            </div>
                            <div class="px-6 py-3.5 border-t border-gray-200 bg-gray-50/90 flex items-center justify-between">
                                <button onclick="closeQueryConfigModal()" class="px-3.5 py-1.5 rounded-lg bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold text-xs transition-colors">
                                    Cancel
                                </button>
                                <button onclick="applyQueryConfigAndClose()" class="px-4 py-1.5 rounded-lg bg-[#16191C] hover:bg-black text-white font-bold text-xs transition-all shadow-xs flex items-center gap-1.5">
                                    <i data-lucide="check" class="w-3.5 h-3.5 text-[#a3e635]"></i>
                                    <span>Apply &amp; Update Report</span>
                                </button>
                            </div>
                        </div>
                    </div>


'''

# Find and replace #page-reports
old_reports_start = html.find('<!-- ================= REPORTS VIEW (ADMIN) ================= -->')
if old_reports_start == -1:
    old_reports_start = html.find('<div id="page-reports"')

old_reports_end = html.find('<!-- ================= INSIGHTS VIEW (ADMIN) ================= -->')

if old_reports_start != -1 and old_reports_end != -1:
    html = html[:old_reports_start] + NEW_REPORTS_HTML + '\n' + html[old_reports_end:]
    print("Replaced #page-reports with Guided Report Builder layout.")
else:
    print("WARNING: Could not find #page-reports bounds in original_render_index.html")

# 2. Read and embed the full Reports Center JS bundle inline before </body>
REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'reports')

with open(os.path.join(REPORTS_DIR, 'types.js'), 'r', encoding='utf-8') as f:
    types_js = f.read()
with open(os.path.join(REPORTS_DIR, 'mockData.js'), 'r', encoding='utf-8') as f:
    mock_data_js = f.read()
with open(os.path.join(REPORTS_DIR, 'reportsRepository.js'), 'r', encoding='utf-8') as f:
    repo_js = f.read()
with open(os.path.join(REPORTS_DIR, 'reportsBuilder.js'), 'r', encoding='utf-8') as f:
    builder_js = f.read()

inline_scripts_bundle = f'''
    <!-- ================= REPORTS CENTER INLINE JS BUNDLE ================= -->
    <script>
{types_js}

{mock_data_js}

{repo_js}

{builder_js}

        // Auto-initialize when navigating to #reports or on DOMContentLoaded
        document.addEventListener('DOMContentLoaded', () => {{
            if (typeof initReportsCenter === 'function') {{
                initReportsCenter();
            }}
        }});
        if (window.location.hash === '#reports') {{
            setTimeout(() => {{
                if (typeof initReportsCenter === 'function') initReportsCenter();
            }}, 100);
        }}
    </script>
'''

# Clean removal of any previous reports scripts
markers = [
    '<!-- ================= REPORTS CENTER INLINE JS BUNDLE',
    '<!-- Reports Center Data Access Layer & Guided Builder Engine -->',
    '<script src="reports/mockData.js"></script>'
]

for m in markers:
    pos = html.find(m)
    if pos != -1:
        body_pos = html.rfind('</body>')
        if body_pos != -1 and pos < body_pos:
            html = html[:pos] + html[body_pos:]

body_pos = html.rfind('</body>')
if body_pos != -1:
    html = html[:body_pos] + inline_scripts_bundle + '\n</body>' + html[body_pos + 7:]
else:
    html += inline_scripts_bundle

print("Embedded Reports Center inline bundle before </body> cleanly.")

with open(ORIGINAL_HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully updated original_render_index.html with full Reports Center!")
