// ============================================
// NEXORA AI - ChatBox Component
// ============================================
import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'
import { Zap } from 'lucide-react'

interface Message {
  id?: number
  role: 'user' | 'assistant'
  content: string
  agent_type?: string
  created_at?: string
}

interface ChatBoxProps {
  messages: Message[]
  isLoading: boolean
  onSend: (message: string, agent: string) => void
  onVoiceClick?: () => void
}

const WELCOME_SUGGESTIONS = [
  'Explain RAG architecture in simple terms',
  'Create a study plan for AI Engineering',
  'What is the difference between LLM and Generative AI?',
  'Help me understand Prompt Engineering',
]

export default function ChatBox({ messages, isLoading, onSend, onVoiceClick }: ChatBoxProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-5">

        {/* Empty state / Welcome screen */}
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full py-12 animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center mb-5 glow-primary">
              <Zap size={30} className="text-white" />
            </div>
            <h3 className="text-xl font-bold gradient-text mb-2">Welcome to NEXORA AI</h3>
            <p className="text-nexora-muted text-sm mb-8 text-center max-w-sm">
              Your AI-powered Knowledge & Productivity Copilot. Ask anything, upload documents, or use voice input.
            </p>

            {/* Quick suggestions */}
            <div className="grid grid-cols-1 gap-2 w-full max-w-lg">
              {WELCOME_SUGGESTIONS.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => onSend(suggestion, 'general')}
                  className="text-left px-4 py-3 rounded-xl glass-card text-sm text-nexora-muted hover:text-nexora-text hover:border-nexora-primary/40 transition-all duration-200"
                >
                  💡 {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chat messages */}
        {messages.map((msg, index) => (
          <MessageBubble
            key={msg.id || index}
            role={msg.role}
            content={msg.content}
            agentType={msg.agent_type}
            createdAt={msg.created_at}
          />
        ))}

        {/* Typing indicator */}
        {isLoading && <MessageBubble role="assistant" content="" isTyping />}

        {/* Scroll anchor */}
        <div ref={bottomRef} />
      </div>

      {/* Input Area */}
      <ChatInput onSend={onSend} isLoading={isLoading} onVoiceClick={onVoiceClick} />
    </div>
  )
}
