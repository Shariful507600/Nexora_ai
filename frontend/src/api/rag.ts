// ============================================
// NEXORA AI - RAG API Functions
// ============================================
import api from './axios'

export const ragAPI = {
  uploadDocument: (file: File, description?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (description) formData.append('description', description)
    return api.post('/api/rag/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  queryDocuments: (question: string, docIds?: number[]) =>
    api.post('/api/rag/query', { question, doc_ids: docIds }),

  getDocuments: () => api.get('/api/rag/documents'),

  deleteDocument: (docId: number) =>
    api.delete(`/api/rag/documents/${docId}`),
}
