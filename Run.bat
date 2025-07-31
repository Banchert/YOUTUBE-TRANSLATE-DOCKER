@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ตั้งค่าสี
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "MAGENTA=[95m"
set "CYAN=[96m"
set "NC=[0m"

:: ฟังก์ชันแสดงผล
:print_header
echo.
echo %CYAN%========================================%NC%
echo %CYAN%    YouTube Video Translator Setup     %NC%
echo %CYAN%========================================%NC%
echo.
goto :eof

:print_status
echo %BLUE%[INFO]%NC% %~1
goto :eof

:print_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

:: เริ่มต้นโปรแกรม
call :print_header

:: ตรวจสอบ Administrator
call :print_status "ตรวจสอบสิทธิ์ Administrator..."
net session >nul 2>&1
if %errorLevel% neq 0 (
    call :print_warning "โปรแกรมนี้ต้องใช้สิทธิ์ Administrator"
    call :print_status "กำลังเรียกใช้สิทธิ์ Administrator..."
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

call :print_success "มีสิทธิ์ Administrator แล้ว"

:: เมนูหลัก
:main_menu
cls
call :print_header
echo %YELLOW%เลือกการดำเนินการ:%NC%
echo.
echo 1. ติดตั้งและเตรียมระบบครั้งแรก (First Time Setup)
echo 2. เริ่มใช้งานระบบ (Start Services)  
echo 3. หยุดการทำงาน (Stop Services)
echo 4. ดูสถานะระบบ (Check Status)
echo 5. ดู Logs
echo 6. ล้างข้อมูลและเริ่มใหม่ (Clean Reset)
echo 7. ติดตั้ง Dependencies เพิ่มเติม
echo 8. เปิดเว็บแอป (Open Web App)
echo 9. ออกจากโปรแกรม (Exit)
echo.
set /p choice="กรุณาเลือก (1-9): "

if "%choice%"=="1" goto first_setup
if "%choice%"=="2" goto start_services
if "%choice%"=="3" goto stop_services
if "%choice%"=="4" goto check_status
if "%choice%"=="5" goto view_logs
if "%choice%"=="6" goto clean_reset
if "%choice%"=="7" goto install_deps
if "%choice%"=="8" goto open_webapp
if "%choice%"=="9" goto exit_program

call :print_error "กรุณาเลือกตัวเลข 1-9"
timeout /t 2 >nul
goto main_menu

:: ติดตั้งครั้งแรก
:first_setup
cls
call :print_header
call :print_status "เริ่มการติดตั้งระบบครั้งแรก..."

:: ตรวจสอบ Docker
call :print_status "ตรวจสอบ Docker..."
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    call :print_error "Docker ไม่พบในระบบ"
    call :print_status "กำลังติดตั้ง Docker Desktop..."
    
    :: ดาวน์โหลดและติดตั้ง Docker Desktop
    call :print_status "กำลังดาวน์โหลด Docker Desktop..."
    powershell -Command "Invoke-WebRequest -Uri 'https://desktop.docker.com/win/main/amd64/Docker%%20Desktop%%20Installer.exe' -OutFile 'DockerInstaller.exe'"
    
    if exist "DockerInstaller.exe" (
        call :print_status "กำลังติดตั้ง Docker Desktop..."
        start /wait DockerInstaller.exe install --quiet
        del DockerInstaller.exe
        
        call :print_warning "Docker Desktop ติดตั้งเสร็จแล้ว กรุณารีสตาร์ทคอมพิวเตอร์และเปิด Docker Desktop ก่อนใช้งาน"
        pause
        goto main_menu
    ) else (
        call :print_error "ไม่สามารถดาวน์โหลด Docker Desktop ได้"
        call :print_status "กรุณาไปดาวน์โหลดและติดตั้งเองจาก: https://docker.com/products/docker-desktop"
        pause
        goto main_menu
    )
)

call :print_success "Docker พบในระบบแล้ว"

:: ตรวจสอบ Docker Compose
call :print_status "ตรวจสอบ Docker Compose..."
docker-compose --version >nul 2>&1
if %errorLevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorLevel% neq 0 (
        call :print_error "Docker Compose ไม่พบในระบบ"
        call :print_status "กรุณาติดตั้ง Docker Desktop ใหม่เวอร์ชันล่าสุด"
        pause
        goto main_menu
    )
    set "DOCKER_COMPOSE=docker compose"
) else (
    set "DOCKER_COMPOSE=docker-compose"
)

call :print_success "Docker Compose พบในระบบแล้ว"

:: ตรวจสอบ Git (ถ้ามี)
call :print_status "ตรวจสอบ Git..."
git --version >nul 2>&1
if %errorLevel% neq 0 (
    call :print_warning "Git ไม่พบในระบบ แต่ไม่จำเป็นสำหรับการรันแอป"
) else (
    call :print_success "Git พบในระบบแล้ว"
)

:: สร้างโฟลเดอร์ที่จำเป็น
call :print_status "สร้างโฟลเดอร์ที่จำเป็น..."
if not exist "uploads" mkdir uploads
if not exist "output" mkdir output
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp
if not exist "ssl" mkdir ssl
if not exist "database" mkdir database
if not exist "nginx\conf.d" mkdir nginx\conf.d
if not exist "monitoring\grafana" mkdir monitoring\grafana

call :print_success "สร้างโฟลเดอร์เสร็จแล้ว"

:: สร้างไฟล์ Environment
call :print_status "สร้างไฟล์ Environment..."

:: สร้าง .env หลัก
if not exist ".env" (
    (
        echo DEBUG=True
        echo SECRET_KEY=your-secret-key-for-production-change-this
        echo.
        echo # Redis
        echo REDIS_URL=redis://redis:6379
        echo.
        echo # Services URLs
        echo WHISPER_SERVICE_URL=http://whisper-service:5001
        echo TTS_SERVICE_URL=http://tts-service:5002
        echo TRANSLATION_SERVICE_URL=http://libretranslate:5000
        echo.
        echo # Database
        echo DATABASE_URL=postgresql://postgres:password@postgres:5432/youtube_translator
        echo.
        echo # Processing Settings
        echo MAX_VIDEO_DURATION=1800
        echo MAX_FILE_SIZE=200
        echo WHISPER_MODEL=medium
        echo TTS_MODEL=tts_models/th/mai_female/glow-tts
        echo.
        echo # Security
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
    ) > .env
    call :print_success "สร้างไฟล์ .env แล้ว"
) else (
    call :print_warning "ไฟล์ .env มีอยู่แล้ว"
)

:: สร้าง frontend/.env
if not exist "frontend\.env" (
    (
        echo REACT_APP_API_URL=http://localhost:8000
        echo REACT_APP_WS_URL=http://localhost:8000
        echo GENERATE_SOURCEMAP=false
        echo SKIP_PREFLIGHT_CHECK=true
    ) > frontend\.env
    call :print_success "สร้างไฟล์ frontend/.env แล้ว"
) else (
    call :print_warning "ไฟล์ frontend/.env มีอยู่แล้ว"
)

:: ตรวจสอบว่า Docker กำลังทำงานอยู่หรือไม่
call :print_status "ตรวจสอบสถานะ Docker..."
docker info >nul 2>&1
if %errorLevel% neq 0 (
    call :print_error "Docker ไม่ได้เริ่มต้นการทำงาน"
    call :print_status "กรุณาเปิด Docker Desktop และรอให้เริ่มต้นการทำงาน"
    call :print_status "หลังจากนั้นกลับมาใช้งานอีกครั้ง"
    pause
    goto main_menu
)

call :print_success "Docker กำลังทำงานอยู่"

:: Build Docker Images
call :print_status "สร้าง Docker Images (อาจใช้เวลานาน)..."
call :print_warning "กำลังดาวน์โหลดและสร้าง Images ครั้งแรกอาจใช้เวลา 10-30 นาที"

cd docker
%DOCKER_COMPOSE% build --parallel
if %errorLevel% neq 0 (
    call :print_error "การสร้าง Docker Images ล้มเหลว"
    pause
    cd ..
    goto main_menu
)
cd ..

call :print_success "สร้าง Docker Images เสร็จแล้ว"

:: ดาวน์โหลด AI Models
call :print_status "ดาวน์โหลด AI Models (อาจใช้เวลานาน)..."
call :print_warning "การดาวน์โหลด AI Models อาจใช้เวลา 5-15 นาที"

cd docker
:: ดาวน์โหลด Whisper models
call :print_status "ดาวน์โหลด Whisper models..."
%DOCKER_COMPOSE% run --rm whisper-service python -c "import whisper; whisper.load_model('base'); whisper.load_model('medium')"

:: ดาวน์โหลด TTS models
call :print_status "ดาวน์โหลด TTS models..."
%DOCKER_COMPOSE% run --rm tts-service python -c "from TTS.api import TTS; TTS(model_name='tts_models/th/mai_female/glow-tts')"

cd ..

call :print_success "ดาวน์โหลด AI Models เสร็จแล้ว"

call :print_success "การติดตั้งเสร็จสมบูรณ์!"
call :print_status "คุณสามารถเลือก '2. เริ่มใช้งานระบบ' ได้แล้ว"
pause
goto main_menu

:: เริ่มใช้งานระบบ
:start_services
cls
call :print_header
call :print_status "เริ่มการทำงานของระบบ..."

:: ตรวจสอบ Docker
docker info >nul 2>&1
if %errorLevel% neq 0 (
    call :print_error "Docker ไม่ได้เริ่มต้นการทำงาน กรุณาเปิด Docker Desktop"
    pause
    goto main_menu
)

:: เริ่มบริการ
cd docker
call :print_status "เริ่มบริการทั้งหมด..."
%DOCKER_COMPOSE% up -d

if %errorLevel% neq 0 (
    call :print_error "ไม่สามารถเริ่มบริการได้"
    pause
    cd ..
    goto main_menu
)

cd ..

call :print_status "รอให้บริการเริ่มต้น..."
timeout /t 30 >nul

:: ตรวจสอบสถานะบริการ
call :print_status "ตรวจสอบสถานะบริการ..."

set services_ok=0

:: ตรวจสอบ Backend
call :print_status "ตรวจสอบ Backend..."
curl -f http://localhost:8000/health >nul 2>&1
if %errorLevel% equ 0 (
    call :print_success "Backend พร้อมใช้งาน"
    set /a services_ok+=1
) else (
    call :print_warning "Backend ยังไม่พร้อม"
)

:: ตรวจสอบ Frontend
call :print_status "ตรวจสอบ Frontend..."
curl -f http://localhost:3000 >nul 2>&1
if %errorLevel% equ 0 (
    call :print_success "Frontend พร้อมใช้งาน"
    set /a services_ok+=1
) else (
    call :print_warning "Frontend ยังไม่พร้อม"
)

:: ตรวจสอบ Translation Service
call :print_status "ตรวจสอบ Translation Service..."
curl -f http://localhost:5000/languages >nul 2>&1
if %errorLevel% equ 0 (
    call :print_success "Translation Service พร้อมใช้งาน"
    set /a services_ok+=1
) else (
    call :print_warning "Translation Service ยังไม่พร้อม"
)

echo.
if %services_ok% geq 2 (
    call :print_success "ระบบพร้อมใช้งาน!"
    echo.
    echo %CYAN%🌐 เข้าใช้งานผ่าน:%NC%
    echo    Frontend:           http://localhost:3000
    echo    Backend API:        http://localhost:8000
    echo    API Documentation:  http://localhost:8000/docs
    echo    Translation:        http://localhost:5000
    echo.
    
    set /p open_browser="ต้องการเปิดเว็บแอปหรือไม่? (y/n): "
    if /i "!open_browser!"=="y" (
        start http://localhost:3000
        call :print_success "เปิดเว็บแอปแล้ว"
    )
) else (
    call :print_warning "บางบริการยังไม่พร้อม กรุณาดู logs เพื่อตรวจสอบปัญหา"
)

pause
goto main_menu

:: หยุดการทำงาน
:stop_services
cls
call :print_header
call :print_status "หยุดการทำงานของระบบ..."

cd docker
%DOCKER_COMPOSE% down
cd ..

call :print_success "หยุดการทำงานเสร็จแล้ว"
pause
goto main_menu

:: ตรวจสอบสถานะ
:check_status
cls
call :print_header
call :print_status "ตรวจสอบสถานะระบบ..."

cd docker
echo %YELLOW%สถานะ Containers:%NC%
%DOCKER_COMPOSE% ps
echo.

echo %YELLOW%สถานะบริการ:%NC%
echo.

:: ตรวจสอบแต่ละบริการ
call :check_service "Frontend" "http://localhost:3000"
call :check_service "Backend API" "http://localhost:8000/health"
call :check_service "Translation Service" "http://localhost:5000/languages"
call :check_service "Whisper Service" "http://localhost:5001/health"
call :check_service "TTS Service" "http://localhost:5002/health"

cd ..
pause
goto main_menu

:: ฟังก์ชันตรวจสอบบริการ
:check_service
curl -f %~2 >nul 2>&1
if %errorLevel% equ 0 (
    echo %GREEN%✓%NC% %~1 - กำลังทำงาน
) else (
    echo %RED%✗%NC% %~1 - ไม่ตอบสนอง
)
goto :eof

:: ดู Logs
:view_logs
cls
call :print_header
echo %YELLOW%เลือกบริการที่ต้องการดู Logs:%NC%
echo.
echo 1. ทั้งหมด (All Services)
echo 2. Backend
echo 3. Frontend  
echo 4. Whisper Service
echo 5. TTS Service
echo 6. Translation Service
echo 7. กลับเมนูหลัก
echo.
set /p log_choice="เลือกบริการ (1-7): "

cd docker
if "%log_choice%"=="1" %DOCKER_COMPOSE% logs -f --tail=100
if "%log_choice%"=="2" %DOCKER_COMPOSE% logs -f backend --tail=100
if "%log_choice%"=="3" %DOCKER_COMPOSE% logs -f frontend --tail=100
if "%log_choice%"=="4" %DOCKER_COMPOSE% logs -f whisper-service --tail=100
if "%log_choice%"=="5" %DOCKER_COMPOSE% logs -f tts-service --tail=100
if "%log_choice%"=="6" %DOCKER_COMPOSE% logs -f libretranslate --tail=100
if "%log_choice%"=="7" cd .. && goto main_menu

cd ..
pause
goto main_menu

:: ล้างข้อมูลและเริ่มใหม่
:clean_reset
cls
call :print_header
call :print_warning "การดำเนินการนี้จะลบข้อมูลทั้งหมดและเริ่มใหม่"
echo.
set /p confirm="ต้องการดำเนินการต่อหรือไม่? (y/n): "
if /i not "%confirm%"=="y" goto main_menu

call :print_status "หยุดบริการทั้งหมด..."
cd docker
%DOCKER_COMPOSE% down -v --remove-orphans
cd ..

call :print_status "ลบ Docker Images..."
docker system prune -a -f

call :print_status "ลบข้อมูลในโฟลเดอร์..."
if exist "uploads\*" del /q uploads\*
if exist "output\*" del /q output\*
if exist "logs\*" del /q logs\*
if exist "temp\*" del /q temp\*

call :print_success "ล้างข้อมูลเสร็จแล้ว คุณสามารถเลือก '1. ติดตั้งและเตรียมระบบครั้งแรก' ได้แล้ว"
pause
goto main_menu

:: ติดตั้ง Dependencies เพิ่มเติม
:install_deps
cls
call :print_header
call :print_status "ติดตั้ง Dependencies เพิ่มเติม..."

:: ติดตั้ง curl ถ้าไม่มี
where curl >nul 2>&1
if %errorLevel% neq 0 (
    call :print_status "ติดตั้ง curl..."
    powershell -Command "Invoke-WebRequest -Uri 'https://curl.se/windows/dl-8.4.0_6/curl-8.4.0_6-win64-mingw.zip' -OutFile 'curl.zip'"
    powershell -Command "Expand-Archive -Path 'curl.zip' -DestinationPath 'curl_temp'"
    copy curl_temp\curl-8.4.0_6-win64-mingw\bin\curl.exe C:\Windows\System32\
    rmdir /s /q curl_temp
    del curl.zip
    call :print_success "ติดตั้ง curl เสร็จแล้ว"
) else (
    call :print_success "curl พร้อมใช้งานแล้ว"
)

:: ติดตั้ง Git ถ้าต้องการ
git --version >nul 2>&1
if %errorLevel% neq 0 (
    set /p install_git="ต้องการติดตั้ง Git หรือไม่? (y/n): "
    if /i "!install_git!"=="y" (
        call :print_status "เปิดหน้าดาวน์โหลด Git..."
        start https://git-scm.com/download/win
        call :print_status "กรุณาดาวน์โหลดและติดตั้ง Git จากหน้าเว็บที่เปิดขึ้น"
    )
) else (
    call :print_success "Git พร้อมใช้งานแล้ว"
)

pause
goto main_menu

:: เปิดเว็บแอป
:open_webapp
cls
call :print_header
call :print_status "เปิดเว็บแอปและบริการต่างๆ..."

start http://localhost:3000
call :print_success "เปิด Frontend (http://localhost:3000)"

timeout /t 2 >nul
start http://localhost:8000/docs
call :print_success "เปิด API Documentation (http://localhost:8000/docs)"

timeout /t 2 >nul
start http://localhost:5555
call :print_success "เปิด Celery Monitor (http://localhost:5555)"

call :print_success "เปิดเว็บแอปทั้งหมดเสร็จแล้ว"
pause
goto main_menu

:: ออกจากโปรแกรม
:exit_program
cls
call :print_header
call :print_status "ออกจากโปรแกรม..."

echo %CYAN%ขอบคุณที่ใช้งาน YouTube Video Translator!%NC%
echo.
echo %YELLOW%สำหรับการใช้งานครั้งต่อไป:%NC%
echo   - เรียกใช้ไฟล์ Run.bat นี้อีกครั้ง
echo   - หรือเลือก '2. เริ่มใช้งานระบบ' หากติดตั้งแล้ว
echo.
echo %BLUE%เว็บไซต์โปรเจค:%NC% https://github.com/your-project
echo %BLUE%เอกสารการใช้งาน:%NC% README.md
echo.
pause
exit /b 0
