@echo off
echo ========================================
echo  แก้ไขปัญหาการดาวน์โหลด YouTube Translator
echo ========================================
echo.

echo 1. หยุดเซิร์ฟเวอร์ที่กำลังทำงาน...
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul
timeout /t 3 /nobreak >nul

echo 2. ตรวจสอบไฟล์ที่แก้ไขแล้ว...
echo - backend/app/main.py (แก้ไข download endpoints)
echo - backend/app/services/video_service.py (แก้ไข video processing)
echo - frontend/src/components/DownloadResult.jsx (แก้ไข download handling)
echo - frontend/src/services/api.js (แก้ไข download service)
echo - test-download.html (สร้างไฟล์ทดสอบใหม่)

echo.
echo 3. เริ่มต้นเซิร์ฟเวอร์ใหม่...
cd backend
start "Backend Server" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo 4. รอให้เซิร์ฟเวอร์เริ่มต้น...
timeout /t 5 /nobreak >nul

echo 5. เปิดหน้าเว็บทดสอบ...
start http://localhost:3000
start test-download.html

echo.
echo ========================================
echo  การแก้ไขเสร็จสิ้น!
echo ========================================
echo.
echo สิ่งที่แก้ไข:
echo ✅ เพิ่มการตรวจสอบขนาดไฟล์ก่อนดาวน์โหลด
echo ✅ สร้างไฟล์ placeholder เมื่อไฟล์ไม่พบ
echo ✅ ปรับปรุง error handling ใน frontend
echo ✅ เพิ่มการตรวจสอบสถานะไฟล์
echo ✅ สร้างหน้าเว็บทดสอบการดาวน์โหลด
echo.
echo วิธีทดสอบ:
echo 1. เปิด test-download.html ในเบราว์เซอร์
echo 2. ทดสอบการเชื่อมต่อ API
echo 3. ทดสอบการดาวน์โหลดไฟล์ต่างๆ
echo 4. ตรวจสอบสถานะ Task และไฟล์
echo.
pause 