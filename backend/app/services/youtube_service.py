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
                'quiet': False,  # Show output for debugging
                'no_warnings': False,  # Show warnings for debugging
                'extract_flat': False,
                'ignoreerrors': True,  # Continue on errors
                'no_check_certificate': True,  # Skip SSL certificate verification
                # Add headers to avoid detection
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Accept-Encoding': 'gzip,deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info
                info = await asyncio.get_event_loop().run_in_executor(
                    None, ydl.extract_info, str(youtube_url), False
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
            logger.info(f"URL type: {type(youtube_url)}, URL repr: {repr(youtube_url)}")
            
            # Validate URL format (basic check)
            url_valid = self._is_valid_youtube_url(youtube_url)
            logger.info(f"URL validation result: {url_valid}")
            if not url_valid:
                raise ValueError("Invalid YouTube URL format")
            
            # Try to get video info to check duration (skip if it fails)
            try:
                video_info = await self.get_video_info(str(youtube_url))
                duration = video_info.get("duration", 0)
                
                if settings.MAX_VIDEO_DURATION > 0 and duration > settings.MAX_VIDEO_DURATION:
                    raise ValueError(f"Video duration ({duration}s) exceeds maximum allowed ({settings.MAX_VIDEO_DURATION}s)")
                    
                logger.info(f"Video info: {video_info.get('title', 'Unknown')} - {duration}s")
            except Exception as e:
                logger.warning(f"Could not get video info, proceeding with download: {str(e)}")
                # Continue with download anyway
            
            # Configure download options with enhanced anti-detection
            output_path = os.path.join(self.upload_dir, f"video_{task_id}.%(ext)s")
            
            ydl_opts = {
                'outtmpl': output_path,
                'format': self._get_best_format(),
                'writeinfojson': True,
                'writedescription': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': True,  # Continue on errors
                'no_warnings': False,  # Show warnings for debugging
                'quiet': False,  # Show output for debugging
                'extract_flat': False,
                'no_check_certificate': True,  # Skip SSL certificate verification
                # Enhanced headers to avoid detection
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                },
                # Enhanced anti-detection options
                'extractor_retries': 5,
                'fragment_retries': 5,
                'retry_sleep_functions': {'http': lambda n: min(2**n, 30)},  # Max 30 seconds
                'sleep_interval': 2,  # Sleep between requests
                'max_sleep_interval': 10,  # Max sleep interval
                'sleep_interval_requests': 1,  # Sleep after N requests
                'throttledratelimit': 100,  # Rate limit
                'concurrent_fragment_downloads': 1,  # Reduce concurrent downloads
                'file_access_retries': 3,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                        'player_skip': ['webpage', 'configs'],
                    }
                }
            }
            
            # Try multiple download strategies
            download_success = False
            video_file = None
            
            # Strategy 1: Try with enhanced options
            try:
                logger.info(f"Attempting download with enhanced options...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    await asyncio.get_event_loop().run_in_executor(
                        None, ydl.download, [str(youtube_url)]
                    )
                
                video_file = self._find_downloaded_file(task_id)
                if video_file and os.path.exists(video_file):
                    download_success = True
                    logger.info(f"Download successful with enhanced options: {video_file}")
                    
            except Exception as e:
                logger.warning(f"Enhanced download failed: {str(e)}")
            
            # Strategy 2: Try with simpler format if first attempt failed
            if not download_success:
                try:
                    logger.info(f"Attempting download with simpler format...")
                    simple_opts = ydl_opts.copy()
                    simple_opts['format'] = 'best[ext=mp4]/best'  # Simpler format selection
                    simple_opts['http_headers'] = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    with yt_dlp.YoutubeDL(simple_opts) as ydl:
                        await asyncio.get_event_loop().run_in_executor(
                            None, ydl.download, [str(youtube_url)]
                        )
                    
                    video_file = self._find_downloaded_file(task_id)
                    if video_file and os.path.exists(video_file):
                        download_success = True
                        logger.info(f"Download successful with simple format: {video_file}")
                        
                except Exception as e:
                    logger.warning(f"Simple format download failed: {str(e)}")
            
            # Strategy 3: Try with audio-only if video download failed
            if not download_success:
                try:
                    logger.info(f"Attempting audio-only download...")
                    audio_opts = ydl_opts.copy()
                    audio_opts['format'] = 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio'
                    audio_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                    
                    with yt_dlp.YoutubeDL(audio_opts) as ydl:
                        await asyncio.get_event_loop().run_in_executor(
                            None, ydl.download, [str(youtube_url)]
                        )
                    
                    video_file = self._find_downloaded_file(task_id)
                    if video_file and os.path.exists(video_file):
                        download_success = True
                        logger.info(f"Audio download successful: {video_file}")
                        
                except Exception as e:
                    logger.warning(f"Audio download failed: {str(e)}")
            
            if not download_success or not video_file or not os.path.exists(video_file):
                error_msg = (
                    "All download strategies failed. YouTube may be blocking downloads. "
                    "Please try uploading the video file directly instead of using YouTube URL. "
                    "You can download the video manually and upload it to the system."
                )
                raise Exception(error_msg)
            
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
            logger.info(f"Validating URL: {repr(url)}, type: {type(url)}")
            parsed = urlparse(str(url))  # Ensure it's a string
            logger.info(f"Parsed: netloc={parsed.netloc}, path={parsed.path}, query={parsed.query}")
            
            # Check for various YouTube URL formats
            youtube_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com']
            
            if parsed.netloc in youtube_domains:
                if parsed.netloc == 'youtu.be':
                    result = bool(parsed.path.strip('/'))
                    logger.info(f"youtu.be validation result: {result}")
                    return result
                else:
                    query_params = parse_qs(parsed.query)
                    result = 'v' in query_params
                    logger.info(f"youtube.com validation result: {result}")
                    return result
            
            logger.info(f"Domain not in youtube_domains: {parsed.netloc}")
            return False
            
        except Exception as e:
            logger.error(f"URL validation error: {e}")
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
        Find the downloaded video or audio file
        """
        # Video extensions
        video_extensions = ['mp4', 'webm', 'mkv', 'avi']
        # Audio extensions
        audio_extensions = ['mp3', 'm4a', 'wav', 'ogg']
        
        # First try video files
        for ext in video_extensions:
            file_path = os.path.join(self.upload_dir, f"video_{task_id}.{ext}")
            if os.path.exists(file_path):
                logger.info(f"Found video file: {file_path}")
                return file_path
        
        # Then try audio files
        for ext in audio_extensions:
            file_path = os.path.join(self.upload_dir, f"video_{task_id}.{ext}")
            if os.path.exists(file_path):
                logger.info(f"Found audio file: {file_path}")
                return file_path
        
        # Check for any file with the task_id pattern
        import glob
        pattern = os.path.join(self.upload_dir, f"video_{task_id}.*")
        files = glob.glob(pattern)
        if files:
            logger.info(f"Found files with task_id pattern: {files}")
            return files[0]  # Return the first found file
        
        logger.warning(f"No downloaded file found for task {task_id}")
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