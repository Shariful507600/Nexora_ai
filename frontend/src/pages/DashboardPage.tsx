// ============================================
// NEXORA AI - Dashboard Page
// ============================================
import { useEffect, useState } from 'react'
import { MessageSquare, FileText, Zap, Activity, Clock, Database } from 'lucide-react'
import KPICard from '../components/dashboard/KPICard'
import { ActivityChart, AgentUsageChart } from '../components/dashboard/ActivityChart'
import Navbar from '../components/layout/Navbar'
import api from '../api/axios'
import { useAuthStore } from '../store/authStore'

interface DashboardData {
  kpis: {
    total_chats: number
    total_messages: number
    total_documents: number
    week_activity: number
    avg_response_ms: number
    total_chunks: number
  }
  charts: {
    daily_activity: { date: string; count: number }[]
    agent_usage: Record<string, number>
  }
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [aiStatus, setAiStatus] = useState<any>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashRes, statusRes] = await Promise.all([
          api.get('/api/analytics/dashboard'),
          api.get('/api/ai/status'),
        ])
        setData(dashRes.data)
        setAiStatus(statusRes.data)
      } catch (err) {
        console.error('Dashboard fetch error:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const kpis = data?.kpis

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <Navbar title="Dashboard" subtitle={`Welcome back, ${user?.full_name} 👋`} />

      <div className="flex-1 overflow-y-auto p-6 space-y-6">

        {/* AI Status Banner */}
        {aiStatus && (
          <div className={`glass-card px-5 py-3 flex items-center gap-3 border ${
            aiStatus.active_provider === 'ollama'
              ? 'border-emerald-500/30 bg-emerald-500/5'
              : aiStatus.active_provider === 'cloud'
              ? 'border-cyan-500/30 bg-cyan-500/5'
              : 'border-red-500/30 bg-red-500/5'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              aiStatus.active_provider !== 'none' ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'
            }`} />
            <span className="text-sm text-nexora-text">
              {aiStatus.active_provider === 'ollama'
                ? `🤖 Ollama running · Model: ${aiStatus.ollama?.current_model}`
                : aiStatus.active_provider === 'cloud'
                ? '☁️ Cloud AI active'
                : '⚠️ No AI provider · Run: ollama serve'}
            </span>
          </div>
        )}

        {/* KPI Cards */}
        {loading ? (
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="glass-card p-5 h-32 animate-pulse">
                <div className="w-10 h-10 bg-nexora-border rounded-xl mb-3" />
                <div className="h-6 bg-nexora-border rounded w-16 mb-2" />
                <div className="h-4 bg-nexora-border rounded w-24" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            <KPICard title="Total Chats"      value={kpis?.total_chats || 0}       icon={MessageSquare} color="primary"   trend={12} />
            <KPICard title="Total Messages"   value={kpis?.total_messages || 0}    icon={Zap}           color="secondary" trend={8}  />
            <KPICard title="Documents"        value={kpis?.total_documents || 0}   icon={FileText}      color="accent"               />
            <KPICard title="This Week"        value={kpis?.week_activity || 0}     icon={Activity}      color="success"  trend={25} />
            <KPICard title="Avg Response"     value={`${kpis?.avg_response_ms || 0}ms`} icon={Clock}   color="warning"              />
            <KPICard title="Knowledge Chunks" value={kpis?.total_chunks || 0}      icon={Database}      color="primary"              />
          </div>
        )}

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <ActivityChart
            data={data?.charts.daily_activity || []}
            title="📈 7-Day Activity"
          />
          <AgentUsageChart data={data?.charts.agent_usage || {}} />
        </div>

        {/* Quick Actions */}
        <div className="glass-card p-5">
          <h3 className="text-sm font-semibold text-nexora-text mb-4">⚡ Quick Actions</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label: 'New Chat',      emoji: '💬', href: '/chat'      },
              { label: 'Upload PDF',    emoji: '📄', href: '/documents' },
              { label: 'Voice Input',   emoji: '🎙️', href: '/voice'     },
              { label: 'Settings',      emoji: '⚙️', href: '/settings'  },
            ].map(({ label, emoji, href }) => (
              <a
                key={href}
                href={href}
                className="flex flex-col items-center gap-2 p-4 rounded-xl bg-nexora-card hover:bg-nexora-border border border-nexora-border hover:border-nexora-primary/40 transition-all duration-200 text-center"
              >
                <span className="text-2xl">{emoji}</span>
                <span className="text-xs font-medium text-nexora-muted">{label}</span>
              </a>
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}
