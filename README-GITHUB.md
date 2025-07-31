# 🎬 YouTube Video Translator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)

> แปลวิดีโอ YouTube เป็นภาษาที่คุณต้องการ พร้อมเสียงและซับไตเติล

## 🌟 Features

- 🎬 **YouTube Video Translation** - แปลวิดีโอ YouTube เป็น 50+ ภาษา
- 🗣️ **Speech-to-Text** - ใช้ OpenAI Whisper แปลงเสียงเป็นข้อความ
- 🌍 **AI Translation** - ใช้ LibreTranslate แปลภาษาด้วย AI
- 🔊 **Text-to-Speech** - ใช้ Coqui TTS สังเคราะห์เสียงธรรมชาติ
- 📹 **Video Processing** - รวมเสียงกับวิดีโอด้วย FFmpeg
- 🎨 **Modern UI** - React Frontend ที่สวยงามและใช้งานง่าย
- 🐳 **Docker Support** - ติดตั้งง่ายด้วย Docker Compose
- 🔒 **Privacy Focused** - ทำงานแบบ Self-hosted ไม่ส่งข้อมูลไปภายนอก

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** 20.10+ และ Docker Compose 2.0+
- **RAM**: อย่างน้อย 8GB (แนะนำ 16GB+)
- **Storage**: อย่างน้อย 20GB พื้นที่ว่าง
- **Internet**: สำหรับดาวน์โหลด AI models

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/youtube-translate.git
cd youtube-translate
```

2. **Start Services**
```bash
# Windows
.\Start.bat

# Linux/macOS
./Start.sh
```

3. **Access Application**
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Translation API**: http://localhost:5000

## 📋 Supported Languages

### 🌏 Asian Languages
- 🇹🇭 **Thai** (ไทย)
- 🇱🇦 **Lao** (ລາວ)
- 🇻🇳 **Vietnamese** (Tiếng Việt)
- 🇨🇳 **Chinese** (中文)
- 🇯🇵 **Japanese** (日本語)
- 🇰🇷 **Korean** (한국어)
- 🇮🇩 **Indonesian** (Bahasa Indonesia)
- 🇲🇾 **Malay** (Bahasa Melayu)

### 🌍 Other Languages
- 🇺🇸 **English**
- 🇪🇸 **Spanish** (Español)
- 🇫🇷 **French** (Français)
- 🇩🇪 **German** (Deutsch)
- 🇮🇹 **Italian** (Italiano)
- 🇵🇹 **Portuguese** (Português)
- 🇷🇺 **Russian** (Русский)
- 🇸🇦 **Arabic** (العربية)
- และอีก 40+ ภาษา

## 🏗️ Architecture

```
🌐 YouTube Video → 📥 Download → 🎵 Extract Audio → 🗣️ Speech-to-Text → 🌍 Translate → 🔊 Text-to-Speech → 📹 Merge Video
```

### Components

- **Frontend** (React) - Web interface สำหรับผู้ใช้
- **Backend** (FastAPI) - API server และ orchestration
- **Whisper Service** - Speech-to-Text ด้วย OpenAI Whisper
- **Translation Service** - แปลภาษาด้วย LibreTranslate
- **TTS Service** - Text-to-Speech ด้วย Coqui TTS
- **Database** (PostgreSQL) - เก็บข้อมูลและประวัติ
- **Cache** (Redis) - เร่งการทำงานและ queue management

## 🛠️ Technology Stack

### Backend
- **Python 3.9+** - ภาษาโปรแกรมหลัก
- **FastAPI** - Web framework
- **OpenAI Whisper** - Speech recognition
- **LibreTranslate** - Machine translation
- **Coqui TTS** - Text-to-speech synthesis
- **FFmpeg** - Video/audio processing
- **PostgreSQL** - Database
- **Redis** - Caching & queue

### Frontend
- **React 18** - UI framework
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Router** - Navigation

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Web server

## 📖 Usage

### Basic Translation

1. **เปิดเว็บแอป** ที่ http://localhost:3000
2. **ใส่ YouTube URL** ของวิดีโอที่ต้องการแปล
3. **เลือกภาษาต้นทาง** (หรือใช้ Auto-detect)
4. **เลือกภาษาปลายทาง** (เช่น ไทย, ลาว)
5. **กด "เริ่มแปลวิดีโอ"**
6. **รอการประมวลผล** (5-15 นาที)
7. **ดาวน์โหลดผลลัพธ์**

### Advanced Features

- **Batch Processing** - แปลหลายวิดีโอพร้อมกัน
- **Custom Settings** - ปรับแต่งคุณภาพและความเร็ว
- **History** - ดูประวัติการแปล
- **API Access** - ใช้ผ่าน REST API

## 🔧 Configuration

### Environment Variables

```bash
# Processing Configuration
MAX_VIDEO_DURATION=0          # 0 = ไม่จำกัด
MAX_TEXT_LENGTH=0             # 0 = ไม่จำกัด
MAX_FILE_SIZE=2000            # 2GB

# AI Models
WHISPER_MODEL=medium          # base, medium, large
TTS_MODEL_TH=tts_models/th/mai_female/glow-tts

# Performance
CONCURRENT_TASKS=5
TASK_TIMEOUT=14400            # 4 hours
```

### Docker Configuration

```yaml
# docker-compose.yml
services:
  frontend:
    ports:
      - "3000:80"
  
  backend:
    ports:
      - "8000:8000"
  
  libretranslate:
    ports:
      - "5000:5000"
```

## 🚀 Deployment

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/youtube-translate.git
cd youtube-translate

# Start development environment
docker-compose -f docker/docker-compose-simple.yml up -d

# View logs
docker-compose logs -f
```

### Production Deployment

```bash
# Use production configuration
cp unlimited-config.env .env

# Start production services
docker-compose -f docker/docker-compose-simple.yml up -d

# Monitor services
docker-compose ps
```

## 📊 Performance

### System Requirements

| **Component** | **Minimum** | **Recommended** |
|---------------|-------------|-----------------|
| **RAM** | 8GB | 16GB+ |
| **CPU** | 4 cores | 8 cores+ |
| **Storage** | 20GB | 50GB+ |
| **Network** | 10 Mbps | 100 Mbps+ |

### Processing Times

| **Video Length** | **Processing Time** | **Output Size** |
|------------------|-------------------|-----------------|
| **5 minutes** | 3-5 minutes | 50-100MB |
| **10 minutes** | 5-10 minutes | 100-200MB |
| **30 minutes** | 15-25 minutes | 300-500MB |
| **1 hour** | 30-45 minutes | 500MB-1GB |

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Backend development
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# Frontend development
cd frontend
npm install
npm start
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI Whisper** - Speech recognition
- **LibreTranslate** - Machine translation
- **Coqui TTS** - Text-to-speech
- **FFmpeg** - Media processing
- **React** - Frontend framework
- **FastAPI** - Backend framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/youtube-translate/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/youtube-translate/discussions)
- **Wiki**: [Documentation](https://github.com/yourusername/youtube-translate/wiki)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/youtube-translate&type=Date)](https://star-history.com/#yourusername/youtube-translate&Date)

---

**Made with ❤️ for the open source community** 