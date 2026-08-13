import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import NewsFeed from './pages/NewsFeed';
import PDFDigest from './pages/PDFDigest';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import CollectorJobs from './pages/CollectorJobs';
import { fetchAnalytics, triggerCollectors } from './services/api';

import TamilNaduMap from './components/TamilNaduMap';

export default function App() {
  const [activeTab, setActiveTab] = useState('feed');
  const [selectedDistrictFilter, setSelectedDistrictFilter] = useState('All');
  const [lang, setLang] = useState('en');
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('wildtn_theme') || 'dark';
  });
  const [bookmarkedOnly, setBookmarkedOnly] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('wildtn_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  const loadAnalyticsData = async () => {
    try {
      const data = await fetchAnalytics();
      setAnalytics(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const handleManualScan = async () => {
    setIsRefreshing(true);
    try {
      await triggerCollectors();
      await loadAnalyticsData();
      setRefreshTrigger(prev => prev + 1);
    } catch (e) {
      console.error(e);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleSelectMapDistrict = (districtName) => {
    setSelectedDistrictFilter(districtName);
    setActiveTab('feed');
  };

  return (
    <div className="app-container">
      <Navbar
        lang={lang}
        setLang={setLang}
        theme={theme}
        toggleTheme={toggleTheme}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        bookmarkedOnly={bookmarkedOnly}
        setBookmarkedOnly={setBookmarkedOnly}
        onRefresh={handleManualScan}
        isRefreshing={isRefreshing}
      />

      <main className="app-main">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          analytics={analytics}
        />

        <section className="main-content">
          {activeTab === 'feed' && (
            <NewsFeed
              lang={lang}
              bookmarkedOnly={bookmarkedOnly}
              onArticlesUpdated={loadAnalyticsData}
              refreshTrigger={refreshTrigger}
              initialDistrict={selectedDistrictFilter}
            />
          )}

          {activeTab === 'map' && (
            <TamilNaduMap
              onSelectDistrict={handleSelectMapDistrict}
              selectedDistrict={selectedDistrictFilter}
            />
          )}

          {activeTab === 'pdf' && <PDFDigest />}

          {activeTab === 'analytics' && (
            <AnalyticsDashboard onSelectDistrict={handleSelectMapDistrict} />
          )}

          {activeTab === 'collectors' && (
            <CollectorJobs onScanComplete={loadAnalyticsData} />
          )}
        </section>
      </main>
    </div>
  );
}

