import React, { useState, useEffect } from 'react'
import api from '../api/client'

export default function CacheManager({ onError }) {
  const [cacheStatus, setCacheStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState(null)
  const [cachedMinifigs, setCachedMinifigs] = useState([])
  const [minifigLoading, setMinifigLoading] = useState(true)
  const [expandedCategories, setExpandedCategories] = useState({})

  const toggleCategory = (categoryName) => {
    setExpandedCategories((prev) => ({
      ...prev,
      [categoryName]: !prev[categoryName],
    }))
  }

  useEffect(() => {
    fetchCacheStatus()
    fetchStats()
    fetchCachedMinifigs()
  }, [])

  const fetchCacheStatus = async () => {
    setLoading(true)
    try {
      const response = await api.getCacheStatus()
      setCacheStatus(response.data)
    } catch (err) {
      onError(err.response?.data?.detail || 'Failed to load cache status')
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await api.getStats()
      setStats(response.data)
    } catch (err) {
      // Silently fail
    }
  }

  const fetchCachedMinifigs = async () => {
    setMinifigLoading(true)
    try {
      const response = await api.getCachedMinifigs()
      setCachedMinifigs(response.data.categories || [])
    } catch (err) {
      onError(err.response?.data?.detail || 'Failed to load cached minifigures')
    } finally {
      setMinifigLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="page">
        <h2>💾 Cache Manager</h2>
        <div className="loading">
          <div className="spinner"></div>
          <span>Loading cache status...</span>
        </div>
      </div>
    )
  }

  if (!cacheStatus) {
    return (
      <div className="page">
        <h2>💾 Cache Manager</h2>
        <div className="alert alert-error">
          <span>❌</span> Failed to load cache status
        </div>
      </div>
    )
  }

  return (
    <div className="page">
      <h2>💾 Cache Manager</h2>
      <p style={{ color: '#666', marginBottom: '30px' }}>
        Manage your cached minifigure data and price information
      </p>

      {/* Cache Status */}
      <div className="stats-grid">
        <div className="stat-box">
          <div className="stat-box-value">{cacheStatus.minifig_count}</div>
          <div className="stat-box-label">Cached Minifigures</div>
        </div>
        <div className="stat-box">
          <div className="stat-box-value">{cacheStatus.price_count}</div>
          <div className="stat-box-label">Cached Prices</div>
        </div>
        {stats?.cache && (
          <>
            <div className="stat-box">
              <div className="stat-box-value">{stats.cache.minifig_count}</div>
              <div className="stat-box-label">Total Minifigures</div>
            </div>
            <div className="stat-box">
              <div className="stat-box-value">
                {stats.cache.minifig_count > 0
                  ? ((stats.cache.price_count / stats.cache.minifig_count) * 100).toFixed(0)
                  : 0}
                %
              </div>
              <div className="stat-box-label">Prices Cached</div>
            </div>
          </>
        )}
      </div>

      {/* Cache Statistics */}
      {stats?.latest_analysis && (
        <div style={{ marginTop: '30px', padding: '20px', background: '#f0f8ff', borderRadius: '8px', borderLeft: '4px solid #667eea' }}>
          <h3 style={{ marginBottom: '15px', color: '#667eea' }}>📊 Latest Analysis</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px' }}>
            <div>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#667eea' }}>
                {stats.latest_analysis.total_checked}
              </div>
              <div style={{ color: '#666', fontSize: '13px' }}>Minifigures Checked</div>
            </div>
            <div>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#2ecc71' }}>
                {stats.latest_analysis.complete_matches}
              </div>
              <div style={{ color: '#666', fontSize: '13px' }}>Can Build</div>
            </div>
            <div>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#ff9800' }}>
                {stats.latest_analysis.incomplete_matches}
              </div>
              <div style={{ color: '#666', fontSize: '13px' }}>Partial Matches</div>
            </div>
          </div>
        </div>
      )}

      {/* Cached Minifigures */}
      <div style={{ marginTop: '30px', padding: '20px', background: '#f7f7fb', borderRadius: '8px', borderLeft: '4px solid #4b6cb7' }}>
        <h3 style={{ marginBottom: '15px', color: '#4b6cb7' }}>🧾 Cached Minifigures</h3>
        <p style={{ color: '#666', marginBottom: '15px' }}>
          ID and name grouped by category.
        </p>
        {minifigLoading ? (
          <div className="loading" style={{ padding: 0 }}>
            <div className="spinner"></div>
            <span>Loading cached minifigures...</span>
          </div>
        ) : cachedMinifigs.length === 0 ? (
          <div className="alert alert-info">
            <span>ℹ️</span> No cached minifigures found.
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '16px' }}>
            {cachedMinifigs.map((group) => (
              <div key={group.category} style={{ background: '#ffffff', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                <div
                  onClick={() => toggleCategory(group.category)}
                  style={{
                    fontWeight: 700,
                    padding: '12px 14px',
                    color: '#333',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    backgroundColor: '#f0f0f5',
                    borderRadius: '8px 8px 0 0',
                  }}
                >
                  <span>{group.category} ({group.items.length})</span>
                  <span style={{ fontSize: '18px' }}>{expandedCategories[group.category] ? '▼' : '▶'}</span>
                </div>
                {expandedCategories[group.category] && (
                  <div style={{ display: 'grid', gap: '6px', padding: '12px 14px' }}>
                    {group.items.map((item) => (
                      <div key={item.id} style={{ display: 'flex', gap: '10px', alignItems: 'baseline' }}>
                        <a
                          href={`https://www.bricklink.com/v2/catalog/catalogitem.page?M=${item.id.toUpperCase()}#T=P`}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            fontFamily: 'monospace',
                            color: '#4b6cb7',
                            minWidth: '70px',
                            textDecoration: 'none',
                            fontWeight: '500',
                          }}
                        >
                          {item.id}
                        </a>
                        <div style={{ color: '#333' }}>{item.name || 'Unknown'}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  )
}
