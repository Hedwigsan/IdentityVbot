import { Box } from '@chakra-ui/react';
import Squares from './Squares';

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
    >
      <Squares
        direction="diagonal"
        speed={0.1}
        borderColor="rgba(200, 200, 200, 0.21)"
        squareSize={40}
        hoverFillColor="rgba(100, 100, 255, 0.1)"
      />
    </Box>
  );
}
