import React, { useState } from 'react';
import apiClient from '../api/client';
import type { AuthResponse, Role } from '../types';

interface AuthProps {
  onLoginSuccess: (token: string, user: AuthResponse['user']) => void;
}

const Auth: React.FC<AuthProps> = ({ onLoginSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  
  // Forms State
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<Role>('patient');
  
  const [msg, setMsg] = useState({ text: '', type: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg({ text: '', type: '' });

    if (!username || !password || (!isLogin && !fullName)) {
      setMsg({ text: 'Please fill out all required fields.', type: 'err' });
      return;
    }

    setLoading(true);
    try {
      if (isLogin) {
        // Authenticate
        const response = await apiClient.post<AuthResponse>('/auth/login', { username, password });
        onLoginSuccess(response.data.token, response.data.user);
      } else {
        // Register account
        await apiClient.post('/auth/register', { username, password, role, full_name: fullName });
        setMsg({ text: 'Account registered successfully! You can now log in.', type: 'success' });
        setIsLogin(true);
        setPassword('');
      }
    } catch (err: any) {
      setMsg({ text: err.response?.data?.message || 'Authentication statement failed.', type: 'err' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-slate-950 relative overflow-hidden">
      {/* Dynamic background accents */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl -z-10 animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl -z-10"></div>
      
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6 relative z-10">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center font-bold text-slate-950 text-xl shadow-xl shadow-teal-500/20 mx-auto">
            M
          </div>
          <h2 className="text-2xl font-extrabold text-slate-100 tracking-tight">
            {isLogin ? 'Sign In to MindBridge' : 'Create an Account'}
          </h2>
          <p className="text-xs text-slate-400">
            {isLogin 
              ? 'Enter credentials to access clinical PPD care services.' 
              : 'Sign up to configure care checklists and journaling.'}
          </p>
        </div>

        {msg.text && (
          <div className={`text-xs p-3.5 rounded-2xl border leading-relaxed ${
            msg.type === 'err' ? 'bg-rose-500/5 border-rose-500/15 text-rose-400' : 'bg-teal-500/5 border-teal-500/15 text-teal-400'
          }`}>
            {msg.text}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <>
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Full Name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Jane Doe"
                  className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 text-xs text-slate-200 focus:outline-none focus:border-teal-500 transition-colors"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Choose Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value as Role)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 text-xs text-slate-200 focus:outline-none focus:border-teal-500 transition-colors"
                  required
                >
                  <option value="patient">Patient (PPD Recovery support)</option>
                  <option value="provider">Professional Specialist (Therapist)</option>
                  <option value="admin">System Administrator</option>
                  <option value="volunteer">Community Volunteer</option>
                  <option value="family">Family/Caregiver Partner</option>
                </select>
              </div>
            </>
          )}

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="username"
              className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 text-xs text-slate-200 focus:outline-none focus:border-teal-500 transition-colors"
              required
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••"
              className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3 text-xs text-slate-200 focus:outline-none focus:border-teal-500 transition-colors"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-2xl bg-teal-500 hover:bg-teal-400 disabled:bg-teal-700 text-slate-950 font-bold text-xs tracking-wider uppercase transition-colors shadow-lg shadow-teal-500/10 pt-3"
          >
            {loading ? 'Processing...' : isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <div className="text-center text-xs text-slate-500 pt-2 border-t border-slate-800/40">
          <span>{isLogin ? "Don't have an account?" : "Already registered?"}</span>{' '}
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setMsg({ text: '', type: '' });
            }}
            className="text-teal-400 font-semibold hover:text-teal-300 transition-colors focus:outline-none"
          >
            {isLogin ? 'Sign Up' : 'Sign In'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Auth;
