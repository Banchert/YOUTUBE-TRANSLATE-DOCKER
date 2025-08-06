#!/usr/bin/env python3
import os
import tempfile
import uuid
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import logging
import edge_tts
from gtts import gTTS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TTS Text-to-Speech Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Available voices
EDGE_VOICES = {
    "th": "th-TH-PremwadeeNeural",  # Thai female voice
    "en": "en-US-JennyNeural",      # English female voice
    "zh": "zh-CN-XiaoxiaoNeural",   # Chinese female voice
    "ja": "ja-JP-NanamiNeural",     # Japanese female voice
    "ko": "ko-KR-SunHiNeural",      # Korean female voice
    "es": "es-ES-ElviraNeural",     # Spanish female voice
    "fr": "fr-FR-DeniseNeural",     # French female voice
    "de": "de-DE-KatjaNeural",      # German female voice
}

class TTSRequest(BaseModel):
    text: str
    language: str = "th"
    voice_type: str = "female"
    use_edge_tts: bool = True
    speech_rate: float = 0.85  # Dynamic speech rate from audio analysis

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "available_voices": list(EDGE_VOICES.keys()),
        "services": ["edge-tts", "google-tts"]
    }

@app.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """Synthesize speech from text"""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="No text provided")
        
        # Generate unique filename
        output_filename = f"tts_{uuid.uuid4().hex}.mp3"
        output_path = os.path.join("/app/uploads", output_filename)
        
        logger.info(f"Synthesizing text ({len(request.text)} chars) in {request.language} with speech_rate {request.speech_rate}")
        
        if request.use_edge_tts and request.language in EDGE_VOICES:
            # Use Microsoft Edge TTS with dynamic speech rate
            voice = EDGE_VOICES[request.language]
            
            # Add SSML for better speech control with dynamic rate
            ssml_text = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{request.language}">
                <voice name="{voice}">
                    <prosody rate="{request.speech_rate}" pitch="0%" volume="100%">
                        {request.text}
                    </prosody>
                </voice>
            </speak>
            """
            
            communicate = edge_tts.Communicate(ssml_text, voice)
            await communicate.save(output_path)
            logger.info(f"Used Edge TTS with voice {voice} and dynamic speed (rate={request.speech_rate})")
        else:
            # Fallback to Google TTS with slower speed
            tts = gTTS(text=request.text, lang=request.language[:2], slow=True)
            tts.save(output_path)
            logger.info(f"Used Google TTS with slow=True for better clarity")
        
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Failed to generate audio")
        
        # Get file size
        file_size = os.path.getsize(output_path)
        
        logger.info(f"TTS synthesis completed: {output_filename} ({file_size} bytes)")
        
        return {
            "audio_file": output_filename,
            "audio_path": output_path,
            "text_length": len(request.text),
            "file_size": file_size,
            "voice_used": EDGE_VOICES.get(request.language, "google-tts"),
            "language": request.language,
            "message": "Speech synthesis completed successfully"
        }
        
    except Exception as e:
        logger.error(f"TTS synthesis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(e)}")

@app.get("/download/{filename}")
async def download_audio(filename: str):
    """Download generated audio file"""
    try:
        file_path = os.path.join("/app/uploads", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            file_path,
            media_type="audio/mpeg",
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"File download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.get("/voices")
async def get_available_voices():
    """Get list of available voices"""
    try:
        voices = {}
        for lang, voice in EDGE_VOICES.items():
            voices[lang] = {
                "voice_id": voice,
                "language": lang,
                "gender": "female",
                "provider": "microsoft-edge"
            }
        
        return {
            "voices": voices,
            "total_voices": len(voices),
            "providers": ["microsoft-edge", "google-tts"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize-batch")
async def synthesize_batch(texts: list[str], language: str = "th"):
    """Synthesize multiple texts in batch"""
    try:
        results = []
        
        for i, text in enumerate(texts):
            if not text.strip():
                continue
                
            request = TTSRequest(text=text, language=language)
            result = await synthesize_speech(request)
            results.append({
                "index": i,
                "text": text,
                "result": result
            })
        
        return {
            "batch_results": results,
            "total_processed": len(results),
            "language": language
        }
        
    except Exception as e:
        logger.error(f"Batch synthesis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch synthesis failed: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5002))
    uvicorn.run(app, host="0.0.0.0", port=port)