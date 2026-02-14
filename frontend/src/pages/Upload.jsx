import React, { useState, useRef } from 'react'
import api from '../api/client'

export default function Upload({ onError }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile.name.endsWith('.xml')) {
        setFile(droppedFile)
        setSuccess(false)
      } else {
        onError('Please drop an XML file')
      }
    }
  }

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setSuccess(false)
    }
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      onError('Please select a file first')
      return
    }

    setLoading(true)
    try {
      const response = await api.analyzeInventory(file)
      setSuccess(true)
      setFile(null)
      setLoading(false)
      // Analysis results are now available in the app state
      // User can navigate to Results page to see them
    } catch (err) {
      onError(err.response?.data?.detail || 'Analysis failed')
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h2>📤 Upload Your Inventory</h2>
      <p style={{ color: '#666', marginBottom: '30px' }}>
        Upload your BrickLink XML inventory file to find which minifigures you can build
      </p>

      {success && (
        <div className="alert alert-success">
          <span>✅</span> Analysis complete! Go to <strong>Results</strong> to see what you can build
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div
          className={`upload-area ${dragActive ? 'dragging' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={handleClick}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".xml"
            onChange={handleFileChange}
          />
          <p>📁 Drop your XML file here or click to browse</p>
          <small>Supported format: BrickLink inventory XML export files</small>

          {file && (
            <div style={{ marginTop: '15px', color: '#667eea', fontWeight: '600' }}>
              ✓ Selected: {file.name}
            </div>
          )}
        </div>

        <div style={{ marginTop: '20px' }}>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={!file || loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span> Analyzing...
              </>
            ) : (
              '🔍 Analyze Inventory'
            )}
          </button>
        </div>
      </form>

      <div style={{ marginTop: '40px', padding: '20px', background: '#f9f8ff', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '15px', color: '#667eea' }}>📋 How to Get Your Inventory File</h3>
        <ol style={{ color: '#666', lineHeight: '1.8' }}>
          <li>Go to <strong>BrickLink</strong> → Your Account → Inventory</li>
          <li>Select your desired inventory</li>
          <li>Click "<strong>Download</strong>" → Choose <strong>XML</strong> format</li>
          <li>Save the file and upload it here</li>
        </ol>
      </div>
    </div>
  )
}
