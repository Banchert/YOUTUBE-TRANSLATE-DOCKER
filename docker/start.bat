@echo off
setlocal enabledelayedexpansion

REM YouTube Video Translator - Docker Startup Script for Windows
REM Version: 2.0.0

echo 🚀 YouTube Video Translator - Docker Startup Script
echo ==================================================
echo.

REM Check if Docker is running
echo [INFO] Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)
echo [SUCCESS] Docker is running

REM Check if Docker Compose is available
echo [INFO] Checking Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not available. Please install Docker Compose first.
    pause
    exit /b 1
)
echo [SUCCESS] Docker Compose is available

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "..\uploads" mkdir "..\uploads"
if not exist "..\output" mkdir "..\output"
if not exist "..\logs" mkdir "..\logs"
if not exist "..\temp" mkdir "..\temp"
if not exist "ssl" mkdir "ssl"
echo [SUCCESS] Directories created

REM Setup environment file
if not exist ".env" (
    echo [INFO] Creating .env file from template...
    copy "env.example" ".env" >nul
    echo [WARNING] Please edit .env file with your configuration before starting services
) else (
    echo [SUCCESS] .env file already exists
)

REM Parse command line arguments
set "mode=%1"
if "%mode%"=="" set "mode=default"

if "%mode%"=="simple" (
    set "compose_file=docker-compose-dev.yml"
) else if "%mode%"=="prod" (
    set "compose_file=docker-compose.prod.yml"
) else if "%mode%"=="monitoring" (
    set "compose_file=docker-compose.prod.yml"
    set "monitoring=true"
) else if "%mode%"=="logs" (
    echo [INFO] Showing logs (Ctrl+C to exit)...
    docker-compose logs -f
    pause
    exit /b 0
) else if "%mode%"=="status" (
    echo [INFO] Service Status:
    docker-compose ps
    echo.
    echo [INFO] Resource Usage:
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    pause
    exit /b 0
) else if "%mode%"=="stop" (
    echo [INFO] Stopping all services...
    docker-compose down
    echo [SUCCESS] Services stopped
    pause
    exit /b 0
) else if "%mode%"=="restart" (
    echo [INFO] Restarting services...
    docker-compose restart
    echo [SUCCESS] Services restarted
    pause
    exit /b 0
) else if "%mode%"=="clean" (
    echo [INFO] Cleaning up Docker resources...
    docker-compose down --volumes --remove-orphans
    docker system prune -f
    echo [SUCCESS] Cleanup completed
    pause
    exit /b 0
) else (
    set "compose_file=docker-compose-dev.yml"
)

REM Build and start services
echo [INFO] Building and starting services using %compose_file%...

REM Stop existing services
echo [INFO] Stopping existing services...
docker-compose -f %compose_file% down --remove-orphans

REM Build images
echo [INFO] Building Docker images...
docker-compose -f %compose_file% build --no-cache

REM Start services
echo [INFO] Starting services...
docker-compose -f %compose_file% up -d

REM Start monitoring if requested
if "%monitoring%"=="true" (
    echo [INFO] Starting monitoring services...
    docker-compose -f %compose_file% --profile monitoring up -d
)

echo [SUCCESS] Services started successfully

REM Wait for services to be ready
echo [INFO] Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Show service status
echo [INFO] Service Status:
docker-compose -f %compose_file% ps

echo.
echo [INFO] Resource Usage:
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

REM Show access URLs
echo.
echo [SUCCESS] 🎉 YouTube Video Translator is ready!
echo.
echo 📱 Access URLs:
echo    Frontend:     http://localhost:3000
echo    Backend API:  http://localhost:8000/docs
echo    Whisper:      http://localhost:5001/health
echo    TTS:          http://localhost:5002/health
echo    Translation:  http://localhost:5000
echo    Redis:        http://localhost:6379
echo    PostgreSQL:   localhost:5432
echo.
echo 📝 Useful commands:
echo    View logs:    docker-compose logs -f [service]
echo    Stop:         docker-compose down
echo    Restart:      docker-compose restart [service]
echo    Status:       docker-compose ps
echo.

pause 