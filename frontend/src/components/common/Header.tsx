import { Box } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import type { User } from '../../types';
import CardNav from './CardNav';

interface HeaderProps {
  user: User | null;
  isAuthenticated: boolean;
  onLogin: () => void;
  onLogout: () => void;
}

export function Header({ user, isAuthenticated, onLogin, onLogout }: HeaderProps) {
  const navigate = useNavigate();

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  // 認証済みユーザー用のCardNavアイテム設定（PC・スマホ共通）
  const cardNavItems = isAuthenticated && user ? [
    {
      label: 'メニュー',
      bgColor: '#00384eff',
      textColor: '#fff',
      links: [
        { label: '記録', href: '/record', onClick: () => handleNavigation('/record') },
        { label: '統計', href: '/stats', onClick: () => handleNavigation('/stats') },
        { label: '履歴', href: '/history', onClick: () => handleNavigation('/history') },
      ]
    },
    {
      label: 'アカウント',
      bgColor: '#011249ff',
      textColor: '#fff',
      links: [
        { label: '設定', href: '/settings', onClick: () => handleNavigation('/settings') },
      ]
    },
    {
      label: 'その他',
      bgColor: '#3d3d3dff',
      textColor: '#fff',
      links: [
        { label: 'ヘルプ', href: '/help', onClick: () => handleNavigation('/help') },
        { label: 'ログアウト', href: '#', onClick: onLogout },
      ]
    }
  ] : [];

  return (
    <>
      {/* 認証済み時のCardNavヘッダー（PC・スマホ共通） */}
      {isAuthenticated && user && (
        <Box position="relative" height="80px">
          <CardNav
            logo="/logo.png"
            logoAlt="Identity Archive"
            items={cardNavItems}
            baseColor="#ffffff"
            menuColor="#000000"
          />
        </Box>
      )}

      {/* 未認証時のシンプルヘッダー（全デバイス共通） */}
      {!isAuthenticated && (
        <Box
          as="header"
          bg="white"
          borderBottom="1px"
          borderColor="gray.200"
          px={4}
          py={3}
          position="sticky"
          top={0}
          zIndex={100}
        >
          <Box maxW="1200px" mx="auto" display="flex" alignItems="center" justifyContent="space-between">
            <Box
              as="img"
              src="/logo.png"
              alt="Identity Archive"
              h="40px"
              cursor="pointer"
              onClick={() => navigate('/')}
            />
            <Box
              as="button"
              bg="blue.500"
              color="white"
              px={4}
              py={2}
              borderRadius="md"
              fontSize="sm"
              fontWeight="medium"
              cursor="pointer"
              _hover={{ bg: 'blue.600' }}
              onClick={onLogin}
            >
              ログイン
            </Box>
          </Box>
        </Box>
      )}
    </>
  );
}
