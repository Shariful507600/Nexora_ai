// ============================================
// NEXORA AI - KPI Card Component
// ============================================
import { LucideIcon } from 'lucide-react'
import { motion } from 'framer-motion'

interface KPICardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: LucideIcon
  color?: 'primary' | 'secondary' | 'accent' | 'success' | 'warning'
  trend?: number
}

const colorMap = {
  primary:   { bg: 'from-indigo-500/20 to-purple-500/10',  icon: 'text-indigo-400',  border: 'border-indigo-500/20' },
  secondary: { bg: 'from-purple-500/20 to-pink-500/10',    icon: 'text-purple-400',  border: 'border-purple-500/20' },
  accent:    { bg: 'from-cyan-500/20 to-blue-500/10',      icon: 'text-cyan-400',    border: 'border-cyan-500/20'   },
  success:   { bg: 'from-emerald-500/20 to-green-500/10',  icon: 'text-emerald-400', border: 'border-emerald-500/20'},
  warning:   { bg: 'from-amber-500/20 to-yellow-500/10',   icon: 'text-amber-400',   border: 'border-amber-500/20'  },
}

export default function KPICard({ title, value, subtitle, icon: Icon, color = 'primary', trend }: KPICardProps) {
  const c = colorMap[color]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -3, transition: { duration: 0.2 } }}
      className={`glass-card p-5 bg-gradient-to-br ${c.bg} border ${c.border}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`w-10 h-10 rounded-xl bg-nexora-surface flex items-center justify-center ${c.icon}`}>
          <Icon size={20} />
        </div>
        {trend !== undefined && (
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
            trend >= 0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
          }`}>
            {trend >= 0 ? '+' : ''}{trend}%
          </span>
        )}
      </div>

      <div>
        <p className="text-2xl font-bold text-nexora-text mb-1">{value}</p>
        <p className="text-sm font-medium text-nexora-text/80">{title}</p>
        {subtitle && <p className="text-xs text-nexora-muted mt-0.5">{subtitle}</p>}
      </div>
    </motion.div>
  )
}
