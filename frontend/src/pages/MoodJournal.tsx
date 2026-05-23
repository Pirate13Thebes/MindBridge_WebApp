import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import type { JournalEntry } from '../types';
import Badge from '../components/Badge';
import Modal from '../components/Modal';

const MoodJournal: React.FC = () => {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [content, setContent] = useState('');
  const [mood, setMood] = useState<'great' | 'good' | 'okay' | 'low' | 'struggling'>('okay');
  const [msg, setMsg] = useState({ text: '', type: '' });

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get<JournalEntry[]>('/journal');
      setEntries(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntries();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content) {
      setMsg({ text: 'Please type some thoughts into your journal entry.', type: 'err' });
      return;
    }

    try {
      await apiClient.post('/journal', { content, mood });
      setMsg({ text: 'Journal entry successfully saved!', type: 'success' });
      setIsModalOpen(false);
      setContent('');
      setMood('okay');
      fetchEntries();
    } catch (err: any) {
      setMsg({ text: err.response?.data?.message || 'Failed to save journal.', type: 'err' });
    }
  };

  const getMoodEmoji = (m: string) => {
    switch (m) {
      case 'great': return '✨';
      case 'good': return '🙂';
      case 'okay': return '😐';
      case 'low': return '😔';
      case 'struggling': return '⚠️';
      default: return '📝';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-wide text-slate-100">Confidential Mood Journal</h2>
          <p className="text-xs text-slate-400">Express your thoughts privately and track PPD emotional recovery indices.</p>
        </div>
        <button
          onClick={() => {
            setMsg({ text: '', type: '' });
            setIsModalOpen(true);
          }}
          className="px-4 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold text-xs tracking-wide shadow-lg shadow-teal-500/10 transition-colors"
        >
          + Write Log
        </button>
      </div>

      {loading ? (
        <div className="text-center py-10 text-slate-500 text-sm">Retrieving journal history...</div>
      ) : entries.length === 0 ? (
        <div className="glass-panel text-center py-12 rounded-2xl border border-slate-800">
          <span className="text-3xl block mb-2">📝</span>
          <p className="text-sm font-medium text-slate-300">Your journal notebook is empty</p>
          <p className="text-xs text-slate-500 mt-1">Start recording logs to build a history of your PPD recovery path.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {entries.map((entry) => (
            <div key={entry._id} className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
              <div className="flex justify-between items-center pb-2 border-b border-slate-800/40">
                <div className="flex items-center gap-2">
                  <span className="text-sm">{getMoodEmoji(entry.mood)}</span>
                  <Badge status={entry.mood} />
                </div>
                <span className="text-[10px] text-slate-500 font-semibold">{entry.created_at.replace('T', ' ').split('.')[0]}</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">{entry.content}</p>
              <div className="text-[9px] text-slate-600 font-semibold tracking-tight">MongoDB Document ID: {entry._id}</div>
            </div>
          ))}
        </div>
      )}

      {/* Write Log Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Confidential Mood Log">
        <form onSubmit={handleSave} className="space-y-4">
          {msg.text && (
            <div className={`text-xs p-3 rounded-lg border ${
              msg.type === 'err' ? 'bg-rose-500/5 border-rose-500/10 text-rose-400' : 'bg-teal-500/5 border-teal-500/10 text-teal-400'
            }`}>
              {msg.text}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">How are you feeling today?</label>
            <div className="grid grid-cols-5 gap-1.5">
              {[
                { value: 'great', label: 'Great', icon: '✨' },
                { value: 'good', label: 'Good', icon: '🙂' },
                { value: 'okay', label: 'Okay', icon: '😐' },
                { value: 'low', label: 'Low', icon: '😔' },
                { value: 'struggling', label: 'Overwhelmed', icon: '⚠️' }
              ].map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setMood(opt.value as any)}
                  className={`py-2 px-1 rounded-xl text-[9px] font-bold border transition-colors flex flex-col items-center gap-1 ${
                    mood === opt.value
                      ? 'bg-teal-500 text-slate-950 border-teal-400'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <span className="text-sm">{opt.icon}</span>
                  <span>{opt.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Express Yourself</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={5}
              placeholder="Write down details about your energy levels, moods, anxiety triggers, or thoughts..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500 resize-none"
              required
            />
          </div>

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="flex-1 py-2 rounded-xl bg-slate-950 hover:bg-slate-800 text-slate-400 border border-slate-800 text-xs font-bold transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 text-xs font-bold shadow-lg shadow-teal-500/10 transition-colors"
            >
              Save Confidential Log
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default MoodJournal;
