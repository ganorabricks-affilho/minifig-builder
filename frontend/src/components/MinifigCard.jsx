import React, { useState } from 'react'

export default function MinifigCard({ minifig, showMissing = false }) {
  const [showDetails, setShowDetails] = useState(false)

  const getStatusIcon = () => {
    if (minifig.can_build) return '✅'
    const percentage = minifig.match_percentage
    if (percentage >= 75) return '⚠️'
    if (percentage >= 50) return '🟡'
    return '🔴'
  }

  const getTotalPartsValue = () => {
    if (!minifig.all_parts || minifig.all_parts.length === 0) return 0
    return minifig.all_parts.reduce((sum, part) => sum + (part.total_price || 0), 0)
  }

  const formatPrice = (price) => {
    if (!price) return '$0.00'
    return `$${price.toFixed(2)}`
  }

  return (
    <div className="card">
      <div style={{ marginBottom: '15px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <div>
            <h3>{minifig.minifig_id}</h3>
            <p style={{ fontSize: '14px', color: '#666' }}>{minifig.minifig_name}</p>
          </div>
          <div style={{ fontSize: '24px' }}>{getStatusIcon()}</div>
        </div>
      </div>

      <div style={{ marginBottom: '15px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ color: '#666' }}>Category:</span>
          <span style={{ fontWeight: '600' }}>{minifig.category_name}</span>
        </div>
        {minifig.year_released && (
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ color: '#666' }}>Year:</span>
            <span>{minifig.year_released}</span>
          </div>
        )}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ color: '#666' }}>Parts:</span>
          <span>
            {minifig.matched_parts}/{minifig.total_parts}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#666' }}>Match:</span>
          <span style={{ fontWeight: '700', color: '#667eea' }}>
            {minifig.match_percentage.toFixed(1)}%
          </span>
        </div>
      </div>

      {minifig.prices_6month_average && (
        <div style={{
          padding: '10px',
          background: '#f9f8ff',
          borderRadius: '6px',
          marginBottom: '15px',
          fontSize: '13px',
        }}>
          💰 Market Value (6-Month Avg):
          {minifig.prices_6month_average.new_condition && (
            <div>New: {formatPrice(minifig.prices_6month_average.new_condition)}</div>
          )}
          {minifig.prices_6month_average.used_condition && (
            <div>Used: {formatPrice(minifig.prices_6month_average.used_condition)}</div>
          )}
          {getTotalPartsValue() > 0 && (
            <div style={{ marginTop: '5px', color: '#667eea', fontWeight: '600' }}>
              Parts Cost: {formatPrice(getTotalPartsValue())}
            </div>
          )}
        </div>
      )}

      <button
        className="btn btn-secondary"
        onClick={() => setShowDetails(!showDetails)}
        style={{ width: '100%' }}
      >
        {showDetails ? '▼ Hide Details' : '▶ Show Details'}
      </button>

      {showDetails && (
        <div style={{ marginTop: '15px', borderTop: '1px solid #eee', paddingTop: '15px' }}>
          {minifig.all_parts && minifig.all_parts.length > 0 && (
            <div style={{ marginBottom: '15px' }}>
              <h4 style={{ marginBottom: '10px', color: '#333' }}>Matched Parts ({minifig.matched_parts}):</h4>
              <div style={{ fontSize: '12px', maxHeight: '200px', overflowY: 'auto' }}>
                {minifig.all_parts.map((part, idx) => (
                  <div key={idx} style={{ marginBottom: '8px', padding: '8px', background: '#f9f9f9', borderRadius: '4px' }}>
                    <div style={{ fontWeight: '600' }}>{part.part_id}</div>
                    <div style={{ color: '#666' }}>{part.part_name}</div>
                    <div style={{ color: '#999', fontSize: '11px' }}>
                      Color: {part.color_name} | Qty: {part.quantity} | Price: {formatPrice(part.price)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {showMissing && minifig.missing_details && minifig.missing_details.length > 0 && (
            <div>
              <h4 style={{ marginBottom: '10px', color: '#d32f2f' }}>Missing Parts ({minifig.missing_parts}):</h4>
              <div style={{ fontSize: '12px', maxHeight: '200px', overflowY: 'auto' }}>
                {minifig.missing_details.map((part, idx) => (
                  <div key={idx} style={{ marginBottom: '8px', padding: '8px', background: '#ffebee', borderRadius: '4px' }}>
                    <div style={{ fontWeight: '600' }}>{part.part_id}</div>
                    <div style={{ color: '#666' }}>{part.part_name}</div>
                    <div style={{ color: '#999', fontSize: '11px' }}>
                      Need: {part.needed} | Have: {part.available} | Short: {part.short_by}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
