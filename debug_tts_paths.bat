@echo off
echo Debugging TTS Paths...
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run the debug script
echo Running TTS path debug...
python debug_tts_paths.py

echo.
echo Debug completed.
pause 