// ============================================
// NEXORA AI - Voice Assistant Page
// ============================================
import { useState } from 'react'
import { Volume2, Send } from 'lucide-react'
import VoiceRecorder from '../components/voice/VoiceRecorder'
import Navbar from '../components/layout/Navbar'
import { aiAPI } from '../api/ai'
import api from '../api/axios'
import toast from 'react-hot-toast'
import ReactMarkdown from 'react-markdown'

export default function VoiceAssistantPage() {
  const [transcript, setTranscript] = useState('')
  const [aiResponse, setAiResponse] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)

  const handleTranscript = (text: string) => {
    setTranscript(text)
  }

  const handleSendToAI = async () => {
    if (!transcript.trim()) { toast.error('আগে voice record করুন!'); return }
    setIsProcessing(true)
    setAiResponse('')
    try {
      const res = await aiAPI.sendMessage(transcript, null, 'general')
      const response = res.data.response
      setAiResponse(response)
      await speakResponse(response)
    } catch {
      toast.error('AI response পেতে সমস্যা হয়েছে!')
    } finally {
      setIsProcessing(false)
    }
  }

  const speakResponse = async (text: string) => {
    setIsSpeaking(true)
    try {
      const shortText = text.length > 300 ? text.substring(0, 300) + '...' : text
      const res = await api.post('/api/voice/text-to-speech', { text: shortText, language: 'en' }, { responseType: 'blob' })
      const url = URL.createObjectURL(res.data)
      const audio = new Audio(url)
      audio.onended = () => { setIsSpeaking(false); URL.revokeObjectURL(url) }
      audio.play()
    } catch { setIsSpeaking(false) }
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      <Navbar title="Voice Assistant" subtitle="Speak and get AI responses" />
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-xl mx-auto space-y-6">

          {/* Voice Recorder */}
          <div className="glass-card p-8 flex flex-col items-center">
            <h3 className="text-sm font-semibold text-nexora-text mb-6">🎙️ Voice Input</h3>
            <VoiceRecorder onTranscript={handleTranscript} />
          </div>

          {/* Send to AI */}
          {transcript && (
            <div className="glass-card p-5">
              <p className="text-xs text-nexora-muted mb-2">Recognized text:</p>
              <p className="text-nexora-text text-sm mb-4 italic">"{transcript}"</p>
              <button onClick={handleSendToAI} disabled={isProcessing}
                className="w-full btn-primary py-3 rounded-xl text-white text-sm font-medium flex items-center justify-center gap-2 disabled:opacity-50">
                {isProcessing
                  ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Processing...</>
                  : <><Send size={15} /> Send to AI</>}
              </button>
            </div>
          )}

          {/* AI Response */}
          {aiResponse && (
            <div className="glass-card p-5 border border-nexora-primary/20">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs text-nexora-primary font-medium">🤖 NEXORA Response:</p>
                <button onClick={() => speakResponse(aiResponse)} disabled={isSpeaking}
                  className="flex items-center gap-1.5 text-xs text-nexora-accent hover:text-nexora-accent/80 disabled:opacity-50">
                  <Volume2 size={13} className={isSpeaking ? 'animate-pulse' : ''} />
                  {isSpeaking ? 'Speaking...' : 'Listen'}
                </button>
              </div>
              <div className="markdown-content text-sm text-nexora-text">
                <ReactMarkdown>{aiResponse}</ReactMarkdown>
              </div>
            </div>
          )}

          {/* Tips */}
          <div className="glass-card p-5">
            <p className="text-sm font-medium text-nexora-text mb-3">💡 Tips</p>
            <ul className="space-y-2 text-xs text-nexora-muted">
              <li>• Microphone access দিন browser এ</li>
              <li>• ভালো microphone ব্যবহার করলে accuracy বাড়বে</li>
              <li>• English ও Bengali উভয় ভাষায় কথা বলতে পারবেন</li>
              <li>• Background noise কম থাকলে ভালো result পাবেন</li>
            </ul>
          </div>

        </div>
      </div>
    </div>
  )
}
