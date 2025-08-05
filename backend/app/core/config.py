# backend/app/core/config.py
import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "YouTube Video Translator"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "output")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "500")) * 1024 * 1024  # 500MB
    
    # Processing Configuration
    MAX_VIDEO_DURATION: int = int(os.getenv("MAX_VIDEO_DURATION", "0"))  # 0 = ไม่จำกัด
    MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", "0"))  # 0 = ไม่จำกัด
    CONCURRENT_TASKS: int = int(os.getenv("CONCURRENT_TASKS", "5"))  # เพิ่มจำนวน concurrent tasks
    TASK_TIMEOUT: int = int(os.getenv("TASK_TIMEOUT", "14400"))  # 4 hours
    
    # External Services
    WHISPER_SERVICE_URL: str = os.getenv("WHISPER_SERVICE_URL", "http://localhost:5001")
    TTS_SERVICE_URL: str = os.getenv("TTS_SERVICE_URL", "http://localhost:5002")
    TRANSLATION_SERVICE_URL: str = os.getenv("TRANSLATION_SERVICE_URL", "http://localhost:5000")
    
    # Whisper Configuration
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "medium")
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "cpu")  # cpu, cuda
    
    # TTS Configuration
    TTS_MODEL_TH: str = os.getenv("TTS_MODEL_TH", "tts_models/th/mai_female/glow-tts")
    TTS_SAMPLE_RATE: int = int(os.getenv("TTS_SAMPLE_RATE", "22050"))
    
    # Translation Configuration
    TRANSLATION_API_KEY: str = os.getenv("TRANSLATION_API_KEY", "")
    DEFAULT_SOURCE_LANG: str = os.getenv("DEFAULT_SOURCE_LANG", "auto")
    DEFAULT_TARGET_LANG: str = os.getenv("DEFAULT_TARGET_LANG", "th")
    
    # FFmpeg Configuration
    FFMPEG_BINARY: str = os.getenv("FFMPEG_BINARY", "ffmpeg")
    AUDIO_CODEC: str = os.getenv("AUDIO_CODEC", "aac")
    VIDEO_CODEC: str = os.getenv("VIDEO_CODEC", "libx264")
    AUDIO_BITRATE: str = os.getenv("AUDIO_BITRATE", "128k")
    VIDEO_QUALITY: str = os.getenv("VIDEO_QUALITY", "720p")
    
    # Redis Configuration (for production)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # Celery Configuration (for production)
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    
    # Monitoring
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "False").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()

# Supported languages for translation
SUPPORTED_LANGUAGES = {
    "th": "Thai",
    "en": "English", 
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ar": "Arabic",
    "hi": "Hindi"
}

# TTS Models mapping
TTS_MODELS = {
    "th": {
        "female": "tts_models/th/mai_female/glow-tts",
        "male": "tts_models/th/mai_male/glow-tts"
    },
    "en": {
        "female": "tts_models/en/ljspeech/tacotron2-DDC",
        "male": "tts_models/en/sam/tacotron-DDC"
    },
    "zh": {
        "female": "tts_models/zh-CN/baker/tacotron2-DDC-GST"
    }
}

# Audio mixing options
AUDIO_MIXING_OPTIONS = {
    "overlay": "Mix translated audio over original (lower original volume)",
    "replace": "Replace original audio completely", 
    "stereo": "Original audio on left channel, translated on right channel"
}

# FFmpeg filter configurations
FFMPEG_FILTERS = {
    "overlay": "[0:a]volume=0.2[a1];[a1][1:a]amix=inputs=2[a]",
    "replace": "",  # Just map the new audio
    "stereo": "[0:a][1:a]join=inputs=2:channel_layout=stereo[a]"
}

# Video quality presets
VIDEO_QUALITY_PRESETS = {
    "720p": {
        "height": 720,
        "bitrate": "2500k",
        "preset": "medium"
    },
    "480p": {
        "height": 480,
        "bitrate": "1500k", 
        "preset": "fast"
    },
    "1080p": {
        "height": 1080,
        "bitrate": "4000k",
        "preset": "slow"
    }
}