@echo off
echo Rebuilding Docker containers with TTS fix...
echo.

cd /d "%~dp0"

REM Check if Docker is available
docker --version >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed or not in PATH
    pause
    exit /b 1
)

REM Stop existing containers
echo Stopping existing containers...
docker-compose -f docker/docker-compose.yml down

REM Rebuild the backend container
echo Rebuilding backend container...
docker-compose -f docker/docker-compose.yml build backend

REM Start the services
echo Starting services...
docker-compose -f docker/docker-compose.yml up -d

echo.
echo Rebuild completed. The TTS fix should now be active.
echo You can test it by running: test_tts_fix.bat
pause 