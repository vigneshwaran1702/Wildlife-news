import React, { useState, useEffect } from 'react';
import FilterBar from '../components/FilterBar';
import ArticleCard from '../components/ArticleCard';
import ArticleModal from '../components/ArticleModal';
import { fetchArticles, toggleBookmark } from '../services/api';
import { ShieldAlert, Newspaper, Sparkles } from 'lucide-react';

export default function NewsFeed({ lang, bookmarkedOnly, onArticlesUpdated }) {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedArticle, setSelectedArticle] = useState(null);

  const [filters, setFilters] = useState({
    search: '',
    district: 'All',
    category: 'All',
    conflictLevel: 'All',
    species: 'All',
    dateFilter: 'All'
  });

  const loadData = async () => {
    setLoading(true);
    try {
      let data = await fetchArticles({ ...filters, bookmarkedOnly, date_status: filters.dateFilter !== 'All' ? filters.dateFilter : undefined });
      if (filters.dateFilter && filters.dateFilter !== 'All') {
        data = data.filter(a => (a.date_status || 'TODAY').toUpperCase() === filters.dateFilter.toUpperCase());
      }
      setArticles(data);
      if (onArticlesUpdated) onArticlesUpdated();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [filters, bookmarkedOnly]);

  const handleToggleBookmark = async (id) => {
    try {
      const updated = await toggleBookmark(id);
      setArticles(articles.map(a => a.id === id ? updated : a));
      if (selectedArticle && selectedArticle.id === id) {
        setSelectedArticle(updated);
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
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
            <Newspaper color="var(--primary-emerald)" />
            {bookmarkedOnly ? 'Bookmarked Wildlife News' : 'Tamil Nadu Wildlife News Feed'}
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Continuous AI analysis of human-animal conflicts, forest department bulletins, & conservation news across TN reserves.
          </p>
        </div>
        <div style={{
          background: 'rgba(0, 0, 0, 0.4)',
          padding: '0.4rem 0.8rem',
          borderRadius: '8px',
          border: '1px solid var(--border-color)',
          fontSize: '0.8rem',
          color: 'var(--primary-emerald)',
          fontWeight: '700'
        }}>
          {articles.length} Reports
        </div>
      </div>

      {/* Filter Bar */}
      <FilterBar filters={filters} setFilters={setFilters} />

      {/* Articles List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <Sparkles className="spin-icon" size={24} color="var(--primary-emerald)" />
          <p style={{ marginTop: '0.5rem' }}>Loading Tamil Nadu Wildlife Reports...</p>
        </div>
      ) : articles.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          <ShieldAlert size={36} color="var(--accent-amber)" style={{ margin: '0 auto 0.75rem' }} />
          <h3>No Wildlife Reports Found</h3>
          <p style={{ fontSize: '0.85rem', marginTop: '0.3rem' }}>Try clearing filters or search term to see more news.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {articles.map(art => (
            <ArticleCard
              key={art.id}
              article={art}
              lang={lang}
              onSelect={setSelectedArticle}
              onToggleBookmark={handleToggleBookmark}
            />
          ))}
        </div>
      )}

      {/* Article Inspection Modal */}
      {selectedArticle && (
        <ArticleModal
          article={selectedArticle}
          onClose={() => setSelectedArticle(null)}
          onToggleBookmark={handleToggleBookmark}
        />
      )}
    </div>
  );
}
