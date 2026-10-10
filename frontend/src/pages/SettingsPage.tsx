// ============================================
// NEXORA AI - Settings Page
// ============================================
import { useState, useEffect } from 'react'
import { Save, Cpu, User, Bell } from 'lucide-react'
import Navbar from '../components/layout/Navbar'
import { useAuthStore } from '../store/authStore'
import api from '../api/axios'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const { user } = useAuthStore()
  const [aiStatus, setAiStatus] = useState<any>(null)
  const [model, setModel] = useState('tinyllama')

  useEffect(() => {
    api.get('/api/ai/status').then(res => {
      setAiStatus(res.data)
      setModel(res.data.ollama?.current_model || 'tinyllama')
    }).catch(() => {})
  }, [])

  const handleSave = () => toast.success('Settings saved!')

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <Navbar title="Settings" subtitle="Configure NEXORA AI" />
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-2xl mx-auto space-y-5">

          {/* Profile */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold text-nexora-text mb-4 flex items-center gap-2">
              <User size={16} className="text-nexora-primary" /> Profile
            </h3>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-nexora-muted block mb-1.5">Full Name</label>
                <input defaultValue={user?.full_name} className="w-full bg-nexora-card border border-nexora-border rounded-xl px-4 py-2.5 text-sm text-nexora-text nexora-input" />
              </div>
              <div>
                <label className="text-xs text-nexora-muted block mb-1.5">Email</label>
                <input defaultValue={user?.email} disabled className="w-full bg-nexora-card border border-nexora-border rounded-xl px-4 py-2.5 text-sm text-nexora-muted cursor-not-allowed" />
              </div>
            </div>
          </div>

          {/* AI Configuration */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold text-nexora-text mb-4 flex items-center gap-2">
              <Cpu size={16} className="text-nexora-secondary" /> AI Configuration
            </h3>
            <div className="space-y-4">
              {/* Ollama status */}
              <div className="flex items-center justify-between p-3 bg-nexora-card rounded-xl">
                <div>
                  <p className="text-sm text-nexora-text">Ollama (Local LLM)</p>
                  <p className="text-xs text-nexora-muted">http://localhost:11434</p>
                </div>
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                  aiStatus?.ollama?.available
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-red-500/20 text-red-400'
                }`}>
                  {aiStatus?.ollama?.available ? '● Running' : '● Offline'}
                </span>
              </div>

              {/* Model selector */}
              <div>
                <label className="text-xs text-nexora-muted block mb-1.5">Active Model</label>
                <select value={model} onChange={e => setModel(e.target.value)}
                  className="w-full bg-nexora-card border border-nexora-border rounded-xl px-4 py-2.5 text-sm text-nexora-text nexora-input">
                  <option value="tinyllama">TinyLlama (Fast, ~1.5GB RAM)</option>
                  <option value="phi3">Phi3-mini (Accurate, ~2.5GB RAM)</option>
                  <option value="mistral">Mistral 7B (Best, ~4GB RAM)</option>
                </select>
              </div>

              {/* Available models */}
              {aiStatus?.ollama?.models?.length > 0 && (
                <div>
                  <p className="text-xs text-nexora-muted mb-2">Installed models:</p>
                  <div className="flex flex-wrap gap-2">
                    {aiStatus.ollama.models.map((m: string) => (
                      <span key={m} className="text-xs bg-nexora-card border border-nexora-border px-2.5 py-1 rounded-lg text-nexora-muted">{m}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Ollama Setup Guide */}
          <div className="glass-card p-6 border border-amber-500/20">
            <h3 className="text-sm font-semibold text-amber-400 mb-3">⚠️ Ollama Setup</h3>
            <div className="space-y-2 text-xs text-nexora-muted font-mono">
              <p className="text-nexora-text text-xs mb-2">Ollama না চললে এই commands run করুন:</p>
              {['ollama serve', 'ollama pull tinyllama', '# অথবা:', 'ollama pull phi3'].map((cmd, i) => (
                <div key={i} className={`px-3 py-2 rounded-lg ${cmd.startsWith('#') ? 'text-nexora-muted' : 'bg-nexora-bg border border-nexora-border text-emerald-400'}`}>
                  {cmd.startsWith('#') ? cmd : `$ ${cmd}`}
                </div>
              ))}
            </div>
          </div>

          {/* Save */}
          <button onClick={handleSave}
            className="w-full btn-primary py-3 rounded-xl text-white text-sm font-medium flex items-center justify-center gap-2">
            <Save size={15} /> Save Settings
          </button>

        </div>
      </div>
    </div>
  )
}
