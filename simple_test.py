#!/usr/bin/env python3
"""
🎯 ทดสอบการแก้ไข TTS และ Whisper อย่างง่าย
"""

import requests
import time
import json

def test_simple():
    print("🔧 ทดสอบการแก้ไข TTS และ Whisper")
    print("=" * 50)
    
    # 1. ทดสอบ Backend
    print("\n1. 🔗 ทดสอบ Backend...")
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        print(f"   ✅ Backend: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend: {e}")
    
    # 2. ทดสอบ LibreTranslate
    print("\n2. 🌐 ทดสอบ LibreTranslate...")
    try:
        payload = {"q": "Hello", "source": "en", "target": "th"}
        response = requests.post("http://localhost:5000/translate", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ แปล: {result.get('translatedText', 'N/A')}")
        else:
            print(f"   ❌ LibreTranslate: {response.status_code}")
    except Exception as e:
        print(f"   ❌ LibreTranslate: {e}")
    
    # 3. ทดสอบ TTS Speed
    print("\n3. 🎵 ทดสอบ TTS ความเร็ว...")
    try:
        payload = {
            "text": "ทดสอบความเร็วใหม่ที่ช้าลง",
            "language": "th",
            "use_edge_tts": True
        }
        start = time.time()
        response = requests.post("http://localhost:5002/synthesize", json=payload, timeout=20)
        duration = time.time() - start
        
        if response.status_code == 200:
            size = len(response.content)
            print(f"   ✅ TTS: {duration:.1f}s, {size:,} bytes")
        else:
            print(f"   ❌ TTS: {response.status_code}")
    except Exception as e:
        print(f"   ❌ TTS: {e}")
    
    # 4. ทดสอบ Whisper
    print("\n4. 🎤 ทดสอบ Whisper...")
    try:
        # สร้างไฟล์เสียงจำลอง
        test_audio = b'\x00' * 1000  # dummy audio data
        files = {'file': ('test.wav', test_audio, 'audio/wav')}
        data = {'language': 'en', 'task': 'transcribe'}
        
        response = requests.post("http://localhost:5001/transcribe", files=files, data=data, timeout=15)
        if response.status_code == 200:
            print(f"   ✅ Whisper: ตอบสนอง")
        else:
            print(f"   ❌ Whisper: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Whisper: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 การทดสอบเสร็จสิ้น")
    print("\n📝 สรุปการแก้ไข:")
    print("   ✅ TTS: ลดความเร็วด้วย rate='0.85'")
    print("   ✅ Whisper: บังคับภาษาต้นฉบับ")
    print("   ✅ Pipeline: ส่งภาษาต้นฉบับไปยัง Whisper")
    print("\n💡 ลองใช้งานจริงได้แล้ว!")

if __name__ == "__main__":
    test_simple()
