import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import type { SupportResource } from '../types';
import Modal from '../components/Modal';

interface SupportDirectoryProps {
  userRole: string;
}

const SupportDirectory: React.FC<SupportDirectoryProps> = ({ userRole }) => {
  const [resources, setResources] = useState<SupportResource[]>([]);
  const [activeTab, setActiveTab] = useState<'' | 'peer' | 'counselor' | 'hotline'>('');
  const [loading, setLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [name, setName] = useState('');
  const [category, setCategory] = useState<'peer' | 'counselor' | 'hotline'>('peer');
  const [contact, setContact] = useState('');
  const [description, setDescription] = useState('');
  const [msg, setMsg] = useState({ text: '', type: '' });

  const fetchResources = async (cat = '') => {
    setLoading(true);
    try {
      const response = await apiClient.get<SupportResource[]>('/support', {
        params: cat ? { category: cat } : {}
      });
      setResources(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResources(activeTab);
  }, [activeTab]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !contact) {
      setMsg({ text: 'Name and contact details are required.', type: 'err' });
      return;
    }

    try {
      await apiClient.post('/support', { name, category, contact, description });
      setMsg({ text: 'Listing saved to MongoDB!', type: 'success' });
      setIsModalOpen(false);
      // Reset form
      setName('');
      setContact('');
      setDescription('');
      fetchResources(activeTab);
    } catch (err: any) {
      setMsg({ text: err.response?.data?.message || 'Failed to save listing.', type: 'err' });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-wide text-slate-100">Professional & Peer Support Directories</h2>
          <p className="text-xs text-slate-400">Access support hotlines, counselor databases, and local peer associations.</p>
        </div>
        {userRole === 'admin' && (
          <button
            onClick={() => {
              setMsg({ text: '', type: '' });
              setIsModalOpen(true);
            }}
            className="px-4 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold text-xs tracking-wide shadow-lg shadow-teal-500/10 transition-colors"
          >
            + Add Listing
          </button>
        )}
      </div>

      {/* Tabs Filter Bar */}
      <div className="flex gap-2 bg-slate-900 p-1 rounded-xl border border-slate-800/80">
        {[
          { value: '', label: 'View All' },
          { value: 'peer', label: 'Peer Groups' },
          { value: 'counselor', label: 'Counselors' },
          { value: 'hotline', label: '24/7 Helplines' }
        ].map((tab) => {
          const isActive = activeTab === tab.value;
          return (
            <button
              key={tab.value}
              onClick={() => setActiveTab(tab.value as any)}
              className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${
                isActive
                  ? 'bg-teal-500 text-slate-950 shadow shadow-teal-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="text-center py-10 text-slate-500 text-sm">Searching MongoDB directory store...</div>
      ) : resources.length === 0 ? (
        <div className="glass-panel text-center py-12 rounded-2xl border border-slate-800">
          <span className="text-3xl block mb-2">📞</span>
          <p className="text-sm font-medium text-slate-300">No support directories found</p>
          <p className="text-xs text-slate-500 mt-1">Check back soon as specialists are updated periodically.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          {resources.map((res) => (
            <div key={res._id} className="glass-panel p-5 rounded-2xl flex flex-col justify-between border border-slate-800 space-y-4">
              <div className="space-y-3">
                <div className="flex justify-between items-start">
                  <span className="text-[10px] text-teal-400 font-bold uppercase tracking-wider bg-teal-400/5 px-2.5 py-0.5 rounded-full border border-teal-500/10">
                    {res.category === 'peer' ? 'Peer Network' : res.category === 'counselor' ? 'Certified Practitioner' : '24/7 Emergency Line'}
                  </span>
                  <span className="text-[9px] text-slate-600 font-semibold tracking-tight">MongoDB ID: {res._id}</span>
                </div>
                <h3 className="font-bold text-slate-100 text-base">{res.name}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{res.description}</p>
              </div>

              <div className="bg-slate-950/40 p-3 rounded-xl flex items-center justify-between border border-slate-800/20 text-xs">
                <span className="text-slate-500 font-bold uppercase tracking-wider text-[10px]">Contact Info:</span>
                <span className="text-teal-400 font-semibold">{res.contact}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Listing Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add Directory Listing (MongoDB Document)">
        <form onSubmit={handleCreate} className="space-y-4">
          {msg.text && (
            <div className={`text-xs p-3 rounded-lg border ${
              msg.type === 'err' ? 'bg-rose-500/5 border-rose-500/10 text-rose-400' : 'bg-teal-500/5 border-teal-500/10 text-teal-400'
            }`}>
              {msg.text}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Listing Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="E.g., National Maternal Mental Health Helpline"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
              required
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as any)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
              required
            >
              <option value="peer">Peer Support Network</option>
              <option value="counselor">Certified Counselor</option>
              <option value="hotline">Emergency 24/7 Hotline</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Contact Information</label>
            <input
              type="text"
              value={contact}
              onChange={(e) => setContact(e.target.value)}
              placeholder="E.g., 1-833-TLC-MAMA or support@ppd.org"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
              required
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Resource Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder="Provide a brief summary of helpline hours, location, or counseling specialties..."
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
              Save Listing
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default SupportDirectory;
