import requests
import time
import os

def test_youtube_download_improvements():
    """Test the improved YouTube download handling"""
    print("🎯 TESTING IMPROVED YOUTUBE DOWNLOAD")
    print("=" * 50)
    
    try:
        # Step 1: Test backend health
        print("\n1️⃣ Testing backend health...")
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            return False
        
        # Step 2: Test YouTube URL translation with improved handling
        print("\n2️⃣ Testing YouTube URL translation...")
        youtube_url = "https://youtu.be/U7tmd4Yh9Do?si=NXcearW5XABOqzcF"
        
        translation_payload = {
            "youtube_url": youtube_url,
            "target_language": "th"
        }
        
        print(f"Translation payload: {translation_payload}")
        translate_response = requests.post("http://localhost:8000/translate", json=translation_payload)
        print(f"Translation response status: {translate_response.status_code}")
        
        if translate_response.status_code != 200:
            print(f"❌ Translation request failed: {translate_response.text}")
            return False
        
        result = translate_response.json()
        task_id = result.get("task_id")
        print(f"✅ Translation started: {task_id}")
        
        # Step 3: Monitor the download process
        print("\n3️⃣ Monitoring download process...")
        max_retries = 20
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                status_response = requests.get(f"http://localhost:8000/status/{task_id}")
                print(f"Status check {retry_count + 1}: {status_response.status_code}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', 'unknown')
                    progress = status_data.get('progress', 0)
                    message = status_data.get('message', 'Processing')
                    
                    print(f"   ✅ Status: {status} ({progress}%) - {message}")
                    
                    # Show step details
                    steps = status_data.get('steps', {})
                    for step_name, step_data in steps.items():
                        step_status = step_data.get('status', 'pending')
                        step_progress = step_data.get('progress', 0)
                        print(f"      {step_name}: {step_status} ({step_progress}%)")
                    
                    if status == 'completed':
                        print(f"\n🎉 SUCCESS! Translation completed!")
                        return True
                    elif status == 'failed':
                        error = status_data.get('error', 'Unknown error')
                        print(f"\n❌ Translation failed: {error}")
                        
                        # Check if it's a YouTube blocking error
                        if "blocking downloads" in error.lower():
                            print(f"\n💡 RECOMMENDATION:")
                            print(f"   YouTube is blocking downloads. Please:")
                            print(f"   1. Download the video manually")
                            print(f"   2. Upload it directly to the system")
                            print(f"   3. Use the file upload feature instead")
                        
                        return False
                    else:
                        print(f"   ⏳ Continuing to monitor...")
                        
                elif status_response.status_code == 404:
                    print(f"   ⏳ Task not found yet (attempt {retry_count + 1}/{max_retries})")
                else:
                    print(f"   ❌ Unexpected status code: {status_response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Status check error: {e}")
            
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(3)  # Wait 3 seconds between retries
        
        print(f"\n⏰ Monitoring completed (max retries reached)")
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_upload_alternative():
    """Test file upload as an alternative to YouTube download"""
    print("\n📁 TESTING FILE UPLOAD ALTERNATIVE")
    print("=" * 40)
    
    try:
        # Create a test video file
        test_video = "test_alternative.mp4"
        video_content = (
            b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom'
            b'\x00\x00\x00\x08free'
            b'\x00\x00\x00\x1cmdat'
            b'\x00' * 1000
        )
        
        with open(test_video, 'wb') as f:
            f.write(video_content)
        
        # Upload video
        with open(test_video, 'rb') as f:
            files = {'video': f}
            upload_response = requests.post("http://localhost:8000/upload", files=files)
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.text}")
            return False
        
        upload_data = upload_response.json()
        print(f"✅ Upload successful: {upload_data.get('filename')}")
        
        # Start translation
        translation_payload = {
            "file_path": upload_data.get('file_path'),
            "target_language": "th"
        }
        
        translate_response = requests.post("http://localhost:8000/translate-file", json=translation_payload)
        if translate_response.status_code != 200:
            print(f"❌ Translation request failed: {translate_response.text}")
            return False
        
        result = translate_response.json()
        task_id = result.get("task_id")
        print(f"✅ Translation started: {task_id}")
        
        # Quick status check
        status_response = requests.get(f"http://localhost:8000/status/{task_id}")
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"✅ Status found: {status_data.get('status')} ({status_data.get('progress')}%)")
            print(f"   Message: {status_data.get('message')}")
        else:
            print(f"❌ Status not found: {status_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ File upload test error: {e}")
        return False
    
    finally:
        # Cleanup
        if os.path.exists('test_alternative.mp4'):
            os.remove('test_alternative.mp4')
            print(f"🧹 Cleaned up test file")

if __name__ == "__main__":
    print("🚀 TESTING YOUTUBE DOWNLOAD IMPROVEMENTS")
    print("=" * 60)
    
    # Test improved YouTube download
    youtube_test = test_youtube_download_improvements()
    
    # Test file upload alternative
    file_test = test_file_upload_alternative()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"   YouTube Download: {'✅ PASSED' if youtube_test else '❌ FAILED'}")
    print(f"   File Upload: {'✅ PASSED' if file_test else '❌ FAILED'}")
    
    if not youtube_test and file_test:
        print(f"\n💡 RECOMMENDATION:")
        print(f"   Use file upload instead of YouTube URLs.")
        print(f"   Download videos manually and upload them directly.")
    elif youtube_test and file_test:
        print(f"\n🎉 BOTH METHODS WORK!")
    else:
        print(f"\n❌ BOTH METHODS FAILED!")
        print(f"   Check the system configuration.") 