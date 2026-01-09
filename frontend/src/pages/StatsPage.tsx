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
  Input,
  Button,
  Tag,
  TagLabel,
  TagCloseButton,
  Wrap,
  WrapItem,
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
  const [traitFilter, setTraitFilter] = useState<string>('');
  const [personaFilter, setPersonaFilter] = useState<string>('');
  const [customPersonaInput, setCustomPersonaInput] = useState<string>('');
  const [customPersona, setCustomPersona] = useState<string>('');
  const [bannedCharacters, setBannedCharacters] = useState<string[]>([]);
  const [selectedBanChar, setSelectedBanChar] = useState<string>('');

  // 使用する人格フィルタ（カスタム入力があればそれを優先）
  const activePersona = customPersona || personaFilter || undefined;

  const { data: overall, isLoading: loadingOverall } = useQuery({
    queryKey: ['stats', 'overall', hunterFilter, traitFilter, activePersona, bannedCharacters],
    queryFn: () => statsApi.getOverall(
      hunterFilter || undefined,
      traitFilter || undefined,
      activePersona,
      bannedCharacters.length > 0 ? bannedCharacters : undefined
    ),
  });

  const { data: picks, isLoading: loadingPicks } = useQuery({
    queryKey: ['stats', 'picks', hunterFilter, traitFilter, limit, activePersona, bannedCharacters],
    queryFn: () => statsApi.getSurvivorPicks(
      hunterFilter || undefined,
      traitFilter || undefined,
      limit,
      activePersona,
      bannedCharacters.length > 0 ? bannedCharacters : undefined
    ),
  });

  const { data: winrate, isLoading: loadingWinrate } = useQuery({
    queryKey: ['stats', 'winrate', hunterFilter, traitFilter, limit, activePersona, bannedCharacters],
    queryFn: () => statsApi.getSurvivorWinrate(
      hunterFilter || undefined,
      traitFilter || undefined,
      limit,
      activePersona,
      bannedCharacters.length > 0 ? bannedCharacters : undefined
    ),
  });

  const { data: kite, isLoading: loadingKite } = useQuery({
    queryKey: ['stats', 'kite', hunterFilter, traitFilter, limit, activePersona, bannedCharacters],
    queryFn: () => statsApi.getSurvivorKite(
      hunterFilter || undefined,
      traitFilter || undefined,
      limit,
      activePersona,
      bannedCharacters.length > 0 ? bannedCharacters : undefined
    ),
  });

  const { data: maps, isLoading: loadingMaps } = useQuery({
    queryKey: ['stats', 'maps', hunterFilter, traitFilter, limit, activePersona, bannedCharacters],
    queryFn: () => statsApi.getMapStats(
      hunterFilter || undefined,
      traitFilter || undefined,
      limit,
      activePersona,
      bannedCharacters.length > 0 ? bannedCharacters : undefined
    ),
  });

  const { data: hunters } = useQuery({
    queryKey: ['hunters'],
    queryFn: masterApi.getHunters,
  });

  const { data: traits } = useQuery({
    queryKey: ['traits'],
    queryFn: masterApi.getTraits,
  });

  const { data: recentPersonas } = useQuery({
    queryKey: ['recentPersonas'],
    queryFn: statsApi.getRecentPersonas,
  });

  const { data: survivors } = useQuery({
    queryKey: ['survivors'],
    queryFn: masterApi.getSurvivors,
  });

  // カスタム人格を適用
  const handleApplyCustomPersona = () => {
    setCustomPersona(customPersonaInput);
  };

  // BANキャラを追加
  const handleAddBannedChar = () => {
    if (selectedBanChar && !bannedCharacters.includes(selectedBanChar) && bannedCharacters.length < 3) {
      setBannedCharacters([...bannedCharacters, selectedBanChar]);
      setSelectedBanChar('');
    }
  };

  // BANキャラを削除
  const handleRemoveBannedChar = (char: string) => {
    setBannedCharacters(bannedCharacters.filter((c) => c !== char));
  };

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
      <Box mb={6}>
        <HStack spacing={4} mb={4} flexWrap="wrap">
          <FormControl maxW="200px">
            <FormLabel fontSize="sm">集計対象</FormLabel>
            <Select
              size="sm"
              value={limit || ''}
              onChange={(e) => setLimit(e.target.value ? parseInt(e.target.value) : undefined)}
              bg="rgba(255, 255, 255, 0.8)"
              borderColor="white"
              borderWidth="2px"
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
              bg="rgba(255, 255, 255, 0.8)"
              borderColor="white"
              borderWidth="2px"
            >
              <option value="">全ハンター</option>
              {hunters?.map((hunter) => (
                <option key={hunter} value={hunter}>
                  {hunter}
                </option>
              ))}
            </Select>
          </FormControl>

          <FormControl maxW="200px">
            <FormLabel fontSize="sm">特質絞り込み</FormLabel>
            <Select
              size="sm"
              value={traitFilter}
              onChange={(e) => setTraitFilter(e.target.value)}
              bg="rgba(255, 255, 255, 0.8)"
              borderColor="white"
              borderWidth="2px"
            >
              <option value="">全特質</option>
              {traits?.map((trait) => (
                <option key={trait} value={trait}>
                  {trait}
                </option>
              ))}
            </Select>
          </FormControl>

          <FormControl maxW="200px">
            <FormLabel fontSize="sm">人格絞り込み</FormLabel>
            <Select
              size="sm"
              value={personaFilter}
              onChange={(e) => {
                setPersonaFilter(e.target.value);
                if (e.target.value !== 'custom') {
                  setCustomPersona('');
                  setCustomPersonaInput('');
                }
              }}
              bg="rgba(255, 255, 255, 0.8)"
              borderColor="white"
              borderWidth="2px"
            >
              <option value="">全人格</option>
              {recentPersonas?.map((persona) => (
                <option key={persona} value={persona}>
                  {persona}
                </option>
              ))}
              <option value="custom">その他（手入力）</option>
            </Select>
          </FormControl>

          {personaFilter === 'custom' && (
            <>
              <FormControl maxW="200px">
                <FormLabel fontSize="sm">人格名入力</FormLabel>
                <Input
                  size="sm"
                  value={customPersonaInput}
                  onChange={(e) => setCustomPersonaInput(e.target.value)}
                  placeholder="人格名を入力"
                  bg="rgba(255, 255, 255, 0.8)"
                  borderColor="white"
                  borderWidth="2px"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleApplyCustomPersona();
                    }
                  }}
                />
              </FormControl>
              <FormControl maxW="100px" alignSelf="flex-end">
                <Button
                  size="sm"
                  onClick={handleApplyCustomPersona}
                  colorScheme="blue"
                  isDisabled={!customPersonaInput}
                >
                  適用
                </Button>
              </FormControl>
            </>
          )}
        </HStack>

        <FormControl>
          <FormLabel fontSize="sm">BANキャラ（最大3キャラ）</FormLabel>
          <HStack spacing={2} mb={2}>
            <Select
              size="sm"
              maxW="200px"
              value={selectedBanChar}
              onChange={(e) => setSelectedBanChar(e.target.value)}
              bg="rgba(255, 255, 255, 0.8)"
              borderColor="white"
              borderWidth="2px"
              isDisabled={bannedCharacters.length >= 3}
            >
              <option value="">サバイバーを選択</option>
              {survivors?.map((survivor) => (
                <option
                  key={survivor}
                  value={survivor}
                  disabled={bannedCharacters.includes(survivor)}
                >
                  {survivor}
                </option>
              ))}
            </Select>
            <Button
              size="sm"
              onClick={handleAddBannedChar}
              isDisabled={!selectedBanChar || bannedCharacters.length >= 3}
              colorScheme="blue"
            >
              追加
            </Button>
          </HStack>
          {bannedCharacters.length > 0 && (
            <Wrap spacing={2}>
              {bannedCharacters.map((char) => (
                <WrapItem key={char}>
                  <Tag size="md" colorScheme="red" borderRadius="full">
                    <TagLabel>{char}</TagLabel>
                    <TagCloseButton onClick={() => handleRemoveBannedChar(char)} />
                  </Tag>
                </WrapItem>
              ))}
            </Wrap>
          )}
        </FormControl>
      </Box>

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
