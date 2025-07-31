// frontend/src/components/HistoryPage.jsx
import React from 'react';
import { motion } from 'framer-motion';
import { useAppStore } from '../store/appStore';

const HistoryPage = () => {
  const { processingHistory } = useAppStore();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">ประวัติการแปลวิดีโอ</h1>
        <p className="text-gray-600">รายการวิดีโอที่เคยแปลทั้งหมด</p>
      </div>

      {processingHistory.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl shadow-md">
          <h3 className="text-xl text-gray-600 font-medium">ไม่พบประวัติการแปลวิดีโอ</h3>
          <p className="text-gray-500 mt-2">ลองแปลวิดีโอแรกของคุณเพื่อเริ่มต้น</p>
        </div>
      ) : (
        <div className="grid gap-6">
          {processingHistory.map((task) => (
            <motion.div
              key={task.task_id}
              className="bg-white rounded-xl shadow-md overflow-hidden"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <div className="flex flex-col md:flex-row">
                {/* Thumbnail */}
                {task.thumbnail && (
                  <div className="md:w-1/3 bg-gray-200">
                    <img
                      src={task.thumbnail}
                      alt={task.title || 'Video thumbnail'}
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}

                {/* Info */}
                <div className="p-6 md:w-2/3">
                  <div className="flex justify-between items-start mb-2">
                    <h2 className="text-xl font-semibold text-gray-800 line-clamp-2">
                      {task.title || 'Untitled Video'}
                    </h2>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      task.status === 'completed' 
                        ? 'bg-green-100 text-green-800'
                        : task.status === 'failed'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {task.status === 'completed' 
                        ? 'เสร็จสิ้น' 
                        : task.status === 'failed'
                        ? 'ล้มเหลว'
                        : 'กำลังประมวลผล'}
                    </span>
                  </div>
                  
                  <p className="text-gray-500 mb-4">
                    {new Date(task.created_at).toLocaleString('th-TH')}
                  </p>
                  
                  <div className="space-y-2">
                    <div className="flex items-center text-sm text-gray-600">
                      <span className="font-medium mr-2">ต้นฉบับ:</span>
                      <span>{task.source_language || 'Auto-detect'}</span>
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <span className="font-medium mr-2">แปลเป็น:</span>
                      <span>{task.target_language || 'Thai'}</span>
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <span className="font-medium mr-2">ระยะเวลา:</span>
                      <span>{task.duration ? `${Math.floor(task.duration / 60)}:${String(task.duration % 60).padStart(2, '0')}` : 'ไม่ทราบ'}</span>
                    </div>
                  </div>
                  
                  {task.status === 'completed' && task.download_url && (
                    <div className="mt-4 flex space-x-3">
                      <a
                        href={task.download_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors duration-200"
                      >
                        <span>ดาวน์โหลด</span>
                      </a>
                      <a
                        href={task.youtube_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 text-sm font-medium rounded-md transition-colors duration-200"
                      >
                        <span>ดูต้นฉบับ</span>
                      </a>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default HistoryPage;
