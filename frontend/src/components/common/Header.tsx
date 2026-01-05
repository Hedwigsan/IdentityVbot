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
  Image,
  IconButton,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  VStack,
  useColorModeValue,
  useDisclosure,
} from '@chakra-ui/react';
import { Link, useNavigate } from 'react-router-dom';
import { FiChevronDown } from 'react-icons/fi';
import { HamburgerIcon } from '@chakra-ui/icons';
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
  const { isOpen, onOpen, onClose } = useDisclosure();

  const handleNavigation = (path: string) => {
    navigate(path);
    onClose();
  };

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
          <Box
            as={Link}
            to="/"
            _hover={{ opacity: 0.8 }}
            transition="opacity 0.2s"
          >
            <Image
              src="/logo.png"
              alt="Identity Archive"
              h="40px"
            />
          </Box>

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
            <>
              {/* デスクトップ用メニュー */}
              <Menu>
                <MenuButton
                  as={Button}
                  variant="ghost"
                  rightIcon={<FiChevronDown />}
                  display={{ base: 'none', md: 'flex' }}
                >
                  <HStack>
                    <Avatar size="sm" src={user.avatar_url} name={user.name} />
                    <Text>
                      {user.name || user.email}
                    </Text>
                  </HStack>
                </MenuButton>
                <MenuList>
                  <MenuItem onClick={() => navigate('/settings')}>設定</MenuItem>
                  <MenuItem onClick={onLogout}>ログアウト</MenuItem>
                </MenuList>
              </Menu>

              {/* スマホ用ハンバーガーメニュー */}
              <IconButton
                icon={<HamburgerIcon />}
                aria-label="メニューを開く"
                onClick={onOpen}
                variant="ghost"
                display={{ base: 'flex', md: 'none' }}
              />
            </>
          ) : (
            <Button colorScheme="blue" onClick={onLogin}>
              Googleでログイン
            </Button>
          )}
        </HStack>
      </Flex>

      {/* スマホ用Drawerメニュー */}
      <Drawer isOpen={isOpen} placement="right" onClose={onClose}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px">
            <HStack>
              <Avatar size="sm" src={user?.avatar_url} name={user?.name} />
              <Text fontSize="sm">{user?.name || user?.email}</Text>
            </HStack>
          </DrawerHeader>

          <DrawerBody>
            <VStack spacing={4} align="stretch" mt={4}>
              <Button
                onClick={() => handleNavigation('/record')}
                variant="ghost"
                justifyContent="flex-start"
                size="lg"
              >
                記録
              </Button>
              <Button
                onClick={() => handleNavigation('/stats')}
                variant="ghost"
                justifyContent="flex-start"
                size="lg"
              >
                統計
              </Button>
              <Button
                onClick={() => handleNavigation('/history')}
                variant="ghost"
                justifyContent="flex-start"
                size="lg"
              >
                履歴
              </Button>
              <Button
                onClick={() => handleNavigation('/settings')}
                variant="ghost"
                justifyContent="flex-start"
                size="lg"
              >
                設定
              </Button>
              <Button
                onClick={() => {
                  onLogout();
                  onClose();
                }}
                variant="ghost"
                justifyContent="flex-start"
                size="lg"
                colorScheme="red"
              >
                ログアウト
              </Button>
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </Box>
  );
}
