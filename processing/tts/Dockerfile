FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    curl \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install TTS library
RUN pip install TTS

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/uploads /app/output && \
    chmod -R 777 /app/uploads /app/output

# Expose port
EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

# Start the service
CMD ["python", "tts_server.py"]