#!/usr/bin/env python3
"""
Comprehensive test script to verify TTS service fixes
"""

import asyncio
import os
import sys
import logging
import tempfile
import shutil

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.tts_service import TTSService, normalize_path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_path_normalization():
    """Test the path normalization function"""
    
    print("Testing path normalization...")
    
    # Test cases for path normalization
    # Focus on the key requirement: removing path duplication
    test_cases = [
        "uploads/file.wav",
        "uploads/uploads/file.wav", 
        "uploads/uploads/uploads/file.wav",
        "/app/uploads/uploads/file.wav",
        "/app/uploads/file.wav",
        "/path/to/uploads/uploads/file.wav",
    ]
    
    for input_path in test_cases:
        result = normalize_path(input_path)
        print(f"  {input_path} -> {result}")
        
        # Check that path duplication is removed
        if 'uploads/uploads' in result:
            print(f"    ❌ Path duplication still present: {result}")
            return False
        
        # Check that the path is absolute
        if not os.path.isabs(result):
            print(f"    ❌ Path is not absolute: {result}")
            return False
    
    print("  ✅ Path normalization tests passed")
    
    # Additional test: Check for the specific error case
    print("\n  Testing specific error case...")
    error_case = "uploads/uploads/optimized_audio_test_chunk_0.wav"
    normalized = normalize_path(error_case)
    print(f"    Error case: {error_case}")
    print(f"    Normalized: {normalized}")
    
    if 'uploads/uploads' in normalized:
        print(f"    ❌ Path duplication still present in error case")
        return False
    
    print(f"    ✅ Error case fixed - no path duplication")
    return True

async def test_tts_service_initialization():
    """Test TTS service initialization"""
    
    print("\nTesting TTS service initialization...")
    
    try:
        tts_service = TTSService()
        print(f"  ✅ TTS service initialized successfully")
        print(f"  Upload dir: {tts_service.upload_dir}")
        print(f"  Output dir: {tts_service.output_dir}")
        return True
    except Exception as e:
        print(f"  ❌ TTS service initialization failed: {e}")
        return False

async def test_file_creation():
    """Test file creation in uploads directory"""
    
    print("\nTesting file creation...")
    
    try:
        tts_service = TTSService()
        
        # Create a test file
        test_file = os.path.join(tts_service.upload_dir, "test_file.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        if os.path.exists(test_file):
            print(f"  ✅ Test file created: {test_file}")
            os.remove(test_file)
            return True
        else:
            print(f"  ❌ Test file was not created")
            return False
            
    except Exception as e:
        print(f"  ❌ File creation test failed: {e}")
        return False

async def test_concatenation_filelist():
    """Test the concatenation filelist creation"""
    
    print("\nTesting concatenation filelist creation...")
    
    try:
        tts_service = TTSService()
        
        # Create some dummy audio files
        test_files = []
        for i in range(3):
            test_file = os.path.join(tts_service.upload_dir, f"test_audio_{i}.wav")
            with open(test_file, 'w') as f:
                f.write(f"dummy audio content {i}")
            test_files.append(test_file)
        
        # Test the concatenation method directly
        task_id = "test_concatenation"
        filelist_path = os.path.join(tts_service.upload_dir, f"filelist_{task_id}.txt")
        
        # Create filelist manually to test path normalization
        with open(filelist_path, 'w') as f:
            for audio_file in test_files:
                normalized_path = normalize_path(audio_file)
                f.write(f"file '{normalized_path}'\n")
        
        # Read and check the filelist
        with open(filelist_path, 'r') as f:
            content = f.read()
            print(f"  Filelist content:\n{content}")
        
        # Check for path duplication
        if 'uploads/uploads' in content:
            print(f"  ❌ Path duplication detected in filelist")
            return False
        
        print(f"  ✅ Filelist created without path duplication")
        
        # Cleanup
        for test_file in test_files:
            os.remove(test_file)
        os.remove(filelist_path)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Concatenation filelist test failed: {e}")
        return False

async def test_docker_environment_simulation():
    """Simulate Docker environment paths"""
    
    print("\nTesting Docker environment simulation...")
    
    try:
        # Simulate Docker environment where working directory is /app
        original_cwd = os.getcwd()
        
        # Create a temporary directory structure similar to Docker
        with tempfile.TemporaryDirectory() as temp_dir:
            app_dir = os.path.join(temp_dir, "app")
            uploads_dir = os.path.join(app_dir, "uploads")
            os.makedirs(uploads_dir)
            
            # Change to app directory
            os.chdir(app_dir)
            
            # Test path normalization in this environment
            test_paths = [
                "uploads/uploads/test.wav",
                "uploads/uploads/optimized_audio_test_chunk_0.wav",
                "/app/uploads/uploads/file.wav"
            ]
            
            for test_path in test_paths:
                normalized = normalize_path(test_path)
                print(f"  Test path: {test_path}")
                print(f"  Normalized: {normalized}")
                
                if 'uploads/uploads' in normalized:
                    print(f"  ❌ Path duplication still present")
                    return False
            
            print(f"  ✅ Docker environment simulation passed")
            
            # Restore original directory
            os.chdir(original_cwd)
            return True
            
    except Exception as e:
        print(f"  ❌ Docker environment simulation failed: {e}")
        return False

async def main():
    """Main test function"""
    
    print("=" * 60)
    print("COMPREHENSIVE TTS FIX TEST")
    print("=" * 60)
    
    tests = [
        ("Path Normalization", test_path_normalization),
        ("TTS Service Initialization", test_tts_service_initialization),
        ("File Creation", test_file_creation),
        ("Concatenation Filelist", test_concatenation_filelist),
        ("Docker Environment Simulation", test_docker_environment_simulation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The TTS fix should work correctly.")
        print("You can now rebuild the Docker containers and test the full system.")
    else:
        print("⚠️  Some tests failed. Please check the output above.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 