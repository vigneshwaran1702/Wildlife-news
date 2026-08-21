import React from 'react';
import { Bookmark, ExternalLink, ShieldAlert, MapPin, Tag, Clock, Eye, Sparkles } from 'lucide-react';

function stripHtml(raw) {
  if (!raw) return '';
  if (typeof raw !== 'string') return String(raw);
  try {
    const doc = new DOMParser().parseFromString(raw, 'text/html');
    return (doc.body.textContent || '').replace(/\s+/g, ' ').trim();
  } catch (e) {
    return raw.replace(/<[^>]*>?/gm, '').replace(/&nbsp;/g, ' ').trim();
  }
}

export default function ArticleCard({ article, lang, onSelect, onToggleBookmark }) {
  const isHighRisk = article.conflict_level === 'High';
  const isMedRisk = article.conflict_level === 'Medium';

  const riskClass = isHighRisk ? 'badge-risk-high' : isMedRisk ? 'badge-risk-medium' : 'badge-risk-low';

  const rawTitle = (lang === 'ta' && article.title_ta) ? article.title_ta : article.title_en;
  const rawSummary = (lang === 'ta' && article.summary_ta) ? article.summary_ta : article.summary_en;
  const rawContent = (lang === 'ta' && article.content_ta) ? article.content_ta : article.content_en;

  const title = stripHtml(rawTitle);
  const summary = stripHtml(rawSummary);
  const content = stripHtml(rawContent);

  const formatArticleDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.toLocaleString(lang === 'ta' ? 'ta-IN' : 'en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      });
    } catch (e) {
      return dateStr;
    }
  };

  const publishedDate = formatArticleDate(article.published_at);

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

  const dateStatus = article.date_status || 'TODAY';
  const statusBadgeStyle = dateStatus === 'TODAY' 
    ? { background: 'rgba(16, 185, 129, 0.2)', color: '#10b981', border: '1px solid rgba(16, 185, 129, 0.4)' }
    : dateStatus === 'YESTERDAY'
    ? { background: 'rgba(245, 158, 11, 0.2)', color: '#f59e0b', border: '1px solid rgba(245, 158, 11, 0.4)' }
    : { background: 'rgba(100, 116, 139, 0.2)', color: '#94a3b8', border: '1px solid rgba(100, 116, 139, 0.4)' };

  return (
    <article className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
      {/* Top Header Row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{
            fontSize: '0.7rem',
            fontWeight: '800',
            padding: '2px 8px',
            borderRadius: '4px',
            textTransform: 'uppercase',
            ...statusBadgeStyle
          }}>
            {dateStatus === 'TODAY' ? '🗓️ TODAY' : dateStatus === 'YESTERDAY' ? '📆 YESTERDAY' : '📁 OLD'}
          </span>
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

      {/* Article Heading */}
      <div>
        <span style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--primary-emerald)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          📌 HEADING
        </span>
        <h3 
          onClick={() => onSelect(article)}
          className={lang === 'ta' ? 'tamil-font' : ''}
          style={{
            fontSize: '1.1rem',
            fontWeight: '700',
            lineHeight: '1.4',
            color: 'var(--heading-color)',
            cursor: 'pointer',
            marginTop: '0.2rem',
            transition: 'color 0.2s'
          }}
        >
          {title}
        </h3>
      </div>

      {/* Where (Location) Box */}
      <div style={{
        background: 'rgba(59, 130, 246, 0.1)',
        border: '1px solid rgba(59, 130, 246, 0.25)',
        borderRadius: '6px',
        padding: '0.5rem 0.75rem',
        fontSize: '0.85rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.4rem',
        color: 'var(--accent-blue)'
      }}>
        <MapPin size={14} color="var(--accent-blue)" />
        <span><b>📍 WHERE:</b> {article.district}</span>
      </div>

      {/* What Happened - Brief Explanation */}
      <div style={{
        background: 'var(--card-box-bg)',
        borderRadius: '8px',
        padding: '0.75rem',
        border: '1px solid var(--border-color)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', fontWeight: '700', color: 'var(--accent-blue)', marginBottom: '0.4rem' }}>
          <Sparkles size={12} /> 📖 BRIEF EXPLANATION
        </div>
        <div className={lang === 'ta' ? 'tamil-font' : ''} style={{ fontSize: '0.88rem', color: 'var(--text-main)', lineHeight: '1.5' }}>
          {content}
        </div>
      </div>

      {/* AI Key Highlights */}
      <div style={{
        background: 'var(--highlight-box-bg)',
        borderRadius: '8px',
        padding: '0.75rem',
        borderLeft: '3px solid var(--primary-emerald)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', fontWeight: '700', color: 'var(--primary-emerald)', marginBottom: '0.4rem' }}>
          <Sparkles size={12} /> ⚡ KEY HIGHLIGHTS
        </div>
        <div className={lang === 'ta' ? 'tamil-font' : ''} style={{ fontSize: '0.85rem', color: 'var(--text-main)', whiteSpace: 'pre-line', lineHeight: '1.4' }}>
          {summary}
        </div>
      </div>

      {/* Species & Footer details (No Source Link) */}
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
          <button 
            onClick={() => onSelect(article)}
            className="btn btn-secondary"
            style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
          >
            Read Full Brief
          </button>
        </div>
      </div>
    </article>
  );
}
