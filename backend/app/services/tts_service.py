# backend/app/services/tts_service.py
import os
import asyncio
import logging
import tempfile
from typing import Optional, Dict, Any
import subprocess
from TTS.api import TTS
import torch
from core.config import settings, TTS_MODELS

logger = logging.getLogger(__name__)

class TTSService:
    """Service for Text-to-Speech conversion using Coqui TTS"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.output_dir = settings.OUTPUT_DIR
        self.tts_models = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Ensure directories exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load default Thai TTS model
        self._load_thai_model()
    
    def _load_thai_model(self):
        """Load Thai TTS model"""
        try:
            model_name = settings.TTS_MODEL_TH
            logger.info(f"Loading Thai TTS model: {model_name}")
            
            self.tts_models["th"] = TTS(model_name=model_name).to(self.device)
            logger.info("Thai TTS model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Thai TTS model: {str(e)}")
            # Fallback to simpler model
            try:
                self.tts_models["th"] = TTS(model_name="tts_models/th/mai_female/glow-tts").to(self.device)
                logger.info("Loaded fallback Thai TTS model")
            except Exception as fallback_error:
                logger.error(f"Failed to load fallback TTS model: {str(fallback_error)}")
                self.tts_models["th"] = None
    
    async def text_to_speech(self, text: str, task_id: str, language: str = "th", voice_type: str = "female") -> str:
        """
        Convert text to speech
        """
        try:
            logger.info(f"Starting text-to-speech for task {task_id}")
            logger.info(f"Text length: {len(text)} characters, Language: {language}")
            
            if not text or not text.strip():
                raise ValueError("Text to convert is empty")
            
            # Clean text for TTS
            cleaned_text = self._preprocess_text_for_tts(text, language)
            
            # Check if text is too long and split if necessary
            if len(cleaned_text) > 1000:
                return await self._synthesize_long_text(cleaned_text, task_id, language, voice_type)
            
            # Generate speech for single text
            audio_path = await self._synthesize_text(cleaned_text, task_id, language, voice_type)
            
            logger.info(f"Text-to-speech completed successfully: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"Text-to-speech failed for task {task_id}: {str(e)}")
            raise Exception(f"Failed to convert text to speech: {str(e)}")
    
    async def _synthesize_text(self, text: str, task_id: str, language: str, voice_type: str) -> str:
        """
        Synthesize speech for a single text
        """
        try:
            output_path = os.path.join(self.upload_dir, f"thai_audio_{task_id}.wav")
            
            # Get appropriate TTS model
            tts_model = self._get_tts_model(language, voice_type)
            
            if tts_model is None:
                # Fallback to external TTS service or basic synthesis
                return await self._fallback_tts(text, task_id, language)
            
            # Run TTS synthesis in executor to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: tts_model.tts_to_file(text=text, file_path=output_path)
            )
            
            if not os.path.exists(output_path):
                raise Exception("TTS output file was not created")
            
            # Optimize audio for video merging
            optimized_path = await self._optimize_audio_for_video(output_path, task_id)
            
            return optimized_path
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {str(e)}")
            raise
    
    async def _synthesize_long_text(self, text: str, task_id: str, language: str, voice_type: str) -> str:
        """
        Synthesize speech for long text by splitting into chunks
        """
        try:
            logger.info(f"Synthesizing long text in chunks for task {task_id}")
            
            # Split text into manageable chunks
            chunks = self._split_text_for_tts(text)
            audio_files = []
            
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    logger.info(f"Synthesizing chunk {i+1}/{len(chunks)}")
                    
                    chunk_output = os.path.join(self.upload_dir, f"tts_chunk_{task_id}_{i}.wav")
                    
                    # Get TTS model
                    tts_model = self._get_tts_model(language, voice_type)
                    
                    if tts_model:
                        await asyncio.get_event_loop().run_in_executor(
                            None, 
                            lambda: tts_model.tts_to_file(text=chunk.strip(), file_path=chunk_output)
                        )
                        
                        if os.path.exists(chunk_output):
                            audio_files.append(chunk_output)
                    
                    # Small delay between chunks
                    await asyncio.sleep(0.1)
            
            if not audio_files:
                raise Exception("No audio chunks were generated")
            
            # Concatenate all audio chunks
            final_audio = await self._concatenate_audio_files(audio_files, task_id)
            
            # Clean up chunk files
            for chunk_file in audio_files:
                try:
                    os.remove(chunk_file)
                except:
                    pass
            
            return final_audio
            
        except Exception as e:
            logger.error(f"Long text TTS failed: {str(e)}")
            raise
    
    def _get_tts_model(self, language: str, voice_type: str):
        """
        Get appropriate TTS model for language and voice type
        """
        # For now, only Thai is supported
        if language == "th":
            return self.tts_models.get("th")
        else:
            logger.warning(f"Language {language} not supported, using Thai model")
            return self.tts_models.get("th")
    
    def _preprocess_text_for_tts(self, text: str, language: str) -> str:
        """
        Preprocess text for TTS synthesis
        """
        # Basic text cleaning
        text = text.strip()
        
        # Remove problematic characters
        text = text.replace('"', '"')
        text = text.replace('"', '"')
        text = text.replace(''', "'")
        text = text.replace(''', "'")
        
        # Language-specific preprocessing
        if language == "th":
            text = self._preprocess_thai_text(text)
        
        return text
    
    def _preprocess_thai_text(self, text: str) -> str:
        """
        Preprocess Thai text for better TTS
        """
        # Add spaces around English words in Thai text
        import re
        text = re.sub(r'([ก-๙])([A-Za-z])', r'\1 \2', text)
        text = re.sub(r'([A-Za-z])([ก-๙])', r'\1 \2', text)
        
        # Fix common Thai pronunciation issues
        replacements = {
            'ฯลฯ': 'และอื่นๆ',
            'ฯ': '',
            'ๆ': 'ๆ',  # Keep as is
            'URL': 'ยูอาร์แอล',
            'Email': 'อีเมล',
            'Facebook': 'เฟซบุ๊ก',
            'YouTube': 'ยูทูป',
            'Google': 'กูเกิล'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _split_text_for_tts(self, text: str, max_length: int = 800) -> list:
        """
        Split text into chunks suitable for TTS
        """
        import re
        
        # Split by sentences first
        sentences = re.split(r'[.!?।]', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_chunk) + len(sentence) > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # Sentence too long, split by phrases
                    phrases = re.split(r'[,;:]', sentence)
                    for phrase in phrases:
                        phrase = phrase.strip()
                        if phrase:
                            if len(current_chunk) + len(phrase) > max_length:
                                if current_chunk:
                                    chunks.append(current_chunk.strip())
                                current_chunk = phrase
                            else:
                                current_chunk += " " + phrase
            else:
                current_chunk += " " + sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _concatenate_audio_files(self, audio_files: list, task_id: str) -> str:
        """
        Concatenate multiple audio files into one
        """
        try:
            output_path = os.path.join(self.upload_dir, f"thai_audio_{task_id}.wav")
            
            # Create file list for FFmpeg
            filelist_path = os.path.join(self.upload_dir, f"filelist_{task_id}.txt")
            with open(filelist_path, 'w') as f:
                for audio_file in audio_files:
                    f.write(f"file '{audio_file}'\n")
            
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
                raise Exception(f"Audio concatenation failed: {stderr.decode()}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Audio concatenation failed: {str(e)}")
            raise
    
    async def _optimize_audio_for_video(self, audio_path: str, task_id: str) -> str:
        """
        Optimize audio for video merging
        """
        try:
            optimized_path = os.path.join(self.upload_dir, f"optimized_thai_audio_{task_id}.wav")
            
            # FFmpeg command for audio optimization
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-ar', str(settings.TTS_SAMPLE_RATE),  # Sample rate
                '-ac', '2',  # Stereo
                '-b:a', '128k',  # Bitrate
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
            
            return optimized_path
            
        except Exception as e:
            logger.warning(f"Audio optimization failed, using original: {str(e)}")
            return audio_path
    
    async def _fallback_tts(self, text: str, task_id: str, language: str) -> str:
        """
        Fallback TTS using external service or espeak
        """
        try:
            logger.warning("Using fallback TTS (espeak)")
            
            output_path = os.path.join(self.upload_dir, f"fallback_thai_audio_{task_id}.wav")
            
            # Use espeak as fallback
            cmd = [
                'espeak',
                '-v', 'th',  # Thai voice
                '-s', '150',  # Speed
                '-w', output_path,  # Output file
                text
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if process.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                raise Exception("Fallback TTS failed")
                
        except Exception as e:
            logger.error(f"Fallback TTS failed: {str(e)}")
            raise Exception("All TTS methods failed")
    
    async def get_audio_duration(self, audio_path: str) -> float:
        """
        Get audio duration using ffprobe
        """
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', audio_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return 0.0
            
            import json
            probe_data = json.loads(stdout.decode())
            duration = float(probe_data['format']['duration'])
            
            return duration
            
        except Exception as e:
            logger.warning(f"Could not get audio duration: {str(e)}")
            return 0.0
    
    async def cleanup_tts_files(self, task_id: str):
        """
        Clean up TTS files for a task
        """
        try:
            files_to_clean = [
                f"thai_audio_{task_id}.wav",
                f"optimized_thai_audio_{task_id}.wav",
                f"fallback_thai_audio_{task_id}.wav",
                f"filelist_{task_id}.txt"
            ]
            
            # Also clean up any TTS chunks
            for i in range(20):  # Assume max 20 chunks
                files_to_clean.append(f"tts_chunk_{task_id}_{i}.wav")
            
            for filename in files_to_clean:
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up TTS file: {file_path}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up TTS files for task {task_id}: {str(e)}")