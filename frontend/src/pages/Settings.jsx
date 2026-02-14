import React, { useState } from 'react'
import api from '../api/client'

export default function Settings({ onConfigUpdated }) {
  const [formData, setFormData] = useState({
    consumer_key: '',
    consumer_secret: '',
    token: '',
    token_secret: '',
  })
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState(null)
  const [showSecrets, setShowSecrets] = useState({
    consumer_key: false,
    consumer_secret: false,
    token: false,
    token_secret: false,
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    setSuccess(false)
    setError(null)
  }

  const toggleShowSecret = (field) => {
    setShowSecrets((prev) => ({
      ...prev,
      [field]: !prev[field],
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(false)

    // Validate all fields are filled
    if (!formData.consumer_key || !formData.consumer_secret || !formData.token || !formData.token_secret) {
      setError('All fields are required')
      setLoading(false)
      return
    }

    try {
      await api.setConfig(formData)
      setSuccess(true)
      setFormData({
        consumer_key: '',
        consumer_secret: '',
        token: '',
        token_secret: '',
      })
      
      // Call callback to update parent component
      if (onConfigUpdated) {
        setTimeout(onConfigUpdated, 1000)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Configuration failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  const fields = [
    {
      name: 'consumer_key',
      label: 'Consumer Key',
      placeholder: 'Your BrickLink API Consumer Key',
    },
    {
      name: 'consumer_secret',
      label: 'Consumer Secret',
      placeholder: 'Your BrickLink API Consumer Secret',
    },
    {
      name: 'token',
      label: 'Access Token',
      placeholder: 'Your BrickLink API Access Token',
    },
    {
      name: 'token_secret',
      label: 'Token Secret',
      placeholder: 'Your BrickLink API Token Secret',
    },
  ]

  return (
    <div className="page">
      <h2>⚙️ Settings</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        Configure your BrickLink API credentials to enable minifigure fetching
      </p>

      {success && (
        <div className="alert alert-success">
          <span>✅</span> Configuration saved successfully! Your credentials are secure.
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          <span>❌</span> {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ maxWidth: '500px' }}>
          {fields.map((field) => (
            <div key={field.name} className="form-group">
              <label>{field.label}</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showSecrets[field.name] ? 'text' : 'password'}
                  name={field.name}
                  placeholder={field.placeholder}
                  value={formData[field.name]}
                  onChange={handleChange}
                  required
                />
                <button
                  type="button"
                  onClick={() => toggleShowSecret(field.name)}
                  style={{
                    position: 'absolute',
                    right: '10px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    fontSize: '16px',
                    color: '#667eea',
                  }}
                >
                  {showSecrets[field.name] ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: '20px' }}>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span> Saving...
              </>
            ) : (
              '💾 Save Configuration'
            )}
          </button>
        </div>
      </form>

      {/* Instructions */}
      <div style={{ marginTop: '40px', padding: '20px', background: '#f0f8ff', borderRadius: '8px', borderLeft: '4px solid #667eea' }}>
        <h3 style={{ marginBottom: '15px', color: '#667eea' }}>📚 How to Get Your API Credentials</h3>
        <ol style={{ color: '#666', lineHeight: '1.8', paddingLeft: '20px' }}>
          <li>
            Visit <a href="https://www.bricklink.com/v2/api/register_consumer.page" target="_blank" rel="noopener noreferrer" style={{ color: '#667eea', textDecoration: 'none' }}>
              BrickLink API Registration
            </a>
          </li>
          <li>Create a new consumer application</li>
          <li>Generate API credentials (will give you Consumer Key & Secret)</li>
          <li>Request OAuth authorization and get your Access Token & Token Secret</li>
          <li>Copy all four values into this form</li>
        </ol>
      </div>

      <div style={{ marginTop: '20px', padding: '20px', background: '#fffaf0', borderRadius: '8px', borderLeft: '4px solid #ff9800' }}>
        <h3 style={{ marginBottom: '10px', color: '#ff9800' }}>🔒 Security Note</h3>
        <p style={{ color: '#666', fontSize: '14px' }}>
          Your API credentials are stored securely on the server and never sent to your browser. They are only used to fetch data from BrickLink API.
        </p>
      </div>
    </div>
  )
}
