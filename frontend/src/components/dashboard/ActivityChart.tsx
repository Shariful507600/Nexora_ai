// ============================================
// NEXORA AI - Activity Chart Component
// ============================================
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, BarChart, Bar, Cell, PieChart, Pie, Legend,
} from 'recharts'

interface ActivityChartProps {
  data: { date: string; count: number }[]
  title: string
}

// Custom tooltip
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload?.length) {
    return (
      <div className="glass-card px-3 py-2 text-xs">
        <p className="text-nexora-muted">{label}</p>
        <p className="text-indigo-400 font-semibold">{payload[0].value} interactions</p>
      </div>
    )
  }
  return null
}

export function ActivityChart({ data, title }: ActivityChartProps) {
  return (
    <div className="glass-card p-5">
      <h3 className="text-sm font-semibold text-nexora-text mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0}   />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
          <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Area type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} fill="url(#colorCount)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

// Agent usage bar chart
interface AgentChartProps {
  data: Record<string, number>
}

const AGENT_COLORS = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981']

export function AgentUsageChart({ data }: AgentChartProps) {
  const chartData = Object.entries(data).map(([name, value]) => ({ name, value }))

  if (!chartData.length) return (
    <div className="glass-card p-5">
      <h3 className="text-sm font-semibold text-nexora-text mb-4">Agent Usage</h3>
      <p className="text-nexora-muted text-sm text-center py-8">No data yet. Start chatting!</p>
    </div>
  )

  return (
    <div className="glass-card p-5">
      <h3 className="text-sm font-semibold text-nexora-text mb-4">Agent Usage</h3>
      <ResponsiveContainer width="100%" height={180}>
        <PieChart>
          <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={65} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={{ stroke: '#64748b' }}>
            {chartData.map((_, i) => (
              <Cell key={i} fill={AGENT_COLORS[i % AGENT_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid #2a2a4a', borderRadius: 8, fontSize: 12 }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
