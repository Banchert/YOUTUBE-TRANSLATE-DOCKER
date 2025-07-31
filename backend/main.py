# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
from typing import Optional
import asyncio

# Create FastAPI app
app = FastAPI(
    title="YouTube Video Translator",
    description="AI-powered video translation service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task storage
tasks = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "YouTube Video Translator API",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    # Test Whisper
    whisper_status = "unknown"
    try:
        import whisper
        whisper_status = "available"
    except Exception as e:
        whisper_status = f"error: {str(e)}"
    
    # Test TTS
    tts_status = "unknown"
    try:
        from TTS.api import TTS
        tts_status = "available"
    except Exception as e:
        tts_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "backend": "running",
            "whisper": whisper_status,
            "tts": tts_status
        }
    }

@app.get("/test-whisper")
async def test_whisper():
    """Test Whisper installation and model loading"""
    try:
        import whisper
        
        # Load smallest model for testing
        print("Loading Whisper base model...")
        model = whisper.load_model("base")
        
        return {
            "status": "success", 
            "message": "Whisper base model loaded successfully!",
            "model": "base"
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Whisper error: {str(e)}"
        }

@app.get("/test-tts")
async def test_tts():
    """Test TTS installation"""
    try:
        from TTS.api import TTS
        
        # Get available models
        models = TTS.list_models()
        
        # Find English models (more reliable)
        english_models = [m for m in models if 'en/' in m and 'ljspeech' in m]
        
        if english_models:
            test_model = english_models[0]
            return {
                "status": "success",
                "message": "TTS is working!",
                "available_models": len(models),
                "test_model": test_model,
                "note": "Thai models not available, using English models"
            }
        else:
            return {
                "status": "partial",
                "message": "TTS installed but no suitable models found",
                "available_models": len(models)
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"TTS error: {str(e)}"
        }

@app.get("/list-tts-models")
async def list_tts_models():
    """List all available TTS models"""
    try:
        from TTS.api import TTS
        models = TTS.list_models()
        
        # Group by language
        grouped_models = {}
        for model in models:
            lang = model.split('/')[1] if '/' in model else 'unknown'
            if lang not in grouped_models:
                grouped_models[lang] = []
            grouped_models[lang].append(model)
        
        return {
            "total_models": len(models),
            "grouped_by_language": grouped_models,
            "thai_available": 'th' in grouped_models
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/process-video/")
async def process_video(request: dict):
    """Process video endpoint (mock for testing)"""
    try:
        youtube_url = request.get("youtube_url")
        target_language = request.get("target_language", "th")
        
        if not youtube_url:
            raise HTTPException(status_code=400, detail="youtube_url is required")
        
        # Validate YouTube URL
        if "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Store task
        tasks[task_id] = {
            "id": task_id,
            "status": "queued",
            "progress": 0,
            "message": "Task created successfully - DEMO MODE",
            "youtube_url": youtube_url,
            "target_language": target_language,
            "created_at": datetime.now().isoformat(),
            "steps": {
                "download": {"status": "pending", "progress": 0},
                "extract_audio": {"status": "pending", "progress": 0},
                "speech_to_text": {"status": "pending", "progress": 0},
                "translate": {"status": "pending", "progress": 0},
                "text_to_speech": {"status": "pending", "progress": 0},
                "merge_video": {"status": "pending", "progress": 0}
            }
        }
        
        # Start mock processing (for demo)
        asyncio.create_task(mock_process_video(task_id))
        
        return {
            "task_id": task_id,
            "status": "queued",
            "message": "Video processing started (DEMO MODE)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def mock_process_video(task_id: str):
    """Mock video processing for demo"""
    try:
        steps = ["download", "extract_audio", "speech_to_text", "translate", "text_to_speech", "merge_video"]
        
        for i, step in enumerate(steps):
            await asyncio.sleep(2)  # Simulate processing time
            
            progress = int(((i + 1) / len(steps)) * 100)
            
            tasks[task_id]["status"] = "processing"
            tasks[task_id]["progress"] = progress
            tasks[task_id]["message"] = f"Processing step: {step}"
            tasks[task_id]["steps"][step] = {"status": "completed", "progress": 100}
        
        # Mark as completed
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["message"] = "Video processing completed (DEMO)"
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"Processing failed: {str(e)}"

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get task status"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]

@app.get("/tasks")
async def list_tasks():
    """List all tasks"""
    return {"tasks": list(tasks.values()), "total": len(tasks)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting YouTube Video Translator Backend...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)