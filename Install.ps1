# YouTube Video Translator - PowerShell Installation Script
# Run as Administrator for best results

param(
    [switch]$SkipDocker,
    [switch]$DevMode,
    [switch]$Force
)

# Set UTF-8 encoding for proper Thai character display
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.OutputEncoding = [System.Text.Encoding]::UTF8

# Color functions
function Write-ColorText {
    param(
        [string]$Text,
        [ConsoleColor]$ForegroundColor = [ConsoleColor]::White
    )
    $originalColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Host $Text
    $Host.UI.RawUI.ForegroundColor = $originalColor
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-ColorText "========================================" -ForegroundColor Cyan
    Write-ColorText "    $Title" -ForegroundColor Cyan
    Write-ColorText "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Status {
    param([string]$Message)
    Write-ColorText "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-ColorText "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-ColorText "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-ColorText "[ERROR] $Message" -ForegroundColor Red
}

# Check if running as Administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Install Chocolatey
function Install-Chocolatey {
    Write-Status "ตรวจสอบ Chocolatey..."
    
    if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Status "ติดตั้ง Chocolatey Package Manager..."
        
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        
        try {
            Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
            Write-Success "ติดตั้ง Chocolatey เสร็จแล้ว"
            
            # Refresh environment variables
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        }
        catch {
            Write-Error "ไม่สามารถติดตั้ง Chocolatey ได้: $($_.Exception.Message)"
            return $false
        }
    } else {
        Write-Success "Chocolatey พร้อมใช้งานแล้ว"
    }
    
    return $true
}

# Install Docker Desktop
function Install-DockerDesktop {
    Write-Status "ตรวจสอบ Docker Desktop..."
    
    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Status "ติดตั้ง Docker Desktop..."
        
        try {
            # Download Docker Desktop installer
            $dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
            $dockerInstaller = "$env:TEMP\DockerDesktopInstaller.exe"
            
            Write-Status "ดาวน์โหลด Docker Desktop..."
            Invoke-WebRequest -Uri $dockerUrl -OutFile $dockerInstaller -UseBasicParsing
            
            Write-Status "ติดตั้ง Docker Desktop (อาจใช้เวลาสักครู่)..."
            Start-Process -FilePath $dockerInstaller -ArgumentList "install --quiet" -Wait
            
            Remove-Item $dockerInstaller -Force
            
            Write-Success "ติดตั้ง Docker Desktop เสร็จแล้ว"
            Write-Warning "กรุณารีสตาร์ทคอมพิวเตอร์และเปิด Docker Desktop ก่อนใช้งาน"
            
            return $true
        }
        catch {
            Write-Error "ไม่สามารถติดตั้ง Docker Desktop ได้: $($_.Exception.Message)"
            Write-Status "กรุณาดาวน์โหลดและติดตั้งเองจาก: https://docker.com/products/docker-desktop"
            return $false
        }
    } else {
        Write-Success "Docker พร้อมใช้งานแล้ว"
        return $true
    }
}

# Install Node.js
function Install-NodeJS {
    Write-Status "ตรวจสอบ Node.js..."
    
    if (!(Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Status "ติดตั้ง Node.js..."
        
        try {
            choco install nodejs -y
            Write-Success "ติดตั้ง Node.js เสร็จแล้ว"
            
            # Refresh environment variables
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        }
        catch {
            Write-Error "ไม่สามารถติดตั้ง Node.js ได้: $($_.Exception.Message)"
            return $false
        }
    } else {
        $nodeVersion = node --version
        Write-Success "Node.js พร้อมใช้งานแล้ว (เวอร์ชัน: $nodeVersion)"
    }
    
    return $true
}

# Install Python
function Install-Python {
    Write-Status "ตรวจสอบ Python..."
    
    if (!(Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Status "ติดตั้ง Python..."
        
        try {
            choco install python -y
            Write-Success "ติดตั้ง Python เสร็จแล้ว"
            
            # Refresh environment variables
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        }
        catch {
            Write-Error "ไม่สามารถติดตั้ง Python ได้: $($_.Exception.Message)"
            return $false
        }
    } else {
        $pythonVersion = python --version
        Write-Success "Python พร้อมใช้งานแล้ว (เวอร์ชัน: $pythonVersion)"
    }
    
    return $true
}

# Install Git
function Install-Git {
    Write-Status "ตรวจสอบ Git..."
    
    if (!(Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Status "ติดตั้ง Git..."
        
        try {
            choco install git -y
            Write-Success "ติดตั้ง Git เสร็จแล้ว"
            
            # Refresh environment variables
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        }
        catch {
            Write-Error "ไม่สามารถติดตั้ง Git ได้: $($_.Exception.Message)"
            return $false
        }
    } else {
        $gitVersion = git --version
        Write-Success "Git พร้อมใช้งานแล้ว (เวอร์ชัน: $gitVersion)"
    }
    
    return $true
}

# Create project directories
function New-ProjectDirectories {
    Write-Status "สร้างโฟลเดอร์โปรเจค..."
    
    $directories = @(
        "uploads",
        "output", 
        "logs",
        "temp",
        "ssl",
        "database",
        "nginx\conf.d",
        "monitoring\grafana"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Status "สร้างโฟลเดอร์: $dir"
        }
    }
    
    Write-Success "สร้างโฟลเดอร์เสร็จแล้ว"
}

# Create environment files
function New-EnvironmentFiles {
    Write-Status "สร้างไฟล์ Environment..."
    
    # Create main .env file
    if (!(Test-Path ".env") -or $Force) {
        $envContent = @"
DEBUG=True
SECRET_KEY=your-secret-key-for-production-change-this

# Redis
REDIS_URL=redis://redis:6379

# Services URLs
WHISPER_SERVICE_URL=http://whisper-service:5001
TTS_SERVICE_URL=http://tts-service:5002
TRANSLATION_SERVICE_URL=http://libretranslate:5000

# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/youtube_translator

# Processing Settings
MAX_VIDEO_DURATION=1800
MAX_FILE_SIZE=200
WHISPER_MODEL=medium
TTS_MODEL=tts_models/th/mai_female/glow-tts

# Security
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success "สร้างไฟล์ .env แล้ว"
    } else {
        Write-Warning "ไฟล์ .env มีอยู่แล้ว"
    }
    
    # Create frontend .env file
    if (!(Test-Path "frontend\.env") -or $Force) {
        $frontendEnvContent = @"
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=http://localhost:8000
GENERATE_SOURCEMAP=false
SKIP_PREFLIGHT_CHECK=true
"@
        $frontendEnvContent | Out-File -FilePath "frontend\.env" -Encoding UTF8
        Write-Success "สร้างไฟล์ frontend/.env แล้ว"
    } else {
        Write-Warning "ไฟล์ frontend/.env มีอยู่แล้ว"
    }
}

# Test Docker functionality
function Test-Docker {
    Write-Status "ทดสอบ Docker..."
    
    try {
        $dockerInfo = docker info 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker ทำงานปกติ"
            return $true
        } else {
            Write-Error "Docker ไม่สามารถเชื่อมต่อได้"
            Write-Warning "กรุณาเปิด Docker Desktop และรอให้เริ่มต้นการทำงาน"
            return $false
        }
    }
    catch {
        Write-Error "ไม่สามารถทดสอบ Docker ได้: $($_.Exception.Message)"
        return $false
    }
}

# Build Docker images
function Build-DockerImages {
    Write-Status "สร้าง Docker Images..."
    Write-Warning "การสร้าง Images ครั้งแรกอาจใช้เวลา 10-30 นาที"
    
    try {
        Set-Location "docker"
        
        if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
            docker-compose build --parallel
        } else {
            docker compose build --parallel
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "สร้าง Docker Images เสร็จแล้ว"
            Set-Location ".."
            return $true
        } else {
            Write-Error "การสร้าง Docker Images ล้มเหลว"
            Set-Location ".."
            return $false
        }
    }
    catch {
        Write-Error "เกิดข้อผิดพลาดในการสร้าง Images: $($_.Exception.Message)"
        Set-Location ".."
        return $false
    }
}

# Download AI models
function Get-AIModels {
    Write-Status "ดาวน์โหลด AI Models..."
    Write-Warning "การดาวน์โหลด AI Models อาจใช้เวลา 5-15 นาที"
    
    try {
        Set-Location "docker"
        
        # Download Whisper models
        Write-Status "ดาวน์โหลด Whisper models..."
        if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
            docker-compose run --rm whisper-service python -c "import whisper; whisper.load_model('base'); whisper.load_model('medium')"
        } else {
            docker compose run --rm whisper-service python -c "import whisper; whisper.load_model('base'); whisper.load_model('medium')"
        }
        
        # Download TTS models
        Write-Status "ดาวน์โหลด TTS models..."
        if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
            docker-compose run --rm tts-service python -c "from TTS.api import TTS; TTS(model_name='tts_models/th/mai_female/glow-tts')"
        } else {
            docker compose run --rm tts-service python -c "from TTS.api import TTS; TTS(model_name='tts_models/th/mai_female/glow-tts')"
        }
        
        Write-Success "ดาวน์โหลด AI Models เสร็จแล้ว"
        Set-Location ".."
        return $true
    }
    catch {
        Write-Error "เกิดข้อผิดพลาดในการดาวน์โหลด Models: $($_.Exception.Message)"
        Set-Location ".."
        return $false
    }
}

# Install for development mode
function Install-DevMode {
    Write-Header "ติดตั้งโหมด Development"
    
    # Install backend dependencies
    Write-Status "ติดตั้ง Backend dependencies..."
    Set-Location "backend"
    
    if (!(Test-Path "venv")) {
        python -m venv venv
    }
    
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    deactivate
    
    Set-Location ".."
    Write-Success "ติดตั้ง Backend dependencies เสร็จแล้ว"
    
    # Install frontend dependencies
    Write-Status "ติดตั้ง Frontend dependencies..."
    Set-Location "frontend"
    npm install
    Set-Location ".."
    Write-Success "ติดตั้ง Frontend dependencies เสร็จแล้ว"
}

# Create quick start scripts
function New-QuickStartScripts {
    Write-Status "สร้างสคริปต์เริ่มใช้งานด่วน..."
    
    # Create Start.bat
    $startBatContent = @"
@echo off
echo Starting YouTube Video Translator...
cd docker
docker-compose up -d
echo.
echo Services are starting...
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000/docs
echo.
echo Press any key to view logs...
pause >nul
docker-compose logs -f
"@
    $startBatContent | Out-File -FilePath "Start.bat" -Encoding ASCII
    
    # Create Stop.bat
    $stopBatContent = @"
@echo off
echo Stopping YouTube Video Translator...
cd docker
docker-compose down
echo Services stopped.
pause
"@
    $stopBatContent | Out-File -FilePath "Stop.bat" -Encoding ASCII
    
    # Create Status.bat
    $statusBatContent = @"
@echo off
echo YouTube Video Translator Status:
echo.
cd docker
docker-compose ps
echo.
echo Service Health:
curl -f http://localhost:8000/health >nul 2>&1 && echo [OK] Backend || echo [ERROR] Backend
curl -f http://localhost:3000 >nul 2>&1 && echo [OK] Frontend || echo [ERROR] Frontend
curl -f http://localhost:5000/languages >nul 2>&1 && echo [OK] Translation || echo [ERROR] Translation
echo.
pause
"@
    $statusBatContent | Out-File -FilePath "Status.bat" -Encoding ASCII
    
    Write-Success "สร้างสคริปต์เริ่มใช้งานด่วนเสร็จแล้ว"
}

# Main installation function
function Start-Installation {
    Write-Header "YouTube Video Translator - การติดตั้ง"
    
    # Check Administrator privileges
    if (!(Test-Administrator)) {
        Write-Warning "โปรแกรมนี้ควรรันด้วยสิทธิ์ Administrator เพื่อการติดตั้งที่สมบูรณ์"
        $continue = Read-Host "ต้องการดำเนินการต่อหรือไม่? (y/n)"
        if ($continue -ne "y") {
            Write-Status "ออกจากการติดตั้ง"
            return
        }
    }
    
    Write-Status "เริ่มการติดตั้ง YouTube Video Translator..."
    
    # Install Chocolatey (package manager)
    if (!(Install-Chocolatey)) {
        Write-Error "ไม่สามารถติดตั้ง Chocolatey ได้"
        return
    }
    
    # Install required software
    if (!$SkipDocker) {
        if (!(Install-DockerDesktop)) {
            Write-Error "ไม่สามารถติดตั้ง Docker ได้"
            return
        }
    }
    
    Install-Git | Out-Null
    Install-NodeJS | Out-Null
    Install-Python | Out-Null
    
    # Create project structure
    New-ProjectDirectories
    New-EnvironmentFiles
    
    # Development mode
    if ($DevMode) {
        Install-DevMode
    }
    
    # Docker setup
    if (!$SkipDocker) {
        if (Test-Docker) {
            if (Build-DockerImages) {
                Get-AIModels | Out-Null
            }
        } else {
            Write-Warning "Docker ไม่พร้อมใช้งาน กรุณาเปิด Docker Desktop และรันสคริปต์อีกครั้ง"
        }
    }
    
    # Create convenience scripts
    New-QuickStartScripts
    
    Write-Header "การติดตั้งเสร็จสมบูรณ์!"
    
    Write-Success "YouTube Video Translator พร้อมใช้งานแล้ว"
    Write-Host ""
    Write-ColorText "สำหรับการใช้งาน:" -ForegroundColor Yellow
    Write-Host "  1. รันไฟล์ Start.bat เพื่อเริ่มระบบ"
    Write-Host "  2. เปิดเว็บเบราว์เซอร์ไปที่ http://localhost:3000"
    Write-Host "  3. รันไฟล์ Stop.bat เพื่อหยุดระบบ"
    Write-Host ""
    Write-ColorText "ไฟล์สำคัญ:" -ForegroundColor Yellow
    Write-Host "  - Run.bat       : เมนูจัดการระบบแบบครบครัน"
    Write-Host "  - Start.bat     : เริ่มระบบ"
    Write-Host "  - Stop.bat      : หยุดระบบ"
    Write-Host "  - Status.bat    : ตรวจสอบสถานะ"
    Write-Host ""
    Write-ColorText "เว็บไซต์:" -ForegroundColor Yellow
    Write-Host "  - Frontend:           http://localhost:3000"
    Write-Host "  - API Documentation:  http://localhost:8000/docs"
    Write-Host "  - Translation API:    http://localhost:5000"
    Write-Host ""
    
    $openApp = Read-Host "ต้องการเริ่มใช้งานระบบทันทีหรือไม่? (y/n)"
    if ($openApp -eq "y") {
        Write-Status "เริ่มระบบ..."
        .\Start.bat
    }
}

# Script execution
try {
    Start-Installation
}
catch {
    Write-Error "เกิดข้อผิดพลาดในการติดตั้ง: $($_.Exception.Message)"
    Write-Host "กรุณาตรวจสอบข้อผิดพลาดและลองใหม่อีกครั้ง"
    Read-Host "กด Enter เพื่อออก"
}
