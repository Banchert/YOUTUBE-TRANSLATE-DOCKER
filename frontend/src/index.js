// =============================================================================
// 🔥 MAIN ENTRY POINT
// frontend/src/index.js
// =============================================================================
import React from 'react'; // นำเข้าไลบรารี React สำหรับการสร้าง UI
import ReactDOM from 'react-dom/client'; // นำเข้า ReactDOM สำหรับการทำงานกับ DOM
import './index.css'; // นำเข้าไฟล์ CSS หลักสำหรับการจัดสไตล์ทั่วทั้งแอป
import App from './App'; // นำเข้าคอมโพเนนต์หลักของแอปพลิเคชัน
import { ErrorBoundary } from './components'; // นำเข้า ErrorBoundary จากไฟล์ index.js ในโฟลเดอร์ components

// สร้าง root สำหรับแอปพลิเคชัน React โดยเชื่อมโยงกับ element ที่มี id เป็น 'root' ในไฟล์ index.html
const root = ReactDOM.createRoot(document.getElementById('root'));

// เรนเดอร์คอมโพเนนต์หลักของแอปพลิเคชัน
root.render(
  // React.StrictMode เป็นเครื่องมือสำหรับช่วยในการพัฒนา React
  // มันจะตรวจสอบปัญหาที่อาจเกิดขึ้นในแอปพลิเคชัน (เช่น deprecated lifecycles)
  <React.StrictMode>
    {/* ErrorBoundary ใช้สำหรับดักจับข้อผิดพลาด (errors) ที่เกิดขึ้นในคอมโพเนนต์ลูก
        ป้องกันไม่ให้ทั้งแอปพลิเคชันล่ม และแสดง UI สำรองแทน */}
    <ErrorBoundary>
      {/* คอมโพเนนต์ App คือหัวใจหลักของแอปพลิเคชันของคุณ
          ซึ่งภายใน App จะมีการจัดการ Routing และแสดงผลส่วนต่างๆ ของ UI */}
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);

// หากคุณต้องการเริ่มวัดประสิทธิภาพของแอป (เช่น เวลาในการโหลด)
// สามารถเปิดใช้งานฟังก์ชัน reportWebVitals ได้
// reportWebVitals(); // ปัจจุบันถูกคอมเมนต์ไว้