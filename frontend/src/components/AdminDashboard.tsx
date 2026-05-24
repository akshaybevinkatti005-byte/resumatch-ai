import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from './AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import type { AdminUser, Session, AdminStats } from '../types';

type Tab = 'stats' | 'users' | 'sessions' | 'activity';

export default function AdminDashboard() {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState<Tab>('stats');
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activity, setActivity] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      if (tab === 'stats') {
        const res = await api.get('/admin/stats');
        setStats(res.data);
      } else if (tab === 'users') {
        const res = await api.get('/admin/users');
        setUsers(res.data.users);
      } else if (tab === 'sessions') {
        const res = await api.get('/admin/sessions?limit=50');
        setSessions(res.data.sessions);
      } else if (tab === 'activity') {
        const res = await api.get('/admin/activity?limit=100');
        setActivity(res.data.activity);
      }
    } catch (err) {
      console.error('Admin fetch error:', err);
    }
    setLoading(false);
  }, [tab]);

  useEffect(() => {
    if (!isAdmin) { navigate('/dashboard'); return; }
    fetchData();
  }, [tab, isAdmin, navigate, fetchData]);

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('Delete this user permanently?')) return;
    try {
      await api.delete(`/admin/users/${userId}`);
      setUsers((prev) => prev.filter((u) => u.id !== userId));
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to delete');
    }
  };

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      await api.put(`/admin/users/${userId}/role?role=${newRole}`);
      setUsers((prev) => prev.map((u) => u.id === userId ? { ...u, role: newRole } : u));
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to update role');
    }
  };

  const tabItems: { key: Tab; label: string; icon: string }[] = [
    { key: 'stats', label: 'Overview', icon: '📊' },
    { key: 'users', label: 'Users', icon: '👥' },
    { key: 'sessions', label: 'Sessions', icon: '🔑' },
    { key: 'activity', label: 'Activity Log', icon: '📋' },
  ];

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-white/[0.04]">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-rose-500 to-amber-500 flex items-center justify-center text-white font-black text-lg">
              A
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-200">Admin Dashboard</h1>
              <p className="text-[10px] text-slate-500">{user?.email}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={() => navigate('/dashboard')} className="px-3 py-1.5 rounded-lg text-xs text-slate-400 border border-white/[0.06] hover:border-electric-500/30 transition-all">
              Back to App
            </button>
            <button onClick={logout} className="px-3 py-1.5 rounded-lg text-xs text-rose-400 border border-rose-500/20 hover:bg-rose-500/10 transition-all">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6">
        {/* Tabs */}
        <div className="flex gap-2 mb-6 bg-navy-800/40 p-1.5 rounded-xl w-fit">
          {tabItems.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                tab === t.key
                  ? 'bg-electric-500/15 text-electric-400 border border-electric-500/20'
                  : 'text-slate-500 hover:text-slate-300'
              }`}
            >
              <span>{t.icon}</span>
              {t.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-8 h-8 border-2 border-electric-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <>
            {/* ──── Stats Tab ──── */}
            {tab === 'stats' && stats && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  {[
                    { label: 'Total Users', value: stats.total_users, color: '#3b82f6' },
                    { label: 'Active Today', value: stats.active_today, color: '#10b981' },
                    { label: 'Total Analyses', value: stats.total_analyses, color: '#8b5cf6' },
                    { label: 'Total Sessions', value: stats.total_sessions, color: '#f59e0b' },
                    { label: 'Avg ATS Score', value: stats.avg_ats_score, color: '#ec4899' },
                  ].map((stat, i) => (
                    <motion.div
                      key={stat.label}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.08 }}
                      className="glass-card p-5 text-center"
                    >
                      <p className="text-3xl font-black" style={{ color: stat.color }}>{stat.value}</p>
                      <p className="text-xs text-slate-500 mt-1">{stat.label}</p>
                    </motion.div>
                  ))}
                </div>

                {/* System info */}
                <div className="glass-card p-5">
                  <h4 className="text-sm font-bold text-slate-200 mb-3">System Resources</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-xs text-slate-500">Process Memory</p>
                      <p className="text-lg font-bold text-slate-300">{stats.system.process_memory_mb?.toFixed(0)} MB</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">System RAM</p>
                      <p className="text-lg font-bold text-slate-300">{stats.system.system_total_mb?.toFixed(0)} MB</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">Available</p>
                      <p className="text-lg font-bold text-neon-400">{stats.system.system_available_mb?.toFixed(0)} MB</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500">RAM Usage</p>
                      <p className="text-lg font-bold" style={{
                        color: (stats.system.system_percent_used || 0) > 85 ? '#f43f5e' : '#10b981'
                      }}>{stats.system.system_percent_used?.toFixed(1)}%</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* ──── Users Tab ──── */}
            {tab === 'users' && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card overflow-hidden">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/[0.05]">
                      <th className="text-left px-5 py-3 text-[11px] text-slate-500 uppercase tracking-wider font-medium">User</th>
                      <th className="text-left px-5 py-3 text-[11px] text-slate-500 uppercase tracking-wider font-medium">Role</th>
                      <th className="text-left px-5 py-3 text-[11px] text-slate-500 uppercase tracking-wider font-medium">Created</th>
                      <th className="text-left px-5 py-3 text-[11px] text-slate-500 uppercase tracking-wider font-medium">Last Login</th>
                      <th className="text-right px-5 py-3 text-[11px] text-slate-500 uppercase tracking-wider font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u, i) => (
                      <motion.tr
                        key={u.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: i * 0.03 }}
                        className="border-b border-white/[0.02] hover:bg-white/[0.02] transition-colors"
                      >
                        <td className="px-5 py-3">
                          <p className="text-sm font-medium text-slate-200">{u.name}</p>
                          <p className="text-[11px] text-slate-500">{u.email}</p>
                        </td>
                        <td className="px-5 py-3">
                          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                            u.role === 'admin'
                              ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                              : 'bg-electric-500/10 text-electric-400 border border-electric-500/20'
                          }`}>
                            {u.role}
                          </span>
                        </td>
                        <td className="px-5 py-3 text-xs text-slate-400">{u.created_at?.slice(0, 16)}</td>
                        <td className="px-5 py-3 text-xs text-slate-400">{u.last_login?.slice(0, 16) || 'Never'}</td>
                        <td className="px-5 py-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                            {u.role !== 'admin' && (
                              <>
                                <button
                                  onClick={() => handleRoleChange(u.id, u.role === 'user' ? 'admin' : 'user')}
                                  className="text-[10px] px-2 py-1 rounded bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 transition-colors"
                                >
                                  {u.role === 'user' ? 'Make Admin' : 'Demote'}
                                </button>
                                <button
                                  onClick={() => handleDeleteUser(u.id)}
                                  className="text-[10px] px-2 py-1 rounded bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 transition-colors"
                                >
                                  Delete
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
                {users.length === 0 && (
                  <p className="text-center py-8 text-sm text-slate-500">No users found</p>
                )}
              </motion.div>
            )}

            {/* ──── Sessions Tab ──── */}
            {tab === 'sessions' && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card overflow-hidden">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-white/[0.05]">
                      <th className="text-left px-5 py-3 text-[11px] text-slate-500 uppercase tracking-wider font-medium">User</th>
                      <th className="text-left px-5 py-3 text-[11px] text-slate-500 uppercase tracking-wider font-medium">Login At</th>
                      <th className="text-left px-5 py-3 text-[11px] text-slate-500 uppercase tracking-wider font-medium">Logout At</th>
                      <th className="text-left px-5 py-3 text-[11px] text-slate-500 uppercase tracking-wider font-medium">Status</th>
                      <th className="text-left px-5 py-3 text-[11px] text-slate-500 uppercase tracking-wider font-medium">IP</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sessions.map((s, i) => (
                      <motion.tr
                        key={s.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: i * 0.02 }}
                        className="border-b border-white/[0.02] hover:bg-white/[0.02] transition-colors"
                      >
                        <td className="px-5 py-3">
                          <p className="text-sm text-slate-200">{s.name}</p>
                          <p className="text-[10px] text-slate-500">{s.email}</p>
                        </td>
                        <td className="px-5 py-3 text-xs text-slate-400">{s.login_at?.slice(0, 19)}</td>
                        <td className="px-5 py-3 text-xs text-slate-400">{s.logout_at?.slice(0, 19) || '—'}</td>
                        <td className="px-5 py-3">
                          <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${
                            s.logout_at
                              ? 'bg-slate-500/10 text-slate-400'
                              : 'bg-neon-500/10 text-neon-400 border border-neon-500/20'
                          }`}>
                            {s.logout_at ? 'Ended' : 'Active'}
                          </span>
                        </td>
                        <td className="px-5 py-3 text-[11px] text-slate-500 font-mono">{s.ip_address || '—'}</td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
                {sessions.length === 0 && (
                  <p className="text-center py-8 text-sm text-slate-500">No sessions recorded</p>
                )}
              </motion.div>
            )}

            {/* ──── Activity Tab ──── */}
            {tab === 'activity' && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card p-5">
                <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
                  {activity.map((a, i) => (
                    <motion.div
                      key={a.id}
                      initial={{ opacity: 0, x: -5 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.02 }}
                      className="flex items-center gap-3 px-4 py-2.5 rounded-lg bg-navy-800/30 hover:bg-navy-800/50 transition-colors"
                    >
                      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${
                        a.action === 'login' ? 'bg-neon-400' :
                        a.action === 'logout' ? 'bg-slate-500' :
                        a.action === 'register' ? 'bg-electric-400' : 'bg-amber-400'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <span className="text-xs text-slate-300">{a.name || 'System'}</span>
                        <span className="text-xs text-slate-500 mx-2">&mdash;</span>
                        <span className="text-xs text-slate-400 capitalize">{a.action}</span>
                        {a.details && <span className="text-[10px] text-slate-600 ml-2">{a.details}</span>}
                      </div>
                      <span className="text-[10px] text-slate-600 flex-shrink-0">{a.timestamp?.slice(0, 19)}</span>
                    </motion.div>
                  ))}
                  {activity.length === 0 && (
                    <p className="text-center py-8 text-sm text-slate-500">No activity recorded</p>
                  )}
                </div>
              </motion.div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
