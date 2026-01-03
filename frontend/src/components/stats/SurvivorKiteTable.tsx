import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
} from '@chakra-ui/react';
import type { SurvivorKiteStats } from '../../types';

interface SurvivorKiteTableProps {
  data: SurvivorKiteStats[];
}

export function SurvivorKiteTable({ data }: SurvivorKiteTableProps) {
  return (
    <Box overflowX="auto">
      <Table variant="simple" size="sm">
        <Thead>
          <Tr>
            <Th>サバイバー</Th>
            <Th isNumeric>平均牽制時間</Th>
            <Th isNumeric>サンプル数</Th>
          </Tr>
        </Thead>
        <Tbody>
          {data.map((item) => (
            <Tr key={item.character}>
              <Td>{item.character}</Td>
              <Td isNumeric fontWeight="bold">{item.avg_kite_time}</Td>
              <Td isNumeric color="gray.500">{item.samples}</Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
}
