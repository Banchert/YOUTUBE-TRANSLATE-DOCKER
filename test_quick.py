#!/usr/bin/env python3
# test_translation_now.py - ทดสอบระบบแปลอย่างรวดเร็ว

import requests
import time
import json

def test_libretranslate():
    """ทดสอบ LibreTranslate service"""
    print("🔍 ทดสอบ LibreTranslate...")
    
    try:
        # ทดสอบการเชื่อมต่อ
        print("   📡 ทดสอบการเชื่อมต่อ...")
        response = requests.get("http://localhost:5000/languages", timeout=10)
        
        if response.status_code == 200:
            languages = response.json()
            print(f"   ✅ เชื่อมต่อได้ - รองรับ {len(languages)} ภาษา")
            
            # แสดงภาษาที่รองรับ
            lang_codes = [lang['code'] for lang in languages]
            print(f"   📝 ภาษาที่รองรับ: {', '.join(lang_codes[:10])}...")
            
            # ทดสอบการแปล
            print("   🔤 ทดสอบการแปล...")
            translate_data = {
                "q": "Hello, how are you?",
                "source": "en", 
                "target": "th"
            }
            
            translate_response = requests.post(
                "http://localhost:5000/translate",
                json=translate_data,
                timeout=15
            )
            
            if translate_response.status_code == 200:
                result = translate_response.json()
                translated = result.get("translatedText", "")
                print(f"   ✅ การแปลสำเร็จ: 'Hello, how are you?' → '{translated}'")
                return True
            else:
                print(f"   ❌ การแปลล้มเหลว: HTTP {translate_response.status_code}")
                return False
                
        else:
            print(f"   ❌ ไม่สามารถเชื่อมต่อ: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectRefused:
        print("   ❌ LibreTranslate ไม่ได้เริ่มทำงาน")
        return False
    except requests.exceptions.Timeout:
        print("   ⏰ LibreTranslate ตอบสนองช้า (อาจกำลังโหลด models)")
        return False
    except Exception as e:
        print(f"   ❌ ข้อผิดพลาด: {e}")
        return False

def test_backend_api():
    """ทดสอบ Backend API"""
    print("\n🖥️ ทดสอบ Backend API...")
    
    try:
        # ทดสอบ health check
        response = requests.get("http://localhost:8000/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print("   ✅ Backend ทำงานปกติ")
            
            # แสดงสถานะ services
            services = health_data.get("services", {})
            for service, status in services.items():
                status_icon = "✅" if "available" in status else "❌"
                print(f"      {status_icon} {service}: {status}")
            
            return True
        else:
            print(f"   ❌ Backend มีปัญหา: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ ไม่สามารถเชื่อมต่อ Backend: {e}")
        return False

def test_frontend():
    """ทดสอบ Frontend"""
    print("\n🌐 ทดสอบ Frontend...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        
        if response.status_code == 200:
            print("   ✅ Frontend ทำงานปกติ")
            print("   🌐 เข้าใช้งานได้ที่: http://localhost:3000")
            return True
        else:
            print(f"   ❌ Frontend มีปัญหา: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ ไม่สามารถเชื่อมต่อ Frontend: {e}")
        return False

def test_quick_video_translation():
    """ทดสอบการแปลวิดีโอแบบรวดเร็ว"""
    print("\n🎬 ทดสอบการเริ่มต้นกระบวนการแปลวิดีโอ...")
    
    try:
        # ใช้วิดีโอสั้นมากสำหรับทดสอบ
        payload = {
            "youtube_url": "https://youtu.be/jNQXAC9IVRw",  # Me at the zoo - 19 วินาที
            "target_language": "th"
        }
        
        response = requests.post(
            "http://localhost:8000/process-video/",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"   ✅ เริ่มการแปลแล้ว - Task ID: {task_id}")
            
            # ตรวจสอบสถานะเบื้องต้น
            time.sleep(2)
            status_response = requests.get(f"http://localhost:8000/status/{task_id}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status", "unknown")
                message = status_data.get("message", "")
                print(f"   📊 สถานะปัจจุบัน: {status} - {message}")
                return True
            else:
                print("   ⚠️ ไม่สามารถตรวจสอบสถานะได้")
                return False
                
        else:
            print(f"   ❌ ไม่สามารถเริ่มการแปลได้: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ ข้อผิดพลาด: {e}")
        return False

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 ทดสอบระบบ YouTube Video Translator อย่างรวดเร็ว")
    print("=" * 60)
    
    # ทดสอบทุก services
    backend_ok = test_backend_api()
    frontend_ok = test_frontend()
    libretranslate_ok = test_libretranslate()
    
    print("\n" + "=" * 60)
    print("📊 สรุปผลการทดสอบ:")
    print(f"   Backend API:     {'✅ ปกติ' if backend_ok else '❌ มีปัญหา'}")
    print(f"   Frontend:        {'✅ ปกติ' if frontend_ok else '❌ มีปัญหา'}")
    print(f"   LibreTranslate:  {'✅ ปกติ' if libretranslate_ok else '❌ มีปัญหา'}")
    
    if backend_ok and frontend_ok and libretranslate_ok:
        print("\n🎉 ระบบทำงานปกติทุกส่วน!")
        print("🌐 เข้าใช้งานได้ที่: http://localhost:3000")
        
        # ทดสอบการแปลวิดีโอ
        test_quick_video_translation()
        
    elif backend_ok and frontend_ok:
        print("\n⚠️ ระบบหลักทำงาน แต่ LibreTranslate มีปัญหา")
        print("💡 แนะนำ: รัน Fix-LibreTranslate.bat เพื่อแก้ไข")
        
    else:
        print("\n❌ ระบบมีปัญหา กรุณาตรวจสอบ:")
        if not backend_ok:
            print("   - Backend API ไม่ทำงาน")
        if not frontend_ok:
            print("   - Frontend ไม่ทำงาน")
        if not libretranslate_ok:
            print("   - LibreTranslate ไม่ทำงาน")
        
        print("\n💡 แนะนำ: รัน Fix-And-Start.bat อีกครั้ง")

if __name__ == "__main__":
    main()
