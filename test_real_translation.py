import requests
import time
import os
import json

def create_test_video_with_audio():
    """Create a test video file with some audio content"""
    print("🎬 Creating test video with audio...")
    
    # Create a more realistic test video file
    # This will be a simple MP4 with some dummy audio data
    test_video_path = "test_video_with_audio.mp4"
    
    # Create a minimal MP4 file with audio track
    mp4_content = (
        b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom'
        b'\x00\x00\x00\x08free'
        b'\x00\x00\x00\x1cmdat'
        b'\x00' * 1000  # Dummy audio/video data
    )
    
    with open(test_video_path, 'wb') as f:
        f.write(mp4_content)
    
    print(f"✅ Created test video: {test_video_path} ({len(mp4_content)} bytes)")
    return test_video_path

def test_complete_translation_pipeline():
    """Test the complete translation pipeline with real file upload"""
    print("🚀 TESTING COMPLETE VIDEO TRANSLATION PIPELINE")
    print("=" * 60)
    
    try:
        # Step 1: Create test video
        video_file = create_test_video_with_audio()
        
        # Step 2: Upload video
        print(f"\n📤 STEP 1: Uploading video file...")
        with open(video_file, 'rb') as f:
            files = {'video': f}
            upload_response = requests.post("http://localhost:8000/upload", files=files)
        
        if upload_response.status_code != 200:
            print(f"❌ Upload failed: {upload_response.text}")
            return
        
        upload_data = upload_response.json()
        print(f"✅ Video uploaded successfully!")
        print(f"   File ID: {upload_data.get('file_id')}")
        print(f"   Filename: {upload_data.get('filename')}")
        print(f"   Size: {upload_data.get('size')} bytes")
        
        # Step 3: Start translation using new endpoint
        print(f"\n🔄 STEP 2: Starting translation...")
        translation_payload = {
            "file_path": upload_data.get('file_path'),  # Use uploaded file path
            "target_language": "th"
        }
        
        translate_response = requests.post("http://localhost:8000/translate-file", json=translation_payload)
        print(f"Translation request status: {translate_response.status_code}")
        
        if translate_response.status_code != 200:
            print(f"❌ Translation request failed: {translate_response.text}")
            return
        
        result = translate_response.json()
        task_id = result.get("task_id")
        print(f"✅ Translation started!")
        print(f"   Task ID: {task_id}")
        
        # Step 4: Monitor progress
        print(f"\n📊 STEP 3: Monitoring translation progress...")
        for i in range(30):  # Monitor for 5 minutes
            time.sleep(10)
            
            status_response = requests.get(f"http://localhost:8000/status/{task_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get('status', 'unknown')
                progress = status_data.get('progress', 0)
                message = status_data.get('message', 'Processing')
                
                print(f"   [{i+1}] {status} ({progress}%) - {message}")
                
                # Show detailed step progress
                steps = status_data.get('steps', {})
                if steps:
                    for step_name, step_data in steps.items():
                        step_status = step_data.get('status', 'pending')
                        step_progress = step_data.get('progress', 0)
                        print(f"      {step_name}: {step_status} ({step_progress}%)")
                
                if status == 'completed':
                    print(f"\n🎉 SUCCESS! Translation completed!")
                    
                    # Step 5: Test download
                    print(f"\n📥 STEP 4: Testing download...")
                    download_response = requests.head(f"http://localhost:8000/download/{task_id}")
                    print(f"Download status: {download_response.status_code}")
                    
                    if download_response.status_code == 200:
                        file_size = download_response.headers.get('content-length', 'unknown')
                        content_type = download_response.headers.get('content-type', 'unknown')
                        print(f"✅ Download available!")
                        print(f"   File size: {file_size} bytes")
                        print(f"   Content type: {content_type}")
                        print(f"   Download URL: http://localhost:8000/download/{task_id}")
                        
                        # Try to download the file
                        print(f"\n💾 STEP 5: Downloading translated video...")
                        download_file_response = requests.get(f"http://localhost:8000/download/{task_id}")
                        
                        if download_file_response.status_code == 200:
                            output_filename = f"translated_video_{task_id}.mp4"
                            with open(output_filename, 'wb') as f:
                                f.write(download_file_response.content)
                            
                            actual_size = os.path.getsize(output_filename)
                            print(f"✅ Video downloaded successfully!")
                            print(f"   Saved as: {output_filename}")
                            print(f"   File size: {actual_size} bytes")
                            
                            # Check if file is valid
                            if actual_size > 1000:
                                print(f"   ✅ File appears to be valid (size > 1KB)")
                            else:
                                print(f"   ⚠️  File seems small, may be placeholder")
                            
                            return True
                        else:
                            print(f"❌ Download failed: {download_file_response.status_code}")
                    else:
                        print(f"❌ Download not available: {download_response.status_code}")
                    
                    break
                elif status == 'failed':
                    error = status_data.get('error', 'Unknown error')
                    print(f"\n❌ Translation failed: {error}")
                    break
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
                break
        
        print(f"\n⏰ Translation monitoring completed")
        
    except Exception as e:
        print(f"❌ Pipeline test error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if os.path.exists('test_video_with_audio.mp4'):
            os.remove('test_video_with_audio.mp4')
            print(f"\n🧹 Cleaned up test video file")

def show_system_status():
    """Show current system status"""
    print(f"\n📊 SYSTEM STATUS CHECK")
    print("=" * 40)
    
    try:
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Backend Status: {health_data.get('status')}")
            
            services = health_data.get('services', {})
            for service, status in services.items():
                status_icon = "✅" if "available" in status.lower() else "⚠️"
                print(f"   {status_icon} {service}: {status}")
        else:
            print(f"❌ Backend health check failed: {health_response.status_code}")
            
    except Exception as e:
        print(f"❌ System status error: {e}")

if __name__ == "__main__":
    show_system_status()
    success = test_complete_translation_pipeline()
    
    if success:
        print(f"\n🎉 SUCCESS! Video translation and download completed!")
        print(f"   You can now view the translated video file.")
    else:
        print(f"\n❌ Translation test did not complete successfully.")
        print(f"   Check the logs above for details.") 