#!/usr/bin/env python3
# test_real_translation.py - ทดสอบการแปลวิดีโอจริง

import asyncio
import requests
import time
import json
import sys
import os

# เพิ่ม path ของ backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_api_connection():
    """ทดสอบการเชื่อมต่อ API"""
    print("🔍 ทดสอบการเชื่อมต่อ API...")
    
    try:
        # ทดสอบ Backend
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend API: ทำงานปกติ")
            health_data = response.json()
            print(f"   Services: {health_data.get('services', {})}")
        else:
            print(f"❌ Backend API: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend API: ไม่สามารถเชื่อมต่อได้ - {e}")
        return False
    
    try:
        # ทดสอบ LibreTranslate
        response = requests.get("http://localhost:5000/languages", timeout=15)
        if response.status_code == 200:
            print("✅ LibreTranslate: ทำงานปกติ")
            languages = response.json()
            print(f"   ภาษาที่รองรับ: {len(languages)} ภาษา")
        else:
            print(f"❌ LibreTranslate: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ LibreTranslate: ไม่สามารถเชื่อมต่อได้ - {e}")
    
    return True

def test_direct_translation():
    """ทดสอบการแปลข้อความโดยตรง"""
    print("\n🔤 ทดสอบการแปลข้อความ...")
    
    try:
        # ทดสอบแปลประโยค
        test_text = "Hello, how are you today?"
        
        payload = {
            "q": test_text,
            "source": "en",
            "target": "th"
        }
        
        response = requests.post(
            "http://localhost:5000/translate",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            translated_text = result.get("translatedText", "")
            print(f"✅ การแปล: '{test_text}' → '{translated_text}'")
            return True
        else:
            print(f"❌ การแปลล้มเหลว: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ การแปลล้มเหลว: {e}")
        return False

def test_video_processing_pipeline():
    """ทดสอบการประมวลผลวิดีโอ"""
    print("\n🎬 ทดสอบการประมวลผลวิดีโอ...")
    
    # ใช้วิดีโอสั้นๆ สำหรับทดสอบ
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll (3:32)
        "https://youtu.be/jNQXAC9IVRw",  # Me at the zoo (19 วินาที)
    ]
    
    for youtube_url in test_urls:
        print(f"\n📹 ทดสอบ URL: {youtube_url}")
        
        try:
            # เริ่มกระบวนการแปล
            payload = {
                "youtube_url": youtube_url,
                "target_language": "th"
            }
            
            print("   📤 เริ่มกระบวนการแปล...")
            response = requests.post(
                "http://localhost:8000/process-video/",
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"   ❌ ไม่สามารถเริ่มกระบวนการได้: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                continue
            
            result = response.json()
            task_id = result.get("task_id")
            
            if not task_id:
                print("   ❌ ไม่ได้รับ task_id")
                continue
            
            print(f"   📋 Task ID: {task_id}")
            
            # ติดตามความคืบหน้า
            max_wait_time = 600  # รอสูงสุด 10 นาที
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                try:
                    status_response = requests.get(f"http://localhost:8000/status/{task_id}", timeout=10)
                    
                    if status_response.status_code != 200:
                        print(f"   ❌ ไม่สามารถตรวจสอบสถานะได้: HTTP {status_response.status_code}")
                        break
                    
                    status_data = status_response.json()
                    status = status_data.get("status", "unknown")
                    progress = status_data.get("progress", 0)
                    message = status_data.get("message", "")
                    
                    print(f"   📊 สถานะ: {status} ({progress}%) - {message}")
                    
                    if status == "completed":
                        print("   ✅ การประมวลผลเสร็จสิ้น!")
                        
                        # ทดสอบการดาวน์โหลด
                        print("   📥 ทดสอบการดาวน์โหลด...")
                        download_response = requests.head(f"http://localhost:8000/download/{task_id}")
                        
                        if download_response.status_code == 200:
                            file_size = download_response.headers.get("Content-Length", "Unknown")
                            print(f"   ✅ ไฟล์พร้อมดาวน์โหลด (ขนาด: {file_size} bytes)")
                        else:
                            print(f"   ⚠️ ไฟล์ยังไม่พร้อม: HTTP {download_response.status_code}")
                        
                        return True
                        
                    elif status == "failed":
                        error = status_data.get("error", "Unknown error")
                        print(f"   ❌ การประมวลผลล้มเหลว: {error}")
                        break
                        
                    elif status == "processing":
                        # แสดงข้อมูลขั้นตอน
                        steps = status_data.get("steps", {})
                        for step_name, step_data in steps.items():
                            step_status = step_data.get("status", "pending")
                            step_progress = step_data.get("progress", 0)
                            if step_status != "pending":
                                print(f"      - {step_name}: {step_status} ({step_progress}%)")
                    
                    time.sleep(5)  # รอ 5 วินาที
                    
                except Exception as e:
                    print(f"   ❌ ข้อผิดพลาดในการตรวจสอบสถานะ: {e}")
                    time.sleep(5)
            
            print(f"   ⏰ หมดเวลารอ ({max_wait_time} วินาที)")
            
        except Exception as e:
            print(f"   ❌ ข้อผิดพลาด: {e}")
        
        # ทดสอบเพียง URL เดียว
        break
    
    return False

def test_file_upload():
    """ทดสอบการอัพโหลดไฟล์"""
    print("\n📁 ทดสอบการอัพโหลดไฟล์...")
    
    # สร้างไฟล์วิดีโอจำลอง (ในความเป็นจริงควรเป็นไฟล์วิดีโอจริง)
    test_file_path = "test_video.mp4"
    
    try:
        # สร้างไฟล์จำลอง
        with open(test_file_path, 'wb') as f:
            # เขียนข้อมูลจำลอง
            f.write(b'FAKE VIDEO DATA FOR TESTING' * 100)
        
        print(f"   📄 สร้างไฟล์ทดสอบ: {test_file_path}")
        
        # ทดสอบอัพโหลด
        with open(test_file_path, 'rb') as f:
            files = {'video': ('test_video.mp4', f, 'video/mp4')}
            response = requests.post("http://localhost:8000/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            file_id = result.get("file_id")
            print(f"   ✅ อัพโหลดสำเร็จ - File ID: {file_id}")
            return True
        else:
            print(f"   ❌ อัพโหลดล้มเหลว: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ ข้อผิดพลาดในการอัพโหลด: {e}")
        return False
    finally:
        # ลบไฟล์ทดสอบ
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def main():
    """ฟังก์ชันหลัก"""
    print("🚀 เริ่มทดสอบระบบ YouTube Video Translator")
    print("=" * 60)
    
    # ทดสอบการเชื่อมต่อ API
    if not test_api_connection():
        print("\n❌ การเชื่อมต่อ API ล้มเหลว - กรุณาตรวจสอบว่าระบบทำงานหรือไม่")
        return
    
    # ทดสอบการแปลข้อความ
    if not test_direct_translation():
        print("\n⚠️ การแปลข้อความไม่ทำงาน - แต่จะทดสอบต่อ")
    
    # ทดสอบการอัพโหลดไฟล์
    test_file_upload()
    
    # ทดสอบการประมวลผลวิดีโอ
    print("\n🎯 เริ่มทดสอบการประมวลผลวิดีโอ...")
    print("   หมายเหตุ: การทดสอบนี้อาจใช้เวลานาน")
    
    test_video_processing_pipeline()
    
    print("\n" + "=" * 60)
    print("🏁 ทดสอบเสร็จสิ้น")

if __name__ == "__main__":
    main()
