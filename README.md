# 🚀 YouTube Video Translator - คู่มือการติดตั้งแบบละเอียด

## 📋 สารบัญ
1. [ความต้องการของระบบ](#ความต้องการของระบบ)
2. [การติดตั้งแบบ Docker (แนะนำ)](#การติดตั้งแบบ-docker)
3. [การติดตั้งแบบ Manual](#การติดตั้งแบบ-manual)
4. [การทดสอบระบบ](#การทดสอบระบบ)
5. [การแก้ไขปัญหา](#การแก้ไขปัญหา)

---

## 🔧 ความต้องการของระบบ

### Hardware Requirements:
- **RAM**: อย่างน้อย 8GB (แนะนำ 16GB+)
- **Storage**: อย่างน้อย 20GB พื้นที่ว่าง
- **CPU**: 4 cores ขึ้นไป (สำหรับประมวลผล AI models)
- **Network**: อินเทอร์เน็ตเสถียร (สำหรับ download models)

### Software Requirements:
- **Docker**: 20.10+ และ Docker Compose 2.0+
- **Git**: สำหรับ clone repository
- **Node.js**: 18+ (ถ้าติดตั้งแบบ manual)
- **Python**: 3.9+ (ถ้าติดตั้งแบบ manual)

### Operating System:
- ✅ **Linux** (Ubuntu 20.04+, CentOS 8+)
- ✅ **macOS** (10.15+)
- ✅ **Windows** (10/11 + WSL2)

---

## 🐳 การติดตั้งแบบ Docker (แนะนำ)

### Step 1: ติดตั้ง Docker

#### Ubuntu/Debian:
```bash
# อัปเดตระบบ
sudo apt update && sudo apt upgrade -y

# ติดตั้ง Docker
sudo apt install -y docker.io docker-compose

# เพิ่ม user เข้า docker group
sudo usermod -aG docker $USER

# รีสตาร์ท session หรือ logout/login
newgrp docker

# ตรวจสอบการติดตั้ง
docker --version
docker-compose --version
```

#### macOS:
```bash
# ติดตั้งผ่าน Homebrew
brew install --cask docker

# หรือดาวน์โหลดจาก https://docker.com/products/docker-desktop
# เปิด Docker Desktop และรอให้เริ่มต้น

# ตรวจสอบ
docker --version
docker-compose --version
```

#### Windows:
```bash
# ติดตั้ง Docker Desktop for Windows
# ดาวน์โหลดจาก: https://docker.com/products/docker-desktop

# เปิด PowerShell หรือ WSL2
docker --version
docker-compose --version
```

### Step 2: Clone Repository

```bash
# Clone project (หรือดาวน์โหลด files ที่ให้ไว้)
mkdir youtube-translator
cd youtube-translator

# สร้างโครงสร้าง directory ตาม artifacts ที่ให้ไว้
mkdir -p {frontend,backend,processing/{whisper,tts,translation},database,nginx,monitoring,uploads,output,logs}
```

### Step 3: สร้าง Project Files

#### สร้างไฟล์ docker-compose.yml:
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Frontend React App
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    networks:
      - app-network

  # Backend FastAPI
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - DEBUG=True
      - REDIS_URL=redis://redis:6379
      - TRANSLATION_SERVICE_URL=http://translation-service:5003
      - TTS_SERVICE_URL=http://tts-service:5002
      - WHISPER_SERVICE_URL=http://whisper-service:5001
    depends_on:
      - redis
      - whisper-service
      - tts-service
      - translation-service
    networks:
      - app-network

  # Whisper Speech-to-Text Service
  whisper-service:
    build: ./processing/whisper
    ports:
      - "5001:5001"
    volumes:
      - ./uploads:/app/uploads
    environment:
      - WHISPER_MODEL=medium
      - WHISPER_DEVICE=cpu
    networks:
      - app-network

  # TTS Service
  tts-service:
    build: ./processing/tts
    ports:
      - "5002:5002"
    volumes:
      - ./uploads:/app/uploads
      - ./output:/app/output
    environment:
      - TTS_MODEL_TH=tts_models/th/mai_female/glow-tts
      - TTS_DEVICE=cpu
    networks:
      - app-network

  # Translation Service
  translation-service:
    build: ./processing/translation
    ports:
      - "5003:5003"
    environment:
      - LIBRETRANSLATE_URL=http://libretranslate:5000
    depends_on:
      - libretranslate
    networks:
      - app-network

  # LibreTranslate
  libretranslate:
    image: libretranslate/libretranslate:latest
    ports:
      - "5000:5000"
    environment:
      - LT_CHAR_LIMIT=25000
      - LT_REQ_LIMIT=200
    networks:
      - app-network

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network

volumes:
  redis_data:

networks:
  app-network:
    driver: bridge
```

### Step 4: สร้าง Dockerfile สำหรับแต่ละ Service

#### Frontend Dockerfile:
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Backend Dockerfile:
```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p uploads output logs

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Whisper Service Dockerfile:
```dockerfile
# processing/whisper/Dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
    flask==2.3.3 \
    flask-cors==4.0.0 \
    openai-whisper==20231117 \
    torch==2.1.1 \
    torchaudio==2.1.1

COPY whisper_server.py .
RUN mkdir -p uploads logs

# Download base model
RUN python -c "import whisper; whisper.load_model('base')"

EXPOSE 5001
CMD ["python", "whisper_server.py"]
```

#### TTS Service Dockerfile:
```dockerfile
# processing/tts/Dockerfile  
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    espeak \
    espeak-data \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
    flask==2.3.3 \
    flask-cors==4.0.0 \
    TTS==0.20.6 \
    torch==2.1.1

COPY tts_server.py .
RUN mkdir -p uploads output logs

EXPOSE 5002
CMD ["python", "tts_server.py"]
```

#### Translation Service Dockerfile:
```dockerfile
# processing/translation/Dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install \
    flask==2.3.3 \
    flask-cors==4.0.0 \
    requests==2.31.0

COPY translation_server.py .
RUN mkdir -p logs

EXPOSE 5003
CMD ["python", "translation_server.py"]
```

### Step 5: สร้าง Environment Files

#### .env:
```env
# .env
DEBUG=True
SECRET_KEY=your-secret-key-for-testing

# Redis
REDIS_URL=redis://redis:6379

# Services
WHISPER_SERVICE_URL=http://whisper-service:5001
TTS_SERVICE_URL=http://tts-service:5002
TRANSLATION_SERVICE_URL=http://translation-service:5003

# Processing
MAX_VIDEO_DURATION=1800
MAX_FILE_SIZE=200
WHISPER_MODEL=medium
TTS_MODEL_TH=tts_models/th/mai_female/glow-tts
```

#### frontend/.env:
```env
# frontend/.env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=http://localhost:8000
```

### Step 6: สร้าง Setup Script

#### setup.sh:
```bash
#!/bin/bash

echo "🚀 Setting up YouTube Video Translator..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Create directories
mkdir -p uploads output logs

# Copy environment files
if [ ! -f .env ]; then
    echo "DEBUG=True" > .env
    echo "SECRET_KEY=test-secret-key" >> .env
fi

# Build and start services
echo "🔨 Building services..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 60

# Health checks
echo "🔍 Checking service health..."

services=(
    "http://localhost:8000/health:Backend"
    "http://localhost:5001/health:Whisper"
    "http://localhost:5002/health:TTS"
    "http://localhost:5003/health:Translation"
    "http://localhost:5000/languages:LibreTranslate"
    "http://localhost:3000:Frontend"
)

for service in "${services[@]}"; do
    url="${service%%:*}"
    name="${service##*:}"
    
    if curl -f "$url" &> /dev/null; then
        echo "✅ $name is healthy"
    else
        echo "⚠️ $name is not responding"
    fi
done

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📱 Access URLs:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8000/docs"
echo "   Whisper:      http://localhost:5001/health"
echo "   TTS:          http://localhost:5002/health"
echo "   Translation:  http://localhost:5003/health"
echo ""
echo "📝 Useful commands:"
echo "   View logs:    docker-compose logs -f [service]"
echo "   Stop:         docker-compose down"
echo "   Restart:      docker-compose restart [service]"
```

### Step 7: เริ่มต้นระบบ

```bash
# ให้สิทธิ์ execute
chmod +x setup.sh

# รัน setup script
./setup.sh

# หรือรันแบบ manual
docker-compose up -d

# ดู logs
docker-compose logs -f
```

---

## 💻 การติดตั้งแบบ Manual (สำหรับ Development)

### Step 1: ติดตั้ง Backend

```bash
# สร้าง Python virtual environment
cd backend
python3 -m venv venv

# Activate environment
# Linux/macOS:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# Download AI models
python -c "import whisper; whisper.load_model('medium')"
python -c "from TTS.api import TTS; TTS('tts_models/th/mai_female/glow-tts')"

# สร้าง directories
mkdir -p uploads output logs

# รัน backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: ติดตั้ง Frontend

```bash
# เปิด terminal ใหม่
cd frontend

# ติดตั้ง Node.js dependencies
npm install

# สร้าง .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# รัน frontend
npm start
```

### Step 3: ติดตั้ง Processing Services

#### Whisper Service:
```bash
# Terminal ใหม่
cd processing/whisper

# ติดตั้ง dependencies
pip install flask flask-cors openai-whisper torch

# รัน service
python whisper_server.py
```

#### TTS Service:
```bash
# Terminal ใหม่  
cd processing/tts

# ติดตั้ง dependencies
pip install flask flask-cors TTS torch

# รัน service
python tts_server.py
```

#### Translation Service:
```bash
# Terminal ใหม่
cd processing/translation

# ติดตั้ง dependencies
pip install flask flask-cors requests

# รัน service
python translation_server.py
```

#### LibreTranslate:
```bash
# รัน LibreTranslate ด้วย Docker
docker run -ti --rm -p 5000:5000 libretranslate/libretranslate

# หรือติดตั้งแบบ pip
pip install libretranslate
libretranslate --port 5000
```

#### Redis:
```bash
# รัน Redis ด้วย Docker
docker run -d -p 6379:6379 redis:alpine

# หรือติดตั้งในระบบ
# Ubuntu: sudo apt install redis-server
# macOS: brew install redis
```

---

## 🧪 การทดสอบระบบ

### Test 1: Health Checks

```bash
# ตรวจสอบ services ทั้งหมด
curl http://localhost:8000/health
curl http://localhost:5001/health  
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5000/languages
```

### Test 2: API Testing

```bash
# ทดสอบ translation service
curl -X POST http://localhost:5003/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "target_lang": "th"}'

# ทดสอบ TTS service
curl -X POST http://localhost:5002/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "สวัสดีครับ", "language": "th"}'
```

### Test 3: Frontend Testing

1. เปิด http://localhost:3000
2. ใส่ YouTube URL (เช่น: https://www.youtube.com/watch?v=dQw4w9WgXcQ)
3. เลือกภาษาเป้าหมายเป็น "ไทย"
4. กดปุ่ม "เริ่มแปลวิดีโอ"
5. รอดู progress และผลลัพธ์

### Test 4: End-to-End Testing

```python
# test_e2e.py
import requests
import time

def test_video_processing():
    # Start processing
    response = requests.post("http://localhost:8000/process-video/", json={
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "target_language": "th"
    })
    
    task_id = response.json()["task_id"]
    print(f"Task ID: {task_id}")
    
    # Check status
    while True:
        status = requests.get(f"http://localhost:8000/status/{task_id}")
        data = status.json()
        
        print(f"Progress: {data['progress']}% - {data['message']}")
        
        if data['status'] == 'completed':
            print("✅ Processing completed!")
            break
        elif data['status'] == 'failed':
            print("❌ Processing failed!")
            break
            
        time.sleep(10)

if __name__ == "__main__":
    test_video_processing()
```

---

## 🔧 การแก้ไขปัญหา

### ปัญหาที่พบบ่อย:

#### 1. Port Already in Use
```bash
# ตรวจสอบ port ที่ใช้
sudo netstat -tlnp | grep :8000

# Kill process
sudo kill -9 <PID>

# หรือเปลี่ยน port ใน docker-compose.yml
```

#### 2. Docker Build Failed
```bash
# ลบ cache และ build ใหม่
docker system prune -a
docker-compose build --no-cache

# ตรวจสอบ disk space
df -h
```

#### 3. AI Models Download Failed
```bash
# Manual download models
docker exec -it <container_name> bash
python -c "import whisper; whisper.load_model('medium')"
python -c "from TTS.api import TTS; TTS('tts_models/th/mai_female/glow-tts')"
```

#### 4. Memory Issues
```bash
# ตรวจสอบ memory usage
docker stats

# เพิ่ม memory limit ใน docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

#### 5. Network Issues
```bash
# ตรวจสอบ Docker network
docker network ls
docker network inspect youtube-translator_app-network

# Restart network
docker-compose down
docker-compose up -d
```

### Debug Commands:

```bash
# ดู logs แบบ real-time
docker-compose logs -f backend
docker-compose logs -f whisper-service

# เข้าไปใน container
docker exec -it youtube-translator_backend_1 bash

# ตรวจสอบ service ภายใน container
curl http://localhost:8000/health

# ดู resource usage
docker stats --no-stream
```

### Performance Tuning:

```bash
# ปรับ CPU และ Memory limits
# ใน docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      memory: 2G

# Enable GPU (ถ้ามี)
runtime: nvidia
environment:
  - WHISPER_DEVICE=cuda
  - TTS_DEVICE=cuda
```

---

## 📚 เอกสารเพิ่มเติม

### Useful Links:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000/health
- **Whisper Service**: http://localhost:5001/health
- **TTS Service**: http://localhost:5002/health
- **Translation Service**: http://localhost:5003/health

### Monitoring:
```bash
# Service status
docker-compose ps

# Resource monitoring
docker stats

# Logs monitoring
docker-compose logs -f --tail=100
```

### Backup & Recovery:
```bash
# Backup data
tar -czf backup-$(date +%Y%m%d).tar.gz uploads output logs

# Restore data  
tar -xzf backup-YYYYMMDD.tar.gz
```

---

## 🎉 เสร็จสิ้น!

หลังจากติดตั้งเสร็จแล้ว คุณสามารถ:

1. **เข้าใช้งาน**: http://localhost:3000
2. **ทดลองแปลวิดีโอ**: วาง YouTube URL และเริ่มประมวลผล
3. **ดู API Documentation**: http://localhost:8000/docs
4. **Monitor ระบบ**: ดู logs และ health checks

**Happy translating! 🚀**