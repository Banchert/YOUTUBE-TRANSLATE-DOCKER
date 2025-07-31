# 🤝 Contributing to YouTube Video Translator

ขอบคุณที่สนใจในการ contribute โปรเจค YouTube Video Translator! 

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## 📜 Code of Conduct

โปรเจคนี้มุ่งมั่นที่จะเป็นพื้นที่ที่เปิดกว้างและเป็นมิตรสำหรับทุกคน โดยไม่คำนึงถึงประสบการณ์ ระดับความเชี่ยวชาญ เพศ อัตลักษณ์ทางเพศ และการแสดงออกทางเพศ

## 🚀 How Can I Contribute?

### 🐛 Reporting Bugs

- ใช้ [GitHub Issues](https://github.com/yourusername/youtube-translate/issues) template
- อธิบายปัญหาอย่างชัดเจนและครบถ้วน
- รวมข้อมูลระบบและขั้นตอนการทำซ้ำ

### 💡 Suggesting Enhancements

- ใช้ [Feature Request](https://github.com/yourusername/youtube-translate/issues/new?template=feature_request.md) template
- อธิบายประโยชน์และกรณีการใช้งาน
- เสนอแนวทางการ implement หากเป็นไปได้

### 🔧 Code Contributions

- Fork repository
- สร้าง feature branch
- เขียนโค้ดตาม coding standards
- เพิ่ม tests หากจำเป็น
- ส่ง Pull Request

## 🛠️ Development Setup

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Docker Desktop**
- **Git**

### Backend Development

```bash
# Clone repository
git clone https://github.com/yourusername/youtube-translate.git
cd youtube-translate

# Setup Python environment
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Setup Node.js environment
cd frontend
npm install

# Run development server
npm start
```

### Docker Development

```bash
# Start all services
docker-compose -f docker/docker-compose-simple.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📝 Coding Standards

### Python (Backend)

- ใช้ **Black** สำหรับ code formatting
- ใช้ **Flake8** สำหรับ linting
- ใช้ **Type hints** สำหรับ function parameters
- เขียน **docstrings** สำหรับ functions และ classes
- ใช้ **async/await** สำหรับ I/O operations

```python
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

async def process_video(
    video_url: str, 
    target_language: str
) -> Dict[str, Any]:
    """
    Process YouTube video for translation.
    
    Args:
        video_url: YouTube video URL
        target_language: Target language code
        
    Returns:
        Dictionary containing processing results
        
    Raises:
        ValueError: If video URL is invalid
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise
```

### JavaScript/React (Frontend)

- ใช้ **ESLint** และ **Prettier**
- ใช้ **Functional Components** และ **Hooks**
- ใช้ **TypeScript** หากเป็นไปได้
- เขียน **JSDoc** สำหรับ functions
- ใช้ **Tailwind CSS** สำหรับ styling

```javascript
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Video upload component with language selection
 * @param {Object} props - Component props
 * @param {Function} props.onTaskStart - Callback when task starts
 * @param {string} props.className - Additional CSS classes
 */
const VideoUpload = ({ onTaskStart, className = '' }) => {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!url.trim()) return;
    
    setIsLoading(true);
    try {
      await onTaskStart({ youtube_url: url });
    } catch (error) {
      console.error('Error starting task:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`video-upload ${className}`}>
      {/* Component JSX */}
    </div>
  );
};

VideoUpload.propTypes = {
  onTaskStart: PropTypes.func.isRequired,
  className: PropTypes.string
};

export default VideoUpload;
```

## 🔄 Pull Request Process

### 1. Fork และ Clone

```bash
# Fork repository บน GitHub
# Clone fork ของคุณ
git clone https://github.com/yourusername/youtube-translate.git
cd youtube-translate

# เพิ่ม upstream remote
git remote add upstream https://github.com/original-owner/youtube-translate.git
```

### 2. สร้าง Feature Branch

```bash
# อัปเดต main branch
git checkout main
git pull upstream main

# สร้าง feature branch
git checkout -b feature/amazing-feature
```

### 3. พัฒนาและ Test

```bash
# เขียนโค้ด
# รัน tests
npm test  # Frontend
pytest    # Backend

# Commit changes
git add .
git commit -m "feat: add amazing feature"
```

### 4. Push และ Create PR

```bash
# Push ไปยัง fork
git push origin feature/amazing-feature

# สร้าง Pull Request บน GitHub
```

### 5. PR Template

```markdown
## 📝 Description
อธิบายการเปลี่ยนแปลงที่ทำ

## 🔧 Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## 🧪 Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## 📸 Screenshots (if applicable)
เพิ่ม screenshots หากมีการเปลี่ยนแปลง UI

## ✅ Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
## 🐛 Bug Description
อธิบายปัญหาที่พบ

## 🔄 Steps to Reproduce
1. ไปที่ '...'
2. คลิก '....'
3. เลื่อนลงไปที่ '....'
4. เห็นข้อผิดพลาด

## ✅ Expected Behavior
อธิบายสิ่งที่ควรเกิดขึ้น

## ❌ Actual Behavior
อธิบายสิ่งที่เกิดขึ้นจริง

## 📱 Environment
- OS: [e.g. Windows 10, macOS 12]
- Browser: [e.g. Chrome 100, Firefox 99]
- Version: [e.g. 1.0.0]

## 📋 Additional Information
ข้อมูลเพิ่มเติมที่เกี่ยวข้อง
```

## 💡 Suggesting Enhancements

### Feature Request Template

```markdown
## 💡 Feature Description
อธิบายฟีเจอร์ที่ต้องการ

## 🎯 Use Case
อธิบายกรณีการใช้งาน

## 💭 Proposed Solution
เสนอแนวทางการ implement

## 🔄 Alternatives Considered
ทางเลือกอื่นที่พิจารณาแล้ว

## 📱 Mockups/Screenshots
เพิ่ม mockups หากเป็น UI feature
```

## 📚 Resources

- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [React Best Practices](https://reactjs.org/docs/hooks-rules.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🙏 Thank You!

ขอบคุณที่ช่วยพัฒนา YouTube Video Translator ให้ดีขึ้น! 🚀 