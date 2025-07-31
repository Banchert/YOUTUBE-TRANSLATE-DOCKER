@echo off
chcp 65001 >nul

echo.
echo ==========================================
echo    Fix Missing Components
echo ==========================================
echo.

echo [INFO] Creating missing UI components...

:: Now let's create a script to rebuild just the frontend
cd docker

echo [INFO] Building Frontend...
docker-compose -f docker-compose-simple.yml build frontend --no-cache

echo [INFO] Restarting Frontend...
docker-compose -f docker-compose-simple.yml up -d frontend

cd ..

echo.
echo [SUCCESS] ระบบพร้อมใช้งาน!
echo.
echo 🌐 เข้าใช้งานผ่าน:
echo    Frontend:           http://localhost:3000
echo    Backend API:        http://localhost:8000
echo    API Documentation:  http://localhost:8000/docs
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
