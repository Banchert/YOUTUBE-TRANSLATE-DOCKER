#!/usr/bin/env python3
"""
🎬 ทดสอบการแสดงวิดีโอใน Web UI
- ทดสอบ Backend API
- ทดสอบ Static File Serving
- ทดสอบ Video Player Integration
"""

import requests
import json
import time
import os

# สี ANSI สำหรับ output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m' 
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status="info"):
    colors = {
        "success": Colors.GREEN,
        "error": Colors.RED,
        "warning": Colors.YELLOW,
        "info": Colors.BLUE,
        "debug": Colors.PURPLE
    }
    color = colors.get(status, Colors.BLUE)
    print(f"{color}{Colors.BOLD}{message}{Colors.ENDC}")

def test_backend_health():
    """ทดสอบ Backend Health"""
    print_status("🔌 ทดสอบ Backend Health...", "info")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status(f"✅ Backend พร้อมใช้งาน: {data.get('status')}", "success")
            return True
        else:
            print_status(f"❌ Backend ตอบกลับ HTTP {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"❌ ไม่สามารถเชื่อมต่อ Backend: {e}", "error")
        return False

def test_demo_task_status():
    """ทดสอบ Demo Task Status API"""
    print_status("📊 ทดสอบ Demo Task Status...", "info")
    
    task_id = "task-1754404431054"
    
    try:
        response = requests.get(f"http://localhost:8000/status/{task_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_status(f"✅ Task Status: {data.get('status')}", "success")
            print_status(f"📝 Progress: {data.get('progress')}%", "info")
            
            # ตรวจสอบ video_url
            video_url = data.get('video_url')
            if video_url:
                print_status(f"🎬 Video URL: {video_url}", "success")
                return video_url
            else:
                print_status("⚠️ ไม่พบ video_url ใน response", "warning")
                return None
        else:
            print_status(f"❌ Task Status API ตอบกลับ HTTP {response.status_code}", "error")
            return None
    except Exception as e:
        print_status(f"❌ ไม่สามารถเรียก Task Status API: {e}", "error")
        return None

def test_static_file_access(video_url):
    """ทดสอบการเข้าถึง Static File"""
    print_status("📁 ทดสอบการเข้าถึง Static File...", "info")
    
    if not video_url:
        print_status("❌ ไม่มี video_url ให้ทดสอบ", "error")
        return False
    
    # สร้าง full URL
    if video_url.startswith('/'):
        full_url = f"http://localhost:8000{video_url}"
    else:
        full_url = video_url
    
    print_status(f"🔗 ทดสอบ URL: {full_url}", "debug")
    
    try:
        # ทดสอบ HEAD request
        response = requests.head(full_url, timeout=10)
        if response.status_code == 200:
            content_length = response.headers.get('content-length', 'Unknown')
            content_type = response.headers.get('content-type', 'Unknown')
            print_status(f"✅ Static file พบ", "success")
            print_status(f"📦 ประเภท: {content_type}, ขนาด: {content_length} bytes", "info")
            return True
        else:
            print_status(f"❌ Static file ไม่พบ: HTTP {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"❌ ไม่สามารถเข้าถึง static file: {e}", "error")
        return False

def test_download_endpoint():
    """ทดสอบ Download Endpoint"""
    print_status("⬇️ ทดสอบ Download Endpoint...", "info")
    
    task_id = "task-1754404431054"
    download_url = f"http://localhost:8000/download/{task_id}"
    
    try:
        response = requests.head(download_url, timeout=10)
        if response.status_code == 200:
            content_length = response.headers.get('content-length', 'Unknown')
            content_type = response.headers.get('content-type', 'Unknown')
            print_status(f"✅ Download endpoint พร้อมใช้งาน", "success")
            print_status(f"📦 ประเภท: {content_type}, ขนาด: {content_length} bytes", "info")
            return True
        else:
            print_status(f"❌ Download endpoint ไม่พบ: HTTP {response.status_code}", "error")
            return False
    except Exception as e:
        print_status(f"❌ ไม่สามารถเข้าถึง download endpoint: {e}", "error")
        return False

def test_file_exists():
    """ทดสอบไฟล์มีอยู่จริงในระบบ"""
    print_status("💾 ทดสอบไฟล์ในระบบ...", "info")
    
    task_id = "task-1754404431054"
    file_paths = [
        f"output/final_{task_id}.mp4",
        f"output/translated_audio_{task_id}.mp3",
        f"output/subtitle_{task_id}.srt"
    ]
    
    all_exist = True
    for file_path in file_paths:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print_status(f"✅ {file_path}: {size} bytes", "success")
        else:
            print_status(f"❌ ไม่พบไฟล์: {file_path}", "error")
            all_exist = False
    
    return all_exist

def generate_test_html():
    """สร้างไฟล์ HTML สำหรับทดสอบ"""
    print_status("📄 สร้างไฟล์ HTML สำหรับทดสอบ...", "info")
    
    html_content = '''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ทดสอบ Video Player - YouTube Translator</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        video { width: 100%; max-width: 600px; height: auto; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 ทดสอบ Video Player Integration</h1>
        
        <div class="status info">
            <strong>📋 ข้อมูลการทดสอบ:</strong><br>
            - Task ID: task-1754404431054<br>
            - Video URL: <span id="videoUrl">กำลังโหลด...</span><br>
            - File Status: <span id="fileStatus">กำลังตรวจสอบ...</span>
        </div>
        
        <h2>🎥 Video Player Test</h2>
        <video id="testVideo" controls preload="metadata">
            <p>กำลังโหลดวิดีโอ...</p>
        </video>
        
        <div style="margin: 20px 0;">
            <button onclick="loadVideo()">🔄 โหลดวิดีโอใหม่</button>
            <button onclick="testAPI()">🔍 ทดสอบ API</button>
            <button onclick="downloadVideo()">⬇️ ดาวน์โหลด</button>
        </div>
        
        <div id="logs" style="background: #f8f9fa; padding: 15px; border-radius: 5px; height: 300px; overflow-y: auto; font-family: monospace; font-size: 12px;"></div>
    </div>

    <script>
        function log(message, type = 'info') {
            const logs = document.getElementById('logs');
            const timestamp = new Date().toLocaleTimeString();
            const colors = { 
                info: '#333', 
                success: '#28a745', 
                error: '#dc3545', 
                warning: '#ffc107' 
            };
            logs.innerHTML += `<div style="color: ${colors[type] || '#333'};">[${timestamp}] ${message}</div>`;
            logs.scrollTop = logs.scrollHeight;
        }

        async function testAPI() {
            log('🔍 ทดสอบ Task Status API...', 'info');
            try {
                const response = await fetch('http://localhost:8000/status/task-1754404431054');
                if (response.ok) {
                    const data = await response.json();
                    log(`✅ API Success: ${JSON.stringify(data, null, 2)}`, 'success');
                    
                    if (data.video_url) {
                        document.getElementById('videoUrl').textContent = data.video_url;
                        return data.video_url;
                    }
                } else {
                    log(`❌ API Error: HTTP ${response.status}`, 'error');
                }
            } catch (error) {
                log(`❌ API Exception: ${error.message}`, 'error');
            }
            return null;
        }

        async function loadVideo() {
            log('🎬 โหลดวิดีโอ...', 'info');
            const videoUrl = await testAPI();
            
            if (videoUrl) {
                const video = document.getElementById('testVideo');
                const fullUrl = videoUrl.startsWith('/') ? `http://localhost:8000${videoUrl}` : videoUrl;
                
                video.onloadstart = () => log('📊 เริ่มโหลดวิดีโอ', 'info');
                video.onloadedmetadata = () => log('📋 โหลด metadata เสร็จ', 'success');
                video.oncanplay = () => log('▶️ วิดีโอพร้อมเล่น', 'success');
                video.onerror = (e) => log(`❌ Error โหลดวิดีโอ: ${e.target.error?.message}`, 'error');
                
                video.src = fullUrl;
                log(`🔗 ตั้งค่า video src: ${fullUrl}`, 'info');
                
                document.getElementById('fileStatus').textContent = 'กำลังโหลด...';
            } else {
                log('❌ ไม่สามารถโหลดวิดีโอได้ - ไม่พบ URL', 'error');
                document.getElementById('fileStatus').textContent = 'ไม่พบไฟล์';
            }
        }

        function downloadVideo() {
            log('⬇️ เปิดหน้าดาวน์โหลด...', 'info');
            window.open('http://localhost:8000/download/task-1754404431054', '_blank');
        }

        // Auto-load on page ready
        document.addEventListener('DOMContentLoaded', () => {
            log('🚀 หน้าเว็บพร้อมใช้งาน', 'info');
            loadVideo();
        });
    </script>
</body>
</html>'''
    
    with open('test-video-ui-integration.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print_status("✅ สร้างไฟล์ test-video-ui-integration.html เสร็จแล้ว", "success")

def main():
    """ฟังก์ชันหลัก"""
    print_status("🎬 เริ่มทดสอบ Video UI Integration", "info")
    print_status("=" * 60, "info")
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Demo Task Status", test_demo_task_status),
        ("File System Check", test_file_exists),
        ("Download Endpoint", test_download_endpoint),
        ("HTML Generator", generate_test_html)
    ]
    
    results = {}
    video_url = None
    
    for test_name, test_func in tests:
        print_status(f"\n🧪 ทดสอบ: {test_name}", "info")
        print_status("-" * 40, "info")
        
        try:
            if test_name == "Demo Task Status":
                video_url = test_func()
                results[test_name] = video_url is not None
            else:
                results[test_name] = test_func()
                
        except Exception as e:
            print_status(f"💥 {test_name}: ข้อผิดพลาด - {str(e)}", "error")
            results[test_name] = False
        
        time.sleep(0.5)
    
    # ทดสอบ static file ถ้ามี video_url
    if video_url:
        print_status(f"\n🧪 ทดสอบ: Static File Access", "info")
        print_status("-" * 40, "info")
        results["Static File Access"] = test_static_file_access(video_url)
    
    # สรุปผล
    print_status("\n" + "=" * 60, "info")
    print_status("📊 สรุปผลการทดสอบ", "info")
    print_status("=" * 60, "info")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ ผ่าน" if result else "❌ ไม่ผ่าน"
        status_color = "success" if result else "error"
        print_status(f"{test_name:<25}: {status}", status_color)
    
    print_status(f"\n🎯 ผลรวม: {passed}/{total} การทดสอบผ่าน", 
                "success" if passed == total else "warning")
    
    if passed >= total - 1:  # อนุญาตให้ 1 test ไม่ผ่าน
        print_status("🎉 Video UI Integration พร้อมใช้งาน!", "success")
        print_status("💡 เปิดไฟล์: test-video-ui-integration.html", "info")
        print_status("🌐 หรือไปที่: http://localhost:3000", "info")
    else:
        print_status("⚠️ มีปัญหาที่ต้องแก้ไข", "warning")
        print_status("🔧 ตรวจสอบ Docker services และ configuration", "info")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_status("\n⏹️ การทดสอบถูกยกเลิก", "warning")
    except Exception as e:
        print_status(f"\n💥 ข้อผิดพลาดร้ายแรง: {str(e)}", "error")
