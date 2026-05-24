import { motion } from 'framer-motion';
import type { CareerPath } from '../types';

interface Props {
  paths: CareerPath[];
}

export default function CareerTimeline({ paths }: Props) {
  if (!paths.length) {
    return (
      <div className="glass-card p-8 text-center text-slate-500">
        <p>Upload a resume to discover your career trajectory.</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="glass-card p-6"
      id="career-timeline"
    >
      <h3 className="text-lg font-bold text-slate-200 mb-1">Career Trajectory</h3>
      <p className="text-xs text-slate-500 mb-6">Potential next roles based on your skill profile</p>

      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-5 top-0 bottom-0 w-px bg-gradient-to-b from-electric-500/50 via-neon-500/30 to-transparent" />

        <div className="space-y-6">
          {paths.map((path, idx) => (
            <motion.div
              key={path.title}
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.4, delay: 0.5 + idx * 0.15 }}
              className="relative pl-12"
            >
              {/* Timeline dot */}
              <div className="absolute left-3 top-3 w-5 h-5 rounded-full border-2 border-electric-500/60 bg-navy-900 flex items-center justify-center">
                <motion.div
                  className="w-2 h-2 rounded-full"
                  style={{
                    backgroundColor: path.match_percentage >= 70 ? '#10b981' :
                                     path.match_percentage >= 40 ? '#f59e0b' : '#f43f5e',
                  }}
                  animate={{ scale: [1, 1.3, 1] }}
                  transition={{ duration: 2, repeat: Infinity, delay: idx * 0.3 }}
                />
              </div>

              {/* Card */}
              <div className="p-4 rounded-xl bg-navy-800/50 border border-white/[0.04] hover:border-electric-500/20 transition-all duration-300">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-slate-200 text-sm">{path.title}</h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      From: {path.from_role} • {path.timeline}
                    </p>
                  </div>
                  <div
                    className="flex-shrink-0 text-sm font-bold px-2 py-0.5 rounded-md"
                    style={{
                      color: path.match_percentage >= 70 ? '#10b981' :
                             path.match_percentage >= 40 ? '#f59e0b' : '#f43f5e',
                      backgroundColor: path.match_percentage >= 70 ? 'rgba(16,185,129,0.1)' :
                                       path.match_percentage >= 40 ? 'rgba(245,158,11,0.1)' : 'rgba(244,63,94,0.1)',
                    }}
                  >
                    {path.match_percentage}% match
                  </div>
                </div>

                {/* Skills you have */}
                {path.skills_have.length > 0 && (
                  <div className="mt-3">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1.5">Skills You Have</p>
                    <div className="flex flex-wrap gap-1.5">
                      {path.skills_have.map((s) => (
                        <span key={s} className="badge-green text-[10px]">{s}</span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Missing skills */}
                {path.skills_missing.length > 0 && (
                  <div className="mt-2.5">
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1.5">Skills to Acquire</p>
                    <div className="flex flex-wrap gap-1.5">
                      {path.skills_missing.map((s) => (
                        <span key={s} className="badge-rose text-[10px]">{s}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
