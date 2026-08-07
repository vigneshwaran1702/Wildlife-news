import React, { useState, useEffect } from 'react';
import { fetchCollectorLogs, triggerCollectors } from '../services/api';
import { Radio, RefreshCw, CheckCircle2, AlertTriangle, Terminal, Rss } from 'lucide-react';

export default function CollectorJobs({ onScanComplete }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await fetchCollectorLogs();
      setLogs(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const handleScan = async () => {
    setScanning(true);
    try {
      await triggerCollectors();
      await loadLogs();
      if (onScanComplete) onScanComplete();
    } catch (e) {
      alert("Error scanning feeds: " + e.message);
    } finally {
      setScanning(false);
    }
  };

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
            <Radio color="var(--primary-emerald)" />
            Web Scrapers & RSS Collector Control Center
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Monitor real-time collector pipelines aggregating Tamil and English environmental news portals across TN.
          </p>
        </div>

        <button className="btn btn-primary" onClick={handleScan} disabled={scanning}>
          <RefreshCw size={16} className={scanning ? 'spin-icon' : ''} />
          {scanning ? 'Scanning All Sources...' : 'Trigger Immediate Feed Scan'}
        </button>
      </div>

      {/* Live Logs Terminal View */}
      <div className="glass-card" style={{ background: '#050c09', border: '1px solid #143525' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid #143525', paddingBottom: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--primary-emerald)', fontWeight: '700' }}>
            <Terminal size={16} />
            Collector Log Stream ({logs.length} entries)
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>APScheduler 15-Min Interval Active</span>
        </div>

        {loading ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loading log stream...</p>
        ) : logs.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No collector logs recorded yet. Trigger a scan above!</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem', maxHeight: '450px', overflowY: 'auto', fontFamily: 'monospace' }}>
            {logs.map(log => (
              <div key={log.id} style={{
                background: 'rgba(15, 31, 23, 0.4)',
                border: '1px solid rgba(34, 77, 56, 0.3)',
                borderRadius: '6px',
                padding: '0.6rem 0.8rem',
                fontSize: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{ color: log.status === 'Success' ? '#34d399' : '#fcd34d', fontWeight: '700' }}>
                    [{log.status.toUpperCase()}]
                  </span>
                  <span style={{ color: '#ffffff', fontWeight: '600' }}>{log.collector_name}</span>
                  <span style={{ color: 'var(--text-muted)' }}>— {log.log_message}</span>
                </div>
                <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
