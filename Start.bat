@echo off
chcp 65001 >nul

echo.
echo ==========================================
echo    เริ่มใช้งาน YouTube Video Translator
echo ==========================================
echo.

echo [INFO] ตรวจสอบ Docker...
docker info >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Docker ไม่ได้เริ่มต้นการทำงาน
    echo [INFO] กรุณาเปิด Docker Desktop ก่อนใช้งาน
    pause
    exit /b 1
)

echo [SUCCESS] Docker พร้อมใช้งาน

echo [INFO] เริ่มบริการทั้งหมด...
cd docker

:: ตรวจสอบว่ามี docker-compose หรือ docker compose
docker-compose --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] ใช้ Docker Compose แบบใหม่...
    docker compose -f docker-compose-simple.yml up -d
) else (
    echo [INFO] ใช้ Docker Compose แบบเดิม...
    docker-compose -f docker-compose-simple.yml up -d
)

if %errorLevel% neq 0 (
    echo [ERROR] ไม่สามารถเริ่มบริการได้
    pause
    exit /b 1
)

cd ..

echo [INFO] รอให้บริการเริ่มต้น...
timeout /t 30 >nul

echo.
echo [SUCCESS] ระบบเริ่มต้นแล้ว!
echo.
echo 🌐 เข้าใช้งานผ่าน:
echo    Frontend:           http://localhost:3000
echo    Backend API:        http://localhost:8000
echo    API Documentation:  http://localhost:8000/docs
echo    Translation API:    http://localhost:5000
echo.

set /p open_browser="ต้องการเปิดเว็บแอปหรือไม่? (y/n): "
if /i "%open_browser%"=="y" (
    start http://localhost:3000
    timeout /t 2 >nul
    start http://localhost:8000/docs
    echo [SUCCESS] เปิดเว็บแอปแล้ว
)

echo.
echo กด Enter เพื่อดู logs แบบ real-time หรือ Ctrl+C เพื่อออก...
pause >nul

cd docker
docker-compose logs -f
cd ..
