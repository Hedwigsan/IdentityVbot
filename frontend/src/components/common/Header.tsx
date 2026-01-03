import {
  Box,
  Flex,
  HStack,
  Button,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Avatar,
  Text,
  useColorModeValue,
} from '@chakra-ui/react';
import { Link, useNavigate } from 'react-router-dom';
import { FiChevronDown } from 'react-icons/fi';
import type { User } from '../../types';

interface HeaderProps {
  user: User | null;
  isAuthenticated: boolean;
  onLogin: () => void;
  onLogout: () => void;
}

export function Header({ user, isAuthenticated, onLogin, onLogout }: HeaderProps) {
  const navigate = useNavigate();
  const bg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box
      as="header"
      bg={bg}
      borderBottom="1px"
      borderColor={borderColor}
      px={4}
      py={3}
      position="sticky"
      top={0}
      zIndex={100}
    >
      <Flex maxW="1200px" mx="auto" align="center" justify="space-between">
        <HStack spacing={8}>
          <Text
            as={Link}
            to="/"
            fontSize="xl"
            fontWeight="bold"
            _hover={{ textDecoration: 'none' }}
          >
            Identity Archive
          </Text>

          {isAuthenticated && (
            <HStack spacing={4} display={{ base: 'none', md: 'flex' }}>
              <Button as={Link} to="/record" variant="ghost" size="sm">
                記録
              </Button>
              <Button as={Link} to="/stats" variant="ghost" size="sm">
                統計
              </Button>
              <Button as={Link} to="/history" variant="ghost" size="sm">
                履歴
              </Button>
            </HStack>
          )}
        </HStack>

        <HStack spacing={4}>
          {isAuthenticated && user ? (
            <Menu>
              <MenuButton
                as={Button}
                variant="ghost"
                rightIcon={<FiChevronDown />}
              >
                <HStack>
                  <Avatar size="sm" src={user.avatar_url} name={user.name} />
                  <Text display={{ base: 'none', md: 'block' }}>
                    {user.name || user.email}
                  </Text>
                </HStack>
              </MenuButton>
              <MenuList>
                <MenuItem onClick={() => navigate('/settings')}>設定</MenuItem>
                <MenuItem onClick={onLogout}>ログアウト</MenuItem>
              </MenuList>
            </Menu>
          ) : (
            <Button colorScheme="blue" onClick={onLogin}>
              Googleでログイン
            </Button>
          )}
        </HStack>
      </Flex>
    </Box>
  );
}
