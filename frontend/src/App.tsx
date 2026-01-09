import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box, Spinner, Center } from '@chakra-ui/react';
import { Header } from './components/common/Header';
import { AnimatedBackground } from './components/common/AnimatedBackground';
import { useAuth } from './hooks/useAuth';
import { RecordPage } from './pages/RecordPage';
import { StatsPage } from './pages/StatsPage';
import { HistoryPage } from './pages/HistoryPage';
import { SettingsPage } from './pages/SettingsPage';
import { HelpPage } from './pages/HelpPage';
import { AuthCallbackPage } from './pages/AuthCallbackPage';
import { LoginPage } from './pages/LoginPage';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Center h="100vh">
        <Spinner size="xl" />
      </Center>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export default function App() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth();
  const location = useLocation();

  // ログイン画面とコールバック画面ではヘッダーを非表示
  const hideHeader = location.pathname === '/login' || location.pathname === '/auth/callback';

  if (isLoading) {
    return (
      <Center h="100vh">
        <Spinner size="xl" />
      </Center>
    );
  }

  return (
    <Box minH="100vh">
      <AnimatedBackground />
      {!hideHeader && (
        <Header
          user={user}
          isAuthenticated={isAuthenticated}
          onLogin={login}
          onLogout={logout}
        />
      )}

      <Box as="main" maxW="1200px" mx="auto" px={hideHeader ? 0 : 4} py={hideHeader ? 0 : 6}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<AuthCallbackPage />} />

          <Route
            path="/"
            element={
              <PrivateRoute>
                <Navigate to="/record" replace />
              </PrivateRoute>
            }
          />
          <Route
            path="/record"
            element={
              <PrivateRoute>
                <RecordPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/stats"
            element={
              <PrivateRoute>
                <StatsPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/history"
            element={
              <PrivateRoute>
                <HistoryPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <PrivateRoute>
                <SettingsPage />
              </PrivateRoute>
            }
          />
          <Route
            path="/help"
            element={
              <PrivateRoute>
                <HelpPage />
              </PrivateRoute>
            }
          />
        </Routes>
      </Box>
    </Box>
  );
}
