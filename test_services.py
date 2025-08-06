import requests
import time

def check_services():
    """Check if external services are running"""
    services = {
        "Translation": "http://localhost:5000/languages",
        "Whisper": "http://localhost:5001/health", 
        "TTS": "http://localhost:5002/health"
    }
    
    print("Checking external services:")
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=3)
            status = "OK" if response.status_code == 200 else f"ERROR ({response.status_code})"
        except Exception as e:
            status = f"NOT RUNNING ({str(e)})"
        print(f"  {name}: {status}")

def test_youtube_translation():
    """Test YouTube video translation with the provided URL"""
    url = "https://youtu.be/U7tmd4Yh9Do?si=NXcearW5XABOqzcF"
    
    print(f"\nTesting YouTube video translation:")
    print(f"URL: {url}")
    
    # Test backend API
    try:
        backend_url = "http://localhost:8000"
        
        # Check if backend is running
        health_response = requests.get(f"{backend_url}/health", timeout=5)
        print(f"Backend status: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("Service statuses:", health_data.get("services", {}))
            
            # Start translation
            translate_payload = {
                "youtube_url": url,
                "target_language": "th"
            }
            
            translate_response = requests.post(f"{backend_url}/translate", json=translate_payload)
            print(f"Translation request status: {translate_response.status_code}")
            
            if translate_response.status_code == 200:
                result = translate_response.json()
                task_id = result.get("task_id")
                print(f"Task ID: {task_id}")
                
                # Monitor task progress
                if task_id:
                    for i in range(30):  # Monitor for 5 minutes
                        time.sleep(10)
                        status_response = requests.get(f"{backend_url}/status/{task_id}")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            print(f"Progress: {status_data.get('progress', 0)}% - {status_data.get('message', 'Processing')}")
                            
                            if status_data.get('status') in ['completed', 'failed']:
                                break
                        else:
                            print(f"Status check failed: {status_response.status_code}")
                            break
            else:
                print(f"Translation failed: {translate_response.text}")
        
    except Exception as e:
        print(f"Backend test failed: {str(e)}")

if __name__ == "__main__":
    check_services()
    test_youtube_translation() 