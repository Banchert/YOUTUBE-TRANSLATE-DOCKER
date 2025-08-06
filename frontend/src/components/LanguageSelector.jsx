// frontend/src/components/LanguageSelector.jsx
import React from 'react';

const LanguageSelector = ({ 
  value, 
  onChange, 
  placeholder = "เลือกภาษา",
  className = '' 
}) => {
  // รายการภาษาที่รองรับ
  const languageOptions = [
    { value: 'auto', label: '🔄 ตรวจจับอัตโนมัติ (Auto-detect)' },
    { value: 'th', label: '🇹🇭 ไทย (Thai)' },
    { value: 'en', label: '🇺🇸 อังกฤษ (English)' },
    { value: 'zh', label: '🇨🇳 จีน (Chinese)' },
    { value: 'ja', label: '🇯🇵 ญี่ปุ่น (Japanese)' },
    { value: 'ko', label: '🇰🇷 เกาหลี (Korean)' },
    { value: 'vi', label: '🇻🇳 เวียดนาม (Vietnamese)' },
    { value: 'id', label: '🇮🇩 อินโดนีเซีย (Indonesian)' },
    { value: 'ms', label: '🇲🇾 มาเลเซีย (Malay)' },
    { value: 'lo', label: '🇱🇦 ลาว (Lao)' },
    { value: 'es', label: '🇪🇸 สเปน (Spanish)' },
    { value: 'fr', label: '🇫🇷 ฝรั่งเศส (French)' },
    { value: 'de', label: '🇩🇪 เยอรมัน (German)' },
    { value: 'it', label: '🇮🇹 อิตาลี (Italian)' },
    { value: 'pt', label: '🇵🇹 โปรตุเกส (Portuguese)' },
    { value: 'ru', label: '🇷🇺 รัสเซีย (Russian)' },
    { value: 'ar', label: '🇸🇦 อาหรับ (Arabic)' },
    { value: 'hi', label: '🇮🇳 ฮินดี (Hindi)' },
    { value: 'tr', label: '🇹🇷 ตุรกี (Turkish)' },
    { value: 'pl', label: '🇵🇱 โปแลนด์ (Polish)' },
    { value: 'nl', label: '🇳🇱 ดัตช์ (Dutch)' },
    { value: 'sv', label: '🇸🇪 สวีเดน (Swedish)' },
    { value: 'da', label: '🇩🇰 เดนมาร์ก (Danish)' },
    { value: 'no', label: '🇳🇴 นอร์เวย์ (Norwegian)' },
    { value: 'fi', label: '🇫🇮 ฟินแลนด์ (Finnish)' },
    { value: 'cs', label: '🇨🇿 เช็ก (Czech)' },
    { value: 'sk', label: '🇸🇰 สโลวัก (Slovak)' },
    { value: 'hu', label: '🇭🇺 ฮังการี (Hungarian)' },
    { value: 'ro', label: '🇷🇴 โรมาเนีย (Romanian)' },
    { value: 'bg', label: '🇧🇬 บัลแกเรีย (Bulgarian)' },
    { value: 'hr', label: '🇭🇷 โครเอเชีย (Croatian)' },
    { value: 'sr', label: '🇷🇸 เซอร์เบีย (Serbian)' },
    { value: 'sl', label: '🇸🇮 สโลวีเนีย (Slovenian)' },
    { value: 'et', label: '🇪🇪 เอสโตเนีย (Estonian)' },
    { value: 'lv', label: '🇱🇻 ลัตเวีย (Latvian)' },
    { value: 'lt', label: '🇱🇹 ลิทัวเนีย (Lithuanian)' },
    { value: 'mt', label: '🇲🇹 มอลตา (Maltese)' },
    { value: 'cy', label: '🇬🇧 เวลส์ (Welsh)' },
    { value: 'ga', label: '🇮🇪 ไอร์แลนด์ (Irish)' },
    { value: 'eu', label: '🇪🇸 บาสก์ (Basque)' },
    { value: 'ca', label: '🇪🇸 คาตาลัน (Catalan)' },
    { value: 'gl', label: '🇪🇸 กาลิเซีย (Galician)' },
    { value: 'oc', label: '🇫🇷 ออกซิตัน (Occitan)' },
    { value: 'br', label: '🇫🇷 เบรอตง (Breton)' },
    { value: 'is', label: '🇮🇸 ไอซ์แลนด์ (Icelandic)' },
    { value: 'mk', label: '🇲🇰 มาซิโดเนีย (Macedonian)' },
    { value: 'sq', label: '🇦🇱 แอลเบเนีย (Albanian)' },
    { value: 'be', label: '🇧🇾 เบลารุส (Belarusian)' },
    { value: 'uk', label: '🇺🇦 ยูเครน (Ukrainian)' }
  ];

  const handleChange = (e) => {
    const selectedValue = e.target.value;
    onChange(selectedValue);
  };

  return (
    <select
      value={value}
      onChange={handleChange}
      className={`w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white ${className}`}
    >
      <option value="" disabled>
        {placeholder}
      </option>
      {languageOptions.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
};

export default LanguageSelector; 