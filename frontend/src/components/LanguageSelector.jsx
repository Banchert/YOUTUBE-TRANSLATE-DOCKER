// frontend/src/components/LanguageSelector.jsx
import React, { useState, useEffect } from 'react';
import Dropdown from './Dropdown';

const LanguageSelector = ({ 
  sourceLanguage, 
  targetLanguage, 
  onSourceLanguageChange, 
  onTargetLanguageChange,
  className = '' 
}) => {
  const [languages, setLanguages] = useState([]);
  const [loading, setLoading] = useState(true);

  // รายการภาษาที่รองรับ
  const languageOptions = [
    { value: 'auto', label: '🔄 ตรวจจับอัตโนมัติ (Auto-detect)', flag: '🔄' },
    { value: 'th', label: '🇹🇭 ไทย (Thai)', flag: '🇹🇭' },
    { value: 'en', label: '🇺🇸 อังกฤษ (English)', flag: '🇺🇸' },
    { value: 'zh', label: '🇨🇳 จีน (Chinese)', flag: '🇨🇳' },
    { value: 'ja', label: '🇯🇵 ญี่ปุ่น (Japanese)', flag: '🇯🇵' },
    { value: 'ko', label: '🇰🇷 เกาหลี (Korean)', flag: '🇰🇷' },
    { value: 'vi', label: '🇻🇳 เวียดนาม (Vietnamese)', flag: '🇻🇳' },
    { value: 'id', label: '🇮🇩 อินโดนีเซีย (Indonesian)', flag: '🇮🇩' },
    { value: 'ms', label: '🇲🇾 มาเลเซีย (Malay)', flag: '🇲🇾' },
    { value: 'lo', label: '🇱🇦 ลาว (Lao)', flag: '🇱🇦' },
    { value: 'es', label: '🇪🇸 สเปน (Spanish)', flag: '🇪🇸' },
    { value: 'fr', label: '🇫🇷 ฝรั่งเศส (French)', flag: '🇫🇷' },
    { value: 'de', label: '🇩🇪 เยอรมัน (German)', flag: '🇩🇪' },
    { value: 'it', label: '🇮🇹 อิตาลี (Italian)', flag: '🇮🇹' },
    { value: 'pt', label: '🇵🇹 โปรตุเกส (Portuguese)', flag: '🇵🇹' },
    { value: 'ru', label: '🇷🇺 รัสเซีย (Russian)', flag: '🇷🇺' },
    { value: 'ar', label: '🇸🇦 อาหรับ (Arabic)', flag: '🇸🇦' },
    { value: 'hi', label: '🇮🇳 ฮินดี (Hindi)', flag: '🇮🇳' },
    { value: 'tr', label: '🇹🇷 ตุรกี (Turkish)', flag: '🇹🇷' },
    { value: 'pl', label: '🇵🇱 โปแลนด์ (Polish)', flag: '🇵🇱' },
    { value: 'nl', label: '🇳🇱 ดัตช์ (Dutch)', flag: '🇳🇱' },
    { value: 'sv', label: '🇸🇪 สวีเดน (Swedish)', flag: '🇸🇪' },
    { value: 'da', label: '🇩🇰 เดนมาร์ก (Danish)', flag: '🇩🇰' },
    { value: 'no', label: '🇳🇴 นอร์เวย์ (Norwegian)', flag: '🇳🇴' },
    { value: 'fi', label: '🇫🇮 ฟินแลนด์ (Finnish)', flag: '🇫🇮' },
    { value: 'cs', label: '🇨🇿 เช็ก (Czech)', flag: '🇨🇿' },
    { value: 'sk', label: '🇸🇰 สโลวัก (Slovak)', flag: '🇸🇰' },
    { value: 'hu', label: '🇭🇺 ฮังการี (Hungarian)', flag: '🇭🇺' },
    { value: 'ro', label: '🇷🇴 โรมาเนีย (Romanian)', flag: '🇷🇴' },
    { value: 'bg', label: '🇧🇬 บัลแกเรีย (Bulgarian)', flag: '🇧🇬' },
    { value: 'hr', label: '🇭🇷 โครเอเชีย (Croatian)', flag: '🇭🇷' },
    { value: 'sr', label: '🇷🇸 เซอร์เบีย (Serbian)', flag: '🇷🇸' },
    { value: 'sl', label: '🇸🇮 สโลวีเนีย (Slovenian)', flag: '🇸🇮' },
    { value: 'et', label: '🇪🇪 เอสโตเนีย (Estonian)', flag: '🇪🇪' },
    { value: 'lv', label: '🇱🇻 ลัตเวีย (Latvian)', flag: '🇱🇻' },
    { value: 'lt', label: '🇱🇹 ลิทัวเนีย (Lithuanian)', flag: '🇱🇹' },
    { value: 'mt', label: '🇲🇹 มอลตา (Maltese)', flag: '🇲🇹' },
    { value: 'cy', label: '🇬🇧 เวลส์ (Welsh)', flag: '🇬🇧' },
    { value: 'ga', label: '🇮🇪 ไอร์แลนด์ (Irish)', flag: '🇮🇪' },
    { value: 'eu', label: '🇪🇸 บาสก์ (Basque)', flag: '🇪🇸' },
    { value: 'ca', label: '🇪🇸 คาตาลัน (Catalan)', flag: '🇪🇸' },
    { value: 'gl', label: '🇪🇸 กาลิเซีย (Galician)', flag: '🇪🇸' },
    { value: 'oc', label: '🇫🇷 ออกซิตัน (Occitan)', flag: '🇫🇷' },
    { value: 'br', label: '🇫🇷 เบรอตง (Breton)', flag: '🇫🇷' },
    { value: 'is', label: '🇮🇸 ไอซ์แลนด์ (Icelandic)', flag: '🇮🇸' },
    { value: 'mk', label: '🇲🇰 มาซิโดเนีย (Macedonian)', flag: '🇲🇰' },
    { value: 'sq', label: '🇦🇱 แอลเบเนีย (Albanian)', flag: '🇦🇱' },
    { value: 'be', label: '🇧🇾 เบลารุส (Belarusian)', flag: '🇧🇾' },
    { value: 'uk', label: '🇺🇦 ยูเครน (Ukrainian)', flag: '🇺🇦' }
  ];

  useEffect(() => {
    // ตรวจสอบภาษาที่รองรับจาก API
    const fetchLanguages = async () => {
      try {
        const response = await fetch('http://localhost:5000/languages');
        if (response.ok) {
          const data = await response.json();
          setLanguages(data);
        }
      } catch (error) {
        console.warn('Could not fetch languages from API, using default list');
      } finally {
        setLoading(false);
      }
    };

    fetchLanguages();
  }, []);

  const handleSourceLanguageChange = (value) => {
    // ถ้าเลือกภาษาต้นทางเป็น auto ให้ไม่แสดงในปลายทาง
    if (value === 'auto') {
      onSourceLanguageChange(value);
    } else {
      onSourceLanguageChange(value);
      // ถ้าภาษาต้นทางและปลายทางเหมือนกัน ให้เปลี่ยนปลายทางเป็นไทย
      if (value === targetLanguage) {
        onTargetLanguageChange('th');
      }
    }
  };

  const handleTargetLanguageChange = (value) => {
    // ไม่ให้เลือกภาษาต้นทางเป็นปลายทาง
    if (value !== sourceLanguage) {
      onTargetLanguageChange(value);
    }
  };

  // กรองภาษาปลายทาง (ไม่รวม auto และภาษาต้นทาง)
  const targetLanguageOptions = languageOptions.filter(option => 
    option.value !== 'auto' && option.value !== sourceLanguage
  );

  if (loading) {
    return (
      <div className={`flex space-x-4 ${className}`}>
        <div className="animate-pulse bg-gray-200 h-10 w-48 rounded"></div>
        <div className="animate-pulse bg-gray-200 h-10 w-48 rounded"></div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col md:flex-row gap-4 ${className}`}>
      {/* ภาษาต้นทาง */}
      <div className="flex-1">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          🌍 ภาษาต้นทาง (Source Language)
        </label>
        <Dropdown
          options={languageOptions}
          value={sourceLanguage}
          onChange={handleSourceLanguageChange}
          placeholder="เลือกภาษาต้นทาง"
          className="w-full"
        />
      </div>

      {/* ลูกศรแสดงทิศทาง */}
      <div className="flex items-center justify-center">
        <div className="bg-blue-100 p-2 rounded-full">
          <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </div>
      </div>

      {/* ภาษาปลายทาง */}
      <div className="flex-1">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          🎯 ภาษาปลายทาง (Target Language)
        </label>
        <Dropdown
          options={targetLanguageOptions}
          value={targetLanguage}
          onChange={handleTargetLanguageChange}
          placeholder="เลือกภาษาปลายทาง"
          className="w-full"
        />
      </div>
    </div>
  );
};

export default LanguageSelector; 