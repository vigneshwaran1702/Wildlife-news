import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap } from 'react-leaflet';
import L from 'leaflet';
import { MapPin, Compass, Trees, Filter, RefreshCw } from 'lucide-react';

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
      <div style="width:22px; height:22px; border-radius:50%; background:${bg}; border:2px solid #ffffff; box-shadow: 0 0 10px ${bg}; display:flex; align-items:center; justify-content:center; color:#ffffff; font-weight:bold; font-size:11px;">
        ${hasTiger ? '🐅' : '📍'}
      </div>
    </div>
  `;
  return L.divIcon({
    html: iconHtml,
    className: 'custom-leaflet-pin',
    iconSize: [22, 22],
    iconAnchor: [11, 11]
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
  const [tileLayerType, setTileLayerType] = useState('dark');
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
    <div style={{ position: 'relative', width: '100%', height: 'calc(100vh - 120px)', minHeight: '680px', borderRadius: '14px', overflow: 'hidden', border: '1px solid var(--border-color)', boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }}>
      {/* Full-Screen Leaflet Map */}
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

        {TN_FULL_MAP_REGIONS.map((region) => {
          const hasTiger = region.reserves.includes('Tiger Reserve');
          const customIcon = createCustomMarker(region.risk, region.name, hasTiger);

          return (
            <React.Fragment key={region.id}>
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

      {/* Floating Header Controls Overlay (Top-Left) */}
      <div style={{
        position: 'absolute',
        top: '16px',
        left: '16px',
        zIndex: 1000,
        background: 'rgba(10, 22, 16, 0.88)',
        backdropFilter: 'blur(12px)',
        padding: '0.65rem 1rem',
        borderRadius: '10px',
        border: '1px solid var(--border-color)',
        boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        flexWrap: 'wrap'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Compass color="var(--primary-emerald)" size={20} />
          <span style={{ fontSize: '0.95rem', fontWeight: '700', color: '#ffffff' }}>
            Full Tamil Nadu GIS Wildlife Map
          </span>
        </div>

        {/* Tile Layer Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', background: 'rgba(0,0,0,0.4)', padding: '2px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
          {['dark', 'satellite', 'osm'].map(layer => (
            <button
              key={layer}
              type="button"
              onClick={() => setTileLayerType(layer)}
              style={{
                padding: '0.25rem 0.6rem',
                borderRadius: '4px',
                border: 'none',
                background: tileLayerType === layer ? 'var(--primary-emerald)' : 'transparent',
                color: tileLayerType === layer ? '#ffffff' : 'var(--text-muted)',
                fontSize: '0.75rem',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              {layer === 'dark' ? 'Dark GIS' : layer === 'satellite' ? 'Satellite' : 'Standard'}
            </button>
          ))}
        </div>

        {/* Reset View Button */}
        <button
          type="button"
          onClick={() => { setMapCenter([11.1271, 78.6569]); setMapZoom(7.2); }}
          className="btn btn-secondary"
          style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
        >
          <RefreshCw size={12} /> Reset View
        </button>
      </div>

      {/* Floating Metadata Overlay Panel (Top-Right) */}
      <div style={{
        position: 'absolute',
        top: '16px',
        right: '16px',
        zIndex: 1000,
        width: '340px',
        maxHeight: 'calc(100% - 32px)',
        overflowY: 'auto',
        background: 'rgba(10, 22, 16, 0.92)',
        backdropFilter: 'blur(16px)',
        borderRadius: '12px',
        border: '1px solid var(--border-color)',
        borderLeft: `4px solid ${getRiskColor(activeRegion.risk)}`,
        boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
        padding: '1.1rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.85rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.7rem', fontWeight: '700', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Division GIS Metadata
          </span>
          <span style={{
            fontSize: '0.65rem',
            fontWeight: '700',
            padding: '2px 6px',
            borderRadius: '4px',
            background: `${getRiskColor(activeRegion.risk)}22`,
            color: getRiskColor(activeRegion.risk),
            border: `1px solid ${getRiskColor(activeRegion.risk)}44`
          }}>
            {activeRegion.risk} Risk Division
          </span>
        </div>

        <h3 style={{ fontSize: '1.25rem', fontWeight: '800', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '0.4rem', margin: 0 }}>
          <MapPin color={getRiskColor(activeRegion.risk)} size={20} />
          {activeRegion.name}
        </h3>

        <div style={{ fontSize: '0.8rem', fontWeight: '600', color: 'var(--primary-emerald)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <Trees size={14} />
          {activeRegion.reserves}
        </div>

        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: '1.4', margin: 0 }}>
          {activeRegion.description}
        </p>

        {/* GIS Coordinates */}
        <div style={{ display: 'flex', gap: '0.8rem', fontSize: '0.72rem', color: 'var(--text-dim)', background: 'rgba(0,0,0,0.3)', padding: '0.35rem 0.65rem', borderRadius: '6px' }}>
          <span>Lat: <b>{activeRegion.lat.toFixed(4)}° N</b></span>
          <span>Lng: <b>{activeRegion.lng.toFixed(4)}° E</b></span>
        </div>

        {/* Key Species Pills */}
        <div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginBottom: '0.35rem', fontWeight: '600' }}>
            Protected Key Species:
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
            {activeRegion.species.map(sp => (
              <span key={sp} style={{
                fontSize: '0.72rem',
                background: 'rgba(255, 255, 255, 0.08)',
                color: 'var(--text-main)',
                padding: '2px 7px',
                borderRadius: '5px',
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
          style={{ width: '100%', justifyContent: 'center', padding: '0.55rem', fontSize: '0.8rem' }}
        >
          <Filter size={14} />
          Filter Today's News Feed For {activeRegion.name}
        </button>

        {/* Quick Division Selector List */}
        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.65rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
          <div style={{ fontSize: '0.7rem', fontWeight: '700', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '0.2rem' }}>
            All TN Divisions ({TN_FULL_MAP_REGIONS.length}):
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', maxHeight: '160px', overflowY: 'auto', paddingRight: '3px' }}>
            {TN_FULL_MAP_REGIONS.map(reg => (
              <div
                key={reg.id}
                onClick={() => handleRegionClick(reg)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.35rem 0.6rem',
                  borderRadius: '5px',
                  background: activeRegion.id === reg.id ? 'rgba(16, 185, 129, 0.2)' : 'rgba(0, 0, 0, 0.35)',
                  border: activeRegion.id === reg.id ? '1px solid var(--primary-emerald)' : '1px solid var(--border-color)',
                  cursor: 'pointer',
                  fontSize: '0.75rem',
                  color: activeRegion.id === reg.id ? '#ffffff' : 'var(--text-muted)',
                  transition: 'all 0.15s'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: getRiskColor(reg.risk) }}></span>
                  <span style={{ fontWeight: activeRegion.id === reg.id ? '700' : '400' }}>{reg.name}</span>
                </div>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-dim)' }}>{reg.incidents} reports</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Floating Info Legend (Bottom-Left) */}
      <div style={{
        position: 'absolute',
        bottom: '16px',
        left: '16px',
        zIndex: 1000,
        background: 'rgba(10, 22, 16, 0.88)',
        backdropFilter: 'blur(8px)',
        padding: '0.4rem 0.75rem',
        borderRadius: '6px',
        border: '1px solid var(--border-color)',
        fontSize: '0.72rem',
        color: 'var(--text-muted)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem'
      }}>
        <span>Showing All {TN_FULL_MAP_REGIONS.length} Wildlife Divisions</span>
        <span>🐅 Tiger Reserve</span>
        <span>📍 Forest Division</span>
      </div>
    </div>
  );
}
