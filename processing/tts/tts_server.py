# TTS server placeholder# =============================================================================
# 🗣️ TTS SERVER - COMPLETE IMPLEMENTATION
# processing/tts/tts_server.py
# =============================================================================

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from TTS.api import TTS
import os
import tempfile
import logging
import uuid
import time
import re
from werkzeug.utils import secure_filename
import threading
from queue import Queue
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configuration
TTS_MODEL_TH = os.getenv('TTS_MODEL_TH', 'tts_models/th/mai_female/glow-tts')
TTS_MODEL_EN = os.getenv('TTS_MODEL_EN', 'tts_models/en/ljspeech/tacotron2-DDC')
TTS_MODEL_LO = os.getenv('TTS_MODEL_LO', 'tts_models/lo/lao_female/glow-tts')
DEVICE = os.getenv('TTS_DEVICE', 'cpu')
MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', '0'))  # 0 = ไม่จำกัด
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/app/output')
TEMP_DIR = os.getenv('TEMP_DIR', '/tmp')

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Global TTS models
tts_models = {}
model_loading_status = {}

def load_tts_model(model_name, language):
    """Load TTS model with error handling"""
    try:
        logger.info(f"Loading TTS model: {model_name} for language: {language}")
        model_loading_status[language] = 'loading'
        
        tts = TTS(model_name=model_name).to(DEVICE)
        tts_models[language] = tts
        model_loading_status[language] = 'loaded'
        
        logger.info(f"Successfully loaded {language} TTS model")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load TTS model {model_name}: {str(e)}")
        model_loading_status[language] = f'error: {str(e)}'
        return False

# Load models at startup
logger.info("Starting TTS models initialization...")

# Load Thai model
load_tts_model(TTS_MODEL_TH, 'th')

# Load English model (optional)
try:
    load_tts_model(TTS_MODEL_EN, 'en')
except Exception as e:
    logger.warning(f"English TTS model not loaded: {str(e)}")

# Load Lao model (optional)
try:
    load_tts_model(TTS_MODEL_LO, 'lo')
except Exception as e:
    logger.warning(f"Lao TTS model not loaded: {str(e)}")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'tts-server',
        'version': '1.0.0',
        'device': DEVICE,
        'models': {
            'thai': {
                'model': TTS_MODEL_TH,
                'status': model_loading_status.get('th', 'not_loaded'),
                'available': 'th' in tts_models
            },
            'english': {
                'model': TTS_MODEL_EN,
                'status': model_loading_status.get('en', 'not_loaded'),
                'available': 'en' in tts_models
            },
            'lao': {
                'model': TTS_MODEL_LO,
                'status': model_loading_status.get('lo', 'not_loaded'),
                'available': 'lo' in tts_models
            }
        },
        'max_text_length': MAX_TEXT_LENGTH,
        'timestamp': time.time()
    })

@app.route('/models', methods=['GET'])
def get_available_models():
    """Get list of available TTS models"""
    models = {}
    
    if 'th' in tts_models:
        models['th'] = {
            'language': 'Thai',
            'model_name': TTS_MODEL_TH,
            'voices': ['female', 'male'],
            'status': 'available'
        }
    
    if 'en' in tts_models:
        models['en'] = {
            'language': 'English',
            'model_name': TTS_MODEL_EN,
            'voices': ['female', 'male'],
            'status': 'available'
        }
    
    if 'lo' in tts_models:
        models['lo'] = {
            'language': 'Lao',
            'model_name': TTS_MODEL_LO,
            'voices': ['female', 'male'],
            'status': 'available'
        }
    
    return jsonify({
        'available_models': models,
        'total_models': len(models)
    })

def preprocess_text_for_tts(text, language='th'):
    """Preprocess text for better TTS quality"""
    # Basic cleaning
    text = text.strip()
    
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text)
    
    # Language-specific preprocessing
    if language == 'th':
        # Thai-specific processing
        text = preprocess_thai_text(text)
    elif language == 'en':
        # English-specific processing
        text = preprocess_english_text(text)
    elif language == 'lo':
        # Lao-specific processing
        text = preprocess_lao_text(text)
    
    return text

def preprocess_thai_text(text):
    """Preprocess Thai text for better TTS"""
    # Replace problematic characters
    replacements = {
        'ฯลฯ': 'และอื่นๆ',
        'ฯ': '',
        'URL': 'ยูอาร์แอล',
        'Email': 'อีเมล',
        'Facebook': 'เฟซบุ๊ก',
        'YouTube': 'ยูทูป',
        'Google': 'กูเกิล',
        'AI': 'เอไอ',
        'API': 'เอพีไอ'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Add spaces around English words in Thai text
    text = re.sub(r'([ก-๙])([A-Za-z])', r'\1 \2', text)
    text = re.sub(r'([A-Za-z])([ก-๙])', r'\1 \2', text)
    
    return text

def preprocess_english_text(text):
    """Preprocess English text for better TTS"""
    # Expand common abbreviations
    replacements = {
        'Dr.': 'Doctor',
        'Mr.': 'Mister',
        'Mrs.': 'Missus',
        'Ms.': 'Miss',
        'Prof.': 'Professor',
        'etc.': 'etcetera',
        'e.g.': 'for example',
        'i.e.': 'that is'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def preprocess_lao_text(text):
    """Preprocess Lao text for better TTS"""
    # Replace problematic characters
    replacements = {
        'ຯ': '', # Remove Lao ellipsis
        'ຯລຯ': 'ລາວອື່ນໆ', # Replace Lao ellipsis with English
        'URL': 'ຢູໄລຍາຣ໌ອລ', # Replace URL with English
        'Email': 'ອີເມລ', # Replace Email with English
        'Facebook': 'ຟີສບຸ໊ກ', # Replace Facebook with English
        'YouTube': 'ຢູໄທູປ', # Replace YouTube with English
        'Google': 'ກູເກິລ', # Replace Google with English
        'AI': 'ອາປີ', # Replace AI with English
        'API': 'ອາປີອີ' # Replace API with English
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Add spaces around English words in Lao text
    text = re.sub(r'([ກ-ຮ])([A-Za-z])', r'\1 \2', text)
    text = re.sub(r'([A-Za-z])([ກ-ຮ])', r'\1 \2', text)
    
    return text

def split_text_for_tts(text, max_length=2000):
    """Split long text into chunks for TTS processing"""
    # ถ้า max_length เป็น 0 หรือไม่จำกัด ให้ไม่แบ่ง
    if max_length == 0 or len(text) <= max_length:
        return [text]
    
    # Split by sentences
    sentences = re.split(r'[.!?။]', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

@app.route('/synthesize', methods=['POST'])
def synthesize():
    """Synthesize speech from text"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        text = data.get('text', '').strip()
        language = data.get('language', 'th')
        voice_type = data.get('voice_type', 'female')
        speed = float(data.get('speed', 1.0))
        
        # Validate input
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({
                'error': f'Text too long. Maximum length is {MAX_TEXT_LENGTH} characters'
            }), 400
        
        if language not in tts_models:
            return jsonify({
                'error': f'Language {language} not supported. Available: {list(tts_models.keys())}'
            }), 400
        
        # Preprocess text
        processed_text = preprocess_text_for_tts(text, language)
        
        # Generate unique filename
        task_id = str(uuid.uuid4())
        output_filename = f"tts_{language}_{task_id}.wav"
        output_path = os.path.join(TEMP_DIR, output_filename)
        
        logger.info(f"Synthesizing text (length: {len(processed_text)}) to {output_filename}")
        start_time = time.time()
        
        # Get TTS model
        tts_model = tts_models[language]
        
        # Synthesize speech
        tts_model.tts_to_file(
            text=processed_text,
            file_path=output_path
        )
        
        synthesis_time = time.time() - start_time
        
        # Verify output file exists
        if not os.path.exists(output_path):
            return jsonify({'error': 'Failed to generate audio file'}), 500
        
        # Get file info
        file_size = os.path.getsize(output_path)
        
        logger.info(f"TTS synthesis completed in {synthesis_time:.2f}s, file size: {file_size} bytes")
        
        return jsonify({
            'success': True,
            'audio_file': output_filename,
            'audio_path': output_path,
            'file_size': file_size,
            'text_length': len(processed_text),
            'language': language,
            'synthesis_time': round(synthesis_time, 2),
            'download_url': f'/download/{output_filename}'
        })
        
    except Exception as e:
        logger.error(f"TTS synthesis failed: {str(e)}")
        return jsonify({'error': f'Synthesis failed: {str(e)}'}), 500

@app.route('/synthesize_to_file', methods=['POST'])
def synthesize_to_file():
    """Synthesize speech directly to specified file path"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        output_path = data.get('output_path')
        language = data.get('language', 'th')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if not output_path:
            return jsonify({'error': 'No output path provided'}), 400
        
        if language not in tts_models:
            return jsonify({'error': f'Language {language} not supported'}), 400
        
        # Preprocess text
        processed_text = preprocess_text_for_tts(text, language)
        
        logger.info(f"Synthesizing text to file: {output_path}")
        
        # Get TTS model and synthesize
        tts_model = tts_models[language]
        tts_model.tts_to_file(text=processed_text, file_path=output_path)
        
        if not os.path.exists(output_path):
            return jsonify({'error': 'Failed to generate audio file'}), 500
        
        file_size = os.path.getsize(output_path)
        
        return jsonify({
            'success': True,
            'output_path': output_path,
            'file_size': file_size,
            'text_length': len(processed_text)
        })
        
    except Exception as e:
        logger.error(f"TTS synthesis to file failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/synthesize_long', methods=['POST'])
def synthesize_long():
    """Synthesize long text by splitting into chunks"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        text = data.get('text', '').strip()
        language = data.get('language', 'th')
        voice_type = data.get('voice_type', 'female')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # ตรวจสอบว่ามี model สำหรับภาษานี้หรือไม่
        if language not in tts_models:
            return jsonify({'error': f'No TTS model available for language: {language}'}), 400
        
        # ถ้าไม่จำกัดความยาว ให้สังเคราะห์ทั้งหมดในครั้งเดียว
        if MAX_TEXT_LENGTH == 0:
            return synthesize_to_file_internal(text, language, voice_type)
        
        # แบ่งข้อความเป็นชิ้นเล็กๆ
        chunks = split_text_for_tts(text, 2000)
        
        if len(chunks) == 1:
            # ข้อความสั้น ไม่ต้องแบ่ง
            return synthesize_to_file_internal(text, language, voice_type)
        
        # สังเคราะห์ทีละชิ้น
        audio_files = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Synthesizing chunk {i+1}/{len(chunks)} ({len(chunk)} characters)")
            
            # สังเคราะห์เสียงสำหรับ chunk นี้
            chunk_result = synthesize_to_file_internal(chunk, language, voice_type)
            
            if chunk_result and 'filename' in chunk_result:
                audio_files.append(chunk_result['filename'])
            else:
                logger.error(f"Failed to synthesize chunk {i+1}")
                return jsonify({'error': f'Failed to synthesize chunk {i+1}'}), 500
        
        # รวมไฟล์เสียง
        if len(audio_files) > 1:
            final_filename = f"combined_{uuid.uuid4().hex}.wav"
            final_path = os.path.join(OUTPUT_DIR, final_filename)
            
            concatenate_audio_files(audio_files, final_path)
            
            # ลบไฟล์ชั่วคราว
            for temp_file in audio_files:
                try:
                    os.remove(os.path.join(OUTPUT_DIR, temp_file))
                except:
                    pass
            
            return jsonify({
                'success': True,
                'filename': final_filename,
                'message': f'Synthesized {len(chunks)} chunks successfully',
                'total_chunks': len(chunks)
            })
        else:
            # มีแค่ไฟล์เดียว
            return jsonify({
                'success': True,
                'filename': audio_files[0],
                'message': 'Synthesized successfully',
                'total_chunks': 1
            })
        
    except Exception as e:
        logger.error(f"Error in synthesize_long: {str(e)}")
        return jsonify({'error': str(e)}), 500

def concatenate_audio_files(file_list, output_path):
    """Concatenate audio files using FFmpeg"""
    try:
        # Create temporary file list for FFmpeg
        filelist_path = os.path.join(TEMP_DIR, f"filelist_{uuid.uuid4().hex}.txt")
        
        with open(filelist_path, 'w') as f:
            for audio_file in file_list:
                f.write(f"file '{audio_file}'\n")
        
        # FFmpeg command
        cmd = [
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', filelist_path, '-c', 'copy', '-y', output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up filelist
        try:
            os.remove(filelist_path)
        except:
            pass
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Audio concatenation failed: {str(e)}")
        return False

@app.route('/download/<filename>', methods=['GET'])
def download_audio(filename):
    """Download generated audio file"""
    try:
        # Secure filename
        filename = secure_filename(filename)
        file_path = os.path.join(TEMP_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='audio/wav'
        )
        
    except Exception as e:
        logger.error(f"File download failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Clean up old temporary files"""
    try:
        data = request.get_json()
        max_age_hours = data.get('max_age_hours', 24)
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0
        
        for filename in os.listdir(TEMP_DIR):
            if filename.startswith('tts_'):
                file_path = os.path.join(TEMP_DIR, filename)
                file_age = current_time - os.path.getctime(file_path)
                
                if file_age > max_age_seconds:
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                    except:
                        pass
        
        return jsonify({
            'success': True,
            'cleaned_files': cleaned_count,
            'max_age_hours': max_age_hours
        })
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

# =============================================================================
# 🌐 TRANSLATION SERVER - COMPLETE IMPLEMENTATION  
# processing/translation/translation_server.py
# =============================================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging
import time
import re
from langdetect import detect, LangDetectError
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configuration
LIBRETRANSLATE_URL = os.getenv('LIBRETRANSLATE_URL', 'http://localhost:5000')
API_KEY = os.getenv('LIBRETRANSLATE_API_KEY', '')
MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', '5000'))
MAX_CHUNK_SIZE = int(os.getenv('MAX_CHUNK_SIZE', '1000'))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))

# Supported languages
SUPPORTED_LANGUAGES = {
    'auto': 'Auto-detect',
    'en': 'English',
    'th': 'Thai',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ar': 'Arabic',
    'hi': 'Hindi'
}

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Test connection to LibreTranslate
        response = requests.get(
            f"{LIBRETRANSLATE_URL}/languages",
            timeout=5
        )
        
        libretranslate_status = 'connected' if response.status_code == 200 else 'disconnected'
        
        return jsonify({
            'status': 'healthy',
            'service': 'translation-server',
            'version': '1.0.0',
            'libretranslate_url': LIBRETRANSLATE_URL,
            'libretranslate_status': libretranslate_status,
            'api_key_configured': bool(API_KEY),
            'max_text_length': MAX_TEXT_LENGTH,
            'supported_languages': len(SUPPORTED_LANGUAGES),
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'libretranslate_status': 'error'
        }), 503

@app.route('/languages', methods=['GET'])
def get_languages():
    """Get supported languages from LibreTranslate"""
    try:
        response = requests.get(
            f"{LIBRETRANSLATE_URL}/languages",
            timeout=10
        )
        
        if response.status_code != 200:
            # Return default languages if LibreTranslate is unavailable
            return jsonify({
                'languages': SUPPORTED_LANGUAGES,
                'source': 'default'
            })
        
        # Parse LibreTranslate response
        languages = response.json()
        language_dict = {lang['code']: lang['name'] for lang in languages}
        
        return jsonify({
            'languages': language_dict,
            'source': 'libretranslate',
            'total': len(language_dict)
        })
        
    except Exception as e:
        logger.error(f"Failed to get languages: {str(e)}")
        return jsonify({
            'languages': SUPPORTED_LANGUAGES,
            'source': 'default',
            'error': str(e)
        })

def preprocess_text(text):
    """Preprocess text for better translation"""
    # Basic cleaning
    text = text.strip()
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove problematic characters but preserve structure
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    return text

def postprocess_translation(text, target_language):
    """Post-process translated text"""
    text = text.strip()
    
    # Language-specific post-processing
    if target_language == 'th':
        text = postprocess_thai_translation(text)
    
    return text

def postprocess_thai_translation(text):
    """Post-process Thai translation"""
    # Fix spacing around Thai characters
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common Thai translation issues
    replacements = {
        ' ๆ': 'ๆ',
        ' ฯ': 'ฯ',
        ' ์': '์',
        ' ็': '็',
        ' ่': '่',
        ' ้': '้',
        ' ๊': '๊',
        ' ๋': '๋'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def split_text_for_translation(text, max_length=1000):
    """Split long text into chunks for translation"""
    if len(text) <= max_length:
        return [text]
    
    # Split by sentences first
    sentences = re.split(r'[.!?।]', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
            else:
                # Sentence is too long, split by commas or phrases
                phrases = re.split(r'[,;:]', sentence)
                for phrase in phrases:
                    phrase = phrase.strip()
                    if phrase:
                        if len(current_chunk) + len(phrase) <= max_length:
                            current_chunk += phrase + ", "
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = phrase + ", "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

@app.route('/detect', methods=['POST'])
def detect_language():
    """Detect language of input text"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Try local detection first
        try:
            detected_lang = detect(text)
            confidence = 0.9  # langdetect doesn't provide confidence
        except LangDetectError:
            detected_lang = 'unknown'
            confidence = 0.0
        
        # Try LibreTranslate detection as fallback/verification
        try:
            detect_data = {'q': text[:500]}  # Limit text for detection
            if API_KEY:
                detect_data['api_key'] = API_KEY
            
            response = requests.post(
                f"{LIBRETRANSLATE_URL}/detect",
                json=detect_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result:
                    libretranslate_lang = result[0]['language']
                    libretranslate_confidence = result[0]['confidence']
                    
                    # Use LibreTranslate result if confidence is higher
                    if libretranslate_confidence > confidence:
                        detected_lang = libretranslate_lang
                        confidence = libretranslate_confidence
        
        except Exception as e:
            logger.warning(f"LibreTranslate detection failed: {str(e)}")
        
        return jsonify({
            'detected_language': detected_lang,
            'confidence': confidence,
            'text_length': len(text)
        })
        
    except Exception as e:
        logger.error(f"Language detection failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/translate', methods=['POST'])
def translate():
    """Translate text"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'th')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({
                'error': f'Text too long. Maximum length is {MAX_TEXT_LENGTH} characters'
            }), 400
        
        logger.info(f"Translating text from {source_lang} to {target_lang} (length: {len(text)})")
        
        # Preprocess text
        processed_text = preprocess_text(text)
        
        # Handle long text by splitting into chunks
        if len(processed_text) > MAX_CHUNK_SIZE:
            return translate_long_text(processed_text, source_lang, target_lang)
        
        # Translate single chunk
        translated_text = translate_chunk(processed_text, source_lang, target_lang)
        
        # Post-process translation
        final_translation = postprocess_translation(translated_text, target_lang)
        
        return jsonify({
            'translated_text': final_translation,
            'source_language': source_lang,
            'target_language': target_lang,
            'original_length': len(text),
            'translated_length': len(final_translation),
            'processing_method': 'single_chunk'
        })
        
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

def translate_chunk(text, source_lang, target_lang):
    """Translate a single chunk of text"""
    try:
        # Prepare request data
        translate_data = {
            'q': text,
            'source': source_lang,
            'target': target_lang,
            'format': 'text'
        }
        
        if API_KEY:
            translate_data['api_key'] = API_KEY
        
        # Make translation request
        response = requests.post(
            f"{LIBRETRANSLATE_URL}/translate",
            json=translate_data,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            logger.error(f"Translation API error {response.status_code}: {response.text}")
            raise Exception(f"Translation service error: {response.status_code}")
        
        result = response.json()
        translated_text = result.get('translatedText', '')
        
        if not translated_text:
            raise Exception("Empty translation result")
        
        return translated_text
        
    except requests.RequestException as e:
        logger.error(f"Translation request failed: {str(e)}")
        raise Exception(f"Translation service unavailable: {str(e)}")

def translate_long_text(text, source_lang, target_lang):
    """Translate long text by splitting into chunks"""
    try:
        logger.info("Translating long text in chunks")
        
        # Split text into chunks
        chunks = split_text_for_translation(text, MAX_CHUNK_SIZE)
        translated_chunks = []
        
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                logger.info(f"Translating chunk {i+1}/{len(chunks)}")
                translated_chunk = translate_chunk(chunk, source_lang, target_lang)
                translated_chunks.append(translated_chunk)
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.5)
        
        # Join translated chunks
        final_translation = " ".join(translated_chunks)
        final_translation = postprocess_translation(final_translation, target_lang)
        
        return jsonify({
            'translated_text': final_translation,
            'source_language': source_lang,
            'target_language': target_lang,
            'original_length': len(text),
            'translated_length': len(final_translation),
            'chunks_processed': len(translated_chunks),
            'processing_method': 'multi_chunk'
        })
        
    except Exception as e:
        logger.error(f"Long text translation failed: {str(e)}")
        raise

@app.route('/translate_batch', methods=['POST'])
def translate_batch():
    """Translate multiple texts in batch"""
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'th')
        
        if not texts or not isinstance(texts, list):
            return jsonify({'error': 'No texts provided or invalid format'}), 400
        
        if len(texts) > 100:
            return jsonify({'error': 'Too many texts. Maximum 100 texts per batch'}), 400
        
        logger.info(f"Batch translating {len(texts)} texts")
        
        results = []
        failed_count = 0
        
        for i, text in enumerate(texts):
            try:
                if not text or not text.strip():
                    results.append({
                        'index': i,
                        'success': False,
                        'error': 'Empty text',
                        'translated_text': ''
                    })
                    failed_count += 1
                    continue
                
                # Preprocess and translate
                processed_text = preprocess_text(text.strip())
                translated_text = translate_chunk(processed_text, source_lang, target_lang)
                final_translation = postprocess_translation(translated_text, target_lang)
                
                results.append({
                    'index': i,
                    'success': True,
                    'original_text': text,
                    'translated_text': final_translation,
                    'original_length': len(text),
                    'translated_length': len(final_translation)
                })
                
                # Small delay between requests
                time.sleep(0.2)
                
            except Exception as e:
                logger.error(f"Failed to translate text {i}: {str(e)}")
                results.append({
                    'index': i,
                    'success': False,
                    'error': str(e),
                    'original_text': text,
                    'translated_text': ''
                })
                failed_count += 1
        
        return jsonify({
            'results': results,
            'total_texts': len(texts),
            'successful': len(texts) - failed_count,
            'failed': failed_count,
            'source_language': source_lang,
            'target_language': target_lang
        })
        
    except Exception as e:
        logger.error(f"Batch translation failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/translate_with_context', methods=['POST'])
def translate_with_context():
    """Translate text with additional context for better accuracy"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        context = data.get('context', '').strip()
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'th')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Prepare context-aware text
        if context:
            contextual_text = f"Context: {context}\n\nTranslate: {text}"
        else:
            contextual_text = text
        
        logger.info(f"Context-aware translation: {len(text)} chars with {len(context)} chars context")
        
        # Translate with context
        translated_result = translate_chunk(contextual_text, source_lang, target_lang)
        
        # Extract actual translation (remove context if translated)
        if context and "Context:" in translated_result:
            lines = translated_result.split('\n')
            for line in lines:
                if line.strip() and not line.lower().startswith('context'):
                    translated_text = line.strip()
                    break
            else:
                translated_text = translated_result
        else:
            translated_text = translated_result
        
        # Post-process
        final_translation = postprocess_translation(translated_text, target_lang)
        
        return jsonify({
            'translated_text': final_translation,
            'source_language': source_lang,
            'target_language': target_lang,
            'context_used': bool(context),
            'original_length': len(text),
            'translated_length': len(final_translation)
        })
        
    except Exception as e:
        logger.error(f"Context-aware translation failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/quality_check', methods=['POST'])
def quality_check():
    """Check translation quality by back-translation"""
    try:
        data = request.get_json()
        original_text = data.get('original_text', '').strip()
        translated_text = data.get('translated_text', '').strip()
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'th')
        
        if not original_text or not translated_text:
            return jsonify({'error': 'Both original and translated text required'}), 400
        
        logger.info("Performing translation quality check")
        
        # Back-translate
        back_translated = translate_chunk(translated_text, target_lang, source_lang)
        
        # Simple quality metrics
        original_words = len(original_text.split())
        translated_words = len(translated_text.split())
        back_translated_words = len(back_translated.split())
        
        # Length ratio
        length_ratio = len(translated_text) / len(original_text) if len(original_text) > 0 else 0
        
        # Word count ratio
        word_ratio = translated_words / original_words if original_words > 0 else 0
        
        # Back-translation similarity (simple)
        similarity_score = calculate_text_similarity(original_text.lower(), back_translated.lower())
        
        # Quality assessment
        quality_score = (similarity_score + min(1.0, word_ratio) + min(1.0, length_ratio)) / 3
        
        if quality_score > 0.8:
            quality_rating = 'excellent'
        elif quality_score > 0.6:
            quality_rating = 'good'
        elif quality_score > 0.4:
            quality_rating = 'fair'
        else:
            quality_rating = 'poor'
        
        return jsonify({
            'quality_score': round(quality_score, 3),
            'quality_rating': quality_rating,
            'back_translation': back_translated,
            'similarity_score': round(similarity_score, 3),
            'length_ratio': round(length_ratio, 3),
            'word_ratio': round(word_ratio, 3),
            'metrics': {
                'original_words': original_words,
                'translated_words': translated_words,
                'back_translated_words': back_translated_words,
                'original_length': len(original_text),
                'translated_length': len(translated_text)
            }
        })
        
    except Exception as e:
        logger.error(f"Quality check failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

def calculate_text_similarity(text1, text2):
    """Calculate simple text similarity"""
    try:
        # Simple word overlap similarity
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
        
    except Exception:
        return 0.0

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get translation service statistics"""
    try:
        # Mock statistics - in production, you'd track these
        stats = {
            'service_uptime': time.time(),
            'total_translations': 0,  # Would track in database
            'successful_translations': 0,
            'failed_translations': 0,
            'average_response_time': 0.5,
            'supported_languages': len(SUPPORTED_LANGUAGES),
            'most_requested_language_pairs': [
                {'source': 'en', 'target': 'th', 'count': 0},
                {'source': 'auto', 'target': 'th', 'count': 0}
            ],
            'current_load': 'low',  # low, medium, high
            'api_status': 'healthy'
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

@app.errorhandler(503)
def service_unavailable(error):
    return jsonify({'error': 'Service unavailable', 'message': str(error)}), 503

# =============================================================================
# 🚀 MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    # TTS Server
    if 'tts_server.py' in __file__:
        logger.info("Starting TTS Server...")
        logger.info(f"Device: {DEVICE}")
        logger.info(f"Thai Model: {TTS_MODEL_TH}")
        logger.info(f"Max text length: {MAX_TEXT_LENGTH}")
        app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
    
    # Translation Server  
    elif 'translation_server.py' in __file__:
        logger.info("Starting Translation Server...")
        logger.info(f"LibreTranslate URL: {LIBRETRANSLATE_URL}")
        logger.info(f"API Key configured: {bool(API_KEY)}")
        logger.info(f"Max text length: {MAX_TEXT_LENGTH}")
        app.run(host='0.0.0.0', port=5003, debug=False, threaded=True)

# =============================================================================
# 📋 ADDITIONAL UTILITIES AND CONFIGURATIONS
# =============================================================================

# processing/tts/config.py
TTS_CONFIG = {
    'models': {
        'th': {
            'female': 'tts_models/th/mai_female/glow-tts',
            'male': 'tts_models/th/mai_male/glow-tts'
        },
        'en': {
            'female': 'tts_models/en/ljspeech/tacotron2-DDC',
            'male': 'tts_models/en/sam/tacotron-DDC'
        }
    },
    'audio_settings': {
        'sample_rate': 22050,
        'channels': 1,
        'format': 'wav',
        'bitrate': '128k'
    },
    'processing': {
        'max_text_length': 1000,
        'chunk_size': 800,
        'synthesis_timeout': 120
    }
}

# processing/translation/config.py
TRANSLATION_CONFIG = {
    'services': {
        'primary': 'libretranslate',
        'fallback': 'google_translate'
    },
    'api_settings': {
        'timeout': 30,
        'max_retries': 3,
        'rate_limit': '100/hour'
    },
    'text_processing': {
        'max_length': 5000,
        'chunk_size': 1000,
        'preserve_formatting': True
    },
    'quality': {
        'enable_back_translation': True,
        'similarity_threshold': 0.6,
        'confidence_threshold': 0.7
    }
}

# processing/utils/audio_utils.py
def optimize_audio_for_web(input_path, output_path):
    """Optimize audio file for web delivery"""
    try:
        cmd = [
            'ffmpeg', '-i', input_path,
            '-acodec', 'aac', '-b:a', '128k',
            '-ar', '44100', '-ac', '2',
            '-y', output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Audio optimization failed: {str(e)}")
        return False

# processing/utils/text_utils.py
def clean_text_for_processing(text, language='th'):
    """Clean text for better processing"""
    # Remove problematic characters
    text = re.sub(r'[^\w\s\u0E00-\u0E7F.,!?]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Language-specific cleaning
    if language == 'th':
        # Thai-specific cleaning
        text = re.sub(r'([ก-๙])\s+([ก-๙])', r'\1\2', text)
    
    return text.strip()

# Docker configurations would be in their respective Dockerfiles as shown in previous artifacts