// API Service for YouTube Video Translator
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.wsURL = WS_URL;
  }

  // Helper method for API calls
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return response;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }

  // Start translation task
  async startTranslation(data) {
    // Check if it's a file upload or YouTube URL
    if (data.file_path) {
      return this.request('/translate-file', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    } else {
      return this.request('/translate', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    }
  }

  // Get task status
  async getTaskStatus(taskId) {
    return this.request(`/status/${taskId}`);
  }

  // Cancel task
  async cancelTask(taskId) {
    return this.request(`/tasks/${taskId}/cancel`, {
      method: 'POST',
    });
  }

  // Get task history
  async getTaskHistory(limit = 10) {
    return this.request(`/tasks?limit=${limit}`);
  }

  // Download file
  async downloadFile(fileUrl, filename) {
    try {
      console.log(`Starting download from: ${fileUrl}`);
      
      const response = await fetch(fileUrl);
      
      if (!response.ok) {
        throw new Error(`Download failed: HTTP ${response.status} - ${response.statusText}`);
      }
      
      // Check if we got actual content
      const contentLength = response.headers.get('content-length');
      if (contentLength && parseInt(contentLength) < 100) {
        console.warn('File seems too small, might be a placeholder');
      }
      
      const blob = await response.blob();
      
      // Check blob size
      if (blob.size < 100) {
        console.warn(`Downloaded file is very small (${blob.size} bytes), might be a placeholder`);
      }
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      
      // Add to DOM, click, and cleanup
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log(`Download completed: ${filename} (${blob.size} bytes)`);
      return true;
      
    } catch (error) {
      console.error('Download failed:', error);
      
      // Provide more specific error messages
      if (error.message.includes('404')) {
        throw new Error('ไฟล์ไม่พบ - อาจยังไม่เสร็จสิ้นการประมวลผล');
      } else if (error.message.includes('403')) {
        throw new Error('ไม่มีสิทธิ์เข้าถึงไฟล์');
      } else if (error.message.includes('500')) {
        throw new Error('เซิร์ฟเวอร์เกิดข้อผิดพลาด');
      } else if (error.message.includes('Failed to fetch')) {
        throw new Error('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
      } else {
        throw error;
      }
    }
  }

  // Get download URL
  getDownloadUrl(taskId, type) {
    const endpoints = {
      video: `/download/${taskId}`,
      audio: `/download/${taskId}/audio`,
      subtitle: `/download/${taskId}/subtitle`,
    };
    
    return `${this.baseURL}${endpoints[type] || endpoints.video}`;
  }

  // Upload video file
  async uploadVideo(file, onProgress = null) {
    const formData = new FormData();
    formData.append('video', file);

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      // Set timeout (5 minutes for large files)
      xhr.timeout = 5 * 60 * 1000; // 5 minutes

      if (onProgress) {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            onProgress(percentComplete);
          }
        });
      }

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            console.log('Upload successful:', response);
            resolve(response);
          } catch (error) {
            console.error('Invalid JSON response:', xhr.responseText);
            reject(new Error('Invalid server response'));
          }
        } else {
          let errorMessage = `Upload failed: HTTP ${xhr.status}`;
          try {
            const errorResponse = JSON.parse(xhr.responseText);
            if (errorResponse.detail) {
              errorMessage = errorResponse.detail;
            }
          } catch (e) {
            // Use default error message if can't parse response
          }
          
          console.error('Upload failed:', xhr.status, xhr.responseText);
          reject(new Error(errorMessage));
        }
      });

      xhr.addEventListener('error', () => {
        console.error('Upload network error');
        reject(new Error('Network error - ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้'));
      });

      xhr.addEventListener('timeout', () => {
        console.error('Upload timeout');
        reject(new Error('Upload timeout - ไฟล์ใหญ่เกินไปหรือการเชื่อมต่อช้า'));
      });

      xhr.addEventListener('abort', () => {
        console.error('Upload aborted');
        reject(new Error('Upload aborted - การอัปโหลดถูกยกเลิก'));
      });

      try {
        xhr.open('POST', `${this.baseURL}/upload`);
        xhr.send(formData);
      } catch (error) {
        console.error('Upload setup error:', error);
        reject(new Error('Upload setup failed - ไม่สามารถเริ่มการอัปโหลดได้'));
      }
    });
  }

  // Get supported languages
  async getSupportedLanguages() {
    return this.request('/languages');
  }

  // Get statistics
  async getStatistics() {
    return this.request('/stats');
  }

  // Create share link
  async createShareLink(data) {
    return this.request('/share', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // WebSocket connection for real-time updates
  connectWebSocket(taskId, callbacks = {}) {
    const wsUrl = `${this.wsURL.replace('http', 'ws')}/ws/${taskId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      if (callbacks.onOpen) callbacks.onOpen();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (callbacks.onMessage) callbacks.onMessage(data);
      } catch (error) {
        console.error('WebSocket message parse error:', error);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      if (callbacks.onClose) callbacks.onClose();
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (callbacks.onError) callbacks.onError(error);
    };

    return ws;
  }

  // Mock data for development (remove in production)
  async getMockTaskProgress(taskId) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    const mockProgresses = [
      { step: 'download', progress: 100, message: 'วิดีโอดาวน์โหลดเสร็จแล้ว' },
      { step: 'extract', progress: 100, message: 'แยกเสียงเสร็จแล้ว' },
      { step: 'transcribe', progress: 75, message: 'กำลังแปลงเสียงเป็นข้อความ...' },
      { step: 'translate', progress: 0, message: 'รอการแปลข้อความ' },
      { step: 'synthesize', progress: 0, message: 'รอการสังเคราะห์เสียง' },
      { step: 'merge', progress: 0, message: 'รอการรวมไฟล์' },
    ];

    return {
      task_id: taskId,
      status: 'processing',
      current_step: 'transcribe',
      progress: mockProgresses,
      estimated_time_remaining: 300, // seconds
    };
  }

  async getMockTaskResult(taskId) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    return {
      task_id: taskId,
      status: 'completed',
      source_language: 'en',
      target_language: 'th',
      video_url: `${this.baseURL}/static/translated_video_${taskId}.mp4`,
      audio_url: `${this.baseURL}/static/translated_audio_${taskId}.mp3`,
      subtitle_url: `${this.baseURL}/static/subtitles_${taskId}.srt`,
      original_duration: 930, // seconds
      file_sizes: {
        video: 157286400, // bytes
        audio: 14876800,
        subtitle: 2048,
      },
      created_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
    };
  }
}

// Export singleton instance
const apiService = new ApiService();
export default apiService;

// Export individual methods for convenience
export const {
  healthCheck,
  startTranslation,
  getTaskStatus,
  cancelTask,
  getTaskHistory,
  downloadFile,
  getDownloadUrl,
  uploadVideo,
  getSupportedLanguages,
  getStatistics,
  createShareLink,
  connectWebSocket,
  getMockTaskProgress,
  getMockTaskResult,
} = apiService;