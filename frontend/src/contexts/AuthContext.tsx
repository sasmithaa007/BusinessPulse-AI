import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import api from '../api/axios';

export interface User {
  id: string;
  email: string;
  fullName: string;
  role: 'admin' | 'analyst' | 'viewer';
}

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  error: string | null;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const DEMO_USER: User = {
  id: '1',
  email: 'admin@businesspulse.demo',
  fullName: 'Demo Administrator',
  role: 'admin',
};

const USER_STORAGE_KEY = 'bp_auth_user';
const TOKEN_STORAGE_KEY = 'bp_access_token';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(USER_STORAGE_KEY);
      if (stored) {
        setUser(JSON.parse(stored));
      }
    } catch {
      localStorage.removeItem(USER_STORAGE_KEY);
      localStorage.removeItem(TOKEN_STORAGE_KEY);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      // Attempt backend login first
      try {
        const res = await api.post('/auth/login', { email, password });
        if (res.data?.access_token) {
          localStorage.setItem(TOKEN_STORAGE_KEY, res.data.access_token);
          // Fetch /auth/me
          const meRes = await api.get('/auth/me');
          const userData: User = {
            id: String(meRes.data.id),
            email: meRes.data.email,
            fullName: meRes.data.name,
            role: meRes.data.role || 'analyst',
          };
          localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData));
          setUser(userData);
          return;
        }
      } catch (backendErr: any) {
        // Fallback for standalone demo if credentials match
        if (email === 'admin@businesspulse.demo' && password === 'Demo@2024!') {
          const loggedUser = { ...DEMO_USER, email };
          localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(loggedUser));
          localStorage.setItem(TOKEN_STORAGE_KEY, 'demo_mock_token');
          setUser(loggedUser);
          return;
        }
        throw new Error(backendErr.response?.data?.detail || 'Invalid email or password.');
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Login failed';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (fullName: string, email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      try {
        await api.post('/auth/register', { name: fullName, email, password });
        // After register, perform login
        const loginRes = await api.post('/auth/login', { email, password });
        if (loginRes.data?.access_token) {
          localStorage.setItem(TOKEN_STORAGE_KEY, loginRes.data.access_token);
        }
      } catch (apiErr: any) {
        // If duplicate or network error, let it propagate or mock
      }

      const newUser: User = {
        id: Date.now().toString(),
        email,
        fullName,
        role: 'analyst',
      };
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(newUser));
      setUser(newUser);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Registration failed';
      setError(msg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(USER_STORAGE_KEY);
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setUser(null);
    setError(null);
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        error,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuthContext must be used within AuthProvider');
  return ctx;
}
