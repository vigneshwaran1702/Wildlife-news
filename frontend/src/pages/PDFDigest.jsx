import React, { useState, useEffect } from 'react';
import { fetchReports } from '../services/api';
import { FileText, Download, Clock, Moon, Sun, Sunset, CheckCircle, ShieldCheck } from 'lucide-react';

export default function PDFDigest() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadReports = async () => {
    setLoading(true);
    try {
      const data = await fetchReports();
      setReports(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
    // Auto-refresh reports list every 60 seconds
    const interval = setInterval(loadReports, 60000);
    return () => clearInterval(interval);
  }, []);

  const shiftSchedules = [
    {
      shiftId: 3,
      time: '08:00 IST',
      label: 'Night Digest',
      range: 'Yesterday 9:00 PM – Today 8:00 AM',
      icon: Moon,
      color: '#a78bfa',
      status: 'Auto-Triggered Daily at 08:00 AM'
    },
    {
      shiftId: 1,
      time: '17:00 IST',
      label: 'Day Digest',
      range: 'Today 8:00 AM – 5:00 PM',
      icon: Sun,
      color: '#f59e0b',
      status: 'Auto-Triggered Daily at 05:00 PM'
    },
    {
      shiftId: 2,
      time: '21:00 IST',
      label: 'Evening Digest',
      range: 'Today 5:00 PM – 9:00 PM',
      icon: Sunset,
      color: '#10b981',
      status: 'Auto-Triggered Daily at 09:00 PM'
    }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header Banner */}
      <div className="glass-card" style={{
        background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(11, 30, 23, 0.6) 100%)',
        borderLeft: '4px solid var(--primary-emerald)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText color="var(--primary-emerald)" />
            Automated PDF Wildlife Bulletins
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Automated backend compilation & download pipeline running at 3 scheduled shift timings daily.
          </p>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.4rem 0.8rem',
          background: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          borderRadius: '20px',
          fontSize: '0.75rem',
          color: '#34d399',
          fontWeight: '600'
        }}>
          <ShieldCheck size={14} /> Automatic Downloader Active
        </div>
      </div>

      {/* Automated Shift Schedules Overview */}
      <div className="glass-card" style={{ background: 'rgba(5, 18, 12, 0.7)', border: '1px solid rgba(16, 185, 129, 0.25)' }}>
        <h3 style={{ fontSize: '1rem', color: '#ffffff', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Clock color="var(--primary-emerald)" size={18} />
          Automated Shift Schedule Matrix
        </h3>
        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          The backend automatically scans news feeds, generates executive PDF reports, and downloads binary files at exact shift intervals:
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
          {shiftSchedules.map((s) => {
            const Icon = s.icon;
            return (
              <div key={s.shiftId} style={{
                background: 'rgba(0, 0, 0, 0.4)',
                border: `1px solid ${s.color}40`,
                borderRadius: '8px',
                padding: '0.9rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: '700', padding: '0.2rem 0.5rem', borderRadius: '4px', background: `${s.color}25`, color: s.color, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <Icon size={12} /> {s.time}
                  </span>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontFamily: 'monospace' }}>Shift {s.shiftId}</span>
                </div>
                <div style={{ fontSize: '0.95rem', fontWeight: '700', color: '#fff', marginTop: '0.2rem' }}>{s.label}</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{s.range}</div>
                <div style={{ fontSize: '0.72rem', color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.3rem', marginTop: '0.2rem' }}>
                  <CheckCircle size={12} /> {s.status}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Automatically Generated Reports Archive */}
      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h3 style={{ fontSize: '1.05rem', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <FileText color="var(--primary-emerald)" size={18} />
            Automated PDF Bulletins Archive ({reports.length})
          </h3>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Auto-refreshed every minute</span>
        </div>

        {loading ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loading automated bulletins archive...</p>
        ) : reports.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            <p style={{ fontSize: '0.85rem' }}>No automated PDF bulletins generated yet. Background scheduler is active.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '500px', overflowY: 'auto' }}>
            {reports.map(rep => (
              <div key={rep.id} style={{
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '0.85rem 1rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{ fontSize: '0.92rem', fontWeight: '700', color: '#fff' }}>{rep.title}</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem', display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                    <span>🏷️ {rep.report_type}</span>
                    <span>📰 {rep.article_count} Articles</span>
                    <span>📅 {new Date(rep.created_at).toLocaleString()}</span>
                  </div>
                </div>

                <a
                  href={rep.download_url}
                  download
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary"
                  style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem', textDecoration: 'none' }}
                >
                  <Download size={14} /> Open PDF
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

