@echo off
echo Testing TTS Service Fix...
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run the test
echo Running TTS fix test...
python test_tts_fix.py

echo.
echo Test completed.
pause 