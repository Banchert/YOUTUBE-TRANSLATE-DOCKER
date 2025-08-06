import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import apiService from '../services/api';

const DownloadResult = ({ result, onDownload, onReset }) => {
  const [activeTab, setActiveTab] = useState('video');
  const [showShareModal, setShowShareModal] = useState(false);
  const [downloading, setDownloading] = useState({});
  const [shareLink, setShareLink] = useState('');
  const [showVideoPreview, setShowVideoPreview] = useState(false);

  if (!result) return null;

  const downloadOptions = [
    {
      type: 'video',
      title: 'วิดีโอที่แปลแล้ว',
      description: 'วิดีโอพร้อมเสียงพากย์ใหม่',
      icon: '🎬',
      color: 'from-blue-500 to-cyan-500',
      format: 'MP4',
      size: result.file_sizes?.video ? formatFileSize(result.file_sizes.video) : '~150MB',
      url: result.video_url
    },
    {
      type: 'audio',
      title: 'เสียงพากย์',
      description: 'ไฟล์เสียงพากย์เท่านั้น',
      icon: '🎵',
      color: 'from-purple-500 to-pink-500',
      format: 'MP3',
      size: result.file_sizes?.audio ? formatFileSize(result.file_sizes.audio) : '~15MB',
      url: result.audio_url
    },
    {
      type: 'subtitle',
      title: 'ซับไตเติล',
      description: 'ไฟล์ซับไตเติลสำหรับนำไปใช้',
      icon: '📝',
      color: 'from-green-500 to-emerald-500',
      format: 'SRT',
      size: result.file_sizes?.subtitle ? formatFileSize(result.file_sizes.subtitle) : '~50KB',
      url: result.subtitle_url
    }
  ];

  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  const handleDownload = async (type) => {
    try {
      setDownloading(prev => ({ ...prev, [type]: true }));
      
      // Use API service to get the correct download URL
      const downloadUrl = apiService.getDownloadUrl(result.task_id, type);
      
      // Generate filename
      const timestamp = new Date().toISOString().slice(0, 10);
      const option = downloadOptions.find(opt => opt.type === type);
      const filename = `${type}_${result.task_id}_${timestamp}.${option.format.toLowerCase()}`;
      
      console.log(`Downloading ${type} from: ${downloadUrl}`);
      
      // Check if the file exists first
      try {
        const checkResponse = await fetch(downloadUrl, { method: 'HEAD' });
        if (!checkResponse.ok) {
          throw new Error(`File not available: HTTP ${checkResponse.status}`);
        }
      } catch (checkError) {
        console.warn(`File check failed for ${type}:`, checkError);
        // Continue anyway, the download might still work
      }
      
      // Use API service to download
      await apiService.downloadFile(downloadUrl, filename);
      
      // Also call the parent handler if provided
      if (onDownload) {
        onDownload(type);
      }

      // Show success message
      console.log(`Downloaded ${type} successfully`);
      
      // Show success toast or notification
      if (window.showToast) {
        window.showToast(`ดาวน์โหลด ${option.title} สำเร็จ!`, 'success');
      } else {
        alert(`ดาวน์โหลด ${option.title} สำเร็จ!`);
      }
      
    } catch (error) {
      console.error(`Download failed for ${type}:`, error);
      
      // More detailed error message
      let errorMessage = `ไม่สามารถดาวน์โหลด ${type} ได้`;
      if (error.message.includes('File not available')) {
        errorMessage = `ไฟล์ ${type} ยังไม่พร้อมใช้งาน`;
      } else if (error.message.includes('Network')) {
        errorMessage = `เกิดข้อผิดพลาดในการเชื่อมต่อ`;
      }
      
      if (window.showToast) {
        window.showToast(errorMessage, 'error');
      } else {
        alert(errorMessage);
      }
    } finally {
      setDownloading(prev => ({ ...prev, [type]: false }));
    }
  };

  const handleShare = async () => {
    try {
      const response = await apiService.createShareLink({
        task_id: result.task_id,
        expires_in: 24 * 60 * 60 // 24 hours
      });
      
      setShareLink(response.data.share_url);
      setShowShareModal(true);
    } catch (error) {
      console.error('Share failed:', error);
      if (window.showToast) {
        window.showToast('ไม่สามารถสร้างลิงก์แชร์ได้', 'error');
      } else {
        alert('ไม่สามารถสร้างลิงก์แชร์ได้');
      }
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      if (window.showToast) {
        window.showToast('คัดลอกลิงก์แล้ว!', 'success');
      } else {
        alert('คัดลอกลิงก์แล้ว!');
      }
    } catch (error) {
      console.error('Copy failed:', error);
      if (window.showToast) {
        window.showToast('ไม่สามารถคัดลอกลิงก์ได้', 'error');
      } else {
        alert('ไม่สามารถคัดลอกลิงก์ได้');
      }
    }
  };

  const getLanguageName = (code) => {
    const languages = {
      'th': 'ไทย',
      'en': 'อังกฤษ',
      'zh': 'จีน',
      'ja': 'ญี่ปุ่น',
      'ko': 'เกาหลี',
      'es': 'สเปน',
      'fr': 'ฝรั่งเศส',
      'de': 'เยอรมัน'
    };
    return languages[code] || code;
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'ไม่ทราบ';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100"
    >
      {/* Success Header */}
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">การแปลเสร็จสิ้น!</h2>
        <p className="text-gray-600">วิดีโอของคุณพร้อมใช้งานแล้ว</p>
      </div>

      {/* Video Preview */}
      <div className="mb-8">
        <div className="bg-gray-900 rounded-xl overflow-hidden">
          <video 
            className="w-full h-64 object-cover"
            controls
            poster="/video-poster.jpg"
            onLoadStart={() => setShowVideoPreview(true)}
          >
            <source src={result.video_url} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
        <div className="mt-4 flex justify-center">
          <button
            onClick={() => setShowVideoPreview(!showVideoPreview)}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            {showVideoPreview ? 'ซ่อนตัวอย่าง' : 'ดูตัวอย่าง'}
          </button>
        </div>
      </div>

      {/* Download Options */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">ดาวน์โหลดไฟล์</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {downloadOptions.map((option) => (
            <motion.div
              key={option.type}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`bg-gradient-to-br ${option.color} rounded-xl p-6 text-white cursor-pointer transition-all duration-200 hover:shadow-lg`}
              onClick={() => handleDownload(option.type)}
            >
              <div className="text-center">
                <div className="text-3xl mb-3">{option.icon}</div>
                <h4 className="font-semibold mb-2">{option.title}</h4>
                <p className="text-sm opacity-90 mb-3">{option.description}</p>
                <div className="bg-white bg-opacity-20 rounded-lg p-2 mb-3">
                  <div className="text-xs opacity-90">รูปแบบ: {option.format}</div>
                  <div className="text-xs opacity-90">ขนาด: {option.size}</div>
                </div>
                <button
                  disabled={downloading[option.type]}
                  className={`w-full py-2 px-4 rounded-lg font-medium transition-colors duration-200 ${
                    downloading[option.type]
                      ? 'bg-white bg-opacity-30 cursor-not-allowed'
                      : 'bg-white bg-opacity-20 hover:bg-opacity-30'
                  }`}
                >
                  {downloading[option.type] ? (
                    <div className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      กำลังดาวน์โหลด...
                    </div>
                  ) : (
                    'ดาวน์โหลด'
                  )}
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <button
          onClick={handleShare}
          className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium transition-colors duration-200 flex items-center justify-center"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
          </svg>
          แชร์ลิงก์
        </button>
        
        <button
          onClick={onReset}
          className="px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-xl font-medium transition-colors duration-200 flex items-center justify-center"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          แปลวิดีโอใหม่
        </button>
      </div>

      {/* Share Modal */}
      <AnimatePresence>
        {showShareModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={() => setShowShareModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-lg font-semibold text-gray-800 mb-4">แชร์ลิงก์</h3>
              <div className="bg-gray-100 rounded-lg p-3 mb-4">
                <input
                  type="text"
                  value={shareLink}
                  readOnly
                  className="w-full bg-transparent text-sm text-gray-600"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => copyToClipboard(shareLink)}
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors duration-200"
                >
                  คัดลอกลิงก์
                </button>
                <button
                  onClick={() => setShowShareModal(false)}
                  className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors duration-200"
                >
                  ปิด
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default DownloadResult;
