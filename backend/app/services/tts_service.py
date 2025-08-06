# backend/app/services/tts_service.py
import os
import asyncio
import logging
import tempfile
import requests
from typing import Optional, Dict, Any
import subprocess
from app.core.config import settings

logger = logging.getLogger(__name__)

def normalize_path(path):
    """
    Normalize a path to avoid duplication issues, especially in Docker environments
    """
    # Convert to absolute path
    abs_path = os.path.abspath(path)
    
    # Split the path
    path_parts = abs_path.split(os.sep)
    
    # Remove any duplicate 'uploads' entries
    if 'uploads' in path_parts:
        uploads_indices = [i for i, part in enumerate(path_parts) if part == 'uploads']
        if len(uploads_indices) > 1:
            # Keep only the first 'uploads' entry
            first_uploads = uploads_indices[0]
            cleaned_parts = path_parts[:first_uploads + 1] + [p for p in path_parts[first_uploads + 1:] if p != 'uploads']
            return os.sep.join(cleaned_parts)
    
    return abs_path

class TTSService:
    """Service for Text-to-Speech conversion using external TTS service"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.output_dir = settings.OUTPUT_DIR
        self.tts_service_url = settings.TTS_SERVICE_URL
        
        # Ensure directories exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Normalize paths to avoid issues
        self.upload_dir = normalize_path(self.upload_dir)
        self.output_dir = normalize_path(self.output_dir)
        
        # Log directory paths for debugging
        logger.info(f"TTS Service initialized with upload_dir: {self.upload_dir}")
        logger.info(f"TTS Service initialized with output_dir: {self.output_dir}")
        logger.info(f"Current working directory: {os.getcwd()}")
    
    async def text_to_speech(self, text: str, task_id: str, language: str = "th", voice_type: str = "female", speech_rate_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Convert text to speech using external TTS service with dynamic speech rate adjustment
        """
        try:
            logger.info(f"Starting text-to-speech for task {task_id}")
            logger.info(f"Text length: {len(text)} characters, Language: {language}")
            
            # Log speech rate information if available
            if speech_rate_info:
                logger.info(f"Speech rate analysis: {speech_rate_info}")
            
            if not text or not text.strip():
                raise ValueError("Text to convert is empty")
            
            # Clean text for TTS
            cleaned_text = self._preprocess_text_for_tts(text, language)
            
            # Check if text is too long and split if necessary
            if len(cleaned_text) > 1000:
                return await self._synthesize_long_text(cleaned_text, task_id, language, voice_type, speech_rate_info)
            
            # Generate speech for single text
            audio_path = await self._synthesize_text(cleaned_text, task_id, language, voice_type, speech_rate_info)
            
            logger.info(f"Text-to-speech completed successfully: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"Text-to-speech failed for task {task_id}: {str(e)}")
            raise Exception(f"Failed to convert text to speech: {str(e)}")
    
    async def _synthesize_text(self, text: str, task_id: str, language: str, voice_type: str, speech_rate_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Synthesize speech for a single text using external TTS service with dynamic rate adjustment
        """
        try:
            output_path = os.path.join(self.upload_dir, f"thai_audio_{task_id}.wav")
            
            # Calculate dynamic speech rate based on analysis
            speech_rate = self._calculate_tts_rate(speech_rate_info)
            
            # Call external TTS service
            url = f"{self.tts_service_url}/synthesize"
            
            payload = {
                "text": text,
                "language": language,
                "voice_type": voice_type,
                "use_edge_tts": True,
                "speech_rate": speech_rate  # Add dynamic speech rate
            }
            
            logger.info(f"TTS request with speech_rate: {speech_rate}")
            
            response = requests.post(url, json=payload)
            
            if response.status_code != 200:
                raise Exception(f"TTS service error: {response.text}")
            
            result = response.json()
            audio_filename = result.get('audio_file')
            
            if not audio_filename:
                raise Exception("TTS service did not return audio file")
            
            # Download the generated audio file
            download_url = f"{self.tts_service_url}/download/{audio_filename}"
            audio_response = requests.get(download_url)
            
            if audio_response.status_code != 200:
                raise Exception("Failed to download generated audio file")
            
            # Save the audio file
            with open(output_path, 'wb') as f:
                f.write(audio_response.content)
            
            if not os.path.exists(output_path):
                raise Exception("TTS output file was not created")
            
            # Optimize audio for video merging
            optimized_path = await self._optimize_audio_for_video(output_path, task_id)
            
            logger.info(f"TTS synthesis completed. Original: {output_path}, Optimized: {optimized_path}")
            return optimized_path
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {str(e)}")
            raise
    
    async def _synthesize_long_text(self, text: str, task_id: str, language: str, voice_type: str, speech_rate_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Synthesize speech for long text by splitting into chunks with dynamic speech rate
        """
        try:
            logger.info(f"Synthesizing long text ({len(text)} chars) for task {task_id}")
            
            # Split text into manageable chunks
            text_chunks = self._split_text_for_tts(text)
            audio_files = []
            
            # Synthesize each chunk
            for i, chunk in enumerate(text_chunks):
                if not chunk.strip():
                    continue
                
                chunk_task_id = f"{task_id}_chunk_{i}"
                chunk_audio = await self._synthesize_text(chunk, chunk_task_id, language, voice_type, speech_rate_info)
                
                # Validate that the chunk audio file was created
                if not os.path.exists(chunk_audio):
                    raise Exception(f"Chunk audio file was not created: {chunk_audio}")
                
                logger.info(f"Created chunk audio file: {chunk_audio}")
                audio_files.append(chunk_audio)
            
            if not audio_files:
                raise Exception("No audio files were generated")
            
            # Concatenate all audio files
            if len(audio_files) == 1:
                final_audio = audio_files[0]
            else:
                final_audio = await self._concatenate_audio_files(audio_files, task_id)
            
            # Clean up individual chunk files
            for audio_file in audio_files:
                if os.path.exists(audio_file) and audio_file != final_audio:
                    try:
                        os.remove(audio_file)
                    except:
                        pass
            
            return final_audio
            
        except Exception as e:
            logger.error(f"Long text synthesis failed: {str(e)}")
            raise
    
    def _preprocess_text_for_tts(self, text: str, language: str) -> str:
        """
        Preprocess text for TTS synthesis
        """
        if language == "th":
            return self._preprocess_thai_text(text)
        else:
            return self._preprocess_english_text(text)
    
    def _preprocess_thai_text(self, text: str) -> str:
        """
        Preprocess Thai text for TTS
        """
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove special characters that might cause issues
        import re
        text = re.sub(r'[^\u0E00-\u0E7F\s\w\.,!?;:]', '', text)
        
        # Ensure proper sentence endings
        text = text.replace('..', '.')
        text = text.replace('!!', '!')
        text = text.replace('??', '?')
        
        return text.strip()
    
    def _preprocess_english_text(self, text: str) -> str:
        """
        Preprocess English text for TTS
        """
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove special characters that might cause issues
        import re
        text = re.sub(r'[^\x00-\x7F\s\w\.,!?;:]', '', text)
        
        # Ensure proper sentence endings
        text = text.replace('..', '.')
        text = text.replace('!!', '!')
        text = text.replace('??', '?')
        
        return text.strip()
    
    def _split_text_for_tts(self, text: str, max_length: int = 800) -> list:
        """
        Split long text into smaller chunks for TTS
        """
        if len(text) <= max_length:
            return [text]
        
        # Split by sentences first
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in '.!?':
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # Group sentences into chunks
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _concatenate_audio_files(self, audio_files: list, task_id: str) -> str:
        """
        Concatenate multiple audio files into one
        """
        try:
            output_path = os.path.join(self.upload_dir, f"thai_audio_{task_id}.wav")
            
            logger.info(f"=== CONCATENATION DEBUG START ===")
            logger.info(f"Task ID: {task_id}")
            logger.info(f"Number of audio files: {len(audio_files)}")
            logger.info(f"Audio files list: {audio_files}")
            
            # Validate that all audio files exist before concatenation
            for i, audio_file in enumerate(audio_files):
                logger.info(f"Checking audio file {i+1}: {audio_file}")
                logger.info(f"  - Type: {type(audio_file)}")
                logger.info(f"  - Exists: {os.path.exists(audio_file)}")
                logger.info(f"  - Absolute: {os.path.abspath(audio_file)}")
                logger.info(f"  - Dirname: {os.path.dirname(audio_file)}")
                logger.info(f"  - Basename: {os.path.basename(audio_file)}")
                
                if not os.path.exists(audio_file):
                    raise Exception(f"Audio file not found: {audio_file}")
                logger.info(f"Audio file exists: {audio_file}")
            
            # Create file list for FFmpeg
            filelist_path = os.path.join(self.upload_dir, f"filelist_{task_id}.txt")
            
            logger.info(f"Creating filelist at: {filelist_path}")
            logger.info(f"Current working directory: {os.getcwd()}")
            logger.info(f"Upload directory: {self.upload_dir}")
            logger.info(f"Upload directory (absolute): {os.path.abspath(self.upload_dir)}")
            
            with open(filelist_path, 'w') as f:
                for i, audio_file in enumerate(audio_files):
                    logger.info(f"Processing audio file {i+1}: {audio_file}")
                    logger.info(f"Audio file exists: {os.path.exists(audio_file)}")
                    logger.info(f"Audio file (absolute): {os.path.abspath(audio_file)}")
                    
                    # Use normalized paths to avoid duplication issues
                    normalized_audio_file = normalize_path(audio_file)
                    logger.info(f"Normalized path: {audio_file} -> {normalized_audio_file}")
                    
                    file_entry = f"file '{normalized_audio_file}'\n"
                    f.write(file_entry)
                    logger.info(f"Wrote to filelist: {file_entry.strip()}")
            
            # Log the filelist content for debugging
            with open(filelist_path, 'r') as f:
                filelist_content = f.read()
                logger.info(f"Complete filelist content for task {task_id}:\n{filelist_content}")
                logger.info(f"Filelist file size: {os.path.getsize(filelist_path)} bytes")
            
            # FFmpeg command to concatenate
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', filelist_path,
                '-c', 'copy',
                '-y',
                output_path
            ]
            
            logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Clean up filelist
            try:
                os.remove(filelist_path)
            except:
                pass
            
            if process.returncode != 0:
                logger.error(f"FFmpeg stdout: {stdout.decode()}")
                logger.error(f"FFmpeg stderr: {stderr.decode()}")
                raise Exception(f"Audio concatenation failed: {stderr.decode()}")
            
            if not os.path.exists(output_path):
                raise Exception(f"Output file was not created: {output_path}")
            
            logger.info(f"Audio concatenation successful: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Audio concatenation failed: {str(e)}")
            raise
    
    async def _optimize_audio_for_video(self, audio_path: str, task_id: str) -> str:
        """
        Optimize audio for video merging
        """
        try:
            optimized_path = os.path.join(self.upload_dir, f"optimized_audio_{task_id}.wav")
            logger.info(f"Optimizing audio: {audio_path} -> {optimized_path}")
            
            # FFmpeg command for audio optimization
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-af', 'volume=1.2,highpass=f=80,lowpass=f=8000',  # Enhance audio
                '-ar', '44100',  # 44.1kHz sample rate
                '-ac', '2',      # Stereo
                '-b:a', '192k',  # 192kbps bitrate
                '-y',
                optimized_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.warning(f"Audio optimization failed, using original: {stderr.decode()}")
                return audio_path
            
            if not os.path.exists(optimized_path):
                logger.warning("Optimized audio file was not created, using original")
                return audio_path
            
            return optimized_path
            
        except Exception as e:
            logger.warning(f"Audio optimization failed, using original: {str(e)}")
            return audio_path
    
    async def get_audio_duration(self, audio_path: str) -> float:
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
    
    async def cleanup_tts_files(self, task_id: str):
        """
        Clean up TTS-related files
        """
        try:
            files_to_clean = [
                f"thai_audio_{task_id}.wav",
                f"optimized_audio_{task_id}.wav",
                f"filelist_{task_id}.txt"
            ]
            
            # Also clean up chunk files
            import glob
            chunk_pattern = f"optimized_audio_{task_id}_chunk_*.wav"
            chunk_files = glob.glob(os.path.join(self.upload_dir, chunk_pattern))
            files_to_clean.extend([os.path.basename(f) for f in chunk_files])
            
            # Also clean up original chunk files (before optimization)
            original_chunk_pattern = f"thai_audio_{task_id}_chunk_*.wav"
            original_chunk_files = glob.glob(os.path.join(self.upload_dir, original_chunk_pattern))
            files_to_clean.extend([os.path.basename(f) for f in original_chunk_files])
            
            for filename in files_to_clean:
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up TTS file: {filename}")
                    
        except Exception as e:
            logger.error(f"Failed to cleanup TTS files for task {task_id}: {str(e)}")
    
    def _calculate_tts_rate(self, speech_rate_info: Optional[Dict[str, Any]]) -> float:
        """
        Calculate optimal TTS speech rate based on original speech analysis
        
        Args:
            speech_rate_info: Dictionary containing speech analysis data
            
        Returns:
            float: TTS speech rate (0.6 - 1.0)
        """
        try:
            if not speech_rate_info:
                logger.info("No speech rate info provided, using default rate 0.85")
                return 0.85
            
            # Extract speech rate information
            detected_wpm = speech_rate_info.get('words_per_minute', 120)
            speech_category = speech_rate_info.get('speech_category', 'normal')
            tts_rate = speech_rate_info.get('recommended_tts_rate', 0.85)
            
            logger.info(f"Speech analysis: WPM={detected_wpm}, Category={speech_category}, Recommended TTS rate={tts_rate}")
            
            # Ensure rate is within valid bounds for TTS service
            if tts_rate < 0.6:
                logger.warning(f"TTS rate {tts_rate} too low, setting to 0.6")
                tts_rate = 0.6
            elif tts_rate > 1.0:
                logger.warning(f"TTS rate {tts_rate} too high, setting to 1.0")
                tts_rate = 1.0
            
            return tts_rate
            
        except Exception as e:
            logger.error(f"Error calculating TTS rate: {str(e)}")
            return 0.85  # Safe fallback