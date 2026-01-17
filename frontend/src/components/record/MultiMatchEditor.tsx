import { useState } from 'react';
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  Heading,
  VStack,
  HStack,
  FormControl,
  FormLabel,
  Input,
  Select,
  Button,
  SimpleGrid,
  Wrap,
  WrapItem,
  Checkbox,
  Textarea,
  Divider,
  Badge,
  Text,
  Switch,
  Collapse,
  IconButton,
} from '@chakra-ui/react';
import { ChevronDownIcon, ChevronUpIcon } from '@chakra-ui/icons';
import { useQuery } from '@tanstack/react-query';
import { masterApi } from '../../services/api';
import type { AnalyzeResponse, MatchCreateRequest, SurvivorData } from '../../types';

interface MultiMatchEditorProps {
  analyzeResults: AnalyzeResponse[];
  onSave: (data: MatchCreateRequest[]) => void;
  onCancel: () => void;
}

interface MatchData {
  result: string;
  mapName: string;
  duration: string;
  hunterCharacter: string;
  playedAt: string;
  survivors: SurvivorData[];
  useIndividualSettings: boolean;
  individualPersona?: string;
  individualTrait?: string;
  individualBannedCharacters?: string[];
}

export function MultiMatchEditor({ analyzeResults, onSave, onCancel }: MultiMatchEditorProps) {
  // 共通設定
  const [persona, setPersona] = useState('');
  const [traitUsed, setTraitUsed] = useState('');
  const [bannedCharacters, setBannedCharacters] = useState<string[]>([]);
  const [isCommonBanOpen, setIsCommonBanOpen] = useState(false);

  // 各試合のデータ
  const [matches, setMatches] = useState<MatchData[]>(
    analyzeResults.map(result => ({
      result: result.result || '',
      mapName: result.map_name || '',
      duration: result.duration || '',
      hunterCharacter: result.hunter_character || '',
      playedAt: result.played_at || '',
      survivors: result.survivors || [],
      useIndividualSettings: false,
      individualPersona: '',
      individualTrait: '',
      individualBannedCharacters: [],
    }))
  );

  // マスターデータ取得
  const { data: hunters } = useQuery({
    queryKey: ['hunters'],
    queryFn: masterApi.getHunters,
  });

  const { data: survivorList } = useQuery({
    queryKey: ['survivors'],
    queryFn: masterApi.getSurvivors,
  });

  const { data: traits } = useQuery({
    queryKey: ['traits'],
    queryFn: masterApi.getTraits,
  });

  const { data: maps } = useQuery({
    queryKey: ['maps'],
    queryFn: masterApi.getMaps,
  });

  // 共通設定変更時に、空欄の個別設定のみを埋める
  const handleTraitChange = (newTrait: string) => {
    setTraitUsed(newTrait);
    if (newTrait) {
      setMatches(prevMatches =>
        prevMatches.map(match => ({
          ...match,
          individualTrait: match.individualTrait || newTrait,
        }))
      );
    }
  };

  const handlePersonaChange = (newPersona: string) => {
    setPersona(newPersona);
    if (newPersona) {
      setMatches(prevMatches =>
        prevMatches.map(match => ({
          ...match,
          individualPersona: match.individualPersona || newPersona,
        }))
      );
    }
  };

  const handleCommonBanChange = (newBannedCharacters: string[]) => {
    setBannedCharacters(newBannedCharacters);
    if (newBannedCharacters.length > 0) {
      setMatches(prevMatches =>
        prevMatches.map(match => ({
          ...match,
          individualBannedCharacters:
            match.individualBannedCharacters && match.individualBannedCharacters.length > 0
              ? match.individualBannedCharacters
              : newBannedCharacters,
        }))
      );
    }
  };

  const handleBanToggle = (name: string) => {
    let newBannedCharacters: string[];
    if (bannedCharacters.includes(name)) {
      newBannedCharacters = bannedCharacters.filter((c) => c !== name);
    } else if (bannedCharacters.length < 3) {
      newBannedCharacters = [...bannedCharacters, name];
    } else {
      return;
    }
    handleCommonBanChange(newBannedCharacters);
  };

  const handleMatchChange = (
    index: number,
    field: keyof MatchData,
    value: string | SurvivorData[] | boolean | string[]
  ) => {
    const newMatches = [...matches];
    newMatches[index] = { ...newMatches[index], [field]: value };
    setMatches(newMatches);
  };

  const handleIndividualBanToggle = (matchIndex: number, name: string) => {
    const match = matches[matchIndex];
    const currentBanned = match.individualBannedCharacters || [];

    if (currentBanned.includes(name)) {
      handleMatchChange(
        matchIndex,
        'individualBannedCharacters',
        currentBanned.filter((c) => c !== name)
      );
    } else if (currentBanned.length < 3) {
      handleMatchChange(
        matchIndex,
        'individualBannedCharacters',
        [...currentBanned, name]
      );
    }
  };

  const handleSurvivorChange = (
    matchIndex: number,
    survivorIndex: number,
    field: keyof SurvivorData,
    value: string | number
  ) => {
    const newMatches = [...matches];
    const newSurvivors = [...newMatches[matchIndex].survivors];
    newSurvivors[survivorIndex] = { ...newSurvivors[survivorIndex], [field]: value };
    newMatches[matchIndex].survivors = newSurvivors;
    setMatches(newMatches);
  };

  const handleSubmit = () => {
    const data: MatchCreateRequest[] = matches.map(match => ({
      result: match.result,
      map_name: match.mapName,
      match_duration: match.duration,
      hunter_character: match.hunterCharacter,
      trait_used: match.useIndividualSettings
        ? (match.individualTrait || undefined)
        : (traitUsed || undefined),
      persona: match.useIndividualSettings
        ? (match.individualPersona || undefined)
        : (persona || undefined),
      banned_characters: match.useIndividualSettings
        ? (match.individualBannedCharacters && match.individualBannedCharacters.length > 0
            ? match.individualBannedCharacters
            : undefined)
        : (bannedCharacters.length > 0 ? bannedCharacters : undefined),
      played_at: match.playedAt,
      survivors: match.survivors,
    }));
    onSave(data);
  };

  return (
    <VStack spacing={6} align="stretch">
      {/* 共通設定 */}
      <Card>
        <CardHeader>
          <Heading size="md">共通設定（全試合に適用）</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <FormControl>
              <FormLabel>特質</FormLabel>
              <Select value={traitUsed} onChange={(e) => handleTraitChange(e.target.value)}>
                <option value="">選択してください</option>
                {traits?.map((trait) => (
                  <option key={trait} value={trait}>
                    {trait}
                  </option>
                ))}
              </Select>
            </FormControl>

            <FormControl>
              <FormLabel>人格</FormLabel>
              <Textarea
                value={persona}
                onChange={(e) => handlePersonaChange(e.target.value)}
                placeholder="使用した人格を入力..."
                rows={2}
              />
            </FormControl>

            <FormControl>
              <HStack justify="space-between" mb={2}>
                <FormLabel mb={0}>BANキャラ</FormLabel>
                <HStack spacing={2}>
                  <Badge colorScheme={bannedCharacters.length === 3 ? 'green' : 'gray'}>
                    {bannedCharacters.length}/3
                  </Badge>
                  {bannedCharacters.length > 0 && (
                    <Text fontSize="sm" color="gray.600">
                      {bannedCharacters.join(', ')}
                    </Text>
                  )}
                  <IconButton
                    aria-label="BANキャラを展開"
                    icon={isCommonBanOpen ? <ChevronUpIcon /> : <ChevronDownIcon />}
                    size="sm"
                    variant="ghost"
                    onClick={() => setIsCommonBanOpen(!isCommonBanOpen)}
                  />
                </HStack>
              </HStack>
              <Collapse in={isCommonBanOpen} animateOpacity>
                <Wrap spacing={2}>
                  {survivorList?.map((survivor) => (
                    <WrapItem key={survivor}>
                      <Checkbox
                        isChecked={bannedCharacters.includes(survivor)}
                        onChange={() => handleBanToggle(survivor)}
                        isDisabled={
                          !bannedCharacters.includes(survivor) && bannedCharacters.length >= 3
                        }
                      >
                        {survivor}
                      </Checkbox>
                    </WrapItem>
                  ))}
                </Wrap>
              </Collapse>
            </FormControl>
          </VStack>
        </CardBody>
      </Card>

      {/* 各試合の編集 */}
      {matches.map((match, matchIndex) => (
        <Card key={matchIndex}>
          <CardHeader>
            <HStack justify="space-between">
              <Heading size="md">試合 {matchIndex + 1}</Heading>
              <Badge colorScheme="blue" fontSize="md">
                {match.result || '未設定'}
              </Badge>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              {/* 基本情報 */}
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                <FormControl isRequired>
                  <FormLabel>勝敗</FormLabel>
                  <Select
                    value={match.result}
                    onChange={(e) => handleMatchChange(matchIndex, 'result', e.target.value)}
                  >
                    <option value="">選択してください</option>
                    <option value="勝利">勝利</option>
                    <option value="敗北">敗北</option>
                    <option value="引き分け">引き分け</option>
                  </Select>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>マップ</FormLabel>
                  <Select
                    value={match.mapName}
                    onChange={(e) => handleMatchChange(matchIndex, 'mapName', e.target.value)}
                  >
                    <option value="">選択してください</option>
                    {maps?.map((map) => (
                      <option key={map} value={map}>
                        {map}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>試合時間</FormLabel>
                  <Input
                    value={match.duration}
                    onChange={(e) => handleMatchChange(matchIndex, 'duration', e.target.value)}
                    placeholder="例: 5:30"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>使用ハンター</FormLabel>
                  <Select
                    value={match.hunterCharacter}
                    onChange={(e) => handleMatchChange(matchIndex, 'hunterCharacter', e.target.value)}
                  >
                    <option value="">選択してください</option>
                    {hunters?.map((hunter) => (
                      <option key={hunter} value={hunter}>
                        {hunter}
                      </option>
                    ))}
                  </Select>
                </FormControl>
              </SimpleGrid>

              {/* 個別設定トグル */}
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor={`individual-${matchIndex}`} mb="0">
                  この試合だけ個別に設定する
                </FormLabel>
                <Switch
                  id={`individual-${matchIndex}`}
                  isChecked={match.useIndividualSettings}
                  onChange={(e) =>
                    handleMatchChange(matchIndex, 'useIndividualSettings', e.target.checked)
                  }
                />
              </FormControl>

              {/* 個別設定（トグルON時のみ表示） */}
              <Collapse in={match.useIndividualSettings} animateOpacity>
                <Card variant="outline" bg="blue.50">
                  <CardBody>
                    <VStack spacing={4} align="stretch">
                      <FormControl>
                        <FormLabel>特質</FormLabel>
                        <Select
                          value={match.individualTrait || ''}
                          onChange={(e) =>
                            handleMatchChange(matchIndex, 'individualTrait', e.target.value)
                          }
                        >
                          <option value="">選択してください</option>
                          {traits?.map((trait) => (
                            <option key={trait} value={trait}>
                              {trait}
                            </option>
                          ))}
                        </Select>
                      </FormControl>

                      <FormControl>
                        <FormLabel>人格</FormLabel>
                        <Textarea
                          value={match.individualPersona || ''}
                          onChange={(e) =>
                            handleMatchChange(matchIndex, 'individualPersona', e.target.value)
                          }
                          placeholder="使用した人格を入力..."
                          rows={2}
                        />
                      </FormControl>

                      <FormControl>
                        <HStack justify="space-between" mb={2}>
                          <FormLabel mb={0}>BANキャラ</FormLabel>
                          <HStack spacing={2}>
                            <Badge
                              colorScheme={
                                (match.individualBannedCharacters?.length || 0) === 3
                                  ? 'green'
                                  : 'gray'
                              }
                            >
                              {match.individualBannedCharacters?.length || 0}/3
                            </Badge>
                            {(match.individualBannedCharacters?.length || 0) > 0 && (
                              <Text fontSize="sm" color="gray.600">
                                {match.individualBannedCharacters?.join(', ')}
                              </Text>
                            )}
                          </HStack>
                        </HStack>
                        <Wrap spacing={2}>
                          {survivorList?.map((survivor) => (
                            <WrapItem key={survivor}>
                              <Checkbox
                                isChecked={match.individualBannedCharacters?.includes(survivor)}
                                onChange={() => handleIndividualBanToggle(matchIndex, survivor)}
                                isDisabled={
                                  !match.individualBannedCharacters?.includes(survivor) &&
                                  (match.individualBannedCharacters?.length || 0) >= 3
                                }
                              >
                                {survivor}
                              </Checkbox>
                            </WrapItem>
                          ))}
                        </Wrap>
                      </FormControl>
                    </VStack>
                  </CardBody>
                </Card>
              </Collapse>

              <Divider />

              {/* サバイバー情報 */}
              <Box>
                <Text fontWeight="bold" mb={2}>
                  サバイバー情報
                </Text>
                <VStack spacing={3} align="stretch">
                  {match.survivors.map((survivor, survivorIndex) => (
                    <Card key={survivorIndex} variant="outline" size="sm">
                      <CardBody>
                        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={3}>
                          <FormControl>
                            <FormLabel fontSize="sm">キャラクター</FormLabel>
                            <Select
                              size="sm"
                              value={survivor.character_name}
                              onChange={(e) =>
                                handleSurvivorChange(
                                  matchIndex,
                                  survivorIndex,
                                  'character_name',
                                  e.target.value
                                )
                              }
                            >
                              <option value="">選択</option>
                              {survivorList?.map((s) => (
                                <option key={s} value={s}>
                                  {s}
                                </option>
                              ))}
                            </Select>
                          </FormControl>

                          <FormControl>
                            <FormLabel fontSize="sm">牽制時間</FormLabel>
                            <Input
                              size="sm"
                              value={survivor.kite_time}
                              onChange={(e) =>
                                handleSurvivorChange(
                                  matchIndex,
                                  survivorIndex,
                                  'kite_time',
                                  e.target.value
                                )
                              }
                              placeholder="0:00"
                            />
                          </FormControl>

                          <FormControl>
                            <FormLabel fontSize="sm">解読進捗</FormLabel>
                            <Input
                              size="sm"
                              value={survivor.decode_progress}
                              onChange={(e) =>
                                handleSurvivorChange(
                                  matchIndex,
                                  survivorIndex,
                                  'decode_progress',
                                  e.target.value
                                )
                              }
                              placeholder="0%"
                            />
                          </FormControl>
                        </SimpleGrid>
                      </CardBody>
                    </Card>
                  ))}
                </VStack>
              </Box>
            </VStack>
          </CardBody>
        </Card>
      ))}

      {/* 保存/キャンセルボタン */}
      <HStack justify="flex-end" spacing={4}>
        <Button variant="ghost" onClick={onCancel}>
          キャンセル
        </Button>
        <Button colorScheme="blue" onClick={handleSubmit}>
          {matches.length}件の試合を保存
        </Button>
      </HStack>
    </VStack>
  );
}
