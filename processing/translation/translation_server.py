# Translation server placeholder# =============================================================================
# 🌐 TRANSLATION SERVER - COMPLETE STANDALONE IMPLEMENTATION
# processing/translation/translation_server.py
# =============================================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging
import time
import re
import json
from functools import wraps
import threading
from queue import Queue
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/translation.log') if os.path.exists('/app/logs') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app, origins=['*'])

# =============================================================================
# 📋 CONFIGURATION
# =============================================================================

# LibreTranslate Configuration
LIBRETRANSLATE_URL = os.getenv('LIBRETRANSLATE_URL', 'http://libretranslate:5000')
API_KEY = os.getenv('LIBRETRANSLATE_API_KEY', '')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# Text Processing Configuration
MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', '0'))  # 0 = ไม่จำกัด
MAX_CHUNK_SIZE = int(os.getenv('MAX_CHUNK_SIZE', '5000'))  # เพิ่มขนาด chunk
MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', '200'))   # เพิ่ม batch size

# Performance Configuration
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'

# Supported Languages
SUPPORTED_LANGUAGES = {
    'auto': 'Auto-detect',
    'en': 'English',
    'th': 'Thai (ไทย)',
    'zh': 'Chinese (中文)',
    'ja': 'Japanese (日本語)',
    'ko': 'Korean (한국어)',
    'vi': 'Vietnamese (Tiếng Việt)',
    'id': 'Indonesian (Bahasa Indonesia)',
    'ms': 'Malay (Bahasa Melayu)',
    'lo': 'Lao (ລາວ)',
    'es': 'Spanish (Español)',
    'fr': 'French (Français)',
    'de': 'German (Deutsch)',
    'it': 'Italian (Italiano)',
    'pt': 'Portuguese (Português)',
    'ru': 'Russian (Русский)',
    'ar': 'Arabic (العربية)',
    'hi': 'Hindi (हिन्दी)',
    'tr': 'Turkish (Türkçe)',
    'pl': 'Polish (Polski)',
    'nl': 'Dutch (Nederlands)',
    'sv': 'Swedish (Svenska)',
    'da': 'Danish (Dansk)',
    'no': 'Norwegian (Norsk)',
    'fi': 'Finnish (Suomi)',
    'cs': 'Czech (Čeština)',
    'sk': 'Slovak (Slovenčina)',
    'hu': 'Hungarian (Magyar)',
    'ro': 'Romanian (Română)',
    'bg': 'Bulgarian (Български)',
    'hr': 'Croatian (Hrvatski)',
    'sr': 'Serbian (Српски)',
    'sl': 'Slovenian (Slovenščina)',
    'et': 'Estonian (Eesti)',
    'lv': 'Latvian (Latviešu)',
    'lt': 'Lithuanian (Lietuvių)',
    'mt': 'Maltese (Malti)',
    'cy': 'Welsh (Cymraeg)',
    'ga': 'Irish (Gaeilge)',
    'eu': 'Basque (Euskera)',
    'ca': 'Catalan (Català)',
    'gl': 'Galician (Galego)',
    'oc': 'Occitan',
    'br': 'Breton (Brezhoneg)',
    'is': 'Icelandic (Íslenska)',
    'mk': 'Macedonian (Македонски)',
    'sq': 'Albanian (Shqip)',
    'be': 'Belarusian (Беларуская)',
    'uk': 'Ukrainian (Українська)',
    'he': 'Hebrew (עברית)',
    'fa': 'Persian (فارسی)',
    'ur': 'Urdu (اردو)',
    'bn': 'Bengali (বাংলা)',
    'ta': 'Tamil (தமிழ்)',
    'te': 'Telugu (తెలుగు)',
    'ml': 'Malayalam (മലയാളം)',
    'kn': 'Kannada (ಕನ್ನಡ)',
    'gu': 'Gujarati (ગુજરાતી)',
    'pa': 'Punjabi (ਪੰਜਾਬੀ)',
    'or': 'Odia (ଓଡ଼ିଆ)',
    'as': 'Assamese (অসমীয়া)',
    'ne': 'Nepali (नेपाली)',
    'si': 'Sinhala (සිංහල)',
    'my': 'Myanmar (မြန်မာ)',
    'km': 'Khmer (ខ្មែរ)',
    'ka': 'Georgian (ქართული)',
    'am': 'Amharic (አማርኛ)',
    'ti': 'Tigrinya (ትግርኛ)',
    'sw': 'Swahili (Kiswahili)',
    'zu': 'Zulu (isiZulu)',
    'af': 'Afrikaans',
    'xh': 'Xhosa (isiXhosa)',
    'st': 'Sesotho',
    'tn': 'Setswana',
    'ss': 'Siswati',
    've': 'Venda (Tshivenḓa)',
    'ts': 'Tsonga (Xitsonga)',
    'nr': 'Ndebele (isiNdebele)',
    'nso': 'Northern Sotho'
}

# =============================================================================
# 🧠 GLOBAL VARIABLES AND CACHE
# =============================================================================

# Simple in-memory cache
translation_cache = {}
cache_timestamps = {}
request_stats = {
    'total_requests': 0,
    'successful_translations': 0,
    'failed_translations': 0,
    'cache_hits': 0,
    'average_response_time': 0,
    'language_pairs': {}
}

# Thread-safe lock for stats
stats_lock = threading.Lock()

# =============================================================================
# 🛠️ UTILITY FUNCTIONS
# =============================================================================

def generate_cache_key(text, source_lang, target_lang):
    """Generate cache key for translation"""
    content = f"{text}:{source_lang}:{target_lang}"
    return hashlib.md5(content.encode()).hexdigest()

def is_cache_valid(timestamp):
    """Check if cache entry is still valid"""
    return time.time() - timestamp < CACHE_TTL

def update_stats(success=True, response_time=0, source_lang='', target_lang=''):
    """Update request statistics"""
    with stats_lock:
        request_stats['total_requests'] += 1
        
        if success:
            request_stats['successful_translations'] += 1
        else:
            request_stats['failed_translations'] += 1
        
        # Update average response time
        total_time = request_stats['average_response_time'] * (request_stats['total_requests'] - 1)
        request_stats['average_response_time'] = (total_time + response_time) / request_stats['total_requests']
        
        # Update language pair stats
        if source_lang and target_lang:
            pair_key = f"{source_lang}->{target_lang}"
            request_stats['language_pairs'][pair_key] = request_stats['language_pairs'].get(pair_key, 0) + 1

def preprocess_text(text):
    """Preprocess text for better translation quality"""
    if not text:
        return ""
    
    # Basic cleaning
    text = text.strip()
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize line breaks
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Remove or replace problematic characters
    text = text.replace('\u00a0', ' ')  # Non-breaking space
    text = text.replace('\u2000', ' ')  # En quad
    text = text.replace('\u2001', ' ')  # Em quad
    text = text.replace('\u2002', ' ')  # En space
    text = text.replace('\u2003', ' ')  # Em space
    text = text.replace('\u2004', ' ')  # Three-per-em space
    text = text.replace('\u2005', ' ')  # Four-per-em space
    text = text.replace('\u2006', ' ')  # Six-per-em space
    text = text.replace('\u2007', ' ')  # Figure space
    text = text.replace('\u2008', ' ')  # Punctuation space
    text = text.replace('\u2009', ' ')  # Thin space
    text = text.replace('\u200a', ' ')  # Hair space
    
    return text.strip()

def postprocess_translation(text, target_language):
    """Post-process translated text for better quality"""
    if not text:
        return ""
    
    text = text.strip()
    
    # Language-specific post-processing
    if target_language == 'th':
        text = postprocess_thai_translation(text)
    elif target_language == 'zh':
        text = postprocess_chinese_translation(text)
    elif target_language == 'ja':
        text = postprocess_japanese_translation(text)
    elif target_language == 'ko':
        text = postprocess_korean_translation(text)
    elif target_language == 'ar':
        text = postprocess_arabic_translation(text)
    elif target_language == 'lo':
        text = postprocess_lao_translation(text)
    
    return text

def postprocess_thai_translation(text):
    """Post-process Thai translation"""
    # Fix spacing around Thai characters and tone marks
    replacements = {
        ' ๆ': 'ๆ',
        ' ฯ': 'ฯ',
        ' ์': '์',
        ' ็': '็',
        ' ่': '่',
        ' ้': '้',
        ' ๊': '๊',
        ' ๋': '๋',
        ' ั': 'ั',
        ' ิ': 'ิ',
        ' ี': 'ี',
        ' ึ': 'ึ',
        ' ื': 'ื',
        ' ุ': 'ุ',
        ' ู': 'ู',
        ' เ ': 'เ',
        ' แ ': 'แ',
        ' โ ': 'โ',
        ' ใ ': 'ใ',
        ' ไ ': 'ไ'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text

def postprocess_chinese_translation(text):
    """Post-process Chinese translation"""
    # Remove spaces between Chinese characters
    text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
    return text

def postprocess_japanese_translation(text):
    """Post-process Japanese translation"""
    # Remove spaces between Japanese characters
    text = re.sub(r'([\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff])\s+([\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff])', r'\1\2', text)
    return text

def postprocess_korean_translation(text):
    """Post-process Korean translation"""
    # Remove spaces between Korean characters where appropriate
    text = re.sub(r'([\uac00-\ud7af])\s+([\uac00-\ud7af])', r'\1\2', text)
    return text

def postprocess_arabic_translation(text):
    """Post-process Arabic translation"""
    # Remove extra spaces and fix RTL text issues
    text = re.sub(r'\s+', ' ', text)
    return text

def postprocess_lao_translation(text):
    """Post-process Lao translation"""
    # Fix spacing around Lao characters and tone marks
    replacements = {
        ' ເ ': 'ເ',
        ' ແ ': 'ແ',
        ' ໂ ': 'ໂ',
        ' ໃ ': 'ໃ',
        ' ໄ ': 'ໄ',
        ' ະ ': 'ະ',
        ' າ ': 'າ',
        ' ິ ': 'ິ',
        ' ີ ': 'ີ',
        ' ຶ ': 'ຶ',
        ' ື ': 'ື',
        ' ຸ ': 'ຸ',
        ' ູ ': 'ູ',
        ' ົ ': 'ົ',
        ' ຽ ': 'ຽ',
        ' ່ ': '່',
        ' ້ ': '້',
        ' ໊ ': '໊',
        ' ໋ ': '໋',
        ' ໍ ': 'ໍ',
        ' ໎ ': '໎',
        ' ໏ ': '໏',
        ' ໐ ': '໐',
        ' ໑ ': '໑',
        ' ໒ ': '໒',
        ' ໓ ': '໓',
        ' ໔ ': '໔',
        ' ໕ ': '໕',
        ' ໖ ': '໖',
        ' ໗ ': '໗',
        ' ໘ ': '໘',
        ' ໙ ': '໙'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text

def split_text_for_translation(text, max_length=5000):
    """Split long text into chunks for translation"""
    # ถ้า max_length เป็น 0 หรือไม่จำกัด ให้ไม่แบ่ง
    if max_length == 0 or len(text) <= max_length:
        return [text]
    
    chunks = []
    
    # First, try to split by paragraphs
    paragraphs = text.split('\n\n')
    current_chunk = ""
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) <= max_length:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
            else:
                # Paragraph is too long, split by sentences
                sentences = split_by_sentences(paragraph)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) <= max_length:
                        current_chunk += sentence + " "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def split_by_sentences(text):
    """Split text by sentences using various delimiters"""
    # Multiple language sentence delimiters
    sentence_delimiters = r'[.!?।。！？｡]'
    sentences = re.split(sentence_delimiters, text)
    
    # Clean up sentences
    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            cleaned_sentences.append(sentence)
    
    return cleaned_sentences

def validate_language_code(lang_code):
    """Validate language code"""
    return lang_code in SUPPORTED_LANGUAGES

def detect_text_language(text):
    """Simple language detection (fallback)"""
    try:
        # Basic heuristics for common languages
        if re.search(r'[\u0E00-\u0E7F]', text):
            return 'th'  # Thai
        elif re.search(r'[\u4e00-\u9fff]', text):
            return 'zh'  # Chinese
        elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
            return 'ja'  # Japanese
        elif re.search(r'[\uac00-\ud7af]', text):
            return 'ko'  # Korean
        elif re.search(r'[\u0600-\u06ff]', text):
            return 'ar'  # Arabic
        elif re.search(r'[\u0400-\u04ff]', text):
            return 'ru'  # Russian
        else:
            return 'en'  # Default to English
    except:
        return 'auto'

# =============================================================================
# 🌐 CORE TRANSLATION FUNCTIONS
# =============================================================================

def translate_chunk(text, source_lang, target_lang):
    """Translate a single chunk of text"""
    try:
        # Check cache first
        if CACHE_ENABLED:
            cache_key = generate_cache_key(text, source_lang, target_lang)
            if cache_key in translation_cache and is_cache_valid(cache_timestamps[cache_key]):
                request_stats['cache_hits'] += 1
                logger.info(f"Cache hit for translation chunk")
                return translation_cache[cache_key]
        
        # Prepare request data
        translate_data = {
            'q': text,
            'source': source_lang,
            'target': target_lang,
            'format': 'text'
        }
        
        if API_KEY:
            translate_data['api_key'] = API_KEY
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'YouTube-Video-Translator/1.0'
        }
        
        # Make translation request with retries
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.post(
                    f"{LIBRETRANSLATE_URL}/translate",
                    json=translate_data,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    translated_text = result.get('translatedText', '')
                    
                    if not translated_text:
                        raise Exception("Empty translation result")
                    
                    # Store in cache
                    if CACHE_ENABLED:
                        translation_cache[cache_key] = translated_text
                        cache_timestamps[cache_key] = time.time()
                    
                    return translated_text
                
                elif response.status_code == 429:
                    # Rate limited, wait and retry
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                    time.sleep(wait_time)
                    continue
                
                else:
                    logger.error(f"Translation API error {response.status_code}: {response.text}")
                    if attempt == MAX_RETRIES - 1:
                        raise Exception(f"Translation service error: {response.status_code}")
            
            except requests.RequestException as e:
                logger.error(f"Translation request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    raise Exception(f"Translation service unavailable: {str(e)}")
                time.sleep(2 ** attempt)
        
        raise Exception("Max retries exceeded")
        
    except Exception as e:
        logger.error(f"Translation chunk failed: {str(e)}")
        raise

def translate_long_text(text, source_lang, target_lang):
    """Translate long text by splitting into chunks"""
    try:
        # ถ้าไม่จำกัดความยาว ให้แปลทั้งหมดในครั้งเดียว
        if MAX_TEXT_LENGTH == 0:
            return translate_chunk(text, source_lang, target_lang)
        
        # แบ่งข้อความเป็นชิ้นเล็กๆ
        chunks = split_text_for_translation(text, MAX_CHUNK_SIZE)
        
        if len(chunks) == 1:
            # ข้อความสั้น ไม่ต้องแบ่ง
            return translate_chunk(text, source_lang, target_lang)
        
        # แปลทีละชิ้น
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Translating chunk {i+1}/{len(chunks)} ({len(chunk)} characters)")
            
            translated_chunk = translate_chunk(chunk, source_lang, target_lang)
            if translated_chunk:
                translated_chunks.append(translated_chunk)
            else:
                logger.error(f"Failed to translate chunk {i+1}")
                return None
        
        # รวมผลลัพธ์
        final_translation = ' '.join(translated_chunks)
        
        # Post-process ตามภาษาเป้าหมาย
        final_translation = postprocess_translation(final_translation, target_lang)
        
        return final_translation
        
    except Exception as e:
        logger.error(f"Error in translate_long_text: {str(e)}")
        return None

# =============================================================================
# 🛣️ API ENDPOINTS
# =============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Test connection to LibreTranslate
        start_time = time.time()
        response = requests.get(f"{LIBRETRANSLATE_URL}/languages", timeout=5)
        response_time = time.time() - start_time
        
        libretranslate_status = 'connected' if response.status_code == 200 else 'disconnected'
        
        return jsonify({
            'status': 'healthy',
            'service': 'translation-server',
            'version': '1.0.0',
            'timestamp': time.time(),
            'libretranslate': {
                'url': LIBRETRANSLATE_URL,
                'status': libretranslate_status,
                'response_time': round(response_time, 3)
            },
            'configuration': {
                'api_key_configured': bool(API_KEY),
                'max_text_length': MAX_TEXT_LENGTH,
                'max_chunk_size': MAX_CHUNK_SIZE,
                'cache_enabled': CACHE_ENABLED,
                'cache_ttl': CACHE_TTL
            },
            'supported_languages': len(SUPPORTED_LANGUAGES),
            'statistics': request_stats
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'service': 'translation-server',
            'libretranslate_status': 'error'
        }), 503

@app.route('/languages', methods=['GET'])
def get_languages():
    """Get supported languages"""
    try:
        # Try to get languages from LibreTranslate
        try:
            response = requests.get(f"{LIBRETRANSLATE_URL}/languages", timeout=10)
            
            if response.status_code == 200:
                languages = response.json()
                language_dict = {lang['code']: lang['name'] for lang in languages}
                
                return jsonify({
                    'languages': language_dict,
                    'source': 'libretranslate',
                    'total': len(language_dict),
                    'timestamp': time.time()
                })
        
        except Exception as e:
            logger.warning(f"Failed to get languages from LibreTranslate: {str(e)}")
        
        # Return default languages
        return jsonify({
            'languages': SUPPORTED_LANGUAGES,
            'source': 'default',
            'total': len(SUPPORTED_LANGUAGES),
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Get languages failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/detect', methods=['POST'])
def detect_language():
    """Detect language of input text"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 1000:  # Limit text for detection
            text = text[:1000]
        
        logger.info(f"Detecting language for text ({len(text)} chars)")
        
        # Try LibreTranslate detection
        detected_lang = 'auto'
        confidence = 0.0
        
        try:
            detect_data = {'q': text}
            if API_KEY:
                detect_data['api_key'] = API_KEY
            
            response = requests.post(
                f"{LIBRETRANSLATE_URL}/detect",
                json=detect_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result and len(result) > 0:
                    detected_lang = result[0]['language']
                    confidence = result[0]['confidence']
        
        except Exception as e:
            logger.warning(f"LibreTranslate detection failed: {str(e)}")
            # Fallback to simple detection
            detected_lang = detect_text_language(text)
            confidence = 0.7  # Estimated confidence for fallback
        
        return jsonify({
            'detected_language': detected_lang,
            'confidence': confidence,
            'text_length': len(data.get('text', '')),
            'language_name': SUPPORTED_LANGUAGES.get(detected_lang, 'Unknown')
        })
        
    except Exception as e:
        logger.error(f"Language detection failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/translate', methods=['POST'])
def translate():
    """Translate text"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        text = data.get('text', '').strip()
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'th')
        
        # Validation
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > MAX_TEXT_LENGTH:
            return jsonify({
                'error': f'Text too long. Maximum length is {MAX_TEXT_LENGTH} characters'
            }), 400
        
        if not validate_language_code(source_lang):
            return jsonify({'error': f'Unsupported source language: {source_lang}'}), 400
        
        if not validate_language_code(target_lang):
            return jsonify({'error': f'Unsupported target language: {target_lang}'}), 400
        
        if source_lang == target_lang and source_lang != 'auto':
            return jsonify({
                'translated_text': text,
                'source_language': source_lang,
                'target_language': target_lang,
                'original_length': len(text),
                'translated_length': len(text),
                'processing_method': 'no_translation_needed',
                'processing_time': 0
            })
        
        logger.info(f"Translating text from {source_lang} to {target_lang} ({len(text)} chars)")
        
        # Preprocess text
        processed_text = preprocess_text(text)
        
        # Choose translation method based on text length
        if len(processed_text) > MAX_CHUNK_SIZE:
            translated_text = translate_long_text(processed_text, source_lang, target_lang)
            processing_method = 'multi_chunk'
        else:
            translated_text = translate_chunk(processed_text, source_lang, target_lang)
            processing_method = 'single_chunk'
        
        # Final post-processing
        final_translation = postprocess_translation(translated_text, target_lang)
        
        processing_time = time.time() - start_time
        
        # Update statistics
        update_stats(True, processing_time, source_lang, target_lang)
        
        logger.info(f"Translation completed in {processing_time:.2f}s")
        
        return jsonify({
            'translated_text': final_translation,
            'source_language': source_lang,
            'target_language': target_lang,
            'original_length': len(text),
            'translated_length': len(final_translation),
            'processing_method': processing_method,
            'processing_time': round(processing_time, 3)
        })
        
    except Exception as e:
        processing_time = time.time() - start_time
        update_stats(False, processing_time)
        
        logger.error(f"Translation failed: {str(e)}")
        return jsonify({
            'error': f'Translation failed: {str(e)}',
            'processing_time': round(processing_time, 3)
        }), 500

@app.route('/translate_batch', methods=['POST'])
def translate_batch():
    """Translate multiple texts in batch"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        texts = data.get('texts', [])
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'th')
        
        if not texts or not isinstance(texts, list):
            return jsonify({'error': 'No texts provided or invalid format'}), 400
        
        if len(texts) > MAX_BATCH_SIZE:
            return jsonify({'error': f'Too many texts. Maximum {MAX_BATCH_SIZE} texts per batch'}), 400
        
        logger.info(f"Batch translating {len(texts)} texts from {source_lang} to {target_lang}")
        
        results = []
        successful = 0
        failed = 0
        
        for i, text in enumerate(texts):
            try:
                if not text or not text.strip():
                    results.append({
                        'index': i,
                        'success': False,
                        'error': 'Empty text',
                        'original_text': text,
                        'translated_text': ''
                    })
                    failed += 1
                    continue
                
                # Preprocess and translate
                processed_text = preprocess_text(text.strip())
                
                if len(processed_text) > MAX_TEXT_LENGTH:
                    results.append({
                        'index': i,
                        'success': False,
                        'error': f'Text too long (>{MAX_TEXT_LENGTH} chars)',
                        'original_text': text,
                        'translated_text': ''
                    })
                    failed += 1
                    continue
                
                if len(processed_text) > MAX_CHUNK_SIZE:
                    translated_text = translate_long_text(processed_text, source_lang, target_lang)
                else:
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
                successful += 1
                
                # Small delay between requests
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to translate text {i}: {str(e)}")
                results.append({
                    'index': i,
                    'success': False,