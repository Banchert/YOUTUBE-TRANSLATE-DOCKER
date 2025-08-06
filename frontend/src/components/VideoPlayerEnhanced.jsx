// Enhanced VideoPlayer component with better error handling and fallbacks
import React, { useState, useEffect, useRef } from 'react';

export default function VideoPlayer({
  originalUrl,
  processedVideo,
  sourceLanguage = 'auto',
  targetLanguage = 'th'
}) {
  const videoRef = useRef(null);
  const [videoError, setVideoError] = useState(null);
  const [videoLoading, setVideoLoading] = useState(false);
  const [videoCanPlay, setVideoCanPlay] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [fileInfo, setFileInfo] = useState(null);

  // ฟังก์ชันสำหรับแปลงรหัสภาษาเป็นชื่อภาษา
  const getLanguageName = (code) => {
    const languageMap = {
      'auto': '🔄 ตรวจจับอัตโนมัติ',
      'th': '🇹🇭 ไทย',
      'en': '🇺🇸 อังกฤษ',
      'zh': '🇨🇳 จีน',
      'ja': '🇯🇵 ญี่ปุ่น',
      'ko': '🇰🇷 เกาหลี',
      'vi': '🇻🇳 เวียดนาม',
      'la': '🇱🇦 ลาว',
      'id': '🇮🇩 อินโดนีเซีย',
      'my': '🇲🇾 มาเลเซีย',
      'es': '🇪🇸 สเปน',
      'fr': '🇫🇷 ฝรั่งเศส',
      'de': '🇩🇪 เยอรมัน',
      'it': '🇮🇹 อิตาลี',
      'pt': '🇵🇹 โปรตุเกส',
      'ru': '🇷🇺 รัสเซีย',
      'ar': '🇸🇦 อาหรับ'
    };
    return languageMap[code] || code;
  };

  // ฟังก์ชันสำหรับแปลง YouTube URL เป็น embed URL
  const getYouTubeEmbedUrl = (url) => {
    const videoId = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/);
    return videoId ? `https://www.youtube.com/embed/${videoId[1]}` : null;
  };

  // ตรวจสอบสถานะ backend และไฟล์
  useEffect(() => {
    if (processedVideo?.video_url) {
      checkBackendAndFile();
    }
  }, [processedVideo?.video_url]);

  const checkBackendAndFile = async () => {
    try {
      // ตรวจสอบ backend health
      setBackendStatus('checking');
      const healthResponse = await fetch('http://localhost:8000/health');
      if (healthResponse.ok) {
        setBackendStatus('healthy');
      } else {
        setBackendStatus('error');
        return;
      }

      // ตรวจสอบไฟล์
      if (processedVideo?.video_url) {
        try {
          const fileResponse = await fetch(processedVideo.video_url, { method: 'HEAD' });
          if (fileResponse.ok) {
            const contentLength = fileResponse.headers.get('content-length');
            const contentType = fileResponse.headers.get('content-type');
            setFileInfo({
              size: contentLength ? parseInt(contentLength) : 0,
              type: contentType || 'unknown',
              exists: true
            });
          } else {
            setFileInfo({ exists: false, error: `HTTP ${fileResponse.status}` });
          }
        } catch (fileError) {
          setFileInfo({ exists: false, error: fileError.message });
        }
      }
    } catch (error) {
      setBackendStatus('error');
      console.error('Backend check failed:', error);
    }
  };

  const handleVideoError = (e) => {
    console.error('Video playback error:', e);
    const video = e.target;
    const error = video.error;
    
    let errorMessage = 'ไม่สามารถเล่นวิดีโอได้';
    if (error) {
      switch (error.code) {
        case error.MEDIA_ERR_ABORTED:
          errorMessage = 'การเล่นวิดีโอถูกยกเลิก';
          break;
        case error.MEDIA_ERR_NETWORK:
          errorMessage = 'เกิดข้อผิดพลาดในการเชื่อมต่อเครือข่าย';
          break;
        case error.MEDIA_ERR_DECODE:
          errorMessage = 'ไม่สามารถเล่นไฟล์วิดีโอได้ (รูปแบบไฟล์ผิดพลาด)';
          break;
        case error.MEDIA_ERR_SRC_NOT_SUPPORTED:
          errorMessage = 'รูปแบบวิดีโอไม่รองรับ หรือไฟล์เสียหาย';
          break;
        default:
          errorMessage = `ข้อผิดพลาด: ${error.message || 'Unknown error'}`;
      }
    }
    
    setVideoError(errorMessage);
    setVideoLoading(false);
    setVideoCanPlay(false);
  };

  const handleVideoLoadStart = () => {
    console.log('Video loading started:', processedVideo?.video_url);
    setVideoLoading(true);
    setVideoError(null);
    setVideoCanPlay(false);
  };

  const handleVideoCanPlay = () => {
    console.log('Video can play');
    setVideoLoading(false);
    setVideoCanPlay(true);
    setVideoError(null);
  };

  const handleVideoLoadedMetadata = () => {
    console.log('Video metadata loaded');
    const video = videoRef.current;
    if (video) {
      console.log(`Video duration: ${video.duration}s, dimensions: ${video.videoWidth}x${video.videoHeight}`);
    }
  };

  const handlePlayVideo = () => {
    const video = videoRef.current;
    if (video) {
      video.play().catch((error) => {
        console.error('Play failed:', error);
        setVideoError('ไม่สามารถเล่นวิดีโอได้ กรุณาลองใหม่');
      });
    }
  };

  const handlePauseVideo = () => {
    const video = videoRef.current;
    if (video) {
      video.pause();
    }
  };

  const handleDownloadVideo = () => {
    if (processedVideo?.video_url) {
      window.open(processedVideo.video_url, '_blank');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes || bytes === 0) return 'ไม่ทราบ';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const embedUrl = getYouTubeEmbedUrl(originalUrl);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Video Player</h3>
        
        {/* Language Information */}
        <div className="bg-blue-50 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div>
                <span className="text-sm text-gray-600">จาก:</span>
                <span className="ml-2 font-medium">{getLanguageName(sourceLanguage)}</span>
              </div>
              <div className="text-gray-400">→</div>
              <div>
                <span className="text-sm text-gray-600">เป็น:</span>
                <span className="ml-2 font-medium">{getLanguageName(targetLanguage)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Original Video */}
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-700 mb-3">วิดีโอต้นฉบับ</h4>
          {embedUrl ? (
            <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
              <iframe
                className="w-full h-full"
                src={embedUrl}
                title="Original YouTube Video"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            </div>
          ) : (
            <div className="bg-gray-100 rounded-lg p-8 text-center">
              <p className="text-gray-500">ไม่สามารถแสดงวิดีโอได้</p>
              <p className="text-sm text-gray-400 mt-2">{originalUrl}</p>
            </div>
          )}
        </div>

        {/* Processed Video */}
        {processedVideo && (
          <div className="mb-6">
            <h4 className="text-lg font-semibold text-gray-700 mb-3">วิดีโอที่แปลแล้ว</h4>
            
            {/* Status Information */}
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Backend Status:</span>
                  <span className={`ml-2 font-medium ${
                    backendStatus === 'healthy' ? 'text-green-600' : 
                    backendStatus === 'error' ? 'text-red-600' : 'text-yellow-600'
                  }`}>
                    {backendStatus === 'healthy' ? '✅ พร้อมใช้งาน' : 
                     backendStatus === 'error' ? '❌ เชื่อมต่อไม่ได้' : '⏳ กำลังตรวจสอบ'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">File Status:</span>
                  <span className={`ml-2 font-medium ${
                    fileInfo?.exists ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {fileInfo?.exists ? `✅ พบไฟล์ (${formatFileSize(fileInfo.size)})` : 
                     fileInfo ? `❌ ไม่พบไฟล์ (${fileInfo.error})` : '⏳ กำลังตรวจสอบ'}
                  </span>
                </div>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                Video URL: {processedVideo.video_url}
              </div>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="font-medium text-green-800">การแปลเสร็จสิ้น</span>
              </div>
            </div>
            
            {/* Video Player with Enhanced Error Handling */}
            <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden relative">
              {videoLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50 z-10">
                  <div className="text-white text-center">
                    <svg className="animate-spin h-8 w-8 mx-auto mb-2" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <p>กำลังโหลดวิดีโอ...</p>
                  </div>
                </div>
              )}
              
              {videoError ? (
                <div className="w-full h-full flex items-center justify-center bg-red-50">
                  <div className="text-center p-6">
                    <svg className="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                    <p className="text-red-700 font-medium mb-2">เกิดข้อผิดพลาด</p>
                    <p className="text-red-600 text-sm mb-4">{videoError}</p>
                    <div className="space-y-2">
                      <button
                        onClick={checkBackendAndFile}
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                      >
                        🔄 ตรวจสอบใหม่
                      </button>
                      <button
                        onClick={handleDownloadVideo}
                        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm ml-2"
                      >
                        📥 ดาวน์โหลดแทน
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <video
                  ref={videoRef}
                  className="w-full h-full"
                  controls
                  preload="metadata"
                  crossOrigin="anonymous"
                  onError={handleVideoError}
                  onLoadStart={handleVideoLoadStart}
                  onCanPlay={handleVideoCanPlay}
                  onLoadedMetadata={handleVideoLoadedMetadata}
                >
                  <source src={processedVideo.video_url} type="video/mp4" />
                  <p className="text-center text-gray-500 p-4">
                    ไม่สามารถเล่นวิดีโอได้ กรุณาใช้ปุ่มดาวน์โหลดด้านล่าง
                  </p>
                </video>
              )}
            </div>

            {/* Enhanced Video Controls */}
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                onClick={handlePlayVideo}
                disabled={!videoCanPlay}
                className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center ${
                  videoCanPlay
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                เล่นวิดีโอ
              </button>
              
              <button
                onClick={handlePauseVideo}
                disabled={!videoCanPlay}
                className={`px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center ${
                  videoCanPlay
                    ? 'bg-gray-600 hover:bg-gray-700 text-white'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                หยุด
              </button>

              <button
                onClick={handleDownloadVideo}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors duration-200 flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                ดาวน์โหลด
              </button>

              <button
                onClick={checkBackendAndFile}
                className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-medium transition-colors duration-200 flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                ตรวจสอบ
              </button>
            </div>

            {/* Video Information */}
            <div className="mt-4 bg-gray-50 rounded-lg p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Task ID:</span>
                  <span className="ml-2 font-mono text-gray-800">{processedVideo.task_id}</span>
                </div>
                <div>
                  <span className="text-gray-600">สถานะ:</span>
                  <span className="ml-2 text-green-600 font-medium">เสร็จสิ้น</span>
                </div>
                <div>
                  <span className="text-gray-600">Video URL:</span>
                  <span className="ml-2 text-xs text-gray-500 break-all">{processedVideo.video_url}</span>
                </div>
                <div>
                  <span className="text-gray-600">File Info:</span>
                  <span className="ml-2 text-xs text-gray-500">
                    {fileInfo ? (fileInfo.exists ? `${fileInfo.type}, ${formatFileSize(fileInfo.size)}` : 'ไม่พบไฟล์') : 'กำลังตรวจสอบ...'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Original URL Info */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h5 className="font-medium text-gray-700 mb-2">ข้อมูลวิดีโอ</h5>
          <p className="text-sm text-gray-600 break-all">{originalUrl}</p>
        </div>
      </div>
    </div>
  );
} 
