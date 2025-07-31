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
echo %CYAN%    Rebuild Frontend After Changes     %NC%
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

:: หยุด containers ที่เกี่ยวข้อง
echo.
echo %BLUE%[INFO]%NC% หยุด containers ที่เกี่ยวข้อง...
cd docker
docker-compose -f docker-compose-simple.yml stop frontend
cd ..

:: ลบ frontend image เก่า
echo %BLUE%[INFO]%NC% ลบ frontend image เก่า...
docker rmi youtube-translate-frontend 2>nul
docker rmi $(docker images -q youtube-translate-frontend) 2>nul

:: Rebuild frontend
echo %BLUE%[INFO]%NC% เริ่ม rebuild frontend...
cd docker
docker-compose -f docker-compose-simple.yml build --no-cache frontend

if %errorLevel% neq 0 (
    echo %RED%[ERROR]%NC% การ build frontend ล้มเหลว
    cd ..
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% Frontend build สำเร็จ

:: เริ่ม frontend ใหม่
echo %BLUE%[INFO]%NC% เริ่ม frontend ใหม่...
docker-compose -f docker-compose-simple.yml up -d frontend

if %errorLevel% neq 0 (
    echo %RED%[ERROR]%NC% การเริ่ม frontend ล้มเหลว
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo %GREEN%[SUCCESS]%NC% Frontend อัปเดตสำเร็จ!
echo.
echo %CYAN%========================================%NC%
echo %CYAN%    ข้อมูลการเข้าถึง Frontend          %NC%
echo %CYAN%========================================%NC%
echo.
echo %GREEN%Frontend URL:%NC% http://localhost:3000
echo %GREEN%Backend API:%NC% http://localhost:8000
echo %GREEN%Translation API:%NC% http://localhost:5000
echo.
echo %YELLOW%[NOTE]%NC% หากยังไม่เห็นการเปลี่ยนแปลง กรุณา:
echo   1. ล้าง cache ของเบราว์เซอร์ (Ctrl+F5)
echo   2. รอ 1-2 นาทีให้ container เริ่มต้นเสร็จ
echo   3. ตรวจสอบ logs: docker logs youtube-translate-frontend-1
echo.

:: ตรวจสอบสถานะ
echo %BLUE%[INFO]%NC% ตรวจสอบสถานะ containers...
docker ps --filter "name=frontend"

echo.
echo %GREEN%[COMPLETE]%NC% การอัปเดตเสร็จสิ้น!
pause 