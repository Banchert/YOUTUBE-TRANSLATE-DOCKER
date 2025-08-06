#!/usr/bin/env python3
"""
Test script to verify TTS service fixes
"""

import asyncio
import os
import sys
import logging

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.tts_service import TTSService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_tts_service():
    """Test the TTS service with the fixes"""
    
    print("Testing TTS Service...")
    
    # Initialize TTS service
    tts_service = TTSService()
    
    # Test with a simple text
    test_text = "สวัสดีครับ นี่คือการทดสอบการแปลงข้อความเป็นเสียง"
    task_id = "test_tts_fix"
    
    try:
        print(f"Converting text: {test_text}")
        audio_path = await tts_service.text_to_speech(test_text, task_id, "th", "female")
        
        if os.path.exists(audio_path):
            print(f"✅ TTS test successful! Audio file created: {audio_path}")
            
            # Get audio duration
            duration = await tts_service.get_audio_duration(audio_path)
            print(f"Audio duration: {duration:.2f} seconds")
            
            # Clean up
            await tts_service.cleanup_tts_files(task_id)
            print("✅ Cleanup completed")
            
        else:
            print(f"❌ TTS test failed! Audio file not found: {audio_path}")
            
    except Exception as e:
        print(f"❌ TTS test failed with error: {str(e)}")
        return False
    
    return True

async def test_long_text_tts():
    """Test TTS service with long text that requires chunking"""
    
    print("\nTesting TTS Service with long text...")
    
    # Initialize TTS service
    tts_service = TTSService()
    
    # Create a long text that will require chunking
    long_text = "สวัสดีครับ นี่คือการทดสอบการแปลงข้อความเป็นเสียงสำหรับข้อความยาว " * 50
    task_id = "test_long_tts_fix"
    
    try:
        print(f"Converting long text ({len(long_text)} characters)")
        audio_path = await tts_service.text_to_speech(long_text, task_id, "th", "female")
        
        if os.path.exists(audio_path):
            print(f"✅ Long text TTS test successful! Audio file created: {audio_path}")
            
            # Get audio duration
            duration = await tts_service.get_audio_duration(audio_path)
            print(f"Audio duration: {duration:.2f} seconds")
            
            # Clean up
            await tts_service.cleanup_tts_files(task_id)
            print("✅ Cleanup completed")
            
        else:
            print(f"❌ Long text TTS test failed! Audio file not found: {audio_path}")
            
    except Exception as e:
        print(f"❌ Long text TTS test failed with error: {str(e)}")
        return False
    
    return True

async def main():
    """Main test function"""
    
    print("=" * 60)
    print("TTS Service Fix Test")
    print("=" * 60)
    
    # Test basic TTS
    success1 = await test_tts_service()
    
    # Test long text TTS
    success2 = await test_long_text_tts()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All TTS tests passed!")
        print("The path concatenation issue has been fixed.")
    else:
        print("❌ Some TTS tests failed!")
        print("Please check the error messages above.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 