// ============================================
// NEXORA AI - AI API Functions
// ============================================
import api from './axios'

export const aiAPI = {
  sendMessage: (message: string, chatId: number | null, agent: string) =>
    api.post('/api/ai/chat', { message, chat_id: chatId, agent }),

  getChats: () => api.get('/api/ai/chats'),

  createChat: (title?: string) =>
    api.post('/api/ai/chats', { title: title || 'New Chat' }),

  getMessages: (chatId: number) =>
    api.get(`/api/ai/chats/${chatId}/messages`),

  getAIStatus: () => api.get('/api/ai/status'),

  deleteChat: (chatId: number) =>
    api.delete(`/api/ai/chats/${chatId}`),
}
