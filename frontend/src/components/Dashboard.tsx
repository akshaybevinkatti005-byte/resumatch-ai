import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import { useAnalysis } from '../hooks/useAnalysis';
import ResumeUpload from './ResumeUpload';
import AnalysisLoader from './AnalysisLoader';
import ATSGauge from './ATSGauge';
import ScoreBreakdown from './ScoreBreakdown';
import SkillHeatmap from './SkillHeatmap';
import CareerTimeline from './CareerTimeline';
import JobList from './JobList';
import InterviewPrep from './InterviewPrep';
import ResumeRewriter from './ResumeRewriter';

type ResultTab = 'analysis' | 'interview' | 'rewriter';

export default function Dashboard() {
  const { stage, result, error, analyze, reset } = useAnalysis();
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [resultTab, setResultTab] = useState<ResultTab>('analysis');

  const isLoading = !['idle', 'complete', 'error'].includes(stage);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-white/[0.04]">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-electric-500 to-neon-500 flex items-center justify-center text-white font-black text-lg">
              R
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">ResuMatch AI</h1>
              <p className="text-[10px] text-slate-500 tracking-wider uppercase">Resume Optimizer & Job Matcher</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* User info */}
            <div className="text-right hidden sm:block">
              <p className="text-xs text-slate-300">{user?.name}</p>
              <p className="text-[10px] text-slate-500">{user?.email}</p>
            </div>

            {stage === 'complete' && (
              <button
                onClick={() => { reset(); setResultTab('analysis'); }}
                className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 border border-white/[0.06] hover:border-electric-500/30 hover:text-slate-200 transition-all"
              >
                New Analysis
              </button>
            )}

            {isAdmin && (
              <button
                onClick={() => navigate('/admin')}
                className="px-3 py-1.5 rounded-lg text-xs font-medium text-amber-400 border border-amber-500/20 hover:bg-amber-500/10 transition-all"
              >
                Admin
              </button>
            )}

            <button
              onClick={logout}
              className="px-3 py-1.5 rounded-lg text-xs text-rose-400 border border-rose-500/20 hover:bg-rose-500/10 transition-all"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          {/* ────── IDLE: Upload Screen ────── */}
          {stage === 'idle' && (
            <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, y: -30 }} transition={{ duration: 0.4 }}>
              <div className="text-center mb-12 pt-8">
                <motion.h2 className="text-4xl md:text-5xl font-black gradient-text mb-4" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                  Decode Your Resume's<br />Hidden Potential
                </motion.h2>
                <motion.p className="text-slate-400 text-lg max-w-xl mx-auto" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                  AI-powered ATS scoring, skill DNA mapping, interview prep, resume rewriting, and real-time job matching.
                </motion.p>
                <motion.div className="flex flex-wrap justify-center gap-3 mt-6" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.35 }}>
                  {['ATS Ghost Score', 'Interview Q Generator', 'Resume Rewriter', 'Job Matcher', 'Career Paths'].map((f) => (
                    <span key={f} className="badge-blue text-xs">{f}</span>
                  ))}
                </motion.div>
              </div>
              <ResumeUpload onUpload={analyze} disabled={isLoading} />
            </motion.div>
          )}

          {/* ────── LOADING ────── */}
          {isLoading && (
            <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <AnalysisLoader currentStage={stage} />
            </motion.div>
          )}

          {/* ────── ERROR ────── */}
          {stage === 'error' && (
            <motion.div key="error" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-lg mx-auto text-center py-16">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-rose-500/10 flex items-center justify-center">
                <svg className="w-8 h-8 text-rose-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-slate-200 mb-2">Analysis Failed</h3>
              <p className="text-sm text-slate-400 mb-6">{error}</p>
              <button onClick={reset} className="btn-primary">Try Again</button>
            </motion.div>
          )}

          {/* ────── RESULTS ────── */}
          {stage === 'complete' && result && (
            <motion.div key="results" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }} className="space-y-6">
              {/* Summary bar */}
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-4 flex flex-wrap items-center justify-between gap-4">
                <div className="flex items-center gap-6 text-sm">
                  <div><span className="text-slate-500">Pages:</span> <span className="text-slate-300 font-medium">{result.resume.page_count}</span></div>
                  <div><span className="text-slate-500">Words:</span> <span className="text-slate-300 font-medium">{result.resume.word_count}</span></div>
                  <div><span className="text-slate-500">Skills:</span> <span className="text-slate-300 font-medium">{result.skills.skills.length}</span></div>
                  {result.skills.total_years && <div><span className="text-slate-500">Exp:</span> <span className="text-slate-300 font-medium">{result.skills.total_years}y</span></div>}
                </div>
                <div className="text-xs text-slate-500">Analyzed in {result.elapsed_seconds}s</div>
              </motion.div>

              {/* Result Tabs */}
              <div className="flex gap-2 bg-navy-800/40 p-1.5 rounded-xl w-fit">
                {[
                  { key: 'analysis' as ResultTab, label: 'Analysis', icon: '📊' },
                  { key: 'interview' as ResultTab, label: 'Interview Prep', icon: '🎯' },
                  { key: 'rewriter' as ResultTab, label: 'Resume Rewriter', icon: '✍️' },
                ].map((t) => (
                  <button
                    key={t.key}
                    onClick={() => setResultTab(t.key)}
                    className={`flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                      resultTab === t.key
                        ? 'bg-electric-500/15 text-electric-400 border border-electric-500/20'
                        : 'text-slate-500 hover:text-slate-300'
                    }`}
                  >
                    <span>{t.icon}</span> {t.label}
                  </button>
                ))}
              </div>

              {/* Tab content */}
              <AnimatePresence mode="wait">
                {resultTab === 'analysis' && (
                  <motion.div key="tab-analysis" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                      <div className="glass-card p-6 flex items-center justify-center">
                        <ATSGauge score={result.ats_score.total_score} grade={result.ats_score.grade} />
                      </div>
                      <div className="lg:col-span-2">
                        <ScoreBreakdown atsScore={result.ats_score} />
                      </div>
                    </div>
                    <SkillHeatmap skills={result.skills.skills} />
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <JobList jobs={result.matched_jobs} />
                      <CareerTimeline paths={result.career_paths} />
                    </div>
                  </motion.div>
                )}

                {resultTab === 'interview' && (
                  <motion.div key="tab-interview" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                    <InterviewPrep data={result.interview_questions} />
                  </motion.div>
                )}

                {resultTab === 'rewriter' && (
                  <motion.div key="tab-rewriter" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                    <ResumeRewriter data={result.rewrite_suggestions} />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <footer className="border-t border-white/[0.04] mt-16">
        <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between text-xs text-slate-600">
          <span>ResuMatch AI v2.0 &bull; Zero-Cost Resume Intelligence</span>
          <span>100% Local NLP &bull; No Data Leaves Your Device</span>
        </div>
      </footer>
    </div>
  );
}
