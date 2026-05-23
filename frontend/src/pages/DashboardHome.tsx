import React from 'react';
import type { Role } from '../types';

interface DashboardHomeProps {
  user: {
    username: string;
    full_name: string;
    role: Role;
  } | null;
}

const DashboardHome: React.FC<DashboardHomeProps> = ({ user }) => {
  if (!user) return null;

  const role = user.role;

  return (
    <div className="space-y-6">
      {/* Premium Hero Greeting banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-teal-950 to-slate-900 border border-slate-800 p-8 shadow-2xl">
        {/* Subtle grid background styling */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30"></div>
        
        <div className="relative z-10 space-y-2">
          <span className="text-xs text-teal-400 font-bold bg-teal-400/10 px-3 py-1 rounded-full uppercase tracking-wider">
            {role.toUpperCase()} Space
          </span>
          <h2 className="text-3xl font-extrabold text-slate-100 tracking-tight">
            Hello, {user.full_name}!
          </h2>
          <p className="text-slate-400 max-w-xl text-sm leading-relaxed">
            Welcome to the MindBridge PPD Clinical Care Suite. We coordinate clinical follow-ups, mood journal logs, and therapy appointments into a unified recovery roadmap.
          </p>
        </div>
      </div>

      {/* Role-specific highlights */}
      <div className="grid md:grid-cols-3 gap-6">
        {role === 'patient' && (
          <>
            <div className="glass-panel p-6 rounded-2xl space-y-3">
              <div className="w-10 h-10 rounded-xl bg-teal-500/10 flex items-center justify-center text-teal-400 text-lg font-bold">📋</div>
              <h3 className="font-bold text-slate-100 text-base">Care Checklists</h3>
              <p className="text-xs text-slate-400 leading-relaxed">Track routine medications, checkups, and post-natal compliance schedules.</p>
            </div>
            <div className="glass-panel p-6 rounded-2xl space-y-3">
              <div className="w-10 h-10 rounded-xl bg-teal-500/10 flex items-center justify-center text-teal-400 text-lg font-bold">📝</div>
              <h3 className="font-bold text-slate-100 text-base">Mood Diary</h3>
              <p className="text-xs text-slate-400 leading-relaxed">Express your thoughts confidentially in our secure mood logging notebook.</p>
            </div>
            <div className="glass-panel p-6 rounded-2xl space-y-3">
              <div className="w-10 h-10 rounded-xl bg-teal-500/10 flex items-center justify-center text-teal-400 text-lg font-bold">🧘‍♀️</div>
              <h3 className="font-bold text-slate-100 text-base">Stage Workouts</h3>
              <p className="text-xs text-slate-400 leading-relaxed">Stretching routines and pelvic floor stabilization tailored to your stage.</p>
            </div>
          </>
        )}
        
        {role === 'provider' && (
          <>
            <div className="glass-panel p-6 rounded-2xl space-y-3 col-span-3">
              <h3 className="font-bold text-slate-100 text-base">Specialist Clinical Portal</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                As a provider, you can review scheduled appointments in your Therapy Roster, confirm clinical session details, and track medication checklist adherence logs on our Compliance Sheets to ensure mothers are staying safe and active.
              </p>
            </div>
          </>
        )}
        
        {role === 'admin' && (
          <>
            <div className="glass-panel p-6 rounded-2xl space-y-3 col-span-3">
              <h3 className="font-bold text-slate-100 text-base">Administrator Command System</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                You have master authorization to monitor database statistics, publish articles, update directories, list user entries, and trigger patient relational history CSV compiles for audits.
              </p>
            </div>
          </>
        )}

        {(role === 'volunteer' || role === 'family') && (
          <>
            <div className="glass-panel p-6 rounded-2xl space-y-3 col-span-3">
              <h3 className="font-bold text-slate-100 text-base">Support & Resource Network</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Welcome to our community support hub. Explore the article database, browse peer helpline directories, and follow guided recovery stretches to help support new mothers on their recovery path.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default DashboardHome;
