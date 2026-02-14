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

  const getMarketValueUsed = () => {
    return minifig.prices_6month_average?.used_condition || 0
  }

  const getProfit = () => {
    const marketValue = getMarketValueUsed()
    const partsCost = getTotalPartsValue()
    return marketValue - partsCost
  }

  const getProfitColor = () => {
    const profit = getProfit()
    if (profit > 0) return '#2ecc71' // green
    if (profit < 0) return '#e74c3c' // red
    return '#95a5a6' // gray
  }

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ marginBottom: '15px' }}>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'flex-start' }}>
          {minifig.thumbnail_url && (
            <div style={{ flexShrink: 0 }}>
              <img
                src={`https:${minifig.thumbnail_url}`}
                alt={minifig.minifig_id}
                style={{
                  width: '80px',
                  height: '80px',
                  objectFit: 'contain',
                  background: '#f5f5f5',
                  borderRadius: '6px',
                  border: '1px solid #e0e0e0',
                }}
              />
            </div>
          )}
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '4px' }}>
              <h3 style={{ margin: 0 }}>{minifig.minifig_id}</h3>
              <div style={{ fontSize: '24px' }}>{getStatusIcon()}</div>
            </div>
            <p
              style={{
                fontSize: '14px',
                color: '#666',
                margin: 0,
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                cursor: 'help',
              }}
              title={minifig.minifig_name}
            >
              {minifig.minifig_name}
            </p>
          </div>
        </div>
      </div>

      {minifig.prices_6month_average && getTotalPartsValue() >= 0 && (
        <div style={{
          padding: '12px 14px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '6px',
          marginBottom: '15px',
          color: 'white',
          fontSize: '14px',
        }}>
          <div style={{ marginBottom: '8px', fontWeight: '700', fontSize: '16px' }}>💰 Financial Analysis</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span>Market Value (Used):</span>
            <span style={{ fontWeight: '700' }}>{formatPrice(getMarketValueUsed())}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span>Parts listing price:</span>
            <span style={{ fontWeight: '700' }}>{formatPrice(getTotalPartsValue())}</span>
          </div>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            paddingTop: '8px',
            borderTop: '1px solid rgba(255,255,255,0.3)',
            fontWeight: '700',
            fontSize: '15px',
            color: getProfitColor(),
          }}>
            <span>Potential {getProfit() > 0 ? 'Profit' : 'Loss'}:</span>
            <span>{formatPrice(Math.abs(getProfit()))}</span>
          </div>
        </div>
      )}

      <div style={{ marginBottom: '15px', flex: 1 }}>
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

      <button
        className="btn btn-secondary"
        onClick={() => setShowDetails(!showDetails)}
        style={{ width: '100%', marginTop: 'auto' }}
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
