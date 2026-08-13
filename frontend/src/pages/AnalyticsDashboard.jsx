import React, { useState, useEffect } from 'react';
import { fetchAnalytics } from '../services/api';
import { BarChart3, AlertTriangle, MapPin, Layers, Activity, ShieldCheck } from 'lucide-react';
import TamilNaduMap from '../components/TamilNaduMap';

export default function AnalyticsDashboard({ onSelectDistrict }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics().then(res => {
      setData(res);
      setLoading(false);
    }).catch(e => {
      console.error(e);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>Loading Wildlife Intelligence Analytics...</div>;
  }

  if (!data) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div className="glass-card" style={{
        background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(11, 30, 23, 0.6) 100%)',
        borderLeft: '4px solid var(--accent-blue)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', color: 'var(--heading-color)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BarChart3 color="var(--accent-blue)" />
            Tamil Nadu Wildlife Intelligence & Conflict Analytics
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Real-time statistical synthesis of human-wildlife conflicts, protected species encounters, and spatial hotspots.
          </p>
        </div>
      </div>

      {/* Interactive Tamil Nadu Wildlife Map */}
      <TamilNaduMap onSelectDistrict={onSelectDistrict} />


      {/* Metric Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div className="glass-card" style={{ borderTop: '3px solid var(--primary-emerald)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Total Tracked News</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '800', color: 'var(--heading-color)', marginTop: '0.2rem' }}>{data.total_articles}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--primary-emerald)', marginTop: '0.2rem' }}>Aggregated across TN</div>
        </div>

        <div className="glass-card" style={{ borderTop: '3px solid var(--accent-red)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>High Conflict Alerts</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '800', color: 'var(--accent-red)', marginTop: '0.2rem' }}>{data.high_conflict_count}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--accent-red)', marginTop: '0.2rem' }}>Immediate response focus</div>
        </div>

        <div className="glass-card" style={{ borderTop: '3px solid var(--accent-amber)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Medium Conflict Events</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '800', color: 'var(--accent-amber)', marginTop: '0.2rem' }}>{data.medium_conflict_count}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--accent-amber)', marginTop: '0.2rem' }}>Movement monitored</div>
        </div>

        <div className="glass-card" style={{ borderTop: '3px solid var(--accent-blue)' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Conservation & Research</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '800', color: 'var(--accent-blue)', marginTop: '0.2rem' }}>{data.low_conflict_count}</div>
          <div style={{ fontSize: '0.7rem', color: 'var(--accent-blue)', marginTop: '0.2rem' }}>Peaceful / Census updates</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* District Hotspot Ranking */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1.05rem', color: 'var(--heading-color)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <MapPin color="var(--primary-emerald)" size={18} />
            Top Hotspot Districts / Forest Ranges
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {data.top_districts.map(d => {
              const pct = Math.round((d.count / (data.total_articles || 1)) * 100);
              return (
                <div key={d.district}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.25rem' }}>
                    <span style={{ fontWeight: '600', color: 'var(--heading-color)' }}>{d.district}</span>
                    <span style={{ color: 'var(--primary-emerald)', fontWeight: '700' }}>{d.count} events ({pct}%)</span>
                  </div>
                  <div style={{ background: 'var(--input-bg)', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
                    <div style={{ background: 'linear-gradient(90deg, #10b981 0%, #059669 100%)', width: `${pct}%`, height: '100%' }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Species Distribution */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1.05rem', color: 'var(--heading-color)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Activity color="var(--accent-amber)" size={18} />
            Species Mention Frequency
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {data.top_species.map(s => {
              const maxCount = data.top_species[0]?.count || 1;
              const pct = Math.round((s.count / maxCount) * 100);
              return (
                <div key={s.species}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.25rem' }}>
                    <span style={{ fontWeight: '600', color: 'var(--heading-color)' }}>🐾 {s.species}</span>
                    <span style={{ color: 'var(--accent-amber)', fontWeight: '700' }}>{s.count} mentions</span>
                  </div>
                  <div style={{ background: 'var(--input-bg)', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
                    <div style={{ background: 'linear-gradient(90deg, #f59e0b 0%, #d97706 100%)', width: `${pct}%`, height: '100%' }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
