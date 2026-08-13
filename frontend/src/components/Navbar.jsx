import React from 'react';
import { ShieldAlert, RefreshCw, Bookmark, FileText, Globe, Sun, Moon } from 'lucide-react';

export default function Navbar({ lang, setLang, theme, toggleTheme, activeTab, setActiveTab, bookmarkedOnly, setBookmarkedOnly, onRefresh, isRefreshing }) {
  return (
    <header style={{
      background: 'var(--navbar-bg)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border-color)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      transition: 'background 0.3s ease'
    }}>
      <div style={{
        maxWidth: '1440px',
        margin: '0 auto',
        padding: '0.8rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        {/* Brand Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', cursor: 'pointer' }} onClick={() => setActiveTab('feed')}>
          <div style={{
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            padding: '0.5rem',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 12px var(--primary-glow)'
          }}>
            <ShieldAlert size={24} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ fontSize: '1.25rem', fontWeight: '800', letterSpacing: '-0.02em', color: 'var(--heading-color)' }}>WildTN</span>
              <span style={{ fontSize: '1.25rem', fontWeight: '700', color: 'var(--primary-emerald)' }}>News</span>
              <span style={{
                fontSize: '0.65rem',
                fontWeight: '700',
                background: 'rgba(245, 158, 11, 0.2)',
                color: 'var(--accent-amber)',
                padding: '2px 6px',
                borderRadius: '4px',
                border: '1px solid rgba(245, 158, 11, 0.4)'
              }}>TAMIL NADU</span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Wildlife & Conservation Intelligence Platform</p>
          </div>
        </div>

        {/* Right Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          {/* Theme Toggle Button */}
          <button 
            className="theme-btn"
            onClick={toggleTheme}
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme === 'dark' ? (
              <>
                <Sun size={16} color="#f59e0b" />
                <span>Light</span>
              </>
            ) : (
              <>
                <Moon size={16} color="#3b82f6" />
                <span>Dark</span>
              </>
            )}
          </button>

          {/* Language Switcher */}
          <div className="lang-toggle">
            <button 
              className={`lang-btn ${lang === 'en' ? 'active' : ''}`}
              onClick={() => setLang('en')}
            >
              English
            </button>
            <button 
              className={`lang-btn ${lang === 'ta' ? 'active' : ''}`}
              onClick={() => setLang('ta')}
            >
              தமிழ்
            </button>
          </div>

          {/* Bookmark Toggle */}
          <button 
            className={`btn ${bookmarkedOnly ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setBookmarkedOnly(!bookmarkedOnly)}
            title="Bookmarked news"
          >
            <Bookmark size={16} fill={bookmarkedOnly ? "#fff" : "none"} />
            <span style={{ fontSize: '0.85rem' }}>Saved</span>
          </button>

          {/* Trigger Scraping */}
          <button 
            className="btn btn-secondary"
            onClick={onRefresh}
            disabled={isRefreshing}
            style={{ opacity: isRefreshing ? 0.7 : 1 }}
          >
            <RefreshCw size={16} className={isRefreshing ? "spin-icon" : ""} />
            <span style={{ fontSize: '0.85rem' }}>{isRefreshing ? 'Scanning...' : 'Scan Feeds'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
