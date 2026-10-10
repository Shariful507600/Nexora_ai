// ============================================
// NEXORA AI - Axios API Client
// ============================================
// Centralized HTTP client। সব API call এখান দিয়ে যায়।
// JWT token automatically header এ যোগ হয়।

import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor - JWT token inject করে
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('nexora_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response interceptor - 401 হলে logout করে
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('nexora_token')
      localStorage.removeItem('nexora_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
