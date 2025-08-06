#!/usr/bin/env python3
"""
Debug script to check TTS paths and working directory
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.config import settings

def debug_paths():
    """Debug the current paths and working directory"""
    
    print("=" * 60)
    print("TTS PATH DEBUG")
    print("=" * 60)
    
    print(f"Current working directory: {os.getcwd()}")
    print(f"Current working directory (absolute): {os.path.abspath(os.getcwd())}")
    
    print(f"\nSettings:")
    print(f"UPLOAD_DIR: {settings.UPLOAD_DIR}")
    print(f"OUTPUT_DIR: {settings.OUTPUT_DIR}")
    
    print(f"\nPath resolution:")
    print(f"UPLOAD_DIR (absolute): {os.path.abspath(settings.UPLOAD_DIR)}")
    print(f"OUTPUT_DIR (absolute): {os.path.abspath(settings.OUTPUT_DIR)}")
    
    print(f"\nDirectory existence:")
    print(f"UPLOAD_DIR exists: {os.path.exists(settings.UPLOAD_DIR)}")
    print(f"OUTPUT_DIR exists: {os.path.exists(settings.OUTPUT_DIR)}")
    
    print(f"\nEnvironment variables:")
    print(f"PWD: {os.environ.get('PWD', 'Not set')}")
    print(f"WORKDIR: {os.environ.get('WORKDIR', 'Not set')}")
    
    print(f"\nTest path construction:")
    test_task_id = "test_debug_123"
    test_path = os.path.join(settings.UPLOAD_DIR, f"optimized_audio_{test_task_id}.wav")
    print(f"Test path: {test_path}")
    print(f"Test path (absolute): {os.path.abspath(test_path)}")
    
    # Check if there are any existing files in uploads
    if os.path.exists(settings.UPLOAD_DIR):
        print(f"\nFiles in UPLOAD_DIR:")
        try:
            files = os.listdir(settings.UPLOAD_DIR)
            for file in files[:10]:  # Show first 10 files
                file_path = os.path.join(settings.UPLOAD_DIR, file)
                print(f"  {file} -> {os.path.abspath(file_path)}")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files")
        except Exception as e:
            print(f"  Error listing files: {e}")
    
    print("=" * 60)

if __name__ == "__main__":
    debug_paths() 