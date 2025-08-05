@echo off
chcp 65001 >nul

echo.
echo ==========================================
echo    สถานะ YouTube Video Translator
echo ==========================================
echo.

echo [INFO] ตรวจสอบ Docker...
docker info >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Docker ไม่ได้เริ่มต้นการทำงาน
    goto :docker_error
)

echo [SUCCESS] Docker กำลังทำงาน
echo.

echo สถานะ Containers:
echo ==================
cd docker

:: ตรวจสอบว่าใช้ docker-compose.yml หรือ docker-compose-simple.yml
docker compose -f docker-compose.yml ps >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] ใช้การตั้งค่าแบบเต็ม (Full Setup)
    set "COMPOSE_FILE=docker-compose.yml"
    set "FULL_SETUP=true"
) else (
    echo [INFO] ใช้การตั้งค่าแบบง่าย (Simple Setup)
    set "COMPOSE_FILE=docker-compose-simple.yml"
    set "FULL_SETUP=false"
)

docker compose -f %COMPOSE_FILE% ps

cd ..
echo.

echo สถานะบริการ:
echo =============

:: ตรวจสอบ Backend
echo | set /p="Backend API:       "
curl -f http://localhost:8000/health >nul 2>&1
if %errorLevel% equ 0 (
    echo [32m✓ ทำงานปกติ[0m
) else (
    echo [31m✗ ไม่ตอบสนอง[0m
)

:: ตรวจสอบ Frontend
echo | set /p="Frontend:          "
curl -f http://localhost:3000 >nul 2>&1
if %errorLevel% equ 0 (
    echo [32m✓ ทำงานปกติ[0m
) else (
    echo [31m✗ ไม่ตอบสนอง[0m
)

:: ตรวจสอบ Translation Service
echo | set /p="Translation API:   "
timeout /t 1 /nobreak >nul 2>&1
powershell -Command "Test-NetConnection -ComputerName localhost -Port 5000 -InformationLevel Quiet" >nul 2>&1
if %errorLevel% equ 0 (
    echo [32m✓ ทำงานปกติ[0m
) else (
    echo [31m✗ ไม่ตอบสนอง[0m
)

:: ตรวจสอบ Whisper Service (เฉพาะ Full Setup)
if "%FULL_SETUP%"=="true" (
    echo | set /p="Whisper Service:   "
    curl -f http://localhost:5001/health >nul 2>&1
    if %errorLevel% equ 0 (
        echo [32m✓ ทำงานปกติ[0m
    ) else (
        echo [31m✗ ไม่ตอบสนอง[0m
    )
)

:: ตรวจสอบ TTS Service (เฉพาะ Full Setup)
if "%FULL_SETUP%"=="true" (
    echo | set /p="TTS Service:       "
    curl -f http://localhost:5002/health >nul 2>&1
    if %errorLevel% equ 0 (
        echo [32m✓ ทำงานปกติ[0m
    ) else (
        echo [31m✗ ไม่ตอบสนอง[0m
    )
)

:: ตรวจสอบ Redis (ใช้ redis-cli แทน curl)
echo | set /p="Redis:             "
docker exec docker-redis-1 redis-cli ping >nul 2>&1
if %errorLevel% equ 0 (
    echo [32m✓ ทำงานปกติ[0m
) else (
    echo [31m✗ ไม่ตอบสนอง[0m
)

echo.
echo เว็บไซต์:
echo =========
echo   Frontend:           http://localhost:3000
echo   API Documentation:  http://localhost:8000/docs
echo   Translation API:    http://localhost:5000
echo   Celery Monitor:     http://localhost:5555
echo.

goto :end

:docker_error
echo [ERROR] Docker ไม่ได้เริ่มต้นการทำงาน
echo.
echo วิธีแก้ไข:
echo 1. เปิด Docker Desktop
echo 2. รอให้ Docker เริ่มต้นการทำงาน (ดูไอคอนใน system tray)
echo 3. รันสคริปต์นี้อีกครั้ง
echo.

:end
pause
