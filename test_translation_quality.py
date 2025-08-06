#!/usr/bin/env python3
# test_translation_quality.py - ทดสอบคุณภาพการแปลและ TTS

import requests
import json
import time

def test_translation_step_by_step():
    """ทดสอบแต่ละขั้นตอนของการแปล"""
    print("🔍 ทดสอบคุณภาพการแปลและ TTS แบบละเอียด")
    print("=" * 60)
    
    # ข้อความตัวอย่างจาก transcript
    test_text = "The Bear and the Bee. Everybody knows that bears love honey. One day Mr. Bear looks in his cupboard and he can't find any honey."
    
    print(f"📝 ข้อความต้นฉบับ (ภาษาอังกฤษ):")
    print(f"   '{test_text}'")
    print()
    
    # ทดสอบการแปล
    print("🔤 ขั้นตอนที่ 1: ทดสอบการแปลภาษา")
    try:
        translate_payload = {
            "q": test_text,
            "source": "en",
            "target": "th"
        }
        
        response = requests.post(
            "http://localhost:5000/translate",
            json=translate_payload,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            translated_text = result.get("translatedText", "")
            print(f"   ✅ การแปลสำเร็จ:")
            print(f"   '{translated_text}'")
            print()
            
            # ประเมินคุณภาพการแปล
            if len(translated_text) < len(test_text) * 0.3:
                print("   ⚠️ คำเตือน: ข้อความแปลสั้นผิดปกติ")
            elif "หมี" in translated_text and "น้ำผึ้ง" in translated_text:
                print("   ✅ การแปลดูเหมือนถูกต้อง (มีคำว่า หมี และ น้ำผึ้ง)")
            else:
                print("   ⚠️ การแปลอาจไม่ถูกต้อง (ไม่พบคำสำคัญ)")
            
        else:
            print(f"   ❌ การแปลล้มเหลว: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ ข้อผิดพลาดในการแปล: {e}")
        return False
    
    # ทดสอบ TTS
    print("🔊 ขั้นตอนที่ 2: ทดสอบ Text-to-Speech")
    try:
        # ใช้ข้อความไทยสั้นๆ เพื่อทดสอบ
        test_thai_text = "สวัสดีครับ ยินดีที่ได้รู้จัก"
        
        tts_payload = {
            "text": test_thai_text,
            "language": "th",
            "use_edge_tts": True
        }
        
        response = requests.post(
            "http://localhost:5002/synthesize",
            json=tts_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            audio_file = result.get("audio_file")
            file_size = result.get("file_size", 0)
            voice_used = result.get("voice_used", "unknown")
            
            print(f"   ✅ TTS สำเร็จ:")
            print(f"   - ไฟล์: {audio_file}")
            print(f"   - ขนาด: {file_size} bytes")
            print(f"   - เสียง: {voice_used}")
            
            # ประเมินไฟล์เสียง
            if file_size < 1000:
                print("   ⚠️ คำเตือน: ไฟล์เสียงเล็กผิดปกติ")
            else:
                print("   ✅ ขนาดไฟล์เสียงปกติ")
            
        else:
            print(f"   ❌ TTS ล้มเหลว: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ ข้อผิดพลาดใน TTS: {e}")
        return False
    
    # ทดสอบ TTS กับข้อความที่แปลแล้ว
    print("🎯 ขั้นตอนที่ 3: ทดสอบ TTS กับข้อความที่แปลแล้ว")
    try:
        tts_translated_payload = {
            "text": translated_text[:100],  # ใช้แค่ 100 ตัวอักษรแรก
            "language": "th",
            "use_edge_tts": True
        }
        
        response = requests.post(
            "http://localhost:5002/synthesize",
            json=tts_translated_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ TTS ข้อความแปลสำเร็จ")
            print(f"   - ไฟล์: {result.get('audio_file')}")
            
            # ทดสอบดาวน์โหลด
            audio_file = result.get('audio_file')
            download_response = requests.get(f"http://localhost:5002/download/{audio_file}")
            
            if download_response.status_code == 200:
                print(f"   ✅ ดาวน์โหลดไฟล์เสียงได้")
                print(f"   - ขนาดที่ดาวน์โหลด: {len(download_response.content)} bytes")
            else:
                print(f"   ⚠️ ไม่สามารถดาวน์โหลดไฟล์เสียง: HTTP {download_response.status_code}")
            
        else:
            print(f"   ❌ TTS ข้อความแปลล้มเหลว: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ ข้อผิดพลาดใน TTS ข้อความแปล: {e}")
    
    print("\n" + "=" * 60)
    print("📊 สรุปการทดสอบ:")
    print("   ✅ หากทุกขั้นตอนผ่าน = ระบบทำงานถูกต้อง")
    print("   ⚠️ หากมีคำเตือน = อาจต้องปรับการตั้งค่า")
    print("   ❌ หากล้มเหลว = ต้องแก้ไขปัญหา")
    
    return True

def test_tts_speed_settings():
    """ทดสอบการตั้งค่าความเร็วของ TTS"""
    print("\n🎛️ ทดสอบการตั้งค่าความเร็ว TTS")
    print("=" * 40)
    
    test_sentences = [
        "ประโยคสั้นๆ สำหรับทดสอบ",
        "ประโยคยาวหน่อยเพื่อดูว่าเสียงจะพูดเร็วหรือช้า และเข้าใจได้หรือไม่",
        "การทดสอบความเร็วในการพูดของระบบปัญญาประดิษฐ์นี้เพื่อให้มั่นใจว่าผู้ฟังจะเข้าใจได้"
    ]
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"\n📝 ทดสอบประโยคที่ {i}:")
        print(f"   '{sentence[:50]}{'...' if len(sentence) > 50 else ''}'")
        
        try:
            payload = {
                "text": sentence,
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
                processing_time = end_time - start_time
                file_size = result.get('file_size', 0)
                
                # คำนวณอัตราส่วนเวลา
                text_length = len(sentence)
                ratio = file_size / text_length if text_length > 0 else 0
                
                print(f"   ✅ สำเร็จ:")
                print(f"   - เวลาประมวลผล: {processing_time:.2f} วินาที")
                print(f"   - ขนาดไฟล์: {file_size} bytes")
                print(f"   - อัตราส่วน: {ratio:.2f} bytes/char")
                
                if processing_time > 10:
                    print(f"   ⚠️ ใช้เวลานาน (>{processing_time:.1f}s)")
                if file_size < text_length * 100:  # หยาบๆ
                    print(f"   ⚠️ ไฟล์เสียงอาจสั้น/เร็วเกินไป")
                
            else:
                print(f"   ❌ ล้มเหลว: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {e}")

def main():
    """ฟังก์ชันหลัก"""
    print("🧪 การทดสอบคุณภาพการแปลและ TTS")
    print("📅 " + time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # ทดสอบการเชื่อมต่อพื้นฐาน
    services = [
        ("LibreTranslate", "http://localhost:5000/languages"),
        ("TTS Service", "http://localhost:5002/health"),
        ("Backend API", "http://localhost:8000/health")
    ]
    
    all_services_ok = True
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: ทำงานปกติ")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                all_services_ok = False
        except Exception as e:
            print(f"❌ {name}: ไม่สามารถเชื่อมต่อ - {e}")
            all_services_ok = False
    
    if not all_services_ok:
        print("\n⚠️ บางบริการไม่ทำงาน - การทดสอบอาจไม่สมบูรณ์")
    
    print("\n" + "=" * 60)
    
    # เริ่มการทดสอบหลัก
    test_translation_step_by_step()
    test_tts_speed_settings()
    
    print("\n🎯 คำแนะนำการแก้ไข:")
    print("   1. หากการแปลผิด: ตรวจสอบ LibreTranslate settings")
    print("   2. หากเสียงเร็วเกินไป: ปรับ TTS speed/rate settings")
    print("   3. หากเสียงแปลก: ตรวจสอบ language detection")
    print("   4. หากไฟล์เสียงเล็ก: ตรวจสอบ audio encoding")

if __name__ == "__main__":
    main()
