import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import type { Reminder } from '../types';

interface ReminderBannerProps {
  userRole: string;
}

const ReminderBanner: React.FC<ReminderBannerProps> = ({ userRole }) => {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (userRole !== 'patient') return;

    const fetchReminders = async () => {
      setLoading(true);
      try {
        const response = await apiClient.get<Reminder[]>('/dashboard/reminders');
        setReminders(response.data);
      } catch (err) {
        console.error('Failed to load reminders feed:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchReminders();
  }, [userRole]);

  if (userRole !== 'patient' || reminders.length === 0 || loading) return null;

  return (
    <div className="space-y-3 mb-6 animate-fade-in">
      <div className="bg-slate-900 border-l-4 border-teal-500 rounded-r-xl p-4 shadow-lg shadow-teal-500/5">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-teal-400">✨</span>
            <h3 className="font-semibold text-slate-200 text-sm tracking-wide">MindBridge Health Assistant</h3>
          </div>
          <span className="text-[10px] text-teal-400 font-bold bg-teal-400/10 px-2 py-0.5 rounded-full">
            {reminders.length} Active Alert{reminders.length > 1 ? 's' : ''}
          </span>
        </div>
        <div className="space-y-2">
          {reminders.map((r, i) => {
            const isOverdue = r.type === 'overdue';
            return (
              <div
                key={i}
                className={`text-xs py-2 px-3 rounded-lg flex items-center gap-3 border ${
                  isOverdue
                    ? 'bg-rose-500/5 border-rose-500/10 text-rose-300'
                    : 'bg-teal-500/5 border-teal-500/10 text-teal-300'
                }`}
              >
                <span>{isOverdue ? '⚠️' : '📅'}</span>
                <span className="font-medium leading-relaxed">{r.message}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ReminderBanner;
