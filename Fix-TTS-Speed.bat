@echo off
chcp 65001 >nul

echo.
echo ==========================================
echo    แก้ไขปัญหาการแปลและ TTS
echo ==========================================
echo.

cd docker

echo [INFO] รีสตาร์ท TTS Service เพื่อใช้การตั้งค่าใหม่...
docker compose -f docker-compose-simple.yml restart tts-service

echo [INFO] รอให้ TTS Service เริ่มต้น...
timeout /t 15 >nul

echo [INFO] ทดสอบ TTS Service...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5002/health' -TimeoutSec 10 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host '[SUCCESS] TTS Service พร้อมใช้งาน' -ForegroundColor Green } else { Write-Host '[ERROR] TTS Service ยังไม่พร้อม' -ForegroundColor Red } } catch { Write-Host '[ERROR] TTS Service ไม่ตอบสนอง' -ForegroundColor Red }"

echo.
echo [INFO] ทดสอบคุณภาพการแปลและ TTS...
cd ..
python test_translation_quality.py

echo.
echo ==========================================
echo [INFO] การแก้ไขเสร็จสิ้น!
echo ==========================================
echo.
echo 🔧 การแก้ไขที่ทำ:
echo    1. ปรับความเร็ว TTS เป็น 85%% (ช้าลง)
echo    2. เพิ่ม SSML สำหรับควบคุมเสียงดีขึ้น
echo    3. เปลี่ยน Google TTS เป็น slow=True
echo    4. ทดสอบคุณภาพการแปลและเสียง
echo.
echo 🎯 ผลลัพธ์ที่คาดหวัง:
echo    - เสียงไทยช้าลงและชัดขึ้น
echo    - การแปลถูกต้องมากขึ้น
echo    - ไม่มีเสียงแปลกๆ ปนกัน
echo.

pause
