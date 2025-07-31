// frontend/src/services/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`Making ${config.method.toUpperCase()} request to ${config.url}`);
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        return response.data;
      },
      (error) => {
        const message = error.response?.data?.detail || 
                      error.response?.data?.message || 
                      error.message || 
                      'เกิดข้อผิดพลาดที่ไม่ทราบสาเหตุ';
        
        console.error('API Error:', {
          status: error.response?.status,
          message,
          url: error.config?.url
        });

        throw new Error(message);
      }
    );
  }

  // Health check
  async healthCheck() {
    return this.client.get('/health');
  }

  // Process video
  async processVideo(data) {
    return this.client.post('/process-video/', data);
  }

  // Get task status
  async getTaskStatus(taskId) {
    return this.client.get(`/status/${taskId}`);
  }

  // Download result
  async downloadResult(taskId) {
    return this.client.get(`/download/${taskId}`, {
      responseType: 'blob'
    });
  }

  // Cancel task
  async cancelTask(taskId) {
    return this.client.delete(`/task/${taskId}`);
  }

  // Get supported languages
  async getSupportedLanguages() {
    return this.client.get('/languages');
  }

  // Get processing statistics
  async getStatistics() {
    return this.client.get('/statistics');
  }
}

export const apiService = new ApiService();

// ===== Hooks =====

// frontend/src/hooks/useWebSocket.js
import { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';

export const useWebSocket = (url) => {
  const [socket, setSocket] = useState(null);
  const [lastMessage, setLastMessage] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Connecting');

  useEffect(() => {
    const socketUrl = process.env.REACT_APP_WS_URL || 'http://localhost:8000';
    const newSocket = io(socketUrl + url);

    newSocket.on('connect', () => {
      console.log('WebSocket connected');
      setConnectionStatus('Open');
      setSocket(newSocket);
    });

    newSocket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setConnectionStatus('Closed');
    });

    newSocket.on('message', (data) => {
      setLastMessage({ data: JSON.stringify(data) });
    });

    newSocket.on('error', (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('Error');
    });

    return () => {
      newSocket.close();
    };
  }, [url]);

  return { socket, lastMessage, connectionStatus };
};

// frontend/src/hooks/useLocalStorage.js
import { useState, useEffect } from 'react';

export const useLocalStorage = (key, initialValue) => {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue];
};

// frontend/src/hooks/useAsync.js
import { useState, useEffect, useCallback } from 'react';

export const useAsync = (asyncFunction, immediate = true) => {
  const [status, setStatus] = useState('idle');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    setStatus('pending');
    setData(null);
    setError(null);

    try {
      const response = await asyncFunction(...args);
      setData(response);
      setStatus('success');
      return response;
    } catch (error) {
      setError(error);
      setStatus('error');
      throw error;
    }
  }, [asyncFunction]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { execute, status, data, error };
};

// frontend/src/store/appStore.js
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAppStore = create(
  persist(
    (set, get) => ({
      // Current processing task
      currentTask: null,
      setCurrentTask: (task) => set({ currentTask: task }),
      clearCurrentTask: () => set({ currentTask: null }),

      // Processing history
      processingHistory: [],
      addToHistory: (task) => set((state) => ({
        processingHistory: [task, ...state.processingHistory.slice(0, 49)] // Keep last 50
      })),
      updateHistoryItem: (taskId, updates) => set((state) => ({
        processingHistory: state.processingHistory.map(item =>
          item.task_id === taskId ? { ...item, ...updates } : item
        )
      })),
      removeFromHistory: (taskId) => set((state) => ({
        processingHistory: state.processingHistory.filter(item => item.task_id !== taskId)
      })),
      clearHistory: () => set({ processingHistory: [] }),

      // User preferences
      preferences: {
        defaultLanguage: 'th',
        defaultMixingMode: 'overlay',
        defaultVoiceType: 'female',
        autoDownload: false,
        notifications: true
      },
      updatePreferences: (newPrefs) => set((state) => ({
        preferences: { ...state.preferences, ...newPrefs }
      })),

      // UI state
      sidebarOpen: false,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      
      darkMode: false,
      setDarkMode: (dark) => set({ darkMode: dark }),

      // Statistics
      statistics: {
        totalProcessed: 0,
        totalSuccessful: 0,
        totalFailed: 0,
        averageProcessingTime: 0
      },
      updateStatistics: (stats) => set({ statistics: stats }),

      // Computed getters
      getTaskById: (taskId) => {
        const state = get();
        return state.processingHistory.find(task => task.task_id === taskId);
      },

      getCompletedTasks: () => {
        const state = get();
        return state.processingHistory.filter(task => task.status === 'completed');
      },

      getFailedTasks: () => {
        const state = get();
        return state.processingHistory.filter(task => task.status === 'failed');
      },

      getProcessingTasks: () => {
        const state = get();
        return state.processingHistory.filter(task => 
          task.status === 'processing' || task.status === 'queued'
        );
      }
    }),
    {
      name: 'youtube-translator-storage',
      partialize: (state) => ({
        processingHistory: state.processingHistory,
        preferences: state.preferences,
        statistics: state.statistics
      })
    }
  )
);

// frontend/src/components/Header.jsx
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  HomeIcon, 
  ClockIcon, 
  Cog6ToothIcon,
  BellIcon 
} from '@heroicons/react/24/outline';

import { useAppStore } from '../store/appStore';

const Header = () => {
  const location = useLocation();
  const { processingHistory, getProcessingTasks } = useAppStore();
  const activeTasks = getProcessingTasks();

  const navigation = [
    { name: 'หน้าหลัก', href: '/', icon: HomeIcon },
    { name: 'ประวัติ', href: '/history', icon: ClockIcon },
    { name: 'การตั้งค่า', href: '/settings', icon: Cog6ToothIcon },
  ];

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">YT</span>
            </div>
            <span className="text-xl font-bold text-gray-800">
              Video Translator
            </span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.name}</span>
                  {item.href === '/history' && processingHistory.length > 0 && (
                    <span className="bg-blue-100 text-blue-600 text-xs font-medium px-2 py-1 rounded-full">
                      {processingHistory.length}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Status & Notifications */}
          <div className="flex items-center space-x-4">
            {/* Active Tasks Indicator */}
            {activeTasks.length > 0 && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="flex items-center space-x-2 bg-blue-50 text-blue-600 px-3 py-1 rounded-full"
              >
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                <span className="text-sm font-medium">
                  {activeTasks.length} งานกำลังประมวลผล
                </span>
              </motion.div>
            )}

            {/* Notifications */}
            <button className="relative p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg transition-colors">
              <BellIcon className="w-5 h-5" />
              {activeTasks.length > 0 && (
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full" />
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

// frontend/src/components/HistoryPage.jsx
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  TrashIcon, 
  ArrowDownTrayIcon,
  EyeIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

import { useAppStore } from '../store/appStore';

const HistoryPage = () => {
  const { 
    processingHistory, 
    removeFromHistory, 
    clearHistory,
    getCompletedTasks,
    getFailedTasks 
  } = useAppStore();
  
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('newest');

  const filteredHistory = processingHistory.filter(task => {
    if (filter === 'completed') return task.status === 'completed';
    if (filter === 'failed') return task.status === 'failed';
    if (filter === 'processing') return ['processing', 'queued'].includes(task.status);
    return true;
  });

  const sortedHistory = [...filteredHistory].sort((a, b) => {
    if (sortBy === 'newest') return new Date(b.created_at) - new Date(a.created_at);
    if (sortBy === 'oldest') return new Date(a.created_at) - new Date(b.created_at);
    return 0;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-50';
      case 'failed': return 'text-red-600 bg-red-50';
      case 'processing': return 'text-blue-600 bg-blue-50';
      case 'queued': return 'text-yellow-600 bg-yellow-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return 'เสร็จแล้ว';
      case 'failed': return 'ล้มเหลว';
      case 'processing': return 'กำลังประมวลผล';
      case 'queued': return 'รอคิว';
      default: return status;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-6xl mx-auto"
    >
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">ประวัติการประมวลผล</h1>
        <p className="text-gray-600">
          ดูและจัดการประวัติการแปลวิดีโอของคุณ
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <div className="text-2xl font-bold text-blue-600">{processingHistory.length}</div>
          <div className="text-sm text-gray-600">ทั้งหมด</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <div className="text-2xl font-bold text-green-600">{getCompletedTasks().length}</div>
          <div className="text-sm text-gray-600">สำเร็จ</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <div className="text-2xl font-bold text-red-600">{getFailedTasks().length}</div>
          <div className="text-sm text-gray-600">ล้มเหลว</div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <div className="text-2xl font-bold text-purple-600">
            {processingHistory.length > 0 
              ? Math.round((getCompletedTasks().length / processingHistory.length) * 100)
              : 0}%
          </div>
          <div className="text-sm text-gray-600">อัตราสำเร็จ</div>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <select 
              value={filter} 
              onChange={(e) => setFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2"
            >
              <option value="all">ทั้งหมด</option>
              <option value="completed">เสร็จแล้ว</option>
              <option value="processing">กำลังประมวลผล</option>
              <option value="failed">ล้มเหลว</option>
            </select>

            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2"
            >
              <option value="newest">ใหม่สุด</option>
              <option value="oldest">เก่าสุด</option>
            </select>
          </div>

          <button
            onClick={clearHistory}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            ลบทั้งหมด
          </button>
        </div>
      </div>

      {/* History List */}
      <div className="space-y-4">
        {sortedHistory.length === 0 ? (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <ClockIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-800 mb-2">ยังไม่มีประวัติ</h3>
            <p className="text-gray-600">เริ่มแปลวิดีโอแรกของคุณได้เลย!</p>
          </div>
        ) : (
          sortedHistory.map((task, index) => (
            <motion.div
              key={task.task_id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="font-semibold text-gray-800 truncate">
                      {task.youtube_url}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                      {getStatusText(task.status)}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>📅 {new Date(task.created_at).toLocaleDateString('th-TH')}</span>
                    <span>🌐 {task.target_language?.toUpperCase()}</span>
                    <span>🎵 {task.audio_mixing}</span>
                    {task.progress && <span>📊 {task.progress}%</span>}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  {task.status === 'completed' && (
                    <>
                      <button
                        onClick={() => window.open(task.download_url, '_blank')}
                        className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                        title="ดาวน์โหลด"
                      >
                        <ArrowDownTrayIcon className="w-5 h-5" />
                      </button>
                      <button
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="ดูรายละเอียด"
                      >
                        <EyeIcon className="w-5 h-5" />
                      </button>
                    </>
                  )}
                  
                  <button
                    onClick={() => removeFromHistory(task.task_id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    title="ลบ"
                  >
                    <TrashIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {task.status === 'processing' && (
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: `${task.progress || 0}%` }}
                    />
                  </div>
                </div>
              )}
            </motion.div>
          ))
        )}
      </div>
    </motion.div>
  );
};

export default HistoryPage;