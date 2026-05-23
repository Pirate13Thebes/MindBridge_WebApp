import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import type { User } from './types';

// Layout Components
import Sidebar from './components/Sidebar';
import ReminderBanner from './components/ReminderBanner';

// Pages
import Auth from './pages/Auth';
import DashboardHome from './pages/DashboardHome';
import TherapySessions from './pages/TherapySessions';
import FollowUpTracker from './pages/FollowUpTracker';
import EducationHub from './pages/EducationHub';
import SupportDirectory from './pages/SupportDirectory';
import MaternalWorkouts from './pages/MaternalWorkouts';
import MoodJournal from './pages/MoodJournal';
import AdminDashboard from './pages/AdminDashboard';

const App: React.FC = () => {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    // Read cached login sessions
    const savedToken = localStorage.getItem('token');
    const savedUserStr = localStorage.getItem('user');

    if (savedToken && savedUserStr) {
      setToken(savedToken);
      try {
        setUser(JSON.parse(savedUserStr));
      } catch (err) {
        localStorage.clear();
      }
    }
    setLoading(false);
  }, []);

  const handleLoginSuccess = (newToken: string, newUser: User) => {
    localStorage.setItem('token', newToken);
    localStorage.setItem('user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  const handleLogout = () => {
    localStorage.clear();
    setToken(null);
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-400 text-sm">
        Connecting to MindBridge Core...
      </div>
    );
  }

  // Redirect to Auth if not logged in
  if (!token || !user) {
    return <Auth onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <Router>
      <div className="flex bg-slate-950 text-slate-100 min-h-screen overflow-x-hidden">
        {/* Navigation Sidebar */}
        <Sidebar 
          user={user} 
          isOpen={sidebarOpen} 
          onClose={() => setSidebarOpen(false)} 
          onLogout={handleLogout} 
        />

        {/* Content Panel Frame */}
        <main className="flex-1 flex flex-col min-h-screen overflow-y-auto w-full">
          {/* Header element */}
          <header className="h-16 border-b border-slate-900 px-6 md:px-8 flex items-center justify-between bg-slate-950/40 backdrop-blur-sm sticky top-0 z-30 w-full">
            <div className="flex items-center gap-3">
              {/* Responsive mobile toggle */}
              <button 
                onClick={() => setSidebarOpen(true)}
                className="md:hidden p-2 -ml-2 text-slate-400 hover:text-slate-200 hover:bg-slate-900 rounded-xl border border-slate-800 transition-colors"
                title="Open menu"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider hidden sm:inline">MindBridge Network Online</span>
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider sm:hidden">Online</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-400 font-bold">Role View:</span>
              <span className="text-xs font-bold text-teal-400 bg-teal-400/5 border border-teal-500/20 px-2.5 py-1 rounded-xl">
                {user.role.toUpperCase()}
              </span>
            </div>
          </header>

          {/* Main workspace cards */}
          <div className="flex-grow p-6 md:p-8 max-w-6xl w-full mx-auto space-y-6">
            {/* Automatic reminders for Patient role */}
            <ReminderBanner userRole={user.role} />

            {/* Dashboard Routing Table */}
            <Routes>
              <Route path="/" element={<DashboardHome user={user} />} />
              <Route path="/therapy" element={<TherapySessions userRole={user.role} />} />
              <Route path="/followup" element={<FollowUpTracker userRole={user.role} />} />
              <Route path="/education" element={<EducationHub userRole={user.role} />} />
              <Route path="/support" element={<SupportDirectory userRole={user.role} />} />
              <Route path="/exercise" element={<MaternalWorkouts />} />
              <Route path="/journal" element={<MoodJournal />} />
              
              {/* Restrict Admin page view */}
              <Route 
                path="/admin" 
                element={user.role === 'admin' ? <AdminDashboard /> : <Navigate to="/" replace />} 
              />
              
              {/* Fallback route */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
};

export default App;
