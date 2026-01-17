import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box, Spinner, Center } from '@chakra-ui/react';
import { Header } from './components/common/Header';
import { Footer } from './components/common/Footer';
import { AnimatedBackground } from './components/common/AnimatedBackground';
import { useAuth } from './contexts/AuthContext';
import { RecordPage } from './pages/RecordPage';
import { StatsPage } from './pages/StatsPage';
import { HistoryPage } from './pages/HistoryPage';
import { SettingsPage } from './pages/SettingsPage';
import { HelpPage } from './pages/HelpPage';
import { AuthCallbackPage } from './pages/AuthCallbackPage';
import { LoginPage } from './pages/LoginPage';
import { TermsPage } from './pages/TermsPage';
import { PrivacyPage } from './pages/PrivacyPage';

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

  // ログイン画面とコールバック画面ではヘッダー・フッターを非表示
  const hideHeaderFooter = location.pathname === '/login' || location.pathname === '/auth/callback';

  if (isLoading) {
    return (
      <Center h="100vh">
        <Spinner size="xl" />
      </Center>
    );
  }

  return (
    <Box minH="100vh" display="flex" flexDirection="column">
      <AnimatedBackground />
      {!hideHeaderFooter && (
        <Header
          user={user}
          isAuthenticated={isAuthenticated}
          onLogin={login}
          onLogout={logout}
        />
      )}

      <Box as="main" px={hideHeaderFooter ? 0 : 4} py={hideHeaderFooter ? 0 : 6} flex="1" w="100%">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<AuthCallbackPage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />

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

      {!hideHeaderFooter && <Footer />}
    </Box>
  );
}
