# Whisper server placeholder# processing/whisper/whisper_server.py
from flask import Flask, request, jsonify
import whisper
import os
import tempfile
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Whisper model
MODEL_NAME = os.getenv('WHISPER_MODEL', 'medium')
DEVICE = os.getenv('WHISPER_DEVICE', 'cpu')

logger.info(f"Loading Whisper model: {MODEL_NAME}")
model = whisper.load_model(MODEL_NAME, device=DEVICE)
logger.info("Whisper model loaded successfully")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model': MODEL_NAME, 'device': DEVICE})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(audio_file.filename)
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        audio_file.save(temp_path)
        
        try:
            # Transcribe audio
            logger.info(f"Transcribing audio file: {filename}")
            result = model.transcribe(temp_path)
            
            response_data = {
                'text': result['text'],
                'language': result['language'],
                'segments': result.get('segments', [])
            }
            
            logger.info(f"Transcription completed for {filename}")
            return jsonify(response_data)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe_url', methods=['POST'])
def transcribe_url():
    try:
        data = request.get_json()
        audio_path = data.get('audio_path')
        
        if not audio_path or not os.path.exists(audio_path):
            return jsonify({'error': 'Audio file not found'}), 400
        
        logger.info(f"Transcribing audio file: {audio_path}")
        result = model.transcribe(audio_path)
        
        response_data = {
            'text': result['text'],
            'language': result['language'],
            'segments': result.get('segments', [])
        }
        
        logger.info(f"Transcription completed for {audio_path}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)

# processing/whisper/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install \
    flask==2.3.3 \
    openai-whisper==20231117 \
    torch==2.1.1 \
    torchaudio==2.1.1 \
    werkzeug==2.3.7

# Copy application code
COPY whisper_server.py .

# Create directories
RUN mkdir -p /app/uploads /app/temp

# Download model at build time (optional)
RUN python -c "import whisper; whisper.load_model('base')"

EXPOSE 5001

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

CMD ["python", "whisper_server.py"]

---

# processing/tts/tts_server.py
from flask import Flask, request, jsonify, send_file
from TTS.api import TTS
import os
import tempfile
import logging
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize TTS models
TTS_MODEL_TH = os.getenv('TTS_MODEL_TH', 'tts_models/th/mai_female/glow-tts')
DEVICE = os.getenv('TTS_DEVICE', 'cpu')

logger.info(f"Loading TTS model: {TTS_MODEL_TH}")
try:
    tts_th = TTS(model_name=TTS_MODEL_TH).to(DEVICE)
    logger.info("Thai TTS model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load TTS model: {e}")
    tts_th = None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy' if tts_th else 'unhealthy',
        'model': TTS_MODEL_TH,
        'device': DEVICE
    })

@app.route('/synthesize', methods=['POST'])
def synthesize():
    try:
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'th')
        voice_type = data.get('voice_type', 'female')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if not tts_th:
            return jsonify({'error': 'TTS model not available'}), 500
        
        # Generate unique filename
        output_filename = f"tts_{uuid.uuid4().hex}.wav"
        output_path = os.path.join(tempfile.gettempdir(), output_filename)
        
        logger.info(f"Synthesizing text: {text[:50]}...")
        
        # Generate speech
        tts_th.tts_to_file(text=text, file_path=output_path)
        
        if not os.path.exists(output_path):
            return jsonify({'error': 'Failed to generate audio'}), 500
        
        logger.info(f"TTS synthesis completed: {output_filename}")
        
        return jsonify({
            'audio_file': output_filename,
            'audio_path': output_path,
            'text_length': len(text)
        })
        
    except Exception as e:
        logger.error(f"TTS synthesis failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/synthesize_to_file', methods=['POST'])
def synthesize_to_file():
    try:
        data = request.get_json()
        text = data.get('text', '')
        output_path = data.get('output_path')
        language = data.get('language', 'th')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if not output_path:
            return jsonify({'error': 'No output path provided'}), 400
        
        if not tts_th:
            return jsonify({'error': 'TTS model not available'}), 500
        
        logger.info(f"Synthesizing text to file: {output_path}")
        
        # Generate speech
        tts_th.tts_to_file(text=text, file_path=output_path)
        
        if not os.path.exists(output_path):
            return jsonify({'error': 'Failed to generate audio file'}), 500
        
        # Get file info
        file_size = os.path.getsize(output_path)
        
        logger.info(f"TTS synthesis completed: {output_path}")
        
        return jsonify({
            'success': True,
            'output_path': output_path,
            'file_size': file_size,
            'text_length': len(text)
        })
        
    except Exception as e:
        logger.error(f"TTS synthesis to file failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_audio(filename):
    try:
        file_path = os.path.join(tempfile.gettempdir(), secure_filename(filename))
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        logger.error(f"File download failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/models', methods=['GET'])
def get_models():
    try:
        available_models = {
            'thai': {
                'female': ['tts_models/th/mai_female/glow-tts'],
                'male': ['tts_models/th/mai_male/glow-tts']
            }
        }
        return jsonify(available_models)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)

# processing/tts/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    build-essential \
    git \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install \
    flask==2.3.3 \
    TTS==0.20.6 \
    torch==2.1.1 \
    torchaudio==2.1.1 \
    werkzeug==2.3.7 \
    coqui-tts==0.20.6

# Copy application code
COPY tts_server.py .

# Create directories
RUN mkdir -p /app/output /app/temp

# Download model at build time (optional)
RUN python -c "from TTS.api import TTS; TTS(model_name='tts_models/th/mai_female/glow-tts')"

EXPOSE 5002

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

CMD ["python", "tts_server.py"]

---

# processing/translation/translation_server.py
from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LibreTranslate configuration
LIBRETRANSLATE_URL = os.getenv('LIBRETRANSLATE_URL', 'http://localhost:5000')
API_KEY = os.getenv('LIBRETRANSLATE_API_KEY', '')

@app.route('/health', methods=['GET'])
def health():
    try:
        # Test connection to LibreTranslate
        response = requests.get(f"{LIBRETRANSLATE_URL}/languages", timeout=5)
        if response.status_code == 200:
            return jsonify({'status': 'healthy', 'libretranslate': 'connected'})
        else:
            return jsonify({'status': 'unhealthy', 'libretranslate': 'disconnected'}), 503
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        text = data.get('text', '')
        source_lang = data.get('source_lang', 'auto')
        target_lang = data.get('target_lang', 'th')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Prepare request to LibreTranslate
        translate_data = {
            'q': text,
            'source': source_lang,
            'target': target_lang,
            'format': 'text'
        }
        
        if API_KEY:
            translate_data['api_key'] = API_KEY
        
        logger.info(f"Translating text from {source_lang} to {target_lang}")
        
        # Make translation request
        response = requests.post(
            f"{LIBRETRANSLATE_URL}/translate",
            json=translate_data,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Translation failed: {response.text}")
            return jsonify({'error': 'Translation service error'}), 500
        
        result = response.json()
        translated_text = result.get('translatedText', '')
        
        logger.info(f"Translation completed successfully")
        
        return jsonify({
            'translated_text': translated_text,
            'source_language': source_lang,
            'target_language': target_lang,
            'original_length': len(text),
            'translated_length': len(translated_text)
        })
        
    except requests.RequestException as e:
        logger.error(f"Translation request failed: {str(e)}")
        return jsonify({'error': 'Translation service unavailable'}), 503
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/detect', methods=['POST'])
def detect_language():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        detect_data = {'q': text}
        if API_KEY:
            detect_data['api_key'] = API_KEY
        
        response = requests.post(
            f"{LIBRETRANSLATE_URL}/detect",
            json=detect_data,
            timeout=10
        )
        
        if response.status_code != 200:
            return jsonify({'error': 'Language detection failed'}), 500
        
        result = response.json()
        detected_lang = result[0]['language'] if result else 'auto'
        confidence = result[0]['confidence'] if result else 0
        
        return jsonify({
            'detected_language': detected_lang,
            'confidence': confidence
        })
        
    except Exception as e:
        logger.error(f"Language detection failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/languages', methods=['GET'])
def get_languages():
    try:
        response = requests.get(f"{LIBRETRANSLATE_URL}/languages", timeout=10)
        
        if response.status_code != 200:
            return jsonify({'error': 'Failed to get languages'}), 500
        
        languages = response.json()
        return jsonify(languages)
        
    except Exception as e:
        logger.error(f"Failed to get languages: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)

# processing/translation/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install \
    flask==2.3.3 \
    requests==2.31.0 \
    werkzeug==2.3.7

# Copy application code
COPY translation_server.py .

EXPOSE 5003

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/health || exit 1

CMD ["python", "translation_server.py"]