import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { RewriteSuggestions } from '../types';

interface Props {
  data: RewriteSuggestions;
}

export default function ResumeRewriter({ data }: Props) {
  const [showOriginal, setShowOriginal] = useState<Record<string, boolean>>({});

  const sections = Object.entries(data.rewritten_sections);
  const hasImprovements = data.improvements_count > 0;

  if (!hasImprovements && data.tips.length === 0) {
    return (
      <div className="glass-card p-8 text-center text-slate-500">
        <p>No rewrite suggestions available. Upload a resume first.</p>
      </div>
    );
  }

  const toggleOriginal = (key: string) => {
    setShowOriginal((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-5"
      id="resume-rewriter"
    >
      {/* Score boost header */}
      <div className="glass-card p-5">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-200">ATS Resume Rewriter</h3>
            <p className="text-xs text-slate-500 mt-0.5">One-click ATS-friendly optimization</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-center">
              <p className="text-2xl font-black text-neon-400">+{data.score_boost_estimate}</p>
              <p className="text-[10px] text-slate-500">Score Boost</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-black text-electric-400">{data.improvements_count}</p>
              <p className="text-[10px] text-slate-500">Improvements</p>
            </div>
          </div>
        </div>

        {/* Keywords inserted */}
        {data.keyword_insertions.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-1.5">
            <span className="text-[10px] text-slate-500 uppercase tracking-wider mr-1 self-center">Keywords Added:</span>
            {data.keyword_insertions.map((ki, i) => (
              <span key={i} className="badge-green text-[10px]">{ki.keyword}</span>
            ))}
          </div>
        )}
      </div>

      {/* Summary suggestion */}
      {data.summary_suggestion && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="glass-card p-5"
        >
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg">✍️</span>
            <h4 className="text-sm font-bold text-slate-200">Suggested Professional Summary</h4>
            <span className="badge-blue text-[10px]">Missing</span>
          </div>
          <p className="text-sm text-slate-300 leading-relaxed bg-neon-500/5 border border-neon-500/10 rounded-lg p-3">
            {data.summary_suggestion}
          </p>
        </motion.div>
      )}

      {/* Rewritten sections */}
      {sections.map(([sectionName, bullets], sIdx) => (
        <motion.div
          key={sectionName}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 + sIdx * 0.1 }}
          className="glass-card p-5"
        >
          <h4 className="text-sm font-bold text-slate-200 capitalize mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-electric-500" />
            {sectionName}
            <span className="text-[10px] text-slate-500 font-normal">
              ({bullets.filter((b) => b.improved).length} improved)
            </span>
          </h4>

          <div className="space-y-3">
            {bullets.map((bullet, bIdx) => {
              const key = `${sectionName}-${bIdx}`;
              const isExpanded = showOriginal[key];

              return (
                <div
                  key={bIdx}
                  className={`p-3 rounded-lg border transition-all ${
                    bullet.improved
                      ? 'bg-neon-500/5 border-neon-500/10'
                      : 'bg-navy-800/30 border-white/[0.03]'
                  }`}
                >
                  {/* Rewritten text */}
                  <p className="text-sm text-slate-200 leading-relaxed">
                    {bullet.rewritten}
                  </p>

                  {/* Changes list */}
                  {bullet.changes.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {bullet.changes.map((c, ci) => (
                        <span key={ci} className="text-[10px] px-2 py-0.5 rounded-full bg-electric-500/10 text-electric-400 border border-electric-500/15">
                          {c}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Toggle original */}
                  {bullet.improved && (
                    <button
                      onClick={() => toggleOriginal(key)}
                      className="mt-2 text-[10px] text-slate-500 hover:text-slate-400 transition-colors"
                    >
                      {isExpanded ? 'Hide original' : 'Show original'}
                    </button>
                  )}

                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden"
                      >
                        <p className="mt-2 text-xs text-slate-500 line-through leading-relaxed p-2 rounded bg-navy-900/50">
                          {bullet.original}
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        </motion.div>
      ))}

      {/* Tips */}
      {data.tips.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-5"
        >
          <h4 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
            <span>💡</span> Pro Tips
          </h4>
          <ul className="space-y-2">
            {data.tips.map((tip, i) => (
              <li key={i} className="flex items-start gap-2.5 text-xs text-slate-400">
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-amber-500/10 text-amber-400 flex items-center justify-center text-[10px] font-bold mt-0.5">
                  {i + 1}
                </span>
                <span className="leading-relaxed">{tip}</span>
              </li>
            ))}
          </ul>
        </motion.div>
      )}
    </motion.div>
  );
}
