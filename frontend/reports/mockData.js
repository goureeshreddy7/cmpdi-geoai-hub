/**
 * @file mockData.js
 * @description Master mock dataset for CMPDI RSHPS Reports Center.
 * VISIBLE LABEL: MOCK DATA FOR ENTERPRISE DEMONSTRATION PURPOSES ONLY.
 */

const IS_MOCK_ENV = true;
const MOCK_BANNER_TEXT = "MOCK DATA — For demonstration and system evaluation only. Not for official statutory submission.";

const MOCK_SUBSIDIARIES = [
    { id: 'SECL', name: 'South Eastern Coalfields Limited', hq: 'Bilaspur, Chhattisgarh', mineCount: 68, state: 'Chhattisgarh & MP' },
    { id: 'NCL', name: 'Northern Coalfields Limited', hq: 'Singrauli, Madhya Pradesh', mineCount: 10, state: 'Madhya Pradesh & UP' },
    { id: 'MCL', name: 'Mahanadi Coalfields Limited', hq: 'Sambalpur, Odisha', mineCount: 42, state: 'Odisha' },
    { id: 'WCL', name: 'Western Coalfields Limited', hq: 'Nagpur, Maharashtra', mineCount: 54, state: 'Maharashtra & MP' },
    { id: 'BCCL', name: 'Bharat Coking Coal Limited', hq: 'Dhanbad, Jharkhand', mineCount: 36, state: 'Jharkhand' },
    { id: 'CCL', name: 'Central Coalfields Limited', hq: 'Ranchi, Jharkhand', mineCount: 44, state: 'Jharkhand' },
    { id: 'ECL', name: 'Eastern Coalfields Limited', hq: 'Sanctoria, West Bengal', mineCount: 72, state: 'West Bengal & Jharkhand' },
    { id: 'NEC', name: 'North Eastern Coalfields', hq: 'Margherita, Assam', mineCount: 4, state: 'Assam' }
];

const MOCK_AREAS = [
    { id: 'SECL-KORBA', subsidiaryId: 'SECL', name: 'Korba Area', coalfield: 'Korba Coalfield' },
    { id: 'SECL-GEVRA', subsidiaryId: 'SECL', name: 'Gevra Area', coalfield: 'Korba Coalfield' },
    { id: 'SECL-DIPKA', subsidiaryId: 'SECL', name: 'Dipka Area', coalfield: 'Korba Coalfield' },
    { id: 'SECL-KUSMUNDA', subsidiaryId: 'SECL', name: 'Kusmunda Area', coalfield: 'Korba Coalfield' },
    { id: 'NCL-SINGRAULI', subsidiaryId: 'NCL', name: 'Singrauli Area', coalfield: 'Singrauli Coalfield' },
    { id: 'NCL-NIGAHI', subsidiaryId: 'NCL', name: 'Nigahi Area', coalfield: 'Singrauli Coalfield' },
    { id: 'MCL-TALCHER', subsidiaryId: 'MCL', name: 'Talcher Area', coalfield: 'Talcher Coalfield' },
    { id: 'MCL-IBVALLEY', subsidiaryId: 'MCL', name: 'Ib Valley Area', coalfield: 'Ib Valley Coalfield' },
    { id: 'WCL-NAGPUR', subsidiaryId: 'WCL', name: 'Nagpur Area', coalfield: 'Wardha Valley' },
    { id: 'WCL-UMRER', subsidiaryId: 'WCL', name: 'Umrer Area', coalfield: 'Umrer Coalfield' },
    { id: 'BCCL-DHANBAD', subsidiaryId: 'BCCL', name: 'Moonidih Western Area', coalfield: 'Jharia Coalfield' },
    { id: 'ECL-SANCTORIA', subsidiaryId: 'ECL', name: 'Raniganj North Area', coalfield: 'Raniganj Coalfield' }
];

const MOCK_MINES = [
    {
        id: 'SECL-GEVRA-OCP',
        name: 'Gevra OCP',
        subsidiary: 'SECL',
        area: 'Gevra Area',
        coalfield: 'Korba Coalfield',
        type: 'Opencast',
        capacity: 70.0,
        status: 'Active',
        lastReportedMonth: '2025-03',
        seams: [
            { horizon: 'Seam X (Top)', thickness: 6.40, depth: 112, ashPercent: 18.4, gcv: 6240, grade: 'G4' },
            { horizon: 'Seam IX (Middle)', thickness: 8.20, depth: 148, ashPercent: 22.1, gcv: 5820, grade: 'G6' },
            { horizon: 'Seam VIII (Bottom)', thickness: 4.80, depth: 194, ashPercent: 26.5, gcv: 5310, grade: 'G8' }
        ]
    },
    {
        id: 'SECL-KUSMUNDA-OCP',
        name: 'Kusmunda OCP',
        subsidiary: 'SECL',
        area: 'Kusmunda Area',
        coalfield: 'Korba Coalfield',
        type: 'Opencast',
        capacity: 50.0,
        status: 'Active',
        lastReportedMonth: '2025-03',
        seams: [
            { horizon: 'Lower Kusmunda', thickness: 24.5, depth: 95, ashPercent: 34.2, gcv: 4200, grade: 'G11' },
            { horizon: 'Upper Kusmunda', thickness: 18.0, depth: 60, ashPercent: 38.0, gcv: 3800, grade: 'G13' }
        ]
    },
    {
        id: 'SECL-DIPKA-OCP',
        name: 'Dipka OCP',
        subsidiary: 'SECL',
        area: 'Dipka Area',
        coalfield: 'Korba Coalfield',
        type: 'Opencast',
        capacity: 40.0,
        status: 'Active',
        lastReportedMonth: '2025-03',
        seams: [
            { horizon: 'Dipka Seam', thickness: 28.0, depth: 130, ashPercent: 35.8, gcv: 4100, grade: 'G12' }
        ]
    },
    {
        id: 'SECL-MANIKPUR-OCP',
        name: 'Manikpur OCP',
        subsidiary: 'SECL',
        area: 'Korba Area',
        coalfield: 'Korba Coalfield',
        type: 'Opencast',
        capacity: 5.2,
        status: 'Active',
        lastReportedMonth: '2025-02', // Seeded Gap: Missing Mar-May 2025
        missingMonths: ['2025-03', '2025-04', '2025-05'],
        seams: [
            { horizon: 'Manikpur Main', thickness: 12.0, depth: 85, ashPercent: 39.5, gcv: 3600, grade: 'G14' }
        ]
    },
    {
        id: 'NCL-JAYANT-OCP',
        name: 'Jayant OCP',
        subsidiary: 'NCL',
        area: 'Singrauli Area',
        coalfield: 'Singrauli Coalfield',
        type: 'Opencast',
        capacity: 25.0,
        status: 'Active',
        lastReportedMonth: '2025-03',
        seams: [
            { horizon: 'Purewa Top', thickness: 8.5, depth: 75, ashPercent: 28.4, gcv: 5100, grade: 'G9' },
            { horizon: 'Purewa Bottom', thickness: 11.2, depth: 110, ashPercent: 31.0, gcv: 4700, grade: 'G10' },
            { horizon: 'Turra', thickness: 14.8, depth: 165, ashPercent: 22.0, gcv: 5800, grade: 'G6' }
        ]
    },
    {
        id: 'NCL-NIGAHI-OCP',
        name: 'Nigahi OCP',
        subsidiary: 'NCL',
        area: 'Nigahi Area',
        coalfield: 'Singrauli Coalfield',
        type: 'Opencast',
        capacity: 21.0,
        status: 'Active',
        lastReportedMonth: '2025-03',
        seams: [
            { horizon: 'Purewa Seam', thickness: 19.5, depth: 120, ashPercent: 29.5, gcv: 4950, grade: 'G9' },
            { horizon: 'Turra Seam', thickness: 15.2, depth: 180, ashPercent: 21.5, gcv: 5900, grade: 'G5' }
        ]
    },
    {
        id: 'NCL-DUDHICHUA-OCP',
        name: 'Dudhichua OCP',
        subsidiary: 'NCL',
        area: 'Singrauli Area',
        coalfield: 'Singrauli Coalfield',
        type: 'Opencast',
        capacity: 20.0,
        status: 'Active',
        lastReportedMonth: '2025-03',
        seams: [
            { horizon: 'Turra Main', thickness: 16.0, depth: 145, ashPercent: 23.0, gcv: 5700, grade: 'G7' }
        ]
    },
    {
        id: 'NCL-JHINGURDAH-OCP',
        name: 'Jhingurdah OCP',
        subsidiary: 'NCL',
        area: 'Singrauli Area',
        coalfield: 'Singrauli Coalfield',
        type: 'Opencast',
        capacity: 3.0,
        status: 'Active',
        lastReportedMonth: '2025-03',
        seams: [
            { horizon: 'Jhingurdah Top', thickness: 132.0, depth: 40, ashPercent: 42.0, gcv: 3200, grade: 'G15' }
        ]
    },
    {
        id: 'MCL-LINGARAJ-OCP',
        name: 'Lingaraj OCP',
        subsidiary: 'MCL',
        area: 'Talcher Area',
        coalfield: 'Talcher Coalfield',
        type: 'Opencast',
        capacity: 20.0,
        status: 'Active',
        lastReportedMonth: '2025-03',
        seams: [
            { horizon: 'Seam II Top', thickness: 14.2, depth: 65, ashPercent: 36.5, gcv: 3900, grade: 'G13' },
            { horizon: 'Seam III Bottom', thickness: 18.5, depth: 110, ashPercent: 38.0, gcv: 3750, grade: 'G13' }
        ]
    },
    {
        id: 'MCL-BHARATPUR-OCP',
        name: 'Bharatpur OCP',
        subsidiary: 'MCL',
        area: 'Talcher Area',
        coalfield: 'Talcher Coalfield',
        type: 'Opencast',
        capacity: 15.0,
        status: 'Active',
        lastReportedMonth: '2024-12', // Seeded Gap: Missing Jan-Feb 2025
        missingMonths: ['2025-01', '2025-02'],
        seams: [
            { horizon: 'Bharatpur Horizon', thickness: 22.0, depth: 95, ashPercent: 37.0, gcv: 3850, grade: 'G13' }
        ]
    },
    {
        id: 'MCL-LAKHANPUR-OCP',
        name: 'Lakhanpur OCP',
        subsidiary: 'MCL',
        area: 'Ib Valley Area',
        coalfield: 'Ib Valley Coalfield',
        type: 'Opencast',
        capacity: 21.0,
        status: 'Active',
        lastReportedMonth: '2025-03',
        seams: [
            { horizon: 'Ib Seam Main', thickness: 31.0, depth: 80, ashPercent: 35.0, gcv: 4150, grade: 'G12' }
        ]
    },
    {
        id: 'WCL-GONDEGAON-OCP',
        name: 'Gondegaon OCP',
        subsidiary: 'WCL',
        area: 'Nagpur Area',
        coalfield: 'Wardha Valley',
        type: 'Opencast',
        capacity: 3.5,
        status: 'Active',
        lastReportedMonth: '2025-03',
        seams: [
            { horizon: 'Gondegaon Seam I', thickness: 7.2, depth: 85, ashPercent: 27.5, gcv: 5200, grade: 'G8' }
        ]
    },
    {
        id: 'WCL-UMRER-OCP',
        name: 'Umrer OCP',
        subsidiary: 'WCL',
        area: 'Umrer Area',
        coalfield: 'Umrer Coalfield',
        type: 'Opencast',
        capacity: 4.2,
        status: 'Active',
        lastReportedMonth: '2025-03',
        seams: [
            { horizon: 'Umrer Composite', thickness: 9.8, depth: 115, ashPercent: 25.0, gcv: 5500, grade: 'G7' }
        ]
    },
    {
        id: 'BCCL-MOONIDIH-UG',
        name: 'Moonidih UG Mine',
        subsidiary: 'BCCL',
        area: 'Moonidih Western Area',
        coalfield: 'Jharia Coalfield',
        type: 'Underground',
        capacity: 2.5,
        status: 'Stale',
        lastReportedMonth: '2024-11', // Seeded Gap: Stale data (last reported 4 months ago)
        isStale: true,
        staleReason: 'Underground longwall face electrification modernization. Last telemetry sync Nov 2024 (4 months ago).',
        seams: [
            { horizon: 'Seam XVI (Top Coking)', thickness: 3.4, depth: 380, ashPercent: 16.5, gcv: 6700, grade: 'Prime Coking' },
            { horizon: 'Seam XV (Bottom Coking)', thickness: 4.2, depth: 450, ashPercent: 17.8, gcv: 6500, grade: 'Prime Coking' }
        ]
    },
    {
        id: 'ECL-JKNAGAR-UG',
        name: 'J.K. Nagar UG Mine',
        subsidiary: 'ECL',
        area: 'Raniganj North Area',
        coalfield: 'Raniganj Coalfield',
        type: 'Underground',
        capacity: 1.8,
        status: 'Active',
        lastReportedMonth: '2025-03',
        seams: [
            { horizon: 'Dishergarh Seam', thickness: 3.8, depth: 320, ashPercent: 14.5, gcv: 6900, grade: 'G2' }
        ]
    }
];

// Helper to generate 24 months time-series (April 2023 to March 2025)
const MONTHS_24 = [
    '2023-04', '2023-05', '2023-06', '2023-07', '2023-08', '2023-09',
    '2023-10', '2023-11', '2023-12', '2024-01', '2024-02', '2024-03',
    '2024-04', '2024-05', '2024-06', '2024-07', '2024-08', '2024-09',
    '2024-10', '2024-11', '2024-12', '2025-01', '2025-02', '2025-03'
];

/**
 * Seed 24 months of metrics per mine with intentional gaps.
 */
function buildMockTimeSeriesDatabase() {
    const db = {};

    MOCK_MINES.forEach(mine => {
        db[mine.id] = {
            production: [],
            offtake: [],
            ob_removal: [],
            stripping_ratio: [],
            hemm_utilisation: [],
            oms: [],
            accidents: []
        };

        const baseCapacityMonthly = mine.capacity / 12.0;
        const isUG = mine.type === 'Underground';

        MONTHS_24.forEach((period, idx) => {
            // Apply intentional gaps
            if (mine.id === 'SECL-MANIKPUR-OCP' && ['2025-03', '2025-04', '2025-05'].includes(period)) {
                return; // Skip missing month
            }
            if (mine.id === 'MCL-BHARATPUR-OCP' && ['2025-01', '2025-02'].includes(period)) {
                return; // Skip missing month
            }
            if (mine.id === 'BCCL-MOONIDIH-UG' && ['2024-12', '2025-01', '2025-02', '2025-03'].includes(period)) {
                return; // Stale data cutoff
            }

            // Seasonal production curve (Monsoon dip in Jul-Aug, high in Feb-Mar)
            const monthNum = parseInt(period.split('-')[1]);
            let seasonality = 1.0;
            if (monthNum === 7 || monthNum === 8) seasonality = 0.78;
            else if (monthNum === 1 || monthNum === 2 || monthNum === 3) seasonality = 1.18;
            else if (monthNum === 10 || monthNum === 11) seasonality = 1.05;

            // Trend factor over 24 months
            const trend = 1.0 + (idx * 0.006);
            const variation = (Math.sin(idx * 1.5) * 0.05);

            // Production (MT)
            const prodTarget = +(baseCapacityMonthly * 1.02).toFixed(2);
            const prodVal = +Math.max(0.1, (baseCapacityMonthly * seasonality * trend + variation)).toFixed(2);
            
            // Offtake (MT)
            const offtakeTarget = +(prodTarget * 0.98).toFixed(2);
            const offtakeVal = +(prodVal * (0.95 + Math.random() * 0.06)).toFixed(2);

            // OB Removal (Mcum) & Stripping Ratio
            const baseSR = isUG ? 0 : (mine.id.includes('GEVRA') ? 3.8 : (mine.id.includes('KUSMUNDA') ? 2.4 : 2.9));
            const obTarget = +(prodTarget * baseSR).toFixed(2);
            const obVal = +(prodVal * (baseSR + (Math.sin(idx) * 0.2))).toFixed(2);
            const srVal = isUG ? 0 : +(obVal / prodVal).toFixed(2);

            // HEMM Utilisation %
            const hemmTarget = 85.0;
            const hemmVal = isUG ? 0 : +(74.0 + (seasonality * 12.0) + (Math.sin(idx) * 3.5)).toFixed(1);

            // OMS (Tonnes per manshift)
            const baseOMS = isUG ? 2.8 : (mine.capacity > 30 ? 28.5 : 14.2);
            const omsVal = +(baseOMS * (0.92 + (seasonality * 0.12))).toFixed(2);

            // Accidents / Safety
            const accidentCount = Math.random() > 0.88 ? 1 : 0;

            const sourceDocId = mine.id.includes('GEVRA') ? 'SECL-GEVRA-OCP-2024' : 
                               (mine.subsidiary === 'NCL' ? 'NCL-MONTHLY-REV-2024' : 'SECL-PROD-REV-2024');
            const pageNum = 12 + (idx % 18);

            const sourceRef = {
                documentId: sourceDocId,
                page: pageNum,
                asOfDate: `${period}-28`,
                docTitle: `Verified Technical Ledger for ${mine.name}`,
                table: `Section 4.1: Monthly Ledger for ${period}`
            };

            db[mine.id].production.push({ period, value: prodVal, target: prodTarget, unit: 'MT', source: sourceRef });
            db[mine.id].offtake.push({ period, value: offtakeVal, target: offtakeTarget, unit: 'MT', source: sourceRef });
            db[mine.id].ob_removal.push({ period, value: obVal, target: obTarget, unit: 'Mcum', source: sourceRef });
            db[mine.id].stripping_ratio.push({ period, value: srVal, target: baseSR, unit: 'CuM/T', source: sourceRef });
            db[mine.id].hemm_utilisation.push({ period, value: hemmVal, target: hemmTarget, unit: '%', source: sourceRef });
            db[mine.id].oms.push({ period, value: omsVal, target: baseOMS, unit: 'Tonnes', source: sourceRef });
            db[mine.id].accidents.push({ period, value: accidentCount, target: 0, unit: 'Count', source: { ...sourceRef, documentId: 'DGMS-SAFETY-AUDIT-2024' } });
        });
    });

    return db;
}

const MOCK_METRICS_TIME_SERIES = buildMockTimeSeriesDatabase();

const MOCK_DOCUMENTS = [
    {
        id: 'SECL-GEVRA-OCP-2024',
        title: 'SECL Gevra Mega-Opencast Pit Phase-VI HEMM & Overburden Removal Audit',
        type: 'Annual Mine Performance Audit',
        subsidiary: 'SECL',
        mineId: 'SECL-GEVRA-OCP',
        publishedDate: 'Aug 2024',
        pageCount: 188,
        extractedText: `Central Mine Planning & Design Institute (CMPDI) technical audit for SECL Gevra Mega-Opencast Pit Phase-VI expansion. 
Coalfield basin: Korba Coalfield / Gondwana Basin. Mining method: Mechanized Opencast utilizing 42 CuM shovel and 240T dumper fleets with walking draglines. 
Stripping Ratio audited at 1:3.8 CuM/T. Geological Reserve status: Proved under ISP norms.
Stratigraphy and Seam analysis:
- Seam X (Top Horizon): 6.40 m thickness, 112 m mean depth, 18.4% ash content, 6,240 kcal/kg GCV, Grade G4.
- Seam IX (Middle Horizon): 8.20 m thickness, 148 m mean depth, 22.1% ash content, 5,820 kcal/kg GCV, Grade G6.
- Seam VIII (Bottom Horizon): 4.80 m thickness, 194 m mean depth, 26.5% ash content, 5,310 kcal/kg GCV, Grade G8.
Continuous highwall radar tracking indicates 0.02 mm bench displacement, validating geotechnical stability.`,
        keywords: { 'Overburden': 76, 'Stripping Ratio': 62, 'Extraction': 82, 'ROM Production': 59, 'Shovel-Dumper': 44, 'Slope Stability': 35 },
        seamTable: [
            { horizon: 'Seam X (Top)', thickness: 6.40, depth: 112, ashPercent: 18.4, gcv: 6240, grade: 'G4' },
            { horizon: 'Seam IX (Middle)', thickness: 8.20, depth: 148, ashPercent: 22.1, gcv: 5820, grade: 'G6' },
            { horizon: 'Seam VIII (Bottom)', thickness: 4.80, depth: 194, ashPercent: 26.5, gcv: 5310, grade: 'G8' }
        ],
        fileUrl: '/data/mock_documents/SECL-GEVRA-OCP-2024.pdf'
    },
    {
        id: 'PQ-LS-UNSTARRED-4052',
        title: 'Lok Sabha Unstarred Question No. 4052 — Coal Production Targets & Overburden Removal',
        type: 'Parliamentary Inquiry Response',
        subsidiary: 'CIL',
        publishedDate: '24 Jul 2024',
        pageCount: 14,
        extractedText: `Parliament of India, Lok Sabha Secretariat. Unstarred Question No. 4052 answered by Union Minister of Coal on 24th July 2024.
Subject: Target vs Actual production in major opencast coal mines including Gevra, Kusmunda, Nigahi, and Lingaraj. 
Total coal production across CIL subsidiaries reached 773.6 Million Tonnes with a growth of 10.1%. 
Overburden removal across opencast pits stood at 1,960 Million CuM. Specific measures undertaken for enhanced HEMM utilization, silo dispatch, and environmental mitigation outlined.`,
        keywords: { 'Parliamentary': 42, 'Production': 68, 'Overburden': 38, 'Gevra': 24, 'Target': 52 },
        fileUrl: '/data/mock_documents/PQ-LS-UNSTARRED-4052.pdf'
    },
    {
        id: 'PQ-RS-STARRED-219',
        title: 'Rajya Sabha Starred Question No. 219 — Highwall Slope Stability & Sump Dewatering',
        type: 'Parliamentary Inquiry Response',
        subsidiary: 'CIL',
        publishedDate: '12 Aug 2024',
        pageCount: 18,
        extractedText: `Parliament of India, Rajya Sabha Official Record. Starred Question No. 219 answered on 12th August 2024.
Subject: DGMS Safety Guidelines and Monsoon Dewatering Preparedness across Opencast Mines in SECL, NCL, and MCL.
The Minister placed on the table of the House comprehensive audit data covering piezometer installation, slope stability radars, and zero effluent discharge protocols. 
All highwall benches exceeding 60m height operate with dedicated slope radar telemetry.`,
        keywords: { 'Safety': 55, 'Slope Stability': 48, 'Groundwater': 36, 'DGMS': 41 },
        fileUrl: '/data/mock_documents/PQ-RS-STARRED-219.pdf'
    },
    {
        id: 'SECL-PROD-REV-2024',
        title: 'SECL Monthly Production & Despatch Performance Review Ledger',
        type: 'Monthly Dispatch & Yield Ledger',
        subsidiary: 'SECL',
        publishedDate: 'Aug 2024',
        pageCount: 92,
        extractedText: `South Eastern Coalfields Limited official consolidated output ledger. 
Monthly dispatch reconciliation for Gevra, Kusmunda, Dipka, and Manikpur mines. 
Gevra OCP achieved 5.85 MT production in August 2024, maintaining cumulative FY off-take trajectory of 104.2% of target. 
Rake loading through rapid loading system (RLS) averaged 38 rakes/day.`,
        keywords: { 'Extraction': 88, 'Offtake': 72, 'Despatch': 64, 'ROM Production': 58 },
        fileUrl: '/data/mock_documents/SECL-PROD-REV-2024.pdf'
    },
    {
        id: 'NCL-MONTHLY-REV-2024',
        title: 'NCL Singrauli Fleet Availability & Overburden Extraction Ledger',
        type: 'Monthly Dispatch & Yield Ledger',
        subsidiary: 'NCL',
        publishedDate: 'Sep 2024',
        pageCount: 84,
        extractedText: `Northern Coalfields Limited Singrauli Headquarters performance summary. 
Jayant, Nigahi, Dudhichua, and Jhingurdah mines collective output analysis. 
Heavy earthmoving machinery (HEMM) availability stood at 86.4% against CIL benchmark of 85.0%. 
Total Overburden handled: 44.8 Million CuM. Turra and Purewa seam extraction parameters verified.`,
        keywords: { 'HEMM': 65, 'Availability': 58, 'Overburden': 70, 'Extraction': 62 },
        fileUrl: '/data/mock_documents/NCL-MONTHLY-REV-2024.pdf'
    },
    {
        id: 'DGMS-SAFETY-AUDIT-2024',
        title: 'DGMS Annual Safety Audit & Occupational Hazard Assessment Monograph',
        type: 'Statutory Safety Audit',
        subsidiary: 'CMPDI',
        publishedDate: 'Jul 2024',
        pageCount: 112,
        extractedText: `Directorate General of Mines Safety (DGMS) comprehensive annual audit report.
Zero fatal accidents recorded across mechanised opencast mega-pits in Korba and Singrauli during Q1-Q2 2024. 
Underground strata control monitoring in Moonidih and J.K. Nagar validated for hydraulic prop resistance and continuous methane drainage.`,
        keywords: { 'Safety': 92, 'DGMS': 78, 'Accident': 42, 'Strata Control': 39 },
        fileUrl: '/data/mock_documents/DGMS-SAFETY-AUDIT-2024.pdf'
    },
    {
        id: 'MOEFCC-ENV-CLEAR-2024',
        title: 'MoEFCC Environmental Clearance Compliance & Progressive Mine Closure Audit',
        type: 'Environmental Compliance Report',
        subsidiary: 'CMPDI',
        publishedDate: 'Jun 2024',
        pageCount: 146,
        extractedText: `Ministry of Environment, Forest and Climate Change (MoEFCC) compliance audit.
Assessment of compensatory afforestation, topsoil preservation, and biological reclamation across SECL, MCL, and NCL concessions. 
Internal overburden dumps totaling 210 hectares brought under thick native canopy afforestation with 88.5% survival rate.`,
        keywords: { 'Reclamation': 74, 'Groundwater': 62, 'Afforestation': 51, 'Mine Closure': 48 },
        fileUrl: '/data/mock_documents/MOEFCC-ENV-CLEAR-2024.pdf'
    },
    {
        id: 'CIL-LAND-RR-2024',
        title: 'Coal India Land Acquisition, Resettlement & Rehabilitation (R&R) Progress Note',
        type: 'Land & R&R Status Note',
        subsidiary: 'CIL',
        publishedDate: 'May 2024',
        pageCount: 78,
        extractedText: `Consolidated Land Acquisition status under Coal Bearing Areas (Acquisition & Development) Act, 1957.
Detailed progress on employment compensation, annuity payments, and resettlement colony infrastructure in SECL Gevra, Kusmunda, and MCL Talcher blocks. 
1,240 Project Affected Persons (PAPs) provided permanent employment packages in FY24.`,
        keywords: { 'Land': 82, 'Rehabilitation': 68, 'Compensation': 54, 'CBA Act': 41 },
        fileUrl: '/data/mock_documents/CIL-LAND-RR-2024.pdf'
    },
    {
        id: 'HEMM-FLEET-UTIL-2024',
        title: 'CMPDI Dragline & Shovel-Dumper Fleet Operational Utilisation Monograph',
        type: 'Equipment Engineering Study',
        subsidiary: 'CMPDI',
        publishedDate: 'Apr 2024',
        pageCount: 130,
        extractedText: `Engineering evaluation of high-capacity HEMM across 14 mega opencast mines.
Walking draglines operational efficiency averaged 6,120 working hours/year. 
Payload monitoring telematics installed on 1,420 dumpers showed 4.2% reduction in cycle turnaround time. Shovel-dumper matching ratio optimized to 1:5.2.`,
        keywords: { 'HEMM': 94, 'Dragline': 71, 'Shovel-Dumper': 83, 'Productivity': 62 },
        fileUrl: '/data/mock_documents/HEMM-FLEET-UTIL-2024.pdf'
    },
    {
        id: 'CMPDI-RES-STATEMENT-2024',
        title: 'CMPDI National Coal Reserves Balance Statement & Geological ISP Assessment',
        type: 'Geological Reserve Assessment',
        subsidiary: 'CMPDI',
        publishedDate: 'Mar 2024',
        pageCount: 220,
        extractedText: `National Coal Inventory Balance Sheet compiled by CMPDI.
India total geological coal resources estimated at 378.2 Billion Tonnes as of 1st April 2024. 
Proved reserves under Indian Standard Procedure (ISP) norms constitute 198.6 Billion Tonnes. 
Damodar Valley, Mahanadi, and Son-Mahanadi basins account for over 72% of prime opencast extractable reserves.`,
        keywords: { 'Geological Reserve': 96, 'ISP Norms': 68, 'Coal Seam': 74, 'Exploration': 81 },
        fileUrl: '/data/mock_documents/CMPDI-RES-STATEMENT-2024.pdf'
    },
    {
        id: 'MCL-TALCHER-BEN-2024',
        title: 'MCL Talcher Coal Washery Yield & Ash Content Reduction Technical Audit',
        type: 'Coal Beneficiation Technical Study',
        subsidiary: 'MCL',
        publishedDate: 'Feb 2024',
        pageCount: 88,
        extractedText: `MCL Talcher thermal coal beneficiation review. 
Heavy media cyclone circuits operating at 10 MTY throughput reduced ROM ash content from 41.2% to 33.8%, enhancing Gross Calorific Value (GCV) by 450 kcal/kg. 
Clean coal dispatch sent via dedicated Merry-Go-Round (MGR) rail corridors to NTPC Kaniha.`,
        keywords: { 'Beneficiation': 78, 'Ash Content': 69, 'Calorific Value': 58, 'MCL': 52 },
        fileUrl: '/data/mock_documents/MCL-TALCHER-BEN-2024.pdf'
    },
    {
        id: 'BCCL-UNDERGROUND-2024',
        title: 'BCCL Underground Strata Control & Continuous Miner Extraction Monograph',
        type: 'Geotechnical Safety Audit',
        subsidiary: 'BCCL',
        publishedDate: 'Jan 2024',
        pageCount: 104,
        extractedText: `Deep underground coking coal extraction analysis at Moonidih colliery.
Deployment of powered support longwall (PSLW) face in Seam XVI with continuous hydraulic pressure sensors. 
Methane drainage manifolds exhaust 28 m3/min of gas, maintaining intake airways below 0.2% CH4 concentration.`,
        keywords: { 'Underground': 84, 'Strata Control': 67, 'Methane': 52, 'Coking Coal': 61 },
        fileUrl: '/data/mock_documents/BCCL-UNDERGROUND-2024.pdf'
    }
];

const MOCK_SAVED_CONFIGS = [
    {
        id: 'cfg-gevra-monthly',
        name: 'Monthly Gevra Mega-OCP Performance Review',
        queryType: 'single_mine',
        subsidiaryIds: ['SECL'],
        mineIds: ['SECL-GEVRA-OCP'],
        periodType: 'FY24-25',
        startDate: '2024-04',
        endDate: '2025-03',
        sections: [
            { id: 'production', title: 'Coal Production & Despatch', enabled: true, presentation: 'table_chart' },
            { id: 'overburden', title: 'Overburden Removal & Stripping Ratio', enabled: true, presentation: 'table_chart' },
            { id: 'hemm', title: 'HEMM Fleet Utilisation', enabled: true, presentation: 'table' },
            { id: 'reserves', title: 'Stratigraphy & Coal Seams', enabled: true, presentation: 'table' },
            { id: 'safety', title: 'Safety & DGMS Compliance', enabled: true, presentation: 'narrative' }
        ],
        attachedSourceDocIds: ['SECL-GEVRA-OCP-2024', 'SECL-PROD-REV-2024'],
        createdAt: '2025-03-15T10:30:00Z'
    },
    {
        id: 'cfg-parliamentary-q4052',
        name: 'Lok Sabha Q. 4052 Multi-Mine Response Brief',
        queryType: 'parliamentary',
        parliamentaryMeta: {
            house: 'Lok Sabha',
            type: 'Unstarred',
            number: '4052',
            answerDate: '2024-07-24',
            ministry: 'Ministry of Coal'
        },
        subsidiaryIds: ['SECL', 'NCL', 'MCL'],
        mineIds: ['SECL-GEVRA-OCP', 'SECL-KUSMUNDA-OCP', 'NCL-JAYANT-OCP', 'MCL-LINGARAJ-OCP'],
        periodType: 'FY24-25',
        startDate: '2024-04',
        endDate: '2024-08',
        sections: [
            { id: 'production', title: 'Production Overview & Target Achievement', enabled: true, presentation: 'table' },
            { id: 'overburden', title: 'Overburden Removal & Stripping Ratio', enabled: true, presentation: 'table' },
            { id: 'safety', title: 'Mine Safety & Incident Records', enabled: true, presentation: 'table' },
            { id: 'environment', title: 'Environmental & Afforestation Status', enabled: true, presentation: 'narrative' }
        ],
        attachedSourceDocIds: ['PQ-LS-UNSTARRED-4052', 'SECL-GEVRA-OCP-2024', 'DGMS-SAFETY-AUDIT-2024'],
        createdAt: '2025-03-20T14:15:00Z'
    }
];

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        IS_MOCK_ENV,
        MOCK_BANNER_TEXT,
        MOCK_SUBSIDIARIES,
        MOCK_AREAS,
        MOCK_MINES,
        MOCK_METRICS_TIME_SERIES,
        MOCK_DOCUMENTS,
        MOCK_SAVED_CONFIGS,
        MONTHS_24
    };
}
