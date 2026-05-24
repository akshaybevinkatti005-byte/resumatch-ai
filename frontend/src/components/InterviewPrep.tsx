import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { InterviewQuestions } from '../types';

interface Props {
  data: InterviewQuestions;
}

type Tab = 'behavioral' | 'technical' | 'situational' | 'role_based';

const tabs: { key: Tab; label: string; icon: string }[] = [
  { key: 'behavioral', label: 'Behavioral', icon: '🧠' },
  { key: 'technical', label: 'Technical', icon: '⚙️' },
  { key: 'situational', label: 'Situational', icon: '🎯' },
  { key: 'role_based', label: 'Role-Based', icon: '👔' },
];

export default function InterviewPrep({ data }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>('behavioral');
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  const questions = data[activeTab] || [];

  if (data.total === 0) {
    return (
      <div className="glass-card p-8 text-center text-slate-500">
        <p>No interview questions available. Upload a resume first.</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-card p-6"
      id="interview-prep"
    >
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-lg font-bold text-slate-200">Interview Question Generator</h3>
          <p className="text-xs text-slate-500 mt-0.5">Personalized questions from YOUR resume</p>
        </div>
        <span className="badge-blue">{data.total} questions</span>
      </div>

      {/* Tabs */}
      <div className="flex gap-1.5 mt-4 mb-5 bg-navy-800/60 p-1 rounded-xl">
        {tabs.map((tab) => {
          const count = (data[tab.key] || []).length;
          return (
            <button
              key={tab.key}
              onClick={() => { setActiveTab(tab.key); setExpandedIdx(null); }}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium transition-all ${
                activeTab === tab.key
                  ? 'bg-electric-500/15 text-electric-400 border border-electric-500/20'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <span>{tab.icon}</span>
              <span className="hidden sm:inline">{tab.label}</span>
              <span className="text-[10px] opacity-60">({count})</span>
            </button>
          );
        })}
      </div>

      {/* Questions */}
      <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            transition={{ duration: 0.2 }}
            className="space-y-2.5"
          >
            {questions.map((q, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="group"
              >
                <button
                  onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
                  className="w-full text-left p-4 rounded-xl bg-navy-800/40 border border-white/[0.03] hover:border-electric-500/15 transition-all"
                >
                  <div className="flex items-start gap-3">
                    <span className="flex-shrink-0 w-7 h-7 rounded-lg bg-electric-500/10 text-electric-400 flex items-center justify-center text-xs font-bold mt-0.5">
                      {idx + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-200 leading-relaxed">{q.question}</p>

                      {/* Skill badge */}
                      {q.skill && (
                        <span className="inline-block mt-2 text-[10px] px-2 py-0.5 rounded-full bg-neon-500/10 text-neon-400 border border-neon-500/20">
                          {q.skill}
                        </span>
                      )}
                    </div>
                    <svg
                      className={`w-4 h-4 text-slate-600 transition-transform flex-shrink-0 mt-1 ${expandedIdx === idx ? 'rotate-180' : ''}`}
                      fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>

                  {/* Expanded content */}
                  <AnimatePresence>
                    {expandedIdx === idx && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-3 ml-10 overflow-hidden"
                      >
                        {q.tip && (
                          <div className="p-2.5 rounded-lg bg-electric-500/5 border border-electric-500/10">
                            <p className="text-[11px] text-slate-400">
                              <span className="text-electric-400 font-medium">Tip: </span>{q.tip}
                            </p>
                          </div>
                        )}
                        {q.context && (
                          <p className="text-[11px] text-slate-500 mt-1">{q.context}</p>
                        )}
                        {q.category && !q.tip && (
                          <p className="text-[11px] text-slate-500 capitalize">Category: {q.category}</p>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </button>
              </motion.div>
            ))}
          </motion.div>
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
