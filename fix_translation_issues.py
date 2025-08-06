#!/usr/bin/env python3
# fix_translation_issues.py - แก้ไขปัญหาการแปลและ TTS

import requests
import json
import time
import re

def analyze_transcript_quality():
    """วิเคราะห์คุณภาพของ transcript ที่ได้"""
    print("🔍 วิเคราะห์คุณภาพ Transcript")
    print("=" * 40)
    
    transcript_file = "uploads/transcript_790afb81-cc69-4f15-b764-933aa30bcf63.json"
    
    try:
        with open(transcript_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        text = data.get('text', '')
        language = data.get('language', 'unknown')
        segments = data.get('segments', [])
        
        print(f"📄 ไฟล์ Transcript: {transcript_file}")
        print(f"🌐 ภาษาที่ตรวจพบ: {language}")
        print(f"📝 ความยาวข้อความ: {len(text)} ตัวอักษร")
        print(f"⏱️ จำนวนส่วน: {len(segments)} segments")
        print()
        
        # แสดงตัวอย่างข้อความ
        print("📋 ตัวอย่างข้อความ (300 ตัวอักษรแรก):")
        print(f"   '{text[:300]}{'...' if len(text) > 300 else ''}'")
        print()
        
        # วิเคราะห์คุณภาพ
        issues = []
        
        if language != 'en':
            issues.append(f"ภาษาไม่ใช่อังกฤษ (ตรวจพบ: {language})")
        
        if len(text.strip()) < 50:
            issues.append("ข้อความสั้นเกินไป")
        
        # ตรวจสอบคำสำคัญที่ควรมี
        expected_words = ['bear', 'bee', 'honey', 'forest']
        found_words = [word for word in expected_words if word.lower() in text.lower()]
        missing_words = [word for word in expected_words if word not in found_words]
        
        if missing_words:
            issues.append(f"ไม่พบคำสำคัญ: {', '.join(missing_words)}")
        
        if issues:
            print("⚠️ ปัญหาที่พบ:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ Transcript มีคุณภาพดี")
        
        return text, language
        
    except Exception as e:
        print(f"❌ ไม่สามารถอ่าน transcript: {e}")
        return None, None

def test_translation_quality(text, source_lang="en"):
    """ทดสอบคุณภาพการแปล"""
    print("\n🔤 ทดสอบคุณภาพการแปล")
    print("=" * 40)
    
    if not text:
        print("❌ ไม่มีข้อความสำหรับทดสอบ")
        return None
    
    # แบ่งข้อความเป็นชิ้นเล็กๆ สำหรับทดสอบ
    test_chunks = [
        text[:200],  # 200 ตัวอักษรแรก
        text[200:400] if len(text) > 200 else "",  # ชิ้นกลาง
        text[-200:] if len(text) > 200 else ""     # 200 ตัวอักษรท้าย
    ]
    
    translations = []
    
    for i, chunk in enumerate(test_chunks):
        if not chunk.strip():
            continue
        
        print(f"\n📝 ทดสอบชิ้นที่ {i+1}:")
        print(f"   ต้นฉบับ: '{chunk[:100]}{'...' if len(chunk) > 100 else ''}'")
        
        try:
            payload = {
                "q": chunk,
                "source": source_lang,
                "target": "th"
            }
            
            response = requests.post(
                "http://localhost:5000/translate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = result.get("translatedText", "")
                
                print(f"   แปล: '{translated[:100]}{'...' if len(translated) > 100 else ''}'")
                
                # ประเมินคุณภาพ
                quality_score = evaluate_translation_quality(chunk, translated)
                print(f"   คะแนนคุณภาพ: {quality_score}/10")
                
                translations.append(translated)
                
            else:
                print(f"   ❌ ล้มเหลว: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {e}")
    
    return translations

def evaluate_translation_quality(original, translated):
    """ประเมินคุณภาพการแปล"""
    score = 10
    
    # ตรวจสอบความยาวที่สมเหตุสมผล
    length_ratio = len(translated) / len(original) if len(original) > 0 else 0
    if length_ratio < 0.3 or length_ratio > 3.0:
        score -= 3
    
    # ตรวจสอบว่ามีข้อความไทย
    thai_chars = len(re.findall(r'[\u0E00-\u0E7F]', translated))
    if thai_chars < len(translated) * 0.5:  # อย่างน้อย 50% เป็นอักษรไทย
        score -= 2
    
    # ตรวจสอบคำสำคัญ
    key_mappings = {
        'bear': ['หมี'],
        'bee': ['ผึ้ง', 'ผิ้ง'],
        'honey': ['น้ำผึ้ง', 'ผึ้ง'],
        'forest': ['ป่า', 'ไผ่'],
        'tree': ['ต้นไม้', 'ไผ่']
    }
    
    for eng_word, thai_words in key_mappings.items():
        if eng_word.lower() in original.lower():
            if not any(thai_word in translated for thai_word in thai_words):
                score -= 1
    
    return max(0, score)

def test_improved_tts(text):
    """ทดสอบ TTS ที่ปรับปรุงแล้ว"""
    print("\n🔊 ทดสอบ TTS ที่ปรับปรุงแล้ว")
    print("=" * 40)
    
    if not text:
        print("❌ ไม่มีข้อความสำหรับทดสอบ TTS")
        return
    
    # ทดสอบกับข้อความไทยตัวอย่าง
    test_texts = [
        "สวัสดีครับ ยินดีที่ได้รู้จัก",
        text[:100] if text else "",  # ใช้ข้อความที่แปลแล้ว
        "การทดสอบความเร็วในการพูดของระบบ"
    ]
    
    for i, test_text in enumerate(test_texts):
        if not test_text.strip():
            continue
        
        print(f"\n🎯 ทดสอบ TTS ที่ {i+1}:")
        print(f"   ข้อความ: '{test_text[:50]}{'...' if len(test_text) > 50 else ''}'")
        
        try:
            payload = {
                "text": test_text,
                "language": "th",
                "use_edge_tts": True
            }
            
            start_time = time.time()
            response = requests.post(
                "http://localhost:5002/synthesize",
                json=payload,
                timeout=30
            )
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                audio_file = result.get('audio_file')
                file_size = result.get('file_size', 0)
                voice_used = result.get('voice_used', 'unknown')
                
                print(f"   ✅ สำเร็จ:")
                print(f"   - เวลา: {processing_time:.2f}s")
                print(f"   - ขนาด: {file_size} bytes")
                print(f"   - เสียง: {voice_used}")
                
                # ประเมิน
                bytes_per_char = file_size / len(test_text) if len(test_text) > 0 else 0
                print(f"   - อัตราส่วน: {bytes_per_char:.1f} bytes/char")
                
                if processing_time < 2:
                    print("   ⚡ ประมวลผลเร็ว")
                elif processing_time > 10:
                    print("   🐌 ประมวลผลช้า")
                
                if bytes_per_char > 1000:
                    print("   🎵 ไฟล์เสียงมีขนาดเหมาะสม")
                else:
                    print("   ⚠️ ไฟล์เสียงอาจเล็กเกินไป")
                
            else:
                print(f"   ❌ ล้มเหลว: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {e}")

def main():
    """ฟังก์ชันหลัก"""
    print("🔧 การวิเคราะห์และแก้ไขปัญหาการแปลและ TTS")
    print("📅 " + time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    # วิเคราะห์ transcript
    text, language = analyze_transcript_quality()
    
    if text:
        # ทดสอบการแปล
        translations = test_translation_quality(text, language)
        
        if translations:
            # ใช้การแปลที่ดีที่สุดสำหรับทดสอบ TTS
            best_translation = max(translations, key=len)  # ใช้การแปลที่ยาวที่สุด
            test_improved_tts(best_translation)
    
    print("\n" + "=" * 60)
    print("📊 สรุปการวิเคราะห์:")
    print("   1. ตรวจสอบคุณภาพ Speech-to-Text")
    print("   2. ทดสอบการแปลภาษา")
    print("   3. ประเมิน TTS ที่ปรับปรุงแล้ว")
    print()
    print("💡 คำแนะนำ:")
    print("   - หาก Transcript ผิด: ปรับ Whisper model")
    print("   - หากการแปลผิด: ปรับ LibreTranslate หรือใช้ service อื่น")
    print("   - หาก TTS เร็ว/ช้า: ปรับ rate ใน SSML")
    print("   - หากเสียงแปลก: ตรวจสอบ language detection")

if __name__ == "__main__":
    main()
