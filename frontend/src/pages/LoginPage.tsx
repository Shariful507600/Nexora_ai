// ============================================
// NEXORA AI - Login / Register Page
// ============================================
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Zap, Mail, Lock, User, Eye, EyeOff } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [isLogin, setIsLogin]         = useState(true)
  const [showPass, setShowPass]       = useState(false)
  const [name, setName]               = useState('')
  const [email, setEmail]             = useState('')
  const [password, setPassword]       = useState('')
  const { login, register, isLoading } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (isLogin) {
        await login(email, password)
        toast.success('স্বাগতম! 🎉')
        navigate('/')
      } else {
        await register(name, email, password)
        toast.success('Account তৈরি হয়েছে! এখন login করুন।')
        setIsLogin(true)
      }
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Something went wrong!')
    }
  }

  return (
    <div className="min-h-screen bg-nexora-bg flex items-center justify-center p-4">
      {/* Background glow */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-nexora-primary/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 left-1/4 w-64 h-64 bg-nexora-secondary/10 rounded-full blur-3xl" />
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md relative z-10">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-nexora-primary to-nexora-secondary flex items-center justify-center mx-auto mb-4 glow-primary">
            <Zap size={28} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold gradient-text">NEXORA AI</h1>
          <p className="text-nexora-muted text-sm mt-1">Knowledge & Productivity Copilot</p>
        </div>

        {/* Card */}
        <div className="glass-card p-8">
          {/* Toggle */}
          <div className="flex bg-nexora-bg rounded-xl p-1 mb-6">
            {['Login', 'Register'].map((tab) => (
              <button key={tab} onClick={() => setIsLogin(tab === 'Login')}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  (tab === 'Login') === isLogin
                    ? 'bg-nexora-primary text-white shadow-lg'
                    : 'text-nexora-muted hover:text-nexora-text'
                }`}>{tab}</button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <AnimatePresence>
              {!isLogin && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
                  <label className="text-xs text-nexora-muted block mb-1.5">Full Name</label>
                  <div className="relative">
                    <User size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-nexora-muted" />
                    <input value={name} onChange={e => setName(e.target.value)} placeholder="আপনার নাম"
                      className="w-full bg-nexora-card border border-nexora-border rounded-xl pl-10 pr-4 py-3 text-sm text-nexora-text placeholder-nexora-muted nexora-input" required />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div>
              <label className="text-xs text-nexora-muted block mb-1.5">Email</label>
              <div className="relative">
                <Mail size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-nexora-muted" />
                <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com"
                  className="w-full bg-nexora-card border border-nexora-border rounded-xl pl-10 pr-4 py-3 text-sm text-nexora-text placeholder-nexora-muted nexora-input" required />
              </div>
            </div>

            <div>
              <label className="text-xs text-nexora-muted block mb-1.5">Password</label>
              <div className="relative">
                <Lock size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-nexora-muted" />
                <input type={showPass ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••"
                  className="w-full bg-nexora-card border border-nexora-border rounded-xl pl-10 pr-11 py-3 text-sm text-nexora-text placeholder-nexora-muted nexora-input" required />
                <button type="button" onClick={() => setShowPass(!showPass)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-nexora-muted hover:text-nexora-text">
                  {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            <button type="submit" disabled={isLoading}
              className="w-full btn-primary py-3 rounded-xl text-white text-sm font-semibold flex items-center justify-center gap-2 disabled:opacity-50 mt-2">
              {isLoading
                ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Loading...</>
                : isLogin ? '🚀 Login' : '✨ Create Account'}
            </button>
          </form>

          {/* Demo credentials */}
          {isLogin && (
            <div className="mt-4 p-3 bg-nexora-bg rounded-xl border border-nexora-border">
              <p className="text-xs text-nexora-muted text-center">
                Demo: <span className="text-nexora-text">demo@nexora.ai</span> / <span className="text-nexora-text">demo123</span>
              </p>
            </div>
          )}
        </div>

        <p className="text-center text-xs text-nexora-muted mt-4">
          Built with ❤️ using FastAPI + React + Ollama
        </p>
      </motion.div>
    </div>
  )
}
