import React, { useState, useEffect } from 'react';
import { fetchReports, generatePDFReport, getShiftTriggerUrl } from '../services/api';
import { FileText, Download, Plus, CheckCircle, Sparkles, Filter, ShieldAlert, Clock, Moon, Sun, Sunset } from 'lucide-react';
import confetti from 'canvas-confetti';

export default function PDFDigest() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const [form, setForm] = useState({
    title: 'Tamil Nadu Wildlife Alert Digest',
    report_type: 'Daily Bulletin',
    category: 'All',
    district: 'All',
    conflict_level: 'All'
  });

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
  }, []);

  const downloadReport = (report) => {
    if (!report?.download_url) return;
    const link = document.createElement('a');
    link.href = report.download_url;
    link.setAttribute('download', `${report.title || 'wildtn-report'}.pdf`);
    link.setAttribute('target', '_blank');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const newReport = await generatePDFReport(form);
      setReports([newReport, ...reports]);
      downloadReport(newReport);
      confetti({ particleCount: 60, spread: 60, origin: { y: 0.7 } });
    } catch (err) {
      alert("Failed to generate PDF report: " + err.message);
    } finally {
      setGenerating(false);
    }
  };

  const shiftSchedules = [
    {
      shiftId: 3,
      time: '08:00 IST',
      label: 'Night Digest',
      range: 'Yesterday 9:00 PM – 8:00 AM',
      icon: Moon,
      color: '#a78bfa',
      url: getShiftTriggerUrl(3)
    },
    {
      shiftId: 1,
      time: '17:00 IST',
      label: 'Day Digest',
      range: 'Today 8:00 AM – 5:00 PM',
      icon: Sun,
      color: '#f59e0b',
      url: getShiftTriggerUrl(1)
    },
    {
      shiftId: 2,
      time: '21:00 IST',
      label: 'Evening Digest',
      range: 'Today 5:00 PM – 9:00 PM',
      icon: Sunset,
      color: '#10b981',
      url: getShiftTriggerUrl(2)
    }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header Banner */}
      <div className="glass-card" style={{
        background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, rgba(11, 30, 23, 0.6) 100%)',
        borderLeft: '4px solid var(--accent-amber)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText color="var(--accent-amber)" />
            PDF Wildlife Intelligence Bulletins
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Auto-generate & download printable executive briefs formatted for Forest Officers, Wildlife Conservationists, and Media.
          </p>
        </div>
      </div>

      {/* Automated Shift Schedules & Direct Trigger Download Links */}
      <div className="glass-card" style={{ background: 'rgba(5, 18, 12, 0.7)', border: '1px solid rgba(16, 185, 129, 0.25)' }}>
        <h3 style={{ fontSize: '1rem', color: '#ffffff', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Clock color="var(--primary-emerald)" size={18} />
          Automated Shift Trigger Schedules & Direct Download Links
        </h3>
        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          PDF digests are compiled automatically at scheduled IST times and can also be triggered manually anytime via API endpoints:
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
          {shiftSchedules.map((s) => {
            const Icon = s.icon;
            return (
              <div key={s.shiftId} style={{
                background: 'rgba(0, 0, 0, 0.4)',
                border: `1px solid ${s.color}40`,
                borderRadius: '8px',
                padding: '0.85rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '0.75rem'
              }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: '700', padding: '0.2rem 0.5rem', borderRadius: '4px', background: `${s.color}25`, color: s.color, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <Icon size={12} /> {s.time}
                    </span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontFamily: 'monospace' }}>Shift {s.shiftId}</span>
                  </div>
                  <div style={{ fontSize: '0.9rem', fontWeight: '700', color: '#fff' }}>{s.label}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{s.range}</div>
                </div>

                <a
                  href={s.url}
                  download
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn"
                  style={{
                    background: `${s.color}20`,
                    color: s.color,
                    border: `1px solid ${s.color}50`,
                    padding: '0.4rem 0.75rem',
                    fontSize: '0.78rem',
                    justifyContent: 'center',
                    textDecoration: 'none'
                  }}
                >
                  <Download size={13} /> Trigger & Download Shift {s.shiftId} PDF
                </a>
              </div>
            );
          })}
        </div>
      </div>


      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Generator Form */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1.05rem', color: '#ffffff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Plus color="var(--primary-emerald)" size={18} />
            Generate Custom PDF Report
          </h3>

          <form onSubmit={handleGenerate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Report Title</label>
              <input
                type="text"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                required
                style={{
                  width: '100%',
                  padding: '0.6rem',
                  background: 'rgba(0, 0, 0, 0.35)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '0.85rem'
                }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Report Type</label>
                <select
                  value={form.report_type}
                  onChange={(e) => setForm({ ...form, report_type: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '0.55rem',
                    background: 'rgba(0, 0, 0, 0.4)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '6px',
                    color: '#fff',
                    fontSize: '0.85rem'
                  }}
                >
                  <option value="Shift 1: Day Bulletin (8:00 AM - 5:00 PM)" style={{ background: '#0a1610' }}>🌅 Shift 1: Day Bulletin (08:00 AM – 05:00 PM)</option>
                  <option value="Shift 2: Evening Bulletin (5:00 PM - 9:00 PM)" style={{ background: '#0a1610' }}>🌇 Shift 2: Evening Bulletin (05:00 PM – 09:00 PM)</option>
                  <option value="Shift 3: Night & Early Morning Bulletin (9:00 PM - 8:00 AM)" style={{ background: '#0a1610' }}>🌙 Shift 3: Night & Early Morning Bulletin (09:00 PM – 08:00 AM)</option>
                  <option value="Daily Bulletin" style={{ background: '#0a1610' }}>📰 Full Daily Bulletin (All Today's News)</option>
                  <option value="Conflict Briefing" style={{ background: '#0a1610' }}>🚨 High Risk Conflict Briefing</option>
                  <option value="Weekly Digest" style={{ background: '#0a1610' }}>📊 Weekly Conservation Digest</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>District Filter</label>
                <select
                  value={form.district}
                  onChange={(e) => setForm({ ...form, district: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '0.55rem',
                    background: 'rgba(0, 0, 0, 0.4)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '6px',
                    color: '#fff',
                    fontSize: '0.85rem'
                  }}
                >
                  <option value="All" style={{ background: '#0a1610' }}>All TN Districts</option>
                  <option value="Coimbatore" style={{ background: '#0a1610' }}>Coimbatore & Valparai</option>
                  <option value="Nilgiris" style={{ background: '#0a1610' }}>Nilgiris & Mudumalai</option>
                  <option value="Erode & Sathyamangalam" style={{ background: '#0a1610' }}>Erode & Sathyamangalam</option>
                  <option value="Tiruppur & Anamalai" style={{ background: '#0a1610' }}>Tiruppur & Anamalai</option>
                  <option value="Theni & Megamalai" style={{ background: '#0a1610' }}>Theni & Megamalai</option>
                  <option value="Dindigul & Kodaikanal" style={{ background: '#0a1610' }}>Dindigul & Kodaikanal</option>
                  <option value="Tirunelveli & KMTR" style={{ background: '#0a1610' }}>Tirunelveli & KMTR</option>
                  <option value="Kanyakumari" style={{ background: '#0a1610' }}>Kanyakumari Sanctuary</option>
                  <option value="Dharmapuri & Krishnagiri" style={{ background: '#0a1610' }}>Dharmapuri & Krishnagiri</option>
                  <option value="Salem & Yercaud" style={{ background: '#0a1610' }}>Salem & Yercaud</option>
                  <option value="Ramanathapuram & Gulf of Mannar" style={{ background: '#0a1610' }}>Ramanathapuram & Marine NP</option>
                  <option value="Chennai & Vandalur" style={{ background: '#0a1610' }}>Chennai & Vandalur Zoo</option>
                  <option value="Chengalpattu & Vedanthangal" style={{ background: '#0a1610' }}>Vedanthangal Sanctuary</option>
                  <option value="Nagapattinam & Point Calimere" style={{ background: '#0a1610' }}>Point Calimere Sanctuary</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Category Filter</label>
                <select
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '0.55rem',
                    background: 'rgba(0, 0, 0, 0.4)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '6px',
                    color: '#fff',
                    fontSize: '0.85rem'
                  }}
                >
                  <option value="All" style={{ background: '#0a1610' }}>All Categories</option>
                  <option value="Human-Wildlife Conflict" style={{ background: '#0a1610' }}>Human-Wildlife Conflict</option>
                  <option value="Eco-Tourism & Sanctuaries" style={{ background: '#0a1610' }}>Eco-Tourism & Sanctuaries</option>
                  <option value="Wildlife Crime & Rescue" style={{ background: '#0a1610' }}>Wildlife Crime & Rescue</option>
                  <option value="Forest Fire & Safety" style={{ background: '#0a1610' }}>Forest Fire & Safety</option>
                  <option value="Forest Encroachment" style={{ background: '#0a1610' }}>Forest Encroachment</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>Risk Filter</label>
                <select
                  value={form.conflict_level}
                  onChange={(e) => setForm({ ...form, conflict_level: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '0.55rem',
                    background: 'rgba(0, 0, 0, 0.4)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '6px',
                    color: '#fff',
                    fontSize: '0.85rem'
                  }}
                >
                  <option value="All" style={{ background: '#0a1610' }}>All Risk Levels</option>
                  <option value="High" style={{ background: '#0a1610' }}>High Risk Only</option>
                  <option value="Medium" style={{ background: '#0a1610' }}>Medium Risk Only</option>
                </select>
              </div>
            </div>

            <button type="submit" className="btn btn-amber" disabled={generating} style={{ marginTop: '0.5rem' }}>
              <Sparkles size={16} />
              {generating ? 'Compiling PDF Digest...' : 'Compile & Generate PDF'}
            </button>
          </form>
        </div>

        {/* Reports Archive */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <h3 style={{ fontSize: '1.05rem', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <FileText color="var(--primary-emerald)" size={18} />
            Generated Report Archive ({reports.length})
          </h3>

          {loading ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loading archive...</p>
          ) : reports.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              <p style={{ fontSize: '0.85rem' }}>No PDF reports generated yet. Click compile above!</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto' }}>
              {reports.map(rep => (
                <div key={rep.id} style={{
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '0.75rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}>
                  <div>
                    <div style={{ fontSize: '0.9rem', fontWeight: '700', color: '#fff' }}>{rep.title}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                      {rep.report_type} • {rep.article_count} Articles • {new Date(rep.created_at).toLocaleDateString()}
                    </div>
                  </div>

                  <a
                    href={rep.download_url}
                    download
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-primary"
                    style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
                  >
                    <Download size={14} /> Download PDF
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
