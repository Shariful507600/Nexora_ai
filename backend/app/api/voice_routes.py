# ============================================
# NEXORA AI - Voice Routes
# ============================================
# Speech-to-Text ও Text-to-Speech endpoints।

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import tempfile
import uuid

from app.core.security import get_current_user_id
from app.core.logger import logger

router = APIRouter(prefix="/api/voice", tags=["Voice AI"])


# ============================================
# Speech to Text
# ============================================
@router.post("/speech-to-text")
async def speech_to_text(
    audio: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
):
    """
    Audio ফাইল থেকে text বের করে।
    SpeechRecognition library ব্যবহার করে।
    Google Speech API (free tier) ব্যবহার করে।
    """
    try:
        import speech_recognition as sr

        # Audio file save করা
        audio_content = await audio.read()
        temp_path = os.path.join(tempfile.gettempdir(), f"nexora_audio_{uuid.uuid4()}.wav")

        with open(temp_path, "wb") as f:
            f.write(audio_content)

        # Speech recognition
        recognizer = sr.Recognizer()

        with sr.AudioFile(temp_path) as source:
            # Noise reduction
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)

        # Google Speech-to-Text (free, no API key needed)
        try:
            text = recognizer.recognize_google(audio_data, language="bn-BD")
        except:
            # English fallback
            text = recognizer.recognize_google(audio_data, language="en-US")

        # Temp file clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

        logger.info(f"🎤 Speech recognized: {text[:50]}...")
        return {"text": text, "confidence": "high"}

    except Exception as e:
        logger.error(f"Speech-to-text error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Speech recognition করতে সমস্যা হয়েছে। আবার চেষ্টা করুন।"
        )


# ============================================
# Text to Speech
# ============================================
class TTSRequest(BaseModel):
    text: str
    language: str = "en"    # "en" or "bn"


@router.post("/text-to-speech")
async def text_to_speech(
    request: TTSRequest,
    user_id: int = Depends(get_current_user_id),
):
    """
    Text কে audio তে রূপান্তর করে।
    gTTS (Google Text-to-Speech) ব্যবহার করে।
    """
    try:
        from gtts import gTTS

        # Language mapping
        lang_map = {"en": "en", "bn": "bn"}
        lang = lang_map.get(request.language, "en")

        # TTS generate করা
        tts = gTTS(text=request.text, lang=lang, slow=False)

        # Temp file এ save করা
        audio_path = os.path.join(tempfile.gettempdir(), f"nexora_tts_{uuid.uuid4()}.mp3")
        tts.save(audio_path)

        logger.info(f"🔊 TTS generated for: {request.text[:50]}...")

        # Audio file return করা
        return FileResponse(
            audio_path,
            media_type="audio/mpeg",
            filename="nexora_response.mp3"
        )

    except Exception as e:
        logger.error(f"Text-to-speech error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Audio generate করতে সমস্যা হয়েছে।"
        )
