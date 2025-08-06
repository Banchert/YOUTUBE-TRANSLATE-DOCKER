# Whisper Language Detection Fix - การแก้ไขปัญหาการถอดเสียงผิดภาษา

## 🎯 ปัญหาที่พบ
**"ผลลัพธ์ที่ได้ พูดไม่ตรงกับภาษาที่ต้องการให้แปล"**

### 🔍 สาเหตุหลัก:
1. **Whisper endpoint ไม่รับ `language` parameter** 
   - Backend ส่ง language มาแล้ว แต่ Whisper ไม่ใช้
   - Whisper ใช้ auto-detection เสมอ
   
2. **การบังคับภาษาไม่ทำงาน**
   - ไม่มีการส่ง language ไปยัง Whisper model
   - Parameter ไม่ถูกส่งเป็น Form data

3. **ไม่มีการ validate ผลลัพธ์**
   - ไม่เช็คว่าภาษาที่ตรวจพบตรงกับที่ต้องการหรือไม่

## ✅ การแก้ไขที่ทำไปแล้ว

### 1. **แก้ไข Whisper Server** (`processing/whisper/whisper_server.py`)

#### A. เพิ่ม language parameter:
```python
@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...), 
    use_gpu: Optional[bool] = Form(True),
    language: Optional[str] = Form(None)  # ← เพิ่มใหม่
):
```

#### B. รองรับการบังคับภาษา:
```python
# Apply language forcing if specified
transcribe_options = {}
if language and language != "auto":
    transcribe_options["language"] = language
    logger.info(f"🎯 Forcing Whisper to use language: {language}")
else:
    logger.info("🔍 Using Whisper auto language detection")

result = model.transcribe(temp_path, **transcribe_options)
```

#### C. Enhanced logging:
```python
lang_info = f"forced language: {language}" if language and language != "auto" else "auto-detect"
logger.info(f"Transcribing audio file: {file.filename} (GPU: {use_gpu}, {lang_info})")
```

### 2. **แก้ไข API Fallback** 
```python
def transcribe_with_api(audio_path, language=None):
    # รองรับ language parameter สำหรับ external API
    if language and language != "auto":
        logger.info(f"🎯 API transcription with forced language: {language}")
```

## 🔧 วิธีการทำงานใหม่

### 1. **Frontend → Backend → Whisper Flow:**
```
[Frontend] 
  ↓ เลือกภาษาต้นทาง (source_language)
[Backend] 
  ↓ ส่ง language parameter
[Whisper] 
  ↓ บังคับใช้ภาษาที่กำหนด (ไม่ auto-detect)
[Result] 
  ↓ ถอดเสียงตามภาษาที่ต้องการ
```

### 2. **การทำงานของ Whisper Model:**
```python
# เดิม (Auto-detection)
result = model.transcribe(audio_file)

# ใหม่ (Language forcing)
result = model.transcribe(audio_file, language="th")  # บังคับไทย
result = model.transcribe(audio_file, language="en")  # บังคับอังกฤษ
```

### 3. **การ Validate:**
```python
detected_language = result.get('language', source_language)

if detected_language != source_language:
    logger.warning(f"Language mismatch! Requested: {source_language}, Detected: {detected_language}")
```

## 🧪 การทดสอบ

### 1. **รัน Whisper Test Script:**
```bash
python test_whisper_language_forcing.py
```

### 2. **ทดสอบ Manual:**
```bash
# ทดสอบ API endpoint
curl -X POST http://localhost:5001/transcribe \
  -F "file=@audio.wav" \
  -F "language=th"
```

### 3. **ตรวจสอบ Logs:**
```bash
docker logs youtube-translate-whisper
docker logs youtube-translate-backend | grep -i whisper
```

## 🎯 ผลลัพธ์ที่คาดหวัง

### ✅ **ก่อนแก้ไข:**
- Whisper ใช้ auto-detection เสมอ
- ถอดเสียงเป็นภาษาที่ตรวจพบ (อาจผิด)
- ไม่สามารถบังคับภาษาได้

### ✅ **หลังแก้ไข:**
- Whisper ใช้ภาษาที่ Frontend เลือก
- ถอดเสียงตามภาษาที่ต้องการ
- มี logging ชัดเจนว่าใช้ภาษาอะไร

## 🚨 การแก้ไขเพิ่มเติม (ถ้าจำเป็น)

### 1. **ปรับ Frontend ให้เลือกภาษาชัดเจน:**
```javascript
// เพิ่มตัวเลือกภาษาต้นทาง
const sourceLanguages = [
  { code: "en", name: "English" },
  { code: "th", name: "ไทย" },
  { code: "ja", name: "日本語" },
  { code: "zh", name: "中文" }
];
```

### 2. **เพิ่มการ validate ใน Backend:**
```python
# ตรวจสอบความถูกต้องของ transcript
if len(transcript.strip()) < 10:
    logger.warning("Transcript too short - possible transcription error")

# ตรวจสอบภาษาที่ตรวจพบ
confidence_score = result.get('confidence', 0)
if confidence_score < 0.5:
    logger.warning(f"Low confidence score: {confidence_score}")
```

### 3. **เพิ่มตัวเลือก Whisper Model:**
```python
# ใช้ model ขนาดใหญ่สำหรับความแม่นยำ
model_name = os.getenv("WHISPER_MODEL", "large")  # เปลี่ยนจาก medium
```

## 📋 Troubleshooting Guide

### ❌ **ถ้ายังถอดเสียงผิดภาษา:**
1. ตรวจสอบ logs: `docker logs youtube-translate-whisper`
2. ทดสอบด้วยไฟล์เสียงสั้น ภาษาชัดเจน
3. เช็ค Frontend ว่าเลือกภาษาต้นทางถูกต้องไหม
4. ดูไฟล์ `transcript_*.json` ใน uploads/

### ❌ **ถ้า Whisper ไม่รับ language parameter:**
1. Restart Whisper container: `docker restart youtube-translate-whisper`
2. ตรวจสอบ Whisper version ใน container
3. ดู API docs: `http://localhost:5001/docs`

### ❌ **ถ้า Backend ไม่ส่ง language:**
1. ตรวจสอบ audio_service.py line ~85-90
2. ดู Backend logs เกี่ยวกับ Whisper requests
3. เช็ค environment variable: WHISPER_SERVICE_URL

## 🎉 สรุป

การแก้ไขนี้จะทำให้:
- **Whisper ถอดเสียงตามภาษาที่ต้องการ** (ไม่ใช่ auto-detect)
- **ลดข้อผิดพลาดจากการตรวจจับภาษาผิด**
- **มี logging ที่ชัดเจน** สำหรับ debugging
- **รองรับการทดสอบ** ด้วย script ที่สร้างไว้

**ทดสอบด้วย:** `python test_whisper_language_forcing.py` 🎯
