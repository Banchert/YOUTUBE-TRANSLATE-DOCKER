import requests
import time
import json

def test_individual_services():
    """Test each service individually"""
    print("=== Testing Individual Services ===")
    
    # Test Translation Service
    print("\n1. Testing Translation Service:")
    try:
        response = requests.get("http://localhost:5000/languages", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Available languages: {len(data)}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test Whisper Service
    print("\n2. Testing Whisper Service:")
    try:
        response = requests.get("http://localhost:5001/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test TTS Service
    print("\n3. Testing TTS Service:")
    try:
        response = requests.get("http://localhost:5002/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ERROR: {e}")

def test_backend_health():
    """Test backend health check"""
    print("\n=== Testing Backend Health ===")
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Backend Status: {data.get('status')}")
            print("Service Connections:")
            for service, status in data.get('services', {}).items():
                print(f"  {service}: {status}")
        else:
            print(f"Backend health check failed: {response.text}")
    except Exception as e:
        print(f"Backend health check error: {e}")

def test_simple_translation():
    """Test simple text translation"""
    print("\n=== Testing Simple Translation ===")
    try:
        payload = {
            "q": "Hello, how are you?",
            "source": "en",
            "target": "th"
        }
        response = requests.post("http://localhost:5000/translate", json=payload, timeout=10)
        print(f"Translation Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Original: {payload['q']}")
            print(f"Translated: {result.get('translatedText')}")
        else:
            print(f"Translation failed: {response.text}")
    except Exception as e:
        print(f"Translation error: {e}")

def get_video_info():
    """Get info about the YouTube video"""
    print("\n=== Getting Video Information ===")
    url = "https://youtu.be/U7tmd4Yh9Do?si=NXcearW5XABOqzcF"
    print(f"URL: {url}")
    
    # Let's try to get video info using yt-dlp
    try:
        import subprocess
        result = subprocess.run([
            'yt-dlp', '--no-download', '--print', 'title,duration,uploader', url
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 3:
                print(f"Title: {lines[0]}")
                print(f"Duration: {lines[1]} seconds")
                print(f"Uploader: {lines[2]}")
        else:
            print(f"yt-dlp error: {result.stderr}")
    except Exception as e:
        print(f"Video info error: {e}")

def test_youtube_translation():
    """Test YouTube video translation"""
    print("\n=== Testing YouTube Video Translation ===")
    url = "https://youtu.be/U7tmd4Yh9Do?si=NXcearW5XABOqzcF"
    
    try:
        # Start translation
        payload = {
            "youtube_url": url,
            "target_language": "th"
        }
        
        print("Starting translation...")
        response = requests.post("http://localhost:8000/translate", json=payload, timeout=10)
        print(f"Translation request status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"Task ID: {task_id}")
            
            if task_id:
                # Monitor task progress
                for i in range(60):  # Monitor for 10 minutes
                    time.sleep(10)
                    try:
                        status_response = requests.get(f"http://localhost:8000/status/{task_id}", timeout=5)
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            status = status_data.get('status', 'unknown')
                            progress = status_data.get('progress', 0)
                            message = status_data.get('message', 'Processing')
                            
                            print(f"[{i*10}s] {status}: {progress}% - {message}")
                            
                            # Print step details if available
                            steps = status_data.get('steps', {})
                            if steps:
                                for step_name, step_data in steps.items():
                                    step_status = step_data.get('status', 'pending')
                                    step_progress = step_data.get('progress', 0)
                                    print(f"  {step_name}: {step_status} ({step_progress}%)")
                            
                            if status in ['completed', 'failed']:
                                if status == 'completed':
                                    print(f"\nSUCCESS! Translation completed.")
                                    print(f"Download URL: http://localhost:8000/download/{task_id}")
                                    
                                    # Test download
                                    try:
                                        download_response = requests.head(f"http://localhost:8000/download/{task_id}")
                                        print(f"Download status: {download_response.status_code}")
                                        if download_response.status_code == 200:
                                            file_size = download_response.headers.get('content-length', 'unknown')
                                            print(f"File size: {file_size} bytes")
                                    except Exception as e:
                                        print(f"Download test error: {e}")
                                else:
                                    print(f"\nFAILED! Translation failed.")
                                    error = status_data.get('error', 'Unknown error')
                                    print(f"Error: {error}")
                                break
                        else:
                            print(f"Status check failed: {status_response.status_code} - {status_response.text}")
                            break
                    except Exception as e:
                        print(f"Status check error: {e}")
                        break
        else:
            print(f"Translation request failed: {response.text}")
            
    except Exception as e:
        print(f"YouTube translation test error: {e}")

if __name__ == "__main__":
    print("YouTube Video Translation System Test")
    print("=" * 50)
    
    test_individual_services()
    test_backend_health()
    test_simple_translation()
    get_video_info()
    test_youtube_translation() 