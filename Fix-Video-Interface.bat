@echo off
chcp 65001 >nul

echo.
echo ====================================================
echo    แก้ไข Video Player Interface - Test & Fix
echo ====================================================
echo.

echo [INFO] เริ่มการทดสอบและแก้ไข Video Player Interface...

echo [INFO] 1. ตรวจสอบ Docker...
docker info >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Docker ไม่ได้เริ่มต้นการทำงาน
    echo [INFO] กรุณาเปิด Docker Desktop ก่อนใช้งาน
    pause
    exit /b 1
)

echo [SUCCESS] Docker พร้อมใช้งาน

echo [INFO] 2. เริ่มบริการ Backend...
cd docker
docker compose -f docker-compose-simple.yml up -d backend

echo [INFO] 3. รอให้ Backend เริ่มต้น...
timeout /t 15 >nul

echo [INFO] 4. ตรวจสอบการทำงานของ Backend...
curl -s http://localhost:8000/health >nul
if %errorLevel% neq 0 (
    echo [WARNING] Backend ยังไม่พร้อม รอเพิ่มเติม...
    timeout /t 10 >nul
)

echo [INFO] 5. ทดสอบไฟล์ demo video...
curl -I http://localhost:8000/download/task-1754404431054

cd ..

echo.
echo [SUCCESS] ระบบ Backend เริ่มต้นแล้ว!
echo.
echo 🧪 การทดสอบ Video Player Interface:
echo    Test Page:          file:///d:/YOUTUBE-TRANSLATE/test-video-playback.html
echo    Backend API:        http://localhost:8000
echo    API Documentation:  http://localhost:8000/docs
echo    Health Check:       http://localhost:8000/health
echo.

set /p open_test="ต้องการเปิดหน้าทดสอบหรือไม่? (y/n): "
if /i "%open_test%"=="y" (
    start file:///d:/YOUTUBE-TRANSLATE/test-video-playback.html
    timeout /t 2 >nul
    start http://localhost:8000/docs
    echo [SUCCESS] เปิดหน้าทดสอบแล้ว
)

echo.
echo 📋 ขั้นตอนการทดสอบ:
echo   1. ตรวจสอบการเชื่อมต่อ Backend (ควรเป็น ✅)
echo   2. ตรวจสอบไฟล์วิดีโอ (ควรเป็น ✅) 
echo   3. ทดสอบการโหลดวิดีโอในเบราว์เซอร์
echo   4. หากไม่สามารถเล่นได้ ให้ใช้ปุ่มดาวน์โหลด
echo.

echo 🛠️  การแก้ไขที่ทำไปแล้ว:
echo   • เพิ่มการตรวจสอบสถานะ Backend และไฟล์
echo   • เพิ่ม Error Handling ที่ดีขึ้น
echo   • เพิ่มปุ่มดาวน์โหลดเมื่อเล่นไม่ได้
echo   • แก้ไข URL Construction ใน ProcessingStatus
echo   • เพิ่ม CORS และ Loading States
echo.

pause
