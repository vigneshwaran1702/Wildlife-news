import React from 'react';
import { Search, MapPin, Shield, Layers, Calendar } from 'lucide-react';

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
  const currentDay = filters.dateFilter || 'All';

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', width: '100%' }}>
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
            padding: '0.6rem 1rem 0.6rem 2.4rem',
            background: 'var(--input-bg)',
            border: '1px solid var(--border-color)',
            borderRadius: '8px',
            color: 'var(--text-main)',
            fontSize: '0.9rem',
            outline: 'none'
          }}
        />
      </div>

      {/* Select Controls & Pick Day Toggle Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '0.75rem', width: '100%', alignItems: 'end' }}>
        {/* Pick Day Pill Filter */}
        <div>
          <label style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--primary-emerald)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.35rem' }}>
            <Calendar size={13} color="var(--primary-emerald)" /> Pick Day
          </label>
          <div style={{
            display: 'flex',
            background: 'var(--input-bg)',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            padding: '2px',
            gap: '2px'
          }}>
            <button
              type="button"
              onClick={() => setFilters({ ...filters, dateFilter: 'All' })}
              style={{
                flex: 1,
                padding: '0.4rem 0.2rem',
                borderRadius: '4px',
                border: 'none',
                background: currentDay === 'All' ? 'var(--primary-emerald)' : 'transparent',
                color: currentDay === 'All' ? '#ffffff' : 'var(--text-muted)',
                fontSize: '0.8rem',
                fontWeight: currentDay === 'All' ? '700' : '500',
                cursor: 'pointer',
                transition: 'all 0.15s'
              }}
            >
              All Days
            </button>
            <button
              type="button"
              onClick={() => setFilters({ ...filters, dateFilter: 'TODAY' })}
              style={{
                flex: 1,
                padding: '0.4rem 0.2rem',
                borderRadius: '4px',
                border: 'none',
                background: currentDay === 'TODAY' ? 'var(--primary-emerald)' : 'transparent',
                color: currentDay === 'TODAY' ? '#ffffff' : 'var(--text-muted)',
                fontSize: '0.8rem',
                fontWeight: currentDay === 'TODAY' ? '700' : '500',
                cursor: 'pointer',
                transition: 'all 0.15s'
              }}
            >
              Today
            </button>
            <button
              type="button"
              onClick={() => setFilters({ ...filters, dateFilter: 'YESTERDAY' })}
              style={{
                flex: 1,
                padding: '0.4rem 0.2rem',
                borderRadius: '4px',
                border: 'none',
                background: currentDay === 'YESTERDAY' ? 'var(--accent-amber)' : 'transparent',
                color: currentDay === 'YESTERDAY' ? '#ffffff' : 'var(--text-muted)',
                fontSize: '0.8rem',
                fontWeight: currentDay === 'YESTERDAY' ? '700' : '500',
                cursor: 'pointer',
                transition: 'all 0.15s'
              }}
            >
              Yesterday
            </button>
          </div>
        </div>

        {/* District */}
        <div>
          <label style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.35rem' }}>
            <MapPin size={13} color="var(--primary-emerald)" /> District / Range
          </label>
          <select
            value={filters.district}
            onChange={(e) => setFilters({ ...filters, district: e.target.value })}
            style={{
              width: '100%',
              padding: '0.45rem 0.6rem',
              background: 'var(--input-bg)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              color: 'var(--text-main)',
              fontSize: '0.85rem'
            }}
          >
            {DISTRICTS.map(d => <option key={d} value={d} style={{ background: 'var(--modal-bg)', color: 'var(--text-main)' }}>{d}</option>)}
          </select>
        </div>

        {/* Category */}
        <div>
          <label style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.35rem' }}>
            <Layers size={13} color="var(--accent-amber)" /> Category
          </label>
          <select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
            style={{
              width: '100%',
              padding: '0.45rem 0.6rem',
              background: 'var(--input-bg)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              color: 'var(--text-main)',
              fontSize: '0.85rem'
            }}
          >
            {CATEGORIES.map(c => <option key={c} value={c} style={{ background: 'var(--modal-bg)', color: 'var(--text-main)' }}>{c}</option>)}
          </select>
        </div>

        {/* Conflict Level */}
        <div>
          <label style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.35rem' }}>
            <Shield size={13} color="var(--accent-red)" /> Conflict Risk
          </label>
          <select
            value={filters.conflictLevel}
            onChange={(e) => setFilters({ ...filters, conflictLevel: e.target.value })}
            style={{
              width: '100%',
              padding: '0.45rem 0.6rem',
              background: 'var(--input-bg)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              color: 'var(--text-main)',
              fontSize: '0.85rem'
            }}
          >
            {CONFLICT_LEVELS.map(cl => <option key={cl} value={cl} style={{ background: 'var(--modal-bg)', color: 'var(--text-main)' }}>{cl}</option>)}
          </select>
        </div>
      </div>
    </div>
  );
}
