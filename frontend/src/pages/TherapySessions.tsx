import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import type { TherapySession, User } from '../types';
import Badge from '../components/Badge';
import Modal from '../components/Modal';

interface TherapySessionsProps {
  userRole: string;
}

const TherapySessions: React.FC<TherapySessionsProps> = ({ userRole }) => {
  const [sessions, setSessions] = useState<TherapySession[]>([]);
  const [providers, setProviders] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  // Booking Form State
  const [therapistId, setTherapistId] = useState('');
  const [sessionDate, setSessionDate] = useState('');
  const [notes, setNotes] = useState('');
  const [msg, setMsg] = useState({ text: '', type: '' });

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get<TherapySession[]>('/therapy');
      setSessions(response.data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSpecialists = async () => {
    try {
      // In demo mode or if offline, we can query users
      const response = await apiClient.get<User[]>('/admin/users');
      setProviders(response.data.filter(u => u.role === 'provider'));
    } catch (err) {
      // Offline fallback
      setProviders([
        { user_id: 1, username: ' Sarah', full_name: 'Dr. Sarah Jenkins (PPD Expert)', role: 'provider' },
        { user_id: 2, username: ' Emily', full_name: 'Dr. Emily Watson (Maternal Counselor)', role: 'provider' }
      ]);
    }
  };

  useEffect(() => {
    fetchSessions();
    if (userRole === 'patient') {
      fetchSpecialists();
    }
  }, [userRole]);

  const handleBook = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!therapistId || !sessionDate) {
      setMsg({ text: 'Please fill out all required fields.', type: 'err' });
      return;
    }

    try {
      await apiClient.post('/therapy', {
        therapist_id: parseInt(therapistId),
        session_date: sessionDate,
        notes
      });
      setMsg({ text: 'Session successfully booked!', type: 'success' });
      setIsModalOpen(false);
      // Reset form
      setNotes('');
      setTherapistId('');
      setSessionDate('');
      fetchSessions();
    } catch (err: any) {
      setMsg({ text: err.response?.data?.message || 'Failed to book session.', type: 'err' });
    }
  };

  const handleUpdateStatus = async (sessionId: number, status: 'completed' | 'cancelled') => {
    try {
      await apiClient.patch(`/therapy/${sessionId}`, { status });
      fetchSessions();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Update failed');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-wide text-slate-100">Clinical Sessions</h2>
          <p className="text-xs text-slate-400">Manage your clinical counseling appointments.</p>
        </div>
        {userRole === 'patient' && (
          <button
            onClick={() => {
              setMsg({ text: '', type: '' });
              setIsModalOpen(true);
            }}
            className="px-4 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold text-xs tracking-wide shadow-lg shadow-teal-500/10 transition-colors"
          >
            + Schedule Session
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-10 text-slate-500 text-sm">Loading sessions...</div>
      ) : sessions.length === 0 ? (
        <div className="glass-panel text-center py-12 rounded-2xl border border-slate-800">
          <span className="text-3xl block mb-2">📅</span>
          <p className="text-sm font-medium text-slate-300">No scheduled sessions</p>
          <p className="text-xs text-slate-500 mt-1">Book your first clinic visit to begin PPD monitoring.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          {sessions.map((sess) => (
            <div key={sess.session_id} className="glass-panel p-5 rounded-2xl flex flex-col justify-between border border-slate-800 space-y-4">
              <div className="space-y-3">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-[10px] text-teal-400 font-bold uppercase tracking-wider block mb-1">
                      Session ID: #{sess.session_id}
                    </span>
                    <h3 className="font-bold text-slate-200 text-sm">
                      {userRole === 'patient' ? `Therapist: ${sess.therapist_name}` : `Patient: ${sess.patient_name}`}
                    </h3>
                  </div>
                  <Badge status={sess.status} />
                </div>
                
                <div className="text-xs text-slate-400 flex items-center gap-2 bg-slate-950/40 p-2.5 rounded-xl">
                  <span>📅</span>
                  <span className="font-semibold text-slate-300">{sess.session_date}</span>
                </div>

                <div className="text-xs text-slate-400 leading-relaxed">
                  <span className="font-bold block text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">Session Notes:</span>
                  {sess.notes || 'No description notes provided.'}
                </div>
              </div>

              {sess.status === 'scheduled' && (
                <div className="flex items-center gap-2 pt-2 border-t border-slate-800/40">
                  {userRole === 'provider' && (
                    <button
                      onClick={() => handleUpdateStatus(sess.session_id, 'completed')}
                      className="flex-1 py-1.5 rounded-lg bg-teal-500/10 hover:bg-teal-500/20 text-teal-400 text-xs font-bold border border-teal-500/20 transition-colors"
                    >
                      ✓ Complete Session
                    </button>
                  )}
                  <button
                    onClick={() => handleUpdateStatus(sess.session_id, 'cancelled')}
                    className="flex-1 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-bold border border-rose-500/20 transition-colors"
                  >
                    Cancel Appointment
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Book Session Modal Overlay */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Book Clinical Therapy Session">
        <form onSubmit={handleBook} className="space-y-4">
          {msg.text && (
            <div className={`text-xs p-3 rounded-lg border ${
              msg.type === 'err' ? 'bg-rose-500/5 border-rose-500/10 text-rose-400' : 'bg-teal-500/5 border-teal-500/10 text-teal-400'
            }`}>
              {msg.text}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Select Mental Health Specialist</label>
            <select
              value={therapistId}
              onChange={(e) => setTherapistId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
              required
            >
              <option value="">-- Select Specialist --</option>
              {providers.map((p) => (
                <option key={p.user_id} value={p.user_id}>{p.full_name}</option>
              ))}
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Appointment Date</label>
            <input
              type="date"
              value={sessionDate}
              onChange={(e) => setSessionDate(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
              required
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Reason/Notes for Session (Optional)</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              placeholder="E.g., discussing postpartum fatigue, medication reviews..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500 resize-none"
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
              Schedule Visit
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default TherapySessions;
