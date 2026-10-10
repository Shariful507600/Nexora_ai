// ============================================
// NEXORA AI - AI Chat Page
// ============================================
import { useState, useEffect } from 'react'
import { Plus, MessageSquare, Trash2 } from 'lucide-react'
import ChatBox from '../components/chat/ChatBox'
import Navbar from '../components/layout/Navbar'
import { aiAPI } from '../api/ai'
import toast from 'react-hot-toast'

interface Message {
  id?: number
  role: 'user' | 'assistant'
  content: string
  agent_type?: string
  created_at?: string
}

interface Chat {
  id: number
  title: string
  created_at: string
}

export default function AIChatPage() {
  const [chats, setChats] = useState<Chat[]>([])
  const [activeChatId, setActiveChatId] = useState<number | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // Load chats on mount
  useEffect(() => {
    loadChats()
  }, [])

  // Load messages when chat changes
  useEffect(() => {
    if (activeChatId) loadMessages(activeChatId)
    else setMessages([])
  }, [activeChatId])

  const loadChats = async () => {
    try {
      const res = await aiAPI.getChats()
      setChats(res.data)
    } catch { /* silent */ }
  }

  const loadMessages = async (chatId: number) => {
    try {
      const res = await aiAPI.getMessages(chatId)
      setMessages(res.data)
    } catch { /* silent */ }
  }

  const handleNewChat = () => {
    setActiveChatId(null)
    setMessages([])
  }

  const handleSend = async (message: string, agent: string) => {
    // Optimistic UI - user message turani দেখাও
    const userMsg: Message = { role: 'user', content: message, created_at: new Date().toISOString() }
    setMessages((prev) => [...prev, userMsg])
    setIsLoading(true)

    try {
      const res = await aiAPI.sendMessage(message, activeChatId, agent)
      const { chat_id, response, provider } = res.data

      // New chat হলে chat list refresh করো
      if (!activeChatId) {
        setActiveChatId(chat_id)
        loadChats()
      }

      const aiMsg: Message = {
        role: 'assistant',
        content: response,
        agent_type: agent,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, aiMsg])

    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'AI response পেতে সমস্যা হয়েছে!')
      setMessages((prev) => prev.slice(0, -1)) // user message সরাও
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex-1 flex min-h-0">

      {/* Chat sidebar */}
      <div className="w-64 border-r border-nexora-border flex flex-col bg-nexora-surface">
        <div className="p-4 border-b border-nexora-border">
          <button
            onClick={handleNewChat}
            className="w-full btn-primary flex items-center justify-center gap-2 py-2.5 rounded-xl text-white text-sm font-medium"
          >
            <Plus size={16} /> New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {chats.length === 0 && (
            <p className="text-nexora-muted text-xs text-center py-6">No chats yet</p>
          )}
          {chats.map((chat) => (
            <button
              key={chat.id}
              onClick={() => setActiveChatId(chat.id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-left text-sm transition-all duration-200 group ${activeChatId === chat.id
                  ? 'bg-nexora-primary/15 text-indigo-300 border border-nexora-primary/30'
                  : 'text-nexora-muted hover:text-nexora-text hover:bg-nexora-card'
                }`}
            >
              <MessageSquare size={14} className="flex-shrink-0" />
              <span className="flex-1 truncate">{chat.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-h-0">
        <Navbar
          title={activeChatId ? (chats.find(c => c.id === activeChatId)?.title || 'Chat') : 'New Chat'}
          subtitle="AI Chat · Multi-agent support"
        />
        <div className="flex-1 min-h-0">
          <ChatBox messages={messages} isLoading={isLoading} onSend={handleSend} />
        </div>
      </div>

    </div>
  )
}