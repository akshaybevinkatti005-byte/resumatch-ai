import { motion } from 'framer-motion';
import type { ATSScore } from '../types';

interface Props {
  atsScore: ATSScore;
}

const categoryIcons: Record<string, string> = {
  parsing: '📄',
  keywords: '🔑',
  formatting: '🎨',
  structure: '🏗️',
};

const categoryLabels: Record<string, string> = {
  parsing: 'Parsing Accuracy',
  keywords: 'Keyword Coverage',
  formatting: 'Formatting',
  structure: 'Structure',
};

export default function ScoreBreakdown({ atsScore }: Props) {
  const { breakdown, recommendations } = atsScore;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.15 }}
      className="space-y-4"
      id="score-breakdown"
    >
      {/* Score cards grid */}
      <div className="grid grid-cols-2 gap-3">
        {Object.entries(breakdown).map(([key, data], idx) => (
          <motion.div
            key={key}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 + idx * 0.1 }}
            className="glass-card p-4"
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">{categoryIcons[key]}</span>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-300">{categoryLabels[key]}</p>
                <p className="text-[10px] text-slate-500">{data.weight}% weight</p>
              </div>
              <span
                className="text-lg font-bold"
                style={{
                  color: data.score >= 80 ? '#10b981' :
                         data.score >= 60 ? '#f59e0b' :
                         data.score >= 40 ? '#f97316' : '#f43f5e',
                }}
              >
                {data.score}
              </span>
            </div>

            {/* Progress bar */}
            <div className="h-1.5 bg-navy-700 rounded-full overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{
                  backgroundColor: data.score >= 80 ? '#10b981' :
                                   data.score >= 60 ? '#f59e0b' :
                                   data.score >= 40 ? '#f97316' : '#f43f5e',
                }}
                initial={{ width: 0 }}
                animate={{ width: `${data.score}%` }}
                transition={{ duration: 1, delay: 0.5 + idx * 0.15, ease: 'easeOut' }}
              />
            </div>

            {/* Details */}
            <ul className="mt-2.5 space-y-1">
              {data.details.map((detail, i) => (
                <li key={i} className="text-[10px] text-slate-500 leading-relaxed">
                  {detail}
                </li>
              ))}
            </ul>
          </motion.div>
        ))}
      </div>

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="glass-card p-5"
        >
          <h4 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
            <span>💡</span> Recommendations
          </h4>
          <ul className="space-y-2">
            {recommendations.map((rec, i) => (
              <motion.li
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.9 + i * 0.08 }}
                className="flex items-start gap-2.5 text-xs text-slate-400"
              >
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-electric-500/10 text-electric-400 flex items-center justify-center text-[10px] font-bold mt-0.5">
                  {i + 1}
                </span>
                <span className="leading-relaxed">{rec}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>
      )}
    </motion.div>
  );
}
