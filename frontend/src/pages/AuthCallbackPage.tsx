import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Center, Spinner, Text, VStack } from '@chakra-ui/react';
import { supabase } from '../lib/supabase';

export function AuthCallbackPage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // SupabaseがURLのハッシュフラグメントからセッションを自動的に処理
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();

        if (sessionError) {
          throw sessionError;
        }

        if (session) {
          // セッションが確立されたら、メインページにリダイレクト
          navigate('/record', { replace: true });
        } else {
          setError('認証セッションが見つかりません');
        }
      } catch (err) {
        console.error('Auth callback error:', err);
        setError('認証に失敗しました');
      }
    };

    handleCallback();
  }, [navigate]);

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
