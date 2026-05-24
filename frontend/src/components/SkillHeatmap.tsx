import { motion } from 'framer-motion';
import { Treemap, ResponsiveContainer, Tooltip } from 'recharts';
import type { Skill } from '../types';

interface Props {
  skills: Skill[];
}

interface TreeNode {
  name: string;
  size: number;
  fill: string;
  category: string;
  proficiency: string;
  years: number | null;
  demand: number;
}

const proficiencyColor: Record<string, string> = {
  expert: '#10b981',
  advanced: '#34d399',
  intermediate: '#f59e0b',
  beginner: '#f43f5e',
  unknown: '#64748b',
};

function CustomTreemapContent(props: any) {
  const { x, y, width, height, name, fill, depth } = props;

  if (depth !== 1 || width < 30 || height < 24) return null;

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        rx={6}
        fill={fill}
        fillOpacity={0.25}
        stroke={fill}
        strokeWidth={1}
        strokeOpacity={0.5}
        className="transition-all duration-200"
      />
      {width > 50 && height > 30 && (
        <text
          x={x + width / 2}
          y={y + height / 2}
          textAnchor="middle"
          dominantBaseline="central"
          fill="#e2e8f0"
          fontSize={Math.min(13, Math.max(9, width / 8))}
          fontFamily="Inter, sans-serif"
          fontWeight={600}
        >
          {name.length > width / 8 ? name.slice(0, Math.floor(width / 8)) + '…' : name}
        </text>
      )}
    </g>
  );
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.[0]) return null;
  const data = payload[0].payload as TreeNode;

  return (
    <div className="glass-card p-3 text-sm min-w-[180px]">
      <p className="font-semibold text-slate-200">{data.name}</p>
      <div className="mt-2 space-y-1 text-xs text-slate-400">
        <div className="flex justify-between">
          <span>Category</span>
          <span className="text-slate-300 capitalize">{data.category}</span>
        </div>
        <div className="flex justify-between">
          <span>Proficiency</span>
          <span style={{ color: proficiencyColor[data.proficiency] }} className="capitalize font-medium">
            {data.proficiency}
          </span>
        </div>
        <div className="flex justify-between">
          <span>Market Demand</span>
          <span className="text-slate-300">{data.demand}%</span>
        </div>
        {data.years && (
          <div className="flex justify-between">
            <span>Experience</span>
            <span className="text-slate-300">{data.years} yrs</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default function SkillHeatmap({ skills }: Props) {
  if (!skills.length) {
    return (
      <div className="glass-card p-8 text-center text-slate-500">
        <p>No skills detected. Upload a resume to see your Skill DNA.</p>
      </div>
    );
  }

  const treeData: TreeNode[] = skills.map((s) => ({
    name: s.name,
    size: Math.max(s.demand || 40, 20),
    fill: proficiencyColor[s.proficiency] || proficiencyColor.unknown,
    category: s.category,
    proficiency: s.proficiency,
    years: s.years,
    demand: s.demand || 40,
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="glass-card p-6"
      id="skill-heatmap"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-200">Skill DNA Heatmap</h3>
          <p className="text-xs text-slate-500 mt-0.5">Area = Market Demand • Color = Your Proficiency</p>
        </div>
        <div className="flex gap-3">
          {Object.entries(proficiencyColor).filter(([k]) => k !== 'unknown').map(([label, color]) => (
            <div key={label} className="flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: color }} />
              <span className="text-[10px] text-slate-500 capitalize">{label}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <Treemap
            data={treeData}
            dataKey="size"
            aspectRatio={4 / 3}
            stroke="rgba(10,15,30,0.8)"
            content={<CustomTreemapContent />}
          >
            <Tooltip content={<CustomTooltip />} />
          </Treemap>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
