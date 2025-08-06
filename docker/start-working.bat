@echo off
echo Starting YouTube Video Translator (Working Version)...

REM Stop existing services
docker-compose -f docker-compose-working.yml down

REM Remove old volumes
docker volume rm docker_redis_data 2>nul
docker volume rm docker_whisper_cache 2>nul
docker volume rm docker_tts_cache 2>nul

REM Build and start services
docker-compose -f docker-compose-working.yml up -d --build

echo.
echo Waiting for services to start...
timeout /t 30 /nobreak >nul

echo.
echo Service Status:
docker-compose -f docker-compose-working.yml ps

echo.
echo Access URLs:
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000/docs
echo Translation: http://localhost:5000
echo.
pause 