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
import type { SurvivorWinrateStats } from '../../types';

interface SurvivorWinrateTableProps {
  data: SurvivorWinrateStats[];
}

export function SurvivorWinrateTable({ data }: SurvivorWinrateTableProps) {
  const getWinrateColor = (rate: number): string => {
    if (rate >= 70) return 'green';
    if (rate >= 50) return 'yellow';
    return 'red';
  };

  return (
    <Box overflowX="auto">
      <Table variant="simple" size="sm">
        <Thead>
          <Tr>
            <Th>サバイバー</Th>
            <Th isNumeric>試合数</Th>
            <Th isNumeric>勝利</Th>
            <Th isNumeric>引分</Th>
            <Th isNumeric>敗北</Th>
            <Th isNumeric>勝率</Th>
          </Tr>
        </Thead>
        <Tbody>
          {data.map((item) => (
            <Tr key={item.character}>
              <Td>{item.character}</Td>
              <Td isNumeric>{item.total}</Td>
              <Td isNumeric color="green.500">{item.wins}</Td>
              <Td isNumeric color="yellow.500">{item.draws}</Td>
              <Td isNumeric color="red.500">{item.losses}</Td>
              <Td isNumeric>
                <Badge colorScheme={getWinrateColor(item.win_rate)}>
                  {item.win_rate_str}
                </Badge>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
}
