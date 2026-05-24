import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import type { User, RegistrationResponse } from '../types';
import api from '../api/client';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, name: string, password: string) => Promise<RegistrationResponse>;
  logout: () => Promise<void>;
  loading: boolean;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('rm_token'));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initializing, setInitializing] = useState(true);

  // Restore session on mount
  useEffect(() => {
    const saved = localStorage.getItem('rm_token');
    if (saved) {
      api.defaults.headers.common['Authorization'] = `Bearer ${saved}`;
      api.get('/auth/me')
        .then((res) => {
          setUser(res.data);
          setToken(saved);
        })
        .catch(() => {
          localStorage.removeItem('rm_token');
          setToken(null);
          delete api.defaults.headers.common['Authorization'];
        })
        .finally(() => setInitializing(false));
    } else {
      setInitializing(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.post('/auth/login', { email, password });
      const { token: newToken, user: userData } = res.data;
      localStorage.setItem('rm_token', newToken);
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      setToken(newToken);
      setUser(userData);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Login failed';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (email: string, name: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.post('/auth/register', { email, name, password });
      // Don't auto-login — user must verify email first
      return res.data;
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Registration failed';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.post('/auth/logout');
    } catch {}
    localStorage.removeItem('rm_token');
    delete api.defaults.headers.common['Authorization'];
    setToken(null);
    setUser(null);
  }, []);

  const clearError = useCallback(() => setError(null), []);

  if (initializing) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-electric-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isAdmin: user?.role === 'admin',
        login,
        register,
        logout,
        loading,
        error,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
