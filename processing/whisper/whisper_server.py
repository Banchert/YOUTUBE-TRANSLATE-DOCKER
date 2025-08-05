#!/usr/bin/env python3
import os
import tempfile
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import requests
import json
import torch
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Whisper Speech-to-Text Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Try to load Whisper model (lazy loading)
whisper_model = None

def get_device():
    """Get the best available device (CUDA GPU or CPU)"""
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"

def get_whisper_model():
    global whisper_model
    if whisper_model is None:
        try:
            import whisper
            model_name = os.getenv("WHISPER_MODEL", "medium")
            device = get_device()
            logger.info(f"Loading Whisper model: {model_name} on {device}")
            whisper_model = whisper.load_model(model_name).to(device)
            logger.info(f"Whisper model loaded successfully on {device}")
        except ImportError:
            logger.warning("Whisper not available, will use external API")
            whisper_model = "api_only"
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            whisper_model = "api_only"
    return whisper_model

def transcribe_with_api(audio_path):
    """Transcribe using external API as fallback"""
    try:
        # This is a placeholder for external API integration
        # You can integrate with OpenAI Whisper API, Google Speech-to-Text, etc.
        
        # For demo purposes, return mock transcription
        return {
            "text": "สวัสดีครับ นี่คือการแปลงเสียงเป็นข้อความแบบจำลอง",
            "language": "th",
            "segments": [
                {
                    "start": 0.0,
                    "end": 5.0,
                    "text": "สวัสดีครับ นี่คือการแปลงเสียงเป็นข้อความแบบจำลอง"
                }
            ]
        }
    except Exception as e:
        logger.error(f"API transcription failed: {e}")
        raise HTTPException(status_code=500, detail="Transcription API failed")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model = get_whisper_model()
    device = get_device()
    gpu_info = None
    
    if device == "cuda":
        gpu_info = {
            "name": torch.cuda.get_device_name(0),
            "memory_allocated": f"{torch.cuda.memory_allocated(0) / 1024**2:.1f}MB",
            "memory_total": f"{torch.cuda.get_device_properties(0).total_memory / 1024**2:.1f}MB"
        }
    
    return {
        "status": "healthy",
        "model_type": "local" if model != "api_only" else "api",
        "device": device,
        "gpu_info": gpu_info,
        "available_models": ["tiny", "base", "small", "medium", "large"]
    }

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...), use_gpu: Optional[bool] = True):
    """Transcribe audio file to text"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        logger.info(f"Transcribing audio file: {file.filename} (GPU: {use_gpu})")
        
        # Get model
        model = get_whisper_model()
        
        if model == "api_only":
            # Use external API
            result = transcribe_with_api(temp_path)
        else:
            # Use local Whisper model
            device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
            if device != model.device:
                model = model.to(device)
            result = model.transcribe(temp_path)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", []),
            "file_processed": file.filename,
            "transcription_method": "local" if model != "api_only" else "api",
            "device_used": str(model.device) if model != "api_only" else "api"
        }
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/transcribe_url")
async def transcribe_from_url(audio_url: str, use_gpu: Optional[bool] = True):
    """Transcribe audio from URL"""
    try:
        logger.info(f"Transcribing from URL: {audio_url} (GPU: {use_gpu})")
        
        # Download audio file
        response = requests.get(audio_url)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        # Get model and transcribe
        model = get_whisper_model()
        
        if model == "api_only":
            result = transcribe_with_api(temp_path)
        else:
            device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
            if device != model.device:
                model = model.to(device)
            result = model.transcribe(temp_path)
        
        # Clean up
        os.unlink(temp_path)
        
        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", []),
            "source_url": audio_url,
            "transcription_method": "local" if model != "api_only" else "api",
            "device_used": str(model.device) if model != "api_only" else "api"
        }
        
    except Exception as e:
        logger.error(f"URL transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"URL transcription failed: {str(e)}")

@app.post("/transcribe_batch")
async def transcribe_batch(files: list[UploadFile] = File(...), use_gpu: Optional[bool] = True):
    """Transcribe multiple audio files"""
    try:
        results = []
        
        for i, file in enumerate(files):
            try:
                result = await transcribe_audio(file, use_gpu=use_gpu)
                results.append({
                    "index": i,
                    "filename": file.filename,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "index": i,
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "batch_results": results,
            "total_files": len(files),
            "successful": len([r for r in results if r["success"]]),
            "failed": len([r for r in results if not r["success"]]),
            "device_used": str(get_whisper_model().device) if get_whisper_model() != "api_only" else "api"
        }
        
    except Exception as e:
        logger.error(f"Batch transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch transcription failed: {str(e)}")

@app.get("/languages")
async def get_supported_languages():
    """Get supported languages for transcription"""
    return {
        "supported_languages": [
            {"code": "th", "name": "Thai", "native": "ไทย"},
            {"code": "en", "name": "English", "native": "English"},
            {"code": "zh", "name": "Chinese", "native": "中文"},
            {"code": "ja", "name": "Japanese", "native": "日本語"},
            {"code": "ko", "name": "Korean", "native": "한국어"},
            {"code": "es", "name": "Spanish", "native": "Español"},
            {"code": "fr", "name": "French", "native": "Français"},
            {"code": "de", "name": "German", "native": "Deutsch"},
            {"code": "auto", "name": "Auto-detect", "native": "Auto-detect"}
        ],
        "total_languages": 9,
        "auto_detection": True,
        "gpu_available": torch.cuda.is_available()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)