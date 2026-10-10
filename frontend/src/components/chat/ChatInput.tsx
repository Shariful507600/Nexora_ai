// ============================================
// NEXORA AI - Chat Input Component
// ============================================
import { useState, useRef, KeyboardEvent } from 'react'
import { Send, Mic, Bot, GraduationCap, Calendar } from 'lucide-react'

interface ChatInputProps {
  onSend: (message: string, agent: string) => void
  isLoading: boolean
  onVoiceClick?: () => void
}

const agents = [
  { id: 'general', label: 'General',  icon: Bot,           color: 'text-indigo-400' },
  { id: 'tutor',   label: 'Tutor',    icon: GraduationCap, color: 'text-emerald-400' },
  { id: 'planner', label: 'Planner',  icon: Calendar,      color: 'text-amber-400' },
]

export default function ChatInput({ onSend, isLoading, onVoiceClick }: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [selectedAgent, setSelectedAgent] = useState('general')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    if (!message.trim() || isLoading) return
    onSend(message.trim(), selectedAgent)
    setMessage('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = () => {
    if (!textareaRef.current) return
    textareaRef.current.style.height = 'auto'
    textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 140) + 'px'
  }

  return (
    <div className="border-t border-nexora-border bg-nexora-surface/80 backdrop-blur-md p-4">
      {/* Agent Selector */}
      <div className="flex gap-2 mb-3">
        {agents.map(({ id, label, icon: Icon, color }) => (
          <button
            key={id}
            onClick={() => setSelectedAgent(id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
              selectedAgent === id
                ? 'bg-nexora-card border border-nexora-primary/50 ' + color
                : 'text-nexora-muted hover:text-nexora-text hover:bg-nexora-card border border-transparent'
            }`}
          >
            <Icon size={13} />
            {label}
          </button>
        ))}
      </div>

      {/* Input Row */}
      <div className="flex items-end gap-3">
        <div className="flex-1 glass-card flex items-end gap-2 px-4 py-2.5 min-h-[48px]">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            onInput={handleInput}
            placeholder="Message NEXORA... (Enter to send, Shift+Enter for new line)"
            rows={1}
            className="flex-1 bg-transparent text-nexora-text placeholder-nexora-muted text-sm resize-none focus:outline-none leading-relaxed"
            style={{ maxHeight: '140px' }}
          />
        </div>

        {/* Voice Button */}
        {onVoiceClick && (
          <button
            onClick={onVoiceClick}
            className="w-11 h-11 rounded-xl bg-nexora-card border border-nexora-border flex items-center justify-center text-nexora-muted hover:text-nexora-accent hover:border-nexora-accent transition-all duration-200"
          >
            <Mic size={18} />
          </button>
        )}

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={!message.trim() || isLoading}
          className="w-11 h-11 rounded-xl btn-primary flex items-center justify-center text-white disabled:opacity-40 disabled:cursor-not-allowed disabled:transform-none transition-all duration-200"
        >
          {isLoading
            ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            : <Send size={17} />
          }
        </button>
      </div>

      <p className="text-xs text-nexora-muted mt-2 text-center">
        NEXORA AI · Local LLM powered · Your data stays private
      </p>
    </div>
  )
}
