@echo off
echo Running Comprehensive TTS Fix Test...
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run the comprehensive test
echo Running comprehensive TTS fix test...
python test_tts_comprehensive.py

echo.
echo Comprehensive test completed.
pause 