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
  Badge,
  Wrap,
  WrapItem,
  Checkbox,
  Textarea,
  Collapse,
  IconButton,
  Text,
} from '@chakra-ui/react';
import { ChevronDownIcon, ChevronUpIcon } from '@chakra-ui/icons';
import { useQuery } from '@tanstack/react-query';
import { masterApi } from '../../services/api';
import type { AnalyzeResponse, MatchCreateRequest, SurvivorData } from '../../types';

interface MatchEditorProps {
  analyzeResult: AnalyzeResponse;
  onSave: (data: MatchCreateRequest) => void;
  onCancel: () => void;
}

export function MatchEditor({ analyzeResult, onSave, onCancel }: MatchEditorProps) {
  const [result, setResult] = useState(analyzeResult.result || '');
  const [mapName, setMapName] = useState(analyzeResult.map_name || '');
  const [duration, setDuration] = useState(analyzeResult.duration || '');
  const [hunterCharacter, setHunterCharacter] = useState(analyzeResult.hunter_character || '');
  const [traitUsed, setTraitUsed] = useState('');
  const [persona, setPersona] = useState('');
  const [bannedCharacters, setBannedCharacters] = useState<string[]>([]);
  const [isBanOpen, setIsBanOpen] = useState(false);
  const [survivors, setSurvivors] = useState<SurvivorData[]>(analyzeResult.survivors || []);

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

  const handleBanToggle = (name: string) => {
    if (bannedCharacters.includes(name)) {
      setBannedCharacters(bannedCharacters.filter((c) => c !== name));
    } else if (bannedCharacters.length < 3) {
      setBannedCharacters([...bannedCharacters, name]);
    }
  };

  const handleSurvivorChange = (
    index: number,
    field: keyof SurvivorData,
    value: string | number
  ) => {
    const newSurvivors = [...survivors];
    newSurvivors[index] = { ...newSurvivors[index], [field]: value };
    setSurvivors(newSurvivors);
  };

  const handleSubmit = () => {
    const data: MatchCreateRequest = {
      result,
      map_name: mapName,
      match_duration: duration,
      hunter_character: hunterCharacter,
      trait_used: traitUsed || undefined,
      persona: persona || undefined,
      banned_characters: bannedCharacters.length > 0 ? bannedCharacters : undefined,
      played_at: analyzeResult.played_at,
      survivors,
    };
    onSave(data);
  };

  return (
    <VStack spacing={6} align="stretch">
      {/* 基本情報 */}
      <Card>
        <CardHeader>
          <Heading size="md">試合情報</Heading>
        </CardHeader>
        <CardBody>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <FormControl>
              <FormLabel>結果</FormLabel>
              <Select value={result} onChange={(e) => setResult(e.target.value)}>
                <option value="">選択してください</option>
                <option value="勝利">勝利</option>
                <option value="敗北">敗北</option>
                <option value="引き分け">引き分け</option>
              </Select>
            </FormControl>

            <FormControl>
              <FormLabel>マップ</FormLabel>
              <Select value={mapName} onChange={(e) => setMapName(e.target.value)}>
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
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                placeholder="例: 7:30"
              />
            </FormControl>

            <FormControl>
              <FormLabel>ハンター</FormLabel>
              <Select
                value={hunterCharacter}
                onChange={(e) => setHunterCharacter(e.target.value)}
              >
                <option value="">選択してください</option>
                {hunters?.map((hunter) => (
                  <option key={hunter} value={hunter}>
                    {hunter}
                  </option>
                ))}
              </Select>
            </FormControl>

            <FormControl>
              <FormLabel>特質</FormLabel>
              <Select value={traitUsed} onChange={(e) => setTraitUsed(e.target.value)}>
                <option value="">選択してください</option>
                {traits?.map((trait) => (
                  <option key={trait} value={trait}>
                    {trait}
                  </option>
                ))}
              </Select>
            </FormControl>
          </SimpleGrid>

          <FormControl mt={4}>
            <FormLabel>人格</FormLabel>
            <Textarea
              value={persona}
              onChange={(e) => setPersona(e.target.value)}
              placeholder="使用した人格を入力..."
              rows={2}
            />
          </FormControl>
        </CardBody>
      </Card>

      {/* Banキャラ選択 */}
      <Card>
        <CardHeader>
          <HStack justify="space-between">
            <Heading size="md">Banキャラ</Heading>
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
                icon={isBanOpen ? <ChevronUpIcon /> : <ChevronDownIcon />}
                size="sm"
                variant="ghost"
                onClick={() => setIsBanOpen(!isBanOpen)}
              />
            </HStack>
          </HStack>
        </CardHeader>
        <CardBody>
          <Collapse in={isBanOpen} animateOpacity>
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
        </CardBody>
      </Card>

      {/* サバイバー情報 */}
      <Card>
        <CardHeader>
          <Heading size="md">サバイバー</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            {survivors.map((survivor, index) => (
              <Box
                key={index}
                p={4}
                borderWidth={1}
                borderRadius="md"
              >
                <SimpleGrid columns={{ base: 2, md: 4 }} spacing={3}>
                  <FormControl>
                    <FormLabel fontSize="sm">キャラクター</FormLabel>
                    <Select
                      size="sm"
                      value={survivor.character_name || ''}
                      onChange={(e) =>
                        handleSurvivorChange(index, 'character_name', e.target.value)
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
                      value={survivor.kite_time || ''}
                      onChange={(e) =>
                        handleSurvivorChange(index, 'kite_time', e.target.value)
                      }
                      placeholder="0:00"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel fontSize="sm">解読進捗</FormLabel>
                    <Input
                      size="sm"
                      value={survivor.decode_progress || ''}
                      onChange={(e) =>
                        handleSurvivorChange(index, 'decode_progress', e.target.value)
                      }
                      placeholder="0%"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel fontSize="sm">救助回数</FormLabel>
                    <Input
                      size="sm"
                      type="number"
                      value={survivor.rescues || 0}
                      onChange={(e) =>
                        handleSurvivorChange(index, 'rescues', parseInt(e.target.value) || 0)
                      }
                    />
                  </FormControl>
                </SimpleGrid>
              </Box>
            ))}

            {survivors.length < 4 && (
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  setSurvivors([
                    ...survivors,
                    {
                      character_name: '',
                      position: survivors.length + 1,
                      kite_time: '',
                      decode_progress: '',
                      board_hits: 0,
                      rescues: 0,
                      heals: 0,
                    },
                  ])
                }
              >
                サバイバーを追加
              </Button>
            )}
          </VStack>
        </CardBody>
      </Card>

      {/* ボタン */}
      <HStack justify="flex-end" spacing={4}>
        <Button variant="outline" onClick={onCancel}>
          キャンセル
        </Button>
        <Button
          colorScheme="blue"
          onClick={handleSubmit}
          isDisabled={!result || !mapName}
        >
          保存
        </Button>
      </HStack>
    </VStack>
  );
}
