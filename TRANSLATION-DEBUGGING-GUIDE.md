# YouTube Video Translator - Translation Issues Debugging Guide

## 🔍 การวินิจฉัยปัญหา "แปลไม่ได้"

### 📝 สาเหตุที่เป็นไปได้:

1. **Docker ไม่ทำงาน**
   - Docker Desktop ไม่เปิด
   - Docker Engine หยุดทำงาน
   - Containers ไม่ได้รัน

2. **Services ไม่พร้อม**
   - LibreTranslate (Port 5000) - สำหรับแปลข้อความ
   - Whisper (Port 5001) - สำหรับแปลงเสียงเป็นข้อความ
   - TTS (Port 5002) - สำหรับแปลงข้อความเป็นเสียง
   - Backend API (Port 8000) - API หลัก

3. **ขั้นตอนการแปลมีข้อผิดพลาด**
   - Speech-to-Text ล้มเหลว
   - Text Translation ล้มเหลว  
   - Text-to-Speech ล้มเหลว
   - Video merging ล้มเหลว

## 🛠️ ขั้นตอนการแก้ไข

### 1. ตรวจสอบ Docker
```powershell
# ตรวจสอบ Docker Desktop
Get-Process "Docker Desktop" -ErrorAction SilentlyContinue

# ตรวจสอบ Docker service
Get-Service docker -ErrorAction SilentlyContinue

# ลอง start Docker service
Start-Service docker
```

### 2. ตรวจสอบ Containers
```bash
# ดู containers ที่ทำงาน
docker ps

# ดู containers ทั้งหมด
docker ps -a

# ดู logs ของ backend
docker logs youtube-translate-backend
```

### 3. เริ่ม Services ใหม่
```bash
cd d:\YOUTUBE-TRANSLATE\docker
docker-compose -f docker-compose-simple.yml down
docker-compose -f docker-compose-simple.yml up -d
```

### 4. ตรวจสอบ Services
```bash
# ทดสอบ Backend API
curl http://localhost:8000/health

# ทดสอบ LibreTranslate
curl http://localhost:5000/languages

# ตรวจสอบ ports
netstat -an | findstr :8000
netstat -an | findstr :5000
```

### 5. ทดสอบ Translation Pipeline

#### A. ทดสอบ LibreTranslate
```bash
curl -X POST http://localhost:5000/translate \
  -H "Content-Type: application/json" \
  -d '{"q":"Hello world","source":"en","target":"th"}'
```

#### B. ทดสอบ TTS Service  
```bash
curl -X POST http://localhost:5002/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"สวัสดี","language":"th","speech_rate":0.85}'
```

#### C. ทดสอบ Backend Pipeline
```bash
curl -X POST http://localhost:8000/process-video/ \
  -H "Content-Type: application/json" \
  -d '{"youtube_url":"https://www.youtube.com/watch?v=test","target_language":"th"}'
```

## 🔧 การแก้ไขเฉพาะปัญหา

### ปัญหา 1: LibreTranslate ไม่ทำงาน
```bash
# ตรวจสอบ logs
docker logs youtube-translate-libretranslate

# Restart service
docker restart youtube-translate-libretranslate
```

### ปัญหา 2: Backend API Error
```bash
# ตรวจสอบ logs
docker logs youtube-translate-backend --tail 100

# ตรวจสอบ environment variables
docker exec youtube-translate-backend env | grep -E "(TRANSLATION|WHISPER|TTS)"
```

### ปัญหา 3: Speech Rate Analysis ล้มเหลว
- ตรวจสอบว่า librosa ติดตั้งใน backend container
- ดู logs สำหรับ speech analysis errors
- ระบบจะใช้ fallback rate 0.85 หากวิเคราะห์ไม่ได้

### ปัญหา 4: Memory Issues
```bash
# ตรวจสอบ resource usage
docker stats

# เพิ่ม memory limit
# แก้ไขใน docker-compose.yml
deploy:
  resources:
    limits:
      memory: 8G
```

## 🎯 การทดสอบแบบ Manual

### 1. เปิดเบราว์เซอร์ทดสอบ:
- http://localhost:8000/docs - Backend API docs
- http://localhost:3000 - Frontend
- http://localhost:5000/docs - LibreTranslate docs

### 2. ใช้ Frontend ทดสอบ:
- อัพโหลดไฟล์วิดีโอสั้นๆ (< 30 วินาที)
- ตั้งภาษาต้นทางและเป้าหมาย
- ดูขั้นตอนการประมวลผล

### 3. ตรวจสอบ Output:
- ไฟล์ใน `d:\YOUTUBE-TRANSLATE\output\`
- Video files, audio files, subtitle files

## 🚨 Warning Signs

⚠️ **ถ้าเห็นข้อความนี้ = มีปัญหา:**
- "Failed to fetch" - Backend ไม่ทำงาน
- "Connection refused" - Service ไม่พร้อม
- "500 Internal Server Error" - Error ใน code
- "Translation failed" - LibreTranslate ปัญหา
- "Speech analysis failed" - Librosa หรือ audio issue

## 📋 Quick Fix Checklist

✅ **ก่อนแปลวิดีโอ ตรวจสอบ:**
1. [ ] Docker Desktop เปิดอยู่
2. [ ] All containers running: `docker ps`
3. [ ] Backend health: `curl localhost:8000/health`
4. [ ] LibreTranslate ready: `curl localhost:5000/languages`  
5. [ ] TTS ready: `curl localhost:5002/health`
6. [ ] No port conflicts
7. [ ] Enough disk space (>2GB free)
8. [ ] Enough RAM (>4GB available)

**หากทุกอย่างเรียบร้อย แต่ยังแปลไม่ได้ → ดู Backend logs เพื่อหาสาเหตุที่แท้จริง**
