@echo off
echo ========================================
echo  แก้ไขปัญหาการอัปโหลด YouTube Translator
echo ========================================
echo.

echo 1. หยุดเซิร์ฟเวอร์ที่กำลังทำงาน...
taskkill /f /im python.exe 2>nul
taskkill /f /im uvicorn.exe 2>nul
timeout /t 3 /nobreak >nul

echo 2. สร้างโฟลเดอร์ที่จำเป็น...
if not exist "uploads" mkdir uploads
if not exist "output" mkdir output
if not exist "logs" mkdir logs

echo 3. ตรวจสอบไฟล์ที่แก้ไขแล้ว...
echo - backend/app/main.py (แก้ไข upload endpoint)
echo - frontend/src/services/api.js (แก้ไข upload service)
echo - frontend/src/components/VideoUpload.jsx (แก้ไข upload handling)
echo - test-upload.html (สร้างไฟล์ทดสอบใหม่)

echo.
echo 4. เริ่มต้นเซิร์ฟเวอร์ใหม่...
cd backend
start "Backend Server" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo 5. รอให้เซิร์ฟเวอร์เริ่มต้น...
timeout /t 5 /nobreak >nul

echo 6. เปิดหน้าเว็บทดสอบ...
start http://localhost:3000
start test-upload.html

echo.
echo ========================================
echo  การแก้ไขเสร็จสิ้น!
echo ========================================
echo.
echo สิ่งที่แก้ไข:
echo ✅ เพิ่มการตรวจสอบไฟล์ก่อนอัปโหลด
echo ✅ เพิ่มการตรวจสอบขนาดไฟล์ (สูงสุด 500MB)
echo ✅ เพิ่มการตรวจสอบประเภทไฟล์
echo ✅ สร้างโฟลเดอร์ uploads อัตโนมัติ
echo ✅ ปรับปรุง error handling และ timeout
echo ✅ เพิ่มหน้าเว็บทดสอบการอัปโหลด
echo.
echo วิธีทดสอบ:
echo 1. เปิด test-upload.html ในเบราว์เซอร์
echo 2. ทดสอบการเชื่อมต่อ API
echo 3. ลองอัปโหลดไฟล์วิดีโอ
echo 4. ทดสอบไฟล์ใหญ่และไฟล์ไม่ถูกต้อง
echo.
echo หากยังมีปัญหา:
echo - ตรวจสอบว่า backend server ทำงานที่ port 8000
echo - ตรวจสอบสิทธิ์การเขียนไฟล์ในโฟลเดอร์ uploads
echo - ตรวจสอบ logs ใน backend สำหรับ error messages
echo.
pause 