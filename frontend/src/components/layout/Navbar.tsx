// ============================================
// NEXORA AI - Navbar Component
// ============================================
import { Bell, Search } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'

interface NavbarProps {
  title: string
  subtitle?: string
}

export default function Navbar({ title, subtitle }: NavbarProps) {
  const { user } = useAuthStore()

  return (
    <header className="h-16 bg-nexora-surface/80 backdrop-blur-md border-b border-nexora-border flex items-center justify-between px-6 sticky top-0 z-10">
      <div>
        <h2 className="font-semibold text-nexora-text">{title}</h2>
        {subtitle && <p className="text-xs text-nexora-muted">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Search hint */}
        <div className="hidden md:flex items-center gap-2 bg-nexora-card border border-nexora-border rounded-lg px-3 py-1.5 text-sm text-nexora-muted">
          <Search size={14} />
          <span>Search...</span>
          <span className="ml-2 text-xs bg-nexora-border px-1.5 rounded">⌘K</span>
        </div>

        {/* Notification bell */}
        <button className="w-9 h-9 rounded-xl bg-nexora-card border border-nexora-border flex items-center justify-center text-nexora-muted hover:text-nexora-primary transition-colors">
          <Bell size={16} />
        </button>

        {/* Avatar */}
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-nexora-primary to-nexora-secondary flex items-center justify-center text-white text-sm font-bold">
          {user?.full_name?.[0]?.toUpperCase() || 'U'}
        </div>
      </div>
    </header>
  )
}
