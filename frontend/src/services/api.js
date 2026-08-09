const rawBase = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');
const API_BASE = rawBase.endsWith('/api') ? rawBase : `${rawBase}/api`;

export async function fetchArticles(params = {}) {
  const query = new URLSearchParams();
  if (params.category && params.category !== 'All') query.append('category', params.category);
  if (params.district && params.district !== 'All') query.append('district', params.district);
  if (params.conflictLevel && params.conflictLevel !== 'All') query.append('conflict_level', params.conflictLevel);
  if (params.species && params.species !== 'All') query.append('species', params.species);
  if (params.search) query.append('search', params.search);
  if (params.bookmarkedOnly) query.append('bookmarked_only', 'true');

  const res = await fetch(`${API_BASE}/articles?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch articles');
  return res.json();
}

export async function fetchArticle(id) {
  const res = await fetch(`${API_BASE}/articles/${id}`);
  if (!res.ok) throw new Error('Failed to fetch article');
  return res.json();
}

export async function toggleBookmark(id) {
  const res = await fetch(`${API_BASE}/articles/bookmark/${id}`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to toggle bookmark');
  return res.json();
}

export async function fetchAnalytics() {
  const res = await fetch(`${API_BASE}/analytics`);
  if (!res.ok) throw new Error('Failed to fetch analytics');
  return res.json();
}

export async function fetchReports() {
  const res = await fetch(`${API_BASE}/pdf/reports`);
  if (!res.ok) throw new Error('Failed to fetch PDF reports');
  return res.json();
}

export async function generatePDFReport(data) {
  const res = await fetch(`${API_BASE}/pdf/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to generate PDF report');
  return res.json();
}

export async function fetchCollectorLogs() {
  const res = await fetch(`${API_BASE}/collectors/logs`);
  if (!res.ok) throw new Error('Failed to fetch logs');
  return res.json();
}

export async function triggerCollectors() {
  const res = await fetch(`${API_BASE}/collectors/trigger`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to trigger collectors');
  return res.json();
}

export function getShiftTriggerUrl(shiftId) {
  return `${API_BASE}/pdf/trigger-shift/${shiftId}`;
}

export async function fetchPdfSchedule() {
  const res = await fetch(`${API_BASE}/pdf/schedule`);
  if (!res.ok) throw new Error('Failed to fetch PDF schedule');
  return res.json();
}

export async function clearReportsHistory() {
  const res = await fetch(`${API_BASE}/pdf/clear-history`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to clear PDF history');
  return res.json();
}

