#!/usr/bin/env python3
"""
Script to fix TTS dynamic rate integration in main.py
"""
import re

def fix_main_py():
    """Fix main.py to use dynamic speech rate for TTS"""
    
    file_path = "backend/app/main.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find text_to_speech calls
    old_pattern = r'thai_audio_path = await tts_service\.text_to_speech\(translated_text, task_id\)'
    
    # New replacement with dynamic speech rate
    new_code = '''# Get speech rate info from task data if available  
        task_data = tasks[task_id]
        speech_rate_info = task_data.get('speech_rate_info')
        thai_audio_path = await tts_service.text_to_speech(translated_text, task_id, speech_rate_info=speech_rate_info)'''
    
    # Replace all occurrences
    updated_content = re.sub(old_pattern, new_code, content)
    
    # Count replacements
    count = len(re.findall(old_pattern, content))
    
    if count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"✅ Updated {count} TTS calls in {file_path}")
    else:
        print(f"❌ No TTS calls found to update in {file_path}")

def fix_tts_service_py():
    """Fix TTS service signature"""
    
    file_path = "backend/app/services/tts_service.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already fixed
    if 'speech_rate_info: Optional[Dict[str, Any]] = None' in content:
        print(f"✅ {file_path} already updated")
        return
    
    print(f"❌ {file_path} needs manual update")

if __name__ == "__main__":
    print("🔧 Fixing TTS dynamic rate integration...")
    fix_main_py()
    fix_tts_service_py()
    print("✅ Fix completed!")
