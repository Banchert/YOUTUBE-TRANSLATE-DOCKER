// frontend/src/components/LoadingSpinner.jsx
import React from 'react';

/**
 * A reusable loading spinner component
 * @param {Object} props - Component props
 * @param {string} [props.size='md'] - Size of the spinner (sm, md, lg)
 * @param {string} [props.color='blue'] - Color of the spinner (blue, gray, green)
 * @param {string} [props.className=''] - Additional CSS classes
 */
const LoadingSpinner = ({ size = 'md', color = 'blue', className = '' }) => {
  // Size mapping
  const sizeMap = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4'
  };

  // Color mapping
  const colorMap = {
    blue: 'border-blue-600',
    gray: 'border-gray-600',
    green: 'border-green-600',
    purple: 'border-purple-600'
  };

  const spinnerSize = sizeMap[size] || sizeMap.md;
  const spinnerColor = colorMap[color] || colorMap.blue;

  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div
        className={`${spinnerSize} rounded-full border-t-transparent ${spinnerColor} animate-spin`}
        role="status"
        aria-label="loading"
      />
    </div>
  );
};

export default LoadingSpinner;
