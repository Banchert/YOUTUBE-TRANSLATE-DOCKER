// frontend/src/components/ProgressBar.jsx
import React from 'react';

/**
 * A reusable progress bar component
 * @param {Object} props - Component props
 * @param {number} props.value - Current progress value (0-100)
 * @param {string} [props.color='blue'] - Color of the progress bar
 * @param {string} [props.height='md'] - Height of the progress bar (sm, md, lg)
 * @param {boolean} [props.showLabel=true] - Whether to show the percentage label
 * @param {string} [props.className=''] - Additional CSS classes
 */
const ProgressBar = ({ 
  value = 0, 
  color = 'blue', 
  height = 'md', 
  showLabel = true,
  className = '' 
}) => {
  // Ensure value is between 0 and 100
  const progress = Math.min(Math.max(0, value), 100);
  
  // Height mapping
  const heightMap = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-4'
  };

  // Color mapping
  const colorMap = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
    purple: 'bg-purple-500',
    gray: 'bg-gray-500'
  };

  const barHeight = heightMap[height] || heightMap.md;
  const barColor = colorMap[color] || colorMap.blue;

  return (
    <div className={`w-full ${className}`}>
      <div className="w-full bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={`${barColor} ${barHeight} rounded-full transition-all duration-300 ease-in-out`}
          style={{ width: `${progress}%` }}
          role="progressbar"
          aria-valuenow={progress}
          aria-valuemin="0"
          aria-valuemax="100"
        />
      </div>
      {showLabel && (
        <div className="text-xs text-right mt-1 text-gray-600">
          {Math.round(progress)}%
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
