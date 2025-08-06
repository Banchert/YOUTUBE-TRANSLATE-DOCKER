# TTS Audio Concatenation Fix

## Problem Description

The TTS service was failing with the following error during audio concatenation:

```
Failed to convert text to speech: Audio concatenation failed: ffmpeg version 5.1.6-0+deb12u1 Copyright (c) 2000-2024 the FFmpeg developers built with gcc 12 (Debian 12.2.0-14) configuration: --prefix=/usr --extra-version=0+deb12u1 --toolchain=hardened --libdir=/usr/lib/x86_64-linux-gnu --incdir=/usr/include/x86_64-linux-gnu --arch=amd64 --enable-gpl --disable-stripping --enable-gnutls --enable-ladspa --enable-libaom --enable-libass --enable-libbluray --enable-libbs2b --enable-libcaca --enable-libcdio --enable-libcodec2 --enable-libdav1d --enable-libflite --enable-libfontconfig --enable-libfreetype --enable-libfribidi --enable-libglslang --enable-libgme --enable-libgsm --enable-libjack --enable-libmp3lame --enable-libmysofa --enable-libopenjpeg --enable-libopenmpt --enable-libopus --enable-libpulse --enable-librabbitmq --enable-librist --enable-librubberband --enable-libshine --enable-libsnappy --enable-libsoxr --enable-libspeex --enable-libsrt --enable-libssh --enable-libsvtav1 --enable-libtheora --enable-libtwolame --enable-libvidstab --enable-libvorbis --enable-libvpx --enable-libwebp --enable-libx265 --enable-libxml2 --enable-libxvid --enable-libzimg --enable-libzmq --enable-libzvbi --enable-lv2 --enable-omx --enable-openal --enable-opencl --enable-opengl --enable-sdl2 --disable-sndio --enable-libjxl --enable-pocketsphinx --enable-librsvg --enable-libmfx --enable-libdc1394 --enable-libdrm --enable-libiec61883 --enable-chromaprint --enable-frei0r --enable-libx264 --enable-libplacebo --enable-librav1e --enable-shared libavutil 57. 28.100 / 57. 28.100 libavcodec 59. 37.100 / 59. 37.100 libavformat 59. 27.100 / 59. 27.100 libavdevice 59. 7.100 / 59. 7.100 libavfilter 8. 44.100 / 8. 44.100 libswscale 6. 7.100 / 6. 7.100 libswresample 4. 7.100 / 4. 7.100 libpostproc 56. 6.100 / 56. 6.100 [concat @ 0x5ed614c4c880] Impossible to open 'uploads/uploads/optimized_audio_5509946c-5845-4877-990a-c56ffa57dfc8_chunk_0.wav' uploads/filelist_5509946c-5845-4877-990a-c56ffa57dfc8.txt: No such file or directory
```

The key issue was the path duplication: `uploads/uploads/...` instead of `uploads/...`

## Root Cause

The problem was in the `_concatenate_audio_files` method in `backend/app/services/tts_service.py`. When creating the filelist for FFmpeg, the code was writing relative paths that could become ambiguous when running in Docker containers where the working directory might already be inside an "uploads" directory.

## Fixes Applied

### 1. Path Normalization Function

**File:** `backend/app/services/tts_service.py`
**New Function:** `normalize_path()`

Added a robust path normalization function that handles path duplication issues:

```python
def normalize_path(path):
    """
    Normalize a path to avoid duplication issues, especially in Docker environments
    """
    # Convert to absolute path
    abs_path = os.path.abspath(path)
    
    # Split the path
    path_parts = abs_path.split(os.sep)
    
    # Remove any duplicate 'uploads' entries
    if 'uploads' in path_parts:
        uploads_indices = [i for i, part in enumerate(path_parts) if part == 'uploads']
        if len(uploads_indices) > 1:
            # Keep only the first 'uploads' entry
            first_uploads = uploads_indices[0]
            cleaned_parts = path_parts[:first_uploads + 1] + [p for p in path_parts[first_uploads + 1:] if p != 'uploads']
            return os.sep.join(cleaned_parts)
    
    return abs_path
```

### 2. Use Normalized Paths in FFmpeg Filelist

**File:** `backend/app/services/tts_service.py`
**Method:** `_concatenate_audio_files`

**Before:**
```python
with open(filelist_path, 'w') as f:
    for audio_file in audio_files:
        f.write(f"file '{audio_file}'\n")
```

**After:**
```python
with open(filelist_path, 'w') as f:
    for audio_file in audio_files:
        # Use normalized paths to avoid duplication issues
        normalized_audio_file = normalize_path(audio_file)
        logger.info(f"Normalized path: {audio_file} -> {normalized_audio_file}")
        f.write(f"file '{normalized_audio_file}'\n")
```

### 2. Enhanced Error Handling and Validation

Added comprehensive validation and logging:

- **File existence validation:** Check that all audio files exist before concatenation
- **Path logging:** Log all file paths for debugging
- **Filelist content logging:** Log the actual content of the FFmpeg filelist
- **FFmpeg command logging:** Log the complete FFmpeg command being executed
- **Output validation:** Verify that the output file was actually created

### 3. Improved Chunk File Validation

**Method:** `_synthesize_long_text`

Added validation to ensure chunk audio files are properly created before attempting concatenation:

```python
# Validate that the chunk audio file was created
if not os.path.exists(chunk_audio):
    raise Exception(f"Chunk audio file was not created: {chunk_audio}")

logger.info(f"Created chunk audio file: {chunk_audio}")
```

### 4. Enhanced Cleanup Method

**Method:** `cleanup_tts_files`

Fixed the chunk file pattern matching to properly clean up all generated files:

```python
# Clean up optimized chunk files
chunk_pattern = f"optimized_audio_{task_id}_chunk_*.wav"

# Clean up original chunk files (before optimization)
original_chunk_pattern = f"thai_audio_{task_id}_chunk_*.wav"
```

### 5. Additional Logging

Added comprehensive logging throughout the TTS service:

- Directory path logging during initialization
- Audio optimization path logging
- TTS synthesis completion logging
- Detailed error logging with FFmpeg output

## Testing

Multiple test scripts have been created to verify the fixes:

### 1. Basic TTS Test
```bash
python test_tts_fix.py
# or
test_tts_fix.bat
```

### 2. Comprehensive Test
```bash
python test_tts_comprehensive.py
# or
test_tts_comprehensive.bat
```

### 3. Path Debug Test
```bash
python debug_tts_paths.py
# or
debug_tts_paths.bat
```

### 4. Docker Rebuild
```bash
rebuild_tts_fix.bat
```

## Test Coverage

The comprehensive test script covers:
1. **Path Normalization**: Tests the `normalize_path()` function with various path scenarios
2. **TTS Service Initialization**: Verifies service starts correctly
3. **File Creation**: Tests file creation in uploads directory
4. **Concatenation Filelist**: Tests filelist creation without path duplication
5. **Docker Environment Simulation**: Simulates Docker environment paths

## Files Modified

1. `backend/app/services/tts_service.py` - Main TTS service with comprehensive fixes
2. `test_tts_fix.py` - Basic test script to verify fixes
3. `test_tts_fix.bat` - Windows batch file to run basic tests
4. `test_tts_comprehensive.py` - Comprehensive test script
5. `test_tts_comprehensive.bat` - Windows batch file to run comprehensive tests
6. `debug_tts_paths.py` - Path debugging script
7. `debug_tts_paths.bat` - Windows batch file to run path debug
8. `rebuild_tts_fix.bat` - Docker rebuild script
9. `TTS-FIX-README.md` - This documentation

## Expected Results

After applying these fixes:

1. ✅ Audio concatenation should work without path errors
2. ✅ Long text TTS should properly chunk and concatenate audio files
3. ✅ All temporary files should be properly cleaned up
4. ✅ Detailed logging should help identify any remaining issues
5. ✅ FFmpeg should receive correct absolute paths for all audio files

## Verification

To verify the fix is working:

1. Run the test script: `python test_tts_fix.py`
2. Check the logs for any path-related errors
3. Verify that audio files are created in the correct locations
4. Confirm that FFmpeg receives proper absolute paths in the filelist

The fix ensures that FFmpeg always receives absolute paths, eliminating the path duplication issue that was causing the concatenation to fail. 