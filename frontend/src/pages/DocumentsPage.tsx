// ============================================
// NEXORA AI - Documents (RAG) Page
// ============================================
import { useState, useEffect } from 'react'
import { FileText, Trash2, Search, Send, BookOpen } from 'lucide-react'
import { motion } from 'framer-motion'
import PDFUploader from '../components/upload/PDFUploader'
import Navbar from '../components/layout/Navbar'
import { ragAPI } from '../api/rag'
import ReactMarkdown from 'react-markdown'
import toast from 'react-hot-toast'

interface Document {
  id: number
  filename: string
  file_size: number
  is_processed: boolean
  chunk_count: number
  page_count: number
  word_count: number
  created_at: string
}

interface RAGResult {
  question: string
  answer: string
  sources: { source: string; similarity: number; text_preview: string }[]
  chunks_used: number
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [question, setQuestion]   = useState('')
  const [ragResult, setRagResult] = useState<RAGResult | null>(null)
  const [isQuerying, setIsQuerying] = useState(false)
  const [selectedDocs, setSelectedDocs] = useState<number[]>([])

  useEffect(() => { loadDocuments() }, [])

  const loadDocuments = async () => {
    try {
      const res = await ragAPI.getDocuments()
      setDocuments(res.data)
    } catch { /* silent */ }
  }

  const handleDelete = async (docId: number) => {
    if (!confirm('এই document মুছে ফেলবেন?')) return
    try {
      await ragAPI.deleteDocument(docId)
      setDocuments((prev) => prev.filter((d) => d.id !== docId))
      toast.success('Document deleted!')
    } catch { toast.error('Delete failed!') }
  }

  const handleQuery = async () => {
    if (!question.trim()) { toast.error('প্রশ্ন লিখুন!'); return }
    if (documents.filter(d => d.is_processed).length === 0) { toast.error('আগে PDF upload করুন!'); return }
    setIsQuerying(true)
    try {
      const res = await ragAPI.queryDocuments(question, selectedDocs.length ? selectedDocs : undefined)
      setRagResult(res.data)
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Query failed!')
    } finally {
      setIsQuerying(false)
    }
  }

  const formatSize = (bytes: number) => bytes < 1024 * 1024
    ? `${(bytes / 1024).toFixed(1)} KB`
    : `${(bytes / (1024 * 1024)).toFixed(1)} MB`

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <Navbar title="Documents · RAG" subtitle="Upload PDFs and ask questions from them" />
      <div className="flex-1 overflow-y-auto p-6 space-y-6">

        {/* Upload Section */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold text-nexora-text mb-4 flex items-center gap-2">
            <FileText size={16} className="text-nexora-primary" /> Upload PDF Document
          </h3>
          <PDFUploader onUploadSuccess={loadDocuments} />
        </div>

        {/* Document List */}
        {documents.length > 0 && (
          <div className="glass-card p-6">
            <h3 className="text-sm font-semibold text-nexora-text mb-4 flex items-center gap-2">
              <BookOpen size={16} className="text-nexora-accent" />
              Your Documents ({documents.length})
            </h3>
            <div className="space-y-2">
              {documents.map((doc) => (
                <motion.div key={doc.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                  className={`flex items-center gap-3 p-3 rounded-xl border transition-all cursor-pointer ${
                    selectedDocs.includes(doc.id)
                      ? 'border-nexora-primary/50 bg-nexora-primary/10'
                      : 'border-nexora-border bg-nexora-card hover:border-nexora-border/80'
                  }`}
                  onClick={() => setSelectedDocs(prev =>
                    prev.includes(doc.id) ? prev.filter(id => id !== doc.id) : [...prev, doc.id]
                  )}
                >
                  <FileText size={16} className={doc.is_processed ? 'text-emerald-400' : 'text-nexora-muted'} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-nexora-text truncate font-medium">{doc.filename}</p>
                    <p className="text-xs text-nexora-muted">
                      {formatSize(doc.file_size)} · {doc.page_count} pages · {doc.chunk_count} chunks
                    </p>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    doc.is_processed
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : 'bg-amber-500/20 text-amber-400'
                  }`}>
                    {doc.is_processed ? 'Ready' : 'Processing'}
                  </span>
                  <button onClick={(e) => { e.stopPropagation(); handleDelete(doc.id) }}
                    className="w-7 h-7 rounded-lg flex items-center justify-center text-nexora-muted hover:text-red-400 hover:bg-red-400/10 transition-colors">
                    <Trash2 size={13} />
                  </button>
                </motion.div>
              ))}
            </div>
            {selectedDocs.length > 0 && (
              <p className="text-xs text-nexora-primary mt-2">
                {selectedDocs.length} document(s) selected for query
              </p>
            )}
          </div>
        )}

        {/* RAG Query */}
        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold text-nexora-text mb-4 flex items-center gap-2">
            <Search size={16} className="text-nexora-secondary" /> Ask from Documents
          </h3>
          <div className="flex gap-3">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
              placeholder="আপনার document সম্পর্কে প্রশ্ন করুন..."
              className="flex-1 bg-nexora-card border border-nexora-border rounded-xl px-4 py-3 text-sm text-nexora-text placeholder-nexora-muted nexora-input"
            />
            <button onClick={handleQuery} disabled={isQuerying}
              className="btn-primary px-5 py-3 rounded-xl text-white flex items-center gap-2 text-sm font-medium disabled:opacity-50">
              {isQuerying
                ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                : <Send size={15} />}
              Ask
            </button>
          </div>
        </div>

        {/* RAG Answer */}
        {ragResult && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6 border border-nexora-primary/20">
            <p className="text-xs text-nexora-primary font-medium mb-1">Q: {ragResult.question}</p>
            <div className="markdown-content text-sm text-nexora-text mt-3 mb-4">
              <ReactMarkdown>{ragResult.answer}</ReactMarkdown>
            </div>
            {ragResult.sources.length > 0 && (
              <div className="border-t border-nexora-border pt-3">
                <p className="text-xs text-nexora-muted mb-2">Sources used ({ragResult.chunks_used} chunks):</p>
                {ragResult.sources.map((src, i) => (
                  <div key={i} className="text-xs text-nexora-muted bg-nexora-card rounded-lg px-3 py-2 mb-1">
                    📄 {src.source} · Similarity: {(src.similarity * 100).toFixed(0)}%
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}

      </div>
    </div>
  )
}
