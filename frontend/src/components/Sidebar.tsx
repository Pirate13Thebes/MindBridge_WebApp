import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import type { Role } from '../types';

interface SidebarProps {
  user: {
    username: string;
    full_name: string;
    role: Role;
  } | null;
  isOpen: boolean;
  onClose: () => void;
  onLogout: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ user, isOpen, onClose, onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();

  if (!user) return null;

  const currentRole = user.role;

  // Define navigation based on roles
  const getNavLinks = () => {
    switch (currentRole) {
      case 'patient':
        return [
          { name: 'Dashboard Home', path: '/' },
          { name: 'Clinical Therapy', path: '/therapy' },
          { name: 'Follow-up Tracker', path: '/followup' },
          { name: 'Article Search', path: '/education' },
          { name: 'Support Groups', path: '/support' },
          { name: 'Maternal Exercises', path: '/exercise' },
          { name: 'Mood Journal', path: '/journal' },
        ];
      case 'provider':
        return [
          { name: 'Dashboard Home', path: '/' },
          { name: 'Clinical Therapy', path: '/therapy' },
          { name: 'Compliance Monitor', path: '/followup' },
          { name: 'Psychoeducational Articles', path: '/education' },
        ];
      case 'admin':
        return [
          { name: 'Dashboard Home', path: '/' },
          { name: 'Therapy Roster', path: '/therapy' },
          { name: 'Article CRUD', path: '/education' },
          { name: 'Support CRM', path: '/support' },
          { name: 'Admin Console', path: '/admin' },
        ];
      case 'volunteer':
      case 'family':
        return [
          { name: 'Dashboard Home', path: '/' },
          { name: 'Psychoeducational Articles', path: '/education' },
          { name: 'Support Directories', path: '/support' },
          { name: 'Maternal Workouts', path: '/exercise' },
        ];
      default:
        return [{ name: 'Dashboard Home', path: '/' }];
    }
  };

  const navLinks = getNavLinks();

  return (
    <>
      {/* Mobile Backdrop overlay */}
      {isOpen && (
        <div 
          onClick={onClose} 
          className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 md:hidden transition-all duration-300"
        />
      )}

      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 border-r border-slate-800 flex flex-col min-h-screen text-slate-300 transform md:relative md:translate-x-0 transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        {/* Title logo */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center font-bold text-slate-950 text-lg shadow-lg shadow-teal-500/20">
              M
            </div>
            <div>
              <h1 className="font-bold text-slate-100 tracking-wide text-md">MindBridge</h1>
              <span className="text-xs text-teal-400 font-medium">PPD Support Care</span>
            </div>
          </div>
          
          {/* Mobile close button */}
          <button
            onClick={onClose}
            className="md:hidden p-1.5 rounded-xl bg-slate-950 hover:bg-slate-850 text-slate-400 border border-slate-800 hover:text-slate-200 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Navigation list */}
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {navLinks.map((link) => {
            const isActive = location.pathname === link.path;
            return (
              <button
                key={link.path}
                onClick={() => {
                  navigate(link.path);
                  onClose();
                }}
                className={`w-full text-left px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 flex items-center justify-between ${
                  isActive
                    ? 'bg-teal-600/20 border border-teal-500/30 text-teal-300 font-semibold'
                    : 'hover:bg-slate-800/60 hover:text-slate-100 border border-transparent'
                }`}
              >
                <span>{link.name}</span>
                {isActive && <span className="w-1.5 h-1.5 rounded-full bg-teal-400 shadow shadow-teal-400"></span>}
              </button>
            );
          })}
        </nav>

        {/* User profile */}
        <div className="p-4 border-t border-slate-800 flex items-center justify-between bg-slate-950/40">
          <div className="truncate pr-2">
            <div className="font-semibold text-slate-100 text-sm truncate">{user.full_name}</div>
            <div className="text-xs text-slate-500 truncate">@{user.username}</div>
          </div>
          <button
            onClick={() => {
              onLogout();
              onClose();
            }}
            className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800/50 rounded-lg transition-colors duration-150"
            title="Logout Account"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
