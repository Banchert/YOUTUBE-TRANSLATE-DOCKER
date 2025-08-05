FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install OpenAI Whisper
RUN pip install openai-whisper

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/uploads /app/temp && \
    chmod -R 777 /app/uploads /app/temp

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Start the service
CMD ["python", "whisper_server.py"]