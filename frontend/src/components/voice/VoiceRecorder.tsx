import { useState, useRef, useEffect } from 'react'
import { Mic, Square, Volume2, AlertCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import api from '../../api/axios'
import toast from 'react-hot-toast'

interface VoiceRecorderProps {
  onTranscript?: (text: string) => void
}

export default function VoiceRecorder({ onTranscript }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isSupported, setIsSupported] = useState(true)
  const [transcript, setTranscript] = useState('')
  const [interimText, setInterimText] = useState('')
  const [isSpeaking, setIsSpeaking] = useState(false)
  const recognitionRef = useRef<any>(null)

  useEffect(() => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SR) setIsSupported(false)
  }, [])

  const startRecording = () => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SR) { toast.error('Browser support নেই!'); return }

    const recognition = new SR()
    recognitionRef.current = recognition
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'bn-BD'

    recognition.onstart = () => {
      setIsRecording(true)
      setTranscript('')
      setInterimText('')
      toast.success('🎤 Recording শুরু...')
    }

    recognition.onresult = (event: any) => {
      let final = '', interim = ''
      for (let i = 0; i < event.results.length; i++) {
        if (event.results[i].isFinal) final += event.results[i][0].transcript + ' '
        else interim += event.results[i][0].transcript
      }
      if (final) { setTranscript(p => p + final); onTranscript?.(final.trim()) }
      setInterimText(interim)
    }

    recognition.onerror = (e: any) => {
      if (e.error === 'language-not-supported') { recognition.lang = 'en-US'; recognition.start(); return }
      setIsRecording(false)
      toast.error('Microphone error!')
    }

    recognition.onend = () => { setIsRecording(false); setInterimText('') }
    recognition.start()
  }

  const stopRecording = () => {
    recognitionRef.current?.stop()
    setIsRecording(false)
    setInterimText('')
    if (transcript) toast.success('✅ Done!')
  }

  const speak = async (text: string) => {
    setIsSpeaking(true)
    try {
      const res = await api.post('/api/voice/text-to-speech', { text: text.substring(0, 300), language: 'en' }, { responseType: 'blob' })
      const url = URL.createObjectURL(res.data)
      const audio = new Audio(url)
      audio.onended = () => { setIsSpeaking(false); URL.revokeObjectURL(url) }
      audio.play()
    } catch {
      const u = new SpeechSynthesisUtterance(text)
      u.onend = () => setIsSpeaking(false)
      window.speechSynthesis.speak(u)
    }
  }

  if (!isSupported) return (
    <div className="flex flex-col items-center gap-3 p-6 text-center">
      <AlertCircle size={32} className="text-amber-400" />
      <p className="text-nexora-muted text-sm">Chrome বা Edge ব্যবহার করুন।</p>
    </div>
  )

  return (
    <div className="flex flex-col items-center gap-6 w-full">
      <div className="relative flex items-center justify-center">
        {isRecording && (
          <>
            <div className="absolute w-32 h-32 rounded-full bg-red-500/15 animate-ping" />
            <div className="absolute w-44 h-44 rounded-full bg-red-500/08 animate-ping" style={{ animationDelay: '0.4s' }} />
          </>
        )}
        <motion.button
          whileTap={{ scale: 0.92 }}
          onClick={isRecording ? stopRecording : startRecording}
          className={`relative w-24 h-24 rounded-full flex items-center justify-center shadow-2xl transition-all duration-300 ${isRecording
            ? 'bg-gradient-to-br from-red-500 to-rose-600'
            : 'bg-gradient-to-br from-indigo-500 to-purple-600'
            }`}
        >
          {isRecording ? <Square size={28} className="text-white" fill="white" /> : <Mic size={28} className="text-white" />}
        </motion.button>
      </div>

      <p className={`text-sm font-medium ${isRecording ? 'text-red-400' : 'text-nexora-muted'}`}>
        {isRecording ? '🔴 Recording... Click করে থামান' : '🎙️ Click করে শুরু করুন'}
      </p>

      {isRecording && interimText && (
        <div className="w-full glass-card px-4 py-3 border border-indigo-500/20">
          <p className="text-xs text-nexora-muted mb-1">Live:</p>
          <p className="text-nexora-muted text-sm italic">{interimText}...</p>
        </div>
      )}

      {transcript && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
          className="w-full glass-card p-4 border border-nexora-primary/20">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1">
              <p className="text-xs text-nexora-primary font-medium mb-2">✅ Transcript:</p>
              <p className="text-nexora-text text-sm leading-relaxed">"{transcript.trim()}"</p>
            </div>
            <button onClick={() => speak(transcript)} disabled={isSpeaking}
              className="w-9 h-9 rounded-xl bg-nexora-card flex items-center justify-center text-nexora-accent hover:bg-nexora-accent/20 transition-colors disabled:opacity-50">
              <Volume2 size={15} className={isSpeaking ? 'animate-pulse' : ''} />
            </button>
          </div>
        </motion.div>
      )}

      <p className="text-xs text-nexora-muted">বাংলা ও English উভয় ভাষায় কথা বলতে পারবেন</p>
    </div>
  )
}