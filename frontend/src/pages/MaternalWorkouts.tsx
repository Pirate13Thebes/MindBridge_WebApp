import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import type { Exercise } from '../types';

const MaternalWorkouts: React.FC = () => {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [selectedStage, setSelectedStage] = useState<string>('trimester_1');
  const [loading, setLoading] = useState(false);

  const fetchExercises = async (stage: string) => {
    setLoading(true);
    try {
      const response = await apiClient.get<Exercise[]>('/exercise', {
        params: stage ? { stage } : {}
      });
      setExercises(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExercises(selectedStage);
  }, [selectedStage]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-wide text-slate-100">Stage Recovery Exercises</h2>
        <p className="text-xs text-slate-400">Yoga stretching routines and pelvic floor reconditioning exercises tailored to your stage.</p>
      </div>

      {/* Maternal Stage Selector Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-2 bg-slate-900 p-1.5 rounded-2xl border border-slate-800/80">
        {[
          { id: 'trimester_1', label: 'Trimester 1', sub: 'Weeks 1-12' },
          { id: 'trimester_2', label: 'Trimester 2', sub: 'Weeks 13-26' },
          { id: 'trimester_3', label: 'Trimester 3', sub: 'Weeks 27-40' },
          { id: 'postpartum_early', label: 'Early Recovery', sub: '0-6 Weeks Post' },
          { id: 'postpartum_late', label: 'Late Strength', sub: '6+ Weeks Post' }
        ].map((stage) => {
          const isSelected = selectedStage === stage.id;
          return (
            <button
              key={stage.id}
              onClick={() => setSelectedStage(stage.id)}
              className={`py-2 px-3 rounded-xl text-center transition-all ${
                isSelected
                  ? 'bg-teal-500 text-slate-950 shadow shadow-teal-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
              }`}
            >
              <div className="text-xs font-bold">{stage.label}</div>
              <div className={`text-[9px] ${isSelected ? 'text-slate-850 font-medium' : 'text-slate-500'}`}>{stage.sub}</div>
            </button>
          );
        })}
      </div>

      {loading ? (
        <div className="text-center py-10 text-slate-500 text-sm">Querying customized routines from MongoDB...</div>
      ) : exercises.length === 0 ? (
        <div className="glass-panel text-center py-12 rounded-2xl border border-slate-800">
          <span className="text-3xl block mb-2">🧘‍♀️</span>
          <p className="text-sm font-medium text-slate-300">No workout guidelines uploaded yet</p>
          <p className="text-xs text-slate-500 mt-1">We are compiling specialized stretch routines for this stage.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          {exercises.map((ex) => (
            <div key={ex._id} className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition-all space-y-4">
              <div className="space-y-3">
                <div className="flex justify-between items-start">
                  <h3 className="font-bold text-slate-100 text-base">{ex.name}</h3>
                  <span className="text-[10px] text-teal-400 font-bold bg-teal-400/5 px-2.5 py-0.5 rounded-full border border-teal-500/10">
                    ⏱️ {ex.duration_min} Mins
                  </span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">{ex.description}</p>
              </div>

              <div className="bg-slate-950/40 p-2.5 rounded-xl border border-slate-800/20 text-[10px] text-slate-500 flex justify-between items-center font-semibold">
                <span>Database Index: MongoDB Store</span>
                <span className="truncate max-w-[150px]">{ex._id}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MaternalWorkouts;
