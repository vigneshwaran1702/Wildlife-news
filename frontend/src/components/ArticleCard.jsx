import React from 'react';
import { Bookmark, ExternalLink, ShieldAlert, MapPin, Tag, Clock, Eye, Sparkles } from 'lucide-react';

export default function ArticleCard({ article, lang, onSelect, onToggleBookmark }) {
  const isHighRisk = article.conflict_level === 'High';
  const isMedRisk = article.conflict_level === 'Medium';

  const riskClass = isHighRisk ? 'badge-risk-high' : isMedRisk ? 'badge-risk-medium' : 'badge-risk-low';

  const title = (lang === 'ta' && article.title_ta) ? article.title_ta : article.title_en;
  const summary = (lang === 'ta' && article.summary_ta) ? article.summary_ta : article.summary_en;

  const publishedDate = new Date(article.published_at).toLocaleDateString(lang === 'ta' ? 'ta-IN' : 'en-US', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <article className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      {/* Top Header Row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className={riskClass}>
            <ShieldAlert size={12} />
            {article.conflict_level.toUpperCase()} RISK
          </span>
          <span className="badge-tag">
            <MapPin size={10} style={{ marginRight: '3px' }} />
            {article.district}
          </span>
          <span className="badge-tag">{article.category}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button 
            onClick={(e) => { e.stopPropagation(); onToggleBookmark(article.id); }}
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', padding: '4px' }}
            title="Save article"
          >
            <Bookmark size={18} fill={article.is_bookmarked ? "#10b981" : "none"} color={article.is_bookmarked ? "#10b981" : "var(--text-muted)"} />
          </button>
        </div>
      </div>

      {/* Article Title */}
      <h3 
        onClick={() => onSelect(article)}
        className={lang === 'ta' ? 'tamil-font' : ''}
        style={{
          fontSize: '1.1rem',
          fontWeight: '700',
          lineHeight: '1.4',
          color: '#ffffff',
          cursor: 'pointer',
          transition: 'color 0.2s'
        }}
      >
        {title}
      </h3>

      {/* AI Summary Bullets */}
      <div style={{
        background: 'rgba(0, 0, 0, 0.3)',
        borderRadius: '8px',
        padding: '0.75rem',
        borderLeft: '3px solid var(--primary-emerald)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', fontWeight: '700', color: 'var(--primary-emerald)', marginBottom: '0.4rem' }}>
          <Sparkles size={12} /> AI Bullet Digest
        </div>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-main)', whiteSpace: 'pre-line', lineHeight: '1.4' }}>
          {summary}
        </div>
      </div>

      {/* Species & Footer details */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid var(--border-color)', paddingTop: '0.65rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', flexWrap: 'wrap' }}>
          {article.species && article.species.map(s => (
            <span key={s} style={{
              fontSize: '0.7rem',
              background: 'rgba(16, 185, 129, 0.1)',
              color: 'var(--primary-emerald)',
              padding: '2px 6px',
              borderRadius: '4px'
            }}>
              🐾 {s}
            </span>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-dim)' }}>
          <a
            href={article.source_url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            style={{
              color: 'var(--primary-emerald)',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '0.2rem',
              fontWeight: '600',
              padding: '0.25rem 0.5rem',
              background: 'rgba(16, 185, 129, 0.12)',
              borderRadius: '4px',
              border: '1px solid rgba(16, 185, 129, 0.3)'
            }}
          >
            {article.source_name} <ExternalLink size={12} />
          </a>
          <a
            href={`https://news.google.com/search?q=${encodeURIComponent(article.title_en + ' Tamil Nadu')}`}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            style={{
              color: '#6ee7b7',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '0.2rem',
              fontWeight: '600',
              padding: '0.25rem 0.5rem',
              background: 'rgba(59, 130, 246, 0.15)',
              borderRadius: '4px',
              border: '1px solid rgba(59, 130, 246, 0.3)'
            }}
          >
            Google News <ExternalLink size={12} />
          </a>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
            <Clock size={12} /> {publishedDate}
          </span>
          <button 
            onClick={() => onSelect(article)}
            className="btn btn-secondary"
            style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
          >
            Read Brief
          </button>
        </div>
      </div>
    </article>
  );
}
