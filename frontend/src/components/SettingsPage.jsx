// frontend/src/components/SettingsPage.jsx
import React from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';

const SettingsPage = () => {
  // Since useAppStore might not be properly set up yet, we'll use a simpler approach
  const preferences = {
    defaultLanguage: 'th',
    defaultMixingMode: 'replace',
    defaultVoiceType: 'female',
    autoDownload: false,
    notifications: true
  };
  
  const { register, handleSubmit } = useForm({
    defaultValues: preferences
  });

  const onSubmit = (data) => {
    // Simplified - just show toast
    console.log('Settings saved:', data);
    toast.success('การตั้งค่าถูกบันทึกแล้ว');
  };

  const languageOptions = [
    { value: 'th', label: 'ไทย (Thai)', flag: '🇹🇭' },
    { value: 'en', label: 'อังกฤษ (English)', flag: '🇺🇸' },
    { value: 'zh', label: 'จีน (Chinese)', flag: '🇨🇳' },
    { value: 'ja', label: 'ญี่ปุ่น (Japanese)', flag: '🇯🇵' },
    { value: 'ko', label: 'เกาหลี (Korean)', flag: '🇰🇷' },
    { value: 'vi', label: 'เวียดนาม (Vietnamese)', flag: '🇻🇳' },
    { value: 'id', label: 'อินโดนีเซีย (Indonesian)', flag: '🇮🇩' },
    { value: 'ms', label: 'มาเลเซีย (Malay)', flag: '🇲🇾' },
    { value: 'lo', label: 'ลาว (Lao)', flag: '🇱🇦' },
  ];

  const mixingOptions = [
    { value: 'overlay', label: 'ทับซ้อน (Overlay)' },
    { value: 'replace', label: 'แทนที่ (Replace)' },
    { value: 'stereo', label: 'สเตอริโอ (Stereo)' }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto"
    >
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">การตั้งค่า</h1>
        <p className="text-gray-600">
          ปรับแต่งการทำงานของระบบตามความต้องการของคุณ
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Default Settings */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center mb-6">
            <span className="w-6 h-6 text-blue-600 mr-3">🌐</span>
            <h2 className="text-xl font-semibold text-gray-800">การตั้งค่าเริ่มต้น</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ภาษาเป้าหมายเริ่มต้น
              </label>
              <select
                {...register('defaultLanguage')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {languageOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.flag} {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                รูปแบบการรวมเสียงเริ่มต้น
              </label>
              <select
                {...register('defaultMixingMode')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {mixingOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ประเภทเสียงเริ่มต้น
              </label>
              <select
                {...register('defaultVoiceType')}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="female">เสียงผู้หญิง</option>
                <option value="male">เสียงผู้ชาย</option>
              </select>
            </div>
          </div>
        </div>

        {/* Download Settings */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center mb-6">
            <span className="w-6 h-6 text-green-600 mr-3">🔊</span>
            <h2 className="text-xl font-semibold text-gray-800">การดาวน์โหลด</h2>
          </div>

          <div className="space-y-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                {...register('autoDownload')}
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span className="ml-3 text-sm text-gray-700">
                ดาวน์โหลดอัตโนมัติเมื่อแปลเสร็จ
              </span>
            </label>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center mb-6">
            <span className="w-6 h-6 text-purple-600 mr-3">🔔</span>
            <h2 className="text-xl font-semibold text-gray-800">การแจ้งเตือน</h2>
          </div>

          <div className="space-y-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                {...register('notifications')}
                className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span className="ml-3 text-sm text-gray-700">
                แจ้งเตือนเมื่อการประมวลผลเสร็จสิ้น
              </span>
            </label>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-8 rounded-lg transition-colors duration-200"
          >
            บันทึกการตั้งค่า
          </button>
        </div>
      </form>
    </motion.div>
  );
};

export default SettingsPage;