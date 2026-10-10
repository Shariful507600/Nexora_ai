// ============================================
// NEXORA AI - Main App Component
// ============================================
import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from './store/authStore'

// Layout
import Sidebar from './components/layout/Sidebar'

// Pages
import LoginPage          from './pages/LoginPage'
import DashboardPage      from './pages/DashboardPage'
import AIChatPage         from './pages/AIChatPage'
import DocumentsPage      from './pages/DocumentsPage'
import VoiceAssistantPage from './pages/VoiceAssistantPage'
import SettingsPage       from './pages/SettingsPage'

// Protected layout wrapper
function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-nexora-bg">
      <Sidebar />
      <main className="flex-1 flex flex-col min-h-screen min-w-0">
        {children}
      </main>
    </div>
  )
}

// Protected route guard
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore()
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  const { loadFromStorage } = useAuthStore()

  // Load saved auth from localStorage on startup
  useEffect(() => {
    loadFromStorage()
  }, [])

  return (
    <BrowserRouter>
      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1a1a2e',
            color: '#e2e8f0',
            border: '1px solid #2a2a4a',
            borderRadius: '12px',
            fontSize: '13px',
          },
          success: { iconTheme: { primary: '#10b981', secondary: '#fff' } },
          error:   { iconTheme: { primary: '#ef4444', secondary: '#fff' } },
        }}
      />

      <Routes>
        {/* Public */}
        <Route path="/login" element={<LoginPage />} />

        {/* Protected routes with sidebar layout */}
        <Route path="/" element={
          <ProtectedRoute>
            <AppLayout><DashboardPage /></AppLayout>
          </ProtectedRoute>
        } />
        <Route path="/chat" element={
          <ProtectedRoute>
            <AppLayout><AIChatPage /></AppLayout>
          </ProtectedRoute>
        } />
        <Route path="/documents" element={
          <ProtectedRoute>
            <AppLayout><DocumentsPage /></AppLayout>
          </ProtectedRoute>
        } />
        <Route path="/voice" element={
          <ProtectedRoute>
            <AppLayout><VoiceAssistantPage /></AppLayout>
          </ProtectedRoute>
        } />
        <Route path="/settings" element={
          <ProtectedRoute>
            <AppLayout><SettingsPage /></AppLayout>
          </ProtectedRoute>
        } />

        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
