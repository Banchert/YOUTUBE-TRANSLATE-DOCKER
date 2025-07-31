# backend/app/services/audio_service.py
import os
import asyncio
import subprocess
import json
import logging
import tempfile
import requests
from typing import Dict, Any, List, Optional
import whisper
from core.config import settings

logger = logging.getLogger(__name__)

class AudioService:
    """Service for audio processing and speech-to-text"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.whisper_model = None
        self.load_whisper_model()
    
    def load_whisper_model(self):
        """Load Whisper model for speech recognition"""
        try:
            model_name = settings.WHISPER_MODEL
            logger.info(f"Loading Whisper model: {model_name}")
            self.whisper_model = whisper.load_model(model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            self.whisper_model = None
    
    async def extract_audio(self, video_path: str, task_id: str) -> str:
        """
        Extract audio from video using FFmpeg
        """
        try:
            logger.info(f"Extracting audio from video for task {task_id}")
            
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Output audio file path
            audio_path = os.path.join(self.upload_dir, f"audio_{task_id}.wav")
            
            # FFmpeg command for audio extraction
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # PCM 16-bit
                '-ar', '16000',  # 16kHz sample rate (optimal for Whisper)
                '-ac', '1',  # Mono channel
                '-y',  # Overwrite output file
                audio_path
            ]
            
            # Run FFmpeg
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown FFmpeg error"
                logger.error(f"FFmpeg audio extraction failed: {error_msg}")
                raise Exception(f"Audio extraction failed: {error_msg}")
            
            if not os.path.exists(audio_path):
                raise Exception("Audio file was not created")
            
            logger.info(f"Audio extracted successfully: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"Audio extraction failed for task {task_id}: {str(e)}")
            raise Exception(f"Failed to extract audio: {str(e)}")
    
    async def speech_to_text(self, audio_path: str, task_id: str) -> str:
        """
        Convert speech to text using Whisper
        """
        try:
            logger.info(f"Starting speech-to-text for task {task_id}")
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            if self.whisper_model is None:
                # Try to reload the model
                self.load_whisper_model()
                if self.whisper_model is None:
                    raise Exception("Whisper model not available")
            
            # Transcribe audio
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.whisper_model.transcribe, audio_path
            )
            
            # Extract transcript text
            transcript = result["text"].strip()
            
            if not transcript:
                raise Exception("No speech detected in audio")
            
            # Save transcript details
            transcript_path = os.path.join(self.upload_dir, f"transcript_{task_id}.json")
            transcript_data = {
                "text": transcript,
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "duration": self._get_audio_duration(audio_path)
            }
            
            with open(transcript_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Speech-to-text completed for task {task_id}")
            logger.info(f"Detected language: {result.get('language', 'unknown')}")
            logger.info(f"Transcript length: {len(transcript)} characters")
            
            return transcript
            
        except Exception as e:
            logger.error(f"Speech-to-text failed for task {task_id}: {str(e)}")
            raise Exception(f"Failed to convert speech to text: {str(e)}")
    
    async def speech_to_text_with_timestamps(self, audio_path: str, task_id: str) -> Dict[str, Any]:
        """
        Convert speech to text with detailed timestamps
        """
        try:
            logger.info(f"Starting detailed speech-to-text for task {task_id}")
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            if self.whisper_model is None:
                self.load_whisper_model()
                if self.whisper_model is None:
                    raise Exception("Whisper model not available")
            
            # Transcribe with word-level timestamps
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.whisper_model.transcribe(
                    audio_path, 
                    word_timestamps=True,
                    verbose=False
                )
            )
            
            # Process segments with timestamps
            processed_segments = []
            for segment in result.get("segments", []):
                processed_segment = {
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "text": segment.get("text", "").strip(),
                    "confidence": segment.get("avg_logprob", 0),
                    "words": segment.get("words", [])
                }
                processed_segments.append(processed_segment)
            
            transcript_data = {
                "full_text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": processed_segments,
                "duration": self._get_audio_duration(audio_path)
            }
            
            # Save detailed transcript
            transcript_path = os.path.join(self.upload_dir, f"detailed_transcript_{task_id}.json")
            with open(transcript_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, ensure_ascii=False, indent=2)
            
            return transcript_data
            
        except Exception as e:
            logger.error(f"Detailed speech-to-text failed for task {task_id}: {str(e)}")
            raise Exception(f"Failed to convert speech to text with timestamps: {str(e)}")
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """
        Get audio duration using ffprobe
        """
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Could not get audio duration: {result.stderr}")
                return 0.0
            
            probe_data = json.loads(result.stdout)
            duration = float(probe_data['format']['duration'])
            
            return duration
            
        except Exception as e:
            logger.warning(f"Failed to get audio duration: {str(e)}")
            return 0.0
    
    async def enhance_audio_quality(self, audio_path: str, task_id: str) -> str:
        """
        Enhance audio quality for better speech recognition
        """
        try:
            logger.info(f"Enhancing audio quality for task {task_id}")
            
            enhanced_path = os.path.join(self.upload_dir, f"enhanced_audio_{task_id}.wav")
            
            # FFmpeg command for audio enhancement
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-af', 'highpass=f=80,lowpass=f=8000,volume=2.0',  # Filter chain
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',      # Mono
                '-y',
                enhanced_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.warning(f"Audio enhancement failed, using original: {stderr.decode()}")
                return audio_path
            
            logger.info(f"Audio enhanced successfully: {enhanced_path}")
            return enhanced_path
            
        except Exception as e:
            logger.warning(f"Audio enhancement failed, using original: {str(e)}")
            return audio_path
    
    async def split_audio_for_processing(self, audio_path: str, task_id: str, chunk_duration: int = 300) -> List[str]:
        """
        Split long audio files into smaller chunks for processing
        """
        try:
            duration = self._get_audio_duration(audio_path)
            
            if duration <= chunk_duration:
                return [audio_path]
            
            logger.info(f"Splitting audio into chunks for task {task_id}")
            
            chunks = []
            chunk_count = int(duration // chunk_duration) + 1
            
            for i in range(chunk_count):
                start_time = i * chunk_duration
                chunk_path = os.path.join(self.upload_dir, f"chunk_{task_id}_{i}.wav")
                
                cmd = [
                    'ffmpeg',
                    '-i', audio_path,
                    '-ss', str(start_time),
                    '-t', str(chunk_duration),
                    '-c', 'copy',
                    '-y',
                    chunk_path
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                await process.communicate()
                
                if process.returncode == 0 and os.path.exists(chunk_path):
                    chunks.append(chunk_path)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Audio splitting failed: {str(e)}")
            return [audio_path]
    
    async def cleanup_audio_files(self, task_id: str):
        """
        Clean up audio files for a task
        """
        try:
            files_to_clean = [
                f"audio_{task_id}.wav",
                f"enhanced_audio_{task_id}.wav",
                f"transcript_{task_id}.json",
                f"detailed_transcript_{task_id}.json"
            ]
            
            # Also clean up any audio chunks
            for i in range(10):  # Assume max 10 chunks
                files_to_clean.append(f"chunk_{task_id}_{i}.wav")
            
            for filename in files_to_clean:
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up audio file: {file_path}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up audio files for task {task_id}: {str(e)}")