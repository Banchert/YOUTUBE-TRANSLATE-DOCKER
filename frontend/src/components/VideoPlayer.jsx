// VideoPlayer component with language information
import React from 'react';

export default function VideoPlayer({
  originalUrl,
  processedVideo,
  sourceLanguage = 'auto',
  targetLanguage = 'th'
}) {
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
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="font-medium text-green-800">การแปลเสร็จสิ้น</span>
              </div>
            </div>
            
            <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
              <video
                className="w-full h-full"
                controls
                preload="metadata"
              >
                <source src={processedVideo.video_url} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>

            {/* Video Controls */}
            <div className="mt-4 flex space-x-3">
              <button
                onClick={() => {
                  const video = document.querySelector('video');
                  if (video) video.play();
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                เล่นวิดีโอ
              </button>
              
              <button
                onClick={() => {
                  const video = document.querySelector('video');
                  if (video) video.pause();
                }}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                หยุด
              </button>
            </div>

            {/* Video Information */}
            <div className="mt-4 bg-gray-50 rounded-lg p-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Task ID:</span>
                  <span className="ml-2 font-mono text-gray-800">{processedVideo.task_id}</span>
                </div>
                <div>
                  <span className="text-gray-600">สถานะ:</span>
                  <span className="ml-2 text-green-600 font-medium">เสร็จสิ้น</span>
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
