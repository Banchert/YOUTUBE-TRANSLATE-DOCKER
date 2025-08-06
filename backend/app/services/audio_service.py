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
    
    async def speech_to_text(self, audio_path: str, task_id: str, source_language: str = "en") -> str:
        """
        Convert speech to text using external Whisper service
        Fixed: บังคับให้ใช้ภาษาต้นฉบับที่กำหนด แทนการ auto-detect
        Enhanced: วิเคราะห์ความเร็วเสียงเพื่อปรับ TTS
        """
        try:
            logger.info(f"Starting speech-to-text for task {task_id} with language: {source_language}")
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Analyze audio for speech rate detection FIRST
            speech_rate_info = await self._analyze_speech_rate(audio_path)
            logger.info(f"Speech rate analysis: {speech_rate_info}")
            
            # Store speech rate info for TTS adjustment
            from app.main import tasks  # Import here to avoid circular import
            if task_id in tasks:
                tasks[task_id]["speech_rate_info"] = speech_rate_info
            
            # Call external Whisper service with explicit language
            url = f"{self.whisper_service_url}/transcribe"
            
            with open(audio_path, 'rb') as audio_file:
                files = {'file': audio_file}
                data = {
                    'language': source_language,  # บังคับภาษาต้นฉบับ
                    'task': 'transcribe'  # ไม่ใช่ translate
                }
                
                logger.info(f"Sending to Whisper with FORCED language: {source_language}")
                response = requests.post(url, files=files, data=data)
                
                if response.status_code != 200:
                    raise Exception(f"Whisper service error: {response.text}")
                
                result = response.json()
                transcript = result.get('text', '')
                detected_language = result.get('language', source_language)
                
                # Validate language enforcement
                if detected_language != source_language:
                    logger.warning(f"Language mismatch! Requested: {source_language}, Detected: {detected_language}")
                    logger.warning("This may indicate the source language setting is incorrect")
                
                # บันทึกข้อมูลการถอดเสียง
                transcript_data = {
                    'text': transcript,
                    'language': detected_language,
                    'requested_language': source_language,
                    'task_id': task_id,
                    'segments': result.get('segments', [])
                }
                
                # Save transcript to file
                transcript_path = os.path.join(self.upload_dir, f"transcript_{task_id}.json")
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    json.dump(transcript_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Speech-to-text completed for task {task_id}. Detected: {detected_language}, Text length: {len(transcript)}")
                
                # ตรวจสอบว่าภาษาที่ตรวจพบตรงกับที่ต้องการหรือไม่
                if detected_language != source_language:
                    logger.warning(f"Language mismatch! Requested: {source_language}, Detected: {detected_language}")
                
                return transcript
                
        except Exception as e:
            logger.error(f"Speech-to-text failed for task {task_id}: {str(e)}")
            raise Exception(f"Failed to convert speech to text: {str(e)}")
    
    async def _analyze_speech_rate(self, audio_path: str) -> dict:
        """
        Analyze speech rate from audio file to determine optimal TTS speed
        Returns speed adjustment info for TTS
        """
        try:
            # Try to use librosa for audio analysis
            try:
                import librosa
                import numpy as np
                
                # Load audio file
                y, sr = librosa.load(audio_path, sr=22050)
                duration = librosa.get_duration(y=y, sr=sr)
                
                # Detect voice activity using RMS energy
                rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
                rms_threshold = np.percentile(rms, 30)  # 30th percentile as threshold
                
                # Count frames with voice activity
                voice_frames = np.sum(rms > rms_threshold)
                total_frames = len(rms)
                voice_ratio = voice_frames / total_frames if total_frames > 0 else 0
                
                # Estimate speech segments
                speech_duration = duration * voice_ratio
                
                # Calculate tempo using onset detection
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                
                # Estimate speaking rate (rough calculation)
                if speech_duration > 0:
                    # Estimate syllables based on tempo and duration
                    estimated_syllables = (tempo * speech_duration) / 60 * 2  # rough estimation
                    estimated_words = estimated_syllables / 2   # ~2 syllables per word average
                    words_per_minute = (estimated_words / speech_duration) * 60 if speech_duration > 0 else 120
                else:
                    words_per_minute = 120  # default
                
                analysis_method = "librosa_advanced"
                
            except ImportError:
                logger.warning("librosa not available, using basic audio analysis")
                # Fallback to basic file analysis
                import wave
                
                with wave.open(audio_path, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    sample_rate = wav_file.getframerate()
                    duration = frames / float(sample_rate)
                
                # Basic estimation without advanced audio processing
                voice_ratio = 0.7  # assume 70% of audio contains speech
                speech_duration = duration * voice_ratio
                words_per_minute = 120  # default WPM
                tempo = 120
                analysis_method = "basic_wave"
                
            # Determine TTS speed adjustment based on original speech rate
            if words_per_minute > 180:  # Very fast speech
                tts_rate = 0.6  # Slow down significantly
                speed_category = "very_fast"
            elif words_per_minute > 150:  # Fast speech
                tts_rate = 0.7  # Slow down considerably
                speed_category = "fast"
            elif words_per_minute > 130:  # Medium-fast speech
                tts_rate = 0.8  # Slow down moderately
                speed_category = "medium_fast"
            elif words_per_minute > 100:  # Normal speech
                tts_rate = 0.85  # Slight slowdown
                speed_category = "normal"
            elif words_per_minute > 80:   # Slow speech
                tts_rate = 0.9   # Minimal adjustment
                speed_category = "slow"
            else:  # Very slow speech
                tts_rate = 0.95  # Almost no adjustment
                speed_category = "very_slow"
            
            speech_info = {
                "duration": duration,
                "voice_ratio": voice_ratio,
                "speech_duration": speech_duration,
                "estimated_wpm": words_per_minute,
                "tempo": tempo if 'tempo' in locals() else 120,
                "tts_rate": tts_rate,
                "speed_category": speed_category,
                "analysis_method": analysis_method,
                "recommendation": f"Original speech: {speed_category} ({words_per_minute:.1f} WPM) → TTS rate: {tts_rate}"
            }
            
            logger.info(f"Speech rate analysis: {speed_category} speech ({words_per_minute:.1f} WPM) → TTS rate: {tts_rate}")
            return speech_info
            
        except Exception as e:
            logger.error(f"Speech rate analysis failed: {e}")
            return {
                "duration": 0,
                "voice_ratio": 0.7,
                "speech_duration": 0,
                "estimated_wpm": 120,
                "tempo": 120,
                "tts_rate": 0.85,  # Safe default
                "speed_category": "unknown",
                "analysis_method": "fallback",
                "recommendation": "Using default TTS rate due to analysis failure",
                "error": str(e)
            }
    
    async def speech_to_text_with_timestamps(self, audio_path: str, task_id: str, source_language: str = "en") -> Dict[str, Any]:
        """
        Convert speech to text with timestamps using external Whisper service
        Fixed: บังคับให้ใช้ภาษาต้นฉบับที่กำหนด
        """
        try:
            logger.info(f"Starting speech-to-text with timestamps for task {task_id} with language: {source_language}")
            
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Call external Whisper service with explicit language
            url = f"{self.whisper_service_url}/transcribe"
            
            with open(audio_path, 'rb') as audio_file:
                files = {'file': audio_file}
                data = {
                    'language': source_language,  # บังคับภาษาต้นฉบับ
                    'task': 'transcribe',  # ไม่ใช่ translate
                    'word_timestamps': True  # เพิ่ม timestamps ระดับคำ
                }
                response = requests.post(url, files=files, data=data)
                
                if response.status_code != 200:
                    raise Exception(f"Whisper service error: {response.text}")
                
                result = response.json()
                detected_language = result.get('language', source_language)
                
                # เพิ่มข้อมูลเพิ่มเติม
                result['requested_language'] = source_language
                result['task_id'] = task_id
                
                # Save transcript to file
                transcript_path = os.path.join(self.upload_dir, f"transcript_{task_id}.json")
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Speech-to-text with timestamps completed for task {task_id}. Detected: {detected_language}")
                
                # ตรวจสอบความถูกต้องของภาษา
                if detected_language != source_language:
                    logger.warning(f"Language mismatch! Requested: {source_language}, Detected: {detected_language}")
                
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