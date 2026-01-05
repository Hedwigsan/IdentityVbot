import { Box } from '@chakra-ui/react';

export function AnimatedBackground() {
  return (
    <Box
      position="fixed"
      top={0}
      left={0}
      width="100vw"
      height="100vh"
      zIndex={-1}
      overflow="hidden"
      bg="gray.50"
      backgroundImage="linear-gradient(rgba(200, 200, 200, 0.2) 1px, transparent 1px), linear-gradient(90deg, rgba(200, 200, 200, 0.2) 1px, transparent 1px)"
      backgroundSize="40px 40px"
    />
  );
}
