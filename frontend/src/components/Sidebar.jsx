import React from 'react';
import { Newspaper, FileText, BarChart3, Radio, AlertTriangle, ShieldCheck, MapPin } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, analytics }) {
  const navItems = [
    { id: 'feed', label: 'Live News Feed', icon: Newspaper },
    { id: 'pdf', label: 'PDF Bulletins & Digest', icon: FileText },
    { id: 'analytics', label: 'Conflict & Hotspot Map', icon: BarChart3 },
    { id: 'collectors', label: 'Collectors & Feeds', icon: Radio },
  ];

  return (
    <aside style={{ width: '260px', flexShrink: 0, display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Navigation */}
      <div className="glass-card" style={{ padding: '0.75rem' }}>
        <div style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', padding: '0.5rem 0.75rem' }}>
          Navigation
        </div>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.65rem 0.85rem',
                  borderRadius: '8px',
                  border: 'none',
                  background: isActive ? 'rgba(16, 185, 129, 0.15)' : 'transparent',
                  color: isActive ? 'var(--primary-emerald)' : 'var(--text-muted)',
                  borderLeft: isActive ? '3px solid var(--primary-emerald)' : '3px solid transparent',
                  fontWeight: isActive ? '600' : '400',
                  fontSize: '0.9rem',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s ease'
                }}
              >
                <Icon size={18} color={isActive ? "var(--primary-emerald)" : "var(--text-muted)"} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Live Threat Counter */}
      {analytics && (
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--text-muted)' }}>TN Conflict Alert Level</span>
            <AlertTriangle size={16} color="var(--accent-red)" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
            <div style={{
              background: 'rgba(239, 68, 68, 0.12)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '8px',
              padding: '0.6rem',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '1.25rem', fontWeight: '800', color: '#fca5a5' }}>{analytics.high_conflict_count}</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>High Risk</div>
            </div>

            <div style={{
              background: 'rgba(245, 158, 11, 0.12)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              borderRadius: '8px',
              padding: '0.6rem',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '1.25rem', fontWeight: '800', color: '#fcd34d' }}>{analytics.medium_conflict_count}</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Medium Risk</div>
            </div>
          </div>

          {/* Top Hotspot District */}
          {analytics.top_districts && analytics.top_districts.length > 0 && (
            <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '0.65rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '0.4rem' }}>
                <MapPin size={14} color="var(--primary-emerald)" />
                Top Incident Hotspot
              </div>
              <div style={{ fontSize: '0.85rem', fontWeight: '700', color: '#ffffff' }}>
                {analytics.top_districts[0].district} ({analytics.top_districts[0].count} events)
              </div>
            </div>
          )}
        </div>
      )}
    </aside>
  );
}
