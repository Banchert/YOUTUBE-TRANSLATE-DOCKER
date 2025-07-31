# database/init.sql
CREATE DATABASE IF NOT EXISTS youtube_translator;

CREATE TABLE IF NOT EXISTS processing_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) UNIQUE NOT NULL,
    youtube_url TEXT NOT NULL,
    target_language VARCHAR(10) DEFAULT 'th',
    audio_mixing VARCHAR(20) DEFAULT 'overlay',
    voice_type VARCHAR(20) DEFAULT 'female',
    status VARCHAR(20) DEFAULT 'queued',
    progress INTEGER DEFAULT 0,
    message TEXT,
    error TEXT,
    result_file TEXT,
    download_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    processing_time FLOAT,
    file_size INTEGER,
    video_duration FLOAT
);

CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_task_id ON processing_tasks(task_id);
CREATE INDEX IF NOT EXISTS idx_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_created_at ON processing_tasks(created_at);

---

# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'youtube-translator-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

---

# monitoring/grafana/dashboards/dashboard.json
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "description": "YouTube Video Translator Application Dashboard",
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "panels": [
    {
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "vis": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "short"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 1,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom"
        },
        "tooltip": {
          "mode": "single"
        }
      },
      "targets": [
        {
          "expr": "rate(http_requests_total[5m])",
          "interval": "",
          "legendFormat": "HTTP Requests/sec",
          "refId": "A"
        }
      ],
      "title": "HTTP Request Rate",
      "type": "timeseries"
    }
  ],
  "schemaVersion": 27,
  "style": "dark",
  "tags": ["youtube-translator"],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-1h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "YouTube Video Translator Dashboard",
  "uid": "youtube-translator",
  "version": 1
}

---

# .env.example (Root level)
# ===========================================
# YouTube Video Translator Configuration
# ===========================================

# Application Environment
NODE_ENV=production
DEBUG=false

# Database Configuration
DATABASE_URL=postgresql://postgres:password@postgres:5432/youtube_translator

# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_DB=0

# External Services URLs
WHISPER_SERVICE_URL=http://whisper-service:5001
TTS_SERVICE_URL=http://tts-service:5002
TRANSLATION_SERVICE_URL=http://libretranslate:5000

# API Keys (if needed)
LIBRETRANSLATE_API_KEY=
OPENAI_API_KEY=

# File Storage Configuration
UPLOAD_DIR=./uploads
OUTPUT_DIR=./output
MAX_FILE_SIZE=500
MAX_VIDEO_DURATION=3600

# Processing Configuration
CONCURRENT_TASKS=3
TASK_TIMEOUT=7200
WHISPER_MODEL=medium
TTS_MODEL_TH=tts_models/th/mai_female/glow-tts

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET=your-jwt-secret-key
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
SENTRY_DSN=

# Email Configuration (optional)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
EMAIL_FROM=noreply@yourdomain.com

---

# .gitignore
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Application specific
uploads/
output/
logs/
temp/
*.log

# Build outputs
build/
dist/
*.egg-info/

# Database
*.db
*.sqlite
*.sqlite3

# Docker
.dockerignore

# Temporary files
tmp/
*.tmp
*.temp

# SSL certificates
ssl/
*.pem
*.key
*.crt

# Backup files
*.bak
*.backup

---

# README.md
# YouTube Video Translator

🎬 แปลวิดีโอ YouTube เป็นภาษาไทยด้วย AI อัตโนมัติ

## ✨ คุณสมบัติ

- 🎯 แปลวิดีโอ YouTube จากภาษาต่างๆ เป็นภาษาไทย
- 🎵 รองรับการรวมเสียงหลายรูปแบบ (Overlay, Replace, Stereo)
- ⚡ ประมวลผลแบบ Real-time พร้อม Progress tracking
- 🎨 UI/UX ที่สวยงามและใช้งานง่าย
- 📱 รองรับทุกอุปกรณ์ (Responsive Design)
- 🔒 ปลอดภัยด้วย Rate limiting และ Input validation
- 📊 สถิติการใช้งานและประวัติการประมวลผล

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React.js      │    │     Nginx       │    │   FastAPI       │
│   Frontend      │───▶│  Reverse Proxy  │───▶│   Backend       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│   Processing    │──────────────┘
                        │    Services     │
                        │                 │
                        │ - Whisper STT   │
                        │ - Coqui TTS     │
                        │ - LibreTranslate│
                        │ - Redis Queue   │
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- อย่างน้อย 8GB RAM
- 20GB พื้นที่ว่าง

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd youtube-translator

# 2. Setup environment
cp .env.example .env
# แก้ไข .env ตามความต้องการ

# 3. Run setup script
chmod +x setup.sh
./setup.sh

# 4. Access application
open http://localhost:3000
```

### Manual Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm start

# Services
docker-compose up redis postgres libretranslate
```

## 📁 Project Structure

```
youtube-translator/
├── frontend/                    # React.js Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/          # React Components
│   │   ├── services/           # API Services
│   │   ├── hooks/              # Custom Hooks
│   │   ├── store/              # State Management
│   │   └── utils/              # Utilities
│   ├── package.json
│   └── Dockerfile
│
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── core/               # Configuration
│   │   ├── services/           # Business Logic
│   │   ├── models/             # Data Models
│   │   ├── api/                # API Routes
│   │   └── utils/              # Utilities
│   ├── requirements.txt
│   └── Dockerfile
│
├── processing/                  # Processing Services
│   ├── whisper/                # Speech-to-Text
│   ├── tts/                    # Text-to-Speech
│   └── translation/            # Translation Service
│
├── database/                    # Database Scripts
├── monitoring/                  # Monitoring Config
├── nginx/                       # Nginx Configuration
├── docker-compose.yml
└── setup.sh
```

## 🔧 Configuration

### Environment Variables

```env
# Application
DEBUG=false
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# External Services
WHISPER_SERVICE_URL=http://whisper-service:5001
TTS_SERVICE_URL=http://tts-service:5002
TRANSLATION_SERVICE_URL=http://libretranslate:5000

# Processing
MAX_VIDEO_DURATION=3600  # 1 hour
MAX_FILE_SIZE=500        # 500MB
CONCURRENT_TASKS=3
```

### Supported Languages

- 🇹🇭 Thai (ไทย)
- 🇺🇸 English
- 🇨🇳 Chinese (中文)
- 🇯🇵 Japanese (日本語)
- 🇰🇷 Korean (한국어)
- และอื่นๆ

## 📊 Monitoring

### Health Checks

```bash
# Backend API
curl http://localhost:8000/health

# Services
curl http://localhost:5001/health  # Whisper
curl http://localhost:5002/health  # TTS
curl http://localhost:5000/languages  # Translation
```

### Monitoring Dashboard

```bash
# Enable monitoring
docker-compose --profile monitoring up -d

# Access dashboards
open http://localhost:9090    # Prometheus
open http://localhost:3001    # Grafana (admin/admin)
open http://localhost:5555    # Flower (Celery)
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service]

# Restart service
docker-compose restart [service]

# Scale services
docker-compose up -d --scale celery-worker=3

# Clean up
docker-compose down -v --remove-orphans
```

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test

# API testing
python scripts/test_api.py

# Load testing
docker run --rm -i loadimpact/k6 run - <scripts/load_test.js
```

## 🚀 Production Deployment

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with SSL
docker-compose -f docker-compose.prod.yml up -d

# Update application
./scripts/deploy.sh
```

### Manual Production

```bash
# Backend
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Frontend
npm run build
serve -s build -l 3000

# Nginx configuration
sudo nginx -t
sudo nginx -s reload
```

## 🔧 API Documentation

### Endpoints

- `POST /process-video/` - เริ่มประมวลผลวิดีโอ
- `GET /status/{task_id}` - ตรวจสอบสถานะ
- `GET /download/{task_id}` - ดาวน์โหลดผลลัพธ์
- `GET /health` - Health check
- `GET /docs` - API Documentation

### Example Usage

```javascript
// Process video
const response = await fetch('/api/process-video/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    youtube_url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    target_language: 'th',
    audio_mixing: 'overlay'
  })
});

// Check status
const status = await fetch(`/api/status/${taskId}`);
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@yourdomain.com
- 💬 Discord: [Your Discord Server]
- 📚 Documentation: [Your Docs URL]
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)

## 🎯 Roadmap

- [ ] รองรับ Subtitle generation
- [ ] Batch processing หลายๆ วิดีโอ
- [ ] Mobile app
- [ ] API rate limiting
- [ ] User authentication
- [ ] Payment integration
- [ ] Multi-language UI

---

Made with ❤️ in Thailand