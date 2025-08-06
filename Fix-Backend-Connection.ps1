# PowerShell script to diagnose and fix Docker/Backend connection issues
# File: Fix-Backend-Connection.ps1

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   YouTube Video Translator - Backend Fix   " -ForegroundColor Cyan  
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Function to test if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Function to test if a port is open
function Test-Port($hostname, $port) {
    try {
        $connection = New-Object System.Net.Sockets.TcpClient($hostname, $port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# 1. Check Docker Installation
Write-Host "[1/7] ตรวจสอบการติดตั้ง Docker..." -ForegroundColor Yellow

if (Test-Command docker) {
    Write-Host "✅ Docker ติดตั้งแล้ว" -ForegroundColor Green
    
    # Check Docker service status
    try {
        $dockerVersion = docker version --format "{{.Server.Version}}" 2>$null
        if ($dockerVersion) {
            Write-Host "✅ Docker Engine เวอร์ชัน: $dockerVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ Docker Engine ไม่ทำงาน" -ForegroundColor Red
            Write-Host "💡 กรุณาเปิด Docker Desktop" -ForegroundColor Cyan
            Write-Host "   หรือเริ่ม Docker service: net start docker" -ForegroundColor Cyan
        }
    }
    catch {
        Write-Host "❌ Docker ไม่สามารถเชื่อมต่อได้" -ForegroundColor Red
        Write-Host "💡 ลองคำสั่ง: Get-Service docker | Start-Service" -ForegroundColor Cyan
    }
} else {
    Write-Host "❌ Docker ไม่ได้ติดตั้ง" -ForegroundColor Red
    Write-Host "💡 ดาวน์โหลดจาก: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
}

# 2. Check Docker Compose
Write-Host ""
Write-Host "[2/7] ตรวจสอบ Docker Compose..." -ForegroundColor Yellow

if (Test-Command "docker") {
    try {
        $composeVersion = docker compose version 2>$null
        if ($composeVersion) {
            Write-Host "✅ Docker Compose พร้อมใช้งาน" -ForegroundColor Green
            Write-Host "   $composeVersion" -ForegroundColor Gray
        } else {
            # Try legacy docker-compose
            $legacyCompose = docker-compose --version 2>$null
            if ($legacyCompose) {
                Write-Host "✅ Docker Compose (legacy) พร้อมใช้งาน" -ForegroundColor Green
                Write-Host "   $legacyCompose" -ForegroundColor Gray
            } else {
                Write-Host "❌ Docker Compose ไม่พบ" -ForegroundColor Red
            }
        }
    }
    catch {
        Write-Host "❌ ไม่สามารถตรวจสอบ Docker Compose ได้" -ForegroundColor Red
    }
}

# 3. Check current containers
Write-Host ""
Write-Host "[3/7] ตรวจสอบ Containers ที่ทำงานอยู่..." -ForegroundColor Yellow

try {
    $containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>$null
    if ($containers) {
        Write-Host "📦 Containers ที่ทำงาน:" -ForegroundColor Green
        $containers | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    } else {
        Write-Host "⚠️  ไม่มี Container ใดทำงานอยู่" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ ไม่สามารถตรวจสอบ Containers ได้" -ForegroundColor Red
}

# 4. Check ports
Write-Host ""
Write-Host "[4/7] ตรวจสอบ Ports..." -ForegroundColor Yellow

$ports = @{
    "Backend API" = 8000
    "Frontend" = 3000  
    "LibreTranslate" = 5000
    "Redis" = 6379
    "PostgreSQL" = 5432
}

foreach ($service in $ports.GetEnumerator()) {
    $isOpen = Test-Port "localhost" $service.Value
    if ($isOpen) {
        Write-Host "✅ $($service.Key): localhost:$($service.Value) - เปิดอยู่" -ForegroundColor Green
    } else {
        Write-Host "❌ $($service.Key): localhost:$($service.Value) - ปิดอยู่" -ForegroundColor Red
    }
}

# 5. Test Backend API specifically
Write-Host ""
Write-Host "[5/7] ทดสอบ Backend API..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Backend API ตอบสนอง: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
}
catch {
    Write-Host "❌ Backend API ไม่ตอบสนอง: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Try to start services
Write-Host ""
Write-Host "[6/7] พยายามเริ่มบริการ..." -ForegroundColor Yellow

$dockerPath = "d:\YOUTUBE-TRANSLATE\docker"
if (Test-Path $dockerPath) {
    Write-Host "📁 เปลี่ยนไดเรกทอรีไป: $dockerPath" -ForegroundColor Gray
    Set-Location $dockerPath
    
    try {
        Write-Host "🚀 เริ่ม Docker Services..." -ForegroundColor Cyan
        docker compose -f docker-compose-simple.yml up -d 2>&1
        
        Write-Host "⏳ รอ 20 วินาทีให้บริการเริ่มต้น..." -ForegroundColor Yellow
        Start-Sleep -Seconds 20
        
        # Test again
        Write-Host "🔄 ทดสอบ Backend อีกครั้ง..." -ForegroundColor Cyan
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 10
            Write-Host "✅ Backend เริ่มต้นสำเร็จ!" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️  Backend ยังไม่พร้อม, ลองอีกครั้งใน 30 วินาที" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "❌ ไม่สามารถเริ่มบริการได้: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ ไม่พบโฟลเดอร์ docker: $dockerPath" -ForegroundColor Red
}

# 7. Final recommendations
Write-Host ""
Write-Host "[7/7] คำแนะนำ..." -ForegroundColor Yellow

Write-Host ""
Write-Host "🔧 หากยังมีปัญหา ลองทำตามขั้นตอนนี้:" -ForegroundColor Cyan
Write-Host "   1. เปิด Docker Desktop" -ForegroundColor White
Write-Host "   2. รอให้ Docker เริ่มต้นเสร็จ (ดูที่ System Tray)" -ForegroundColor White  
Write-Host "   3. รันคำสั่ง: docker ps" -ForegroundColor White
Write-Host "   4. รันคำสั่ง: docker compose -f docker-compose-simple.yml up -d" -ForegroundColor White
Write-Host "   5. รอ 30 วินาที แล้วเทส: http://localhost:8000/health" -ForegroundColor White

Write-Host ""
Write-Host "📱 ทดสอบ Manual:" -ForegroundColor Cyan  
Write-Host "   • เปิดเบราว์เซอร์ไป: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • ทดสอบ health endpoint: http://localhost:8000/health" -ForegroundColor White
Write-Host "   • ดู logs: docker compose logs backend" -ForegroundColor White

Write-Host ""
Write-Host "🎬 หลังจาก Backend พร้อมแล้ว:" -ForegroundColor Cyan
Write-Host "   • เปิดไฟล์: d:\YOUTUBE-TRANSLATE\test-video-playback.html" -ForegroundColor White
Write-Host "   • หรือเปิด Frontend: http://localhost:3000" -ForegroundColor White

Write-Host ""
Write-Host "กด Enter เพื่อออก..."
Read-Host
