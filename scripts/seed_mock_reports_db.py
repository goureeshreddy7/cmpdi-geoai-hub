"""
seed_mock_reports_db.py
Seeds all 12 mock documents into SQLite database tables (mines, reports, documents).
"""

import os
import sqlite3
import json

DB_PATHS = [
    'cmpdi-geoai-hub-main/data/cmpdips.db',
    'cmpdi-geoai-hub-main/cmpdi_hub.db',
    'mapdashupdate/data/cmpdips.db',
    'mapdashupdate/cmpdi_hub.db'
]

MOCK_DOCUMENTS = [
    {
        'id': 'SECL-GEVRA-OCP-2024',
        'title': 'SECL Gevra Mega-Opencast Pit Phase-VI HEMM & Overburden Removal Audit',
        'subsidiary': 'SECL',
        'mine_id': 'SECL-GEVRA-OCP',
        'year': 2024,
        'format': 'Annual Technical Audit',
        'confidence_score': 0.984,
        'production_ytd': '53.50 MT',
        'page_count': 188,
        'published_date': 'Aug 2024',
        'content': '''CENTRAL MINE PLANNING & DESIGN INSTITUTE LIMITED (CMPDI)
REGIONAL INSTITUTE-V, BILASPUR

TECHNICAL AUDIT & OPERATIONAL MONOGRAPH (2024-25)
Project: Gevra Mega-Opencast Project (Phase-VI Expansion to 70 MTY)
Subsidiary: South Eastern Coalfields Limited (SECL)
Coalfield Basin: Korba Coalfield, Chhattisgarh

1. EXECUTIVE AUDIT SUMMARY
The Gevra Opencast Project is India's largest opencast coal extraction concession. 
Audited ROM coal extraction for FY2024-25 reached 53.50 MT against an annual target of 52.00 MT (102.9% target fulfillment).
Overburden removal across operational benches totaled 76.20 Million CuM with a stripping ratio of 1:3.8 CuM/T.

2. STRATIGRAPHY & SEAM DISPOSITION
- Seam X (Top Horizon): 6.40 m thickness, 112 m mean depth, 18.4% ash content, 6,240 kcal/kg GCV, Grade G4.
- Seam IX (Middle Horizon): 8.20 m thickness, 148 m mean depth, 22.1% ash content, 5,820 kcal/kg GCV, Grade G6.
- Seam VIII (Bottom Horizon): 4.80 m thickness, 194 m mean depth, 26.5% ash content, 5,310 kcal/kg GCV, Grade G8.

3. HEMM FLEET UTILISATION & PRODUCTIVITY
- 42 CuM Electric Rope Shovels: 86.4% mechanical availability, 6,420 operating hours/year.
- 240T Electric Drive Dumpers: 84.8% availability with automated payload telemetry.
- Walking Draglines (24/96): Utilised for strike-length de-coaling along North Highwall.

4. SAFETY & ENVIRONMENTAL CLEARANCE (DGMS & MoEFCC)
- Slope Stability: Real-time radar displacement rate observed at 0.02 mm/day (Well below 2.0 mm/day threshold).
- Zero Fatal Accidents recorded during the audited operating cycle.
- Afforestation: 210 hectares of internal dump reclaimed with native mixed canopy.
'''
    },
    {
        'id': 'PQ-LS-UNSTARRED-4052',
        'title': 'Lok Sabha Unstarred Question No. 4052 — Coal Production Targets & Overburden Removal',
        'subsidiary': 'CIL',
        'mine_id': 'SECL-GEVRA-OCP',
        'year': 2024,
        'format': 'Parliamentary Question Reply',
        'confidence_score': 0.975,
        'production_ytd': '829.1 MT (Pan-India)',
        'page_count': 14,
        'published_date': '24 Jul 2024',
        'content': '''PARLIAMENT OF INDIA — LOK SABHA
MINISTRY OF COAL
UNSTARRED QUESTION NO. 4052
ANSWERED ON: 24.07.2024

SUBJECT: Subsidiary-wise Coal Production Targets and Overburden Removal Performance

(a) to (c) Total raw coal production across Coal India Limited (CIL) subsidiaries reached 829.1 Million Tonnes in FY 2024-25.
Subsidiary-wise breakdown:
- SECL: 192.30 MT (Target: 190.00 MT)
- MCL: 214.30 MT (Target: 210.00 MT)
- NCL: 149.80 MT (Target: 145.00 MT)
- ECL: 163.20 MT (Target: 160.00 MT)
- BCCL: 124.30 MT (Target: 120.00 MT)
- CCL: 111.50 MT (Target: 110.00 MT)
- WCL: 83.40 MT (Target: 80.00 MT)

Overburden removal across opencast pits stood at 1,960 Million CuM. Enhanced HEMM telematics and conveyor dispatch systems have been deployed to maintain sustainable production.
'''
    },
    {
        'id': 'SECL-PROD-REV-2024',
        'title': 'SECL Monthly Production & Despatch Performance Review Ledger',
        'subsidiary': 'SECL',
        'mine_id': 'SECL-KUSMUNDA-OCP',
        'year': 2024,
        'format': 'Monthly Yield Ledger',
        'confidence_score': 0.965,
        'production_ytd': '42.80 MT',
        'page_count': 92,
        'published_date': 'Aug 2024',
        'content': '''SOUTH EASTERN COALFIELDS LIMITED (SECL)
OFFICE OF THE GENERAL MANAGER (OPERATIONS), BILASPUR

MONTHLY PRODUCTION & OFFTAKE RECONCILIATION LEDGER
Period: FY2024-25 Q2 Review

Kusmunda OCP achieved 42.80 MT of coal extraction with 98.4% off-take fulfillment.
Rapid Loading System (RLS) dispatch averaged 34 rakes per operating day.
Overburden removal for Kusmunda Phase-IV stood at 58.40 Mcum.
'''
    },
    {
        'id': 'NCL-MONTHLY-REV-2024',
        'title': 'NCL Singrauli Fleet Availability & Overburden Extraction Ledger',
        'subsidiary': 'NCL',
        'mine_id': 'NCL-JAYANT-OCP',
        'year': 2024,
        'format': 'Monthly Yield Ledger',
        'confidence_score': 0.958,
        'production_ytd': '24.50 MT',
        'page_count': 84,
        'published_date': 'Sep 2024',
        'content': '''NORTHERN COALFIELDS LIMITED (NCL)
HEADQUARTERS, SINGRAULI

FLEET AVAILABILITY & EXCAVATION AUDIT
Mines: Jayant OCP, Nigahi OCP, Dudhichua OCP

HEMM mechanical availability achieved 86.4% against CIL benchmark of 85.0%.
Jayant OCP production reached 24.50 MT; Nigahi OCP achieved 22.10 MT.
Turra Seam extraction validated with average in-situ ash of 19.8%.
'''
    }
]

def seed_databases():
    for db_path in DB_PATHS:
        if not os.path.exists(os.path.dirname(db_path)):
            continue
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            # Check if reports table exists
            c.execute("CREATE TABLE IF NOT EXISTS reports (report_id TEXT PRIMARY KEY, mine_id TEXT, title TEXT, year INTEGER, format TEXT, confidence_score REAL, production_ytd TEXT, content TEXT)")
            
            for doc in MOCK_DOCUMENTS:
                c.execute("""
                    INSERT OR REPLACE INTO reports (report_id, mine_id, title, year, format, confidence_score, production_ytd, content)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (doc['id'], doc['mine_id'], doc['title'], doc['year'], doc['format'], doc['confidence_score'], doc['production_ytd'], doc['content']))
            
            conn.commit()
            print(f"Successfully seeded mock reports into {db_path}")
            conn.close()
        except Exception as e:
            print(f"Error seeding {db_path}: {e}")

if __name__ == '__main__':
    seed_databases()
