import os
import re

ORIGINAL_HTML_PATH = 'c:/Users/LENOVO/Downloads/final_cmpdi/cmpdi-geoai-hub-main/original_render_index.html'

with open(ORIGINAL_HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# Locate the Insights view in original_render_index.html
insights_start = html.find('<!-- ================= INSIGHTS VIEW (ADMIN) ================= -->')
if insights_start == -1:
    insights_start = html.find('<div id="page-insights"')

# Find the end of #page-insights
next_view_marker = '<!-- ================= AI QUERY STUDIO WITH CHAT HISTORY ================= -->'
if next_view_marker not in html:
    next_view_marker = '<!-- ========================================================================= -->'

insights_end = html.find(next_view_marker, insights_start)

if insights_start != -1 and insights_end != -1:
    print(f"Found page-insights from index {insights_start} to {insights_end}")
else:
    print("Could not find page-insights boundaries!")
