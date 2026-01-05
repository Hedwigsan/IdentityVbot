import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Progress,
} from '@chakra-ui/react';
import type { SurvivorPickStats } from '../../types';

interface SurvivorPicksChartProps {
  data: SurvivorPickStats[];
}

export function SurvivorPicksChart({ data }: SurvivorPicksChartProps) {
  const maxPicks = Math.max(...data.map((d) => d.picks), 1);

  return (
    <Box overflowX="auto">
      <Table
        variant="simple"
        size="sm"
        sx={{
          'th, td': {
            borderBottom: 'none !important',
          },
        }}
      >
        <Thead>
          <Tr>
            <Th w="200px">サバイバー</Th>
            <Th isNumeric w="100px">ピック数</Th>
            <Th>割合</Th>
          </Tr>
        </Thead>
        <Tbody>
          {data.map((item) => (
            <Tr key={item.character}>
              <Td>{item.character}</Td>
              <Td isNumeric>{item.picks}</Td>
              <Td>
                <Progress
                  value={(item.picks / maxPicks) * 100}
                  size="sm"
                  colorScheme="blue"
                />
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
}
