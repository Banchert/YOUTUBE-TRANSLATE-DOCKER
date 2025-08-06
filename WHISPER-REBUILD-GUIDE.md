# Whisper Container Rebuild Guide

## 🔧 ทำไมต้อง Rebuild Container?

### ✅ **สาเหตุที่ต้อง rebuild:**
1. **แก้ไข source code** - whisper_server.py เปลี่ยนแปลง
2. **เพิ่ม language parameter** - Form data support
3. **Dependencies เปลี่ยน** - requirements.txt อัพเดต
4. **Dockerfile แก้ไข** - build process เปลี่ยน

### 🎯 **การแก้ไขที่ทำไป:**
- ✅ เพิ่ม `language: Optional[str] = Form(None)` 
- ✅ รองรับการบังคับภาษา `model.transcribe(audio, language="th")`
- ✅ Enhanced logging และ error handling
- ✅ Form data validation

## 🚀 วิธี Rebuild Container

### Option 1: **Full Rebuild (แนะนำ)**
```bash
cd d:\YOUTUBE-TRANSLATE\docker

# หยุด services ทั้งหมด
docker-compose -f docker-compose.yml down

# Rebuild Whisper service (no cache)
docker-compose -f docker-compose.yml build --no-cache whisper-service

# เริ่ม services ทั้งหมด
docker-compose -f docker-compose.yml up -d
```

### Option 2: **Rebuild เฉพาะ Whisper**
```bash
# หยุดเฉพาะ Whisper
docker-compose -f docker-compose.yml stop whisper-service

# Rebuild 
docker-compose -f docker-compose.yml build whisper-service

# เริ่มเฉพาะ Whisper
docker-compose -f docker-compose.yml up -d whisper-service
```

### Option 3: **ใช้ Batch Script**
```bash
# รัน script ที่สร้างไว้
.\rebuild-whisper.bat
```

## 🔍 การตรวจสอบหลัง Rebuild

### 1. **ตรวจสอบ Container Status:**
```bash
docker ps | grep whisper
```

### 2. **ดู Logs:**
```bash
docker logs docker-whisper-service-1 --tail 20
```

### 3. **ทดสอบ Health Endpoint:**
```bash
curl http://localhost:5001/health
```

### 4. **ทดสอบ Language Parameter:**
```bash
curl -X POST http://localhost:5001/transcribe \
  -F "file=@test.wav" \
  -F "language=th" \
  -F "use_gpu=true"
```

## ⚠️ Troubleshooting

### ❌ **หาก rebuild ล้มเหลว:**

1. **Docker ไม่ทำงาน:**
   ```bash
   # ตรวจสอบ Docker Desktop
   docker --version
   docker info
   ```

2. **Port conflicts:**
   ```bash
   # ตรวจสอบ port 5001
   netstat -an | findstr :5001
   ```

3. **Memory issues:**
   ```bash
   # ตรวจสอบ Docker resources
   docker system df
   docker system prune -f
   ```

4. **Build cache issues:**
   ```bash
   # ลบ cache และ rebuild
   docker builder prune -f
   docker-compose build --no-cache
   ```

### ❌ **หาก Whisper ไม่ start:**

1. **ดู detailed logs:**
   ```bash
   docker-compose logs whisper-service
   ```

2. **ตรวจสอบ Dockerfile:**
   ```bash
   # ใน processing/whisper/Dockerfile
   # ต้องมี COPY whisper_server.py
   ```

3. **เช็ค dependencies:**
   ```bash
   # ใน processing/whisper/requirements.txt
   # ต้องมี fastapi, torch, whisper
   ```

## 🎯 สัญญาณว่า Rebuild สำเร็จ

### ✅ **Container Health:**
```json
{
  "status": "healthy",
  "model_type": "local",
  "device": "cpu",
  "available_models": ["tiny", "base", "small", "medium", "large"]
}
```

### ✅ **Logs แสดง:**
```
INFO: Loading Whisper model: medium on cpu
INFO: Whisper model loaded successfully on cpu
INFO: Uvicorn running on http://0.0.0.0:5001
```

### ✅ **Language Support:**
```json
{
  "supported_languages": [
    {"code": "th", "name": "Thai"},
    {"code": "en", "name": "English"},
    {"code": "auto", "name": "Auto-detect"}
  ]
}
```

## 🚀 Next Steps หลัง Rebuild

1. **ทดสอบ Whisper แยก:**
   ```bash
   python test_whisper_language_forcing.py
   ```

2. **ทดสอบ Full Pipeline:**
   - เปิด Frontend: http://localhost:3000
   - อัพโหลดไฟล์เสียง/วิดีโอ
   - เลือกภาษาต้นทางชัดเจน
   - ดูผลลัพธ์

3. **Monitor Logs:**
   ```bash
   docker logs docker-whisper-service-1 -f
   ```

## 📋 Checklist

- [ ] Docker Desktop เปิดอยู่
- [ ] หยุด containers เก่า
- [ ] Rebuild whisper-service
- [ ] เริ่ม services ใหม่  
- [ ] ทดสอบ health endpoint
- [ ] ทดสอบ language parameter
- [ ] ทดสอบผ่าน Frontend

**Rebuild เสร็จแล้ว → ทดสอบการบังคับภาษาใน Whisper! 🎯**
