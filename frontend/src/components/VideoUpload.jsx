import React, { useState } from 'react';
import LanguageSelector from './LanguageSelector';

export default function VideoUpload({ onTaskStart }) {
  const [url, setUrl] = useState('');
  const [sourceLanguage, setSourceLanguage] = useState('auto');
  const [targetLanguage, setTargetLanguage] = useState('th');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('กรุณาใส่ URL ของวิดีโอ YouTube');
      return;
    }

    // Validate YouTube URL
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
    if (!youtubeRegex.test(url)) {
      setError('กรุณาใส่ URL ของ YouTube ที่ถูกต้อง');
      return;
    }

    setIsLoading(true);
    setError('');

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
      setError('เกิดข้อผิดพลาดในการเริ่มต้นการแปล');
    } finally {
      setIsLoading(false);
    }
  };

  return ( 
    <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2m-9 0h10m-10 0a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V6a2 2 0 00-2-2" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">เริ่มต้นการแปลวิดีโอ</h2>
        <p className="text-gray-600">ใส่ URL ของวิดีโอ YouTube ที่ต้องการแปล</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="youtube-url" className="block text-sm font-medium text-gray-700 mb-2">
            YouTube URL
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <input 
              id="youtube-url"
              type="text" 
              value={url} 
              onChange={(e) => {
                setUrl(e.target.value);
                setError('');
              }}
              placeholder="https://www.youtube.com/watch?v=..." 
              className={`w-full pl-10 pr-4 py-4 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                error ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-gray-400'
              }`}
              disabled={isLoading}
            />
          </div>
          {error && (
            <p className="mt-2 text-sm text-red-600 flex items-center">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ภาษาต้นทาง
            </label>
            <LanguageSelector 
              value={sourceLanguage}
              onChange={setSourceLanguage}
              placeholder="เลือกภาษาต้นทาง"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ภาษาปลายทาง
            </label>
            <LanguageSelector 
              value={targetLanguage}
              onChange={setTargetLanguage}
              placeholder="เลือกภาษาปลายทาง"
            />
          </div>
        </div>

        <button 
          type="submit"
          disabled={isLoading || !url.trim()}
          className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all duration-200 ${
            isLoading || !url.trim()
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 shadow-lg hover:shadow-xl'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              กำลังเริ่มต้น...
            </div>
          ) : (
            'เริ่มต้นการแปล'
          )}
        </button>
      </form>

      {/* Instructions */}
      <div className="mt-8 p-4 bg-blue-50 rounded-xl">
        <h3 className="font-semibold text-blue-800 mb-2 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          วิธีการใช้งาน
        </h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• คัดลอก URL จากวิดีโอ YouTube ที่ต้องการแปล</li>
          <li>• เลือกภาษาต้นทางและภาษาปลายทาง</li>
          <li>• กดปุ่ม "เริ่มต้นการแปล"</li>
          <li>• รอสักครู่ระบบจะประมวลผลและแปลวิดีโอให้</li>
        </ul>
      </div>
    </div> 
  ); 
} 
