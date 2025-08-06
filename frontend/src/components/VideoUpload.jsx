import React, { useState, useRef } from 'react';
import LanguageSelector from './LanguageSelector';

export default function VideoUpload({ onTaskStart }) {
  const [url, setUrl] = useState('');
  const [sourceLanguage, setSourceLanguage] = useState('auto');
  const [targetLanguage, setTargetLanguage] = useState('th');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['video/mp4', 'video/webm', 'video/avi', 'video/mkv', 'video/mov'];
    if (!allowedTypes.includes(file.type)) {
      setError('กรุณาเลือกไฟล์วิดีโอที่ถูกต้อง (MP4, WebM, AVI, MKV, MOV)');
      return;
    }

    // Validate file size (max 500MB)
    const maxSize = 500 * 1024 * 1024; // 500MB
    if (file.size > maxSize) {
      setError('ขนาดไฟล์ต้องไม่เกิน 500MB');
      return;
    }

    setError('');
    setUploadedFile(file);
    setUrl(''); // Clear URL when file is uploaded
  };

  const handleUrlChange = (e) => {
    setUrl(e.target.value);
    setError('');
    setUploadedFile(null); // Clear file when URL is entered
  };

  const handleLanguageChange = (type, value) => {
    if (type === 'source') {
      setSourceLanguage(value);
    } else {
      setTargetLanguage(value);
    }
    // Don't auto-start translation when language changes
  };

  const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('video', file);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      return result.file_path;
    } catch (error) {
      console.error('Upload error:', error);
      throw new Error('เกิดข้อผิดพลาดในการอัพโหลดไฟล์');
    }
  };

  const handleTranslate = async () => {
    if (!url.trim() && !uploadedFile) {
      setError('กรุณาใส่ URL หรืออัพโหลดไฟล์วิดีโอ');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      let taskData = {
        source_language: sourceLanguage,
        target_language: targetLanguage
      };

      if (uploadedFile) {
        // Upload file first
        setUploadProgress(50);
        const filePath = await uploadFile(uploadedFile);
        setUploadProgress(100);
        
        taskData.file_path = filePath;
      } else if (url.trim()) {
        // Validate YouTube URL
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
        if (!youtubeRegex.test(url)) {
          throw new Error('กรุณาใส่ URL ของ YouTube ที่ถูกต้อง');
        }
        
        taskData.youtube_url = url;
      }

      // Start translation
      await onTaskStart(taskData);
      
      // Reset form
      setUrl('');
      setUploadedFile(null);
      setUploadProgress(0);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
    } catch (error) {
      console.error('Error starting task:', error);
      
      // Handle specific YouTube blocking errors
      if (error.message && error.message.includes('blocking downloads')) {
        setError(
          'YouTube ถูกบล็อกการดาวน์โหลด กรุณาดาวน์โหลดวิดีโอด้วยตนเองแล้วอัพโหลดไฟล์โดยตรง'
        );
      } else if (error.message && error.message.includes('413')) {
        setError(
          'ไฟล์มีขนาดใหญ่เกินไป กรุณาเลือกไฟล์ที่มีขนาดไม่เกิน 500MB'
        );
      } else {
        setError(error.message || 'เกิดข้อผิดพลาดในการเริ่มต้นการแปล');
      }
    } finally {
      setIsLoading(false);
      setUploadProgress(0);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.classList.add('border-blue-500', 'bg-blue-50');
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      const event = { target: { files: [file] } };
      handleFileUpload(event);
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
        <p className="text-gray-600">ใส่ URL ของวิดีโอ YouTube หรืออัพโหลดไฟล์วิดีโอ</p>
      </div>

      <div className="space-y-6">
        {/* File Upload Section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            อัพโหลดไฟล์วิดีโอ
          </label>
          <div
            className={`border-2 border-dashed rounded-xl p-6 text-center transition-all ${
              uploadedFile 
                ? 'border-green-300 bg-green-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileUpload}
              className="hidden"
            />
            
            {uploadedFile ? (
              <div className="space-y-2">
                <svg className="w-12 h-12 text-green-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-green-700 font-medium">{uploadedFile.name}</p>
                <p className="text-sm text-green-600">
                  {(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
                <button
                  onClick={() => {
                    setUploadedFile(null);
                    if (fileInputRef.current) fileInputRef.current.value = '';
                  }}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  ลบไฟล์
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <svg className="w-12 h-12 text-gray-400 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-gray-600">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    คลิกเพื่อเลือกไฟล์
                  </button>
                  {' '}หรือลากไฟล์มาวางที่นี่
                </p>
                <p className="text-xs text-gray-500">
                  รองรับ MP4, WebM, AVI, MKV, MOV (สูงสุด 500MB)
                </p>
              </div>
            )}
          </div>
        </div>

        {/* OR Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">หรือ</span>
          </div>
        </div>

        {/* YouTube URL Section */}
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
              onChange={handleUrlChange}
              placeholder="https://www.youtube.com/watch?v=..." 
              className={`w-full pl-10 pr-4 py-4 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                error ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-gray-400'
              }`}
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Language Selection */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ภาษาต้นทาง
            </label>
            <LanguageSelector 
              value={sourceLanguage}
              onChange={(value) => handleLanguageChange('source', value)}
              placeholder="เลือกภาษาต้นทาง"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ภาษาปลายทาง
            </label>
            <LanguageSelector 
              value={targetLanguage}
              onChange={(value) => handleLanguageChange('target', value)}
              placeholder="เลือกภาษาปลายทาง"
            />
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
            <p className="text-sm text-red-600 flex items-center">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </p>
          </div>
        )}

        {/* Upload Progress */}
        {uploadProgress > 0 && uploadProgress < 100 && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>กำลังอัพโหลด...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Translate Button */}
        <button 
          onClick={handleTranslate}
          disabled={isLoading || (!url.trim() && !uploadedFile)}
          className={`w-full py-4 px-6 rounded-xl font-semibold text-white transition-all duration-200 ${
            isLoading || (!url.trim() && !uploadedFile)
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
      </div>

      {/* Instructions */}
      <div className="mt-8 p-4 bg-blue-50 rounded-xl">
        <h3 className="font-semibold text-blue-800 mb-2 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          วิธีการใช้งาน
        </h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• <strong>แนะนำ:</strong> อัพโหลดไฟล์วิดีโอโดยตรง (รองรับสูงสุด 500MB)</li>
          <li>• หรือใส่ URL ของวิดีโอ YouTube (อาจล้มเหลวเพราะ YouTube ถูกบล็อก)</li>
          <li>• เลือกภาษาต้นทางและภาษาปลายทาง</li>
          <li>• กดปุ่ม "เริ่มต้นการแปล" เพื่อเริ่มการประมวลผล</li>
          <li>• รอสักครู่ระบบจะประมวลผลและแปลวิดีโอให้</li>
        </ul>
      </div>

      {/* YouTube Warning */}
      <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
        <h3 className="font-semibold text-yellow-800 mb-2 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          หมายเหตุสำคัญ
        </h3>
        <div className="text-sm text-yellow-700 space-y-1">
          <p><strong>YouTube URLs อาจล้มเหลว:</strong> YouTube ถูกบล็อกการดาวน์โหลดอัตโนมัติ</p>
          <p><strong>วิธีแก้ไข:</strong> ดาวน์โหลดวิดีโอด้วยตนเองแล้วอัพโหลดไฟล์โดยตรง</p>
          <p><strong>รองรับไฟล์:</strong> MP4, WebM, AVI, MKV, MOV (สูงสุด 500MB)</p>
        </div>
      </div>
    </div> 
  ); 
} 
