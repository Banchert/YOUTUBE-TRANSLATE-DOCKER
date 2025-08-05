# backend/app/services/audio_service.py
import os
import asyncio
import subprocess
import json
import logging
import tempfile
import requests
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class AudioService:
    """Service for audio processing and speech-to-text"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.whisper_service_url = settings.WHISPER_SERVICE_URL
    
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
        Convert speech to text using external Whisper service
        """
        try:
            logger.info(f"Starting speech-to-text for task {task_id}")
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Call external Whisper service
            url = f"{self.whisper_service_url}/transcribe"
            
            with open(audio_path, 'rb') as audio_file:
                files = {'file': audio_file}
                response = requests.post(url, files=files)
                
                if response.status_code != 200:
                    raise Exception(f"Whisper service error: {response.text}")
                
                result = response.json()
                transcript = result.get('text', '')
                
                # Save transcript to file
                transcript_path = os.path.join(self.upload_dir, f"transcript_{task_id}.json")
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Speech-to-text completed for task {task_id}")
                return transcript
                
        except Exception as e:
            logger.error(f"Speech-to-text failed for task {task_id}: {str(e)}")
            raise Exception(f"Failed to convert speech to text: {str(e)}")
    
    async def speech_to_text_with_timestamps(self, audio_path: str, task_id: str) -> Dict[str, Any]:
        """
        Convert speech to text with timestamps using external Whisper service
        """
        try:
            logger.info(f"Starting speech-to-text with timestamps for task {task_id}")
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Call external Whisper service
            url = f"{self.whisper_service_url}/transcribe"
            
            with open(audio_path, 'rb') as audio_file:
                files = {'file': audio_file}
                response = requests.post(url, files=files)
                
                if response.status_code != 200:
                    raise Exception(f"Whisper service error: {response.text}")
                
                result = response.json()
                
                # Save transcript to file
                transcript_path = os.path.join(self.upload_dir, f"transcript_{task_id}.json")
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Speech-to-text with timestamps completed for task {task_id}")
                return result
                
        except Exception as e:
            logger.error(f"Speech-to-text with timestamps failed for task {task_id}: {str(e)}")
            raise Exception(f"Failed to convert speech to text with timestamps: {str(e)}")
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """
        Get audio duration using FFprobe
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                logger.warning(f"Could not get audio duration: {result.stderr}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error getting audio duration: {str(e)}")
            return 0.0
    
    async def enhance_audio_quality(self, audio_path: str, task_id: str) -> str:
        """
        Enhance audio quality using FFmpeg
        """
        try:
            logger.info(f"Enhancing audio quality for task {task_id}")
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Output enhanced audio file path
            enhanced_path = os.path.join(self.upload_dir, f"enhanced_audio_{task_id}.wav")
            
            # FFmpeg command for audio enhancement
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-af', 'highpass=f=200,lowpass=f=3000,volume=1.5',  # Basic enhancement
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',  # Mono channel
                '-y',  # Overwrite output file
                enhanced_path
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
                logger.error(f"FFmpeg audio enhancement failed: {error_msg}")
                # Return original file if enhancement fails
                return audio_path
            
            if not os.path.exists(enhanced_path):
                logger.warning("Enhanced audio file was not created, using original")
                return audio_path
            
            logger.info(f"Audio enhancement completed: {enhanced_path}")
            return enhanced_path
            
        except Exception as e:
            logger.error(f"Audio enhancement failed for task {task_id}: {str(e)}")
            # Return original file if enhancement fails
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
        Clean up temporary audio files
        """
        try:
            files_to_clean = [
                f"audio_{task_id}.wav",
                f"enhanced_audio_{task_id}.wav",
                f"transcript_{task_id}.json"
            ]
            
            # Also clean up chunks
            import glob
            chunk_pattern = f"chunk_{task_id}_*.wav"
            chunk_files = glob.glob(os.path.join(self.upload_dir, chunk_pattern))
            files_to_clean.extend([os.path.basename(f) for f in chunk_files])
            
            for filename in files_to_clean:
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up audio file: {filename}")
                    
        except Exception as e:
            logger.error(f"Failed to cleanup audio files for task {task_id}: {str(e)}")