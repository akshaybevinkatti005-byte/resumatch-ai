import { motion } from 'framer-motion';
import type { Job } from '../types';

interface Props {
  jobs: Job[];
}

export default function JobList({ jobs }: Props) {
  if (!jobs.length) {
    return (
      <div className="glass-card p-8 text-center text-slate-500">
        <p>No matched jobs yet. Results will appear after analysis.</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="glass-card p-6"
      id="job-matches"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-200">Top Job Matches</h3>
          <p className="text-xs text-slate-500 mt-0.5">Ranked by semantic similarity to your resume</p>
        </div>
        <span className="badge-blue">{jobs.length} matches</span>
      </div>

      <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
        {jobs.map((job, idx) => (
          <motion.a
            key={job.id}
            href={job.url || '#'}
            target="_blank"
            rel="noopener noreferrer"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 + idx * 0.06 }}
            className="block p-4 rounded-xl bg-navy-800/40 border border-white/[0.03] hover:border-electric-500/20 hover:bg-navy-700/40 transition-all duration-300 group"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <h4 className="font-semibold text-sm text-slate-200 group-hover:text-electric-400 transition-colors truncate">
                  {job.title}
                </h4>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-slate-400">{job.company}</span>
                  <span className="text-slate-600">•</span>
                  <span className="text-xs text-slate-500">{job.location}</span>
                </div>
              </div>

              {/* Match score */}
              {job.match_score !== undefined && (
                <div className="flex-shrink-0">
                  <div
                    className="text-sm font-bold px-2.5 py-1 rounded-lg"
                    style={{
                      color: job.match_score >= 75 ? '#10b981' :
                             job.match_score >= 60 ? '#f59e0b' : '#64748b',
                      backgroundColor: job.match_score >= 75 ? 'rgba(16,185,129,0.1)' :
                                       job.match_score >= 60 ? 'rgba(245,158,11,0.1)' : 'rgba(100,116,139,0.1)',
                    }}
                  >
                    {job.match_score}%
                  </div>
                </div>
              )}
            </div>

            {/* Tags */}
            {job.tags && job.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-2.5">
                {job.tags.slice(0, 5).map((tag) => (
                  <span key={tag} className="text-[10px] px-2 py-0.5 rounded-full bg-white/[0.04] text-slate-500">
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* Salary + Source */}
            <div className="flex items-center justify-between mt-2.5">
              <div className="text-xs text-slate-500">
                {job.salary_min && job.salary_max
                  ? `$${(job.salary_min / 1000).toFixed(0)}k – $${(job.salary_max / 1000).toFixed(0)}k`
                  : job.salary_min
                  ? `From $${(job.salary_min / 1000).toFixed(0)}k`
                  : ''}
              </div>
              <span className="text-[10px] text-slate-600">{job.source}</span>
            </div>
          </motion.a>
        ))}
      </div>
    </motion.div>
  );
}
