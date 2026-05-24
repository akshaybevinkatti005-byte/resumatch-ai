import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface Props {
  score: number;
  grade: string;
  size?: number;
}

export default function ATSGauge({ score, grade, size = 220 }: Props) {
  const [animatedScore, setAnimatedScore] = useState(0);

  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const center = size / 2;

  // Animate score count-up
  useEffect(() => {
    let start = 0;
    const duration = 1800;
    const startTime = performance.now();

    const tick = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(eased * score);
      setAnimatedScore(current);
      if (progress < 1) requestAnimationFrame(tick);
    };

    requestAnimationFrame(tick);
  }, [score]);

  const dashOffset = circumference - (animatedScore / 100) * circumference;

  // Color based on score
  const getColor = (s: number) => {
    if (s >= 80) return { main: '#10b981', glow: 'rgba(16,185,129,0.3)' };
    if (s >= 60) return { main: '#f59e0b', glow: 'rgba(245,158,11,0.3)' };
    if (s >= 40) return { main: '#f97316', glow: 'rgba(249,115,22,0.3)' };
    return { main: '#f43f5e', glow: 'rgba(244,63,94,0.3)' };
  };

  const color = getColor(animatedScore);

  const gradeLabel = (g: string) => {
    switch (g) {
      case 'A': return 'Excellent';
      case 'B': return 'Good';
      case 'C': return 'Fair';
      case 'D': return 'Needs Work';
      case 'F': return 'Poor';
      default: return '';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="flex flex-col items-center"
      id="ats-gauge"
    >
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background track */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            stroke="rgba(255,255,255,0.05)"
            strokeWidth={strokeWidth}
            fill="none"
          />

          {/* Score arc */}
          <motion.circle
            cx={center}
            cy={center}
            r={radius}
            stroke={color.main}
            strokeWidth={strokeWidth}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            style={{
              filter: `drop-shadow(0 0 8px ${color.glow})`,
              transition: 'stroke-dashoffset 0.1s ease-out, stroke 0.3s ease',
            }}
          />

          {/* Decorative ticks */}
          {Array.from({ length: 40 }).map((_, i) => {
            const angle = (i / 40) * 360;
            const rad = (angle * Math.PI) / 180;
            const isMajor = i % 10 === 0;
            const innerR = radius - (isMajor ? 18 : 12);
            const outerR = radius - 8;
            return (
              <line
                key={i}
                x1={center + innerR * Math.cos(rad)}
                y1={center + innerR * Math.sin(rad)}
                x2={center + outerR * Math.cos(rad)}
                y2={center + outerR * Math.sin(rad)}
                stroke="rgba(255,255,255,0.08)"
                strokeWidth={isMajor ? 1.5 : 0.5}
              />
            );
          })}
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="text-5xl font-black tabular-nums"
            style={{ color: color.main }}
          >
            {animatedScore}
          </span>
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest mt-1">
            Ghost Score
          </span>
        </div>
      </div>

      {/* Grade badge */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.2 }}
        className="mt-4 flex items-center gap-2"
      >
        <span
          className="text-2xl font-black px-3 py-1 rounded-lg"
          style={{
            color: color.main,
            backgroundColor: `${color.main}15`,
            border: `1px solid ${color.main}30`,
          }}
        >
          {grade}
        </span>
        <span className="text-sm text-slate-400">{gradeLabel(grade)}</span>
      </motion.div>
    </motion.div>
  );
}
