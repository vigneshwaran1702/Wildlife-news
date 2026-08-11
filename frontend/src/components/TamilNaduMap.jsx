import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap } from 'react-leaflet';
import L from 'leaflet';
import { MapPin, Compass, ShieldAlert, Trees, Layers, Filter, Eye, RefreshCw } from 'lucide-react';

// Fix Leaflet Default Icon Asset Path Issue in Vite/React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Comprehensive Real Coordinates & Information for All Major TN Wildlife Divisions & Districts
const TN_FULL_MAP_REGIONS = [
  {
    id: 'nilgiris',
    name: 'Nilgiris',
    reserves: 'Mudumalai Tiger Reserve (MTR) & Ooty Range',
    lat: 11.5833,
    lng: 76.5667,
    risk: 'High',
    species: ['Asian Elephant', 'Bengal Tiger', 'Leopard', 'Gaur'],
    incidents: 14,
    description: 'Nilgiri Biosphere Core corridor connecting Bandipur, Wayanad & Mudumalai.'
  },
  {
    id: 'coimbatore',
    name: 'Coimbatore',
    reserves: 'Mettupalayam, Boluvampatti & Siruvani Forest Ranges',
    lat: 11.0168,
    lng: 76.9558,
    risk: 'High',
    species: ['Asian Elephant', 'Leopard', 'Wild Boar', 'King Cobra'],
    incidents: 18,
    description: 'Major railway corridor & human-elephant conflict hotline along Western Ghats.'
  },
  {
    id: 'erode',
    name: 'Erode & Sathyamangalam',
    reserves: 'Sathyamangalam Tiger Reserve (STR)',
    lat: 11.5000,
    lng: 77.2333,
    risk: 'High',
    species: ['Bengal Tiger', 'Elephant', 'Striped Hyena', 'Blackbuck'],
    incidents: 11,
    description: 'Largest wildlife sanctuary in TN bridging Eastern & Western Ghats.'
  },
  {
    id: 'tiruppur',
    name: 'Tiruppur & Anamalai',
    reserves: 'Anamalai Buffer & Amaravathi Dam Range',
    lat: 11.1085,
    lng: 77.3411,
    risk: 'Medium',
    species: ['Elephant', 'Gaur', 'Marsh Crocodile'],
    incidents: 6,
    description: 'Udumalpet & Amaravathi reservoir forest divisions.'
  },
  {
    id: 'theni',
    name: 'Theni & Megamalai',
    reserves: 'Srivilliputhur Megamalai Tiger Reserve (SMTR)',
    lat: 10.0104,
    lng: 77.4768,
    risk: 'High',
    species: ['Bengal Tiger', 'Elephant', 'Nilgiri Tahr', 'Lion-tailed Macaque'],
    incidents: 9,
    description: 'High elevation cardamom hill reserve & tiger breeding habitat.'
  },
  {
    id: 'dindigul',
    name: 'Dindigul & Kodaikanal',
    reserves: 'Kodaikanal Wildlife Sanctuary & Palani Hills',
    lat: 10.3673,
    lng: 77.9803,
    risk: 'Medium',
    species: ['Gaur (Indian Bison)', 'Barking Deer', 'Sloth Bear'],
    incidents: 7,
    description: 'Shola-grassland ecosystem with frequent Gaur sightings in hill stations.'
  },
  {
    id: 'tirunelveli',
    name: 'Tirunelveli & KMTR',
    reserves: 'Kalakkad Mundanthurai Tiger Reserve (KMTR)',
    lat: 8.7139,
    lng: 77.7567,
    risk: 'High',
    species: ['Bengal Tiger', 'Lion-tailed Macaque', 'Leopard', 'Sambar Deer'],
    incidents: 8,
    description: 'First Tiger Reserve in TN & Agasthyamalai Biosphere water catchments.'
  },
  {
    id: 'kanyakumari',
    name: 'Kanyakumari',
    reserves: 'Kanyakumari Wildlife Sanctuary',
    lat: 8.0883,
    lng: 77.5385,
    risk: 'Low',
    species: ['Sambar Deer', 'Leopard', 'Russell Viper'],
    incidents: 3,
    description: 'Southernmost tip reserve connecting Agasthyamalai Biosphere.'
  },
  {
    id: 'dharmapuri',
    name: 'Dharmapuri & Krishnagiri',
    reserves: 'Cauvery North Wildlife Sanctuary & Pennagaram',
    lat: 12.1211,
    lng: 78.1582,
    risk: 'High',
    species: ['Asian Elephant', 'Sloth Bear', 'Spotted Deer'],
    incidents: 12,
    description: 'Inter-state elephant migratory path between Karnataka & Tamil Nadu.'
  },
  {
    id: 'krishnagiri',
    name: 'Krishnagiri & Hosur',
    reserves: 'Hosur Forest Division & Cauvery Wildlife Corridor',
    lat: 12.5186,
    lng: 78.2137,
    risk: 'High',
    species: ['Asian Elephant', 'Leopard', 'Jackal'],
    incidents: 10,
    description: 'Bannerghatta-Hosur migratory elephant corridor.'
  },
  {
    id: 'salem',
    name: 'Salem & Yercaud',
    reserves: 'Servarayan & Shevaroys Hill Range',
    lat: 11.6643,
    lng: 78.1460,
    risk: 'Medium',
    species: ['Sloth Bear', 'Leopard', 'Indian Pangolin'],
    incidents: 5,
    description: 'Eastern Ghats isolated hill range with sloth bear human encounters.'
  },
  {
    id: 'chennai',
    name: 'Chennai & Vandalur',
    reserves: 'Guindy National Park & Arignar Anna Zoo',
    lat: 13.0827,
    lng: 80.2707,
    risk: 'Low',
    species: ['Blackbuck', 'Golden Jackal', 'Star Tortoise'],
    incidents: 2,
    description: 'Urban forest national park & captive wildlife rescue headquarters.'
  },
  {
    id: 'chengalpattu',
    name: 'Chengalpattu & Vedanthangal',
    reserves: 'Vedanthangal & Karikili Bird Sanctuaries',
    lat: 12.5447,
    lng: 79.8608,
    risk: 'Low',
    species: ['Migratory Waterbirds', 'Spot-billed Pelican', 'Openbill Stork'],
    incidents: 1,
    description: 'Oldest water bird sanctuary in India with international migratory species.'
  },
  {
    id: 'ramnad',
    name: 'Ramanathapuram & Gulf of Mannar',
    reserves: 'Gulf of Mannar Marine National Park',
    lat: 9.3639,
    lng: 78.8317,
    risk: 'Medium',
    species: ['Dugong (Sea Cow)', 'Green Sea Turtle', 'Corals'],
    incidents: 4,
    description: 'First Marine National Park in South Asia & Dugong conservation reserve.'
  },
  {
    id: 'nagapattinam',
    name: 'Nagapattinam & Point Calimere',
    reserves: 'Point Calimere Wildlife & Bird Sanctuary',
    lat: 10.7656,
    lng: 79.8424,
    risk: 'Low',
    species: ['Blackbuck', 'Greater Flamingo', 'Feral Horse'],
    incidents: 2,
    description: 'Coastal wetland sanctuary famed for flamingo wintering grounds.'
  },
  {
    id: 'tenkasi',
    name: 'Tenkasi & Virudhunagar',
    reserves: 'Srivilliputhur Grizzled Giant Squirrel Sanctuary',
    lat: 8.9593,
    lng: 77.3134,
    risk: 'Medium',
    species: ['Grizzled Giant Squirrel', 'Asian Elephant', 'Leopard'],
    incidents: 5,
    description: 'Protected canopy habitat for endangered Grizzled Giant Squirrel.'
  },
  {
    id: 'trichy',
    name: 'Tiruchirappalli & Pachaimalai',
    reserves: 'Pachaimalai Hills Reserve Forest',
    lat: 10.7905,
    lng: 78.7047,
    risk: 'Low',
    species: ['Spotted Deer', 'Wild Boar', 'Peafowl'],
    incidents: 3,
    description: 'Central Tamil Nadu tribal forest hill range.'
  },
  {
    id: 'villupuram',
    name: 'Villupuram & Kalvarayan',
    reserves: 'Kalvarayan Hills Reserve Forest',
    lat: 11.9401,
    lng: 79.4861,
    risk: 'Low',
    species: ['Sloth Bear', 'Spotted Deer', 'Python'],
    incidents: 2,
    description: 'Eastern Ghats dry deciduous forest division.'
  },
  {
    id: 'vellore',
    name: 'Vellore & Jawadhu Hills',
    reserves: 'Jawadhu Hills & Kavalur Range',
    lat: 12.9165,
    lng: 79.1325,
    risk: 'Medium',
    species: ['Sloth Bear', 'Spotted Deer', 'Pangolin'],
    incidents: 4,
    description: 'Dense sandalwood & sloth bear habitats in Jawadhu Hills.'
  },
  {
    id: 'thanjavur',
    name: 'Thanjavur & Tiruvarur',
    reserves: 'Udayamarthandapuram Bird Sanctuary',
    lat: 10.7870,
    lng: 79.1378,
    risk: 'Low',
    species: ['Waterbirds', 'Smooth-coated Otter'],
    incidents: 1,
    description: 'Delta bird sanctuaries & river otter habitats.'
  }
];

// Custom HTML Markers helper
const createCustomMarker = (risk, name, hasTiger) => {
  const bg = risk === 'High' ? '#ef4444' : risk === 'Medium' ? '#f59e0b' : '#10b981';
  const pulse = risk === 'High' ? `<div style="position:absolute; width:28px; height:28px; border-radius:50%; background:${bg}; opacity:0.35; animation: pulse 1.8s infinite; top:-4px; left:-4px;"></div>` : '';
  const iconHtml = `
    <div style="position:relative; cursor:pointer;">
      ${pulse}
      <div style="width:20px; height:20px; border-radius:50%; background:${bg}; border:2px solid #ffffff; box-shadow: 0 0 10px ${bg}; display:flex; align-items:center; justify-content:center; color:#ffffff; font-weight:bold; font-size:10px;">
        ${hasTiger ? '🐅' : '📍'}
      </div>
    </div>
  `;
  return L.divIcon({
    html: iconHtml,
    className: 'custom-leaflet-pin',
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  });
};

// Map Recenter Helper Component
function ChangeMapView({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom);
  }, [center, zoom, map]);
  return null;
}

export default function TamilNaduMap({ onSelectDistrict, selectedDistrict }) {
  const [activeRegion, setActiveRegion] = useState(TN_FULL_MAP_REGIONS[0]);
  const [tileLayerType, setTileLayerType] = useState('dark'); // 'dark' | 'osm' | 'satellite'
  const [filterRisk, setFilterRisk] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [mapCenter, setMapCenter] = useState([11.1271, 78.6569]);
  const [mapZoom, setMapZoom] = useState(7.2);

  const TILE_LAYERS = {
    dark: {
      url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    },
    osm: {
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    },
    satellite: {
      url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    }
  };

  const filteredRegions = TN_FULL_MAP_REGIONS.filter(reg => {
    const matchesRisk = filterRisk === 'All' || reg.risk === filterRisk;
    const matchesSearch = !searchQuery || 
      reg.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
      reg.reserves.toLowerCase().includes(searchQuery.toLowerCase()) ||
      reg.species.some(s => s.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesRisk && matchesSearch;
  });

  const handleRegionClick = (region) => {
    setActiveRegion(region);
    setMapCenter([region.lat, region.lng]);
    setMapZoom(9);
    if (onSelectDistrict) {
      onSelectDistrict(region.name);
    }
  };

  const getRiskColor = (risk) => {
    if (risk === 'High') return '#ef4444';
    if (risk === 'Medium') return '#f59e0b';
    return '#10b981';
  };

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', padding: '1.25rem' }}>
      {/* Header Controls Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Compass color="var(--primary-emerald)" size={22} />
            Full Tamil Nadu Interactive GIS & Wildlife Map
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
            Real-time Leaflet GIS map of Tamil Nadu forest divisions, tiger reserves, sanctuaries & conflict hotspots.
          </p>
        </div>

        {/* Tile Layer Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(0,0,0,0.4)', padding: '3px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          <button
            type="button"
            onClick={() => setTileLayerType('dark')}
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '6px',
              border: 'none',
              background: tileLayerType === 'dark' ? 'var(--primary-emerald)' : 'transparent',
              color: tileLayerType === 'dark' ? '#ffffff' : 'var(--text-muted)',
              fontSize: '0.8rem',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Dark GIS
          </button>
          <button
            type="button"
            onClick={() => setTileLayerType('satellite')}
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '6px',
              border: 'none',
              background: tileLayerType === 'satellite' ? 'var(--primary-emerald)' : 'transparent',
              color: tileLayerType === 'satellite' ? '#ffffff' : 'var(--text-muted)',
              fontSize: '0.8rem',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Satellite
          </button>
          <button
            type="button"
            onClick={() => setTileLayerType('osm')}
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '6px',
              border: 'none',
              background: tileLayerType === 'osm' ? 'var(--primary-emerald)' : 'transparent',
              color: tileLayerType === 'osm' ? '#ffffff' : 'var(--text-muted)',
              fontSize: '0.8rem',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Standard Map
          </button>
        </div>
      </div>

      {/* Filter & Search Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '200px' }}>
          <input
            type="text"
            placeholder="Search district, tiger reserve, or species (e.g. Mudumalai, Elephant)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '0.45rem 0.8rem',
              background: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              color: 'var(--text-main)',
              fontSize: '0.85rem'
            }}
          />
        </div>

        {/* Risk Pill Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          {['All', 'High', 'Medium', 'Low'].map(r => (
            <button
              key={r}
              type="button"
              onClick={() => setFilterRisk(r)}
              style={{
                padding: '0.35rem 0.65rem',
                borderRadius: '6px',
                border: '1px solid var(--border-color)',
                background: filterRisk === r ? (r === 'High' ? '#ef4444' : r === 'Medium' ? '#f59e0b' : r === 'Low' ? '#10b981' : 'var(--primary-emerald)') : 'rgba(0,0,0,0.4)',
                color: filterRisk === r ? '#ffffff' : 'var(--text-muted)',
                fontSize: '0.75rem',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              {r === 'All' ? 'All Risk Levels' : `${r} Risk`}
            </button>
          ))}
        </div>

        {/* Reset Map Button */}
        <button
          type="button"
          onClick={() => { setMapCenter([11.1271, 78.6569]); setMapZoom(7.2); setSearchQuery(''); setFilterRisk('All'); }}
          className="btn btn-secondary"
          style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }}
        >
          <RefreshCw size={14} /> Reset View
        </button>
      </div>

      {/* Main Map & Information Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
        
        {/* Full Leaflet Map View */}
        <div style={{
          height: '520px',
          borderRadius: '12px',
          overflow: 'hidden',
          border: '1px solid var(--border-color)',
          boxShadow: '0 0 20px rgba(0,0,0,0.4)',
          position: 'relative'
        }}>
          <MapContainer
            center={mapCenter}
            zoom={mapZoom}
            scrollWheelZoom={true}
            style={{ width: '100%', height: '100%' }}
          >
            <ChangeMapView center={mapCenter} zoom={mapZoom} />
            
            <TileLayer
              url={TILE_LAYERS[tileLayerType].url}
              attribution={TILE_LAYERS[tileLayerType].attribution}
            />

            {filteredRegions.map((region) => {
              const hasTiger = region.reserves.includes('Tiger Reserve');
              const customIcon = createCustomMarker(region.risk, region.name, hasTiger);

              return (
                <React.Fragment key={region.id}>
                  {/* Outer circle halo for high risk */}
                  {region.risk === 'High' && (
                    <CircleMarker
                      center={[region.lat, region.lng]}
                      radius={16}
                      pathOptions={{
                        color: '#ef4444',
                        fillColor: '#ef4444',
                        fillOpacity: 0.2,
                        weight: 1
                      }}
                    />
                  )}

                  <Marker
                    position={[region.lat, region.lng]}
                    icon={customIcon}
                    eventHandlers={{
                      click: () => handleRegionClick(region)
                    }}
                  >
                    <Popup>
                      <div style={{ padding: '4px', maxWidth: '220px', color: '#0f172a' }}>
                        <div style={{ fontSize: '12px', fontWeight: 'bold', color: '#059669', marginBottom: '2px' }}>
                          📍 {region.name}
                        </div>
                        <div style={{ fontSize: '11px', fontWeight: '600', color: '#334155', marginBottom: '4px' }}>
                          🌲 {region.reserves}
                        </div>
                        <div style={{ fontSize: '10px', color: '#475569', marginBottom: '6px' }}>
                          {region.description}
                        </div>
                        <div style={{ fontSize: '10px', fontWeight: 'bold', color: getRiskColor(region.risk), marginBottom: '6px' }}>
                          ● {region.risk} Risk ({region.incidents} Reports Today)
                        </div>
                        <button
                          onClick={() => onSelectDistrict && onSelectDistrict(region.name)}
                          style={{
                            width: '100%',
                            padding: '4px 8px',
                            background: '#059669',
                            color: '#ffffff',
                            border: 'none',
                            borderRadius: '4px',
                            fontSize: '10px',
                            fontWeight: 'bold',
                            cursor: 'pointer'
                          }}
                        >
                          Filter News Feed
                        </button>
                      </div>
                    </Popup>
                  </Marker>
                </React.Fragment>
              );
            })}
          </MapContainer>

          {/* Floating Map Info Overlay */}
          <div style={{
            position: 'absolute',
            bottom: '10px',
            left: '10px',
            zIndex: 1000,
            background: 'rgba(10, 22, 16, 0.85)',
            backdropFilter: 'blur(8px)',
            padding: '0.4rem 0.75rem',
            borderRadius: '6px',
            border: '1px solid var(--border-color)',
            fontSize: '0.75rem',
            color: 'var(--text-muted)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem'
          }}>
            <span>Showing {filteredRegions.length} Wildlife Divisions</span>
            <span>🐅 Tiger Reserve</span>
          </div>
        </div>

        {/* Selected Division Sidebar Panel */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="glass-card" style={{
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(10, 22, 16, 0.95) 100%)',
            borderLeft: `4px solid ${getRiskColor(activeRegion.risk)}`,
            padding: '1.25rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Division GIS Metadata
              </span>
              <span style={{
                fontSize: '0.7rem',
                fontWeight: '700',
                padding: '2px 8px',
                borderRadius: '4px',
                background: `${getRiskColor(activeRegion.risk)}22`,
                color: getRiskColor(activeRegion.risk),
                border: `1px solid ${getRiskColor(activeRegion.risk)}44`
              }}>
                {activeRegion.risk} Risk Division
              </span>
            </div>

            <h2 style={{ fontSize: '1.35rem', fontWeight: '800', color: '#ffffff', marginBottom: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <MapPin color={getRiskColor(activeRegion.risk)} size={22} />
              {activeRegion.name}
            </h2>

            <div style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--primary-emerald)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <Trees size={15} />
              {activeRegion.reserves}
            </div>

            <p style={{ fontSize: '0.825rem', color: 'var(--text-muted)', lineHeight: '1.45', marginBottom: '1rem' }}>
              {activeRegion.description}
            </p>

            {/* GIS Coordinates */}
            <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '1rem', background: 'rgba(0,0,0,0.3)', padding: '0.4rem 0.75rem', borderRadius: '6px' }}>
              <span>Lat: <b>{activeRegion.lat.toFixed(4)}° N</b></span>
              <span>Lng: <b>{activeRegion.lng.toFixed(4)}° E</b></span>
            </div>

            {/* Key Species Pills */}
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '0.4rem', fontWeight: '600' }}>
                Protected Key Species:
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                {activeRegion.species.map(sp => (
                  <span key={sp} style={{
                    fontSize: '0.75rem',
                    background: 'rgba(255, 255, 255, 0.08)',
                    color: 'var(--text-main)',
                    padding: '3px 8px',
                    borderRadius: '6px',
                    border: '1px solid var(--border-color)'
                  }}>
                    🐾 {sp}
                  </span>
                ))}
              </div>
            </div>

            {/* Filter Action Button */}
            <button
              onClick={() => onSelectDistrict && onSelectDistrict(activeRegion.name)}
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: '0.65rem' }}
            >
              <Filter size={16} />
              Filter Today's News Feed For {activeRegion.name}
            </button>
          </div>

          {/* All Divisions Quick List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
              All TN Forest Divisions ({filteredRegions.length}):
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', maxHeight: '190px', overflowY: 'auto', paddingRight: '4px' }}>
              {filteredRegions.map(reg => (
                <div
                  key={reg.id}
                  onClick={() => handleRegionClick(reg)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '0.45rem 0.75rem',
                    borderRadius: '6px',
                    background: activeRegion.id === reg.id ? 'rgba(16, 185, 129, 0.18)' : 'rgba(0, 0, 0, 0.4)',
                    border: activeRegion.id === reg.id ? '1px solid var(--primary-emerald)' : '1px solid var(--border-color)',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                    color: activeRegion.id === reg.id ? '#ffffff' : 'var(--text-muted)',
                    transition: 'all 0.15s'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: getRiskColor(reg.risk) }}></span>
                    <span style={{ fontWeight: activeRegion.id === reg.id ? '700' : '500' }}>{reg.name}</span>
                  </div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{reg.incidents} reports</span>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
