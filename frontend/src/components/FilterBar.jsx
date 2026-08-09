import React from 'react';
import { Search, Filter, MapPin, Shield, Layers } from 'lucide-react';

const DISTRICTS = [
  'All',
  'Coimbatore',
  'Nilgiris',
  'Erode & Sathyamangalam',
  'Tiruppur & Anamalai',
  'Theni & Megamalai',
  'Dindigul & Kodaikanal',
  'Tirunelveli & KMTR',
  'Kanyakumari',
  'Dharmapuri & Krishnagiri',
  'Salem & Yercaud',
  'Ramanathapuram & Gulf of Mannar',
  'Chennai & Vandalur',
  'Chengalpattu & Vedanthangal',
  'Nagapattinam & Point Calimere',
  'Tiruchirappalli & Namakkal',
  'Tiruvannamalai & Vellore',
  'Thanjavur & Tiruvarur',
  'Tenkasi & Virudhunagar',
  'Villupuram & Cuddalore'
];

const CATEGORIES = [
  'All',
  'Human-Wildlife Conflict',
  'Eco-Tourism & Sanctuaries',
  'Wildlife Crime & Rescue',
  'Forest Fire & Safety',
  'Forest Encroachment',
  'Species Conservation',
  'Forest Dept & Policy'
];

const CONFLICT_LEVELS = ['All', 'High', 'Medium', 'Low', 'None'];

export default function FilterBar({ filters, setFilters }) {
  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Search Input */}
      <div style={{ position: 'relative', width: '100%' }}>
        <Search size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
        <input
          type="text"
          placeholder="Search news by keyword, species, village, or forest range..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          style={{
            width: '100%',
            padding: '0.65rem 1rem 0.65rem 2.4rem',
            background: 'rgba(0, 0, 0, 0.35)',
            border: '1px solid var(--border-color)',
            borderRadius: '8px',
            color: 'var(--text-main)',
            fontSize: '0.9rem',
            outline: 'none'
          }}
        />
      </div>

      {/* Select Dropdowns */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
        {/* District */}
        <div>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.3rem' }}>
            <MapPin size={12} color="var(--primary-emerald)" /> District / Range
          </label>
          <select
            value={filters.district}
            onChange={(e) => setFilters({ ...filters, district: e.target.value })}
            style={{
              width: '100%',
              padding: '0.5rem',
              background: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              color: 'var(--text-main)',
              fontSize: '0.85rem'
            }}
          >
            {DISTRICTS.map(d => <option key={d} value={d} style={{ background: '#0a1610' }}>{d}</option>)}
          </select>
        </div>

        {/* Category */}
        <div>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.3rem' }}>
            <Layers size={12} color="var(--accent-amber)" /> Category
          </label>
          <select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
            style={{
              width: '100%',
              padding: '0.5rem',
              background: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              color: 'var(--text-main)',
              fontSize: '0.85rem'
            }}
          >
            {CATEGORIES.map(c => <option key={c} value={c} style={{ background: '#0a1610' }}>{c}</option>)}
          </select>
        </div>

        {/* Conflict Level */}
        <div>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.3rem' }}>
            <Shield size={12} color="var(--accent-red)" /> Conflict Risk
          </label>
          <select
            value={filters.conflictLevel}
            onChange={(e) => setFilters({ ...filters, conflictLevel: e.target.value })}
            style={{
              width: '100%',
              padding: '0.5rem',
              background: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              color: 'var(--text-main)',
              fontSize: '0.85rem'
            }}
          >
            {CONFLICT_LEVELS.map(cl => <option key={cl} value={cl} style={{ background: '#0a1610' }}>{cl}</option>)}
          </select>
        </div>

        {/* Everyday Date Filter */}
        <div>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.3rem' }}>
            📅 Date Filter
          </label>
          <select
            value={filters.dateFilter || 'All'}
            onChange={(e) => setFilters({ ...filters, dateFilter: e.target.value })}
            style={{
              width: '100%',
              padding: '0.5rem',
              background: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              color: 'var(--text-main)',
              fontSize: '0.85rem'
            }}
          >
            <option value="All" style={{ background: '#0a1610' }}>All Dates</option>
            <option value="TODAY" style={{ background: '#0a1610' }}>🗓️ TODAY</option>
            <option value="YESTERDAY" style={{ background: '#0a1610' }}>📆 YESTERDAY</option>
            <option value="OLD" style={{ background: '#0a1610' }}>📁 OLDER</option>
          </select>
        </div>
      </div>
    </div>
  );
}
