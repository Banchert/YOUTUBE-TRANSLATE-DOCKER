#!/usr/bin/env python3
import sys
import re

def update_main_py():
    """Update main.py to use dynamic speech rate"""
    
    with open('backend/app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match the TTS call
    pattern = r'thai_audio_path = await tts_service\.text_to_speech\(translated_text, task_id\)'
    
    # Replacement with dynamic speech rate
    replacement = '''# Get speech rate info from task data if available  
        task_data = tasks[task_id]
        speech_rate_info = task_data.get('speech_rate_info')
        thai_audio_path = await tts_service.text_to_speech(translated_text, task_id, speech_rate_info=speech_rate_info)'''
    
    # Count matches
    matches = re.findall(pattern, content)
    print(f"Found {len(matches)} TTS calls to update")
    
    if matches:
        # Replace all occurrences
        updated_content = re.sub(pattern, replacement, content)
        
        # Write back
        with open('backend/app/main.py', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Successfully updated main.py")
    else:
        print("❌ No TTS calls found to update")

if __name__ == "__main__":
    update_main_py()
