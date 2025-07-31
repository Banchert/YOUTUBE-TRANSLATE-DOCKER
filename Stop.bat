@echo off
chcp 65001 >nul

echo.
echo ==========================================
echo    หยุดการทำงาน YouTube Video Translator
echo ==========================================
echo.

echo [INFO] หยุดบริการทั้งหมด...
cd docker

:: ตรวจสอบว่ามี docker-compose หรือ docker compose
docker-compose --version >nul 2>&1
if %errorLevel% neq 0 (
    docker compose -f docker-compose-simple.yml down
) else (
    docker-compose -f docker-compose-simple.yml down
)

cd ..

if %errorLevel% equ 0 (
    echo [SUCCESS] หยุดการทำงานเสร็จแล้ว
) else (
    echo [WARNING] อาจมีปัญหาในการหยุดบริการ
)

echo.
echo บริการทั้งหมดถูกหยุดแล้ว
echo สำหรับการเริ่มใช้งานครั้งต่อไป ให้รันไฟล์ Start.bat
echo.
pause
