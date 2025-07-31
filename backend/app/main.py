# backend/app/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import os
import uuid
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Import our services
from services.youtube_service import YouTubeService
from services.audio_service import AudioService
from services.translation_service import TranslationService
from services.tts_service import TTSService
from services.video_service import VideoService
from models.schemas import ProcessRequest, ProcessStatus, ProcessResponse
from core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="YouTube Video Translator",
    description="Translate YouTube videos to Thai with AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
os.makedirs("output", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="output"), name="static")

# Initialize services
youtube_service = YouTubeService()
audio_service = AudioService()
translation_service = TranslationService()
tts_service = TTSService()
video_service = VideoService()

# In-memory task storage (in production, use Redis)
tasks: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "YouTube Video Translator API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "youtube": "available",
            "translation": "available",
            "tts": "available",
            "ffmpeg": "available"
        }
    }

@app.post("/process-video/", response_model=ProcessResponse)
async def process_video(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    """
    Start processing a YouTube video
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        tasks[task_id] = {
            "id": task_id,
            "status": "queued",
            "progress": 0,
            "message": "Task queued for processing",
            "youtube_url": request.youtube_url,
            "target_language": request.target_language,
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
        
        # Add background task
        background_tasks.add_task(
            process_youtube_video_pipeline,
            task_id,
            request.youtube_url,
            request.target_language
        )
        
        logger.info(f"Started processing task {task_id} for URL: {request.youtube_url}")
        
        return ProcessResponse(
            task_id=task_id,
            status="queued",
            message="Video processing started"
        )
        
    except Exception as e:
        logger.error(f"Error starting video processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")

@app.get("/status/{task_id}", response_model=ProcessStatus)
async def get_task_status(task_id: str):
    """
    Get processing status for a task
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    return ProcessStatus(**task)

@app.get("/download/{task_id}")
async def download_result(task_id: str):
    """
    Download the processed video
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    output_file = f"output/final_{task_id}.mp4"
    if not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        path=output_file,
        filename=f"translated_video_{task_id}.mp4",
        media_type="video/mp4"
    )

@app.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """
    Delete a task and its associated files
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Clean up files
    files_to_clean = [
        f"uploads/video_{task_id}.mp4",
        f"uploads/audio_{task_id}.wav",
        f"uploads/transcript_{task_id}.json",
        f"uploads/translated_{task_id}.txt",
        f"uploads/thai_audio_{task_id}.wav",
        f"output/final_{task_id}.mp4"
    ]
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Remove task from memory
    del tasks[task_id]
    
    return {"message": "Task deleted successfully"}

async def process_youtube_video_pipeline(
    task_id: str,
    youtube_url: str,
    target_language: str = "th"
):
    """
    Main processing pipeline for YouTube video translation
    """
    try:
        logger.info(f"Starting pipeline for task {task_id}")
        
        # Update task status
        def update_task_status(status: str, progress: int, message: str, step: str = None):
            tasks[task_id]["status"] = status
            tasks[task_id]["progress"] = progress
            tasks[task_id]["message"] = message
            tasks[task_id]["updated_at"] = datetime.now().isoformat()
            
            if step:
                tasks[task_id]["steps"][step]["status"] = "completed" if progress == 100 else "processing"
                tasks[task_id]["steps"][step]["progress"] = progress
        
        # Step 1: Download YouTube video
        update_task_status("processing", 10, "Downloading YouTube video...", "download")
        video_path = await youtube_service.download_video(youtube_url, task_id)
        update_task_status("processing", 20, "Video downloaded successfully", "download")
        
        # Step 2: Extract audio
        update_task_status("processing", 30, "Extracting audio from video...", "extract_audio")
        audio_path = await audio_service.extract_audio(video_path, task_id)
        update_task_status("processing", 40, "Audio extracted successfully", "extract_audio")
        
        # Step 3: Speech to text
        update_task_status("processing", 50, "Converting speech to text...", "speech_to_text")
        transcript = await audio_service.speech_to_text(audio_path, task_id)
        update_task_status("processing", 60, "Speech converted to text", "speech_to_text")
        
        # Step 4: Translate text
        update_task_status("processing", 70, "Translating text to Thai...", "translate")
        translated_text = await translation_service.translate(transcript, target_language)
        update_task_status("processing", 80, "Text translated successfully", "translate")
        
        # Step 5: Text to speech
        update_task_status("processing", 85, "Converting Thai text to speech...", "text_to_speech")
        thai_audio_path = await tts_service.text_to_speech(translated_text, task_id)
        update_task_status("processing", 90, "Thai audio generated", "text_to_speech")
        
        # Step 6: Merge audio with video
        update_task_status("processing", 95, "Merging audio with video...", "merge_video")
        final_video_path = await video_service.merge_audio_video(
            video_path, thai_audio_path, task_id
        )
        update_task_status("completed", 100, "Video processing completed!", "merge_video")
        
        # Store final result
        tasks[task_id]["result_file"] = final_video_path
        tasks[task_id]["download_url"] = f"/download/{task_id}"
        
        logger.info(f"Pipeline completed successfully for task {task_id}")
        
    except Exception as e:
        logger.error(f"Pipeline failed for task {task_id}: {str(e)}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"Processing failed: {str(e)}"
        tasks[task_id]["error"] = str(e)

# WebSocket endpoint for real-time updates (optional)
@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket, task_id: str):
    """
    WebSocket endpoint for real-time task updates
    """
    await websocket.accept()
    
    try:
        while True:
            if task_id in tasks:
                task_data = tasks[task_id]
                await websocket.send_json(task_data)
                
                # Close connection if task is completed or failed
                if task_data["status"] in ["completed", "failed"]:
                    break
            
            await asyncio.sleep(2)  # Update every 2 seconds
            
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {str(e)}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )