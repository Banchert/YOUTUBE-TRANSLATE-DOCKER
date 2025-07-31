// frontend/src/components/StatusBadge.jsx
import React from 'react';

/**
 * A reusable status badge component
 * @param {Object} props - Component props
 * @param {string} props.status - Status to display (completed, processing, failed, pending)
 * @param {string} [props.size='md'] - Size of the badge (sm, md, lg)
 * @param {string} [props.className=''] - Additional CSS classes
 */
const StatusBadge = ({ status, size = 'md', className = '' }) => {
  // Map status to colors and labels
  const statusConfig = {
    completed: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      label: 'เสร็จสิ้น'
    },
    processing: {
      bg: 'bg-blue-100',
      text: 'text-blue-800',
      label: 'กำลังประมวลผล'
    },
    failed: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      label: 'ล้มเหลว'
    },
    pending: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-800',
      label: 'รอดำเนินการ'
    }
  };

  // Size mapping
  const sizeMap = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base'
  };

  const config = statusConfig[status] || statusConfig.pending;
  const badgeSize = sizeMap[size] || sizeMap.md;

  return (
    <span 
      className={`inline-flex items-center rounded-full font-medium ${config.bg} ${config.text} ${badgeSize} ${className}`}
    >
      {config.label}
    </span>
  );
};

export default StatusBadge;
