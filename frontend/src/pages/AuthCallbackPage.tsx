import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Center, Spinner, Text, VStack } from '@chakra-ui/react';
import { authApi } from '../services/api';

export function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');

      if (!code) {
        setError('認証コードが見つかりません');
        return;
      }

      try {
        const { access_token } = await authApi.exchangeToken(code);
        localStorage.setItem('access_token', access_token);
        navigate('/record', { replace: true });
      } catch (err) {
        console.error('Auth callback error:', err);
        setError('認証に失敗しました');
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  if (error) {
    return (
      <Center minH="80vh">
        <VStack spacing={4}>
          <Text color="red.500">{error}</Text>
          <Text
            as="a"
            href="/login"
            color="blue.500"
            textDecoration="underline"
          >
            ログインページへ戻る
          </Text>
        </VStack>
      </Center>
    );
  }

  return (
    <Center minH="80vh">
      <VStack spacing={4}>
        <Spinner size="xl" />
        <Text>認証中...</Text>
      </VStack>
    </Center>
  );
}
