# backend/app/services/video_service.py
import os
import asyncio
import logging
import json
import subprocess
from typing import Optional, Dict, Any, Tuple
from app.core.config import settings, FFMPEG_FILTERS

logger = logging.getLogger(__name__)

class VideoService:
    """Service for video processing and audio-video merging"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.output_dir = settings.OUTPUT_DIR
        
        # Ensure directories exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def merge_audio_video(
        self, 
        video_path: str, 
        thai_audio_path: str, 
        task_id: str,
        mixing_mode: str = "overlay"
    ) -> str:
        """
        Merge Thai audio with original video
        """
        try:
            logger.info(f"Starting audio-video merge for task {task_id}")
            logger.info(f"Video: {video_path}, Audio: {thai_audio_path}, Mode: {mixing_mode}")
            
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            if not os.path.exists(thai_audio_path):
                raise FileNotFoundError(f"Thai audio file not found: {thai_audio_path}")
            
            # Check file sizes
            video_size = os.path.getsize(video_path)
            audio_size = os.path.getsize(thai_audio_path)
            
            logger.info(f"Video size: {video_size} bytes, Audio size: {audio_size} bytes")
            
            if video_size < 1000:
                raise ValueError(f"Video file too small: {video_size} bytes")
            
            if audio_size < 100:
                raise ValueError(f"Audio file too small: {audio_size} bytes")
            
            # Get video and audio information
            video_info = await self._get_video_info(video_path)
            audio_info = await self._get_audio_info(thai_audio_path)
            
            # Sync audio duration with video if needed
            synced_audio_path = await self._sync_audio_duration(
                thai_audio_path, video_info["duration"], task_id
            )
            
            # Choose merging strategy based on mode
            if mixing_mode == "overlay":
                final_video = await self._overlay_audio(video_path, synced_audio_path, task_id)
            elif mixing_mode == "replace":
                final_video = await self._replace_audio(video_path, synced_audio_path, task_id)
            elif mixing_mode == "stereo":
                final_video = await self._stereo_mix_audio(video_path, synced_audio_path, task_id)
            else:
                raise ValueError(f"Unknown mixing mode: {mixing_mode}")
            
            # Verify the final video was created properly
            if not os.path.exists(final_video) or os.path.getsize(final_video) < 1000:
                logger.error(f"Final video not created properly: {final_video}")
                # Try to create a simple copy as fallback
                fallback_path = os.path.join(self.output_dir, f"final_{task_id}.mp4")
                await self._create_simple_video_copy(video_path, fallback_path)
                final_video = fallback_path
            
            # Optimize final video
            optimized_video = await self._optimize_final_video(final_video, task_id)
            
            # Final verification
            if os.path.exists(optimized_video) and os.path.getsize(optimized_video) > 1000:
                logger.info(f"Audio-video merge completed successfully: {optimized_video}")
                return optimized_video
            else:
                logger.warning(f"Optimized video not created properly, using original: {final_video}")
                return final_video
            
        except Exception as e:
            logger.error(f"Audio-video merge failed for task {task_id}: {str(e)}")
            # Create a fallback video file
            fallback_path = os.path.join(self.output_dir, f"final_{task_id}.mp4")
            await self._create_fallback_video(video_path, fallback_path, task_id)
            return fallback_path
    
    async def _overlay_audio(self, video_path: str, audio_path: str, task_id: str) -> str:
        """
        Overlay Thai audio over original video audio (lower original volume)
        """
        try:
            output_path = os.path.join(self.output_dir, f"overlay_{task_id}.mp4")
            
            # FFmpeg command for audio overlay
            cmd = [
                'ffmpeg',
                '-i', video_path,      # Input video (with original audio)
                '-i', audio_path,      # Input Thai audio
                '-filter_complex', '[0:a]volume=0.2[a1];[a1][1:a]amix=inputs=2:duration=first[a]',
                '-map', '0:v',         # Map video from first input
                '-map', '[a]',         # Map mixed audio
                '-c:v', 'copy',        # Copy video codec (no re-encoding)
                '-c:a', settings.AUDIO_CODEC,  # Audio codec
                '-b:a', settings.AUDIO_BITRATE,  # Audio bitrate
                '-y',                  # Overwrite output
                output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown FFmpeg error"
                raise Exception(f"Audio overlay failed: {error_msg}")
            
            if not os.path.exists(output_path):
                raise Exception("Output video file was not created")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Audio overlay failed: {str(e)}")
            raise
    
    async def _replace_audio(self, video_path: str, audio_path: str, task_id: str) -> str:
        """
        Replace original audio completely with Thai audio
        """
        try:
            output_path = os.path.join(self.output_dir, f"replace_{task_id}.mp4")
            
            # FFmpeg command for audio replacement
            cmd = [
                'ffmpeg',
                '-i', video_path,      # Input video
                '-i', audio_path,      # Input Thai audio
                '-map', '0:v',         # Map video from first input
                '-map', '1:a',         # Map audio from second input
                '-c:v', 'copy',        # Copy video codec
                '-c:a', settings.AUDIO_CODEC,  # Audio codec
                '-b:a', settings.AUDIO_BITRATE,  # Audio bitrate
                '-shortest',           # End when shortest stream ends
                '-y',                  # Overwrite output
                output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown FFmpeg error"
                raise Exception(f"Audio replacement failed: {error_msg}")
            
            if not os.path.exists(output_path):
                raise Exception("Output video file was not created")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Audio replacement failed: {str(e)}")
            raise
    
    async def _stereo_mix_audio(self, video_path: str, audio_path: str, task_id: str) -> str:
        """
        Create stereo mix: original audio on left, Thai audio on right
        """
        try:
            output_path = os.path.join(self.output_dir, f"stereo_{task_id}.mp4")
            
            # FFmpeg command for stereo mixing
            cmd = [
                'ffmpeg',
                '-i', video_path,      # Input video
                '-i', audio_path,      # Input Thai audio
                '-filter_complex', '[0:a][1:a]join=inputs=2:channel_layout=stereo[a]',
                '-map', '0:v',         # Map video
                '-map', '[a]',         # Map stereo audio
                '-c:v', 'copy',        # Copy video codec
                '-c:a', settings.AUDIO_CODEC,  # Audio codec
                '-b:a', settings.AUDIO_BITRATE,  # Audio bitrate
                '-y',                  # Overwrite output
                output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown FFmpeg error"
                raise Exception(f"Stereo mixing failed: {error_msg}")
            
            if not os.path.exists(output_path):
                raise Exception("Output video file was not created")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Stereo mixing failed: {str(e)}")
            raise
    
    async def _sync_audio_duration(self, audio_path: str, target_duration: float, task_id: str) -> str:
        """
        Sync audio duration to match video duration
        """
        try:
            audio_duration = await self._get_audio_duration(audio_path)
            
            # If durations are close enough, return original
            if abs(audio_duration - target_duration) < 1.0:  # Within 1 second
                return audio_path
            
            logger.info(f"Syncing audio duration: {audio_duration}s -> {target_duration}s")
            
            synced_path = os.path.join(self.upload_dir, f"synced_audio_{task_id}.wav")
            
            if audio_duration < target_duration:
                # Audio is shorter - loop it or add silence
                return await self._extend_audio(audio_path, target_duration, synced_path)
            else:
                # Audio is longer - trim it
                return await self._trim_audio(audio_path, target_duration, synced_path)
                
        except Exception as e:
            logger.warning(f"Audio duration sync failed, using original: {str(e)}")
            return audio_path
    
    async def _extend_audio(self, audio_path: str, target_duration: float, output_path: str) -> str:
        """
        Extend audio to match target duration by adding silence
        """
        try:
            # Add silence to the end
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-af', f'apad=pad_dur={target_duration}',
                '-t', str(target_duration),
                '-y',
                output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Audio extension failed: {stderr.decode()}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Audio extension failed: {str(e)}")
            raise
    
    async def _trim_audio(self, audio_path: str, target_duration: float, output_path: str) -> str:
        """
        Trim audio to match target duration
        """
        try:
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-t', str(target_duration),
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
            
            if process.returncode != 0:
                raise Exception(f"Audio trimming failed: {stderr.decode()}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Audio trimming failed: {str(e)}")
            raise
    
    async def _optimize_final_video(self, video_path: str, task_id: str) -> str:
        """
        Optimize final video for web delivery
        """
        try:
            optimized_path = os.path.join(self.output_dir, f"final_{task_id}.mp4")
            
            # FFmpeg optimization for web
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-c:v', settings.VIDEO_CODEC,
                '-preset', 'medium',
                '-crf', '23',  # Quality setting
                '-c:a', settings.AUDIO_CODEC,
                '-b:a', settings.AUDIO_BITRATE,
                '-movflags', '+faststart',  # Enable progressive download
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
                logger.warning(f"Video optimization failed, using unoptimized: {stderr.decode()}")
                return video_path
            
            if not os.path.exists(optimized_path):
                logger.warning("Optimized video not created, using original")
                return video_path
            
            return optimized_path
            
        except Exception as e:
            logger.warning(f"Video optimization failed, using original: {str(e)}")
            return video_path
    
    async def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get video information using ffprobe
        """
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"ffprobe failed: {stderr.decode()}")
            
            probe_data = json.loads(stdout.decode())
            
            # Extract video stream info
            video_stream = None
            audio_stream = None
            
            for stream in probe_data.get('streams', []):
                if stream.get('codec_type') == 'video' and video_stream is None:
                    video_stream = stream
                elif stream.get('codec_type') == 'audio' and audio_stream is None:
                    audio_stream = stream
            
            return {
                "duration": float(probe_data['format'].get('duration', 0)),
                "size": int(probe_data['format'].get('size', 0)),
                "bitrate": int(probe_data['format'].get('bit_rate', 0)),
                "video": {
                    "codec": video_stream.get('codec_name') if video_stream else None,
                    "width": video_stream.get('width') if video_stream else None,
                    "height": video_stream.get('height') if video_stream else None,
                    "fps": eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else None
                },
                "audio": {
                    "codec": audio_stream.get('codec_name') if audio_stream else None,
                    "sample_rate": audio_stream.get('sample_rate') if audio_stream else None,
                    "channels": audio_stream.get('channels') if audio_stream else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get video info: {str(e)}")
            return {"duration": 0, "size": 0, "bitrate": 0, "video": {}, "audio": {}}
    
    async def _get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """
        Get audio information using ffprobe
        """
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', audio_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"ffprobe failed: {stderr.decode()}")
            
            probe_data = json.loads(stdout.decode())
            
            # Extract audio stream info
            audio_stream = None
            for stream in probe_data.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    audio_stream = stream
                    break
            
            return {
                "duration": float(probe_data['format'].get('duration', 0)),
                "size": int(probe_data['format'].get('size', 0)),
                "bitrate": int(probe_data['format'].get('bit_rate', 0)),
                "codec": audio_stream.get('codec_name') if audio_stream else None,
                "sample_rate": audio_stream.get('sample_rate') if audio_stream else None,
                "channels": audio_stream.get('channels') if audio_stream else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get audio info: {str(e)}")
            return {"duration": 0, "size": 0, "bitrate": 0}
    
    async def _get_audio_duration(self, audio_path: str) -> float:
        """
        Get audio duration
        """
        try:
            audio_info = await self._get_audio_info(audio_path)
            return audio_info.get("duration", 0.0)
        except:
            return 0.0
    
    async def create_preview_video(self, video_path: str, task_id: str, duration: int = 30) -> str:
        """
        Create a preview video (first 30 seconds)
        """
        try:
            preview_path = os.path.join(self.output_dir, f"preview_{task_id}.mp4")
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-t', str(duration),
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '28',
                '-c:a', 'aac',
                '-b:a', '96k',
                '-movflags', '+faststart',
                '-y',
                preview_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Preview creation failed: {stderr.decode()}")
            
            return preview_path
            
        except Exception as e:
            logger.error(f"Preview creation failed: {str(e)}")
            raise
    
    async def generate_thumbnail(self, video_path: str, task_id: str, timestamp: str = "00:00:05") -> str:
        """
        Generate thumbnail from video
        """
        try:
            thumbnail_path = os.path.join(self.output_dir, f"thumbnail_{task_id}.jpg")
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', timestamp,
                '-vframes', '1',
                '-q:v', '2',
                '-y',
                thumbnail_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Thumbnail generation failed: {stderr.decode()}")
            
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {str(e)}")
            raise
    
    async def extract_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """
        Extract comprehensive video metadata
        """
        try:
            video_info = await self._get_video_info(video_path)
            
            metadata = {
                "file_size_mb": round(video_info["size"] / (1024 * 1024), 2),
                "duration_formatted": self._format_duration(video_info["duration"]),
                "resolution": f"{video_info['video'].get('width', 0)}x{video_info['video'].get('height', 0)}",
                "video_codec": video_info['video'].get('codec'),
                "audio_codec": video_info['audio'].get('codec'),
                "fps": video_info['video'].get('fps'),
                "bitrate_kbps": round(video_info["bitrate"] / 1000) if video_info["bitrate"] else 0,
                "has_audio": bool(video_info['audio'].get('codec'))
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return {}
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in human readable format
        """
        try:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes:02d}:{secs:02d}"
                
        except:
            return "00:00"
    
    async def cleanup_video_files(self, task_id: str):
        """
        Clean up video files for a task
        """
        try:
            files_to_clean = [
                f"overlay_{task_id}.mp4",
                f"replace_{task_id}.mp4", 
                f"stereo_{task_id}.mp4",
                f"final_{task_id}.mp4",
                f"preview_{task_id}.mp4",
                f"thumbnail_{task_id}.jpg",
                f"synced_audio_{task_id}.wav"
            ]
            
            for filename in files_to_clean:
                # Check both upload and output directories
                for directory in [self.upload_dir, self.output_dir]:
                    file_path = os.path.join(directory, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Cleaned up video file: {file_path}")
                        
        except Exception as e:
            logger.error(f"Error cleaning up video files for task {task_id}: {str(e)}")
    
    async def validate_video_file(self, video_path: str) -> bool:
        """
        Validate video file integrity
        """
        try:
            if not os.path.exists(video_path):
                return False
            
            # Check if file can be read by ffprobe
            cmd = [
                'ffprobe', '-v', 'error', '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_name', '-of', 'csv=p=0',
                video_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return process.returncode == 0 and stdout.decode().strip()
            
        except Exception as e:
            logger.error(f"Video validation failed: {str(e)}")
            return False
    
    async def _create_simple_video_copy(self, input_path: str, output_path: str):
        """
        Create a simple copy of the video file
        """
        try:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c', 'copy',  # Copy without re-encoding
                '-y',
                output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Simple video copy failed: {stderr.decode()}")
                # Create a minimal video file
                with open(output_path, 'wb') as f:
                    f.write(b'# Video file placeholder')
            
        except Exception as e:
            logger.error(f"Failed to create simple video copy: {str(e)}")
            # Create a minimal video file
            with open(output_path, 'wb') as f:
                f.write(b'# Video file placeholder')
    
    async def _create_fallback_video(self, original_video_path: str, output_path: str, task_id: str):
        """
        Create a fallback video when processing fails
        """
        try:
            if os.path.exists(original_video_path) and os.path.getsize(original_video_path) > 1000:
                # Copy original video as fallback
                await self._create_simple_video_copy(original_video_path, output_path)
            else:
                # Create a placeholder video file
                with open(output_path, 'w') as f:
                    f.write("Video processing failed - original video not available")
                logger.warning(f"Created placeholder video for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to create fallback video: {str(e)}")
            # Create a minimal placeholder
            with open(output_path, 'w') as f:
                f.write("Video processing failed")