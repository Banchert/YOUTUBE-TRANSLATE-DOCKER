import React, { useState, useEffect } from 'react'; 
import apiService from '../services/api';

export default function ProcessingStatus({ taskId, onComplete, onReset }) { 
  const [status, setStatus] = useState('processing');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('กำลังเริ่มต้นการประมวลผล...');
  const [steps, setSteps] = useState({});
  const [error, setError] = useState(null);
  const [startTime] = useState(Date.now());
  const [retryCount, setRetryCount] = useState(0);

  const stepConfig = {
    download: { name: 'ดาวน์โหลดวิดีโอ', icon: '📥', description: 'กำลังดาวน์โหลดวิดีโอ' },
    extract_audio: { name: 'แยกเสียง', icon: '🎵', description: 'แยกเสียงจากวิดีโอ' },
    speech_to_text: { name: 'แปลงเสียงเป็นข้อความ', icon: '🎤', description: 'ใช้ Whisper AI แปลงเสียงพูดเป็นข้อความ' },
    translate: { name: 'แปลข้อความ', icon: '🌐', description: 'แปลข้อความเป็นภาษาไทย' },
    text_to_speech: { name: 'สร้างเสียงพูด', icon: '🔊', description: 'สร้างเสียงพูดภาษาไทย' },
    merge_video: { name: 'รวมไฟล์วิดีโอ', icon: '🎬', description: 'รวมวิดีโอกับเสียงพากย์ใหม่' }
  };

  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await apiService.getTaskStatus(taskId);
        // API service returns the data directly, not wrapped in response.data
        const data = response;
        
        setStatus(data.status);
        setProgress(data.progress || 0);
        setMessage(data.message || 'กำลังประมวลผล...');
        setSteps(data.steps || {});
        setRetryCount(0); // Reset retry count on success
        
        if (data.status === 'completed') {
          onComplete({
            task_id: taskId,
            video_url: apiService.getDownloadUrl(taskId, 'video'),
            audio_url: apiService.getDownloadUrl(taskId, 'audio'),
            subtitle_url: apiService.getDownloadUrl(taskId, 'subtitle'),
            file_sizes: data.file_sizes || {}
          });
        } else if (data.status === 'failed') {
          setError(data.error || 'เกิดข้อผิดพลาดในการประมวลผล');
        }
      } catch (err) {
        console.error('Status check failed:', err);
        
        // Handle different error types
        if (err.message.includes('404')) {
          setRetryCount(prev => prev + 1);
          if (retryCount < 5) {
            console.log(`Task not found yet (attempt ${retryCount + 1}/5), continuing to poll...`);
            setMessage(`กำลังรอข้อมูลงาน (${retryCount + 1}/5)...`);
          } else {
            setError('ไม่พบข้อมูลงาน กรุณาลองใหม่อีกครั้ง');
          }
        } else if (err.message.includes('Network') || err.message.includes('fetch')) {
          setError('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้');
        } else {
          setError('ไม่สามารถตรวจสอบสถานะได้');
        }
      }
    };

    // Poll every 3 seconds initially, then every 2 seconds
    const interval = setInterval(pollStatus, retryCount < 3 ? 3000 : 2000);
    
    // Initial check
    pollStatus();

    return () => clearInterval(interval);
  }, [taskId, onComplete, retryCount]);

  const getElapsedTime = () => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const getStepStatus = (stepName) => {
    const step = steps[stepName];
    if (!step) return 'pending';
    return step.status;
  };

  const getStepProgress = (stepName) => {
    const step = steps[stepName];
    if (!step) return 0;
    return step.progress || 0;
  };

  if (error) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-8 border border-red-100">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-red-800 mb-2">เกิดข้อผิดพลาด</h2>
          <p className="text-red-600 mb-6">{error}</p>
          <div className="space-y-3">
            <button 
              onClick={onReset}
              className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl font-medium transition-colors duration-200"
            >
              ลองใหม่
            </button>
            <div className="text-sm text-gray-500">
              Task ID: {taskId}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return ( 
    <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
          {status === 'completed' ? (
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <svg className="w-8 h-8 text-white animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          )}
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          {status === 'completed' ? 'การแปลเสร็จสิ้น!' : 'กำลังประมวลผลวิดีโอ'}
        </h2>
        <p className="text-gray-600">{message}</p>
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">ความคืบหน้า</span>
          <span className="text-sm font-medium text-blue-600">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-4 mb-8">
        {Object.entries(stepConfig).map(([stepKey, stepInfo]) => {
          const stepStatus = getStepStatus(stepKey);
          const stepProgress = getStepProgress(stepKey);
          const isActive = stepStatus === 'processing';
          const isCompleted = stepStatus === 'completed';
          const isPending = stepStatus === 'pending';

          return (
            <div 
              key={stepKey}
              className={`flex items-center p-4 rounded-xl transition-all duration-300 ${
                isCompleted 
                  ? 'bg-green-50 border border-green-200' 
                  : isActive
                    ? 'bg-blue-50 border border-blue-200'
                    : 'bg-gray-50 border border-gray-200'
              }`}
            >
              <div className={`w-10 h-10 rounded-full flex items-center justify-center mr-4 ${
                isCompleted 
                  ? 'bg-green-500' 
                  : isActive
                    ? 'bg-blue-500 animate-pulse'
                    : 'bg-gray-300'
              }`}>
                {isCompleted ? (
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <span className="text-white font-bold">{stepInfo.icon}</span>
                )}
              </div>
              <div className="flex-1">
                <h3 className={`font-semibold ${
                  isCompleted ? 'text-green-800' : isActive ? 'text-blue-800' : 'text-gray-500'
                }`}>
                  {stepInfo.name}
                </h3>
                <p className={`text-sm ${
                  isCompleted ? 'text-green-600' : isActive ? 'text-blue-600' : 'text-gray-400'
                }`}>
                  {stepInfo.description}
                </p>
                {isActive && stepProgress > 0 && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-1">
                      <div 
                        className="bg-blue-500 h-1 rounded-full transition-all duration-300"
                        style={{ width: `${stepProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
              {isActive && (
                <div className="ml-4">
                  <div className="w-4 h-4 bg-blue-500 rounded-full animate-ping"></div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Task Info */}
      <div className="bg-gray-50 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-600">Task ID</p>
            <p className="font-mono text-sm font-medium text-gray-800">{taskId}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">เวลาที่ใช้</p>
            <p className="font-medium text-gray-800">{getElapsedTime()}</p>
          </div>
        </div>
      </div>

      {/* Cancel Button */}
      {status !== 'completed' && (
        <div className="text-center">
          <button 
            onClick={onReset}
            className="px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-xl font-medium transition-colors duration-200"
          >
            ยกเลิกการประมวลผล
          </button>
        </div>
      )}
    </div>
  ); 
} 
