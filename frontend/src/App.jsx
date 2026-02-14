import React, { useState, useEffect } from 'react'
import api from './api/client'
import Header from './components/Header'
import Upload from './pages/Upload'
import Results from './pages/Results'
import CacheManager from './pages/CacheManager'
import Settings from './pages/Settings'

export default function App() {
  const [currentPage, setCurrentPage] = useState('upload')
  const [isConfigured, setIsConfigured] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    checkConfiguration()
  }, [])

  const checkConfiguration = async () => {
    try {
      const response = await api.checkConfig()
      setIsConfigured(response.data.configured)
    } catch (err) {
      setIsConfigured(false)
    } finally {
      setLoading(false)
    }
  }

  const handleConfigUpdated = () => {
    checkConfiguration()
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <div className="spinner"></div>
      </div>
    )
  }

  if (!isConfigured) {
    return (
      <div>
        <Header currentPage={currentPage} setCurrentPage={setCurrentPage} />
        <div className="content">
          <div className="page">
            <h2>⚙️ Configuration Required</h2>
            <p style={{ marginBottom: '20px', color: '#666' }}>
              BrickLink API credentials are not configured. Please set them up first.
            </p>
            <Settings onConfigUpdated={handleConfigUpdated} />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <Header currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <div className="content">
        {error && (
          <div className="alert alert-error" onClick={() => setError(null)}>
            <span>❌</span> {error}
          </div>
        )}
        
        {currentPage === 'upload' && <Upload onError={setError} />}
        {currentPage === 'results' && <Results onError={setError} />}
        {currentPage === 'cache' && <CacheManager onError={setError} />}
        {currentPage === 'settings' && <Settings onConfigUpdated={handleConfigUpdated} />}
      </div>
    </div>
  )
}
