import React from 'react';

interface BadgeProps {
  status: string;
}

const Badge: React.FC<BadgeProps> = ({ status }) => {
  const getStyles = () => {
    switch (status.toLowerCase()) {
      case 'completed':
      case 'great':
      case 'good':
        return 'bg-teal-500/10 text-teal-400 border-teal-500/20';
      case 'scheduled':
      case 'pending':
      case 'okay':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'cancelled':
      case 'low':
        return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
      case 'overdue':
      case 'struggling':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    }
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getStyles()}`}>
      {status.toUpperCase()}
    </span>
  );
};

export default Badge;
