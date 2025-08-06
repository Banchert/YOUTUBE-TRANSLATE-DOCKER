# 🌐 การตั้งค่าภาษาต้นทาง และ ปลายทาง ในระบบ YouTube Video Translator

## 📊 ภาพรวมการตั้งค่าภาษา

### 🔸 **ภาษาต้นทาง (Source Language)**
- 🎯 **หน้าที่**: กำหนดให้ **Whisper ถอดเสียงจาก Video** ด้วยภาษาที่ระบุ
- 🛠️ **โมเดล**: Whisper AI (OpenAI)
- 📍 **ตั้งค่าที่**: `backend/app/services/audio_service.py`
- ⚙️ **Default**: `"en"` (อังกฤษ)
- 💡 **ตัวอย่าง**: Video ภาษาอังกฤษ → ตั้งค่า source="en" → Whisper ถอดเป็นข้อความอังกฤษ

### 🔹 **ภาษาปลายทาง (Target Language)**  
- 🎯 **หน้าที่**: ภาษาที่จะแปลไป และให้ **TTS อ่านออกเสียง**
- 🛠️ **โมเดล**: LibreTranslate (แปลภาษา) + Edge TTS (อ่านออกเสียง)
- 📍 **ตั้งค่าที่**: `backend/app/main.py`, `processing/tts/tts_server.py`
- ⚙️ **Default**: `"th"` (ไทย)
- 💡 **ตัวอย่าง**: ข้อความอังกฤษ → LibreTranslate แปลเป็นไทย → TTS อ่านเสียงไทย

---

## 🔧 1. การตั้งค่าภาษาต้นทาง (Source Language) - สำหรับ Whisper ถอดเสียงจาก Video

### 📁 **ไฟล์หลัก**: `backend/app/services/audio_service.py`

```python
async def speech_to_text(self, audio_path: str, task_id: str, source_language: str = "en") -> str:
    # บังคับให้ Whisper ถอดเสียงตามภาษาที่กำหนด
    data = {
        'language': source_language,  # บังคับภาษาที่ต้องการให้ Whisper ถอด
        'task': 'transcribe'  # ถอดเสียงเป็นข้อความ (ไม่ใช่แปลภาษา)
    }
```

### 🎯 **ความหมาย**: 
- กำหนดให้ Whisper รู้ว่าเสียงใน Video เป็นภาษาอะไร
- ป้องกันไม่ให้ Whisper เดาภาษาผิด (Auto-detect ผิด)
- ตัวอย่าง: Video อังกฤษ → ตั้ง `source_language="en"` → Whisper จะถอดเป็นข้อความอังกฤษ

### � **Whisper รองรับภาษาสำหรับถอดเสียง**:
- `"en"` - English (อังกฤษ)
- `"th"` - Thai (ไทย) 
- `"ja"` - Japanese (ญี่ปุ่น)
- `"ko"` - Korean (เกาหลี)
- `"zh"` - Chinese (จีน)
- `"es"` - Spanish (สเปน)
- `"fr"` - French (ฝรั่งเศส)
- `"de"` - German (เยอรมัน)
- และอีกมากกว่า 90 ภาษา

### ⚙️ **การตั้งค่าใน API**:
```python
# ใน backend/app/main.py
source_language = tasks[task_id].get("source_language", "en")  # Default เป็นอังกฤษ
transcript = await audio_service.speech_to_text(audio_path, task_id, source_language)
```

---

## 🔧 2. การตั้งค่าภาษาปลายทาง (Target Language) - สำหรับแปลภาษาและ TTS อ่านออกเสียง

### 📁 **ไฟล์หลัก**: `processing/tts/tts_server.py`

```python
# Available voices สำหรับ TTS อ่านออกเสียง
EDGE_VOICES = {
    "th": "th-TH-PremwadeeNeural",  # TTS อ่านเสียงไทย (หญิง)
    "en": "en-US-JennyNeural",      # TTS อ่านเสียงอังกฤษ (หญิง)
    "zh": "zh-CN-XiaoxiaoNeural",   # TTS อ่านเสียงจีน (หญิง)
    "ja": "ja-JP-NanamiNeural",     # TTS อ่านเสียงญี่ปุ่น (หญิง)
    "ko": "ko-KR-SunHiNeural",      # TTS อ่านเสียงเกาหลี (หญิง)
    "es": "es-ES-ElviraNeural",     # TTS อ่านเสียงสเปน (หญิง)
    "fr": "fr-FR-DeniseNeural",     # TTS อ่านเสียงฝรั่งเศส (หญิง)
    "de": "de-DE-KatjaNeural",      # TTS อ่านเสียงเยอรมัน (หญิง)
}
```

### 🎯 **ความหมาย**:
- กำหนดภาษาที่ต้องการให้แปลไป
- กำหนดเสียงที่ TTS จะใช้อ่านออกเสียง
- ตัวอย่าง: `target_language="th"` → แปลเป็นไทย + TTS อ่านด้วยเสียงไทย

### 📁 **การตั้งค่าใน Translation**: `processing/translation/translation_server.py`

```python
def postprocess_translation(text, target_language):
    """Post-process translated text for better quality"""
    if target_language == 'th':
        text = postprocess_thai_translation(text)
    elif target_language == 'zh':
        text = postprocess_chinese_translation(text)
    elif target_language == 'ja':
        text = postprocess_japanese_translation(text)
    elif target_language == 'ko':
        text = postprocess_korean_translation(text)
    elif target_language == 'ar':
        text = postprocess_arabic_translation(text)
    elif target_language == 'lo':
        text = postprocess_lao_translation(text)
```

---

## 🔄 3. Flow การทำงานของภาษา

### ✅ **ขั้นตอนการประมวลผล**:
```
1. 🎬 Video อังกฤษ (ตัวอย่าง)
   ↓
2. 🎵 Extract Audio จาก Video
   ↓  
3. 🎤 Whisper ถอดเสียง (source_language="en") → English Text
   ↓
4. 🌐 LibreTranslate แปลภาษา (en → th) → Thai Text  
   ↓
5. 🗣️ Edge TTS อ่านออกเสียง (th-TH-PremwadeeNeural) → Thai Audio
   ↓
6. 🎞️ Merge Thai Audio + Original Video = Final Video
```

### 📝 **ตัวอย่างการทำงานจริง**:
- **Input**: วิดีโอ YouTube ภาษาอังกฤษ
- **Source Language**: `"en"` → Whisper จะบังคับถอดเป็นภาษาอังกฤษ
- **Target Language**: `"th"` → แปลเป็นไทย และ TTS อ่านเสียงไทย
- **Output**: วิดีโอเดิมแต่มีเสียงพากย์ภาษาไทย
```python
# ใน backend/app/main.py - การใช้งานจริง
async def process_youtube_video_pipeline(
    task_id: str,
    youtube_url: str,
    target_language: str = "th"  # ภาษาที่จะแปลไป
):
    # ดึงภาษาต้นทางสำหรับ Whisper ถอดเสียง
    source_language = tasks[task_id].get("source_language", "en")  # ภาษาของ Video
    
    # ส่งไปให้ Whisper ถอดเสียงจาก Video
    transcript = await audio_service.speech_to_text(audio_path, task_id, source_language)
    
    # แปลข้อความไปยังภาษาปลายทาง
    translated_text = await translation_service.translate(transcript, target_language)
    
    # ให้ TTS อ่านออกเสียงด้วยภาษาปลายทาง
    thai_audio_path = await tts_service.text_to_speech(translated_text, task_id, target_language)
```

---

## 🛠️ 4. การเปลี่ยนแปลงการตั้งค่าภาษา

### 🎯 **เปลี่ยนภาษาต้นทาง**:

#### Frontend API Call:
```javascript
// ใน frontend/src/services/api.js
const response = await fetch(`${this.baseURL}/process_youtube`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    youtube_url: "https://youtube.com/watch?v=...",
    source_language: "ja",  // เปลี่ยนเป็นญี่ปุ่น
    target_language: "th"   // แปลเป็นไทย
  })
});
```

#### Backend Reception:
```python
# ใน backend/app/main.py
@app.post("/process_youtube")
async def process_youtube_video(request: YouTubeRequest):
    task_id = str(uuid.uuid4())
    
    # เก็บการตั้งค่าภาษา
    tasks[task_id] = {
        "id": task_id,
        "source_language": request.source_language,  # จากผู้ใช้
        "target_language": request.target_language,
        # ...
    }
```

### 🗣️ **เปลี่ยนภาษาปลายทาง**:

#### เพิ่มเสียงใหม่ใน TTS:
```python
# ใน processing/tts/tts_server.py
EDGE_VOICES = {
    "th": "th-TH-PremwadeeNeural",
    "en": "en-US-JennyNeural", 
    "vi": "vi-VN-HoaiMyNeural",  # เพิ่มเวียดนาม
    "my": "my-MM-NilarNeural",   # เพิ่มพม่า
    "km": "km-KH-PisachNeural",  # เพิ่มเขมร
}
```

---

## 📋 5. ภาษาที่รองรับปัจจุบัน

### 🎤 **Whisper (ภาษาต้นทาง)** - 99+ ภาษา:
- ✅ **หลัก**: EN, TH, JA, KO, ZH, ES, FR, DE, IT, PT, RU
- ✅ **เอเชีย**: VI, MY, KM, LO, ID, MS, TL
- ✅ **ยุโรป**: NL, SV, NO, DA, FI, PL, CS, SK
- ✅ **อื่นๆ**: AR, HE, HI, UR, FA, TR

### 🗣️ **Edge TTS (ภาษาปลายทาง)** - 8 ภาษา:
- ✅ `th` - ไทย (th-TH-PremwadeeNeural)
- ✅ `en` - อังกฤษ (en-US-JennyNeural)
- ✅ `zh` - จีน (zh-CN-XiaoxiaoNeural)
- ✅ `ja` - ญี่ปุ่น (ja-JP-NanamiNeural)
- ✅ `ko` - เกาหลี (ko-KR-SunHiNeural)
- ✅ `es` - สเปน (es-ES-ElviraNeural)
- ✅ `fr` - ฝรั่งเศส (fr-FR-DeniseNeural)
- ✅ `de` - เยอรมัน (de-DE-KatjaNeural)

### 🌐 **LibreTranslate (แปลภาษา)** - 30+ ภาษา:
- ✅ **ครอบคลุม**: EN, TH, JA, KO, ZH, ES, FR, DE, IT, PT, RU, AR, HI
- ✅ **อัตโนมัติ**: ตรวจจับภาษาต้นทางและแปลไปยังภาษาเป้าหมาย

---

## 🔧 6. การ Debug และ Troubleshooting

### 🔍 **ตรวจสอบภาษาที่ตรวจพบ**:
```python
# ใน backend/app/services/audio_service.py
detected_language = result.get('language', source_language)
logger.info(f"Requested: {source_language}, Detected: {detected_language}")

if detected_language != source_language:
    logger.warning(f"Language mismatch! Requested: {source_language}, Detected: {detected_language}")
```

### 🧪 **ทดสอบภาษาเฉพาะ**:
```python
# ทดสอบญี่ปุ่น → ไทย
python test_specific_language.py --source="ja" --target="th" --url="https://youtube.com/..."
```

### 📊 **ตรวจสอบความสามารถของโมเดล**:
```bash
# ตรวจสอบ Whisper
curl http://localhost:5001/health

# ตรวจสอบ TTS
curl http://localhost:5002/health

# ตรวจสอบ LibreTranslate
curl http://localhost:5000/languages
```

---

## 💡 7. แนวทางการปรับปรุง

### 🎯 **เพิ่มภาษาใหม่**:
1. **เพิ่มใน Whisper**: รองรับอัตโนมัติ (90+ ภาษา)
2. **เพิ่มใน LibreTranslate**: ตรวจสอบ API languages
3. **เพิ่มใน TTS**: เพิ่มเสียงใน `EDGE_VOICES`
4. **เพิ่ม Post-processing**: เพิ่มใน `translation_server.py`

### 🔧 **ปรับแต่งคุณภาพ**:
```python
# ปรับแต่งการทำงานของ Whisper
whisper_options = {
    "language": source_language,
    "task": "transcribe",
    "temperature": 0.0,  # ลดความสุ่ม
    "best_of": 5,        # เลือกผลลัพธ์ที่ดีที่สุดจาก 5 ครั้ง
    "beam_size": 5       # ใช้ beam search
}
```

### 🚀 **การใช้งานขั้นสูง**:
```python
# Auto-detect ภาษาต้นทาง แล้วเลือก TTS ที่เหมาะสม
auto_detected = await whisper_service.detect_language(audio_path)
if auto_detected in EDGE_VOICES:
    voice = EDGE_VOICES[auto_detected]
else:
    voice = "en-US-JennyNeural"  # fallback
```

---

## 📝 สรุป

**การตั้งค่าภาษาในระบบนี้แบ่งเป็น 3 ส่วนหลัก:**

1. 🎤 **Whisper** (ภาษาต้นทาง) - ถอดเสียงเป็นข้อความ
2. 🌐 **LibreTranslate** (แปลภาษา) - แปลจากต้นทางไปปลายทาง  
3. 🗣️ **Edge TTS** (ภาษาปลายทาง) - อ่านข้อความออกเสียง

**การตั้งค่าปัจจุบัน:**
- 🔸 **Default Source**: `"en"` (อังกฤษ)
- 🔹 **Default Target**: `"th"` (ไทย)
- ✅ **แก้ไขแล้ว**: บังคับภาษาต้นทางเพื่อไม่ให้ Whisper auto-detect ผิด
- ⚡ **ปรับปรุงแล้ว**: TTS ความเร็วช้าลง (rate=0.85)

**สามารถปรับเปลี่ยนได้ผ่าน API request หรือการแก้ไขไฟล์ configuration โดยตรง** 🛠️
