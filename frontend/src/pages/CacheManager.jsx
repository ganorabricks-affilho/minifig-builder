import React, { useState, useEffect } from 'react'
import api from '../api/client'

export default function CacheManager({ onError }) {
  const [cacheStatus, setCacheStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    fetchCacheStatus()
    fetchStats()
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

  const handleUpdatePrices = async () => {
    setUpdating(true)
    try {
      const response = await api.updatePrices()
      await new Promise((resolve) => setTimeout(resolve, 2000)) // Wait 2 seconds
      await fetchCacheStatus()
      await fetchStats()
    } catch (err) {
      onError(err.response?.data?.detail || 'Failed to update prices')
    } finally {
      setUpdating(false)
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

      {/* Cache Details */}
      <div style={{ marginTop: '30px', padding: '20px', background: '#f9f8ff', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '15px', color: '#667eea' }}>📂 Cache Details</h3>
        <div style={{ fontSize: '14px', color: '#666', lineHeight: '1.8' }}>
          <div>
            <strong>Minifigure Cache File:</strong>
            <br />
            <code style={{ background: '#fff', padding: '8px', borderRadius: '4px', display: 'block', marginTop: '5px', fontSize: '12px', overflow: 'auto' }}>
              {cacheStatus.minifig_cache_file}
            </code>
          </div>
          <div style={{ marginTop: '15px' }}>
            <strong>Price Cache File:</strong>
            <br />
            <code style={{ background: '#fff', padding: '8px', borderRadius: '4px', display: 'block', marginTop: '5px', fontSize: '12px', overflow: 'auto' }}>
              {cacheStatus.price_cache_file}
            </code>
          </div>
        </div>
      </div>

      {/* Price Update Section */}
      <div style={{ marginTop: '30px', padding: '20px', background: '#fffaf0', borderRadius: '8px', borderLeft: '4px solid #ff9800' }}>
        <h3 style={{ marginBottom: '15px', color: '#ff9800' }}>💰 Update Prices</h3>
        <p style={{ color: '#666', marginBottom: '15px' }}>
          Update the cached prices for all minifigures. This will fetch fresh data from BrickLink API.
        </p>
        <button
          className="btn btn-primary"
          onClick={handleUpdatePrices}
          disabled={updating || cacheStatus.minifig_count === 0}
        >
          {updating ? (
            <>
              <span className="spinner"></span> Updating Prices...
            </>
          ) : (
            '📊 Update All Prices'
          )}
        </button>
        {cacheStatus.minifig_count === 0 && (
          <p style={{ color: '#ff9800', fontSize: '12px', marginTop: '10px' }}>
            ⚠️ No minifigures in cache. Run cache_valuable_minifigs.py first.
          </p>
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

      {/* Help Section */}
      <div style={{ marginTop: '30px', padding: '20px', background: '#f9f9f9', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '15px', color: '#333' }}>❓ How to Populate Cache</h3>
        <p style={{ color: '#666', marginBottom: '10px' }}>
          To build the cache of minifigures, run the Python cache script from your terminal:
        </p>
        <code
          style={{
            background: '#fff',
            padding: '12px',
            borderRadius: '4px',
            display: 'block',
            fontSize: '13px',
            overflow: 'auto',
            margin: '10px 0',
          }}
        >
          python3 src/cache_valuable_minifigs.py --theme sw --min-price 2.0
        </code>
        <p style={{ color: '#666', fontSize: '13px', marginTop: '10px' }}>
          <strong>Parameters:</strong>
          <br />
          • <code>--theme</code>: Theme prefix (sw, sh, hp, cas, etc.)
          <br />
          • <code>--min-price</code>: Minimum price threshold (default: 2.0)
          <br />
          • Multiple themes: <code>--theme sw sh hp</code>
        </p>
      </div>
    </div>
  )
}
