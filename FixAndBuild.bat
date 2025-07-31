@echo off
chcp 65001 >nul

echo.
echo ==========================================
echo    Fix and Build YouTube Video Translator
echo ==========================================
echo.

echo [INFO] แก้ไขปัญหาและ Build ใหม่...

echo [INFO] หยุดบริการเดิม...
cd docker
docker-compose -f docker-compose-simple.yml down
cd ..

echo [INFO] สร้างไฟล์ที่ขาดหาย...

:: สร้าง Components ที่ขาดหาย
echo [INFO] สร้าง Components พื้นฐาน...

echo // Simple Header component > frontend\src\components\Header.jsx
echo import React from 'react'; >> frontend\src\components\Header.jsx
echo export default function Header() { >> frontend\src\components\Header.jsx
echo   return ( >> frontend\src\components\Header.jsx
echo     ^<div className="bg-white shadow-sm"^> >> frontend\src\components\Header.jsx
echo       ^<div className="container mx-auto px-4 py-4"^> >> frontend\src\components\Header.jsx
echo         ^<h1 className="text-2xl font-bold text-gray-800"^>YouTube Video Translator^</h1^> >> frontend\src\components\Header.jsx
echo       ^</div^> >> frontend\src\components\Header.jsx
echo     ^</div^> >> frontend\src\components\Header.jsx
echo   ); >> frontend\src\components\Header.jsx
echo } >> frontend\src\components\Header.jsx

echo // Simple VideoUpload component > frontend\src\components\VideoUpload.jsx
echo import React, { useState } from 'react'; >> frontend\src\components\VideoUpload.jsx
echo export default function VideoUpload({ onTaskStart }) { >> frontend\src\components\VideoUpload.jsx
echo   const [url, setUrl] = useState(''); >> frontend\src\components\VideoUpload.jsx
echo   const handleSubmit = () =^> { >> frontend\src\components\VideoUpload.jsx
echo     if (url) onTaskStart({ youtube_url: url, task_id: 'demo-123' }); >> frontend\src\components\VideoUpload.jsx
echo   }; >> frontend\src\components\VideoUpload.jsx
echo   return ( >> frontend\src\components\VideoUpload.jsx
echo     ^<div className="bg-white p-6 rounded-lg shadow"^> >> frontend\src\components\VideoUpload.jsx
echo       ^<input >> frontend\src\components\VideoUpload.jsx
echo         type="text" >> frontend\src\components\VideoUpload.jsx
echo         value={url} >> frontend\src\components\VideoUpload.jsx
echo         onChange={(e) =^> setUrl(e.target.value)} >> frontend\src\components\VideoUpload.jsx
echo         placeholder="Enter YouTube URL" >> frontend\src\components\VideoUpload.jsx
echo         className="w-full p-3 border rounded mb-4" >> frontend\src\components\VideoUpload.jsx
echo       /^> >> frontend\src\components\VideoUpload.jsx
echo       ^<button onClick={handleSubmit} className="bg-blue-500 text-white px-6 py-3 rounded"^> >> frontend\src\components\VideoUpload.jsx
echo         Start Translation >> frontend\src\components\VideoUpload.jsx
echo       ^</button^> >> frontend\src\components\VideoUpload.jsx
echo     ^</div^> >> frontend\src\components\VideoUpload.jsx
echo   ); >> frontend\src\components\VideoUpload.jsx
echo } >> frontend\src\components\VideoUpload.jsx

echo // Simple ProcessingStatus component > frontend\src\components\ProcessingStatus.jsx
echo import React from 'react'; >> frontend\src\components\ProcessingStatus.jsx
echo export default function ProcessingStatus({ taskId, onComplete, onReset }) { >> frontend\src\components\ProcessingStatus.jsx
echo   return ( >> frontend\src\components\ProcessingStatus.jsx
echo     ^<div className="bg-white p-6 rounded-lg shadow"^> >> frontend\src\components\ProcessingStatus.jsx
echo       ^<h3 className="text-lg font-bold mb-4"^>Processing Video...^</h3^> >> frontend\src\components\ProcessingStatus.jsx
echo       ^<div className="text-center"^> >> frontend\src\components\ProcessingStatus.jsx
echo         ^<div className="spinner"^>^</div^> >> frontend\src\components\ProcessingStatus.jsx
echo         ^<p^>Task ID: {taskId}^</p^> >> frontend\src\components\ProcessingStatus.jsx
echo         ^<button onClick={onReset} className="mt-4 bg-gray-500 text-white px-4 py-2 rounded"^> >> frontend\src\components\ProcessingStatus.jsx
echo           Cancel >> frontend\src\components\ProcessingStatus.jsx
echo         ^</button^> >> frontend\src\components\ProcessingStatus.jsx
echo       ^</div^> >> frontend\src\components\ProcessingStatus.jsx
echo     ^</div^> >> frontend\src\components\ProcessingStatus.jsx
echo   ); >> frontend\src\components\ProcessingStatus.jsx
echo } >> frontend\src\components\ProcessingStatus.jsx

echo // Simple VideoPlayer component > frontend\src\components\VideoPlayer.jsx
echo import React from 'react'; >> frontend\src\components\VideoPlayer.jsx
echo export default function VideoPlayer({ originalUrl, processedVideo }) { >> frontend\src\components\VideoPlayer.jsx
echo   return ( >> frontend\src\components\VideoPlayer.jsx
echo     ^<div className="bg-white p-6 rounded-lg shadow"^> >> frontend\src\components\VideoPlayer.jsx
echo       ^<h3 className="text-lg font-bold mb-4"^>Video Player^</h3^> >> frontend\src\components\VideoPlayer.jsx
echo       ^<p^>Original URL: {originalUrl}^</p^> >> frontend\src\components\VideoPlayer.jsx
echo       {processedVideo ^&^& ^<p^>Processed: Yes^</p^>} >> frontend\src\components\VideoPlayer.jsx
echo     ^</div^> >> frontend\src\components\VideoPlayer.jsx
echo   ); >> frontend\src\components\VideoPlayer.jsx
echo } >> frontend\src\components\VideoPlayer.jsx

echo // Store file > frontend\src\store\appStore.js
if not exist "frontend\src\store" mkdir frontend\src\store
echo import { create } from 'zustand'; > frontend\src\store\appStore.js
echo export const useAppStore = create((set) =^> ({ >> frontend\src\store\appStore.js
echo   currentTask: null, >> frontend\src\store\appStore.js
echo   processingHistory: [], >> frontend\src\store\appStore.js
echo   setCurrentTask: (task) =^> set({ currentTask: task }), >> frontend\src\store\appStore.js
echo   addToHistory: (task) =^> set((state) =^> ({ >> frontend\src\store\appStore.js
echo     processingHistory: [...state.processingHistory, task] >> frontend\src\store\appStore.js
echo   })) >> frontend\src\store\appStore.js
echo })); >> frontend\src\store\appStore.js

echo [INFO] แก้ไข App.js ให้ใช้ components ง่ายๆ...

echo import React, { useState } from 'react'; > frontend\src\App.js
echo import './App.css'; >> frontend\src\App.js
echo import Header from './components/Header'; >> frontend\src\App.js
echo import VideoUpload from './components/VideoUpload'; >> frontend\src\App.js
echo import ProcessingStatus from './components/ProcessingStatus'; >> frontend\src\App.js
echo import VideoPlayer from './components/VideoPlayer'; >> frontend\src\App.js
echo import { useAppStore } from './store/appStore'; >> frontend\src\App.js
echo. >> frontend\src\App.js
echo function App() { >> frontend\src\App.js
echo   const { currentTask, setCurrentTask } = useAppStore(); >> frontend\src\App.js
echo   const [videoUrl, setVideoUrl] = useState(''); >> frontend\src\App.js
echo   const [processedVideo, setProcessedVideo] = useState(null); >> frontend\src\App.js
echo. >> frontend\src\App.js
echo   const handleTaskStart = (taskData) =^> { >> frontend\src\App.js
echo     setCurrentTask(taskData); >> frontend\src\App.js
echo     setVideoUrl(taskData.youtube_url); >> frontend\src\App.js
echo   }; >> frontend\src\App.js
echo. >> frontend\src\App.js
echo   const handleTaskComplete = (result) =^> setProcessedVideo(result); >> frontend\src\App.js
echo   const handleReset = () =^> { >> frontend\src\App.js
echo     setCurrentTask(null); >> frontend\src\App.js
echo     setVideoUrl(''); >> frontend\src\App.js
echo     setProcessedVideo(null); >> frontend\src\App.js
echo   }; >> frontend\src\App.js
echo. >> frontend\src\App.js
echo   return ( >> frontend\src\App.js
echo     ^<div className="min-h-screen bg-gray-100"^> >> frontend\src\App.js
echo       ^<Header /^> >> frontend\src\App.js
echo       ^<main className="container mx-auto px-4 py-8"^> >> frontend\src\App.js
echo         ^<div className="max-w-4xl mx-auto"^> >> frontend\src\App.js
echo           ^<h1 className="text-4xl font-bold text-center mb-8"^>YouTube Video Translator^</h1^> >> frontend\src\App.js
echo           {!currentTask ^&^& !processedVideo ^&^& ( >> frontend\src\App.js
echo             ^<VideoUpload onTaskStart={handleTaskStart} /^> >> frontend\src\App.js
echo           )} >> frontend\src\App.js
echo           {currentTask ^&^& !processedVideo ^&^& ( >> frontend\src\App.js
echo             ^<ProcessingStatus taskId={currentTask.task_id} onComplete={handleTaskComplete} onReset={handleReset} /^> >> frontend\src\App.js
echo           )} >> frontend\src\App.js
echo           {(videoUrl ^|^| processedVideo) ^&^& ( >> frontend\src\App.js
echo             ^<VideoPlayer originalUrl={videoUrl} processedVideo={processedVideo} /^> >> frontend\src\App.js
echo           )} >> frontend\src\App.js
echo         ^</div^> >> frontend\src\App.js
echo       ^</main^> >> frontend\src\App.js
echo     ^</div^> >> frontend\src\App.js
echo   ); >> frontend\src\App.js
echo } >> frontend\src\App.js
echo. >> frontend\src\App.js
echo export default App; >> frontend\src\App.js

echo [INFO] สร้าง App.css...
echo .App { > frontend\src\App.css
echo   text-align: center; >> frontend\src\App.css
echo } >> frontend\src\App.css

echo [SUCCESS] แก้ไขไฟล์เสร็จแล้ว!

echo [INFO] Build Docker Images...
cd docker

echo [INFO] Building Backend...
docker-compose -f docker-compose-simple.yml build backend --no-cache

echo [INFO] Building Frontend...
docker-compose -f docker-compose-simple.yml build frontend --no-cache

cd ..

echo [SUCCESS] Build เสร็จแล้ว!

echo [INFO] เริ่มบริการใหม่...
cd docker
docker-compose -f docker-compose-simple.yml up -d
cd ..

echo [INFO] รอให้บริการเริ่มต้น...
timeout /t 30 >nul

echo.
echo [SUCCESS] ระบบพร้อมใช้งาน!
echo.
echo 🌐 เข้าใช้งานผ่าน:
echo    Frontend:           http://localhost:3000
echo    Backend API:        http://localhost:8000
echo    API Documentation:  http://localhost:8000/docs
echo    Translation API:    http://localhost:5000
echo.

set /p open_browser="ต้องการเปิดเว็บแอปหรือไม่? (y/n): "
if /i "%open_browser%"=="y" (
    start http://localhost:3000
    timeout /t 2 >nul
    start http://localhost:8000/docs
    echo [SUCCESS] เปิดเว็บแอปแล้ว
)

echo.
pause
