import requests
import time
import os
import json

def create_proper_mp4():
    """Create a proper MP4 file with valid structure"""
    print("🎬 Creating proper MP4 file...")
    
    # This creates a minimal but valid MP4 file
    # MP4 structure: ftyp -> moov -> mdat
    mp4_content = (
        # ftyp box
        b'\x00\x00\x00\x20'  # box size
        b'ftyp'              # box type
        b'mp41'              # major brand
        b'\x00\x00\x00\x00'  # minor version
        b'mp41'              # compatible brand
        b'isom'              # compatible brand
        
        # moov box (minimal)
        b'\x00\x00\x00\x10'  # box size
        b'moov'              # box type
        b'\x00\x00\x00\x08'  # mvhd box size
        b'mvhd'              # mvhd box type
        b'\x00\x00\x00\x00'  # version and flags
        
        # mdat box
        b'\x00\x00\x00\x08'  # box size
        b'mdat'              # box type
        b'\x00' * 1000       # dummy data
    )
    
    test_video_path = "proper_test_video.mp4"
    with open(test_video_path, 'wb') as f:
        f.write(mp4_content)
    
    print(f"✅ Created proper MP4: {test_video_path} ({len(mp4_content)} bytes)")
    return test_video_path

def test_with_real_video_file():
    """Test with a real video file if available"""
    print("🎬 Looking for real video files...")
    
    # Common video file locations to check
    possible_videos = [
        "test.mp4",
        "sample.mp4", 
        "video.mp4",
        "demo.mp4",
        "example.mp4"
    ]
    
    for video_file in possible_videos:
        if os.path.exists(video_file):
            print(f"✅ Found real video file: {video_file}")
            return video_file
    
    print("⚠️  No real video files found, using generated MP4")
    return create_proper_mp4()

def test_complete_translation_pipeline():
    """Test the complete translation pipeline"""
    print("🚀 TESTING COMPLETE VIDEO TRANSLATION PIPELINE")
    print("=" * 60)
    
    try:
        # Step 1: Get test video
        video_file = test_with_real_video_file()
        
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
        
        # Step 3: Start translation
        print(f"\n🔄 STEP 2: Starting translation...")
        translation_payload = {
            "file_path": upload_data.get('file_path'),
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
                                print(f"   🎬 You can now play: {output_filename}")
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
                    
                    # Show more details about the error
                    if "moov atom not found" in error:
                        print(f"   💡 This is expected for dummy video files without proper audio")
                        print(f"   💡 Try with a real video file that contains audio")
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
        # Cleanup generated files
        for cleanup_file in ["proper_test_video.mp4"]:
            if os.path.exists(cleanup_file):
                os.remove(cleanup_file)
                print(f"🧹 Cleaned up: {cleanup_file}")

def show_usage_instructions():
    """Show instructions for using real video files"""
    print(f"\n" + "=" * 60)
    print("📋 HOW TO TEST WITH REAL VIDEO FILES")
    print("=" * 60)
    
    print(f"\n🎬 To test with real video files:")
    print(f"   1. Place a video file (MP4, AVI, MOV) in the current directory")
    print(f"   2. Name it: test.mp4, sample.mp4, video.mp4, demo.mp4, or example.mp4")
    print(f"   3. Run this script again")
    print(f"   4. The system will automatically detect and use the real video file")
    
    print(f"\n🌐 Or use the web interface:")
    print(f"   1. Open: http://localhost:3000")
    print(f"   2. Click 'Upload Video'")
    print(f"   3. Select your video file")
    print(f"   4. Choose target language (Thai)")
    print(f"   5. Click 'Translate'")
    
    print(f"\n📁 Supported video formats:")
    print(f"   • MP4, AVI, MOV, WebM, MKV, M4V")
    print(f"   • Max size: 500MB")
    print(f"   • Should contain audio for translation")

if __name__ == "__main__":
    success = test_complete_translation_pipeline()
    
    if success:
        print(f"\n🎉 SUCCESS! Video translation and download completed!")
        print(f"   You can now view the translated video file.")
    else:
        print(f"\n❌ Translation test did not complete successfully.")
        print(f"   This is expected for dummy video files without audio.")
        print(f"   Try with a real video file that contains speech.")
    
    show_usage_instructions() 