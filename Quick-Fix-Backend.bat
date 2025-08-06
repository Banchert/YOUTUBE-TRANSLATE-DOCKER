@echo off
chcp 65001 >nul

echo.
echo ============================================
echo    แก้ไขปัญหาการเชื่อมต่อ Backend
echo ============================================
echo.

echo [INFO] ตรวจสอบและเริ่ม Docker Services...

:: Check if Docker is running
echo [1/5] ตรวจสอบ Docker...
docker info >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Docker ไม่ทำงาน!
    echo.
    echo 💡 การแก้ไข:
    echo    1. เปิด Docker Desktop
    echo    2. รอให้แสดง "Docker Desktop is running"
    echo    3. รันไฟล์นี้อีกครั้ง
    echo.
    pause
    exit /b 1
)
echo [SUCCESS] Docker พร้อมใช้งาน

:: Go to docker directory
echo [2/5] เปลี่ยนไปยัง docker directory...
cd /d "d:\YOUTUBE-TRANSLATE\docker"
if %errorLevel% neq 0 (
    echo [ERROR] ไม่พบโฟลเดอร์ docker
    pause
    exit /b 1
)

:: Stop existing containers first
echo [3/5] หยุด containers เดิม...
docker compose -f docker-compose-simple.yml down >nul 2>&1

:: Start services
echo [4/5] เริ่ม Docker Services...
docker compose -f docker-compose-simple.yml up -d

if %errorLevel% neq 0 (
    echo [ERROR] ไม่สามารถเริ่มบริการได้
    echo.
    echo 🔍 ลองตรวจสอบ:
    echo    docker compose -f docker-compose-simple.yml logs
    pause
    exit /b 1
)

:: Wait for services to start
echo [5/5] รอให้บริการเริ่มต้น...
echo กำลังรอ 30 วินาที...
timeout /t 30 >nul

:: Test backend
echo.
echo ทดสอบ Backend...
curl -s http://localhost:8000/health >nul
if %errorLevel% equ 0 (
    echo [SUCCESS] ✅ Backend พร้อมใช้งาน!
) else (
    echo [WARNING] ⚠️ Backend ยังไม่พร้อม - ลองรออีก 30 วินาที
)

:: Show status
echo.
echo ===============================================
echo               สถานะบริการ
echo ===============================================
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ===============================================
echo                ลิงก์ทดสอบ
echo ===============================================
echo Backend API:      http://localhost:8000/docs
echo Health Check:     http://localhost:8000/health  
echo Frontend:         http://localhost:3000
echo Translation API:  http://localhost:5000
echo.

set /p test_now="ต้องการทดสอบ Video Interface ตอนนี้หรือไม่? (y/n): "
if /i "%test_now%"=="y" (
    echo.
    echo เปิดหน้าทดสอบ...
    start "" "d:\YOUTUBE-TRANSLATE\test-video-playback.html"
    timeout /t 2 >nul
    start http://localhost:8000/docs
    echo.
    echo [INFO] เปิดหน้าทดสอบแล้ว - ตรวจสอบการทำงานในเบราว์เซอร์
)

echo.
echo 📋 หากยังมีปัญหา:
echo    1. ตรวจสอบ Docker Desktop เปิดอยู่
echo    2. รอ 1-2 นาที แล้วลองใหม่
echo    3. ดู logs: docker compose logs backend
echo    4. รีสตาร์ท: docker compose restart
echo.

cd /d "d:\YOUTUBE-TRANSLATE"
pause
