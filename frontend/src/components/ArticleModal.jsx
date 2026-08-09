import React, { useState } from 'react';
import { X, ExternalLink, Bookmark, Sparkles, MapPin, ShieldAlert, Building, AlertTriangle } from 'lucide-react';

export default function ArticleModal({ article, onClose, onToggleBookmark }) {
  const [viewLang, setViewLang] = useState('en');

  if (!article) return null;

  const isTamil = viewLang === 'ta';
  const title = (isTamil && article.title_ta) ? article.title_ta : article.title_en;
  const content = (isTamil && article.content_ta) ? article.content_ta : article.content_en;
  const summary = (isTamil && article.summary_ta) ? article.summary_ta : article.summary_en;

  const handleOpenSource = (e, url) => {
    e.stopPropagation();
    e.preventDefault();
    if (!url) return;
    try {
      const win = window.open(url, '_blank', 'noopener,noreferrer');
      if (!win) {
        window.location.href = url;
      }
    } catch (err) {
      window.location.href = url;
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header Bar */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span className={`badge-risk-${article.conflict_level.toLowerCase()}`}>
              <ShieldAlert size={12} />
              {article.conflict_level.toUpperCase()} RISK
            </span>
            <span className="badge-tag">{article.district}</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {/* Modal Language Toggle */}
            <div className="lang-toggle">
              <button className={`lang-btn ${viewLang === 'en' ? 'active' : ''}`} onClick={() => setViewLang('en')}>English</button>
              <button className={`lang-btn ${viewLang === 'ta' ? 'active' : ''}`} onClick={() => setViewLang('ta')}>தமிழ்</button>
            </div>
            <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Title */}
        <h2 className={isTamil ? 'tamil-font' : ''} style={{ fontSize: '1.35rem', fontWeight: '800', lineHeight: '1.35', color: '#ffffff', marginBottom: '0.75rem' }}>
          {title}
        </h2>

        {/* Metadata */}
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem', display: 'flex', gap: '1rem' }}>
          <span>Source: <b>{article.source_name}</b></span>
          <span>•</span>
          <span>Category: <b>{article.category}</b></span>
        </div>

        {/* Key Entities Box */}
        {article.key_entities && (
          <div style={{
            background: 'rgba(16, 185, 129, 0.08)',
            border: '1px solid rgba(16, 185, 129, 0.25)',
            borderRadius: '10px',
            padding: '1rem',
            marginBottom: '1.25rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', fontWeight: '700', color: 'var(--primary-emerald)', marginBottom: '0.5rem' }}>
              <Sparkles size={14} /> AI Extracted Intelligence
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.8rem' }}>
              <div>
                <span style={{ color: 'var(--text-dim)' }}>Target Locations:</span>
                <div style={{ fontWeight: '600', color: '#fff' }}>{article.key_entities.locations?.join(', ') || article.district}</div>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)' }}>Species Involved:</span>
                <div style={{ fontWeight: '600', color: 'var(--accent-amber)' }}>{article.key_entities.species?.join(', ') || 'Wildlife'}</div>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)' }}>Forest Authorities:</span>
                <div style={{ fontWeight: '600', color: '#fff' }}>{article.key_entities.authorities?.join(', ')}</div>
              </div>
              <div>
                <span style={{ color: 'var(--text-dim)' }}>Assessed Impact:</span>
                <div style={{ fontWeight: '600', color: '#fff' }}>{article.key_entities.impact}</div>
              </div>
            </div>
          </div>
        )}

        {/* Article Full Content (What Happened) */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--primary-emerald)', textTransform: 'uppercase', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Sparkles size={14} /> ⚡ WHAT HAPPENED
          </div>
          <div className={isTamil ? 'tamil-font' : ''} style={{ fontSize: '0.95rem', lineHeight: '1.6', color: 'var(--text-main)' }}>
            {content}
          </div>
        </div>

        {/* Footer Actions */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid var(--border-color)', paddingTop: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <button 
            className="btn btn-secondary"
            onClick={() => onToggleBookmark(article.id)}
          >
            <Bookmark size={16} fill={article.is_bookmarked ? "#10b981" : "none"} />
            {article.is_bookmarked ? 'Saved in Bookmarks' : 'Save Article'}
          </button>
          <button className="btn btn-primary" onClick={onClose}>
            Close Brief
          </button>
        </div>
      </div>
    </div>
  );
}
