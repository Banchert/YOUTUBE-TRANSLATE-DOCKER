// frontend/src/components/Toast.jsx
import React, { useState, useEffect } from 'react';

/**
 * A simple toast notification component
 * @param {Object} props - Component props
 * @param {string} props.message - Message to display
 * @param {string} [props.type='info'] - Type of toast (info, success, error, warning)
 * @param {number} [props.duration=3000] - Duration in ms before auto-dismissal
 * @param {function} [props.onClose] - Function to call when toast is dismissed
 */
const Toast = ({ message, type = 'info', duration = 3000, onClose }) => {
  const [visible, setVisible] = useState(true);

  // Type mapping for styles
  const typeStyles = {
    info: 'bg-blue-50 text-blue-800 border-blue-300',
    success: 'bg-green-50 text-green-800 border-green-300',
    error: 'bg-red-50 text-red-800 border-red-300',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-300'
  };

  // Icons for different types
  const icons = {
    info: 'ℹ️',
    success: '✅',
    error: '❌',
    warning: '⚠️'
  };

  // Auto-dismiss after duration
  useEffect(() => {
    if (duration === 0) return; // Don't auto-dismiss if duration is 0

    const timer = setTimeout(() => {
      setVisible(false);
      if (onClose) onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  if (!visible) return null;

  return (
    <div 
      className={`fixed top-4 right-4 z-50 flex items-center p-4 rounded-lg border shadow-lg transition-all duration-300 ${typeStyles[type] || typeStyles.info}`}
      role="alert"
    >
      <span className="mr-2">{icons[type] || icons.info}</span>
      <div className="ml-3 text-sm font-medium">{message}</div>
      <button
        type="button"
        className="ml-auto -mx-1.5 -my-1.5 rounded-lg p-1.5 inline-flex h-8 w-8 focus:outline-none"
        onClick={() => {
          setVisible(false);
          if (onClose) onClose();
        }}
        aria-label="Close"
      >
        <span className="sr-only">Close</span>
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  );
};

export default Toast;
