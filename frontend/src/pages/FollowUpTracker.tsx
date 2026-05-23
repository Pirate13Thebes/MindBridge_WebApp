import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import type { FollowUpRecord } from '../types';
import Badge from '../components/Badge';
import Modal from '../components/Modal';

interface FollowUpTrackerProps {
  userRole: string;
}

const FollowUpTracker: React.FC<FollowUpTrackerProps> = ({ userRole }) => {
  const [records, setRecords] = useState<FollowUpRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Task Form State
  const [recordType, setRecordType] = useState('medication');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [msg, setMsg] = useState({ text: '', type: '' });

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get<FollowUpRecord[]>('/followup');
      setRecords(response.data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [userRole]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description || !dueDate) {
      setMsg({ text: 'Please enter a description and due date.', type: 'err' });
      return;
    }

    try {
      await apiClient.post('/followup', {
        record_type: recordType,
        description,
        due_date: dueDate
      });
      setMsg({ text: 'Task logged successfully!', type: 'success' });
      setIsModalOpen(false);
      // Reset fields
      setDescription('');
      setDueDate('');
      fetchRecords();
    } catch (err: any) {
      setMsg({ text: err.response?.data?.message || 'Failed to save task.', type: 'err' });
    }
  };

  const handleComplete = async (recordId: number) => {
    try {
      await apiClient.patch(`/followup/${recordId}/complete`);
      fetchRecords();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Checkoff failed');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-wide text-slate-100">Care Follow-up Tracker</h2>
          <p className="text-xs text-slate-400">
            {userRole === 'patient'
              ? 'Log and check off routine medications, pediatrician checkups, or clinical injections.'
              : 'Monitor compliance and post-natal adherence records across all patients.'}
          </p>
        </div>
        {userRole === 'patient' && (
          <button
            onClick={() => {
              setMsg({ text: '', type: '' });
              setIsModalOpen(true);
            }}
            className="px-4 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold text-xs tracking-wide shadow-lg shadow-teal-500/10 transition-colors"
          >
            + Add Task
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-10 text-slate-500 text-sm">Loading tracker...</div>
      ) : records.length === 0 ? (
        <div className="glass-panel text-center py-12 rounded-2xl border border-slate-800">
          <span className="text-3xl block mb-2">📋</span>
          <p className="text-sm font-medium text-slate-300">No scheduled tasks</p>
          <p className="text-xs text-slate-500 mt-1">Start tracking medication schedules or routine checks today.</p>
        </div>
      ) : (
        <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-900 border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider">
                  {userRole !== 'patient' && <th className="p-4">Patient Name</th>}
                  <th className="p-4">Category</th>
                  <th className="p-4">Description</th>
                  <th className="p-4">Due Date</th>
                  <th className="p-4">Status</th>
                  {userRole === 'patient' && <th className="p-4 text-center">Action</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40">
                {records.map((r) => (
                  <tr key={r.record_id} className="hover:bg-slate-900/40 transition-colors">
                    {userRole !== 'patient' && (
                      <td className="p-4 font-semibold text-slate-200">{r.patient_name || 'System Patient'}</td>
                    )}
                    <td className="p-4 capitalize">
                      <span className="font-semibold text-teal-400 bg-teal-400/5 px-2 py-0.5 rounded-md border border-teal-500/10">
                        {r.record_type}
                      </span>
                    </td>
                    <td className="p-4 text-slate-300 font-medium">{r.description}</td>
                    <td className="p-4 text-slate-400">{r.due_date}</td>
                    <td className="p-4">
                      <Badge status={r.status} />
                    </td>
                    {userRole === 'patient' && (
                      <td className="p-4 text-center">
                        {r.status !== 'completed' ? (
                          <button
                            onClick={() => handleComplete(r.record_id)}
                            className="px-3 py-1 rounded-lg bg-teal-500/10 hover:bg-teal-500/20 text-teal-400 font-bold border border-teal-500/20 transition-colors"
                          >
                            Check Off ✓
                          </button>
                        ) : (
                          <span className="text-slate-500 text-[10px] font-bold bg-slate-950/60 px-2 py-1 rounded-md">COMPLETED</span>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Log Task Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Log Follow-up Medication or Checkup">
        <form onSubmit={handleCreate} className="space-y-4">
          {msg.text && (
            <div className={`text-xs p-3 rounded-lg border ${
              msg.type === 'err' ? 'bg-rose-500/5 border-rose-500/10 text-rose-400' : 'bg-teal-500/5 border-teal-500/10 text-teal-400'
            }`}>
              {msg.text}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Care Category</label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'medication', label: 'Medication' },
                { value: 'injection', label: 'Injection' },
                { value: 'checkup', label: 'Checkup' }
              ].map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setRecordType(opt.value)}
                  className={`py-2 rounded-xl text-xs font-bold border transition-colors ${
                    recordType === opt.value
                      ? 'bg-teal-500 text-slate-950 border-teal-400'
                      : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Task Description</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="E.g., Take Postnatal Prenatal Vitamin Complex 50mg"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
              required
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Due Date</label>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
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
              Save Schedule
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default FollowUpTracker;
