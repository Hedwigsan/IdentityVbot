import { createContext, useContext, useState, useEffect, useCallback, useRef, type ReactNode } from 'react';
import type { AuthChangeEvent, Session } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase';
import { authApi } from '../services/api';
import type { User } from '../types';

// タイムアウト付きPromise
function withTimeout<T>(promise: Promise<T>, ms: number, errorMessage: string): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(() => reject(new Error(errorMessage)), ms)
    ),
  ]);
}

// 認証チェックのタイムアウト（5秒）
const AUTH_TIMEOUT_MS = 5000;
// 強制ロード解除のタイムアウト（10秒）
const FORCE_LOADING_TIMEOUT_MS = 10000;

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  refetch: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const forceTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isFetchingRef = useRef(false);
  const authErrorCountRef = useRef(0);
  const hasInitializedRef = useRef(false);

  // 認証エラーの最大回数（これを超えたらセッションをクリア）
  const MAX_AUTH_ERRORS = 3;

  // 強制ロード解除タイマーをクリア
  const clearForceTimeout = useCallback(() => {
    if (forceTimeoutRef.current) {
      clearTimeout(forceTimeoutRef.current);
      forceTimeoutRef.current = null;
    }
  }, []);

  // セッションを完全にクリア
  const clearAllAuthData = useCallback(async () => {
    console.warn('認証データをクリアします');
    try {
      await supabase.auth.signOut();
    } catch {
      // エラーを無視
    }
    localStorage.removeItem('access_token');
    // Supabaseのローカルストレージキーをクリア
    const keysToRemove: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && (key.startsWith('sb-') || key.includes('supabase'))) {
        keysToRemove.push(key);
      }
    }
    keysToRemove.forEach(key => localStorage.removeItem(key));
    setUser(null);
    setIsAuthenticated(false);
    setIsLoading(false);
    authErrorCountRef.current = 0;
  }, []);

  // ユーザー情報を取得（タイムアウト付き、重複実行防止）
  const fetchUser = useCallback(async () => {
    // 既にフェッチ中の場合はスキップ
    if (isFetchingRef.current) {
      return;
    }
    isFetchingRef.current = true;

    try {
      // Supabaseセッション取得（タイムアウト付き）
      const { data: { session }, error: sessionError } = await withTimeout(
        supabase.auth.getSession(),
        AUTH_TIMEOUT_MS,
        'セッション取得がタイムアウトしました'
      );

      // セッション取得でエラーが発生した場合
      if (sessionError) {
        console.error('Session error:', sessionError);
        authErrorCountRef.current++;
        if (authErrorCountRef.current >= MAX_AUTH_ERRORS) {
          await clearAllAuthData();
          return;
        }
      }

      if (!session) {
        setIsLoading(false);
        setIsAuthenticated(false);
        setUser(null);
        clearForceTimeout();
        authErrorCountRef.current = 0;
        return;
      }

      // Supabaseのセッションからアクセストークンを取得
      const token = session.access_token;
      localStorage.setItem('access_token', token);

      // バックエンドからユーザー情報を取得（タイムアウト付き）
      const userData = await withTimeout(
        authApi.getMe(),
        AUTH_TIMEOUT_MS,
        'ユーザー情報取得がタイムアウトしました'
      );
      setUser(userData);
      setIsAuthenticated(true);
      authErrorCountRef.current = 0; // 成功したらリセット
    } catch (error) {
      console.error('Fetch user error:', error);
      authErrorCountRef.current++;

      // エラーが連続で発生した場合はセッションをクリア
      if (authErrorCountRef.current >= MAX_AUTH_ERRORS) {
        console.warn(`認証エラーが${MAX_AUTH_ERRORS}回連続で発生しました。セッションをクリアします。`);
        await clearAllAuthData();
        return;
      }

      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setIsLoading(false);
      clearForceTimeout();
      isFetchingRef.current = false;
    }
  }, [clearForceTimeout, clearAllAuthData]);

  useEffect(() => {
    // 既に初期化済みの場合はスキップ（StrictModeでの二重実行対策）
    if (hasInitializedRef.current) {
      return;
    }
    hasInitializedRef.current = true;

    // 強制タイムアウト: 10秒経過してもisLoadingがtrueの場合は強制解除＆セッションクリア
    forceTimeoutRef.current = setTimeout(async () => {
      console.warn('認証チェックが10秒以上かかっています。セッションをクリアします。');
      await clearAllAuthData();
      isFetchingRef.current = false;
    }, FORCE_LOADING_TIMEOUT_MS);

    fetchUser();

    // Supabaseの認証状態変更を監視
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event: AuthChangeEvent, session: Session | null) => {
        // SIGNED_OUTイベントでは何もしない（すでにクリア済み）
        if (event === 'SIGNED_OUT') {
          setUser(null);
          setIsAuthenticated(false);
          localStorage.removeItem('access_token');
          return;
        }

        if (session) {
          localStorage.setItem('access_token', session.access_token);
          // 少し遅延させて状態が安定してからfetchUser
          setTimeout(() => fetchUser(), 100);
        } else {
          setUser(null);
          setIsAuthenticated(false);
          localStorage.removeItem('access_token');
        }
      }
    );

    // トークンの有効期限を定期的にチェック（5分ごと）
    const tokenCheckInterval = setInterval(async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();

        if (!session) {
          console.warn('セッションが無効です。ログアウトします。');
          setUser(null);
          setIsAuthenticated(false);
          localStorage.removeItem('access_token');
          return;
        }

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
    }, 5 * 60 * 1000);

    return () => {
      subscription.unsubscribe();
      clearInterval(tokenCheckInterval);
      clearForceTimeout();
    };
  }, [fetchUser, clearForceTimeout, clearAllAuthData]);

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

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    refetch: fetchUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
