import { motion, useScroll, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useRef } from 'react';

const features = [
  {
    icon: '🎯',
    title: 'ATS Ghost Score',
    desc: 'See exactly how ATS bots read your resume. Get a real score across 4 dimensions — parsing, keywords, formatting, and structure.',
    color: '#3b82f6',
  },
  {
    icon: '🧬',
    title: 'Skill DNA Heatmap',
    desc: 'Visualize your entire skill profile in one treemap. Area = market demand, color = your proficiency level.',
    color: '#10b981',
  },
  {
    icon: '🎤',
    title: 'Interview Q Generator',
    desc: 'Get personalized behavioral, technical, and situational questions generated directly from YOUR resume content.',
    color: '#8b5cf6',
  },
  {
    icon: '✍️',
    title: 'One-Click Resume Rewriter',
    desc: 'Transform weak bullet points into ATS-optimized power statements. Action verbs, metrics, and keyword injection — automatically.',
    color: '#f59e0b',
  },
  {
    icon: '🌐',
    title: 'Live Job Matching',
    desc: 'Semantic matching against 150+ real job listings from RemoteOK, Jobicy, Arbeitnow, and Himalayas — updated every 30 minutes.',
    color: '#ec4899',
  },
  {
    icon: '🚀',
    title: 'Career Trajectory',
    desc: 'Discover your next role. AI maps your skills to ESCO career paths and shows exactly what to learn for each transition.',
    color: '#06b6d4',
  },
];

const steps = [
  { num: '01', title: 'Upload', desc: 'Drop your PDF resume — parsed instantly with PyMuPDF', icon: '📄' },
  { num: '02', title: 'Analyze', desc: 'Local NLP extracts skills, scores ATS, and matches jobs', icon: '⚡' },
  { num: '03', title: 'Optimize', desc: 'Get actionable rewrites, interview prep, and career paths', icon: '✨' },
];

const stats = [
  { value: '100%', label: 'Free Forever' },
  { value: '0', label: 'API Keys Needed' },
  { value: '150+', label: 'Job Sources' },
  { value: '<3s', label: 'Analysis Time' },
];

export default function LandingPage() {
  const navigate = useNavigate();
  const heroRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll();
  const heroOpacity = useTransform(scrollYProgress, [0, 0.15], [1, 0]);
  const heroScale = useTransform(scrollYProgress, [0, 0.15], [1, 0.95]);

  return (
    <div className="min-h-screen overflow-x-hidden">
      {/* ═══════════ NAV ═══════════ */}
      <motion.nav
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="fixed top-0 left-0 right-0 z-50 border-b border-white/[0.04] bg-navy-900/70 backdrop-blur-xl"
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-electric-500 to-neon-500 flex items-center justify-center text-white font-black text-base">
              R
            </div>
            <span className="text-lg font-bold gradient-text">ResuMatch AI</span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/login')}
              className="px-4 py-2 rounded-lg text-sm text-slate-400 hover:text-slate-200 transition-colors"
            >
              Sign In
            </button>
            <motion.button
              onClick={() => navigate('/login')}
              className="btn-primary text-sm px-5 py-2"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Get Started Free
            </motion.button>
          </div>
        </div>
      </motion.nav>

      {/* ═══════════ HERO ═══════════ */}
      <motion.section
        ref={heroRef}
        style={{ opacity: heroOpacity, scale: heroScale }}
        className="relative pt-32 pb-20 px-6 min-h-[90vh] flex flex-col items-center justify-center"
      >
        {/* Animated orbs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <motion.div
            className="absolute w-[600px] h-[600px] rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 65%)', top: '-15%', left: '-10%' }}
            animate={{ x: [0, 40, 0], y: [0, -30, 0], scale: [1, 1.1, 1] }}
            transition={{ duration: 18, repeat: Infinity, ease: 'easeInOut' }}
          />
          <motion.div
            className="absolute w-[500px] h-[500px] rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(16,185,129,0.1) 0%, transparent 65%)', bottom: '-10%', right: '-8%' }}
            animate={{ x: [0, -30, 0], y: [0, 40, 0], scale: [1, 1.15, 1] }}
            transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
          />
          <motion.div
            className="absolute w-[300px] h-[300px] rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 65%)', top: '40%', right: '20%' }}
            animate={{ x: [0, 20, 0], y: [0, -20, 0] }}
            transition={{ duration: 14, repeat: Infinity, ease: 'easeInOut' }}
          />
          {/* Grid overlay */}
          <div className="absolute inset-0 opacity-[0.03]" style={{
            backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
            backgroundSize: '60px 60px',
          }} />
        </div>

        <div className="relative max-w-4xl mx-auto text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-electric-500/10 border border-electric-500/20 mb-8"
          >
            <span className="w-2 h-2 rounded-full bg-neon-400 animate-pulse" />
            <span className="text-xs font-medium text-electric-400">100% Free &bull; Zero API Keys &bull; Privacy-First</span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.7 }}
            className="text-5xl md:text-7xl font-black leading-[1.1] mb-6"
          >
            <span className="text-slate-100">Your Resume,</span>
            <br />
            <span className="gradient-text">Decoded by AI</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
            className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            ATS scoring, skill DNA mapping, interview prep, resume rewriting, and live job matching —
            all powered by <span className="text-slate-300 font-medium">local NLP models</span> running on your machine.
          </motion.p>

          {/* CTA buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <motion.button
              onClick={() => navigate('/login')}
              className="btn-primary text-base px-8 py-4 text-lg font-bold shadow-lg shadow-electric-500/20"
              whileHover={{ scale: 1.05, boxShadow: '0 20px 40px rgba(59,130,246,0.3)' }}
              whileTap={{ scale: 0.95 }}
            >
              Analyze Your Resume Free →
            </motion.button>
            <span className="text-xs text-slate-600">No credit card • No sign-up required to try</span>
          </motion.div>

          {/* Floating preview mockup */}
          <motion.div
            initial={{ opacity: 0, y: 60 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.8 }}
            className="mt-16 relative"
          >
            <div className="glass-card p-6 max-w-3xl mx-auto border border-white/[0.06]">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-3 h-3 rounded-full bg-rose-500/60" />
                <div className="w-3 h-3 rounded-full bg-amber-500/60" />
                <div className="w-3 h-3 rounded-full bg-neon-500/60" />
                <span className="ml-2 text-[10px] text-slate-600 font-mono">ResuMatch AI Dashboard</span>
              </div>
              <div className="grid grid-cols-3 gap-4">
                {/* ATS Score mini */}
                <div className="bg-navy-800/60 rounded-xl p-4 text-center">
                  <p className="text-3xl font-black text-neon-400">87</p>
                  <p className="text-[10px] text-slate-500 mt-1">ATS Ghost Score</p>
                  <div className="h-1.5 bg-navy-700 rounded-full mt-2 overflow-hidden">
                    <motion.div className="h-full bg-neon-500 rounded-full" initial={{ width: 0 }} animate={{ width: '87%' }} transition={{ delay: 1.2, duration: 1.5 }} />
                  </div>
                </div>
                {/* Skills mini */}
                <div className="bg-navy-800/60 rounded-xl p-4 text-center">
                  <p className="text-3xl font-black text-electric-400">24</p>
                  <p className="text-[10px] text-slate-500 mt-1">Skills Detected</p>
                  <div className="flex justify-center gap-1 mt-2">
                    {['bg-neon-500', 'bg-electric-500', 'bg-amber-500', 'bg-neon-500', 'bg-electric-500'].map((c, i) => (
                      <motion.div key={i} className={`w-4 h-3 rounded-sm ${c} opacity-40`} initial={{ opacity: 0 }} animate={{ opacity: 0.4 }} transition={{ delay: 1.4 + i * 0.1 }} />
                    ))}
                  </div>
                </div>
                {/* Jobs mini */}
                <div className="bg-navy-800/60 rounded-xl p-4 text-center">
                  <p className="text-3xl font-black text-violet-400">12</p>
                  <p className="text-[10px] text-slate-500 mt-1">Job Matches</p>
                  <div className="space-y-1 mt-2">
                    {[85, 72, 68].map((w, i) => (
                      <motion.div key={i} className="h-1 bg-navy-700 rounded-full overflow-hidden">
                        <motion.div className="h-full bg-violet-500/50 rounded-full" initial={{ width: 0 }} animate={{ width: `${w}%` }} transition={{ delay: 1.6 + i * 0.15, duration: 0.8 }} />
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            {/* Glow under card */}
            <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 w-2/3 h-12 bg-electric-500/10 blur-3xl rounded-full" />
          </motion.div>
        </div>
      </motion.section>

      {/* ═══════════ STATS BAR ═══════════ */}
      <section className="py-12 border-y border-white/[0.04]">
        <div className="max-w-5xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((s, i) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="text-center"
            >
              <p className="text-3xl md:text-4xl font-black gradient-text">{s.value}</p>
              <p className="text-xs text-slate-500 mt-1">{s.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ═══════════ FEATURES ═══════════ */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-black text-slate-100 mb-4">
              Everything You Need to <span className="gradient-text">Land the Job</span>
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto">
              Six AI-powered tools working together to optimize every aspect of your job search.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
                className="glass-card p-6 group cursor-default"
              >
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-4"
                  style={{ backgroundColor: `${f.color}15` }}
                >
                  {f.icon}
                </div>
                <h3 className="text-base font-bold text-slate-200 mb-2 group-hover:text-white transition-colors">
                  {f.title}
                </h3>
                <p className="text-sm text-slate-500 leading-relaxed">
                  {f.desc}
                </p>
                {/* Bottom accent line */}
                <motion.div
                  className="h-0.5 rounded-full mt-4 origin-left"
                  style={{ backgroundColor: f.color }}
                  initial={{ scaleX: 0, opacity: 0.3 }}
                  whileHover={{ scaleX: 1, opacity: 0.6 }}
                  transition={{ duration: 0.3 }}
                />
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════ HOW IT WORKS ═══════════ */}
      <section className="py-24 px-6 border-t border-white/[0.04]">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-black text-slate-100 mb-4">
              Three Steps to a <span className="gradient-text">Better Resume</span>
            </h2>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((step, i) => (
              <motion.div
                key={step.num}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                className="relative text-center"
              >
                {/* Connector line */}
                {i < steps.length - 1 && (
                  <div className="hidden md:block absolute top-10 left-[60%] right-[-40%] h-px bg-gradient-to-r from-white/10 to-transparent" />
                )}
                <motion.div
                  className="w-20 h-20 mx-auto rounded-2xl bg-navy-800/60 border border-white/[0.06] flex items-center justify-center text-3xl mb-5"
                  whileHover={{ scale: 1.1, borderColor: 'rgba(59,130,246,0.3)' }}
                >
                  {step.icon}
                </motion.div>
                <span className="text-[10px] font-bold text-electric-500 uppercase tracking-widest">{step.num}</span>
                <h3 className="text-lg font-bold text-slate-200 mt-1 mb-2">{step.title}</h3>
                <p className="text-sm text-slate-500">{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════════ PRIVACY SECTION ═══════════ */}
      <section className="py-20 px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto glass-card p-10 text-center relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-electric-500/5 to-neon-500/5" />
          <div className="relative">
            <div className="text-4xl mb-4">🔒</div>
            <h3 className="text-2xl font-black text-slate-100 mb-3">Your Data Never Leaves Your Device</h3>
            <p className="text-slate-400 max-w-lg mx-auto leading-relaxed">
              ResuMatch AI runs entirely on local NLP models. No cloud APIs, no data collection, no tracking.
              Your resume stays on YOUR machine — always.
            </p>
            <div className="flex flex-wrap justify-center gap-3 mt-6">
              {['No Cloud APIs', 'No Data Storage', 'No Tracking', 'Open Source Ready'].map((t) => (
                <span key={t} className="text-xs px-3 py-1.5 rounded-full bg-neon-500/10 text-neon-400 border border-neon-500/20">
                  {t}
                </span>
              ))}
            </div>
          </div>
        </motion.div>
      </section>

      {/* ═══════════ FINAL CTA ═══════════ */}
      <section className="py-24 px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl md:text-5xl font-black text-slate-100 mb-4">
            Ready to <span className="gradient-text">Decode Your Resume?</span>
          </h2>
          <p className="text-slate-400 mb-8 max-w-md mx-auto">
            Join thousands of professionals optimizing their resumes with AI — completely free.
          </p>
          <motion.button
            onClick={() => navigate('/login')}
            className="btn-primary text-lg px-10 py-4 font-bold shadow-xl shadow-electric-500/20"
            whileHover={{ scale: 1.05, boxShadow: '0 25px 50px rgba(59,130,246,0.3)' }}
            whileTap={{ scale: 0.95 }}
          >
            Get Started Free →
          </motion.button>
        </motion.div>
      </section>

      {/* ═══════════ FOOTER ═══════════ */}
      <footer className="border-t border-white/[0.04] py-8 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-electric-500 to-neon-500 flex items-center justify-center text-white font-black text-xs">
              R
            </div>
            <span className="text-sm font-semibold text-slate-400">ResuMatch AI</span>
            <span className="text-xs text-slate-600">&bull; v2.0</span>
          </div>
          <div className="flex items-center gap-6 text-xs text-slate-600">
            <span>Built with FastAPI + React 18</span>
            <span>&bull;</span>
            <span>Local NLP • Zero Cost</span>
            <span>&bull;</span>
            <span>&copy; {new Date().getFullYear()}</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
