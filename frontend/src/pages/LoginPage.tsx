import { Box, Button, Center, Heading, Text, VStack } from '@chakra-ui/react';
import { Navigate } from 'react-router-dom';
import { FcGoogle } from 'react-icons/fc';
import { useAuth } from '../hooks/useAuth';

export function LoginPage() {
  const { isAuthenticated, login, isLoading } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/record" replace />;
  }

  return (
    <Center minH="80vh">
      <VStack spacing={8} textAlign="center">
        <Heading size="2xl">Identity Archive</Heading>
        <Text fontSize="lg" color="gray.600">
          第五人格ハンター戦績管理システム
        </Text>
        <Box pt={4}>
          <Button
            size="lg"
            leftIcon={<FcGoogle />}
            onClick={login}
            isLoading={isLoading}
            colorScheme="gray"
            variant="outline"
          >
            Googleでログイン
          </Button>
        </Box>
      </VStack>
    </Center>
  );
}
