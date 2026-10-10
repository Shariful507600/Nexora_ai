// ============================================
// NEXORA AI - Sidebar Component
// ============================================
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, MessageSquare, FileText,
  Mic, Settings, LogOut, Zap,
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'

const navItems = [
  { to: '/',         icon: LayoutDashboard, label: 'Dashboard'       },
  { to: '/chat',     icon: MessageSquare,   label: 'AI Chat'         },
  { to: '/documents',icon: FileText,        label: 'Documents (RAG)' },
  { to: '/voice',    icon: Mic,             label: 'Voice Assistant' },
  { to: '/settings', icon: Settings,        label: 'Settings'        },
]

export default function Sidebar() {
  const { user, logout } = useAuthStore()

  return (
    <aside className="w-64 min-h-screen bg-nexora-surface border-r border-nexora-border flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-nexora-border">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-nexora-primary to-nexora-secondary flex items-center justify-center glow-primary">
            <Zap size={18} className="text-white" />
          </div>
          <div>
            <h1 className="font-bold text-lg gradient-text">NEXORA</h1>
            <p className="text-xs text-nexora-muted">AI Copilot</p>
          </div>
        </div>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'nav-link-active text-indigo-400'
                  : 'text-nexora-muted hover:text-nexora-text hover:bg-nexora-card'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User info + Logout */}
      <div className="p-4 border-t border-nexora-border">
        <div className="flex items-center gap-3 px-3 py-2 mb-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-nexora-primary to-nexora-secondary flex items-center justify-center text-white text-xs font-bold">
            {user?.full_name?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-nexora-text truncate">{user?.full_name}</p>
            <p className="text-xs text-nexora-muted truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm text-nexora-muted hover:text-red-400 hover:bg-red-400/10 transition-all duration-200"
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </aside>
  )
}
