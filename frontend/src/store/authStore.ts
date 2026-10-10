// ============================================
// NEXORA AI - Auth Store (Zustand)
// ============================================
import { create } from 'zustand'
import api from '../api/axios'

interface User {
  id: number
  full_name: string
  email: string
}

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
  loadFromStorage: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: false,

  loadFromStorage: () => {
    const token = localStorage.getItem('nexora_token')
    const user = localStorage.getItem('nexora_user')
    if (token && user) {
      set({ token, user: JSON.parse(user) })
    }
  },

  login: async (email, password) => {
    set({ isLoading: true })
    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)
      const res = await api.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      const { access_token, user_id, full_name } = res.data
      const user = { id: user_id, full_name, email }
      localStorage.setItem('nexora_token', access_token)
      localStorage.setItem('nexora_user', JSON.stringify(user))
      set({ token: access_token, user, isLoading: false })
    } catch (err) {
      set({ isLoading: false })
      throw err
    }
  },

  register: async (full_name, email, password) => {
    set({ isLoading: true })
    try {
      await api.post('/api/auth/register', { full_name, email, password })
      set({ isLoading: false })
    } catch (err) {
      set({ isLoading: false })
      throw err
    }
  },

  logout: () => {
    localStorage.removeItem('nexora_token')
    localStorage.removeItem('nexora_user')
    set({ user: null, token: null })
    window.location.href = '/login'
  },
}))
