import { useState, useEffect, useCallback } from 'react';
import type { AuthChangeEvent, Session } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase';
import { authApi } from '../services/api';
import type { User } from '../types';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // ユーザー情報を取得
  const fetchUser = useCallback(async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();

      if (!session) {
        setIsLoading(false);
        setIsAuthenticated(false);
        return;
      }

      // Supabaseのセッションからアクセストークンを取得
      const token = session.access_token;
      localStorage.setItem('access_token', token);

      // バックエンドからユーザー情報を取得
      const userData = await authApi.getMe();
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Fetch user error:', error);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();

    // Supabaseの認証状態変更を監視
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event: AuthChangeEvent, session: Session | null) => {
      if (session) {
        localStorage.setItem('access_token', session.access_token);
        fetchUser();
      } else {
        setUser(null);
        setIsAuthenticated(false);
        localStorage.removeItem('access_token');
      }
    });

    // トークンの有効期限を定期的にチェック（5分ごと）
    const tokenCheckInterval = setInterval(async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();

        if (!session) {
          // セッションが無効な場合はログアウト
          console.warn('セッションが無効です。ログアウトします。');
          setUser(null);
          setIsAuthenticated(false);
          localStorage.removeItem('access_token');
          return;
        }

        // トークンの有効期限をチェック（有効期限の1時間前にリフレッシュ）
        const expiresAt = session.expires_at;
        if (expiresAt) {
          const expiresInMs = expiresAt * 1000 - Date.now();
          const oneHourInMs = 60 * 60 * 1000;

          if (expiresInMs < oneHourInMs) {
            console.log('トークンをリフレッシュします');
            const { data: { session: newSession }, error } = await supabase.auth.refreshSession();

            if (error || !newSession) {
              console.error('トークンのリフレッシュに失敗しました', error);
              setUser(null);
              setIsAuthenticated(false);
              localStorage.removeItem('access_token');
            } else {
              localStorage.setItem('access_token', newSession.access_token);
              console.log('トークンをリフレッシュしました');
            }
          }
        }
      } catch (error) {
        console.error('トークンチェックエラー:', error);
      }
    }, 5 * 60 * 1000); // 5分ごと

    return () => {
      subscription.unsubscribe();
      clearInterval(tokenCheckInterval);
    };
  }, [fetchUser]);

  // ログイン開始（Supabase Client経由）
  const login = useCallback(async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      });

      if (error) throw error;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }, []);

  // ログアウト
  const logout = useCallback(async () => {
    try {
      await supabase.auth.signOut();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
      localStorage.removeItem('access_token');
    }
  }, []);

  return {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    refetch: fetchUser,
  };
}
