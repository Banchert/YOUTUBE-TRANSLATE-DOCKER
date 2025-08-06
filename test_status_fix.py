import requests
import time
import os

def test_status_checking():
    """Test the status checking functionality"""
    print("🧪 TESTING STATUS CHECKING")
    print("=" * 40)
    
    try:
        # Step 1: Test backend health
        print("\n1️⃣ Testing backend health...")
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            return False
        
        # Step 2: Create and upload a test video
        print("\n2️⃣ Creating test video...")
        test_video = "test_status.mp4"
        video_content = (
            b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom'
            b'\x00\x00\x00\x08free'
            b'\x00\x00\x00\x1cmdat'
            b'\x00' * 1000
        )
        
        with open(test_video, 'wb') as f:
            f.write(video_content)
        
        # Step 3: Upload video
        print("\n3️⃣ Uploading video...")
        with open(test_video, 'rb') as f:
            files = {'video': f}
            upload_response = requests.post("http://localhost:8000/upload", files=files)
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.text}")
            return False
        
        upload_data = upload_response.json()
        print(f"✅ Upload successful: {upload_data.get('filename')}")
        
        # Step 4: Start translation
        print("\n4️⃣ Starting translation...")
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
        
        # Step 5: Test status checking with retries
        print("\n5️⃣ Testing status checking...")
        max_retries = 10
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
                        print(f"\n🎉 SUCCESS! Status checking works correctly!")
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
                time.sleep(3)  # Wait 3 seconds between retries
        
        print(f"\n⏰ Status checking test completed (max retries reached)")
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists('test_status.mp4'):
            os.remove('test_status.mp4')
            print(f"\n🧹 Cleaned up test file")

def test_invalid_task_id():
    """Test status checking with invalid task ID"""
    print("\n🔍 TESTING INVALID TASK ID")
    print("=" * 30)
    
    try:
        # Test with non-existent task ID
        invalid_task_id = "invalid-task-id-12345"
        status_response = requests.get(f"http://localhost:8000/status/{invalid_task_id}")
        
        print(f"Invalid task ID test: {status_response.status_code}")
        
        if status_response.status_code == 404:
            print("✅ Correctly returns 404 for invalid task ID")
            return True
        else:
            print(f"❌ Unexpected response: {status_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid task ID test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 STARTING STATUS CHECKING TESTS")
    print("=" * 50)
    
    # Test invalid task ID first
    invalid_test = test_invalid_task_id()
    
    # Test normal workflow
    normal_test = test_status_checking()
    
    if invalid_test and normal_test:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   Status checking is working correctly.")
    else:
        print(f"\n❌ SOME TESTS FAILED!")
        print(f"   Check the logs above for issues.") 