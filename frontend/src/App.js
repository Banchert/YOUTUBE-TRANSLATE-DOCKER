import React, { useState } from 'react'; 
import './App.css'; 
import Header from './components/Header'; 
import VideoUpload from './components/VideoUpload'; 
import ProcessingStatus from './components/ProcessingStatus'; 
import VideoPlayer from './components/VideoPlayer'; 
import { useAppStore } from './store/appStore'; 
 
function App() { 
  const { currentTask, setCurrentTask } = useAppStore(); 
  const [videoUrl, setVideoUrl] = useState(''); 
  const [processedVideo, setProcessedVideo] = useState(null); 
 
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
 
  return ( 
    <div className="min-h-screen bg-gray-100"> 
      <Header /> 
      <main className="container mx-auto px-4 py-8"> 
        <div className="max-w-4xl mx-auto"> 
          <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
            🎬 YouTube Video Translator
          </h1>
          <p className="text-center text-gray-600 mb-8">
            แปลวิดีโอ YouTube เป็นภาษาที่คุณต้องการ พร้อมเสียงและซับไตเติล
          </p>
          
          {!currentTask && !processedVideo && ( 
            <VideoUpload onTaskStart={handleTaskStart} /> 
          )} 
          {currentTask && !processedVideo && ( 
            <ProcessingStatus 
              taskId={currentTask.task_id} 
              sourceLanguage={currentTask.source_language}
              targetLanguage={currentTask.target_language}
              onComplete={handleTaskComplete} 
              onReset={handleReset} 
            /> 
          )} 
          {(videoUrl || processedVideo) && ( 
            <VideoPlayer 
              originalUrl={videoUrl} 
              processedVideo={processedVideo}
              sourceLanguage={currentTask?.source_language}
              targetLanguage={currentTask?.target_language}
            /> 
          )} 
        </div> 
      </main> 
    </div> 
  ); 
} 
 
export default App;
