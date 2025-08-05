import React, { useState } from 'react'; 
import './App.css'; 
import Header from './components/Header'; 
import VideoUpload from './components/VideoUpload'; 
import ProcessingStatus from './components/ProcessingStatus'; 
import VideoPlayer from './components/VideoPlayer'; 
import Dashboard from './components/Dashboard';
import DownloadResult from './components/DownloadResult';
import { useAppStore } from './store/appStore'; 
 
function App() { 
  const { currentTask, setCurrentTask } = useAppStore(); 
  const [videoUrl, setVideoUrl] = useState(''); 
  const [processedVideo, setProcessedVideo] = useState(null); 
  const [currentPage, setCurrentPage] = useState('main'); // main, dashboard, history, settings

  const handleTaskStart = (taskData) => { 
    // เพิ่มข้อมูลภาษาเข้าไปใน task
    const enhancedTaskData = {
      ...taskData,
      source_language: taskData.source_language || 'auto',
      target_language: taskData.target_language || 'th',
      created_at: new Date().toISOString()
    };
    
    setCurrentTask(enhancedTaskData); 
    setVideoUrl(taskData.youtube_url); 
  }; 
 
  const handleTaskComplete = (result) => setProcessedVideo(result); 
  const handleReset = () => { 
    setCurrentTask(null); 
    setVideoUrl(''); 
    setProcessedVideo(null); 
  }; 

  const handleNavigate = (page) => {
    setCurrentPage(page);
  };

  const handleDownload = (type) => {
    console.log(`Downloading ${type} for task:`, processedVideo?.task_id);
    // Download logic will be handled by DownloadResult component
  };

  // Render different pages
  if (currentPage === 'dashboard') {
    return (
      <div className="min-h-screen bg-gray-100"> 
        <Header onNavigate={handleNavigate} currentPage={currentPage} /> 
        <main className="container mx-auto px-4 py-8"> 
          <Dashboard onNavigate={handleNavigate} />
        </main> 
      </div> 
    );
  }

  return ( 
    <div className="min-h-screen bg-gray-100"> 
      <Header onNavigate={handleNavigate} currentPage={currentPage} /> 
      <main className="container mx-auto px-4 py-8"> 
        <div className="max-w-6xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-4">YouTube Video Translator</h1>
            <p className="text-lg text-gray-600">แปลวิดีโอ YouTube เป็นภาษาไทย พร้อมเสียงพูดภาษาไทย</p>
          </div>

          {/* Main Content */}
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left Column - Upload & Processing */}
            <div className="space-y-6">
              {!currentTask && !processedVideo && ( 
                <VideoUpload onTaskStart={handleTaskStart} /> 
              )} 
              {currentTask && !processedVideo && ( 
                <ProcessingStatus taskId={currentTask.task_id} onComplete={handleTaskComplete} onReset={handleReset} /> 
              )} 
            </div>

            {/* Right Column - Video Player & Results */}
            <div className="space-y-6">
              {(videoUrl || processedVideo) && ( 
                <VideoPlayer originalUrl={videoUrl} processedVideo={processedVideo} /> 
              )} 
              {processedVideo && (
                <DownloadResult 
                  result={processedVideo} 
                  onDownload={handleDownload}
                  onReset={handleReset}
                />
              )}
            </div>
          </div>

          {/* Features Section */}
          {!currentTask && !processedVideo && (
            <div className="mt-16">
              <h2 className="text-3xl font-bold text-center mb-8 text-gray-800">
                ฟีเจอร์เด่น
              </h2>
              <div className="grid md:grid-cols-3 gap-8">
                <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Speech Recognition</h3>
                  <p className="text-gray-600">แปลงเสียงพูดในวิดีโอเป็นข้อความด้วย Whisper AI</p>
                </div>
                
                <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Translation</h3>
                  <p className="text-gray-600">แปลข้อความเป็นภาษาไทยด้วย LibreTranslate</p>
                </div>
                
                <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-semibold mb-2">Text-to-Speech</h3>
                  <p className="text-gray-600">สร้างเสียงพูดภาษาไทยด้วย TTS AI</p>
                </div>
              </div>
            </div>
          )}
        </div> 
      </main> 
    </div> 
  ); 
} 
 
export default App;
