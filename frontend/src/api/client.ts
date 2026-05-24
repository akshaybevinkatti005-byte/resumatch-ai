import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach auth token from localStorage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('rm_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses — let AuthContext handle actual redirects
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      // Only clear token for auth-specific endpoints, not all 401s
      const url = err.config?.url || '';
      if (url.includes('/auth/me')) {
        localStorage.removeItem('rm_token');
        delete api.defaults.headers.common['Authorization'];
      }
    }
    return Promise.reject(err);
  }
);

export default api;
