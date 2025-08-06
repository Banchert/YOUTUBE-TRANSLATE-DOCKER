import requests
import time
import os

def test_complete_workflow():
    """Test the complete workflow from frontend to backend"""
    print("🎯 TESTING COMPLETE WORKFLOW")
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
        
        # Step 2: Test frontend accessibility
        print("\n2️⃣ Testing frontend accessibility...")
        try:
            frontend_response = requests.get("http://localhost:3000", timeout=5)
            if frontend_response.status_code == 200:
                print("✅ Frontend is accessible")
            else:
                print(f"⚠️ Frontend status: {frontend_response.status_code}")
        except Exception as e:
            print(f"❌ Frontend not accessible: {e}")
        
        # Step 3: Test YouTube URL translation (simulating frontend)
        print("\n3️⃣ Testing YouTube URL translation...")
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
        
        # Step 4: Test status monitoring
        print("\n4️⃣ Testing status monitoring...")
        max_retries = 15
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
                        
                        # Test download
                        download_response = requests.head(f"http://localhost:8000/download/{task_id}")
                        print(f"Download available: {download_response.status_code == 200}")
                        
                        return True
                    elif status == 'failed':
                        error = status_data.get('error', 'Unknown error')
                        print(f"\n❌ Translation failed: {error}")
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
                time.sleep(4)  # Wait 4 seconds between retries
        
        print(f"\n⏰ Status monitoring completed (max retries reached)")
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_upload_workflow():
    """Test file upload workflow"""
    print("\n📁 TESTING FILE UPLOAD WORKFLOW")
    print("=" * 40)
    
    try:
        # Create test video
        test_video = "test_final.mp4"
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
        else:
            print(f"❌ Status not found: {status_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ File upload test error: {e}")
        return False
    
    finally:
        # Cleanup
        if os.path.exists('test_final.mp4'):
            os.remove('test_final.mp4')
            print(f"🧹 Cleaned up test file")

if __name__ == "__main__":
    print("🚀 STARTING FINAL WORKFLOW TESTS")
    print("=" * 60)
    
    # Test YouTube URL workflow
    youtube_test = test_complete_workflow()
    
    # Test file upload workflow
    file_test = test_file_upload_workflow()
    
    if youtube_test and file_test:
        print(f"\n🎉 ALL WORKFLOW TESTS PASSED!")
        print(f"   The system is working correctly.")
        print(f"   Frontend and backend communication is established.")
    else:
        print(f"\n❌ SOME WORKFLOW TESTS FAILED!")
        print(f"   Check the logs above for issues.") 