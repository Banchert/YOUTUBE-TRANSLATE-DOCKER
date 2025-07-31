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
      'id': '🇮🇩 อินโดนีเซีย',
      'ms': '🇲🇾 มาเลเซีย',
      'lo': '🇱🇦 ลาว',
      'es': '🇪🇸 สเปน',
      'fr': '🇫🇷 ฝรั่งเศส',
      'de': '🇩🇪 เยอรมัน',
      'it': '🇮🇹 อิตาลี',
      'pt': '🇵🇹 โปรตุเกส',
      'ru': '🇷🇺 รัสเซีย',
      'ar': '🇸🇦 อาหรับ',
      'hi': '🇮🇳 ฮินดี',
      'tr': '🇹🇷 ตุรกี'
    };
    return languageMap[code] || code;
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-2">
          🎬 ผลลัพธ์การแปลวิดีโอ
        </h2>
        <p className="text-gray-600">
          วิดีโอที่แปลจาก {getLanguageName(sourceLanguage)} เป็น {getLanguageName(targetLanguage)}
        </p>
      </div>

      {/* Language Information */}
      <div className="mb-6 p-4 bg-green-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div>
              <span className="text-sm font-medium text-gray-600">จาก:</span>
              <span className="ml-2 text-lg">{getLanguageName(sourceLanguage)}</span>
            </div>
            <div className="text-green-500">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-600">เป็น:</span>
              <span className="ml-2 text-lg">{getLanguageName(targetLanguage)}</span>
            </div>
          </div>
          <div className="text-green-600">
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
        </div>
      </div>

      {/* Video Player */}
      <div className="mb-6">
        <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
          {processedVideo ? (
            <video 
              controls 
              className="w-full h-full rounded-lg"
              src={processedVideo.url}
            >
              Your browser does not support the video tag.
            </video>
          ) : (
            <div className="text-center text-gray-500">
              <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p>วิดีโอต้นฉบับ</p>
              <p className="text-sm">(ยังไม่มีการแปล)</p>
            </div>
          )}
        </div>
      </div>

      {/* Download Section */}
      {processedVideo && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="text-lg font-medium text-gray-800 mb-3">
            📥 ดาวน์โหลดผลลัพธ์
          </h3>
          <div className="space-y-2">
            <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
              🎬 ดาวน์โหลดวิดีโอที่แปลแล้ว
            </button>
            <button className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors">
              📝 ดาวน์โหลดซับไตเติล
            </button>
            <button className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors">
              🔊 ดาวน์โหลดไฟล์เสียง
            </button>
          </div>
        </div>
      )}

      {/* Original Video Link */}
      <div className="text-center">
        <a 
          href={originalUrl} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-800 text-sm underline"
        >
          👁️ ดูวิดีโอต้นฉบับบน YouTube
        </a>
      </div>
    </div>
  );
} 
