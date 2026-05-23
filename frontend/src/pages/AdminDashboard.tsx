import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import type { User, AdminStats } from '../types';

const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [exportId, setExportId] = useState('');

  const fetchData = async () => {
    setLoading(true);
    try {
      const statsRes = await apiClient.get<AdminStats>('/admin/stats');
      setStats(statsRes.data);

      const usersRes = await apiClient.get<User[]>('/admin/users');
      setUsers(usersRes.data);
    } catch (err) {
      console.error(err);
      // Fallback mocks
      setStats({
        users: 14,
        therapy_sessions: 28,
        followup_records: 45,
        articles: 10,
        journals: 32,
        exercises: 12,
        support_resources: 8
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleExportCSV = async (patientId: number) => {
    try {
      // Since it requires JWT auth token in headers, we can fetch via Axios and trigger dynamic download
      const response = await apiClient.get(`/admin/export/${patientId}`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'text/csv' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', `patient_${patientId}_clinical_history.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (err) {
      alert('Failed to generate export file. Verify that the Patient ID exists.');
    }
  };

  const patients = users.filter(u => u.role === 'patient');

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-wide text-slate-100">System Administration Console</h2>
        <p className="text-xs text-slate-400">Monitor dual-database performance metrics and trigger compliant patient data CSV compilations.</p>
      </div>

      {/* Aggregate stats charts */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Platform Users', val: stats.users, desc: 'MySQL users table', icon: '👥' },
            { label: 'Therapy Sessions', val: stats.therapy_sessions, desc: 'MySQL clinical schedule', icon: '📅' },
            { label: 'Followup Checkups', val: stats.followup_records, desc: 'MySQL prescriptions', icon: '📋' },
            { label: 'Confidential Journals', val: stats.journals, desc: 'MongoDB document collection', icon: '📝' }
          ].map((card, i) => (
            <div key={i} className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-2 flex flex-col justify-between">
              <div className="flex justify-between items-start">
                <span className="text-xs text-slate-400 font-bold uppercase tracking-wider">{card.label}</span>
                <span className="text-lg">{card.icon}</span>
              </div>
              <div>
                <div className="text-3xl font-extrabold text-teal-400">{card.val}</div>
                <div className="text-[9px] text-slate-500 font-semibold">{card.desc}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Relational export and directory grid */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* Export console card */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="font-bold text-slate-100 text-sm">Export Clinical Patient Profile</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Merges MySQL clinical checkup logs and scheduled sessions with MongoDB mood journal diaries into a standardized flat CSV document.
          </p>

          <div className="space-y-2">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Patient ID</label>
            <div className="flex gap-2">
              <input
                type="number"
                value={exportId}
                onChange={(e) => setExportId(e.target.value)}
                placeholder="Enter ID..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
              />
              <button
                onClick={() => exportId && handleExportCSV(parseInt(exportId))}
                className="px-4 py-2 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 text-xs font-bold transition-all shadow-lg shadow-teal-500/10"
              >
                Export
              </button>
            </div>
          </div>

          <div className="border-t border-slate-800/60 pt-4 space-y-2">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Quick-Select Registered Patients</label>
            <div className="max-h-[140px] overflow-y-auto space-y-1.5 pr-1">
              {patients.map(p => (
                <button
                  key={p.user_id}
                  onClick={() => handleExportCSV(p.user_id)}
                  className="w-full text-left p-2 rounded-xl bg-slate-950 hover:bg-slate-900 border border-slate-850 hover:border-slate-700 transition-all flex items-center justify-between text-xs text-slate-300"
                >
                  <span className="font-medium truncate">{p.full_name}</span>
                  <span className="text-[10px] font-bold text-teal-400 bg-teal-400/5 px-2 py-0.5 rounded border border-teal-500/10">ID: {p.user_id}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* User directory */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 md:col-span-2 space-y-4">
          <h3 className="font-bold text-slate-100 text-sm">System User Directory</h3>
          {loading ? (
            <div className="text-center py-10 text-slate-500 text-xs">Querying database...</div>
          ) : (
            <div className="overflow-x-auto border border-slate-800/80 rounded-xl">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-900 border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider">
                    <th className="p-3">ID</th>
                    <th className="p-3">Username</th>
                    <th className="p-3">Role</th>
                    <th className="p-3">Full Name</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40">
                  {users.map((u) => (
                    <tr key={u.user_id} className="hover:bg-slate-900/40 transition-colors">
                      <td className="p-3 text-slate-500 font-bold">{u.user_id}</td>
                      <td className="p-3 text-slate-300">@{u.username}</td>
                      <td className="p-3 capitalize">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          u.role === 'admin' 
                            ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' 
                            : u.role === 'provider'
                            ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                            : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                        }`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="p-3 text-slate-200 font-medium">{u.full_name}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
