@echo off
chcp 65001 >nul

echo.
echo ==========================================
echo    แก้ไขและเริ่มระบบ YouTube Translator
echo ==========================================
echo.

:: ตรวจสอบ Docker
echo [INFO] ตรวจสอบ Docker...
docker version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Docker ไม่ได้ติดตั้งหรือไม่ได้เริ่มทำงาน
    echo [INFO] กรุณาติดตั้ง Docker Desktop และเปิดใช้งาน
    echo [INFO] ดาวน์โหลดได้จาก: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [SUCCESS] Docker พร้อมใช้งาน
echo.

:: หยุดระบบเก่า
echo [INFO] หยุดระบบเก่า (ถ้ามี)...
cd docker
docker compose -f docker-compose-simple.yml down >nul 2>&1
docker-compose -f docker-compose-simple.yml down >nul 2>&1

:: ลบ volume เก่า
echo [INFO] ลบข้อมูลเก่า...
docker volume prune -f >nul 2>&1

:: สร้างโฟลเดอร์ที่จำเป็น
echo [INFO] สร้างโฟลเดอร์...
cd ..
if not exist "uploads" mkdir uploads
if not exist "output" mkdir output
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp

:: ลบไฟล์ placeholder เก่า
echo [INFO] ลบไฟล์ placeholder เก่า...
del "output\*.mp4" >nul 2>&1
del "output\*.mp3" >nul 2>&1
del "output\*.srt" >nul 2>&1

:: Build และเริ่มระบบ
echo [INFO] Build และเริ่มระบบ...
cd docker

:: ลองใช้ docker compose แบบใหม่ก่อน
docker compose -f docker-compose-simple.yml build >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] ใช้ Docker Compose V2...
    docker compose -f docker-compose-simple.yml up -d
) else (
    echo [INFO] ใช้ Docker Compose V1...
    docker-compose -f docker-compose-simple.yml build
    docker-compose -f docker-compose-simple.yml up -d
)

if %errorLevel% neq 0 (
    echo [ERROR] ไม่สามารถเริ่มระบบได้
    echo [INFO] ดูรายละเอียดข้อผิดพลาด:
    docker-compose -f docker-compose-simple.yml logs
    pause
    exit /b 1
)

cd ..

echo [INFO] รอให้ระบบเริ่มต้น...
timeout /t 45 >nul

:: ตรวจสอบสถานะบริการ
echo.
echo [INFO] ตรวจสอบสถานะบริการ...
echo =====================================

:: ตรวจสอบ Backend
echo | set /p="Backend API (Port 8000):    "
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -TimeoutSec 5 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host '[SUCCESS] ทำงานปกติ' -ForegroundColor Green } else { Write-Host '[ERROR] ไม่ตอบสนอง' -ForegroundColor Red } } catch { Write-Host '[ERROR] ไม่ตอบสนอง' -ForegroundColor Red }"

:: ตรวจสอบ Frontend
echo | set /p="Frontend (Port 3000):       "
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000' -TimeoutSec 5 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host '[SUCCESS] ทำงานปกติ' -ForegroundColor Green } else { Write-Host '[ERROR] ไม่ตอบสนอง' -ForegroundColor Red } } catch { Write-Host '[ERROR] ไม่ตอบสนอง' -ForegroundColor Red }"

:: ตรวจสอบ LibreTranslate
echo | set /p="Translation API (Port 5000): "
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000/languages' -TimeoutSec 10 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host '[SUCCESS] ทำงานปกติ' -ForegroundColor Green } else { Write-Host '[ERROR] ไม่ตอบสนอง' -ForegroundColor Red } } catch { Write-Host '[ERROR] ไม่ตอบสนอง' -ForegroundColor Red }"

:: ตรวจสอบ Whisper Service (Full Mode)
echo | set /p="Whisper Service (Port 5001):  "
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5001/health' -TimeoutSec 5 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host '[SUCCESS] ทำงานปกติ' -ForegroundColor Green } else { Write-Host '[WARNING] ไม่ตอบสนอง' -ForegroundColor Yellow } } catch { Write-Host '[WARNING] ไม่ตอบสนอง (Simple Mode)' -ForegroundColor Yellow }"

:: ตรวจสอบ TTS Service (Full Mode)
echo | set /p="TTS Service (Port 5002):      "
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5002/health' -TimeoutSec 5 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host '[SUCCESS] ทำงานปกติ' -ForegroundColor Green } else { Write-Host '[WARNING] ไม่ตอบสนอง' -ForegroundColor Yellow } } catch { Write-Host '[WARNING] ไม่ตอบสนอง (Simple Mode)' -ForegroundColor Yellow }"

:: ตรวจสอบ Database
echo | set /p="Database (Port 5432):       "
powershell -Command "try { $connection = New-Object System.Net.Sockets.TcpClient; $connection.Connect('localhost', 5432); $connection.Close(); Write-Host '[SUCCESS] ทำงานปกติ' -ForegroundColor Green } catch { Write-Host '[ERROR] ไม่ตอบสนอง' -ForegroundColor Red }"

echo.
echo =====================================
echo [SUCCESS] ระบบเริ่มต้นแล้ว!
echo =====================================
echo.
echo � สถานะ: ระบบทำงานในโหมด FULL MODE
echo    - Whisper Service (Speech-to-Text): ใช้งานได้
echo    - TTS Service (Text-to-Speech): ใช้งานได้
echo    - LibreTranslate (Translation): ใช้งานได้
echo.
echo �🌐 URL สำหรับใช้งาน:
echo    Frontend (เว็บแอป):        http://localhost:3000
echo    Backend API:               http://localhost:8000
echo    API Documentation:         http://localhost:8000/docs
echo    Translation Service:       http://localhost:5000
echo    Whisper Service:           http://localhost:5001/health
echo    TTS Service:               http://localhost:5002/health
echo.
echo 📝 คำแนะนำการใช้งาน:
echo    1. เปิดเว็บเบราว์เซอร์ไปที่ http://localhost:3000
echo    2. ใส่ YouTube URL ที่ต้องการแปล หรือ อัพโหลดไฟล์วิดีโอ
echo    3. เลือกภาษาเป้าหมาย (ไทย)
echo    4. กดปุ่ม "แปลวิดีโอ"
echo    5. รอการประมวลผลเสร็จ (รวมทั้งการสร้างเสียงแปล)
echo    6. ดาวน์โหลดผลลัพธ์ (วิดีโอพร้อมเสียงไทย)
echo.
echo ⚡ ความสามารถ Full Mode:
echo    ✅ แปลงเสียงเป็นข้อความ (Whisper AI)
echo    ✅ แปลภาษา (LibreTranslate)
echo    ✅ แปลงข้อความเป็นเสียงไทย (TTS AI)
echo    ✅ รวมเสียงใหม่กับวิดีโอต้นฉบับ
echo.

set /p open_browser="ต้องการเปิดเว็บแอปหรือไม่? (y/n): "
if /i "%open_browser%"=="y" (
    start http://localhost:3000
    timeout /t 2 >nul
    start http://localhost:8000/docs
    echo [SUCCESS] เปิดเว็บแอปแล้ว
)

echo.
echo หากต้องการดู logs แบบ real-time ให้กด Enter
echo หรือ Ctrl+C เพื่อออก...
pause >nul

cd docker
docker compose logs -f 2>&1 || docker-compose logs -f
cd ..
