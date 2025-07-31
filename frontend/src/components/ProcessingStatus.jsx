// ProcessingStatus component with language information
import React from 'react';
import ProgressBar from './ProgressBar';
import StatusBadge from './StatusBadge';

export default function ProcessingStatus({ 
  taskId, 
  sourceLanguage = 'auto',
  targetLanguage = 'th',
  onComplete, 
  onReset 
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
          ⚙️ กำลังประมวลผลวิดีโอ
        </h2>
        <p className="text-gray-600">
          ระบบกำลังแปลวิดีโอของคุณ กรุณารอสักครู่...
        </p>
      </div>

      {/* Language Information */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div>
              <span className="text-sm font-medium text-gray-600">จาก:</span>
              <span className="ml-2 text-lg">{getLanguageName(sourceLanguage)}</span>
            </div>
            <div className="text-blue-500">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-600">เป็น:</span>
              <span className="ml-2 text-lg">{getLanguageName(targetLanguage)}</span>
            </div>
          </div>
          <StatusBadge status="processing" />
        </div>
      </div>

      {/* Task ID */}
      <div className="mb-4">
        <span className="text-sm text-gray-500">Task ID: {taskId}</span>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <ProgressBar progress={65} />
        <p className="text-sm text-gray-600 mt-2">
          ขั้นตอนที่ 3/5: กำลังแปลข้อความเป็นเสียง...
        </p>
      </div>

      {/* Processing Steps */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-700 mb-3">ขั้นตอนการประมวลผล:</h3>
        <div className="space-y-2">
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <span className="text-sm text-gray-600">ดาวน์โหลดวิดีโอ</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <span className="text-sm text-gray-600">แปลงเสียงเป็นข้อความ</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
            </div>
            <span className="text-sm text-gray-800 font-medium">แปลข้อความเป็นเสียง</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center">
              <span className="text-xs text-gray-500">4</span>
            </div>
            <span className="text-sm text-gray-400">รวมเสียงกับวิดีโอ</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center">
              <span className="text-xs text-gray-500">5</span>
            </div>
            <span className="text-sm text-gray-400">สร้างไฟล์ผลลัพธ์</span>
          </div>
        </div>
      </div>

      {/* Cancel Button */}
      <div className="flex justify-end">
        <button
          onClick={onReset}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
        >
          ยกเลิก
        </button>
      </div>
    </div>
  );
} 
