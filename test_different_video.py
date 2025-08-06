import requests
import time

def test_with_different_video():
    """Test with a different, potentially less restricted YouTube video"""
    print("Testing with a different YouTube video")
    print("=" * 50)
    
    # Try a different video (public domain or creative commons)
    test_urls = [
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # "Me at the zoo" - first YouTube video
        "https://www.youtube.com/watch?v=9bZkp7q19f0",  # Gangnam Style
        "https://youtu.be/U7tmd4Yh9Do?si=NXcearW5XABOqzcF"  # Original video
    ]
    
    for i, url in enumerate(test_urls):
        print(f"\n--- Test {i+1}: {url} ---")
        
        try:
            payload = {
                "youtube_url": url,
                "target_language": "th"
            }
            
            response = requests.post("http://localhost:8000/translate", json=payload)
            print(f"Request status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get("task_id")
                print(f"Task ID: {task_id}")
                
                # Check status a few times
                for j in range(5):
                    time.sleep(10)
                    status_response = requests.get(f"http://localhost:8000/status/{task_id}")
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get('status')
                        progress = status_data.get('progress', 0)
                        message = status_data.get('message', '')
                        
                        print(f"  [{j+1}] {status} ({progress}%) - {message}")
                        
                        if status in ['completed', 'failed']:
                            if status == 'completed':
                                print(f"SUCCESS! Video {i+1} translation completed!")
                                return True
                            else:
                                error = status_data.get('error', 'Unknown error')
                                print(f"FAILED: {error}")
                                break
                    else:
                        print(f"  Status check failed: {status_response.status_code}")
                        break
            else:
                print(f"Translation request failed: {response.text}")
                
        except Exception as e:
            print(f"Test {i+1} error: {e}")
    
    return False

if __name__ == "__main__":
    success = test_with_different_video()
    if not success:
        print("\nAll tests failed. YouTube might be blocking downloads from this environment.") 