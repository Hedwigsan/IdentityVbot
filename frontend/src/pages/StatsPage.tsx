import { useState } from 'react';
import {
  Box,
  Heading,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Spinner,
  Center,
  Select,
  HStack,
  FormControl,
  FormLabel,
} from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { statsApi, masterApi } from '../services/api';
import { OverallStatsCard } from '../components/stats/OverallStatsCard';
import { SurvivorPicksChart } from '../components/stats/SurvivorPicksChart';
import { SurvivorWinrateTable } from '../components/stats/SurvivorWinrateTable';
import { SurvivorKiteTable } from '../components/stats/SurvivorKiteTable';
import { MapStatsTable } from '../components/stats/MapStatsTable';

export function StatsPage() {
  const [limit, setLimit] = useState<number | undefined>(undefined);
  const [hunterFilter, setHunterFilter] = useState<string>('');

  const { data: overall, isLoading: loadingOverall } = useQuery({
    queryKey: ['stats', 'overall'],
    queryFn: statsApi.getOverall,
  });

  const { data: picks, isLoading: loadingPicks } = useQuery({
    queryKey: ['stats', 'picks', limit],
    queryFn: () => statsApi.getSurvivorPicks(limit),
  });

  const { data: winrate, isLoading: loadingWinrate } = useQuery({
    queryKey: ['stats', 'winrate', limit],
    queryFn: () => statsApi.getSurvivorWinrate(limit),
  });

  const { data: kite, isLoading: loadingKite } = useQuery({
    queryKey: ['stats', 'kite', hunterFilter, limit],
    queryFn: () => statsApi.getSurvivorKite(hunterFilter || undefined, limit),
  });

  const { data: maps, isLoading: loadingMaps } = useQuery({
    queryKey: ['stats', 'maps', hunterFilter, limit],
    queryFn: () => statsApi.getMapStats(hunterFilter || undefined, limit),
  });

  const { data: hunters } = useQuery({
    queryKey: ['hunters'],
    queryFn: masterApi.getHunters,
  });

  const isLoading = loadingOverall || loadingPicks || loadingWinrate || loadingKite || loadingMaps;

  if (isLoading && !overall) {
    return (
      <Center h="400px">
        <Spinner size="xl" />
      </Center>
    );
  }

  return (
    <Box>
      <Heading size="lg" mb={6}>
        統計
      </Heading>

      {/* フィルター */}
      <HStack spacing={4} mb={6}>
        <FormControl maxW="200px">
          <FormLabel fontSize="sm">集計対象</FormLabel>
          <Select
            size="sm"
            value={limit || ''}
            onChange={(e) => setLimit(e.target.value ? parseInt(e.target.value) : undefined)}
          >
            <option value="">全試合</option>
            <option value="10">直近10試合</option>
            <option value="50">直近50試合</option>
            <option value="100">直近100試合</option>
          </Select>
        </FormControl>

        <FormControl maxW="200px">
          <FormLabel fontSize="sm">ハンター絞り込み</FormLabel>
          <Select
            size="sm"
            value={hunterFilter}
            onChange={(e) => setHunterFilter(e.target.value)}
          >
            <option value="">全ハンター</option>
            {hunters?.map((hunter) => (
              <option key={hunter} value={hunter}>
                {hunter}
              </option>
            ))}
          </Select>
        </FormControl>
      </HStack>

      {/* 全体統計 */}
      {overall && <OverallStatsCard stats={overall} />}

      {/* タブ */}
      <Tabs mt={6}>
        <TabList>
          <Tab>サバイバーピック</Tab>
          <Tab>サバイバー勝率</Tab>
          <Tab>平均牽制時間</Tab>
          <Tab>マップ勝率</Tab>
        </TabList>

        <TabPanels>
          <TabPanel px={0}>
            {picks && <SurvivorPicksChart data={picks} />}
          </TabPanel>
          <TabPanel px={0}>
            {winrate && <SurvivorWinrateTable data={winrate} />}
          </TabPanel>
          <TabPanel px={0}>
            {kite && <SurvivorKiteTable data={kite} />}
          </TabPanel>
          <TabPanel px={0}>
            {maps && <MapStatsTable data={maps} />}
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
}
