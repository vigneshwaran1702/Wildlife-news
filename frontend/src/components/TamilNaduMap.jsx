import React, { useState } from 'react';
import { MapPin, ShieldAlert, AlertTriangle, Trees, Compass, Eye, Filter, CheckCircle2 } from 'lucide-react';

// Tamil Nadu Forest Divisions, Tiger Reserves & Districts Data
const TN_REGIONS = [
  {
    id: 'nilgiris',
    name: 'Nilgiris',
    reserves: 'Mudumalai Tiger Reserve & Nilgiri Biosphere',
    cx: 120,
    cy: 130,
    risk: 'High',
    species: ['Elephant', 'Tiger', 'Leopard', 'Gaur'],
    incidents: 12,
    description: 'Critical Elephant corridor connecting Bandipur, Wayanad & Mudumalai.'
  },
  {
    id: 'coimbatore',
    name: 'Coimbatore',
    reserves: 'Mettupalayam, Boluvampatti & Siruvani Ranges',
    cx: 140,
    cy: 200,
    risk: 'High',
    species: ['Elephant', 'Leopard', 'Wild Boar'],
    incidents: 15,
    description: 'Major railway corridor & human-elephant conflict zone near Western Ghats.'
  },
  {
    id: 'erode',
    name: 'Erode & Sathyamangalam',
    reserves: 'Sathyamangalam Tiger Reserve (STR)',
    cx: 200,
    cy: 150,
    risk: 'High',
    species: ['Tiger', 'Elephant', 'Hyena', 'Blackbuck'],
    incidents: 9,
    description: 'Largest wildlife sanctuary in TN connecting Eastern & Western Ghats.'
  },
  {
    id: 'tiruppur',
    name: 'Tiruppur & Anamalai',
    reserves: 'Anamalai Buffer & Amaravathi Range',
    cx: 170,
    cy: 230,
    risk: 'Medium',
    species: ['Elephant', 'Gaur', 'Crocodile'],
    incidents: 6,
    description: 'Udumalpet & Amaravathi reservoir forest divisions.'
  },
  {
    id: 'theni',
    name: 'Theni & Megamalai',
    reserves: 'Srivilliputhur Megamalai Tiger Reserve',
    cx: 170,
    cy: 310,
    risk: 'High',
    species: ['Tiger', 'Elephant', 'Nilgiri Tahr'],
    incidents: 8,
    description: 'High elevation cardamom hill reserve & tiger breeding habitat.'
  },
  {
    id: 'dindigul',
    name: 'Dindigul & Kodaikanal',
    reserves: 'Kodaikanal Wildlife Sanctuary & Palani Hills',
    cx: 220,
    cy: 280,
    risk: 'Medium',
    species: ['Gaur', 'Indian Bison', 'Barking Deer'],
    incidents: 5,
    description: 'Shola-grassland ecosystem with frequent Gaur sightings in urban areas.'
  },
  {
    id: 'tirunelveli',
    name: 'Tirunelveli & KMTR',
    reserves: 'Kalakkad Mundanthurai Tiger Reserve',
    cx: 190,
    cy: 400,
    risk: 'High',
    species: ['Tiger', 'Lion-tailed Macaque', 'Leopard'],
    incidents: 7,
    description: 'First Tiger Reserve in TN, biodiversity hotspot with endemic fauna.'
  },
  {
    id: 'kanyakumari',
    name: 'Kanyakumari',
    reserves: 'Kanyakumari Wildlife Sanctuary',
    cx: 180,
    cy: 450,
    risk: 'Low',
    species: ['Sambar Deer', 'Leopard', 'Viper'],
    incidents: 3,
    description: 'Southernmost tip forest reserve connecting Agasthyamalai Biosphere.'
  },
  {
    id: 'dharmapuri',
    name: 'Dharmapuri & Krishnagiri',
    reserves: 'Cauvery North Wildlife Sanctuary & Hosur',
    cx: 260,
    cy: 110,
    risk: 'High',
    species: ['Elephant', 'Sloth Bear', 'Spotted Deer'],
    incidents: 10,
    description: 'Inter-state elephant migratory path between Karnataka & Tamil Nadu.'
  },
  {
    id: 'salem',
    name: 'Salem & Yercaud',
    reserves: 'Servarayan & Shevaroys Range',
    cx: 260,
    cy: 165,
    risk: 'Medium',
    species: ['Sloth Bear', 'Leopard', 'Pangolin'],
    incidents: 4,
    description: 'Eastern Ghats isolated hill range with sloth bear human encounters.'
  },
  {
    id: 'chennai',
    name: 'Chennai & Vandalur',
    reserves: 'Guindy National Park & Arignar Anna Zoo',
    cx: 390,
    cy: 80,
    risk: 'Low',
    species: ['Blackbuck', 'Jackal', 'Star Tortoise'],
    incidents: 2,
    description: 'Urban forest ecosystem & captive wildlife protection headquarters.'
  },
  {
    id: 'chengalpattu',
    name: 'Chengalpattu & Vedanthangal',
    reserves: 'Vedanthangal Bird Sanctuary',
    cx: 375,
    cy: 115,
    risk: 'Low',
    species: ['Migratory Waterbirds', 'Pelican', 'Heron'],
    incidents: 1,
    description: 'Oldest water bird sanctuary in India with international migratory species.'
  },
  {
    id: 'ramnad',
    name: 'Ramanathapuram & Gulf of Mannar',
    reserves: 'Gulf of Mannar Marine National Park',
    cx: 320,
    cy: 350,
    risk: 'Medium',
    species: ['Dugong (Sea Cow)', 'Sea Turtle', 'Coral Reefs'],
    incidents: 4,
    description: 'First Marine National Park in South Asia & Dugong conservation reserve.'
  },
  {
    id: 'nagapattinam',
    name: 'Nagapattinam & Point Calimere',
    reserves: 'Point Calimere Wildlife & Bird Sanctuary',
    cx: 360,
    cy: 260,
    risk: 'Low',
    species: ['Blackbuck', 'Flamingo', 'Wild Horse'],
    incidents: 2,
    description: 'Coastal wetland sanctuary famed for flamingo flocks & feral horses.'
  },
  {
    id: 'tenkasi',
    name: 'Tenkasi & Virudhunagar',
    reserves: 'Srivilliputhur Grizzled Squirrel Sanctuary',
    cx: 190,
    cy: 355,
    risk: 'Medium',
    species: ['Grizzled Giant Squirrel', 'Elephant', 'Leopard'],
    incidents: 5,
    description: 'Protected canopy habitat for endangered Grizzled Giant Squirrel.'
  }
];

export default function TamilNaduMap({ onSelectDistrict, selectedDistrict }) {
  const [activeRegion, setActiveRegion] = useState(TN_REGIONS[0]);
  const [hoveredRegion, setHoveredRegion] = useState(null);

  const handleRegionClick = (region) => {
    setActiveRegion(region);
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
      {/* Header Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h3 style={{ fontSize: '1.15rem', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Compass color="var(--primary-emerald)" size={20} />
            Tamil Nadu Interactive Wildlife & Hotspot Map
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
            Click any district or tiger reserve marker to view active conflict status, key species & regional news.
          </p>
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', background: 'rgba(0, 0, 0, 0.4)', padding: '0.4rem 0.8rem', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '0.75rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#fca5a5' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#ef4444' }}></span> High Conflict
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#fcd34d' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b' }}></span> Medium Risk
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#6ee7b7' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></span> Protected Zone
          </span>
        </div>
      </div>

      {/* Main Map Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', alignItems: 'center' }}>
        
        {/* Geographic Vector Map View */}
        <div style={{
          position: 'relative',
          background: 'radial-gradient(circle at 40% 40%, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.02) 60%, rgba(10, 22, 16, 0.95) 100%)',
          borderRadius: '12px',
          border: '1px solid var(--border-color)',
          padding: '1rem',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '430px'
        }}>
          <svg viewBox="0 0 450 500" style={{ width: '100%', maxHeight: '420px', filter: 'drop-shadow(0 0 16px rgba(0,0,0,0.6))' }}>
            {/* Tamil Nadu State Outline Path */}
            <path
              d="M 120 100 L 250 80 L 390 60 L 410 100 L 380 160 L 360 260 L 340 320 L 310 370 L 210 430 L 170 480 L 160 440 L 170 380 L 140 300 L 110 210 L 100 150 Z"
              fill="rgba(16, 185, 129, 0.06)"
              stroke="rgba(16, 185, 129, 0.4)"
              strokeWidth="2"
              strokeDasharray="4 2"
            />
            {/* Bay of Bengal & Arabian Sea Coastal Labels */}
            <text x="360" y="200" fill="rgba(255,255,255,0.15)" fontSize="10" fontWeight="700" letterSpacing="1.5">BAY OF BENGAL</text>
            <text x="80" y="380" fill="rgba(255,255,255,0.12)" fontSize="9" fontWeight="700" letterSpacing="1">WESTERN GHATS</text>

            {/* Connecting Corridor Lines */}
            <line x1="120" y1="130" x2="140" y2="200" stroke="rgba(245,158,11,0.3)" strokeWidth="1.5" strokeDasharray="3 3" />
            <line x1="120" y1="130" x2="200" y2="150" stroke="rgba(16,185,129,0.3)" strokeWidth="1.5" strokeDasharray="3 3" />
            <line x1="170" y1="310" x2="190" y2="400" stroke="rgba(239,68,68,0.3)" strokeWidth="1.5" strokeDasharray="3 3" />

            {/* Region Interactive Nodes */}
            {TN_REGIONS.map((region) => {
              const isSelected = activeRegion.id === region.id || selectedDistrict === region.name;
              const isHovered = hoveredRegion?.id === region.id;
              const color = getRiskColor(region.risk);

              return (
                <g
                  key={region.id}
                  onClick={() => handleRegionClick(region)}
                  onMouseEnter={() => setHoveredRegion(region)}
                  onMouseLeave={() => setHoveredRegion(null)}
                  style={{ cursor: 'pointer' }}
                >
                  {/* Glowing outer pulse for high risk */}
                  {region.risk === 'High' && (
                    <circle
                      cx={region.cx}
                      cy={region.cy}
                      r={isSelected ? "18" : "12"}
                      fill={color}
                      opacity="0.25"
                      className="pulse-glow"
                    />
                  )}

                  {/* Base Circle Marker */}
                  <circle
                    cx={region.cx}
                    cy={region.cy}
                    r={isSelected ? "10" : isHovered ? "9" : "7"}
                    fill={isSelected ? color : "rgba(10, 22, 16, 0.9)"}
                    stroke={color}
                    strokeWidth={isSelected ? "3" : "2"}
                    style={{ transition: 'all 0.2s ease' }}
                  />

                  {/* Tiger Reserve Indicator */}
                  {region.reserves.includes('Tiger Reserve') && (
                    <text x={region.cx - 4} y={region.cy + 3} fontSize="8" fill="#ffffff">🐅</text>
                  )}

                  {/* Label Text */}
                  <text
                    x={region.cx + 12}
                    y={region.cy + 4}
                    fill={isSelected ? '#ffffff' : 'var(--text-muted)'}
                    fontSize={isSelected ? "11" : "9.5"}
                    fontWeight={isSelected ? "800" : "500"}
                    style={{ transition: 'all 0.2s ease', pointerEvents: 'none' }}
                  >
                    {region.name}
                  </text>
                </g>
              );
            })}
          </svg>

          {/* Quick Map Floating Badge */}
          <div style={{
            position: 'absolute',
            bottom: '12px',
            left: '12px',
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(8px)',
            padding: '0.4rem 0.75rem',
            borderRadius: '6px',
            border: '1px solid var(--border-color)',
            fontSize: '0.7rem',
            color: 'var(--text-muted)'
          }}>
            🐅 = Recognized Tiger Reserve Division
          </div>
        </div>

        {/* Selected Region Detailed Card */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="glass-card" style={{
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(10, 22, 16, 0.8) 100%)',
            borderLeft: `4px solid ${getRiskColor(activeRegion.risk)}`,
            padding: '1.25rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                District & Forest Division Details
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
                {activeRegion.risk} Risk Conflict Zone
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

            {/* Key Species Pills */}
            <div style={{ marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '0.4rem', fontWeight: '600' }}>
                Protected Key Wildlife Species:
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

            {/* Metrics */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', background: 'rgba(0, 0, 0, 0.3)', padding: '0.75rem', borderRadius: '8px', marginBottom: '1rem' }}>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Recorded Events Today</div>
                <div style={{ fontSize: '1.2rem', fontWeight: '800', color: '#ffffff' }}>{activeRegion.incidents} Reports</div>
              </div>
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Status Filter</div>
                <div style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--primary-emerald)', marginTop: '0.2rem' }}>
                  {selectedDistrict === activeRegion.name ? 'Active Filter' : 'Click to Filter'}
                </div>
              </div>
            </div>

            {/* Filter Feed Action Button */}
            <button
              onClick={() => onSelectDistrict && onSelectDistrict(activeRegion.name)}
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: '0.65rem' }}
            >
              <Filter size={16} />
              Filter Feed For {activeRegion.name}
            </button>
          </div>

          {/* District Selector List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', maxHeight: '140px', overflowY: 'auto', paddingRight: '4px' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-dim)', marginBottom: '0.2rem' }}>
              Select Division Directly:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
              {TN_REGIONS.map(reg => (
                <button
                  key={reg.id}
                  onClick={() => handleRegionClick(reg)}
                  style={{
                    fontSize: '0.75rem',
                    padding: '3px 8px',
                    borderRadius: '6px',
                    border: '1px solid var(--border-color)',
                    background: activeRegion.id === reg.id ? 'var(--primary-emerald)' : 'rgba(0, 0, 0, 0.4)',
                    color: activeRegion.id === reg.id ? '#ffffff' : 'var(--text-muted)',
                    cursor: 'pointer',
                    transition: 'all 0.15s'
                  }}
                >
                  {reg.name}
                </button>
              ))}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
