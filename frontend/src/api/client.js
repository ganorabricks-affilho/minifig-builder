import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const api = {
  // Analysis endpoints
  analyzeInventory: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/api/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  getResults: () => client.get('/api/results'),

  // Cache endpoints
  getCacheStatus: () => client.get('/api/cache/status'),
  getCachedMinifigs: () => client.get('/api/cache/minifigs'),

  // Search endpoints
  searchMinifigs: (query, theme) =>
    client.get('/api/search', {
      params: { q: query, theme },
    }),
  getThemes: () => client.get('/api/themes'),

  // Stats endpoints
  getStats: () => client.get('/api/stats'),

  // Health check
  healthCheck: () => client.get('/health'),
}

export default api
