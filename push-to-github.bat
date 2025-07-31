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
echo %CYAN%    Push to GitHub Repository         %NC%
echo %CYAN%========================================%NC%
echo.

:: ตรวจสอบ Git
echo %BLUE%[INFO]%NC% ตรวจสอบ Git...
git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo %RED%[ERROR]%NC% Git ไม่พบในระบบ
    echo %YELLOW%[WARNING]%NC% กรุณาติดตั้ง Git ก่อน
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% Git พร้อมใช้งาน

:: ตรวจสอบสถานะ Git
echo.
echo %BLUE%[INFO]%NC% ตรวจสอบสถานะ Git...
git status --porcelain
if %errorLevel% neq 0 (
    echo %RED%[ERROR]%NC% ไม่ใช่ Git repository
    pause
    exit /b 1
)

:: ขอข้อมูล GitHub
echo.
echo %YELLOW%[INPUT]%NC% กรุณาใส่ข้อมูล GitHub:
echo.

set /p github_username="GitHub Username: "
if "!github_username!"=="" (
    echo %RED%[ERROR]%NC% กรุณาใส่ GitHub Username
    pause
    exit /b 1
)

set /p repo_name="Repository Name (default: youtube-translate): "
if "!repo_name!"=="" set repo_name=youtube-translate

set /p github_url="GitHub Repository URL (optional): "
if "!github_url!"=="" (
    set github_url=https://github.com/!github_username!/!repo_name!.git
)

echo.
echo %BLUE%[INFO]%NC% ข้อมูลที่ใช้:
echo   Username: !github_username!
echo   Repository: !repo_name!
echo   URL: !github_url!
echo.

set /p confirm="ยืนยันการ Push ไป GitHub? (y/N): "
if /i not "!confirm!"=="y" (
    echo %YELLOW%[CANCELLED]%NC% ยกเลิกการ Push
    pause
    exit /b 0
)

:: เพิ่ม Remote Origin
echo.
echo %BLUE%[INFO]%NC% เพิ่ม Remote Origin...
git remote add origin !github_url! 2>nul
if %errorLevel% neq 0 (
    echo %YELLOW%[WARNING]%NC% Remote origin มีอยู่แล้ว
    git remote set-url origin !github_url!
)

:: Push ไป GitHub
echo %BLUE%[INFO]%NC% Push ไป GitHub...
git push -u origin master

if %errorLevel% neq 0 (
    echo %RED%[ERROR]%NC% การ Push ล้มเหลว
    echo.
    echo %YELLOW%[TROUBLESHOOTING]%NC% วิธีแก้ไข:
    echo   1. ตรวจสอบ GitHub URL
    echo   2. ตรวจสอบ Username และ Password/Token
    echo   3. สร้าง Repository บน GitHub ก่อน
    echo   4. ใช้ Personal Access Token แทน Password
    echo.
    pause
    exit /b 1
)

echo.
echo %GREEN%[SUCCESS]%NC% Push ไป GitHub สำเร็จ!
echo.
echo %CYAN%========================================%NC%
echo %CYAN%    Repository Information             %NC%
echo %CYAN%========================================%NC%
echo.
echo %GREEN%Repository URL:%NC% https://github.com/!github_username!/!repo_name!
echo %GREEN%Clone Command:%NC% git clone https://github.com/!github_username!/!repo_name!.git
echo %GREEN%Raw Files:%NC% https://raw.githubusercontent.com/!github_username!/!repo_name!/master/
echo.
echo %YELLOW%[NEXT STEPS]%NC% หลังจาก Push สำเร็จ:
echo   1. เปิด https://github.com/!github_username!/!repo_name!
echo   2. ตรวจสอบไฟล์ทั้งหมดถูก Push ขึ้นไป
echo   3. อัปเดต README.md หากจำเป็น
echo   4. เพิ่ม Topics และ Description
echo   5. เปิด Issues และ Discussions
echo.

:: สร้างไฟล์ข้อมูล Repository
echo # GitHub Repository Information > github-info.txt
echo Repository: !github_username!/!repo_name! >> github-info.txt
echo URL: https://github.com/!github_username!/!repo_name! >> github-info.txt
echo Clone: git clone https://github.com/!github_username!/!repo_name!.git >> github-info.txt
echo Created: %date% %time% >> github-info.txt

echo %GREEN%[INFO]%NC% ข้อมูล Repository ถูกบันทึกใน github-info.txt

echo.
echo %GREEN%[COMPLETE]%NC% การ Push เสร็จสิ้น!
pause 