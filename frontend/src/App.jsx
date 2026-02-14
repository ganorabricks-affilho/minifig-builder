import React, { useState } from 'react'
import Header from './components/Header'
import Upload from './pages/Upload'
import Results from './pages/Results'
import CacheManager from './pages/CacheManager'

export default function App() {
  const [currentPage, setCurrentPage] = useState('upload')
  const [error, setError] = useState(null)

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
      </div>
    </div>
  )
}
