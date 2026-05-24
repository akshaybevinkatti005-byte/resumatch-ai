import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from './AuthContext';

export default function LoginPage() {
  const { login, register, loading, error, clearError } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState('');
  const [verificationSent, setVerificationSent] = useState(false);
  const [verifiedSuccess, setVerifiedSuccess] = useState(false);
  const [verificationError, setVerificationError] = useState('');

  // Check URL query parameters for verification status
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);

    if (params.get('verified') === 'true') {
      setVerifiedSuccess(true);
      // Clean the URL without reload
      window.history.replaceState({}, '', window.location.pathname);
    }

    const verificationStatus = params.get('verification');
    if (verificationStatus === 'expired') {
      setVerificationError('This verification link has expired or was already used. Please register again.');
      window.history.replaceState({}, '', window.location.pathname);
    } else if (verificationStatus === 'failed') {
      setVerificationError('Email verification failed. Please try registering again.');
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');
    clearError();
    setVerificationSent(false);
    setVerifiedSuccess(false);
    setVerificationError('');

    if (!email || !password) {
      setLocalError('Email and password are required');
      return;
    }
    if (isRegister && !name.trim()) {
      setLocalError('Name is required');
      return;
    }
    if (password.length < 6) {
      setLocalError('Password must be at least 6 characters');
      return;
    }

    try {
      if (isRegister) {
        const result = await register(email, name, password);
        if (result?.requires_verification) {
          setVerificationSent(true);
        }
      } else {
        await login(email, password);
      }
    } catch {}
  };

  const displayError = localError || error;

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden">
      {/* Animated background orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute w-96 h-96 rounded-full opacity-10"
          style={{ background: 'radial-gradient(circle, #3b82f6 0%, transparent 70%)', top: '-10%', right: '-10%' }}
          animate={{ scale: [1, 1.2, 1], x: [0, 30, 0], y: [0, -20, 0] }}
          transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute w-80 h-80 rounded-full opacity-10"
          style={{ background: 'radial-gradient(circle, #10b981 0%, transparent 70%)', bottom: '-10%', left: '-5%' }}
          animate={{ scale: [1, 1.3, 1], x: [0, -20, 0], y: [0, 30, 0] }}
          transition={{ duration: 15, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 40, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className="w-full max-w-md relative"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-electric-500 to-neon-500 flex items-center justify-center text-white font-black text-2xl mb-4 shadow-lg shadow-electric-500/20">
            R
          </div>
          <h1 className="text-3xl font-black gradient-text">ResuMatch AI</h1>
          <p className="text-sm text-slate-400 mt-1">Resume Intelligence Platform</p>
        </div>

        {/* Verification Success Banner */}
        <AnimatePresence>
          {verifiedSuccess && (
            <motion.div
              initial={{ opacity: 0, y: -15, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.4, ease: 'easeOut' }}
              className="mb-6 p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 backdrop-blur-sm"
            >
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 rounded-lg bg-emerald-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-emerald-300 font-semibold text-sm">Email verified successfully!</p>
                  <p className="text-emerald-400/70 text-xs mt-1">Your account is now active. Sign in below to get started.</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Verification Sent Banner */}
        <AnimatePresence>
          {verificationSent && (
            <motion.div
              initial={{ opacity: 0, y: -15, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.4, ease: 'easeOut' }}
              className="mb-6 p-4 rounded-xl border border-blue-500/30 bg-blue-500/10 backdrop-blur-sm"
            >
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                  </svg>
                </div>
                <div>
                  <p className="text-blue-300 font-semibold text-sm">Check your email!</p>
                  <p className="text-blue-400/70 text-xs mt-1">
                    We've sent a verification link to <strong className="text-blue-300">{email}</strong>.
                    Click the link to activate your account, then sign in here.
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Verification Error Banner */}
        <AnimatePresence>
          {verificationError && (
            <motion.div
              initial={{ opacity: 0, y: -15, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.4, ease: 'easeOut' }}
              className="mb-6 p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 backdrop-blur-sm"
            >
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                  </svg>
                </div>
                <div>
                  <p className="text-amber-300 font-semibold text-sm">Verification Issue</p>
                  <p className="text-amber-400/70 text-xs mt-1">{verificationError}</p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Card */}
        <div className="glass-card p-8">
          {/* Toggle */}
          <div className="flex bg-navy-800/80 rounded-xl p-1 mb-6">
            <button
              onClick={() => { setIsRegister(false); clearError(); setLocalError(''); setVerificationSent(false); }}
              className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                !isRegister ? 'bg-electric-500/20 text-electric-400' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setIsRegister(true); clearError(); setLocalError(''); setVerifiedSuccess(false); }}
              className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                isRegister ? 'bg-electric-500/20 text-electric-400' : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              Create Account
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <AnimatePresence mode="wait">
              {isRegister && (
                <motion.div
                  key="name"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <label htmlFor="name-input" className="block text-xs font-medium text-slate-400 mb-1.5">Full Name</label>
                  <input
                    id="name-input"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="John Doe"
                    className="w-full px-4 py-3 rounded-xl bg-navy-800/80 border border-white/[0.06] text-slate-200 placeholder-slate-500 focus:outline-none focus:border-electric-500/50 focus:ring-1 focus:ring-electric-500/20 transition-all"
                  />
                </motion.div>
              )}
            </AnimatePresence>

            <div>
              <label htmlFor="email-input" className="block text-xs font-medium text-slate-400 mb-1.5">Email</label>
              <input
                id="email-input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full px-4 py-3 rounded-xl bg-navy-800/80 border border-white/[0.06] text-slate-200 placeholder-slate-500 focus:outline-none focus:border-electric-500/50 focus:ring-1 focus:ring-electric-500/20 transition-all"
              />
            </div>

            <div>
              <label htmlFor="password-input" className="block text-xs font-medium text-slate-400 mb-1.5">Password</label>
              <input
                id="password-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min 6 characters"
                className="w-full px-4 py-3 rounded-xl bg-navy-800/80 border border-white/[0.06] text-slate-200 placeholder-slate-500 focus:outline-none focus:border-electric-500/50 focus:ring-1 focus:ring-electric-500/20 transition-all"
              />
            </div>

            {/* Error */}
            <AnimatePresence>
              {displayError && (
                <motion.div
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm"
                >
                  {displayError}
                </motion.div>
              )}
            </AnimatePresence>

            <motion.button
              type="submit"
              disabled={loading}
              className={`w-full btn-primary text-base py-3.5 ${loading ? 'opacity-60 cursor-wait' : ''}`}
              whileHover={!loading ? { scale: 1.02 } : {}}
              whileTap={!loading ? { scale: 0.98 } : {}}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  {isRegister ? 'Creating Account...' : 'Signing In...'}
                </span>
              ) : isRegister ? 'Create Account' : 'Sign In'}
            </motion.button>
          </form>

          {/* Admin hint */}
          {!isRegister && (
            <p className="text-[10px] text-slate-600 text-center mt-4">
              Admin? Use admin@resumatch.ai
            </p>
          )}
        </div>

        {/* Privacy note */}
        <p className="text-center text-[11px] text-slate-600 mt-6">
          100% Local NLP &bull; No data leaves your device &bull; Zero API costs
        </p>
      </motion.div>
    </div>
  );
}
