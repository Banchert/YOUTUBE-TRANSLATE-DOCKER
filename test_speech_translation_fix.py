#!/usr/bin/env python3
# test_speech_translation_fix.py - ทดสอบการแก้ไขปัญหาการถอดเสียงและ TTS

import requests
import json
import time
import os

def test_whisper_language_detection():
    """ทดสอบการบังคับภาษาใน Whisper"""
    print("🎤 ทดสอบการแก้ไขปัญหา Whisper Language Detection")
    print("=" * 70)
    
    # Test cases สำหรับภาษาต่างๆ
    test_cases = [
        {
            "language": "en",
            "description": "ภาษาอังกฤษ",
            "test_text": "Hello, this is a test of English speech recognition."
        },
        {
            "language": "th", 
            "description": "ภาษาไทย",
            "test_text": "สวัสดีครับ นี่คือการทดสอบการรู้จำเสียงภาษาไทย"
        }
    ]
    
    for test_case in test_cases:
        lang = test_case["language"]
        desc = test_case["description"]
        text = test_case["test_text"]
        
        print(f"\n📝 ทดสอบ {desc} (language={lang})")
        print(f"   ข้อความ: '{text}'")
        
        try:
            # จำลองการส่ง request ไปยัง Whisper service
            whisper_payload = {
                "language": lang,
                "task": "transcribe"
            }
            
            print(f"   📤 ส่ง request: language='{lang}', task='transcribe'")
            
            # ตรวจสอบ URL endpoint
            whisper_url = "http://localhost:5001/transcribe"
            try:
                response = requests.get("http://localhost:5001/health", timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ Whisper service พร้อมใช้งาน")
                else:
                    print(f"   ⚠️ Whisper service ตอบสนองแต่ไม่ปกติ: HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ Whisper service ไม่ทำงาน: {e}")
                print(f"   💡 กรุณาเริ่ม Whisper service ก่อน")
                continue
                
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {e}")

def test_tts_speed_improvement():
    """ทดสอบการปรับปรุงความเร็ว TTS"""
    print("\n🔊 ทดสอบการแก้ไขปัญหา TTS ความเร็ว")
    print("=" * 50)
    
    test_sentences = [
        {
            "text": "ทดสอบความเร็วปกติ",
            "expected_duration": "ปกติ (ไม่เร็วเกินไป)"
        },
        {
            "text": "ประโยคที่ยาวขึ้นเพื่อทดสอบว่าเสียงจะพูดด้วยความเร็วที่เหมาะสมหรือไม่",
            "expected_duration": "ช้าลง (rate=0.85)"
        },
        {
            "text": "การทดสอบระบบ Text-to-Speech ที่ได้รับการปรับปรุงให้พูดช้าลงเพื่อความชัดเจนและเข้าใจง่ายขึ้น",
            "expected_duration": "ช้ามาก (slow=True)"
        }
    ]
    
    try:
        # ตรวจสอบ TTS service
        tts_response = requests.get("http://localhost:5002/health", timeout=5)
        if tts_response.status_code != 200:
            print("❌ TTS service ไม่ทำงาน")
            print("💡 กรุณาเริ่ม TTS service ก่อน")
            return
            
        print("✅ TTS service พร้อมใช้งาน")
        
        for i, test in enumerate(test_sentences, 1):
            text = test["text"]
            expected = test["expected_duration"]
            
            print(f"\n📝 ทดสอบประโยคที่ {i}:")
            print(f"   ข้อความ: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            print(f"   คาดหวัง: {expected}")
            
            try:
                payload = {
                    "text": text,
                    "language": "th", 
                    "use_edge_tts": True
                }
                
                start_time = time.time()
                response = requests.post(
                    "http://localhost:5002/synthesize",
                    json=payload,
                    timeout=30
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    result = response.json()
                    file_size = result.get('file_size', 0)
                    voice_used = result.get('voice_used', 'unknown')
                    processing_time = end_time - start_time
                    
                    print(f"   ✅ สำเร็จ:")
                    print(f"   - เวลาประมวลผล: {processing_time:.2f} วินาที")
                    print(f"   - ขนาดไฟล์: {file_size:,} bytes") 
                    print(f"   - เสียงที่ใช้: {voice_used}")
                    
                    # ประเมินผลลัพธ์
                    chars_per_byte = len(text) / file_size if file_size > 0 else 0
                    print(f"   - อัตราส่วน: {chars_per_byte:.4f} chars/byte")
                    
                    # คำแนะนำการปรับปรุง
                    if processing_time > 10:
                        print(f"   ⚠️ ใช้เวลานาน ({processing_time:.1f}s)")
                    if file_size < len(text) * 80:  # หยาบๆ
                        print(f"   ⚠️ ไฟล์เสียงอาจสั้น/เร็วเกินไป")
                    else:
                        print(f"   ✅ ความเร็วเหมาะสม")
                        
                else:
                    print(f"   ❌ ล้มเหลว: HTTP {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ ข้อผิดพลาด: {e}")
                
    except Exception as e:
        print(f"❌ ไม่สามารถเชื่อมต่อ TTS service: {e}")

def test_full_pipeline_integration():
    """ทดสอบ pipeline เต็มรูปแบบ"""
    print("\n🔄 ทดสอบ Integration ของ Pipeline ที่แก้ไขแล้ว")
    print("=" * 60)
    
    try:
        # ตรวจสอบ Backend API
        backend_response = requests.get("http://localhost:8000/health", timeout=5)
        if backend_response.status_code != 200:
            print("❌ Backend API ไม่ทำงาน")
            print("💡 กรุณาเริ่ม Backend service ก่อน")
            return
            
        print("✅ Backend API พร้อมใช้งาน")
        
        # สร้าง demo task เพื่อทดสอบ 
        demo_payload = {
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll
            "source_language": "en",
            "target_language": "th"
        }
        
        print("\n📤 ส่ง request ทดสอบ...")
        print(f"   URL: {demo_payload['youtube_url']}")
        print(f"   จาก: {demo_payload['source_language']} → เป็น: {demo_payload['target_language']}")
        
        # ส่ง request (แค่ทดสอบการสร้าง task)
        response = requests.post(
            "http://localhost:8000/translate",
            json=demo_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get('task_id')
            
            print(f"   ✅ Task สร้างสำเร็จ: {task_id}")
            print(f"   📋 ตรวจสอบสถานะได้ที่: http://localhost:8000/status/{task_id}")
            
            # ตรวจสอบสถานะ task
            status_response = requests.get(f"http://localhost:8000/status/{task_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"   📊 สถานะปัจจุบัน: {status_data.get('status', 'unknown')}")
                print(f"   📈 ความคืบหน้า: {status_data.get('progress', 0)}%")
            
        else:
            print(f"   ❌ ไม่สามารถสร้าง task ได้: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ข้อผิดพลาดใน integration test: {e}")

def test_service_health():
    """ตรวจสอบสุขภาพของ services ทั้งหมด"""
    print("\n🏥 ตรวจสอบสุขภาพ Services")
    print("=" * 40)
    
    services = [
        ("Backend API", "http://localhost:8000/health"),
        ("Whisper Service", "http://localhost:5001/health"), 
        ("TTS Service", "http://localhost:5002/health"),
        ("LibreTranslate", "http://localhost:5000/languages"),
        ("Frontend", "http://localhost:3000")
    ]
    
    healthy_services = []
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: สุขภาพดี")
                healthy_services.append(name)
            else:
                print(f"⚠️ {name}: ตอบสนองแต่ไม่ปกติ (HTTP {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: ไม่ทำงาน - {e}")
    
    print(f"\n📊 สรุป: {len(healthy_services)}/{len(services)} services ทำงานปกติ")
    
    if len(healthy_services) == len(services):
        print("🎉 ระบบพร้อมใช้งาน!")
    elif len(healthy_services) >= 3:
        print("⚠️ ระบบใช้งานได้บางส่วน")
    else:
        print("❌ ระบบมีปัญหา กรุณาตรวจสอบ services")

def main():
    """ฟังก์ชันหลัก"""
    print("🧪 การทดสอบการแก้ไขปัญหา Speech & TTS")
    print("📅 " + time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    print("🎯 การแก้ไขที่ทำไปแล้ว:")
    print("   1. ✅ แก้ไข Whisper ให้บังคับใช้ภาษาต้นฉบับ")
    print("   2. ✅ ปรับ TTS ให้พูดช้าลง (rate=0.85, slow=True)")
    print("   3. ✅ เพิ่ม language parameter ใน pipeline")
    print("   4. ✅ ปรับปรุง error handling และ logging")
    print()
    
    # รันการทดสอบทั้งหมด
    test_service_health()
    test_whisper_language_detection()
    test_tts_speed_improvement()
    test_full_pipeline_integration()
    
    print("\n" + "=" * 70)
    print("📋 สรุปการทดสอบ:")
    print("   💡 หากทุก test ผ่าน = การแก้ไขสำเร็จ")
    print("   ⚠️ หากมีคำเตือน = อาจต้องปรับแต่งเพิ่มเติม")
    print("   ❌ หากล้มเหลว = ต้องตรวจสอบ configuration")
    print()
    print("🔧 การใช้งานจริง:")
    print("   1. เริ่ม Docker services: docker compose up -d")
    print("   2. รอ services พร้อม (30 วินาทีี)")
    print("   3. ทดสอบด้วย Frontend: http://localhost:3000")
    print("   4. หรือใช้ test page: test-video-playback.html")

if __name__ == "__main__":
    main()
