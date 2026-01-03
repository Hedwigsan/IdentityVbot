import {
  Card,
  CardBody,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
} from '@chakra-ui/react';
import type { OverallStats } from '../../types';

interface OverallStatsCardProps {
  stats: OverallStats;
}

export function OverallStatsCard({ stats }: OverallStatsCardProps) {
  return (
    <Card>
      <CardBody>
        <SimpleGrid columns={{ base: 2, md: 5 }} spacing={4}>
          <Stat>
            <StatLabel>総試合数</StatLabel>
            <StatNumber>{stats.total_matches}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>勝利</StatLabel>
            <StatNumber color="green.500">{stats.wins}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>引き分け</StatLabel>
            <StatNumber color="yellow.500">{stats.draws}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>敗北</StatLabel>
            <StatNumber color="red.500">{stats.losses}</StatNumber>
          </Stat>
          <Stat>
            <StatLabel>勝率</StatLabel>
            <StatNumber>{stats.win_rate}</StatNumber>
            <StatHelpText>引き分け除外</StatHelpText>
          </Stat>
        </SimpleGrid>
      </CardBody>
    </Card>
  );
}
