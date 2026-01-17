import { Box, Container, HStack, VStack, Text, Link } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

export function Footer() {
  return (
    <Box
      as="footer"
      bg="gray.50"
      borderTop="1px"
      borderColor="gray.200"
      py={8}
      mt={12}
    >
      <Container maxW="container.lg">
        <VStack spacing={4}>
          {/* リンク */}
          <HStack spacing={6} flexWrap="wrap" justify="center">
            <Link
              as={RouterLink}
              to="/terms"
              fontSize="sm"
              color="gray.600"
              _hover={{ color: 'blue.500', textDecoration: 'underline' }}
            >
              利用規約
            </Link>
            <Link
              as={RouterLink}
              to="/privacy"
              fontSize="sm"
              color="gray.600"
              _hover={{ color: 'blue.500', textDecoration: 'underline' }}
            >
              プライバシーポリシー
            </Link>
          </HStack>

          {/* 著作権表記 */}
          <VStack spacing={1}>
            <Text fontSize="sm" color="gray.600" textAlign="center">
              Fan-made site. All game assets © NetEase Inc.
            </Text>
            <Text fontSize="xs" color="gray.500" textAlign="center">
              このサイトは非公式のファンメイドサイトであり、NetEase Inc.とは一切関係ありません。
            </Text>
            <Text fontSize="xs" color="gray.500" textAlign="center">
              第五人格（Identity V）およびそのすべてのゲーム内アセットの著作権・商標権はNetEase Inc.に帰属します。
            </Text>
          </VStack>

          {/* サイト情報 */}
          <Text fontSize="xs" color="gray.400" textAlign="center">
            © 2026 Identity Archive. All rights reserved.
          </Text>
        </VStack>
      </Container>
    </Box>
  );
}
