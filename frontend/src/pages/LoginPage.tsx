import { Box, Button, Center, Image, Text, VStack } from '@chakra-ui/react';
import { Navigate } from 'react-router-dom';
import { FcGoogle } from 'react-icons/fc';
import { useAuth } from '../contexts/AuthContext';

export function LoginPage() {
  const { isAuthenticated, login, isLoading } = useAuth();

  if (isAuthenticated) {
    return <Navigate to="/record" replace />;
  }

  return (
    <Center minH="100vh">
      <VStack spacing={12} textAlign="center">
        <Image
          src="/logo.png"
          alt="Identity Archive"
          maxW="1000px"
          w="90%"
        />
        <Text fontSize="2xl" color="gray.600" mt={-4}>
          第五人格ハンター戦績管理システム
        </Text>
        <Box pt={8}>
          <Button
            size="lg"
            leftIcon={<FcGoogle />}
            onClick={login}
            isLoading={isLoading}
            bg="rgba(255, 255, 255, 0.2)"
            border="2px"
            borderColor="white"
            _hover={{ bg: 'gray.50' }}
            px={8}
            py={7}
            fontSize="xl"
            boxShadow="lg"
          >
            Googleでログイン
          </Button>
        </Box>
      </VStack>
    </Center>
  );
}
