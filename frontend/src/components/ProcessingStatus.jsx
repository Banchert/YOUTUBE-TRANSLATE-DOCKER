import React, { useState, useEffect } from 'react'; 

export default function ProcessingStatus({ taskId, onComplete, onReset }) { 
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  const steps = [
    { name: 'ดาวน์โหลดวิดีโอ', icon: '📥', description: 'กำลังดาวน์โหลดวิดีโอจาก YouTube' },
    { name: 'แปลงเสียงเป็นข้อความ', icon: '🎤', description: 'ใช้ Whisper AI แปลงเสียงพูดเป็นข้อความ' },
    { name: 'แปลข้อความ', icon: '🌐', description: 'แปลข้อความเป็นภาษาไทยด้วย LibreTranslate' },
    { name: 'สร้างเสียงพูด', icon: '🔊', description: 'สร้างเสียงพูดภาษาไทยด้วย TTS AI' },
    { name: 'รวมไฟล์วิดีโอ', icon: '🎬', description: 'รวมวิดีโอต้นฉบับกับเสียงพูดภาษาไทย' },
    { name: 'เสร็จสิ้น', icon: '✅', description: 'การแปลเสร็จสิ้น พร้อมใช้งาน' }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          onComplete({ video_url: 'demo-video.mp4', task_id: taskId });
          return 100;
        }
        return prev + 2;
      });
    }, 200);

    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev >= steps.length - 1) {
          clearInterval(stepInterval);
          return steps.length - 1;
        }
        return prev + 1;
      });
    }, 3000);

    return () => {
      clearInterval(interval);
      clearInterval(stepInterval);
    };
  }, [onComplete, taskId, steps.length]);

  return ( 
    <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-white animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">กำลังประมวลผลวิดีโอ</h2>
        <p className="text-gray-600">กรุณารอสักครู่ ระบบกำลังแปลวิดีโอให้คุณ</p>
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">ความคืบหน้า</span>
          <span className="text-sm font-medium text-blue-600">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-4 mb-8">
        {steps.map((step, index) => (
          <div 
            key={index}
            className={`flex items-center p-4 rounded-xl transition-all duration-300 ${
              index <= currentStep 
                ? 'bg-blue-50 border border-blue-200' 
                : 'bg-gray-50 border border-gray-200'
            }`}
          >
            <div className={`w-10 h-10 rounded-full flex items-center justify-center mr-4 ${
              index < currentStep 
                ? 'bg-green-500' 
                : index === currentStep 
                  ? 'bg-blue-500 animate-pulse' 
                  : 'bg-gray-300'
            }`}>
              {index < currentStep ? (
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <span className="text-white font-bold">{step.icon}</span>
              )}
            </div>
            <div className="flex-1">
              <h3 className={`font-semibold ${
                index <= currentStep ? 'text-gray-800' : 'text-gray-500'
              }`}>
                {step.name}
              </h3>
              <p className={`text-sm ${
                index <= currentStep ? 'text-gray-600' : 'text-gray-400'
              }`}>
                {step.description}
              </p>
            </div>
            {index === currentStep && (
              <div className="ml-4">
                <div className="w-4 h-4 bg-blue-500 rounded-full animate-ping"></div>
              </div>
            )}
          </div>
        ))}
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
            <p className="font-medium text-gray-800">{Math.floor(progress / 10)} วินาที</p>
          </div>
        </div>
      </div>

      {/* Cancel Button */}
      <div className="text-center">
        <button 
          onClick={onReset}
          className="px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-xl font-medium transition-colors duration-200"
        >
          ยกเลิกการประมวลผล
        </button>
      </div>
    </div>
  ); 
} 
