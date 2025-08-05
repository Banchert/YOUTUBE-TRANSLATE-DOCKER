import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import StatsCard from './StatsCard';

const Dashboard = ({ onNavigate }) => {
  const [stats, setStats] = useState({
    totalVideos: 0,
    totalMinutes: 0,
    activeLanguages: 0,
    successRate: 0
  });
  
  const [recentActivity, setRecentActivity] = useState([]);
  const [systemHealth, setSystemHealth] = useState({
    api: 'healthy',
    whisper: 'healthy',
    translation: 'healthy',
    tts: 'healthy'
  });

  useEffect(() => {
    // Fetch dashboard data
    fetchDashboardData();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Mock data for now - replace with actual API calls
      setStats({
        totalVideos: 1247,
        totalMinutes: 18503,
        activeLanguages: 12,
        successRate: 98.5
      });

      setRecentActivity([
        {
          id: 1,
          type: 'completed',
          title: 'แปลวิดีโอ "สอน React.js"',
          time: '5 นาทีที่แล้ว',
          languages: 'EN → TH',
          duration: '15:30'
        },
        {
          id: 2,
          type: 'processing',
          title: 'แปลวิดีโอ "AI Tutorial"',
          time: '10 นาทีที่แล้ว',
          languages: 'EN → TH',
          duration: '25:45'
        },
        {
          id: 3,
          type: 'completed',
          title: 'แปลวิดีโอ "Python Basics"',
          time: '1 ชั่วโมงที่แล้ว',
          languages: 'EN → TH',
          duration: '30:20'
        }
      ]);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'completed': return '✅';
      case 'processing': return '⚙️';
      case 'failed': return '❌';
      default: return '📄';
    }
  };

  const getServiceStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const handleQuickAction = (action) => {
    if (onNavigate) {
      onNavigate(action);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="max-w-7xl mx-auto space-y-8"
    >
      {/* Welcome Section */}
      <motion.div
        className="text-center mb-12"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
          ยินดีต้อนรับสู่ YouTube Video Translator
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          แปลวิดีโอ YouTube เป็นภาษาต่างๆ ด้วยเทคโนโลยี AI ที่ทันสมัย
          สะดวก รวดเร็ว และแม่นยำ
        </p>
      </motion.div>

      {/* Statistics Cards */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <StatsCard
          title="วิดีโอที่แปลแล้ว"
          value={stats.totalVideos.toLocaleString()}
          icon="🎬"
          color="from-blue-500 to-cyan-500"
          change="+12.5%"
        />
        <StatsCard
          title="นาทีทั้งหมด"
          value={stats.totalMinutes.toLocaleString()}
          icon="⏱️"
          color="from-purple-500 to-pink-500"
          change="+8.2%"
        />
        <StatsCard
          title="ภาษาที่รองรับ"
          value={stats.activeLanguages}
          icon="🌍"
          color="from-green-500 to-emerald-500"
          change="+3"
        />
        <StatsCard
          title="อัตราความสำเร็จ"
          value={`${stats.successRate}%`}
          icon="🎯"
          color="from-orange-500 to-red-500"
          change="+1.2%"
        />
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Quick Actions */}
        <motion.div
          className="lg:col-span-2"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-xl border border-white/20 p-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
              <span className="mr-3">🚀</span>
              เริ่มใช้งาน
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <motion.button
                onClick={() => handleQuickAction('translate')}
                className="group relative overflow-hidden bg-gradient-to-r from-blue-500 to-purple-500 text-white p-6 rounded-2xl text-left transition-all duration-300 hover:shadow-xl"
                whileHover={{ scale: 1.02, y: -5 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="relative z-10">
                  <div className="text-3xl mb-3">🎬</div>
                  <h3 className="text-xl font-bold mb-2">แปลวิดีโอใหม่</h3>
                  <p className="text-blue-100">เริ่มแปลวิดีโอ YouTube</p>
                </div>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </motion.button>

              <motion.button
                onClick={() => handleQuickAction('history')}
                className="group relative overflow-hidden bg-gradient-to-r from-green-500 to-emerald-500 text-white p-6 rounded-2xl text-left transition-all duration-300 hover:shadow-xl"
                whileHover={{ scale: 1.02, y: -5 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="relative z-10">
                  <div className="text-3xl mb-3">📚</div>
                  <h3 className="text-xl font-bold mb-2">ดูประวัติ</h3>
                  <p className="text-green-100">วิดีโอที่แปลไว้แล้ว</p>
                </div>
                <div className="absolute inset-0 bg-gradient-to-r from-green-600 to-emerald-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </motion.button>

              <motion.button
                onClick={() => handleQuickAction('settings')}
                className="group relative overflow-hidden bg-gradient-to-r from-orange-500 to-red-500 text-white p-6 rounded-2xl text-left transition-all duration-300 hover:shadow-xl"
                whileHover={{ scale: 1.02, y: -5 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="relative z-10">
                  <div className="text-3xl mb-3">⚙️</div>
                  <h3 className="text-xl font-bold mb-2">ตั้งค่าระบบ</h3>
                  <p className="text-orange-100">กำหนดค่าและปรับแต่ง</p>
                </div>
                <div className="absolute inset-0 bg-gradient-to-r from-orange-600 to-red-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </motion.button>

              <motion.button
                onClick={() => handleQuickAction('dashboard')}
                className="group relative overflow-hidden bg-gradient-to-r from-pink-500 to-rose-500 text-white p-6 rounded-2xl text-left transition-all duration-300 hover:shadow-xl"
                whileHover={{ scale: 1.02, y: -5 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="relative z-10">
                  <div className="text-3xl mb-3">📊</div>
                  <h3 className="text-xl font-bold mb-2">รายงานสถิติ</h3>
                  <p className="text-pink-100">ดูข้อมูลการใช้งาน</p>
                </div>
                <div className="absolute inset-0 bg-gradient-to-r from-pink-600 to-rose-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* System Status & Recent Activity */}
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          {/* System Status */}
          <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-xl border border-white/20 p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">🟢</span>
              สถานะระบบ
            </h3>
            
            <div className="space-y-3">
              {Object.entries(systemHealth).map(([service, status]) => (
                <div key={service} className="flex items-center justify-between">
                  <span className="text-gray-700 capitalize">
                    {service === 'api' ? 'API Server' : 
                     service === 'whisper' ? 'Whisper AI' :
                     service === 'translation' ? 'Translation Service' :
                     'Text-to-Speech'}
                  </span>
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${getServiceStatusColor(status)}`}></div>
                    <span className="text-sm text-gray-600 capitalize">{status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-xl border border-white/20 p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
              <span className="mr-2">⚡</span>
              กิจกรรมล่าสุด
            </h3>
            
            <div className="space-y-3">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-center space-x-3 p-3 bg-gray-50/50 rounded-xl">
                  <div className="text-xl">{getActivityIcon(activity.type)}</div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">
                      {activity.title}
                    </p>
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <span>{activity.languages}</span>
                      <span>•</span>
                      <span>{activity.duration}</span>
                      <span>•</span>
                      <span>{activity.time}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Popular Languages */}
      <motion.div
        className="bg-white/80 backdrop-blur-md rounded-3xl shadow-xl border border-white/20 p-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
      >
        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
          <span className="mr-3">🌍</span>
          ภาษายอดนิยม
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[
            { code: 'th', name: 'ไทย', flag: '🇹🇭', usage: 85 },
            { code: 'en', name: 'English', flag: '🇺🇸', usage: 72 },
            { code: 'zh', name: '中文', flag: '🇨🇳', usage: 65 },
            { code: 'ja', name: '日本語', flag: '🇯🇵', usage: 58 },
            { code: 'ko', name: '한국어', flag: '🇰🇷', usage: 45 },
            { code: 'vi', name: 'Tiếng Việt', flag: '🇻🇳', usage: 38 }
          ].map((lang) => (
            <motion.div
              key={lang.code}
              className="text-center p-4 bg-gray-50/50 rounded-2xl hover:bg-gray-100/50 transition-colors"
              whileHover={{ scale: 1.05 }}
            >
              <div className="text-3xl mb-2">{lang.flag}</div>
              <div className="font-medium text-gray-800 text-sm mb-1">{lang.name}</div>
              <div className="text-xs text-gray-500">{lang.usage}% การใช้งาน</div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default Dashboard; 