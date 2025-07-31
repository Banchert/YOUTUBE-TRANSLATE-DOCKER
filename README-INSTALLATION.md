# 🚀 YouTube Video Translator - คู่มือการติดตั้งและใช้งาน (Windows)

## 📁 ไฟล์สำคัญที่ได้สร้างขึ้น

### ไฟล์การติดตั้งและจัดการ
- **`Run.bat`** - เมนูจัดการระบบแบบครบครัน (แนะนำ)
- **`Install.ps1`** - สคริปต์ PowerShell สำหรับติดตั้งอัตโนมัติ
- **`Start.bat`** - เริ่มระบบแบบง่าย
- **`Stop.bat`** - หยุดระบบ
- **`Status.bat`** - ตรวจสอบสถานะระบบ

## 🎯 วิธีการติดตั้งและใช้งาน

### วิธีที่ 1: ใช้ Run.bat (แนะนำสำหรับผู้เริ่มต้น)

1. **คลิกขวาที่ `Run.bat`** → เลือก **"Run as administrator"**
2. เลือกเมนู **"1. ติดตั้งและเตรียมระบบครั้งแรก"**
3. รอให้การติดตั้งเสร็จสิ้น (อาจใช้เวลา 15-45 นาที)
4. เลือกเมนู **"2. เริ่มใช้งานระบบ"**
5. เปิดเว็บเบราว์เซอร์ไปที่ **http://localhost:3000**

### วิธีที่ 2: ใช้ PowerShell Script (สำหรับการติดตั้งอัตโนมัติ)

1. เปิด **PowerShell** ด้วยสิทธิ์ Administrator
2. รันคำสั่ง:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\Install.ps1
   ```
3. รอให้การติดตั้งเสร็จสิ้น
4. รันไฟล์ **`Start.bat`**

### วิธีที่ 3: การใช้งานแบบง่าย (หลังติดตั้งแล้ว)

- **เริ่มใช้งาน**: ดับเบิลคลิก `Start.bat`
- **หยุดการทำงาน**: ดับเบิลคลิก `Stop.bat`
- **ตรวจสอบสถานะ**: ดับเบิลคลิก `Status.bat`

## 📋 ข้อกำหนดของระบบ

### ฮาร์ดแวร์
- **RAM**: อย่างน้อย 8GB (แนะนำ 16GB+)
- **พื้นที่ดิสก์**: อย่างน้อย 20GB
- **CPU**: 4 cores ขึ้นไป
- **อินเทอร์เน็ต**: สำหรับดาวน์โหลด AI models

### ซอฟต์แวร์
- **Windows 10/11** (64-bit)
- **Docker Desktop** (จะติดตั้งอัตโนมัติ)
- **PowerShell 5.1+** (มาพร้อม Windows)

## 🌐 การเข้าใช้งาน

หลังจากเริ่มระบบแล้ว สามารถเข้าใช้งานผ่าน:

- **เว็บแอปหลัก**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Translation API**: http://localhost:5000
- **System Monitor**: http://localhost:5555

## 📱 การใช้งาน YouTube Video Translator

1. **เปิดเว็บแอป**: ไปที่ http://localhost:3000
2. **ใส่ URL วิดีโอ**: วาง YouTube URL ในช่อง input
3. **เลือกภาษา**: เลือกภาษาที่ต้องการแปล (เช่น ไทย)
4. **เริ่มประมวลผล**: กดปุ่ม "เริ่มแปลวิดีโอ"
5. **รอผลลัพธ์**: ดูความคืบหน้าและดาวน์โหลดไฟล์ที่แปลแล้ว

## 🛠️ การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

#### 1. Docker ไม่ทำงาน
```
ปัญหา: [ERROR] Docker ไม่ได้เริ่มต้นการทำงาน
แก้ไข:
1. เปิด Docker Desktop
2. รอให้สถานะเป็น "Docker Desktop is running"
3. รันสคริปต์อีกครั้ง
```

#### 2. Port ถูกใช้งาน
```
ปัญหา: Port 3000, 8000 ถูกใช้งานแล้ว
แก้ไข:
1. เปิด Task Manager
2. ปิดโปรแกรมที่ใช้ port เหล่านั้น
3. หรือใช้คำสั่ง: netstat -ano | findstr :3000
```

#### 3. การดาวน์โหลด AI Models ล้มเหลว
```
ปัญหา: ไม่สามารถดาวน์โหลด Whisper/TTS models ได้
แก้ไข:
1. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
2. ลองรันใหม่อีกครั้ง
3. ใช้ VPN หากจำเป็น
```

#### 4. หน่วยความจำไม่เพียงพอ
```
ปัญหา: ระบบทำงานช้าหรือหยุดทำงาน
แก้ไข:
1. ปิดโปรแกรมอื่นๆ
2. เพิ่ม RAM ของ Docker Desktop
3. ใช้ Whisper model ขนาดเล็กกว่า (base แทน medium)
```

### คำสั่งการแก้ไขปัญหา

#### ล้างระบบและเริ่มใหม่
```batch
# รันใน Run.bat
เลือก "6. ล้างข้อมูลและเริ่มใหม่"
```

#### ดู Logs เพื่อตรวจสอบปัญหา
```batch
# รันใน Run.bat
เลือก "5. ดู Logs"
```

#### ตรวจสอบการใช้งาน Resources
```powershell
docker stats
```

## 📂 โครงสร้างไฟล์

```
YOUTUBE-TRANSLATE/
├── Run.bat              # เมนูจัดการหลัก
├── Install.ps1          # สคริปต์ติดตั้งอัตโนมัติ
├── Start.bat           # เริ่มระบบ
├── Stop.bat            # หยุดระบบ
├── Status.bat          # ตรวจสอบสถานะ
├── .env                # ตั้งค่าหลัก (สร้างอัตโนมัติ)
├── uploads/            # ไฟล์อัปโหลด
├── output/             # ไฟล์ผลลัพธ์
├── logs/               # ล็อกระบบ
├── backend/            # โค้ด Backend API
├── frontend/           # โค้ด Frontend React
├── processing/         # AI Services (Whisper, TTS, Translation)
└── docker/             # Docker configurations
```

## 🔧 การตั้งค่าขั้นสูง

### การปรับแต่งการใช้งาน Memory

แก้ไขไฟล์ `docker/docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 4G    # ปรับตามความต้องการ
```

### การเปลี่ยน AI Models

แก้ไขไฟล์ `.env`:
```env
WHISPER_MODEL=base     # เปลี่ยนจาก medium เพื่อใช้ memory น้อยลง
TTS_MODEL=tts_models/th/mai_female/glow-tts
```

### การเปิดใช้งาน GPU (หากมี NVIDIA GPU)

1. ติดตั้ง NVIDIA Docker Runtime
2. แก้ไขไฟล์ `docker-compose.yml` เพิ่ม:
   ```yaml
   runtime: nvidia
   environment:
     - WHISPER_DEVICE=cuda
     - TTS_DEVICE=cuda
   ```

## 📞 การขอความช่วยเหลือ

หากพบปัญหาในการติดตั้งหรือใช้งาน:

1. **ตรวจสอบ Logs**: รันไฟล์ `Status.bat` หรือ `Run.bat` → เลือก "5. ดู Logs"
2. **ตรวจสอบ System Requirements**: ให้แน่ใจว่าเครื่องมี RAM เพียงพอ
3. **ลองรีสตาร์ท**: หยุดระบบด้วย `Stop.bat` แล้วเริ่มใหม่ด้วย `Start.bat`
4. **Reset ระบบ**: ใช้ `Run.bat` → เลือก "6. ล้างข้อมูลและเริ่มใหม่"

## 🎉 การใช้งานที่สำเร็จ

หากทุกอย่างทำงานปกติ คุณจะเห็น:

- ✅ เว็บแอปเปิดได้ที่ http://localhost:3000
- ✅ สามารถใส่ YouTube URL และแปลวิดีโอได้
- ✅ ดาวน์โหลดไฟล์ผลลัพธ์ได้
- ✅ ระบบแสดงความคืบหน้าการประมวลผล

**ขอให้สนุกกับการใช้งาน YouTube Video Translator! 🚀**
