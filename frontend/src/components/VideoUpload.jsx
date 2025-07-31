// VideoUpload component with language selection
import React, { useState } from 'react';
import LanguageSelector from './LanguageSelector';

export default function VideoUpload({ onTaskStart }) {
  const [url, setUrl] = useState('');
  const [sourceLanguage, setSourceLanguage] = useState('auto');
  const [targetLanguage, setTargetLanguage] = useState('th');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!url.trim()) {
      alert('กรุณาใส่ YouTube URL');
      return;
    }

    setIsLoading(true);
    
    try {
      // เรียกใช้ callback function
      await onTaskStart({ 
        youtube_url: url, 
        source_language: sourceLanguage,
        target_language: targetLanguage,
        task_id: `task-${Date.now()}` 
      });
      
      // รีเซ็ตฟอร์ม
      setUrl('');
    } catch (error) {
      console.error('Error starting task:', error);
      alert('เกิดข้อผิดพลาดในการเริ่มงาน');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUrlChange = (e) => {
    setUrl(e.target.value);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-2">
          🎬 แปลวิดีโอ YouTube
        </h2>
        <p className="text-gray-600">
          ใส่ลิงก์ YouTube และเลือกภาษาที่ต้องการแปล
        </p>
      </div>

      {/* YouTube URL Input */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          📺 YouTube URL
        </label>
        <input
          type="text"
          value={url}
          onChange={handleUrlChange}
          placeholder="https://www.youtube.com/watch?v=..."
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
          disabled={isLoading}
        />
      </div>

      {/* Language Selection */}
      <div className="mb-6">
        <LanguageSelector
          sourceLanguage={sourceLanguage}
          targetLanguage={targetLanguage}
          onSourceLanguageChange={setSourceLanguage}
          onTargetLanguageChange={setTargetLanguage}
        />
      </div>

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSubmit}
          disabled={isLoading || !url.trim()}
          className={`
            px-6 py-3 rounded-lg font-medium transition-all duration-200
            ${isLoading || !url.trim()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 shadow-md hover:shadow-lg'
            }
          `}
        >
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>กำลังเริ่ม...</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <span>🚀 เริ่มแปลวิดีโอ</span>
            </div>
          )}
        </button>
      </div>

      {/* Help Text */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-700">
          💡 <strong>เคล็ดลับ:</strong> ระบบจะตรวจจับภาษาต้นทางอัตโนมัติ หรือคุณสามารถเลือกภาษาเองได้
        </p>
      </div>
    </div>
  );
} 
