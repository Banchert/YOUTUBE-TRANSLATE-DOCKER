# backend/app/services/youtube_service.py
import os
import asyncio
import subprocess
import json
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
import yt_dlp
from app.core.config import settings

logger = logging.getLogger(__name__)

class YouTubeService:
    """Service for downloading YouTube videos"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def get_video_info(self, youtube_url: str) -> Dict[str, Any]:
        """
        Extract video information without downloading
        """
        try:
            # Configure yt-dlp options for info extraction only
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info
                info = await asyncio.get_event_loop().run_in_executor(
                    None, ydl.extract_info, youtube_url, False
                )
                
                # Parse and return relevant information
                video_info = {
                    "id": info.get("id"),
                    "title": info.get("title", "Unknown Title"),
                    "duration": info.get("duration", 0),
                    "thumbnail": info.get("thumbnail"),
                    "uploader": info.get("uploader", "Unknown"),
                    "upload_date": info.get("upload_date"),
                    "view_count": info.get("view_count"),
                    "like_count": info.get("like_count"),
                    "description": info.get("description", "")[:500],  # Limit description
                    "formats": [
                        {
                            "format_id": f.get("format_id"),
                            "height": f.get("height"),
                            "width": f.get("width"),
                            "ext": f.get("ext"),
                            "filesize": f.get("filesize")
                        }
                        for f in info.get("formats", [])
                        if f.get("height") and f.get("ext") == "mp4"
                    ]
                }
                
                return video_info
                
        except Exception as e:
            logger.error(f"Failed to extract video info: {str(e)}")
            raise Exception(f"Could not extract video information: {str(e)}")
    
    async def download_video(self, youtube_url: str, task_id: str) -> str:
        """
        Download YouTube video using yt-dlp
        """
        try:
            logger.info(f"Starting download for task {task_id}: {youtube_url}")
            
            # Validate URL
            if not self._is_valid_youtube_url(youtube_url):
                raise ValueError("Invalid YouTube URL")
            
            # Get video info first to check duration
            video_info = await self.get_video_info(youtube_url)
            duration = video_info.get("duration", 0)
            
            if duration > settings.MAX_VIDEO_DURATION:
                raise ValueError(f"Video duration ({duration}s) exceeds maximum allowed ({settings.MAX_VIDEO_DURATION}s)")
            
            # Configure download options
            output_path = os.path.join(self.upload_dir, f"video_{task_id}.%(ext)s")
            
            ydl_opts = {
                'outtmpl': output_path,
                'format': self._get_best_format(),
                'writeinfojson': True,
                'writedescription': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': False,
                'no_warnings': True,
                'quiet': True,
            }
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                await asyncio.get_event_loop().run_in_executor(
                    None, ydl.download, [youtube_url]
                )
            
            # Find the downloaded file
            video_file = self._find_downloaded_file(task_id)
            
            if not video_file or not os.path.exists(video_file):
                raise Exception("Downloaded video file not found")
            
            logger.info(f"Video downloaded successfully: {video_file}")
            return video_file
            
        except Exception as e:
            logger.error(f"Download failed for task {task_id}: {str(e)}")
            raise Exception(f"Failed to download video: {str(e)}")
    
    def _is_valid_youtube_url(self, url: str) -> bool:
        """
        Validate if the URL is a valid YouTube URL
        """
        try:
            parsed = urlparse(url)
            
            # Check for various YouTube URL formats
            youtube_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com']
            
            if parsed.netloc in youtube_domains:
                if parsed.netloc == 'youtu.be':
                    return bool(parsed.path.strip('/'))
                else:
                    query_params = parse_qs(parsed.query)
                    return 'v' in query_params
            
            return False
            
        except Exception:
            return False
    
    def _get_best_format(self) -> str:
        """
        Get the best format string for yt-dlp based on settings
        """
        quality = settings.VIDEO_QUALITY
        
        format_strings = {
            "1080p": "best[height<=1080][ext=mp4]/best[height<=1080]/best[ext=mp4]/best",
            "720p": "best[height<=720][ext=mp4]/best[height<=720]/best[ext=mp4]/best",
            "480p": "best[height<=480][ext=mp4]/best[height<=480]/best[ext=mp4]/best"
        }
        
        return format_strings.get(quality, format_strings["720p"])
    
    def _find_downloaded_file(self, task_id: str) -> Optional[str]:
        """
        Find the downloaded video file
        """
        possible_extensions = ['mp4', 'webm', 'mkv', 'avi']
        
        for ext in possible_extensions:
            file_path = os.path.join(self.upload_dir, f"video_{task_id}.{ext}")
            if os.path.exists(file_path):
                return file_path
        
        return None
    
    async def cleanup_files(self, task_id: str):
        """
        Clean up downloaded files for a task
        """
        try:
            files_to_clean = [
                f"video_{task_id}.mp4",
                f"video_{task_id}.webm", 
                f"video_{task_id}.mkv",
                f"video_{task_id}.info.json"
            ]
            
            for filename in files_to_clean:
                file_path = os.path.join(self.upload_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up file: {file_path}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up files for task {task_id}: {str(e)}")

    async def get_video_duration(self, video_path: str) -> float:
        """
        Get video duration using ffprobe
        """
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise Exception(f"ffprobe failed: {stderr.decode()}")
            
            probe_data = json.loads(stdout.decode())
            duration = float(probe_data['format']['duration'])
            
            return duration
            
        except Exception as e:
            logger.error(f"Failed to get video duration: {str(e)}")
            return 0.0