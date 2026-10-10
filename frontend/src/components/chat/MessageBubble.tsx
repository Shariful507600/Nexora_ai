// ============================================
// NEXORA AI - Message Bubble Component
// ============================================
import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import { Zap, User, Bot, Clock } from 'lucide-react'

interface MessageBubbleProps {
  role: 'user' | 'assistant'
  content: string
  agentType?: string
  createdAt?: string
  isTyping?: boolean
}

const agentColors: Record<string, string> = {
  general: 'text-indigo-400',
  tutor:   'text-emerald-400',
  planner: 'text-amber-400',
  rag:     'text-cyan-400',
}

const agentLabel: Record<string, string> = {
  general: 'NEXORA',
  tutor:   'Tutor Agent',
  planner: 'Planner Agent',
  rag:     'RAG Agent',
}

export default function MessageBubble({ role, content, agentType = 'general', createdAt, isTyping }: MessageBubbleProps) {
  const isUser = role === 'user'

  if (isTyping) {
    return (
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
        className="flex items-start gap-3 message-bubble">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
          <Zap size={14} className="text-white" />
        </div>
        <div className="glass-card px-4 py-3 flex items-center gap-1.5">
          <div className="typing-dot" />
          <div className="typing-dot" />
          <div className="typing-dot" />
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex items-start gap-3 message-bubble ${isUser ? 'flex-row-reverse' : ''}`}
    >
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 ${
        isUser
          ? 'bg-nexora-card border border-nexora-border'
          : 'bg-gradient-to-br from-indigo-500 to-purple-600'
      }`}>
        {isUser
          ? <User size={14} className="text-nexora-muted" />
          : <Zap size={14} className="text-white" />
        }
      </div>

      {/* Bubble */}
      <div className={`max-w-[75%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
        {/* Agent label */}
        {!isUser && (
          <span className={`text-xs font-medium ${agentColors[agentType] || 'text-indigo-400'}`}>
            {agentLabel[agentType] || 'NEXORA'}
          </span>
        )}

        <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? 'bg-gradient-to-br from-indigo-600 to-purple-700 text-white rounded-tr-sm'
            : 'glass-card text-nexora-text rounded-tl-sm'
        }`}>
          {isUser
            ? <p className="whitespace-pre-wrap">{content}</p>
            : <div className="markdown-content"><ReactMarkdown>{content}</ReactMarkdown></div>
          }
        </div>

        {/* Timestamp */}
        {createdAt && (
          <div className="flex items-center gap-1 text-xs text-nexora-muted px-1">
            <Clock size={10} />
            {new Date(createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        )}
      </div>
    </motion.div>
  )
}
