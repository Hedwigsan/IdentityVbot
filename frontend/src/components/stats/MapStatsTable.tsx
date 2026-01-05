import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
} from '@chakra-ui/react';
import type { MapStats } from '../../types';

interface MapStatsTableProps {
  data: MapStats[];
}

export function MapStatsTable({ data }: MapStatsTableProps) {
  const getWinrateColor = (rate: string): string => {
    const num = parseFloat(rate);
    if (num >= 70) return 'green';
    if (num >= 50) return 'yellow';
    return 'red';
  };

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
            <Th>マップ</Th>
            <Th isNumeric>試合数</Th>
            <Th isNumeric>勝利</Th>
            <Th isNumeric>引分</Th>
            <Th isNumeric>敗北</Th>
            <Th isNumeric>勝率</Th>
          </Tr>
        </Thead>
        <Tbody>
          {data.map((item) => (
            <Tr key={item.map_name}>
              <Td>{item.map_name}</Td>
              <Td isNumeric>{item.total}</Td>
              <Td isNumeric color="green.500">{item.wins}</Td>
              <Td isNumeric color="yellow.500">{item.draws}</Td>
              <Td isNumeric color="red.500">{item.losses}</Td>
              <Td isNumeric>
                <Badge colorScheme={getWinrateColor(item.win_rate)}>
                  {item.win_rate}
                </Badge>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
}
