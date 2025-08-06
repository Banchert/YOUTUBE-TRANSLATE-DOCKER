@echo off
chcp 65001 >nul

echo.
echo ==========================================
echo    แก้ไขปัญหา LibreTranslate Service
echo ==========================================
echo.

cd docker

:: ตรวจสอบสถานะ container
echo [INFO] ตรวจสอบสถานะ containers...
docker compose -f docker-compose-simple.yml ps

echo.
echo [INFO] ตรวจสอบ logs ของ LibreTranslate...
echo =========================================
docker compose -f docker-compose-simple.yml logs libretranslate --tail=20

echo.
echo [INFO] รีสตาร์ท LibreTranslate service...
docker compose -f docker-compose-simple.yml restart libretranslate

echo [INFO] รอให้ LibreTranslate เริ่มต้น (อาจใช้เวลา 2-5 นาที)...
echo [INFO] LibreTranslate กำลังดาวน์โหลด language models...

:: รอและตรวจสอบสถานะทุก 15 วินาที
for /L %%i in (1,1,20) do (
    timeout /t 15 >nul
    echo [INFO] ตรวจสอบครั้งที่ %%i/20...
    
    :: ทดสอบการเชื่อมต่อ
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000/languages' -TimeoutSec 10 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host '[SUCCESS] LibreTranslate พร้อมใช้งาน!' -ForegroundColor Green; exit 0 } } catch { Write-Host '[WAITING] ยังไม่พร้อม...' -ForegroundColor Yellow }" >nul 2>&1
    
    if %errorLevel% equ 0 (
        echo [SUCCESS] LibreTranslate พร้อมใช้งานแล้ว!
        goto :ready
    )
    
    echo    - ยังไม่พร้อม, รอต่อ...
)

echo [WARNING] LibreTranslate ใช้เวลานานกว่าปกติ
echo [INFO] ตรวจสอบ logs ล่าสุด:
docker compose -f docker-compose-simple.yml logs libretranslate --tail=10

goto :end

:ready
echo.
echo =========================================
echo [SUCCESS] LibreTranslate พร้อมใช้งาน!
echo =========================================

:: ทดสอบการแปล
echo [INFO] ทดสอบการแปลภาษา...
powershell -Command "try { $body = @{ q='Hello'; source='en'; target='th' } | ConvertTo-Json; $response = Invoke-RestMethod -Uri 'http://localhost:5000/translate' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 15; Write-Host ('[SUCCESS] ทดสอบการแปล: Hello -> ' + $response.translatedText) -ForegroundColor Green } catch { Write-Host '[ERROR] การทดสอบแปลล้มเหลว' -ForegroundColor Red }"

echo.
echo ✅ ระบบพร้อมใช้งานแล้ว!
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000/docs
echo    Translation: http://localhost:5000

:end
cd ..
pause
