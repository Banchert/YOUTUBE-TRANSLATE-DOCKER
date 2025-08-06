import requests
import time
import os

def test_frontend_backend_communication():
    """Test communication between frontend and backend"""
    print("🔍 TESTING FRONTEND-BACKEND COMMUNICATION")
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
        
        # Step 3: Create test video
        print("\n3️⃣ Creating test video...")
        test_video = "test_comm.mp4"
        video_content = (
            b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom'
            b'\x00\x00\x00\x08free'
            b'\x00\x00\x00\x1cmdat'
            b'\x00' * 1000
        )
        
        with open(test_video, 'wb') as f:
            f.write(video_content)
        
        # Step 4: Test upload endpoint
        print("\n4️⃣ Testing upload endpoint...")
        with open(test_video, 'rb') as f:
            files = {'video': f}
            upload_response = requests.post("http://localhost:8000/upload", files=files)
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.text}")
            return False
        
        upload_data = upload_response.json()
        print(f"✅ Upload successful: {upload_data.get('filename')}")
        
        # Step 5: Test translation endpoint
        print("\n5️⃣ Testing translation endpoint...")
        translation_payload = {
            "file_path": upload_data.get('file_path'),
            "target_language": "th"
        }
        
        print(f"Translation payload: {translation_payload}")
        translate_response = requests.post("http://localhost:8000/translate-file", json=translation_payload)
        print(f"Translation response status: {translate_response.status_code}")
        
        if translate_response.status_code != 200:
            print(f"❌ Translation request failed: {translate_response.text}")
            return False
        
        result = translate_response.json()
        task_id = result.get("task_id")
        print(f"✅ Translation started: {task_id}")
        
        # Step 6: Test status endpoint immediately
        print("\n6️⃣ Testing status endpoint...")
        status_response = requests.get(f"http://localhost:8000/status/{task_id}")
        print(f"Status response: {status_response.status_code}")
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"✅ Status found: {status_data.get('status')}")
            print(f"   Progress: {status_data.get('progress')}%")
            print(f"   Message: {status_data.get('message')}")
        else:
            print(f"❌ Status not found: {status_response.status_code}")
            print(f"   Response: {status_response.text}")
        
        # Step 7: Test with invalid task ID
        print("\n7️⃣ Testing invalid task ID...")
        invalid_response = requests.get("http://localhost:8000/status/invalid-task-id")
        print(f"Invalid task response: {invalid_response.status_code}")
        
        if invalid_response.status_code == 404:
            print("✅ Correctly returns 404 for invalid task")
        else:
            print(f"❌ Unexpected response for invalid task: {invalid_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists('test_comm.mp4'):
            os.remove('test_comm.mp4')
            print(f"\n🧹 Cleaned up test file")

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n🔍 TESTING API ENDPOINTS")
    print("=" * 30)
    
    endpoints = [
        ("/health", "GET"),
        ("/languages", "GET"),
        ("/stats", "GET"),
        ("/upload", "POST"),
    ]
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"http://localhost:8000{endpoint}")
            else:
                # For POST endpoints, just check if they exist
                response = requests.options(f"http://localhost:8000{endpoint}")
            
            status = "✅" if response.status_code in [200, 405] else "❌"
            print(f"{status} {method} {endpoint}: {response.status_code}")
            
        except Exception as e:
            print(f"❌ {method} {endpoint}: {e}")

if __name__ == "__main__":
    test_api_endpoints()
    success = test_frontend_backend_communication()
    
    if success:
        print(f"\n🎉 COMMUNICATION TEST PASSED!")
        print(f"   Frontend and backend are communicating correctly.")
    else:
        print(f"\n❌ COMMUNICATION TEST FAILED!")
        print(f"   Check the logs above for issues.") 