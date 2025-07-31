@echo off
chcp 65001 >nul

echo.
echo ==========================================
echo    Build YouTube Video Translator
echo ==========================================
echo.

echo [INFO] หยุดบริการเดิม...
cd docker
docker-compose -f docker-compose-simple.yml down
cd ..

echo [INFO] Build Docker Images...
cd docker

echo [INFO] Building Backend...
docker-compose -f docker-compose-simple.yml build backend

echo [INFO] Building Frontend...
docker-compose -f docker-compose-simple.yml build frontend

echo [INFO] Building อื่นๆ...
docker-compose -f docker-compose-simple.yml build

cd ..

echo [SUCCESS] Build เสร็จแล้ว!

echo.
echo [INFO] เริ่มบริการใหม่...
cd docker
docker-compose -f docker-compose-simple.yml up -d
cd ..

echo.
echo [INFO] รอให้บริการเริ่มต้น...
timeout /t 30 >nul

echo.
echo [SUCCESS] ระบบพร้อมใช้งาน!
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
pause
