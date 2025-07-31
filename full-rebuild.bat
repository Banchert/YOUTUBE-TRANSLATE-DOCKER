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

echo.
echo %CYAN%========================================%NC%
echo %CYAN%    Full System Rebuild                %NC%
echo %CYAN%========================================%NC%
echo.

:: ตรวจสอบ Docker
echo %BLUE%[INFO]%NC% ตรวจสอบ Docker...
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo %RED%[ERROR]%NC% Docker ไม่พบในระบบ
    echo %YELLOW%[WARNING]%NC% กรุณาติดตั้ง Docker Desktop ก่อน
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% Docker พร้อมใช้งาน

:: หยุดและลบ containers ทั้งหมด
echo.
echo %BLUE%[INFO]%NC% หยุดและลบ containers ทั้งหมด...
cd docker
docker-compose -f docker-compose-simple.yml down

:: ลบ images เก่า
echo %BLUE%[INFO]%NC% ลบ images เก่า...
docker rmi youtube-translate-frontend 2>nul
docker rmi youtube-translate-backend 2>nul
docker system prune -f

:: Rebuild ทั้งหมด
echo %BLUE%[INFO]%NC% เริ่ม rebuild ทั้งระบบ...
docker-compose -f docker-compose-simple.yml build --no-cache

if %errorLevel% neq 0 (
    echo %RED%[ERROR]%NC% การ build ล้มเหลว
    cd ..
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% Build สำเร็จ

:: เริ่มระบบใหม่
echo %BLUE%[INFO]%NC% เริ่มระบบใหม่...
docker-compose -f docker-compose-simple.yml up -d

if %errorLevel% neq 0 (
    echo %RED%[ERROR]%NC% การเริ่มระบบล้มเหลว
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo %GREEN%[SUCCESS]%NC% ระบบอัปเดตสำเร็จ!
echo.
echo %CYAN%========================================%NC%
echo %CYAN%    ข้อมูลการเข้าถึงระบบ               %NC%
echo %CYAN%========================================%NC%
echo.
echo %GREEN%Frontend URL:%NC% http://localhost:3000
echo %GREEN%Backend API:%NC% http://localhost:8000
echo %GREEN%Translation API:%NC% http://localhost:5000
echo %GREEN%API Documentation:%NC% http://localhost:8000/docs
echo.
echo %YELLOW%[NOTE]%NC% ระบบอาจใช้เวลา 2-5 นาทีในการเริ่มต้น
echo   - LibreTranslate ต้องการเวลาโหลด models
echo   - Frontend ต้องการเวลา build
echo   - Backend ต้องการเวลาเชื่อมต่อ database
echo.

:: ตรวจสอบสถานะ
echo %BLUE%[INFO]%NC% ตรวจสอบสถานะ containers...
docker ps

echo.
echo %GREEN%[COMPLETE]%NC% การ rebuild เสร็จสิ้น!
echo %YELLOW%[TIP]%NC% ใช้ Status.bat เพื่อตรวจสอบสถานะ
pause 