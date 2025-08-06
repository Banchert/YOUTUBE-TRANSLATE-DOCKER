@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    YouTube Video Translator Status
echo ========================================
echo.

:: Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [31m✗ Docker ไม่ทำงาน[0m
    echo กรุณาเริ่ม Docker Desktop ก่อน
    pause
    exit /b 1
)

echo [32m✓ Docker ทำงานปกติ[0m
echo.

:: Check Docker containers
echo ตรวจสอบ Services:
echo =============

:: Check Backend API
docker exec docker-backend-1 curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo Backend API:       [32m✓ ทำงานปกติ[0m
) else (
    echo Backend API:       [31m✗ ไม่ตอบสนอง[0m
)

:: Check Frontend
docker exec docker-frontend-1 curl -f http://localhost:80 >nul 2>&1
if %errorlevel% equ 0 (
    echo Frontend:          [32m✓ ทำงานปกติ[0m
) else (
    echo Frontend:          [31m✗ ไม่ตอบสนอง[0m
)

:: Check Translation API (LibreTranslate)
powershell -Command "try { Invoke-WebRequest -Uri http://localhost:5000/languages -UseBasicParsing -TimeoutSec 5 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    echo Translation API:   [32m✓ ทำงานปกติ[0m
) else (
    echo Translation API:   [31m✗ ไม่ตอบสนอง[0m
)

:: Check Redis
docker exec docker-redis-1 redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo Redis:             [32m✓ ทำงานปกติ[0m
) else (
    echo Redis:             [31m✗ ไม่ตอบสนอง[0m
)

:: Check Whisper Service
docker exec docker-whisper-service-1 curl -f http://localhost:5001/health >nul 2>&1
if %errorlevel% equ 0 (
    echo Whisper Service:   [32m✓ ทำงานปกติ[0m
) else (
    echo Whisper Service:   [31m✗ ไม่ตอบสนอง[0m
)

:: Check TTS Service
docker exec docker-tts-service-1 curl -f http://localhost:5002/health >nul 2>&1
if %errorlevel% equ 0 (
    echo TTS Service:       [32m✓ ทำงานปกติ[0m
) else (
    echo TTS Service:       [31m✗ ไม่ตอบสนอง[0m
)

echo.
echo เว็บไซต์:
echo =========
echo   Frontend:           http://localhost:3000
echo   API Documentation:  http://localhost:8000/docs
echo   Translation API:    http://localhost:5000
echo   Whisper Service:    http://localhost:5001
echo   TTS Service:        http://localhost:5002
echo   Redis:              localhost:6379
echo   PostgreSQL:         localhost:5432
echo.

echo Press any key to continue . . .
pause >nul
