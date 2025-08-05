import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import apiService from '../services/api';

const DownloadResult = ({ result, onDownload, onReset }) => {
  const [activeTab, setActiveTab] = useState('video');
  const [showShareModal, setShowShareModal] = useState(false);
  const [downloading, setDownloading] = useState({});
  const [shareLink, setShareLink] = useState('');

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
      let errorMessage = `การดาวน์โหลด ${type} ล้มเหลว`;
      if (error.message.includes('404')) {
        errorMessage += ': ไม่พบไฟล์ (Task อาจยังไม่เสร็จสิ้น)';
      } else if (error.message.includes('403')) {
        errorMessage += ': ไม่มีสิทธิ์เข้าถึงไฟล์';
      } else if (error.message.includes('500')) {
        errorMessage += ': เซิร์ฟเวอร์เกิดข้อผิดพลาด';
      } else if (error.message.includes('File not available')) {
        errorMessage += ': ไฟล์ไม่พร้อมใช้งาน';
      } else {
        errorMessage += `: ${error.message}`;
      }
      
      // Show error toast or alert
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
      setShowShareModal(true);
      
      // Create share link
      const response = await apiService.createShareLink(result.task_id);
      setShareLink(response.share_url || `${window.location.origin}/shared/${result.task_id}`);
      
    } catch (error) {
      console.error('Failed to create share link:', error);
      setShareLink(`${window.location.origin}/shared/${result.task_id}`);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      alert('คัดลอกลิงก์เรียบร้อยแล้ว');
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      alert('ไม่สามารถคัดลอกลิงก์ได้');
    }
  };

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
      'es': '🇪🇸 สเปน',
      'fr': '🇫🇷 ฝรั่งเศส'
    };
    return languageMap[code] || code;
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '15:30'; // Default mock duration
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="max-w-6xl mx-auto"
    >
      {/* Success Header */}
      <motion.div
        className="text-center mb-8"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <motion.div
          className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full mb-4"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", bounce: 0.5, delay: 0.3 }}
        >
          <span className="text-4xl">✅</span>
        </motion.div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-4">
          แปลสำเร็จแล้ว!
        </h1>
        <p className="text-xl text-gray-600">
          วิดีโอของคุณได้รับการแปลเรียบร้อยแล้ว พร้อมดาวน์โหลด
        </p>
      </motion.div>

      {/* Translation Info */}
      <motion.div
        className="bg-white/80 backdrop-blur-md rounded-3xl shadow-xl border border-white/20 p-6 mb-8"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <div className="flex items-center justify-center space-x-8">
          <div className="text-center">
            <div className="text-sm font-medium text-gray-600 mb-1">ภาษาต้นทาง</div>
            <div className="text-lg font-bold">{getLanguageName(result.source_language)}</div>
          </div>
          <motion.div
            className="text-green-500"
            animate={{ x: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </motion.div>
          <div className="text-center">
            <div className="text-sm font-medium text-gray-600 mb-1">ภาษาปลายทาง</div>
            <div className="text-lg font-bold">{getLanguageName(result.target_language)}</div>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Video Preview */}
        <motion.div
          className="lg:col-span-2"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-xl border border-white/20 p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
              <span className="mr-3">🎬</span>
              ตัวอย่างผลลัพธ์
            </h2>

            {/* Tab Navigation */}
            <div className="flex bg-gray-100 rounded-2xl p-1 mb-6">
              {['video', 'original'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex-1 px-4 py-2 rounded-xl font-medium transition-all duration-300 ${
                    activeTab === tab
                      ? 'bg-white text-gray-800 shadow-md'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  {tab === 'video' ? '🎬 วิดีโอที่แปลแล้ว' : '📹 วิดีโอต้นฉบับ'}
                </button>
              ))}
            </div>

            {/* Video Player Area */}
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="aspect-video bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl flex items-center justify-center mb-4"
              >
                <div className="text-center text-white">
                  <div className="text-6xl mb-4">
                    {activeTab === 'video' ? '🎬' : '📹'}
                  </div>
                  <h3 className="text-xl font-bold mb-2">
                    {activeTab === 'video' ? 'วิดีโอที่แปลแล้ว' : 'วิดีโอต้นฉบับ'}
                  </h3>
                  <p className="text-gray-300 mb-4">
                    {activeTab === 'video' 
                      ? `แปลจาก ${getLanguageName(result.source_language)} เป็น ${getLanguageName(result.target_language)}`
                      : 'วิดีโอต้นฉบับก่อนการแปล'
                    }
                  </p>
                  <motion.button
                    className="px-6 py-2 bg-white/20 hover:bg-white/30 rounded-xl backdrop-blur-sm transition-colors"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => activeTab === 'video' && result.video_url && window.open(result.video_url, '_blank')}
                  >
                    ▶️ เล่น
                  </motion.button>
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Video Info */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div className="p-3 bg-gray-50/50 rounded-xl">
                <div className="text-sm text-gray-600">ความยาว</div>
                <div className="font-bold text-gray-800">{formatDuration(result.original_duration)}</div>
              </div>
              <div className="p-3 bg-gray-50/50 rounded-xl">
                <div className="text-sm text-gray-600">คุณภาพ</div>
                <div className="font-bold text-gray-800">1080p</div>
              </div>
              <div className="p-3 bg-gray-50/50 rounded-xl">
                <div className="text-sm text-gray-600">ขนาดไฟล์</div>
                <div className="font-bold text-gray-800">{downloadOptions[0].size}</div>
              </div>
              <div className="p-3 bg-gray-50/50 rounded-xl">
                <div className="text-sm text-gray-600">รูปแบบ</div>
                <div className="font-bold text-gray-800">MP4</div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Download Options */}
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          {/* Download Cards */}
          <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-xl border border-white/20 p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
              <span className="mr-2">📥</span>
              ดาวน์โหลด
            </h3>
            
            <div className="space-y-4">
              {downloadOptions.map((option, index) => (
                <motion.div
                  key={option.type}
                  className="group"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.7 + index * 0.1 }}
                >
                  <motion.button
                    onClick={() => handleDownload(option.type)}
                    disabled={downloading[option.type]}
                    className={`w-full p-4 rounded-2xl text-left transition-all duration-300 bg-gradient-to-r ${option.color} text-white hover:shadow-xl group-hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed`}
                    whileHover={{ scale: downloading[option.type] ? 1 : 1.02 }}
                    whileTap={{ scale: downloading[option.type] ? 1 : 0.98 }}
                  >
                    <div className="flex items-center space-x-4">
                      <div className="text-3xl">{option.icon}</div>
                      <div className="flex-1">
                        <div className="font-bold text-lg">{option.title}</div>
                        <div className="text-sm opacity-90">{option.description}</div>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className="text-xs bg-white/20 px-2 py-1 rounded">{option.format}</span>
                          <span className="text-xs">{option.size}</span>
                        </div>
                      </div>
                      {downloading[option.type] ? (
                        <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      ) : (
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      )}
                    </div>
                  </motion.button>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-xl border border-white/20 p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4">การกระทำเพิ่มเติม</h3>
            
            <div className="space-y-3">
              <motion.button
                onClick={handleShare}
                className="w-full flex items-center space-x-3 p-3 bg-blue-50 hover:bg-blue-100 rounded-xl transition-colors"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <span className="text-2xl">🔗</span>
                <div className="text-left">
                  <div className="font-medium text-blue-800">แชร์ผลลัพธ์</div>
                  <div className="text-sm text-blue-600">สร้างลิงก์สำหรับแชร์</div>
                </div>
              </motion.button>

              <motion.button
                className="w-full flex items-center space-x-3 p-3 bg-purple-50 hover:bg-purple-100 rounded-xl transition-colors"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <span className="text-2xl">📊</span>
                <div className="text-left">
                  <div className="font-medium text-purple-800">ดูรายละเอียด</div>
                  <div className="text-sm text-purple-600">สถิติการแปลและคุณภาพ</div>
                </div>
              </motion.button>
            </div>
          </div>

          {/* Reset Button */}
          <motion.button
            onClick={onReset}
            className="w-full p-4 bg-gray-100 hover:bg-gray-200 rounded-2xl transition-colors font-medium text-gray-700"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            🔄 แปลวิดีโอใหม่
          </motion.button>
        </motion.div>
      </div>

      {/* Share Modal */}
      <AnimatePresence>
        {showShareModal && (
          <motion.div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowShareModal(false)}
          >
            <motion.div
              className="bg-white rounded-3xl p-8 max-w-md w-full"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-xl font-bold text-gray-800 mb-4">แชร์ผลลัพธ์</h3>
              <p className="text-gray-600 mb-6">
                สร้างลิงก์สำหรับแชร์ผลลัพธ์การแปลกับผู้อื่น
              </p>
              
              {shareLink && (
                <div className="mb-4 p-3 bg-gray-50 rounded-xl">
                  <div className="text-sm text-gray-600 mb-1">ลิงก์แชร์:</div>
                  <div className="text-sm font-mono text-gray-800 break-all">{shareLink}</div>
                </div>
              )}
              
              <div className="space-y-4">
                <button 
                  onClick={() => copyToClipboard(shareLink)}
                  className="w-full p-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors"
                >
                  📱 คัดลอกลิงก์
                </button>
                <button className="w-full p-3 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-colors">
                  💬 แชร์ผ่าน LINE
                </button>
                <button className="w-full p-3 bg-gray-500 text-white rounded-xl hover:bg-gray-600 transition-colors">
                  📧 ส่งทางอีเมล
                </button>
              </div>
              
              <button
                onClick={() => setShowShareModal(false)}
                className="w-full mt-4 p-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors"
              >
                ปิด
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default DownloadResult;
