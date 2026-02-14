import React, { useState, useEffect } from 'react'
import api from '../api/client'
import MinifigCard from '../components/MinifigCard'

export default function Results({ onError }) {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, complete, incomplete
  const [searchQuery, setSearchQuery] = useState('')
  const [minMatchPercentage, setMinMatchPercentage] = useState(0)
  const [themes, setThemes] = useState([])
  const [selectedTheme, setSelectedTheme] = useState('')

  useEffect(() => {
    fetchResults()
    fetchThemes()
  }, [])

  const fetchResults = async () => {
    setLoading(true)
    try {
      const response = await api.getResults()
      setResults(response.data)
    } catch (err) {
      onError(err.response?.data?.detail || 'Failed to load results')
      setResults(null)
    } finally {
      setLoading(false)
    }
  }

  const fetchThemes = async () => {
    try {
      const response = await api.getThemes()
      setThemes(response.data.themes || [])
    } catch (err) {
      // Silently fail for themes
    }
  }

  if (loading) {
    return (
      <div className="page">
        <h2>📊 Results</h2>
        <div className="loading">
          <div className="spinner"></div>
          <span>Loading results...</span>
        </div>
      </div>
    )
  }

  if (!results) {
    return (
      <div className="page">
        <h2>📊 Results</h2>
        <div className="alert alert-info">
          <span>ℹ️</span> No analysis results yet. <strong>Upload an inventory</strong> to get started!
        </div>
      </div>
    )
  }

  const getFilteredMinifigs = () => {
    let filtered = []

    if (filter === 'complete') {
      filtered = results.complete || []
    } else if (filter === 'incomplete') {
      filtered = results.incomplete || []
    } else {
      filtered = [...(results.complete || []), ...(results.incomplete || [])]
    }

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (m) =>
          m.minifig_id.toLowerCase().includes(query) ||
          m.minifig_name.toLowerCase().includes(query)
      )
    }

    // Apply theme filter
    if (selectedTheme) {
      filtered = filtered.filter(
        (m) => m.category_name.toLowerCase().includes(selectedTheme.toLowerCase())
      )
    }

    // Apply match percentage filter
    filtered = filtered.filter((m) => m.match_percentage >= minMatchPercentage)

    return filtered
  }

  const filteredMinifigs = getFilteredMinifigs()
  const summary = results.summary
  const completeMinifigs = results.complete || []

  return (
    <div className="page">
      <h2>📊 Analysis Results</h2>

      {/* Summary Stats */}
      <div className="stats-grid">
        <div className="stat-box">
          <div className="stat-box-value">{summary.total_checked}</div>
          <div className="stat-box-label">Total Checked</div>
        </div>
        <div className="stat-box">
          <div className="stat-box-value">{summary.complete_matches}</div>
          <div className="stat-box-label">Complete Matches ✅</div>
        </div>
        <div className="stat-box">
          <div className="stat-box-value">{summary.incomplete_matches}</div>
          <div className="stat-box-label">Incomplete Matches</div>
        </div>
        <div className="stat-box">
          <div className="stat-box-value">
            {summary.total_checked > 0 ? ((summary.complete_matches / summary.total_checked) * 100).toFixed(1) : 0}%
          </div>
          <div className="stat-box-label">Build Success Rate</div>
        </div>
      </div>

      {/* Filters */}
      <div style={{ marginTop: '30px', padding: '20px', background: '#f9f8ff', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '15px', color: '#667eea' }}>🔍 Filters</h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
          {/* Search */}
          <div className="form-group">
            <label>Search</label>
            <input
              type="text"
              placeholder="Minifig ID or name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* Match Percentage Filter */}
          <div className="form-group">
            <label>Min Match: {minMatchPercentage.toFixed(0)}%</label>
            <input
              type="range"
              min="0"
              max="100"
              step="10"
              value={minMatchPercentage}
              onChange={(e) => setMinMatchPercentage(parseFloat(e.target.value))}
            />
          </div>

          {/* Theme Filter */}
          {themes.length > 0 && (
            <div className="form-group">
              <label>Theme</label>
              <select
                value={selectedTheme}
                onChange={(e) => setSelectedTheme(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  fontFamily: 'inherit',
                }}
              >
                <option value="">All Themes</option>
                {themes.map((theme) => (
                  <option key={theme.prefix} value={theme.prefix}>
                    {theme.theme} ({theme.count})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Result Type Filter */}
          <div className="form-group">
            <label>Show</label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontFamily: 'inherit',
              }}
            >
              <option value="all">All Results ({filteredMinifigs.length})</option>
              <option value="complete">Complete Only ({completeMinifigs.length})</option>
              <option value="incomplete">Incomplete Only ({results.incomplete?.length || 0})</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results Grid */}
      <div style={{ marginTop: '30px' }}>
        <h3 style={{ marginBottom: '15px', color: '#333' }}>
          {filteredMinifigs.length} Result{filteredMinifigs.length !== 1 ? 's' : ''}
        </h3>

        {filteredMinifigs.length === 0 ? (
          <div className="alert alert-info">
            <span>ℹ️</span> No minifigures match your filters. Try adjusting your search criteria.
          </div>
        ) : (
          <div className="card-grid">
            {filteredMinifigs.map((minifig, idx) => (
              <MinifigCard
                key={idx}
                minifig={minifig}
                showMissing={filter !== 'complete'}
              />
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div style={{ marginTop: '30px', display: 'flex', gap: '10px' }}>
        <button className="btn btn-primary" onClick={fetchResults}>
          🔄 Refresh Results
        </button>
      </div>
    </div>
  )
}
