import React from 'react'

export default function Header({ currentPage, setCurrentPage }) {
  const pages = [
    { id: 'upload', label: '📤 Upload' },
    { id: 'results', label: '📊 Results' },
    { id: 'cache', label: '💾 Cache' },
    { id: 'settings', label: '⚙️ Settings' },
  ]

  return (
    <div className="header">
      <div className="header-content">
        <h1>🧱 Minifig Builder</h1>
        <div className="nav-tabs">
          {pages.map((page) => (
            <button
              key={page.id}
              className={currentPage === page.id ? 'active' : ''}
              onClick={() => setCurrentPage(page.id)}
            >
              {page.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
