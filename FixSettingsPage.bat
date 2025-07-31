@echo off
chcp 65001 >nul

echo.
echo ==========================================
echo    Fix SettingsPage and Rebuild Frontend
echo ==========================================
echo.

echo [INFO] SettingsPage.jsx ถูกแก้ไขแล้ว เริ่มการ Build ใหม่...

:: Now let's create a script to rebuild just the frontend
cd docker

echo [INFO] Building Frontend...
docker-compose -f docker-compose-simple.yml build frontend --no-cache

echo [INFO] Restarting Frontend...
docker-compose -f docker-compose-simple.yml up -d frontend

cd ..

echo.
echo [SUCCESS] แก้ไขและ Build Frontend ใหม่เรียบร้อยแล้ว!
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
