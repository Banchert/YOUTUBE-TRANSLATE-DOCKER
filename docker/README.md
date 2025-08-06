# 🐳 YouTube Video Translator - Docker Setup

## 📋 Overview

This directory contains all Docker-related files for the YouTube Video Translator application. The system is designed to run multiple microservices in containers for easy deployment and scaling.

## 🏗️ Architecture

The application consists of the following services:

- **Frontend**: React application served by Nginx
- **Backend**: FastAPI application with multiple workers
- **Whisper Service**: OpenAI Whisper for speech-to-text
- **TTS Service**: Text-to-speech synthesis
- **LibreTranslate**: Translation service
- **Redis**: Caching and task queue
- **PostgreSQL**: Database storage
- **Nginx**: Reverse proxy (optional)
- **Prometheus & Grafana**: Monitoring (optional)

## 📁 File Structure

```
docker/
├── docker-compose.yml          # Main development configuration
├── docker-compose-simple.yml   # Simplified setup (no database)
├── docker-compose.prod.yml     # Production configuration
├── nginx.conf                  # Nginx reverse proxy configuration
├── prometheus.yml              # Prometheus monitoring configuration
├── env.example                 # Environment variables template
├── start.sh                    # Linux/macOS startup script
├── start.bat                   # Windows startup script
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Docker**: Version 20.10+ with Docker Compose 2.0+
2. **Git**: For cloning the repository
3. **System Requirements**:
   - RAM: 8GB minimum (16GB+ recommended)
   - Storage: 20GB+ free space
   - CPU: 4+ cores

### Installation

#### Option 1: Using Startup Scripts (Recommended)

**Linux/macOS:**
```bash
cd docker
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
cd docker
start.bat
```

#### Option 2: Manual Setup

1. **Clone and navigate to the project:**
```bash
cd docker
```

2. **Create environment file:**
```bash
cp env.example .env
# Edit .env with your configuration
```

3. **Start services:**
```bash
# Development mode
docker-compose up -d

# Simple mode (no database)
docker-compose -f docker-compose-simple.yml up -d

# Production mode
docker-compose -f docker-compose.prod.yml up -d
```

## 🎛️ Configuration Options

### Environment Variables

Copy `env.example` to `.env` and customize:

```env
# Application Settings
DEBUG=False
SECRET_KEY=your-secret-key-here

# Processing Settings
WHISPER_MODEL=medium          # Options: tiny, base, small, medium, large, large-v3
TTS_MODEL=tts_models/th/mai_female/glow-tts
WHISPER_DEVICE=cuda           # Options: cpu, cuda
TTS_DEVICE=cpu                # Options: cpu, cuda

# Resource Limits
BACKEND_MEMORY_LIMIT=4G
WHISPER_MEMORY_LIMIT=6G
```

### Service Modes

#### 1. Development Mode (`docker-compose.yml`)
- Full feature set with PostgreSQL database
- Health checks and monitoring
- Suitable for development and testing

#### 2. Simple Mode (`docker-compose-simple.yml`)
- Lightweight setup without PostgreSQL
- Uses file-based storage
- Good for quick testing

#### 3. Production Mode (`docker-compose.prod.yml`)
- High-performance configuration
- GPU support for AI models
- Monitoring with Prometheus/Grafana
- Nginx reverse proxy

## 📊 Monitoring

### Enable Monitoring

```bash
# Start with monitoring
./start.sh monitoring

# Or manually
docker-compose -f docker-compose.prod.yml --profile monitoring up -d
```

### Access Monitoring

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

## 🔧 Management Commands

### Using Startup Scripts

```bash
# Start services
./start.sh                    # Development mode
./start.sh simple             # Simple mode
./start.sh prod               # Production mode
./start.sh monitoring         # With monitoring

# Management
./start.sh status             # Show service status
./start.sh logs               # Show logs
./start.sh restart            # Restart services
./start.sh stop               # Stop services
./start.sh clean              # Clean up everything
```

### Using Docker Compose Directly

```bash
# Service management
docker-compose up -d          # Start services
docker-compose down           # Stop services
docker-compose restart        # Restart services
docker-compose ps             # Show status
docker-compose logs -f        # Show logs

# Individual services
docker-compose logs -f backend
docker-compose restart whisper-service
docker-compose exec backend bash

# Cleanup
docker-compose down --volumes --remove-orphans
docker system prune -f
```

## 🌐 Access URLs

After starting the services:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Whisper Service**: http://localhost:5001/health
- **TTS Service**: http://localhost:5002/health
- **Translation**: http://localhost:5000
- **Redis**: localhost:6379
- **PostgreSQL**: localhost:5432

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check what's using the ports
netstat -tlnp | grep :8000
# Kill the process or change ports in docker-compose.yml
```

#### 2. Memory Issues
```bash
# Check memory usage
docker stats
# Reduce memory limits in docker-compose.yml
```

#### 3. GPU Issues
```bash
# Check GPU availability
nvidia-smi
# Switch to CPU mode in .env file
WHISPER_DEVICE=cpu
TTS_DEVICE=cpu
```

#### 4. Build Failures
```bash
# Clean and rebuild
docker-compose down --volumes --remove-orphans
docker system prune -a
docker-compose build --no-cache
```

### Debug Commands

```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:5001/health
curl http://localhost:5002/health

# View service logs
docker-compose logs -f backend
docker-compose logs -f whisper-service

# Enter container
docker-compose exec backend bash
docker-compose exec whisper-service bash

# Check resource usage
docker stats --no-stream
```

## 📈 Performance Tuning

### For High Load

1. **Increase Workers:**
```yaml
# In docker-compose.yml
environment:
  - MAX_WORKERS=8
```

2. **Adjust Memory Limits:**
```yaml
deploy:
  resources:
    limits:
      memory: 8G
      cpus: '4.0'
```

3. **Use GPU:**
```yaml
deploy:
  reservations:
    devices:
      - driver: nvidia
        count: 1
        capabilities: [gpu]
```

### For Development

1. **Reduce Resource Usage:**
```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
```

2. **Use CPU Mode:**
```env
WHISPER_DEVICE=cpu
TTS_DEVICE=cpu
```

## 🔒 Security Considerations

1. **Change Default Passwords:**
   - Update PostgreSQL password in `.env`
   - Change LibreTranslate master key

2. **Use HTTPS in Production:**
   - Configure SSL certificates in `nginx.conf`
   - Enable HTTPS in production mode

3. **Network Security:**
   - Use internal Docker networks
   - Limit external port exposure

## 📝 Logs and Debugging

### Log Locations

- **Application Logs**: `../logs/`
- **Docker Logs**: `docker-compose logs -f`
- **Nginx Logs**: Inside nginx container

### Log Levels

```env
# In .env file
DEBUG=True  # For development
DEBUG=False # For production
```

## 🤝 Contributing

When modifying Docker configurations:

1. Test changes in development mode first
2. Update documentation
3. Test in simple mode
4. Verify production mode works
5. Update startup scripts if needed

## 📞 Support

For issues related to Docker setup:

1. Check the troubleshooting section
2. Review logs: `docker-compose logs -f`
3. Verify system requirements
4. Check Docker and Docker Compose versions

---

**Happy translating! 🚀** 