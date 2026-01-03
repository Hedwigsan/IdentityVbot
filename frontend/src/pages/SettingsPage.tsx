import {
  Box,
  Heading,
  VStack,
  Card,
  CardBody,
  HStack,
  Avatar,
  Text,
  Button,
} from '@chakra-ui/react';
import { useAuth } from '../hooks/useAuth';

export function SettingsPage() {
  const { user, logout } = useAuth();

  return (
    <Box>
      <Heading size="lg" mb={6}>
        設定
      </Heading>

      <VStack spacing={6} align="stretch" maxW="600px">
        <Card>
          <CardBody>
            <HStack spacing={4}>
              <Avatar
                size="lg"
                src={user?.avatar_url}
                name={user?.name}
              />
              <Box>
                <Text fontWeight="bold" fontSize="lg">
                  {user?.name || 'ユーザー'}
                </Text>
                <Text color="gray.500">{user?.email}</Text>
              </Box>
            </HStack>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Button colorScheme="red" variant="outline" onClick={logout}>
              ログアウト
            </Button>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  );
}
