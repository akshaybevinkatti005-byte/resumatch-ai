import { motion, AnimatePresence } from 'framer-motion';
import type { AnalysisStage } from '../types';

const stages: { key: AnalysisStage; label: string; icon: string }[] = [
  { key: 'uploading', label: 'Uploading Resume...', icon: '📄' },
  { key: 'extracting', label: 'Extracting Resume Content...', icon: '🔍' },
  { key: 'analyzing_skills', label: 'Normalizing Skill Vectors...', icon: '🧬' },
  { key: 'scoring', label: 'Analyzing Structural Integrity...', icon: '📊' },
  { key: 'matching', label: 'Scanning 50+ Global Job Boards...', icon: '🌐' },
  { key: 'generating', label: 'Generating Career Intelligence...', icon: '✨' },
];

interface Props {
  currentStage: AnalysisStage;
}

export default function AnalysisLoader({ currentStage }: Props) {
  const currentIndex = stages.findIndex((s) => s.key === currentStage);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-lg mx-auto py-16"
    >
      {/* Central pulsing orb */}
      <div className="flex justify-center mb-10">
        <div className="relative">
          <motion.div
            className="w-24 h-24 rounded-full"
            style={{
              background: 'radial-gradient(circle, rgba(59,130,246,0.3) 0%, rgba(16,185,129,0.1) 60%, transparent 70%)',
            }}
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.6, 1, 0.6],
            }}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          />
          <motion.div
            className="absolute inset-3 rounded-full bg-gradient-to-br from-electric-500 to-neon-500"
            animate={{ rotate: 360 }}
            transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
            style={{ opacity: 0.8 }}
          />
          <div className="absolute inset-0 flex items-center justify-center text-3xl">
            <AnimatePresence mode="wait">
              <motion.span
                key={currentStage}
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.5 }}
                transition={{ duration: 0.3 }}
              >
                {stages[currentIndex]?.icon || '⚡'}
              </motion.span>
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Stage list */}
      <div className="space-y-3">
        {stages.map((stage, idx) => {
          const isActive = idx === currentIndex;
          const isCompleted = idx < currentIndex;
          const isPending = idx > currentIndex;

          return (
            <motion.div
              key={stage.key}
              initial={{ opacity: 0, x: -20 }}
              animate={{
                opacity: isPending ? 0.3 : 1,
                x: 0,
              }}
              transition={{ delay: idx * 0.1, duration: 0.4 }}
              className={`flex items-center gap-4 px-5 py-3 rounded-xl transition-all duration-500 ${
                isActive
                  ? 'bg-electric-500/10 border border-electric-500/20'
                  : isCompleted
                  ? 'bg-neon-500/5 border border-transparent'
                  : 'border border-transparent'
              }`}
            >
              {/* Status indicator */}
              <div className="flex-shrink-0 w-6 h-6 flex items-center justify-center">
                {isCompleted ? (
                  <motion.svg
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="w-5 h-5 text-neon-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2.5}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </motion.svg>
                ) : isActive ? (
                  <motion.div
                    className="w-3 h-3 rounded-full bg-electric-500"
                    animate={{ scale: [1, 1.3, 1], opacity: [1, 0.6, 1] }}
                    transition={{ duration: 1.2, repeat: Infinity }}
                  />
                ) : (
                  <div className="w-2 h-2 rounded-full bg-slate-600" />
                )}
              </div>

              {/* Label */}
              <span
                className={`text-sm font-medium ${
                  isActive ? 'text-electric-400' : isCompleted ? 'text-neon-400' : 'text-slate-500'
                }`}
              >
                {stage.label}
              </span>

              {/* Progress bar for active stage */}
              {isActive && (
                <div className="flex-1 ml-2">
                  <div className="h-1 bg-navy-700 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-electric-500 to-neon-500 rounded-full"
                      initial={{ width: '0%' }}
                      animate={{ width: '100%' }}
                      transition={{ duration: 2.5, ease: 'easeInOut' }}
                    />
                  </div>
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Subtitle */}
      <motion.p
        className="text-center text-sm text-slate-500 mt-8"
        animate={{ opacity: [0.4, 0.8, 0.4] }}
        transition={{ duration: 3, repeat: Infinity }}
      >
        Powered by local NLP models • No data leaves your device
      </motion.p>
    </motion.div>
  );
}
