# 🚀 YouTube Video Translator - Quick Start

## 🏗️ ระบบทำงานแบบไหน?

### การทำงานของระบบ:
```
🌐 YouTube Video → 📥 Download → 🎵 Extract Audio → 🗣️ Speech-to-Text → 🌍 Translate → 🔊 Text-to-Speech → 📹 Merge Video
```

### ส่วนประกอบของระบบ:
- **Frontend (React)** - หน้าเว็บสำหรับผู้ใช้
- **Backend API (FastAPI)** - จัดการคำขอและประสานงาน  
- **Whisper Service** - แปลงเสียงเป็นข้อความด้วย AI
- **Translation Service** - แปลภาษาด้วย LibreTranslate
- **TTS Service** - แปลงข้อความเป็นเสียงด้วย AI
- **Database & Cache** - เก็บข้อมูลและเร่งการทำงาน

### ทำไมต้องใช้ Docker? 🤔
- **AI Models ขนาดใหญ่** - Whisper & TTS models หลาย GB
- **Dependencies ซับซ้อน** - Python, FFmpeg, CUDA drivers 
- **ติดตั้งง่าย** - รันแค่คำสั่งเดียวแทนการติดตั้งหลายโปรแกรม
- **สเถียร** - environment เหมือนกันทุกเครื่อง ไม่มีปัญหาเวอร์ชัน
- **แยกส่วน** - แต่ละ service ทำงานแยกกัน ไม่รบกวนกัน

## ⚡ เริ่มใช้งานด่วน (5 นาที)

### 1. ติดตั้ง (ครั้งแรกเท่านั้น)
1. **คลิกขวา `Run.bat`** → **"Run as administrator"**
2. เลือก **"1. ติดตั้งและเตรียมระบบครั้งแรก"**
3. รอ 15-30 นาที (ดาวน์โหลด Docker + AI models)

### 2. เริ่มใช้งาน
- **เริ่ม**: ดับเบิลคลิก `Start.bat`
- **เปิดเว็บ**: http://localhost:3000
- **หยุด**: ดับเบิลคลิก `Stop.bat`

### 3. ตรวจสอบสถานะ
เมื่อเริ่มระบบแล้ว ควรเห็น:
```
✔ Network docker_app-network         Created
✔ Volume "docker_redis_data"         Created  
✔ Volume "docker_postgres_data"      Created
✔ Container docker-postgres-1        Started
✔ Container docker-libretranslate-1  Started
✔ Container docker-redis-1           Started
```

### 4. แปลวิดีโอ
1. วาง YouTube URL
2. เลือกภาษาปลายทาง (เช่น ไทย)
3. กด "เริ่มแปลวิดีโอ"
4. ดาวน์โหลดผลลัพธ์

## 🆘 แก้ปัญหาด่วน

| ปัญหา | แก้ไข |
|-------|-------|
| Docker error | เปิด Docker Desktop รอให้ "running" |
| Port ถูกใช้ | ปิดโปรแกรมอื่นหรือรีสตาร์ทเครื่อง |
| หน่วยความจำไม่พอ | ปิดโปรแกรมอื่น หรือใช้ "base" model |
| ดาวน์โหลดล้มเหลว | ตรวจสอบอินเทอร์เน็ต ลองใหม่ |
| "version is obsolete" | ไฟล์ได้แก้ไขแล้ว ใช้ docker-compose-simple.yml |
| "top-level object must be mapping" | ปัญหา YAML format - ใช้ไฟล์ที่แก้ไขแล้ว |

### 🔧 ปัญหา Docker Compose
หากพบข้อผิดพลาด `version is obsolete` หรือ `top-level object must be mapping`:
1. ✅ ระบบได้สร้างไฟล์ `docker-compose-simple.yml` ที่ทำงานได้แล้ว
2. ✅ สคริปต์ Start.bat ใช้ไฟล์นี้โดยอัตโนมัติแล้ว
3. ✅ ระบบเริ่มต้นสำเร็จแล้ว!

### ✅ สถานะปัจจุบัน
Services ที่ทำงานแล้ว (Container Level):
- 🟢 **LibreTranslate** - Translation API (Port 5000) - Container UP
- 🟢 **PostgreSQL** - Database (Port 5432) - Container UP
- 🟢 **Redis** - Cache (Port 6379) - Container UP
- 🟢 **Docker Network** - การเชื่อมต่อระหว่าง services

Services ที่ยังไม่ตอบสนอง HTTP (ปกติ):
- 🟡 **LibreTranslate** - ใช้เวลา 2-5 นาทีในการเริ่มต้น
- 🔴 **Frontend** - ยังไม่ได้สร้าง (Port 3000)
- 🔴 **Backend** - ยังไม่ได้สร้าง (Port 8000)
- 🔴 **Whisper** - ยังไม่ได้สร้าง (Port 5001)
- 🔴 **TTS** - ยังไม่ได้สร้าง (Port 5002)

### 🕐 รอให้ LibreTranslate พร้อม
LibreTranslate ต้องการเวลา 2-5 นาทีในการเริ่มต้น:
1. ดาวน์โหลด language models
2. โหลด AI models เข้า memory
3. เริ่มต้น web server

**ลองเช็คอีกครั้งใน 2-3 นาที หรือเปิด http://localhost:5000 ในเบราว์เซอร์**

## 📱 ลิงก์สำคัญ
- **Translation API**: http://localhost:5000 🟡 รอ 2-5 นาที
- **Database**: PostgreSQL:5432 ✅ Container ทำงานแล้ว
- **Cache**: Redis:6379 ✅ Container ทำงานแล้ว
- **เว็บแอป**: http://localhost:3000 ⚠️ ต้องสร้างให้เสร็จ
- **API Docs**: http://localhost:8000/docs ⚠️ ต้องสร้างให้เสร็จ
- **Status**: รัน `Status.bat`

### 🧪 ทดสอบ Services
**ตรวจสอบ LibreTranslate (รอ 2-5 นาที):**
```bash
# วิธี 1: เปิดเบราว์เซอร์
http://localhost:5000

# วิธี 2: ใช้ curl (ถ้ามี)
curl http://localhost:5000/languages
```

**ตรวจสอบ Database Connection:**
```bash
# ใช้ psql (ถ้ามี PostgreSQL client)
psql -h localhost -p 5432 -U postgres -d youtube_translator
# Password: password
```

**ตรวจสอบ Redis:**
```bash
# ใช้ redis-cli (ถ้ามี Redis client)
redis-cli -h localhost -p 6379 ping
```

### 🚧 ขั้นตอนต่อไป
ตอนนี้ infrastructure services ทำงานแล้ว:

**Phase 1: ✅ Infrastructure (เสร็จแล้ว)**
- PostgreSQL Database
- Redis Cache  
- LibreTranslate API (กำลังเริ่มต้น)
- Docker Network

**Phase 2: � Application Services (พร้อม Build)**
1. ✅ **Backend API (FastAPI)** - โค้ดพร้อมแล้ว
2. ✅ **Frontend (React)** - โค้ดพร้อมแล้ว
3. 🔴 **Whisper Service** - ยังไม่สร้าง
4. 🔴 **TTS Service** - ยังไม่สร้าง

### 🚀 เริ่มสร้างเว็บแอป
**มีปัญหาใน Build? ใช้คำสั่งนี้แก้ไขและ build ใหม่:**

```batch
# วิธี 1: ใช้ FixAndBuild.bat (แนะนำ - แก้ปัญหาอัตโนมัติ)
ดับเบิลคลิก FixAndBuild.bat

# วิธี 2: ใช้ Build.bat (ถ้าไม่มีปัญหา)
ดับเบิลคลิก Build.bat

# วิธี 3: Manual
cd docker
docker-compose -f docker-compose-simple.yml build --no-cache
docker-compose -f docker-compose-simple.yml up -d
```

### 🐛 ปัญหาที่แก้ไขแล้ว:
- ✅ **Backend**: ลด dependencies ที่ทำให้ติดตั้งล้มเหลว
- ✅ **Frontend**: สร้างไฟล์ `index.css` และ components ที่ขาดหาย
- ✅ **ErrorBoundary**: สร้าง error handling component
- ✅ **Store**: สร้าง state management ด้วย Zustand

**หลังจาก build เสร็จ (5-10 นาที):**
- Frontend: http://localhost:3000 ✅
- Backend API: http://localhost:8000 ✅  
- API Docs: http://localhost:8000/docs ✅

## 💡 เคล็ดลับ
- ใช้วิดีโอสั้นๆ (< 10 นาที) สำหรับการทดสอบ
- Model "medium" ให้คุณภาพดี แต่ใช้ RAM มาก
- Model "base" เร็วกว่า ใช้ RAM น้อยกว่า
- หยุดระบบเมื่อไม่ใช้เพื่อประหยัด RAM

## 🔍 ทำความเข้าใจระบบ

### ขั้นตอนการแปลวิดีโอ:
1. **ดาวน์โหลดวิดีโอ** จาก YouTube (yt-dlp)
2. **แยกเสียง** ออกมาเป็นไฟล์ audio (FFmpeg)
3. **Speech-to-Text** แปลงเสียงเป็นข้อความ (Whisper AI)
4. **แปลภาษา** ข้อความเป็นภาษาเป้าหมาย (LibreTranslate)
5. **Text-to-Speech** แปลงข้อความเป็นเสียงใหม่ (TTS AI)
6. **รวมไฟล์** วิดีโอเดิม + เสียงใหม่ (FFmpeg)

### ทำไมใช้เวลานาน?
- **AI Models** ต้องประมวลผลทีละส่วน
- **Video Quality** วิดีโอคุณภาพสูงใช้เวลามาก
- **Language Models** การแปลและสังเคราะห์เสียงซับซ้อน
- **Hardware** CPU/GPU และ RAM มีผลต่อความเร็ว

### ทำไมต้องใช้ Docker?
แทนที่จะติดตั้ง:
- Python 3.9+ และ 20+ libraries
- Node.js และ npm packages  
- PostgreSQL database
- Redis server
- FFmpeg และ codecs
- AI models (Whisper 2GB+, TTS 1GB+)
- การตั้งค่า environment variables

**Docker ทำให้ติดตั้งแค่ 1 คำสั่ง และทำงานเหมือนกันทุกเครื่อง!**

**🎉 พร้อมใช้งาน! ขอให้สนุกกับการแปลวิดีโอ**
