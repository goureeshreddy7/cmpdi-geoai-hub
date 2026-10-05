"""
generate_mock_docs.py
Generates official mock technical report documents in data/mock_documents/
for all 12 referenced CMPDI repository documents.
"""

import os
import json

DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_documents')
os.makedirs(DOCS_DIR, exist_ok=True)

DOCUMENTS = [
    {
        'id': 'SECL-GEVRA-OCP-2024',
        'title': 'SECL Gevra Mega-Opencast Pit Phase-VI HEMM & Overburden Removal Audit',
        'type': 'Annual Mine Performance Audit',
        'subsidiary': 'SECL Bilaspur',
        'publishedDate': 'Aug 2024',
        'pages': 188,
        'summary': 'Central Mine Planning & Design Institute (CMPDI) comprehensive technical audit for SECL Gevra Mega-Opencast Pit Phase-VI expansion.',
        'seams': [
            {'horizon': 'Seam X (Top Horizon)', 'thickness': '6.40 m', 'depth': '112 m', 'ash': '18.4%', 'gcv': '6,240 kcal/kg', 'grade': 'G4'},
            {'horizon': 'Seam IX (Middle Horizon)', 'thickness': '8.20 m', 'depth': '148 m', 'ash': '22.1%', 'gcv': '5,820 kcal/kg', 'grade': 'G6'},
            {'horizon': 'Seam VIII (Bottom Horizon)', 'thickness': '4.80 m', 'depth': '194 m', 'ash': '26.5%', 'gcv': '5,310 kcal/kg', 'grade': 'G8'}
        ],
        'sections': [
            ('1. Pit Geometry & Stripping Sequence', 'Walking dragline side-casting handled over 42.6 MCuM of overburden in harmony with rapid shovel-dumper circuit synchronization. Current operating bench slope angle maintained at 45 degrees conforming to DGMS guidelines.'),
            ('2. HEMM Fleet Productivity', '42 CuM electric rope shovels matched with 240T dumpers recorded average fleet availability of 87.2% against CIL benchmark of 85.0%. Total truck cycle turnaround time optimized to 18.4 minutes.'),
            ('3. Geotechnical Stability & Sump Drainage', 'Continuous interferometric slope stability radar detected 0.02 mm bench displacement, validating highwall integrity. Sump dewatering capacity of 18,000 GPM effectively drained seasonal monsoon inflows without production curtailment.')
        ]
    },
    {
        'id': 'PQ-LS-UNSTARRED-4052',
        'title': 'Lok Sabha Unstarred Question No. 4052 — Coal Production Targets & Overburden Removal',
        'type': 'Parliamentary Inquiry Response',
        'subsidiary': 'Ministry of Coal',
        'publishedDate': '24 Jul 2024',
        'pages': 14,
        'summary': 'Parliament of India, Lok Sabha Secretariat. Unstarred Question No. 4052 answered by Union Minister of Coal on 24th July 2024.',
        'sections': [
            ('Statement Laid on the Table of the Lok Sabha', 'In response to Unstarred Question No. 4052 regarding coal output targets across Coal India Limited subsidiaries, total national coal production reached 773.6 Million Tonnes with a growth of 10.1% over previous fiscal year.'),
            ('Subsidiary-wise Performance Ledger', 'SECL achieved 167.0 MT, NCL achieved 131.0 MT, and MCL achieved 193.0 MT. Specific capital investments deployed for high-capacity continuous miners, rapid loading silos, and railway evacuation links.')
        ]
    },
    {
        'id': 'PQ-RS-STARRED-219',
        'title': 'Rajya Sabha Starred Question No. 219 — Highwall Slope Stability & Sump Dewatering',
        'type': 'Parliamentary Inquiry Response',
        'subsidiary': 'Ministry of Coal',
        'publishedDate': '12 Aug 2024',
        'pages': 18,
        'summary': 'Parliament of India, Rajya Sabha Official Record. Starred Question No. 219 answered on 12th August 2024.',
        'sections': [
            ('Oral Answer on Highwall Safety Standards', 'The Minister of Coal confirmed that all 14 mega opencast mines operating with bench heights exceeding 60m are equipped with real-time slope stability radars (SSR) with 24x7 geotechnical monitoring.'),
            ('Zero Effluent Discharge Protocols', 'All mine drainage effluents are channelled through modular multi-stage settling lagoons. Over 82% of treated pit water is recycled for dust suppression, industrial washeries, and regional irrigation.')
        ]
    }
]

# Generate template HTML for all documents
for doc in DOCUMENTS:
    filepath = os.path.join(DOCS_DIR, f"{doc['id']}.html")
    seam_table_html = ""
    if 'seams' in doc:
        rows = "".join([f"<tr><td style='padding:8px;border:1px solid #D9DCD8;font-weight:bold;'>{s['horizon']}</td><td style='padding:8px;border:1px solid #D9DCD8;'>{s['thickness']}</td><td style='padding:8px;border:1px solid #D9DCD8;'>{s['depth']}</td><td style='padding:8px;border:1px solid #D9DCD8;'>{s['ash']}</td><td style='padding:8px;border:1px solid #D9DCD8;'>{s['gcv']}</td><td style='padding:8px;border:1px solid #D9DCD8;font-weight:bold;color:#B0420C;'>{s['grade']}</td></tr>" for s in doc['seams']])
        seam_table_html = f"""
        <h3 style="margin-top:24px;margin-bottom:8px;font-size:14px;text-transform:uppercase;color:#16191C;border-bottom:1px solid #D9DCD8;padding-bottom:4px;">Stratigraphy & Coal Seams Breakdown</h3>
        <table style="width:100%;border-collapse:collapse;font-size:12px;margin-bottom:20px;">
            <thead>
                <tr style="background:#F5F6F4;text-align:left;">
                    <th style="padding:8px;border:1px solid #D9DCD8;">Seam Horizon</th>
                    <th style="padding:8px;border:1px solid #D9DCD8;">Thickness</th>
                    <th style="padding:8px;border:1px solid #D9DCD8;">Mean Depth</th>
                    <th style="padding:8px;border:1px solid #D9DCD8;">Ash %</th>
                    <th style="padding:8px;border:1px solid #D9DCD8;">GCV</th>
                    <th style="padding:8px;border:1px solid #D9DCD8;">Grade</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
        """

    sections_html = "".join([f"""
    <div style="margin-bottom:18px;">
        <h4 style="font-size:13px;font-weight:bold;color:#16191C;margin-bottom:6px;">{sec[0]}</h4>
        <p style="font-size:12px;line-height:1.6;color:#4F565D;margin:0;">{sec[1]}</p>
    </div>
    """ for sec in doc.get('sections', [])])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{doc['title']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #F5F6F4;
            color: #16191C;
            margin: 0;
            padding: 40px 20px;
        }}
        .document-container {{
            max-width: 820px;
            margin: 0 auto;
            background: #FFFFFF;
            border: 1px solid #D9DCD8;
            padding: 48px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        .header {{
            border-bottom: 2px solid #16191C;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .mock-badge {{
            display: inline-block;
            background: #FFF4E5;
            color: #B0420C;
            border: 1px solid #FBD38D;
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            padding: 2px 8px;
            border-radius: 4px;
            margin-bottom: 12px;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            padding: 12px 16px;
            font-size: 11px;
            margin-bottom: 24px;
        }}
    </style>
</head>
<body>
    <div class="document-container">
        <div class="header">
            <span class="mock-badge">MOCK DATA — ARCHIVE COPY</span>
            <div style="font-size:11px;color:#64748B;font-weight:700;letter-spacing:1px;text-transform:uppercase;">
                DOCUMENT ID: {doc['id']} &bull; {doc['type']} &bull; {doc['publishedDate']} &bull; {doc['pages']} PAGES
            </div>
            <h1 style="font-size:20px;font-weight:800;color:#16191C;margin-top:8px;margin-bottom:4px;line-height:1.3;">
                {doc['title']}
            </h1>
            <div style="font-size:12px;color:#4F565D;">
                Central Mine Planning & Design Institute &bull; Coal India Limited Repository
            </div>
        </div>

        <div class="meta-grid">
            <div><strong>Issuing Agency:</strong> {doc.get('subsidiary', 'CMPDI')}</div>
            <div><strong>Publication Date:</strong> {doc['publishedDate']}</div>
            <div><strong>Classification:</strong> Official Technical Record</div>
            <div><strong>Verification Status:</strong> Authenticated under ISP Norms</div>
        </div>

        <p style="font-size:13px;line-height:1.6;color:#334155;margin-bottom:20px;">
            {doc['summary']}
        </p>

        {seam_table_html}
        {sections_html}

        <div style="border-top:1px solid #D9DCD8;padding-top:16px;margin-top:32px;display:flex;justify-content:space-between;font-size:11px;color:#64748B;">
            <span>CMPDI Central Geo-Data Repository &bull; Certified Copy</span>
            <span>Ref: {doc['id']}</span>
        </div>
    </div>
</body>
</html>"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

print("Generated mock document preview files in data/mock_documents/")
