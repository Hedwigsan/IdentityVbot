import { useState, useEffect, useCallback } from 'react';
import { authApi } from '../services/api';
import type { User } from '../types';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // ユーザー情報を取得
  const fetchUser = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setIsLoading(false);
      setIsAuthenticated(false);
      return;
    }

    try {
      const userData = await authApi.getMe();
      setUser(userData);
      setIsAuthenticated(true);
    } catch {
      // トークンが無効な場合
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  // ログイン開始
  const login = useCallback(async () => {
    try {
      const callbackUrl = `${window.location.origin}/auth/callback`;
      const { url } = await authApi.login(callbackUrl);
      window.location.href = url;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }, []);

  // ログアウト
  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // エラーでも続行
    } finally {
      setUser(null);
      setIsAuthenticated(false);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }, []);

  // OAuthコールバック処理
  const handleCallback = useCallback(async (code: string) => {
    try {
      const tokens = await authApi.exchangeToken(code);
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);
      await fetchUser();
      return true;
    } catch (error) {
      console.error('Callback error:', error);
      return false;
    }
  }, [fetchUser]);

  return {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    handleCallback,
    refetch: fetchUser,
  };
}
