import React from 'react';
import { motion } from 'framer-motion';

const StatsCard = ({ title, value, icon, color, change, delay = 0 }) => {
  const isPositive = change && change.startsWith('+');
  
  return (
    <motion.div
      className="relative overflow-hidden bg-white/80 backdrop-blur-md rounded-3xl shadow-xl border border-white/20 p-6 group cursor-pointer"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ scale: 1.02, y: -5 }}
    >
      {/* Background Gradient */}
      <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-5 group-hover:opacity-10 transition-opacity duration-300`}></div>
      
      {/* Icon Background */}
      <div className={`absolute top-4 right-4 w-12 h-12 bg-gradient-to-br ${color} opacity-10 rounded-2xl flex items-center justify-center`}>
        <span className="text-2xl">{icon}</span>
      </div>
      
      <div className="relative z-10">
        {/* Title */}
        <h3 className="text-sm font-medium text-gray-600 mb-2 uppercase tracking-wide">
          {title}
        </h3>
        
        {/* Value */}
        <div className="flex items-end space-x-2 mb-3">
          <span className="text-3xl font-bold text-gray-800">
            {value}
          </span>
          {change && (
            <span className={`text-sm font-medium px-2 py-1 rounded-full ${
              isPositive 
                ? 'text-green-700 bg-green-100' 
                : 'text-red-700 bg-red-100'
            }`}>
              {change}
            </span>
          )}
        </div>
        
        {/* Icon */}
        <div className="flex items-center space-x-2">
          <div className={`w-8 h-8 bg-gradient-to-br ${color} rounded-xl flex items-center justify-center shadow-md`}>
            <span className="text-white text-lg">{icon}</span>
          </div>
          <div className={`h-1 flex-1 bg-gradient-to-r ${color} rounded-full opacity-30`}></div>
        </div>
      </div>
      
      {/* Hover Effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/0 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
    </motion.div>
  );
};

export default StatsCard; 