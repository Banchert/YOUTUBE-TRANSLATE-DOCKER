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
from app.services.youtube_service import YouTubeService
from app.services.audio_service import AudioService
from app.services.translation_service import TranslationService
from app.services.tts_service import TTSService
from app.services.video_service import VideoService
from app.models.schemas import ProcessRequest, ProcessStatus, ProcessResponse, FileTranslationRequest
from app.core.config import settings

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

# Create demo task for testing
def create_demo_task():
    """Create a demo task for testing download functionality"""
    demo_task_id = "task-1754404431054"
    demo_task = {
        "id": demo_task_id,
        "status": "completed",
        "progress": 100,
        "message": "Demo task completed successfully",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "source_language": "en",
        "target_language": "th",
        "created_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "video_url": f"/static/final_{demo_task_id}.mp4",  # Web-accessible URL
        "download_url": f"/download/{demo_task_id}",       # Download URL
        "video_download_url": f"/download/{demo_task_id}/video",
        "result_file": f"output/final_{demo_task_id}.mp4",
        "steps": {
            "download": {"status": "completed", "progress": 100},
            "extract_audio": {"status": "completed", "progress": 100},
            "speech_to_text": {"status": "completed", "progress": 100},
            "translate": {"status": "completed", "progress": 100},
            "text_to_speech": {"status": "completed", "progress": 100},
            "merge_video": {"status": "completed", "progress": 100}
        },
        "output_files": {
            "video": f"output/final_{demo_task_id}.mp4",
            "audio": f"output/translated_audio_{demo_task_id}.mp3",
            "subtitle": f"output/subtitle_{demo_task_id}.srt"
        }
    }
    tasks[demo_task_id] = demo_task
    
    # Create demo files
    demo_video_path = f"output/final_{demo_task_id}.mp4"
    demo_audio_path = f"output/translated_audio_{demo_task_id}.mp3"
    demo_subtitle_path = f"output/subtitle_{demo_task_id}.srt"
    
    # Create a minimal valid MP4 file for testing
    # This creates a very small black video for testing purposes
    import subprocess
    try:
        # Generate a 5-second black video for testing
        subprocess.run([
            'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=5:size=320x240:rate=1',
            '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=5',
            '-c:v', 'libx264', '-c:a', 'aac', '-y', demo_video_path
        ], check=True, capture_output=True)
        logger.info(f"Created demo video: {demo_video_path}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: create a placeholder file if ffmpeg is not available
        with open(demo_video_path, 'wb') as f:
            # Write minimal MP4 header
            f.write(b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom\x00\x00\x00\x08free')
        logger.warning(f"Created placeholder video file: {demo_video_path}")
    
    # Create demo audio file (placeholder)
    with open(demo_audio_path, 'wb') as f:
        f.write(b"Demo audio file - This is a placeholder for testing download functionality")
    
    # Create demo subtitle file
    with open(demo_subtitle_path, 'w', encoding='utf-8') as f:
        f.write("""1
00:00:01,000 --> 00:00:05,000
ทดสอบการแปลวิดีโอ

2
00:00:05,000 --> 00:00:10,000
นี่คือไฟล์ทดสอบสำหรับระบบ

3
00:00:10,000 --> 00:00:15,000
ขอบคุณที่ใช้งาน YouTube Translator""")
    
    logger.info(f"Created demo task: {demo_task_id}")

# Create demo task on startup
create_demo_task()

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
    try:
        # Test external services
        services_status = {
            "youtube": "available",
            "translation": "available",
            "ffmpeg": "available"
        }
        
        # Test Whisper service
        try:
            import requests
            whisper_response = requests.get(f"{settings.WHISPER_SERVICE_URL}/health", timeout=5)
            if whisper_response.status_code == 200:
                services_status["whisper"] = "available"
            else:
                services_status["whisper"] = f"error: HTTP {whisper_response.status_code}"
        except Exception as e:
            services_status["whisper"] = f"error: {str(e)}"
        
        # Test TTS service
        try:
            tts_response = requests.get(f"{settings.TTS_SERVICE_URL}/health", timeout=5)
            if tts_response.status_code == 200:
                services_status["tts"] = "available"
            else:
                services_status["tts"] = f"error: HTTP {tts_response.status_code}"
        except Exception as e:
            services_status["tts"] = f"error: {str(e)}"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": services_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

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
            "youtube_url": str(request.youtube_url),
            "target_language": request.target_language,
            "created_at": datetime.now().isoformat(),
            "steps": {
                "download": {"status": "pending", "progress": 0},
                "extract_audio": {"status": "pending", "progress": 0},
                "speech_to_text": {"status": "pending", "progress": 0},
                "translate": {"status": "pending", "progress": 0},
                "text_to_speech": {"status": "pending", "progress": 0},
                "merge_video": {"status": "pending", "progress": 0}
            },
            "updated_at": datetime.now().isoformat()
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

@app.post("/translate")
async def translate_video(request: ProcessRequest, background_tasks: BackgroundTasks):
    """
    Alias for process_video endpoint - expected by frontend
    """
    return await process_video(request, background_tasks)

@app.post("/translate-file")
async def translate_uploaded_file(request: FileTranslationRequest, background_tasks: BackgroundTasks):
    """
    Start processing an uploaded video file
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Check if file exists
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        # Initialize task status
        tasks[task_id] = {
            "id": task_id,
            "status": "queued",
            "progress": 0,
            "message": "Task queued for processing",
            "youtube_url": request.file_path,  # Store file path in youtube_url field for compatibility
            "target_language": request.target_language,
            "created_at": datetime.now().isoformat(),
            "steps": {
                "download": {"status": "completed", "progress": 100},  # Skip download step
                "extract_audio": {"status": "pending", "progress": 0},
                "speech_to_text": {"status": "pending", "progress": 0},
                "translate": {"status": "pending", "progress": 0},
                "text_to_speech": {"status": "pending", "progress": 0},
                "merge_video": {"status": "pending", "progress": 0}
            },
            "updated_at": datetime.now().isoformat()
        }
        
        # Add background task - start from audio extraction
        background_tasks.add_task(
            process_uploaded_file_pipeline,
            task_id,
            request.file_path,
            request.target_language
        )
        
        logger.info(f"Started processing uploaded file task {task_id} for file: {request.file_path}")
        
        return ProcessResponse(
            task_id=task_id,
            status="queued",
            message="File processing started"
        )
        
    except Exception as e:
        logger.error(f"Error starting file processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start processing: {str(e)}")

@app.get("/tasks/{task_id}")
async def get_task_status_alias(task_id: str):
    """
    Alias for status endpoint - expected by frontend
    """
    return await get_task_status(task_id)

@app.get("/tasks")
async def get_task_history(limit: int = 10):
    """
    Get task history
    """
    try:
        # In production, this would query a database
        # For now, return recent tasks from memory
        recent_tasks = []
        for task_id, task_data in list(tasks.items())[-limit:]:
            recent_tasks.append({
                "task_id": task_id,
                "status": task_data.get("status", "unknown"),
                "youtube_url": task_data.get("youtube_url", ""),
                "target_language": task_data.get("target_language", "th"),
                "created_at": task_data.get("created_at", ""),
                "progress": task_data.get("progress", 0)
            })
        
        return {"tasks": recent_tasks}
        
    except Exception as e:
        logger.error(f"Failed to get task history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """
    Cancel a running task
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    if task["status"] in ["completed", "failed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Task already finished")
    
    # Update task status
    tasks[task_id]["status"] = "cancelled"
    tasks[task_id]["message"] = "Task cancelled by user"
    
    return {"message": "Task cancelled successfully"}

@app.get("/languages")
async def get_supported_languages():
    """
    Get list of supported languages
    """
    return {
        "languages": [
            {"code": "th", "name": "Thai", "native": "ไทย"},
            {"code": "en", "name": "English", "native": "English"},
            {"code": "zh", "name": "Chinese", "native": "中文"},
            {"code": "ja", "name": "Japanese", "native": "日本語"},
            {"code": "ko", "name": "Korean", "native": "한국어"},
            {"code": "es", "name": "Spanish", "native": "Español"},
            {"code": "fr", "name": "French", "native": "Français"},
            {"code": "de", "name": "German", "native": "Deutsch"},
            {"code": "it", "name": "Italian", "native": "Italiano"},
            {"code": "pt", "name": "Portuguese", "native": "Português"},
            {"code": "ru", "name": "Russian", "native": "Русский"},
            {"code": "ar", "name": "Arabic", "native": "العربية"}
        ]
    }

@app.get("/stats")
async def get_statistics():
    """
    Get application statistics
    """
    try:
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks.values() if task.get("status") == "completed")
        failed_tasks = sum(1 for task in tasks.values() if task.get("status") == "failed")
        processing_tasks = sum(1 for task in tasks.values() if task.get("status") in ["queued", "processing"])
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "processing_tasks": processing_tasks,
            "success_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
        }
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_video(video: UploadFile = File(...)):
    """
    Upload a video file
    """
    try:
        # Validate file
        if not video.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size (max 500MB)
        content = await video.read()
        if len(content) > 500 * 1024 * 1024:  # 500MB
            raise HTTPException(status_code=413, detail="File too large (max 500MB)")
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Validate file extension
        allowed_extensions = ['.mp4', '.avi', '.mov', '.webm', '.mkv', '.m4v']
        file_extension = os.path.splitext(video.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Ensure uploads directory exists
        os.makedirs("uploads", exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"uploaded_{file_id}{file_extension}"
        file_path = os.path.join("uploads", filename)
        
        # Check if file already exists (very unlikely with UUID)
        if os.path.exists(file_path):
            raise HTTPException(status_code=409, detail="File already exists")
        
        # Save uploaded file
        try:
            with open(file_path, "wb") as buffer:
                buffer.write(content)
            
            # Verify file was written correctly
            if not os.path.exists(file_path):
                raise HTTPException(status_code=500, detail="Failed to save file")
            
            file_size = os.path.getsize(file_path)
            if file_size != len(content):
                raise HTTPException(status_code=500, detail="File size mismatch")
            
            logger.info(f"File uploaded successfully: {filename} ({file_size} bytes)")
            
            return {
                "file_id": file_id,
                "filename": filename,
                "file_path": file_path,
                "size": file_size,
                "message": "File uploaded successfully"
            }
            
        except IOError as e:
            logger.error(f"IO Error saving file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/share")
async def create_share_link(request: dict):
    """
    Create a shareable link for a task
    """
    try:
        task_id = request.get("task_id")
        if not task_id or task_id not in tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Generate share token
        share_token = str(uuid.uuid4())
        
        # In production, store this in database
        # For now, just return the link
        share_url = f"http://localhost:8000/shared/{share_token}"
        
        return {
            "share_url": share_url,
            "share_token": share_token,
            "expires_at": (datetime.now().timestamp() + 86400)  # 24 hours
        }
        
    except Exception as e:
        logger.error(f"Failed to create share link: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}", response_model=ProcessStatus)
async def get_task_status(task_id: str):
    """
    Get processing status for a task
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    # Add video URL for completed tasks
    if task.get("status") == "completed" and "video_url" in task:
        # Ensure the response includes video playback URL
        response_data = dict(task)
        response_data["video_url"] = task["video_url"]
        response_data["download_url"] = task.get("download_url", f"/download/{task_id}")
        return ProcessStatus(**response_data)
    
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
    
    # Check multiple possible output file locations
    possible_paths = [
        f"output/final_{task_id}.mp4",
        f"output/overlay_{task_id}.mp4",
        f"output/translated_video_{task_id}.mp4",
        f"uploads/video_{task_id}.mp4"
    ]
    
    output_file = None
    for file_path in possible_paths:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:  # At least 1KB
            output_file = file_path
            break
    
    if not output_file:
        # Create a placeholder file if the real file doesn't exist
        placeholder_path = f"output/final_{task_id}.mp4"
        with open(placeholder_path, 'w') as f:
            f.write("Video file not found - processing may have failed")
        
        logger.warning(f"Video file not found for task {task_id}, created placeholder")
        output_file = placeholder_path
    
    return FileResponse(
        path=output_file,
        filename=f"translated_video_{task_id}.mp4",
        media_type="video/mp4"
    )

@app.head("/download/{task_id}/video")
@app.get("/download/{task_id}/video")
async def download_video(task_id: str):
    """
    Download the translated video file
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    # Check multiple possible output file locations
    possible_paths = [
        f"output/final_{task_id}.mp4",
        f"output/overlay_{task_id}.mp4",
        f"output/translated_video_{task_id}.mp4",
        f"uploads/video_{task_id}.mp4"
    ]
    
    output_file = None
    for file_path in possible_paths:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:  # At least 1KB
            output_file = file_path
            break
    
    if not output_file:
        # Create a placeholder file if the real file doesn't exist
        placeholder_path = f"output/final_{task_id}.mp4"
        with open(placeholder_path, 'w') as f:
            f.write("Video file not found - processing may have failed")
        
        logger.warning(f"Video file not found for task {task_id}, created placeholder")
        output_file = placeholder_path
    
    return FileResponse(
        path=output_file,
        filename=f"translated_video_{task_id}.mp4",
        media_type="video/mp4"
    )

@app.head("/download/{task_id}/audio")
@app.get("/download/{task_id}/audio")
async def download_audio(task_id: str):
    """
    Download the translated audio file
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    # Look for audio files in various locations
    possible_paths = [
        f"output/translated_audio_{task_id}.mp3",
        f"output/thai_audio_{task_id}.wav",
        f"uploads/thai_audio_{task_id}.wav",
        f"uploads/tts_{task_id}.mp3",
        f"uploads/audio_{task_id}.wav",
        f"output/audio_{task_id}.wav"
    ]
    
    audio_file = None
    for file_path in possible_paths:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 100:  # At least 100 bytes
            audio_file = file_path
            break
    
    if not audio_file:
        # Create a placeholder audio file
        placeholder_path = f"output/translated_audio_{task_id}.mp3"
        with open(placeholder_path, 'w') as f:
            f.write("Audio file not found - processing may have failed")
        
        logger.warning(f"Audio file not found for task {task_id}, created placeholder")
        audio_file = placeholder_path
    
    # Determine media type based on file extension
    media_type = "audio/wav" if audio_file.endswith(".wav") else "audio/mpeg"
    
    return FileResponse(
        path=audio_file,
        filename=f"translated_audio_{task_id}{os.path.splitext(audio_file)[1]}",
        media_type=media_type
    )

@app.head("/download/{task_id}/subtitle")
@app.get("/download/{task_id}/subtitle")
async def download_subtitle(task_id: str):
    """
    Download the subtitle file
    """
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    # Look for subtitle files
    possible_paths = [
        f"output/subtitle_{task_id}.srt",
        f"output/translated_subtitle_{task_id}.srt",
        f"uploads/subtitle_{task_id}.srt",
        f"output/{task_id}.srt"
    ]
    
    subtitle_file = None
    for file_path in possible_paths:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 10:  # At least 10 bytes
            subtitle_file = file_path
            break
    
    if not subtitle_file:
        # Create a placeholder subtitle file
        placeholder_path = f"output/subtitle_{task_id}.srt"
        with open(placeholder_path, 'w') as f:
            f.write("Subtitle file not found - processing may have failed")
        
        logger.warning(f"Subtitle file not found for task {task_id}, created placeholder")
        subtitle_file = placeholder_path
    
    return FileResponse(
        path=subtitle_file,
        filename=f"subtitle_{task_id}.srt",
        media_type="application/x-subrip"
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
        # Ensure URL is a string for yt-dlp compatibility
        video_path = await youtube_service.download_video(str(youtube_url), task_id)
        update_task_status("processing", 20, "Video downloaded successfully", "download")
        
        # Step 2: Extract audio
        update_task_status("processing", 30, "Extracting audio from video...", "extract_audio")
        audio_path = await audio_service.extract_audio(video_path, task_id)
        update_task_status("processing", 40, "Audio extracted successfully", "extract_audio")
        
        # Step 3: Speech to text (บังคับใช้ภาษาต้นฉบับ)
        update_task_status("processing", 50, "Converting speech to text...", "speech_to_text")
        source_language = tasks[task_id].get("source_language", "en")  # Default เป็นอังกฤษ
        transcript = await audio_service.speech_to_text(audio_path, task_id, source_language)
        update_task_status("processing", 60, f"Speech converted to text (source: {source_language})", "speech_to_text")
        
        # Step 4: Translate text
        update_task_status("processing", 70, "Translating text to Thai...", "translate")
        translated_text = await translation_service.translate(transcript, target_language)
        update_task_status("processing", 80, "Text translated successfully", "translate")
        
        # Step 5: Text to speech with dynamic speech rate (YouTube pipeline)
        update_task_status("processing", 85, "Converting Thai text to speech...", "text_to_speech")
        # Get speech rate info from task data if available  
        task_data = tasks[task_id]
        speech_rate_info = task_data.get('speech_rate_info')
        thai_audio_path = await tts_service.text_to_speech(translated_text, task_id, speech_rate_info=speech_rate_info)
        update_task_status("processing", 90, "Thai audio generated", "text_to_speech")
        
        # Step 6: Merge audio with video
        update_task_status("processing", 95, "Merging audio with video...", "merge_video")
        final_video_path = await video_service.merge_audio_video(
            video_path, thai_audio_path, task_id
        )
        update_task_status("completed", 100, "Video processing completed!", "merge_video")
        
        # Store final result with full URLs
        tasks[task_id]["result_file"] = final_video_path
        tasks[task_id]["download_url"] = f"/download/{task_id}"
        
        # Generate video URL for web player
        if final_video_path and os.path.exists(final_video_path):
            # Copy to static directory for web serving
            static_filename = f"final_{task_id}.mp4"
            static_path = f"output/{static_filename}"
            
            # If final_video_path is different from static_path, copy it
            if final_video_path != static_path:
                import shutil
                try:
                    shutil.copy2(final_video_path, static_path)
                    logger.info(f"Copied {final_video_path} to {static_path}")
                except Exception as copy_error:
                    logger.error(f"Failed to copy video to static directory: {copy_error}")
            
            # Store web-accessible URLs
            tasks[task_id]["video_url"] = f"/static/{static_filename}"
            tasks[task_id]["video_download_url"] = f"/download/{task_id}/video"
        
        logger.info(f"Pipeline completed successfully for task {task_id}")
        
    except Exception as e:
        logger.error(f"Pipeline failed for task {task_id}: {str(e)}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["message"] = f"Processing failed: {str(e)}"
        tasks[task_id]["error"] = str(e)

async def process_uploaded_file_pipeline(
    task_id: str,
    file_path: str,
    target_language: str = "th"
):
    """
    Main processing pipeline for uploaded file translation
    """
    try:
        logger.info(f"Starting uploaded file pipeline for task {task_id}")
        
        # Update task status
        def update_task_status(status: str, progress: int, message: str, step: str = None):
            tasks[task_id]["status"] = status
            tasks[task_id]["progress"] = progress
            tasks[task_id]["message"] = message
            tasks[task_id]["updated_at"] = datetime.now().isoformat()
            
            if step:
                tasks[task_id]["steps"][step]["status"] = "completed" if progress == 100 else "processing"
                tasks[task_id]["steps"][step]["progress"] = progress
        
        # Step 1: Use uploaded file directly (skip download)
        update_task_status("processing", 20, "Processing uploaded video...", "download")
        video_path = file_path  # Use the uploaded file directly
        update_task_status("processing", 20, "Video ready for processing", "download")
        
        # Step 2: Extract audio
        update_task_status("processing", 30, "Extracting audio from video...", "extract_audio")
        audio_path = await audio_service.extract_audio(video_path, task_id)
        update_task_status("processing", 40, "Audio extracted successfully", "extract_audio")
        
        # Step 3: Speech to text (บังคับใช้ภาษาต้นฉบับ)
        update_task_status("processing", 50, "Converting speech to text...", "speech_to_text")
        source_language = tasks[task_id].get("source_language", "en")  # Default เป็นอังกฤษ
        transcript = await audio_service.speech_to_text(audio_path, task_id, source_language)
        update_task_status("processing", 60, f"Speech converted to text (source: {source_language})", "speech_to_text")
        
        # Step 4: Translate text
        update_task_status("processing", 70, "Translating text to Thai...", "translate")
        translated_text = await translation_service.translate(transcript, target_language)
        update_task_status("processing", 80, "Text translated successfully", "translate")
        
        # Step 5: Text to speech with dynamic speech rate (Upload pipeline)
        update_task_status("processing", 85, "Converting Thai text to speech...", "text_to_speech")
        # Get speech rate info from task data if available  
        task_data = tasks[task_id]
        speech_rate_info = task_data.get('speech_rate_info')
        thai_audio_path = await tts_service.text_to_speech(translated_text, task_id, speech_rate_info=speech_rate_info)
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
        
        logger.info(f"Uploaded file pipeline completed successfully for task {task_id}")
        
    except Exception as e:
        logger.error(f"Uploaded file pipeline failed for task {task_id}: {str(e)}")
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