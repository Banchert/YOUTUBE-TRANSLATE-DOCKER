# 🎯 แก้ไขปัญหา TTS เร็วเกินไป และ Whisper ถอดเสียงผิดภาษา

## 🚨 ปัญหาที่พบ

### 1. **TTS พูดเร็วเกินไป**
- เสียงพากย์ภาษาไทยพูดเร็วผิดปกติ
- ผู้ฟังไม่สามารถตามได้
- ไม่เป็นธรรมชาติ

### 2. **Whisper ถอดเสียงผิดภาษา**  
- Whisper ถอดเสียงเป็นภาษาไทยทันที
- ไม่ได้ถอดเป็นภาษาต้นฉบับ (อังกฤษ) ก่อนแล้วค่อยแปล
- ทำให้การแปลไม่ถูกต้อง

## 🔧 การแก้ไขที่ทำไป

### 1. **แก้ไข TTS ให้พูดช้าลง**

**ไฟล์:** `processing/tts/tts_server.py`

#### เปลี่ยนจาก:
```python
# ไม่มีการควบคุมความเร็ว
communicate = edge_tts.Communicate(request.text, voice)
```

#### เป็น:
```python
# เพิ่ม SSML เพื่อควบคุมความเร็ว
ssml_text = f"""
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{request.language}">
    <voice name="{voice}">
        <prosody rate="0.85" pitch="0%" volume="100%">
            {request.text}
        </prosody>
    </voice>
</speak>
"""
communicate = edge_tts.Communicate(ssml_text, voice)
```

#### การปรับปรุง:
- ✅ **rate="0.85"** - ลดความเร็วลง 15%
- ✅ **slow=True** สำหรับ Google TTS
- ✅ เพิ่ม SSML tags เพื่อควบคุมที่ดีขึ้น

### 2. **แก้ไข Whisper ให้บังคับใช้ภาษาต้นฉบับ**

**ไฟล์:** `backend/app/services/audio_service.py`

#### เปลี่ยนจาก:
```python
async def speech_to_text(self, audio_path: str, task_id: str) -> str:
    # ไม่มีการกำหนดภาษา - ให้ Whisper auto-detect
    files = {'file': audio_file}
    response = requests.post(url, files=files)
```

#### เป็น:
```python
async def speech_to_text(self, audio_path: str, task_id: str, source_language: str = "en") -> str:
    # บังคับให้ใช้ภาษาที่กำหนด
    files = {'file': audio_file}
    data = {
        'language': source_language,  # บังคับภาษาต้นฉบับ
        'task': 'transcribe'  # ไม่ใช่ translate
    }
    response = requests.post(url, files=files, data=data)
```

#### การปรับปรุง:
- ✅ **บังคับภาษาต้นฉบับ** แทนการ auto-detect
- ✅ **task='transcribe'** แทน 'translate'
- ✅ เพิ่ม **logging เพื่อติดตาม** ภาษาที่ตรวจพบ
- ✅ **ตรวจสอบความถูกต้อง** ของภาษาที่ได้

### 3. **แก้ไข Pipeline ให้ส่งภาษาต้นฉบับ**

**ไฟล์:** `backend/app/main.py`

#### เพิ่มการส่งภาษาต้นฉบับ:
```python
# แทนที่
transcript = await audio_service.speech_to_text(audio_path, task_id)

# เป็น
source_language = tasks[task_id].get("source_language", "en")
transcript = await audio_service.speech_to_text(audio_path, task_id, source_language)
```

#### การปรับปรุง:
- ✅ ส่ง **source_language** จาก task configuration
- ✅ **Default เป็น "en"** หากไม่ระบุ
- ✅ อัพเดท **status message** ให้แสดงภาษาที่ใช้

## 📊 ผลลัพธ์ที่คาดหวัง

### Before (ก่อนแก้ไข):
```
1. วิดีโอภาษาอังกฤษ → Whisper ถอดเป็นไทย → ไม่ต้องแปล → TTS เร็ว
2. ผลลัพธ์: เสียงไทยผิดๆ + เร็วเกินไป
```

### After (หลังแก้ไข):
```
1. วิดีโอภาษาอังกฤษ → Whisper ถอดเป็นอังกฤษ → แปลเป็นไทย → TTS ช้า
2. ผลลัพธ์: เสียงไทยถูกต้อง + ความเร็วเหมาะสม
```

## 🧪 การทดสอบ

### 1. **Quick Test**
```bash
# รันการทดสอบอัตโนมัติ
python test_speech_translation_fix.py
```

### 2. **Manual Test**  
```bash
# เริ่ม services
docker compose -f docker/docker-compose-simple.yml up -d

# รอ 30 วินาที
timeout /t 30

# ทดสอบ TTS
curl -X POST http://localhost:5002/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"ทดสอบความเร็วที่ปรับปรุงแล้ว","language":"th","use_edge_tts":true}'

# ทดสอบ translation quality  
python test_translation_quality.py
```

### 3. **Integration Test**
- เปิด: `test-video-playback.html`
- หรือใช้ Frontend: http://localhost:3000
- ทดสอบแปลวิดีโอภาษาอังกฤษ

## 🎛️ การปรับแต่งเพิ่มเติม (ถ้าจำเป็น)

### ปรับความเร็ว TTS:
```python
# ใน processing/tts/tts_server.py
<prosody rate="0.8" pitch="0%" volume="100%">  # ช้ากว่าเดิม (0.8)
<prosody rate="0.9" pitch="0%" volume="100%">  # เร็วกว่าเดิม (0.9)
```

### เพิ่มภาษาต้นฉบับอื่นๆ:
```python
# ใน API request
{
    "youtube_url": "...",
    "source_language": "ja",  # ญี่ปุ่น
    "target_language": "th"
}
```

### การตรวจสอบคุณภาพ:
```python
# ใน audio_service.py
if detected_language != source_language:
    logger.warning(f"Language mismatch! Requested: {source_language}, Detected: {detected_language}")
```

## 📁 ไฟล์ที่แก้ไข

1. **`processing/tts/tts_server.py`**
   - เพิ่ม SSML สำหรับควบคุมความเร็ว
   - ตั้งค่า rate="0.85" และ slow=True

2. **`backend/app/services/audio_service.py`**
   - เพิ่ม source_language parameter
   - บังคับภาษาใน Whisper API call
   - เพิ่ม validation และ logging

3. **`backend/app/main.py`**
   - ส่ง source_language ไปยัง speech_to_text
   - อัพเดท status messages

4. **`test_speech_translation_fix.py`** (ใหม่)
   - สคริปต์ทดสอบการแก้ไข
   - ตรวจสอบ TTS speed และ Whisper language

## 🎯 การใช้งานจริง

### สำหรับผู้ใช้:
1. เริ่มระบบตามปกติ
2. ระบุภาษาต้นฉบับให้ถูกต้อง (หากจำเป็น)
3. เสียงพากย์จะช้าลงและถูกต้องขึ้น

### สำหรับนักพัฒนา:
1. ตรวจสอบ logs สำหรับ language detection
2. ปรับแต่ง TTS speed หากจำเป็น
3. เพิ่มภาษาใหม่ได้ง่าย

## 🔍 Troubleshooting

### ปัญหา: เสียงยังเร็วเกินไป
```python
# ลดค่า rate ใน tts_server.py
<prosody rate="0.7" pitch="0%" volume="100%">
```

### ปัญหา: Whisper ยังถอดผิดภาษา
```python
# ตรวจสอบ logs ใน audio_service.py
logger.info(f"Requested: {source_language}, Detected: {detected_language}")
```

### ปัญหา: การแปลไม่ถูกต้อง
```bash
# ทดสอบ LibreTranslate
curl http://localhost:5000/translate \
  -H "Content-Type: application/json" \
  -d '{"q":"test","source":"en","target":"th"}'
```

---

## ✅ สรุปการแก้ไข

การแก้ไขนี้จะทำให้:
- 🎵 **TTS พูดช้าลงและเป็นธรรมชาติมากขึ้น**
- 🎯 **Whisper ถอดเสียงเป็นภาษาต้นฉบับก่อนแปล**
- 📈 **คุณภาพการแปลดีขึ้น**
- 🔧 **ควบคุมและติดตามได้ดีขึ้น**

**การแก้ไขนี้เป็น backward compatible** ไม่กระทบต่อระบบเดิม
