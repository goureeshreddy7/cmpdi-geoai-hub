import re

with open('c:/Users/LENOVO/Downloads/final_cmpdi/cmpdi-geoai-hub-main/original_render_index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Leaflet & Custom Geological Map CSS in head
head_css_scripts = '''
    <!-- Leaflet & MarkerCluster CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css" />

    <style>
        .leaflet-container {
            font-family: 'Inter', sans-serif !important;
            border-radius: 1.75rem;
            outline: none !important;
            background: #f1f5f9;
        }
        
        #minesMapContainer:focus, .leaflet-container:focus, .leaflet-marker-icon:focus {
            outline: none !important;
        }
        
        /* ── Cluster Marker Styling ── */
        .custom-cluster-icon {
            background: #111111;
            color: #a3e635;
            border: 2.5px solid #a3e635;
            border-radius: 9999px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 12px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.35);
        }

        /* ── SVG Teardrop Pin Marker Styling ── */
        .mine-pin-container {
            background: transparent !important;
            border: none !important;
            outline: none !important;
        }
        .mine-pin-wrapper {
            position: relative;
            width: 26px;
            height: 36px;
            cursor: pointer;
            transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
            outline: none !important;
        }
        .mine-pin-wrapper:hover {
            transform: scale(1.2) translateY(-4px);
            z-index: 1000 !important;
        }
        .mine-pin-svg {
            display: block;
            filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.35));
        }
        .mine-pin-pulse {
            position: absolute;
            bottom: -3px;
            left: 50%;
            transform: translateX(-50%);
            width: 12px;
            height: 4px;
            border-radius: 50%;
            background: rgba(0, 0, 0, 0.25);
            filter: blur(1px);
        }

        /* ── Borehole Survey Marker Styling ── */
        .borehole-marker-icon {
            width: 18px;
            height: 18px;
            background: #0284c7;
            border: 2px solid #ffffff;
            border-radius: 4px;
            transform: rotate(45deg);
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        .borehole-marker-icon:hover {
            transform: rotate(45deg) scale(1.3);
            background: #0369a1;
            z-index: 1000 !important;
        }

        /* ── Hover Tooltip Pill Badge ── */
        .mine-tooltip-custom {
            background: #111111 !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 14px !important;
            padding: 5px 12px !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35) !important;
            color: #ffffff !important;
            font-family: 'Inter', sans-serif !important;
            z-index: 9999 !important;
            pointer-events: none;
        }
        .mine-tooltip-custom::before {
            border-top-color: #111111 !important;
        }
        .mine-pin-label {
            display: flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
        }
        .mine-pin-name {
            font-weight: 800;
            font-size: 11px;
            color: #ffffff;
            letter-spacing: -0.01em;
        }
        .mine-pin-tag {
            font-size: 9px;
            font-weight: 900;
            padding: 2px 7px;
            border-radius: 999px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            background: #a3e635;
            color: #111111;
        }

        /* ── Custom Popup Styling ── */
        .mine-popup .leaflet-popup-content-wrapper {
            background: #ffffff;
            border-radius: 1.5rem;
            padding: 6px;
            box-shadow: 0 20px 40px -8px rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(0, 0, 0, 0.06);
        }
        .mine-popup .leaflet-popup-tip {
            background: #ffffff;
        }
        .leaflet-container a.leaflet-popup-close-button {
            top: 12px;
            right: 12px;
            color: #9ca3af;
        }

        /* Floating Map Control Bar */
        .floating-map-layer-bar {
            position: absolute;
            top: 14px;
            right: 14px;
            z-index: 400;
            backdrop-filter: blur(8px);
        }

        /* Geological Layer Toggle Overlay */
        .geological-layer-toggles {
            position: absolute;
            bottom: 16px;
            left: 16px;
            z-index: 400;
            backdrop-filter: blur(10px);
        }

        /* Geological Map Legend */
        .geological-legend-box {
            position: absolute;
            bottom: 16px;
            right: 16px;
            z-index: 400;
            backdrop-filter: blur(10px);
        }
    </style>
'''
head_end = html.find('</head>')
if head_end != -1:
    html = html[:head_end] + f'{head_css_scripts}\n' + html[head_end:]


# 2. Add 'Mine Map' sidebar nav button right after 'Dashboard'
sidebar_map_btn = '''
                <a href="#map" class="nav-btn admin-nav w-12 h-12 lg:w-14 lg:h-14 rounded-2xl flex items-center justify-center relative z-10 group text-gray-400 hover:text-white hover:scale-105" id="nav-map">
                    <i data-lucide="map" class="w-6 h-6 stroke-[2.2]"></i>
                    <span class="active-indicator absolute left-1 top-3.5 w-1.5 h-7 bg-[#a3e635] rounded-r-full shadow-[0_0_8px_#a3e635]"></span>
                    <span class="nav-tooltip absolute left-20 bg-white text-[#111111] text-xs px-3 py-2 rounded-xl opacity-0 group-hover:opacity-100 pointer-events-none transition-all whitespace-nowrap z-[60] shadow-xl font-bold hidden lg:block border border-gray-100">Mine Map</span>
                </a>
'''
html = html.replace('<a href="#reports"', f'{sidebar_map_btn}\n                <a href="#reports"')

# 3. Add Spatial Mine Map View container before 'page-reports'
map_view_html = '''
                    <!-- ================= SPATIAL MINE MAP VIEW ================= -->
                    <div id="page-map" class="page-view flex-col space-y-6">
                        
                        <!-- Filter & Stats Bar -->
                        <div class="bg-white rounded-[2rem] p-5 border border-gray-200/80 shadow-xs flex flex-col gap-4">
                            <div class="flex flex-wrap items-center justify-between gap-4">
                                <div class="flex flex-wrap items-center gap-3 flex-1 min-w-[280px]">
                                    <!-- Search Input -->
                                    <div class="relative flex-1 min-w-[200px] max-w-xs">
                                        <i data-lucide="search" class="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2"></i>
                                        <input type="text" id="mapSearchInput" oninput="applyMapFiltersDebounced()" placeholder="Search coalfield, block, mine, state..." class="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-full text-xs font-semibold focus:ring-2 focus:ring-[#a3e635] focus:bg-white outline-none transition-all">
                                    </div>

                                    <!-- Subsidiary Filter -->
                                    <select id="mapSubsidiaryFilter" onchange="applyMapFilters()" class="px-3.5 py-2 bg-gray-50 border border-gray-200 rounded-full text-xs font-bold text-gray-700 outline-none focus:ring-2 focus:ring-[#a3e635] cursor-pointer">
                                        <option value="">All Subsidiaries</option>
                                    </select>

                                    <!-- State Filter -->
                                    <select id="mapStateFilter" onchange="applyMapFilters()" class="px-3.5 py-2 bg-gray-50 border border-gray-200 rounded-full text-xs font-bold text-gray-700 outline-none focus:ring-2 focus:ring-[#a3e635] cursor-pointer">
                                        <option value="">All States</option>
                                    </select>

                                    <!-- Mine Type Filter -->
                                    <select id="mapTypeFilter" onchange="applyMapFilters()" class="px-3.5 py-2 bg-gray-50 border border-gray-200 rounded-full text-xs font-bold text-gray-700 outline-none focus:ring-2 focus:ring-[#a3e635] cursor-pointer">
                                        <option value="">All Mine Types</option>
                                        <option value="Opencast">Opencast</option>
                                        <option value="Underground">Underground</option>
                                        <option value="Mixed">Mixed</option>
                                    </select>

                                    <!-- Basemap Selector -->
                                    <div class="flex items-center gap-1.5 bg-gray-50 border border-gray-200 rounded-full px-3 py-1.5 shadow-2xs hover:bg-white transition-all">
                                        <i data-lucide="layers" class="w-3.5 h-3.5 text-gray-500"></i>
                                        <select id="mapLayerSwitcher" onchange="switchMapBaseLayer(this.value)" class="bg-transparent text-xs font-bold text-gray-800 outline-none cursor-pointer">
                                            <option value="gis">GIS Layer View</option>
                                            <option value="geological">Geological Coalfield Map</option>
                                            <option value="satellite">Satellite / Hybrid View</option>
                                            <option value="topo">Terrain / Topographic View</option>
                                        </select>
                                    </div>

                                    <!-- Reset Filters -->
                                    <button onclick="resetMapFilters()" class="px-3 py-2 text-xs font-bold text-gray-500 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors flex items-center gap-1.5 cursor-pointer">
                                        <i data-lucide="rotate-ccw" class="w-3.5 h-3.5"></i>
                                        <span>Reset</span>
                                    </button>
                                </div>

                                <!-- Count Badge -->
                                <div class="flex items-center gap-2">
                                    <span id="mapMinesCountBadge" class="bg-[#eefcce] text-[#111111] px-3.5 py-1.5 rounded-full text-xs font-black border border-[#d9f99d] shadow-2xs">
                                        77 Mines Geocoded
                                    </span>
                                </div>
                            </div>
                        </div>

                        <!-- Map & Details Grid -->
                        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                            <!-- Leaflet Map Container -->
                            <div class="lg:col-span-8 bg-white rounded-[2rem] p-3 border border-gray-200/80 shadow-xs relative overflow-hidden h-[580px]">
                                <!-- Floating Quick Layer Pill inside Map -->
                                <div class="floating-map-layer-bar flex items-center gap-1 bg-white/95 border border-gray-200/90 rounded-2xl p-1 shadow-lg">
                                    <button type="button" onclick="switchMapBaseLayer('gis')" id="layer-btn-gis" title="GIS Layer View" class="layer-btn px-2.5 py-1.5 rounded-xl text-[10px] font-black tracking-tight transition-all bg-[#111111] text-[#a3e635] shadow-xs">
                                        GIS
                                    </button>
                                    <button type="button" onclick="switchMapBaseLayer('geological')" id="layer-btn-geological" title="Geological Coalfield Map" class="layer-btn px-2.5 py-1.5 rounded-xl text-[10px] font-black tracking-tight transition-all text-gray-600 hover:text-black hover:bg-gray-100">
                                        Geological
                                    </button>
                                    <button type="button" onclick="switchMapBaseLayer('satellite')" id="layer-btn-satellite" title="Satellite / Hybrid View" class="layer-btn px-2.5 py-1.5 rounded-xl text-[10px] font-black tracking-tight transition-all text-gray-600 hover:text-black hover:bg-gray-100">
                                        Satellite
                                    </button>
                                    <button type="button" onclick="switchMapBaseLayer('topo')" id="layer-btn-topo" title="Terrain / Topographic View" class="layer-btn px-2.5 py-1.5 rounded-xl text-[10px] font-black tracking-tight transition-all text-gray-600 hover:text-black hover:bg-gray-100">
                                        Terrain
                                    </button>
                                </div>

                                <!-- Geological Layer Toggles Overlay -->
                                <div id="geologicalTogglesOverlay" class="geological-layer-toggles hidden flex-wrap items-center gap-1.5 bg-white/95 border border-gray-200/90 rounded-2xl p-1.5 shadow-xl">
                                    <label class="flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-[10px] font-black text-gray-700 hover:bg-gray-100 cursor-pointer transition-all">
                                        <input type="checkbox" id="toggleCoalfields" checked onchange="toggleGeologicalLayer('coalfields', this.checked)" class="accent-[#111111] rounded">
                                        <span>Coalfield Basins</span>
                                    </label>
                                    <label class="flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-[10px] font-black text-gray-700 hover:bg-gray-100 cursor-pointer transition-all">
                                        <input type="checkbox" id="toggleCoalBlocks" checked onchange="toggleGeologicalLayer('blocks', this.checked)" class="accent-[#111111] rounded">
                                        <span>Coal Blocks</span>
                                    </label>
                                    <label class="flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-[10px] font-black text-gray-700 hover:bg-gray-100 cursor-pointer transition-all">
                                        <input type="checkbox" id="toggleMines" checked onchange="toggleGeologicalLayer('mines', this.checked)" class="accent-[#111111] rounded">
                                        <span>Active Mines</span>
                                    </label>
                                    <label class="flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-[10px] font-black text-gray-700 hover:bg-gray-100 cursor-pointer transition-all">
                                        <input type="checkbox" id="toggleBoreholes" checked onchange="toggleGeologicalLayer('boreholes', this.checked)" class="accent-[#111111] rounded">
                                        <span>Boreholes</span>
                                    </label>
                                </div>

                                <!-- Geological Map Legend -->
                                <div id="geologicalLegendOverlay" class="geological-legend-box hidden bg-white/95 border border-gray-200/90 rounded-2xl p-2.5 shadow-xl text-[10px] font-extrabold text-gray-700 space-y-1">
                                    <div class="text-[9px] uppercase tracking-wider text-gray-400 font-black mb-1">Geological Legend</div>
                                    <div class="flex items-center gap-2"><span class="w-3 h-3 rounded bg-amber-500/60 border border-amber-600 inline-block"></span> <span>Gondwana Basin</span></div>
                                    <div class="flex items-center gap-2"><span class="w-3 h-3 rounded bg-emerald-500/50 border border-emerald-600 border-dashed inline-block"></span> <span>Operational Coal Block</span></div>
                                    <div class="flex items-center gap-2"><span class="w-2.5 h-2.5 rounded-full bg-[#f59e0b] border border-white inline-block"></span> <span>Coal Mine Pin</span></div>
                                    <div class="flex items-center gap-2"><span class="w-2.5 h-2.5 rotate-45 bg-[#0284c7] border border-white inline-block"></span> <span>Borehole Drill Log</span></div>
                                    <div class="text-[8px] text-gray-400 pt-1 border-t border-gray-100">GSI / CMPDI Geological Memoirs (WGS84)</div>
                                </div>

                                <div id="minesMapContainer" class="w-full h-full rounded-[1.5rem] z-0"></div>
                            </div>

                            <!-- Selected Mine / Coalfield Detail Card & Reports List -->
                            <div class="lg:col-span-4 bg-white rounded-[2rem] p-6 border border-gray-200/80 shadow-xs flex flex-col h-[580px] overflow-hidden">
                                <div id="mineDetailHeader" class="border-b border-gray-100 pb-4 mb-4">
                                    <div class="flex items-center justify-between mb-1.5">
                                        <span id="selectedMineSub" class="bg-[#111111] text-[#a3e635] text-[10px] font-black uppercase px-2.5 py-0.5 rounded-md">CMPDI</span>
                                        <span id="selectedMineType" class="text-xs font-extrabold text-orange-600 bg-orange-50 px-2.5 py-0.5 rounded-full border border-orange-200">Opencast</span>
                                    </div>
                                    <h3 id="selectedMineName" class="text-lg font-black text-[#111111] tracking-tight">Select a mine or coalfield</h3>
                                    <p id="selectedMineLoc" class="text-xs font-semibold text-gray-500">Hover over any pin or polygon to view geological data and linked reports</p>
                                </div>

                                <div class="flex-1 overflow-y-auto custom-scrollbar pr-1" id="mineReportsListContainer">
                                    <p class="text-xs font-bold text-gray-400 text-center py-12">Click on any coalfield basin or mine marker on the map to load associated geological exploration and production reports.</p>
                                </div>
                            </div>
                        </div>
                    </div>
'''
html = html.replace('<div id="page-reports"', f'{map_view_html}\n                    <div id="page-reports"')

# 4. Update pageMeta to include 'map'
page_meta_old = "'dashboard': { title: 'Dashboard <span class=\"text-xl\">ðŸ‘‹</span>', subtitle: 'Welcome to CMPDI GeoAI Hub!' },"
page_meta_new = """'dashboard': { title: 'Dashboard <span class=\"text-xl\">👋</span>', subtitle: 'Welcome to CMPDI GeoAI Hub!' },
            'map': { title: 'Geological Coalfield & Spatial Hub 🗺️', subtitle: 'Interactive 2D Geological Coalfield Map & Mine Intelligence of India' },"""
html = html.replace(page_meta_old, page_meta_new)

# 5. Add Leaflet Scripts, Geological Basins/Blocks/Borehole Layers, SVG Pin Generator & Hover Tooltips before </body>
map_scripts = '''
    <!-- Leaflet & MarkerCluster JS CDN -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
    <script>
        let minesMapInstance = null;
        let minesClusterGroup = null;
        let allMinesGeoJSON = [];
        let currentBaseLayers = [];
        let activeLayerKey = 'gis';

        // Geological Map Layers & Datasets
        let coalfieldsGeoLayer = null;
        let coalBlocksGeoLayer = null;
        let boreholesGeoLayer = null;
        let coalfieldsData = null;
        let coalBlocksData = null;
        let boreholesData = null;

        // 4 Multi-Layer GIS Basemap Configurations
        const BASE_LAYER_CONFIGS = {
            'gis': [
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    maxZoom: 19,
                    attribution: '© OpenStreetMap contributors'
                })
            ],
            'geological': [
                // Clean, light-neutral geological cartographic base with clear boundaries (no watermark)
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
                    maxZoom: 19,
                    attribution: '© Esri, HERE, Garmin, GSI / CMPDI Geological'
                }),
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
                    maxZoom: 19,
                    opacity: 0.9
                })
            ],
            'satellite': [
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                    maxZoom: 19,
                    attribution: '© Esri, Maxar, Earthstar Geographics'
                }),
                L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', {
                    maxZoom: 19,
                    opacity: 0.85
                })
            ],
            'topo': [
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
                    maxZoom: 19,
                    attribution: '© Esri, USGS, FAO, NPS'
                })
            ]
        };

        const BASIN_COLORS = {
            'CF-RANIGANJ-01': '#f59e0b',
            'CF-JHARIA-02': '#ef4444',
            'CF-BOKARO-03': '#f97316',
            'CF-KARANPURA-04': '#8b5cf6',
            'CF-SINGRAULI-05': '#06b6d4',
            'CF-KORBA-06': '#10b981',
            'CF-TALCHER-07': '#d97706',
            'CF-WARDHA-08': '#3b82f6',
            'CF-GODAVARI-09': '#6366f1'
        };

        async function loadGeologicalDatasets() {
            try {
                if (!coalfieldsData) {
                    const cfResp = await fetch(`${API_BASE}/api/geological/coalfields`);
                    coalfieldsData = await cfResp.json();
                }
                if (!coalBlocksData) {
                    const blkResp = await fetch(`${API_BASE}/api/geological/coalblocks`);
                    coalBlocksData = await blkResp.json();
                }
                if (!boreholesData) {
                    const bhResp = await fetch(`${API_BASE}/api/geological/boreholes`);
                    boreholesData = await bhResp.json();
                }
            } catch(err) {
                console.warn('Error loading geological datasets', err);
            }
        }

        function initGeologicalLayers() {
            if (!minesMapInstance) return;

            // 1. Coalfield Basins Layer
            if (coalfieldsData && !coalfieldsGeoLayer) {
                coalfieldsGeoLayer = L.geoJSON(coalfieldsData, {
                    style: function(feature) {
                        const color = BASIN_COLORS[feature.properties.coalfield_id] || '#f59e0b';
                        return {
                            fillColor: color,
                            weight: 2.5,
                            opacity: 0.9,
                            color: color,
                            fillOpacity: 0.22,
                            dashArray: ''
                        };
                    },
                    onEachFeature: function(feature, layer) {
                        const p = feature.properties;
                        layer.bindTooltip(`
                            <div class="mine-pin-label">
                                <span class="mine-pin-name">${p.name}</span>
                                <span class="mine-pin-tag">${p.subsidiary}</span>
                            </div>
                        `, {
                            permanent: false,
                            direction: 'top',
                            className: 'mine-tooltip-custom',
                            opacity: 1
                        });

                        layer.on({
                            mouseover: function(e) {
                                const l = e.target;
                                l.setStyle({
                                    weight: 3.5,
                                    fillOpacity: 0.45,
                                    color: '#111111'
                                });
                                if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                                    l.bringToFront();
                                }
                            },
                            mouseout: function(e) {
                                coalfieldsGeoLayer.resetStyle(e.target);
                            },
                            click: function(e) {
                                showCoalfieldDetails(p);
                                if (e.target.getBounds) {
                                    minesMapInstance.fitBounds(e.target.getBounds(), { padding: [40, 40], maxZoom: 9 });
                                }
                            }
                        });
                    }
                });
            }

            // 2. Coal Blocks Layer
            if (coalBlocksData && !coalBlocksGeoLayer) {
                coalBlocksGeoLayer = L.geoJSON(coalBlocksData, {
                    style: function(feature) {
                        return {
                            fillColor: '#10b981',
                            weight: 2,
                            opacity: 0.95,
                            color: '#059669',
                            fillOpacity: 0.35,
                            dashArray: '4, 4'
                        };
                    },
                    onEachFeature: function(feature, layer) {
                        const p = feature.properties;
                        layer.bindTooltip(`
                            <div class="mine-pin-label">
                                <span class="mine-pin-name">${p.name}</span>
                                <span class="mine-pin-tag" style="background:#86efac;color:#064e3b;">BLOCK</span>
                            </div>
                        `, {
                            permanent: false,
                            direction: 'top',
                            className: 'mine-tooltip-custom',
                            opacity: 1
                        });

                        layer.on('click', function() {
                            showCoalBlockDetails(p);
                        });
                    }
                });
            }

            // 3. Boreholes Layer
            if (boreholesData && !boreholesGeoLayer) {
                boreholesGeoLayer = L.geoJSON(boreholesData, {
                    pointToLayer: function(feature, latlng) {
                        const icon = L.divIcon({
                            className: '',
                            html: '<div class="borehole-marker-icon"></div>',
                            iconSize: [18, 18],
                            iconAnchor: [9, 9]
                        });
                        return L.marker(latlng, { icon: icon, keyboard: false });
                    },
                    onEachFeature: function(feature, layer) {
                        const p = feature.properties;
                        layer.bindTooltip(`
                            <div class="mine-pin-label">
                                <span class="mine-pin-name">${p.borehole_id}</span>
                                <span class="mine-pin-tag" style="background:#38bdf8;color:#082f49;">BOREHOLE</span>
                            </div>
                        `, {
                            permanent: false,
                            direction: 'top',
                            className: 'mine-tooltip-custom',
                            opacity: 1
                        });

                        layer.on('click', function() {
                            showBoreholeDetails(p);
                        });
                    }
                });
            }
        }

        function showCoalfieldDetails(p) {
            const subEl = document.getElementById('selectedMineSub');
            const typeEl = document.getElementById('selectedMineType');
            const nameEl = document.getElementById('selectedMineName');
            const locEl = document.getElementById('selectedMineLoc');
            const listEl = document.getElementById('mineReportsListContainer');

            if (subEl) subEl.textContent = p.subsidiary || 'CMPDI';
            if (typeEl) {
                typeEl.textContent = 'Coalfield Basin';
                typeEl.className = 'text-xs font-extrabold text-amber-800 bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200';
            }
            if (nameEl) nameEl.textContent = p.name;
            if (locEl) locEl.textContent = `${p.basin} • ${p.state} • Reserves: ${p.estimated_reserves_bt} BT`;

            if (listEl) {
                listEl.innerHTML = `
                    <div class="bg-gray-50 p-4 rounded-2xl border border-gray-200/80 mb-4 space-y-2">
                        <div class="flex justify-between text-xs">
                            <span class="font-extrabold text-gray-500">Geological Age:</span>
                            <span class="font-black text-[#111111]">${p.age}</span>
                        </div>
                        <div class="flex justify-between text-xs">
                            <span class="font-extrabold text-gray-500">Formations:</span>
                            <span class="font-bold text-[#111111] text-right max-w-[200px]">${p.formations}</span>
                        </div>
                        <div class="flex justify-between text-xs">
                            <span class="font-extrabold text-gray-500">Coal Rank / Quality:</span>
                            <span class="font-bold text-[#111111] text-right max-w-[200px]">${p.coal_rank}</span>
                        </div>
                        <div class="flex justify-between text-xs">
                            <span class="font-extrabold text-gray-500">Active Mine Units:</span>
                            <span class="font-black text-green-700 bg-green-100 px-2 py-0.5 rounded-full">${p.active_mines_count} Mines</span>
                        </div>
                    </div>

                    <h4 class="text-xs font-black text-gray-800 mb-2 uppercase tracking-wider">Linked Geological & Exploration Reports</h4>
                    <div class="space-y-2">
                        <div class="p-3.5 bg-gray-50 hover:bg-[#eefcce]/50 rounded-2xl border border-gray-200/70 transition-all cursor-pointer group" onclick="alertBox('Viewing: Geological Memoir & Resource Evaluation for ' + '${p.name}')">
                            <div class="flex items-center justify-between mb-1">
                                <span class="text-[10px] font-extrabold uppercase text-gray-400">GSI / CMPDI MEMOIR • 2024</span>
                                <span class="text-[10px] font-black text-green-700 bg-green-100 px-2 py-0.5 rounded-full">100% Match</span>
                            </div>
                            <h5 class="text-xs font-black text-gray-900 group-hover:text-black leading-snug">Geological Evaluation & Coal Seam Correlation: ${p.name}</h5>
                            <p class="text-[11px] font-semibold text-gray-500 mt-1">Total Estimated Reserves: ${p.estimated_reserves_bt} Billion Tonnes</p>
                        </div>
                    </div>
                `;
            }
        }

        function showCoalBlockDetails(p) {
            const subEl = document.getElementById('selectedMineSub');
            const typeEl = document.getElementById('selectedMineType');
            const nameEl = document.getElementById('selectedMineName');
            const locEl = document.getElementById('selectedMineLoc');
            const listEl = document.getElementById('mineReportsListContainer');

            if (subEl) subEl.textContent = p.subsidiary || 'SECL';
            if (typeEl) {
                typeEl.textContent = 'Coal Block';
                typeEl.className = 'text-xs font-extrabold text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200';
            }
            if (nameEl) nameEl.textContent = p.name;
            if (locEl) locEl.textContent = `${p.coalfield} • Capacity: ${p.capacity_mtpa} MTPA • ${p.status}`;

            if (listEl) {
                listEl.innerHTML = `
                    <div class="bg-gray-50 p-4 rounded-2xl border border-gray-200/80 mb-4 space-y-2">
                        <div class="flex justify-between text-xs">
                            <span class="font-extrabold text-gray-500">Block ID:</span>
                            <span class="font-black text-[#111111]">${p.block_id}</span>
                        </div>
                        <div class="flex justify-between text-xs">
                            <span class="font-extrabold text-gray-500">Surface Area:</span>
                            <span class="font-black text-[#111111]">${p.area_sqkm} sq.km</span>
                        </div>
                        <div class="flex justify-between text-xs">
                            <span class="font-extrabold text-gray-500">Seam Thickness:</span>
                            <span class="font-bold text-[#111111]">${p.seam_thickness_m}</span>
                        </div>
                    </div>
                `;
            }
        }

        function showBoreholeDetails(p) {
            const subEl = document.getElementById('selectedMineSub');
            const typeEl = document.getElementById('selectedMineType');
            const nameEl = document.getElementById('selectedMineName');
            const locEl = document.getElementById('selectedMineLoc');
            const listEl = document.getElementById('mineReportsListContainer');

            if (subEl) subEl.textContent = 'DRILL CORE';
            if (typeEl) {
                typeEl.textContent = 'Borehole Log';
                typeEl.className = 'text-xs font-extrabold text-sky-800 bg-sky-50 px-2.5 py-0.5 rounded-full border border-sky-200';
            }
            if (nameEl) nameEl.textContent = p.borehole_id;
            if (locEl) locEl.textContent = `${p.coalfield} • Depth: ${p.total_depth_m}m • Collar El: ${p.collar_elevation_m}m`;

            if (listEl) {
                listEl.innerHTML = `
                    <div class="bg-gray-50 p-4 rounded-2xl border border-gray-200/80 mb-4 space-y-2">
                        <div class="flex justify-between text-xs">
                            <span class="font-extrabold text-gray-500">Target Formation:</span>
                            <span class="font-black text-[#111111]">${p.formation}</span>
                        </div>
                        <div class="flex justify-between text-xs">
                            <span class="font-extrabold text-gray-500">Net Coal Intercept:</span>
                            <span class="font-black text-green-700">${p.coal_intercept_m} meters</span>
                        </div>
                        <div class="flex justify-between text-xs">
                            <span class="font-extrabold text-gray-500">Survey Agency:</span>
                            <span class="font-bold text-[#111111]">${p.agency}</span>
                        </div>
                        <div class="flex justify-between text-xs">
                            <span class="font-extrabold text-gray-500">Lithology Summary:</span>
                            <span class="font-bold text-gray-700 text-right max-w-[200px]">${p.lithology}</span>
                        </div>
                    </div>
                `;
            }
        }

        function toggleGeologicalLayer(layerName, isVisible) {
            if (!minesMapInstance) return;
            if (layerName === 'coalfields' && coalfieldsGeoLayer) {
                if (isVisible) minesMapInstance.addLayer(coalfieldsGeoLayer);
                else minesMapInstance.removeLayer(coalfieldsGeoLayer);
            } else if (layerName === 'blocks' && coalBlocksGeoLayer) {
                if (isVisible) minesMapInstance.addLayer(coalBlocksGeoLayer);
                else minesMapInstance.removeLayer(coalBlocksGeoLayer);
            } else if (layerName === 'mines' && minesClusterGroup) {
                if (isVisible) minesMapInstance.addLayer(minesClusterGroup);
                else minesMapInstance.removeLayer(minesClusterGroup);
            } else if (layerName === 'boreholes' && boreholesGeoLayer) {
                if (isVisible) minesMapInstance.addLayer(boreholesGeoLayer);
                else minesMapInstance.removeLayer(boreholesGeoLayer);
            }
        }

        function switchMapBaseLayer(layerKey) {
            activeLayerKey = layerKey;
            if (!minesMapInstance) return;

            // Remove existing active base layers
            currentBaseLayers.forEach(layer => {
                if (minesMapInstance.hasLayer(layer)) {
                    minesMapInstance.removeLayer(layer);
                }
            });
            currentBaseLayers = [];

            const newLayers = BASE_LAYER_CONFIGS[layerKey] || BASE_LAYER_CONFIGS['gis'];
            newLayers.forEach(layer => {
                layer.addTo(minesMapInstance);
                if (layer.bringToBack) {
                    layer.bringToBack();
                }
                currentBaseLayers.push(layer);
            });

            // Handle Geological Overlay UI
            const toggleOverlay = document.getElementById('geologicalTogglesOverlay');
            const legendOverlay = document.getElementById('geologicalLegendOverlay');

            if (layerKey === 'geological') {
                if (toggleOverlay) toggleOverlay.classList.remove('hidden');
                if (legendOverlay) legendOverlay.classList.remove('hidden');

                // Add geological layers
                initGeologicalLayers();
                if (coalfieldsGeoLayer) minesMapInstance.addLayer(coalfieldsGeoLayer);
                if (coalBlocksGeoLayer) minesMapInstance.addLayer(coalBlocksGeoLayer);
                if (boreholesGeoLayer) minesMapInstance.addLayer(boreholesGeoLayer);
                if (coalfieldsGeoLayer) coalfieldsGeoLayer.bringToBack();
            } else {
                if (toggleOverlay) toggleOverlay.classList.add('hidden');
                if (legendOverlay) legendOverlay.classList.add('hidden');

                // Remove geological layers from non-geological views
                if (coalfieldsGeoLayer && minesMapInstance.hasLayer(coalfieldsGeoLayer)) minesMapInstance.removeLayer(coalfieldsGeoLayer);
                if (coalBlocksGeoLayer && minesMapInstance.hasLayer(coalBlocksGeoLayer)) minesMapInstance.removeLayer(coalBlocksGeoLayer);
                if (boreholesGeoLayer && minesMapInstance.hasLayer(boreholesGeoLayer)) minesMapInstance.removeLayer(boreholesGeoLayer);
            }

            // Sync Dropdown Select
            const selectEl = document.getElementById('mapLayerSwitcher');
            if (selectEl && selectEl.value !== layerKey) {
                selectEl.value = layerKey;
            }

            // Sync Floating Button Styles
            ['gis', 'geological', 'satellite', 'topo'].forEach(key => {
                const btn = document.getElementById(`layer-btn-${key}`);
                if (btn) {
                    if (key === layerKey) {
                        btn.className = 'layer-btn px-2.5 py-1.5 rounded-xl text-[10px] font-black tracking-tight transition-all bg-[#111111] text-[#a3e635] shadow-xs';
                    } else {
                        btn.className = 'layer-btn px-2.5 py-1.5 rounded-xl text-[10px] font-black tracking-tight transition-all text-gray-600 hover:text-black hover:bg-gray-100';
                    }
                }
            });
        }

        function getMineSvgPinIcon(type) {
            const colors = {
                'Opencast': '#f59e0b',
                'Underground': '#3b82f6',
                'Mixed': '#8b5cf6'
            };
            const color = colors[type] || '#f59e0b';
            return L.divIcon({
                className: 'mine-pin-container',
                html: `
                    <div class="mine-pin-wrapper">
                        <svg class="mine-pin-svg" viewBox="0 0 26 36" width="26" height="36" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M13 0C5.82 0 0 5.82 0 13C0 22.75 11.5 34.6 12.35 35.45C12.72 35.82 13.28 35.82 13.65 35.45C14.5 34.6 26 22.75 26 13C26 5.82 20.18 0 13 0Z" fill="${color}" stroke="#ffffff" stroke-width="1.5" />
                            <circle cx="13" cy="13" r="5" fill="#ffffff"/>
                            <circle cx="13" cy="13" r="2.5" fill="${color}"/>
                        </svg>
                        <div class="mine-pin-pulse"></div>
                    </div>
                `,
                iconSize: [26, 36],
                iconAnchor: [13, 36],
                popupAnchor: [0, -36],
                tooltipAnchor: [0, -36]
            });
        }

        async function initMinesMap() {
            const mapEl = document.getElementById('minesMapContainer');
            if (!mapEl) return;

            if (!minesMapInstance) {
                minesMapInstance = L.map('minesMapContainer', {
                    center: [23.5, 82.5],
                    zoom: 5,
                    zoomControl: false,
                    attributionControl: false,
                    keyboard: false,
                    scrollWheelZoom: true,
                    tap: false,
                    boxZoom: false
                });

                // Completely disable focus auto-scrolling on click/drag
                mapEl.removeAttribute('tabindex');
                mapEl.setAttribute('tabindex', '-1');

                const mainScrollArea = document.querySelector('.custom-scrollbar');
                if (mainScrollArea) {
                    mapEl.addEventListener('mousedown', function() {
                        const top = mainScrollArea.scrollTop;
                        requestAnimationFrame(() => {
                            if (mainScrollArea.scrollTop !== top) {
                                mainScrollArea.scrollTop = top;
                            }
                        });
                    }, true);

                    mapEl.addEventListener('touchstart', function() {
                        const top = mainScrollArea.scrollTop;
                        requestAnimationFrame(() => {
                            if (mainScrollArea.scrollTop !== top) {
                                mainScrollArea.scrollTop = top;
                            }
                        });
                    }, { passive: true });
                }

                L.control.zoom({ position: 'topleft' }).addTo(minesMapInstance);

                // Add Default Layer
                switchMapBaseLayer(activeLayerKey);

                minesClusterGroup = L.markerClusterGroup({
                    showCoverageOnHover: false,
                    maxClusterRadius: 40,
                    iconCreateFunction: function(cluster) {
                        return L.divIcon({
                            html: `<div class="custom-cluster-icon w-9 h-9">${cluster.getChildCount()}</div>`,
                            className: '',
                            iconSize: [36, 36]
                        });
                    }
                });
                minesMapInstance.addLayer(minesClusterGroup);

                await loadMinesFilters();
                await loadGeologicalDatasets();
                await fetchAndPlotMines();
            } else {
                setTimeout(() => {
                    minesMapInstance.invalidateSize();
                }, 200);
            }
        }

        async function loadMinesFilters() {
            try {
                const resp = await fetch(`${API_BASE}/api/mines/stats`);
                const data = await resp.json();
                if (data && data.status === 'ok') {
                    const subSelect = document.getElementById('mapSubsidiaryFilter');
                    if (subSelect && data.subsidiaries) {
                        subSelect.innerHTML = '<option value="">All Subsidiaries</option>' +
                            data.subsidiaries.map(s => `<option value="${s}">${s}</option>`).join('');
                    }
                    const stateSelect = document.getElementById('mapStateFilter');
                    if (stateSelect && data.states) {
                        stateSelect.innerHTML = '<option value="">All States</option>' +
                            data.states.map(st => `<option value="${st}">${st}</option>`).join('');
                    }
                }
            } catch(err) {
                console.warn('Could not load mine filter stats', err);
            }
        }

        let mapDebounceTimer = null;
        function applyMapFiltersDebounced() {
            clearTimeout(mapDebounceTimer);
            mapDebounceTimer = setTimeout(applyMapFilters, 300);
        }

        async function applyMapFilters() {
            const sub = document.getElementById('mapSubsidiaryFilter')?.value || '';
            const state = document.getElementById('mapStateFilter')?.value || '';
            const type = document.getElementById('mapTypeFilter')?.value || '';
            const search = document.getElementById('mapSearchInput')?.value || '';

            const params = new URLSearchParams();
            if (sub) params.append('subsidiary', sub);
            if (state) params.append('state', state);
            if (type) params.append('type', type);
            if (search) params.append('search', search);

            await fetchAndPlotMines(params.toString());
        }

        function resetMapFilters() {
            if (document.getElementById('mapSubsidiaryFilter')) document.getElementById('mapSubsidiaryFilter').value = '';
            if (document.getElementById('mapStateFilter')) document.getElementById('mapStateFilter').value = '';
            if (document.getElementById('mapTypeFilter')) document.getElementById('mapTypeFilter').value = '';
            if (document.getElementById('mapSearchInput')) document.getElementById('mapSearchInput').value = '';
            fetchAndPlotMines();
        }

        async function fetchAndPlotMines(queryString = '') {
            try {
                const url = `${API_BASE}/api/mines${queryString ? '?' + queryString : ''}`;
                const resp = await fetch(url);
                const data = await resp.json();

                if (!data || !data.features) return;
                allMinesGeoJSON = data.features;

                const countBadge = document.getElementById('mapMinesCountBadge');
                if (countBadge) countBadge.textContent = `${data.count || allMinesGeoJSON.length} Mines Visible`;

                if (!minesClusterGroup) return;
                minesClusterGroup.clearLayers();

                const bounds = [];

                allMinesGeoJSON.forEach(feature => {
                    const coords = feature.geometry.coordinates; // [lng, lat]
                    const props = feature.properties;
                    const latLng = [coords[1], coords[0]];
                    bounds.push(latLng);

                    // Create Teardrop SVG Pin Icon
                    const pinIcon = getMineSvgPinIcon(props.type);
                    const marker = L.marker(latLng, { icon: pinIcon, keyboard: false });

                    // Hover Tooltip (Dark Pill Badge with Mine Name + Green Tag)
                    marker.bindTooltip(`
                        <div class="mine-pin-label">
                            <span class="mine-pin-name">${props.name}</span>
                            <span class="mine-pin-tag">${props.subsidiary || 'CIL'}</span>
                        </div>
                    `, {
                        permanent: false,
                        direction: 'top',
                        offset: [0, -34],
                        className: 'mine-tooltip-custom',
                        opacity: 1
                    });

                    // Click Popup & Selection (autoPan: false to prevent moving window or map)
                    marker.bindPopup(`
                        <div class="p-2 text-left font-sans">
                            <span class="text-[9px] font-black uppercase tracking-wider px-2 py-0.5 rounded bg-gray-100 text-gray-700">${props.subsidiary}</span>
                            <h4 class="text-sm font-black text-gray-900 mt-1 mb-0.5">${props.name}</h4>
                            <p class="text-xs text-gray-500 font-semibold">${props.district ? props.district + ', ' : ''}${props.state}</p>
                            <p class="text-[11px] font-bold text-orange-600 mt-0.5">Type: ${props.type}</p>
                            <button onclick="showMineDetails('${props.mine_id}')" class="mt-2.5 w-full py-1.5 bg-[#111111] text-[#a3e635] text-[11px] font-black rounded-lg hover:bg-black transition-all cursor-pointer">
                                View Linked Reports →
                            </button>
                        </div>
                    `, { className: 'mine-popup', closeButton: false, autoPan: false });

                    marker.on('click', () => {
                        showMineDetails(props.mine_id, props);
                    });

                    minesClusterGroup.addLayer(marker);
                });

                if (bounds.length > 0 && minesMapInstance) {
                    minesMapInstance.fitBounds(bounds, { padding: [30, 30], maxZoom: 10 });
                }
            } catch(err) {
                console.error('Error fetching mines GeoJSON', err);
            }
        }

        async function showMineDetails(mineId, initialProps = null) {
            try {
                const resp = await fetch(`${API_BASE}/api/mines/${mineId}/reports`);
                const data = await resp.json();

                const subEl = document.getElementById('selectedMineSub');
                const typeEl = document.getElementById('selectedMineType');
                const nameEl = document.getElementById('selectedMineName');
                const locEl = document.getElementById('selectedMineLoc');
                const listEl = document.getElementById('mineReportsListContainer');

                if (subEl) subEl.textContent = data.subsidiary || initialProps?.subsidiary || 'CIL';
                if (typeEl) {
                    typeEl.textContent = initialProps?.type || 'Opencast';
                    typeEl.className = 'text-xs font-extrabold text-orange-600 bg-orange-50 px-2.5 py-0.5 rounded-full border border-orange-200';
                }
                if (nameEl) nameEl.textContent = data.mine_name || initialProps?.name || 'Coal Mine';
                if (locEl) locEl.textContent = `ID: ${mineId} • ${data.reports?.length || 0} Reports Linked`;

                if (listEl) {
                    if (!data.reports || data.reports.length === 0) {
                        listEl.innerHTML = '<p class="text-xs font-bold text-gray-400 text-center py-8">No institutional reports linked to this mine.</p>';
                    } else {
                        listEl.innerHTML = data.reports.map(r => `
                            <div class="p-3.5 mb-2.5 bg-gray-50 hover:bg-[#eefcce]/50 rounded-2xl border border-gray-200/70 transition-all cursor-pointer group" onclick="openReportDocModal('${r.report_id}')">
                                <div class="flex items-center justify-between mb-1">
                                    <span class="text-[10px] font-extrabold uppercase text-gray-400">${r.format} • ${r.year}</span>
                                    <span class="text-[10px] font-black text-green-700 bg-green-100 px-2 py-0.5 rounded-full">${Math.round((r.confidence_score||0.95)*100)}% Match</span>
                                </div>
                                <h5 class="text-xs font-black text-gray-900 group-hover:text-black leading-snug">${r.title}</h5>
                                <p class="text-[11px] font-semibold text-gray-500 mt-1">${r.production_ytd ? 'Prod: ' + r.production_ytd : 'Status: Verified'}</p>
                            </div>
                        `).join('');
                    }
                }
            } catch(err) {
                console.error('Error fetching mine details', err);
            }
        }

        async function openReportDocModal(reportId) {
            try {
                const resp = await fetch(`${API_BASE}/api/reports/${reportId}`);
                const data = await resp.json();
                if (data && data.content) {
                    alertBox(`Viewing: ${data.title}`);
                    const modal = document.createElement('div');
                    modal.className = 'fixed inset-0 z-[200] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4';
                    modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
                    modal.innerHTML = `
                        <div class="bg-white w-full max-w-2xl max-h-[80vh] rounded-[2rem] p-6 shadow-2xl flex flex-col overflow-hidden border border-gray-100">
                            <div class="flex items-center justify-between border-b border-gray-100 pb-3 mb-3">
                                <div>
                                    <span class="text-[10px] font-black uppercase tracking-wider text-[#84cc16] bg-[#eefcce] px-2.5 py-0.5 rounded-md">${data.subsidiary} • ${data.year}</span>
                                    <h4 class="text-sm font-black text-gray-900 mt-1">${data.title}</h4>
                                </div>
                                <button onclick="this.closest('.fixed').remove()" class="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-600 font-bold">✕</button>
                            </div>
                            <div class="flex-1 overflow-y-auto custom-scrollbar text-xs font-medium text-gray-700 leading-relaxed whitespace-pre-line p-4 bg-gray-50 rounded-xl border border-gray-200/60 font-mono">
                                ${data.content}
                            </div>
                        </div>
                    `;
                    document.body.appendChild(modal);
                }
            } catch(err) {
                alertBox('Could not load report content');
            }
        }

        // Window resize handler
        window.addEventListener('resize', () => {
            if (minesMapInstance) {
                minesMapInstance.invalidateSize();
            }
        });
    </script>
'''

body_end = html.rfind('</body>')
if body_end != -1:
    html = html[:body_end] + f'{map_scripts}\n' + html[body_end:]


# In handleRouting, add map initialization
old_router_trigger = "if (pageId === 'reports') {"
new_router_trigger = """if (pageId === 'map') {
                setTimeout(initMinesMap, 100);
            }
            if (pageId === 'reports') {"""
html = html.replace(old_router_trigger, new_router_trigger)

# Replace hardcoded API_BASE with dynamic origin
html = html.replace("const API_BASE = 'https://cmpdi-geoai-hub.onrender.com';", "const API_BASE = (window.location.protocol === 'file:' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') ? '' : 'https://cmpdi-geoai-hub.onrender.com';")

with open('c:/Users/LENOVO/Downloads/final_cmpdi/cmpdi-geoai-hub-main/frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Successfully replaced 3D DTM with Interactive 2D Geological Coalfield Map in index.html!")
