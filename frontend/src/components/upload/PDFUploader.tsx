// ============================================
// NEXORA AI - PDF Uploader Component
// ============================================
import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, CheckCircle, XCircle, Loader } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { ragAPI } from '../../api/rag'
import toast from 'react-hot-toast'

interface UploadState {
  status: 'idle' | 'uploading' | 'processing' | 'success' | 'error'
  progress: number
  result?: { filename: string; pages: number; chunks: number }
  error?: string
}

interface PDFUploaderProps {
  onUploadSuccess?: () => void
}

export default function PDFUploader({ onUploadSuccess }: PDFUploaderProps) {
  const [uploadState, setUploadState] = useState<UploadState>({ status: 'idle', progress: 0 })

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    if (!file.name.endsWith('.pdf')) {
      toast.error('শুধুমাত্র PDF ফাইল upload করুন!')
      return
    }

    setUploadState({ status: 'uploading', progress: 20 })

    try {
      setUploadState({ status: 'processing', progress: 60 })

      const response = await ragAPI.uploadDocument(file)
      const data = response.data

      setUploadState({
        status: 'success',
        progress: 100,
        result: { filename: data.filename, pages: data.pages, chunks: data.chunks },
      })

      toast.success(`✅ "${data.filename}" সফলভাবে upload হয়েছে!`)
      onUploadSuccess?.()

      // Reset after 4 seconds
      setTimeout(() => setUploadState({ status: 'idle', progress: 0 }), 4000)

    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Upload failed!'
      setUploadState({ status: 'error', progress: 0, error: msg })
      toast.error(msg)
      setTimeout(() => setUploadState({ status: 'idle', progress: 0 }), 3000)
    }
  }, [onUploadSuccess])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: uploadState.status !== 'idle',
  })

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300 ${
          isDragActive
            ? 'border-nexora-primary bg-nexora-primary/10 scale-[1.02]'
            : uploadState.status === 'idle'
            ? 'border-nexora-border hover:border-nexora-primary/50 hover:bg-nexora-card'
            : 'border-nexora-border cursor-not-allowed'
        }`}
      >
        <input {...getInputProps()} />

        <AnimatePresence mode="wait">
          {/* Idle state */}
          {uploadState.status === 'idle' && (
            <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <div className="w-14 h-14 rounded-2xl bg-nexora-card border border-nexora-border flex items-center justify-center mx-auto mb-4">
                <Upload size={24} className="text-nexora-primary" />
              </div>
              <p className="text-nexora-text font-medium mb-1">
                {isDragActive ? 'PDF ছেড়ে দিন...' : 'PDF drag করুন অথবা click করুন'}
              </p>
              <p className="text-nexora-muted text-sm">Maximum 10MB · PDF only</p>
            </motion.div>
          )}

          {/* Uploading / Processing */}
          {(uploadState.status === 'uploading' || uploadState.status === 'processing') && (
            <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <Loader size={32} className="text-nexora-primary animate-spin mx-auto mb-3" />
              <p className="text-nexora-text font-medium">
                {uploadState.status === 'uploading' ? 'Uploading...' : 'Processing & creating embeddings...'}
              </p>
              <p className="text-nexora-muted text-sm mt-1">এটি কিছুটা সময় নিতে পারে</p>
              {/* Progress bar */}
              <div className="mt-4 bg-nexora-card rounded-full h-1.5 overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-nexora-primary to-nexora-secondary rounded-full"
                  initial={{ width: '0%' }}
                  animate={{ width: `${uploadState.progress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </motion.div>
          )}

          {/* Success */}
          {uploadState.status === 'success' && uploadState.result && (
            <motion.div key="success" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
              <CheckCircle size={32} className="text-emerald-400 mx-auto mb-3" />
              <p className="text-emerald-400 font-semibold mb-3">Upload সফল!</p>
              <div className="flex justify-center gap-4 text-sm">
                <span className="glass-card px-3 py-1.5 text-nexora-muted">
                  📄 {uploadState.result.pages} pages
                </span>
                <span className="glass-card px-3 py-1.5 text-nexora-muted">
                  🧩 {uploadState.result.chunks} chunks
                </span>
              </div>
            </motion.div>
          )}

          {/* Error */}
          {uploadState.status === 'error' && (
            <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <XCircle size={32} className="text-red-400 mx-auto mb-3" />
              <p className="text-red-400 font-medium">{uploadState.error}</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
