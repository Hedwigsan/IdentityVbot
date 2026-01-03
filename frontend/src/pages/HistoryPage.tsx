import { useState, useRef } from 'react';
import {
  Box,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  IconButton,
  HStack,
  Select,
  FormControl,
  FormLabel,
  Spinner,
  Center,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  VStack,
  Text,
  SimpleGrid,
  useToast,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  Button,
} from '@chakra-ui/react';
import { FiEye, FiTrash2 } from 'react-icons/fi';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { matchesApi, masterApi } from '../services/api';
import type { MatchResponse } from '../types';

export function HistoryPage() {
  const [hunterFilter, setHunterFilter] = useState<string>('');
  const [mapFilter, setMapFilter] = useState<string>('');
  const [resultFilter, setResultFilter] = useState<string>('');
  const [selectedMatch, setSelectedMatch] = useState<MatchResponse | null>(null);
  const [deleteMatchId, setDeleteMatchId] = useState<number | null>(null);

  const { isOpen: isDetailOpen, onOpen: onDetailOpen, onClose: onDetailClose } = useDisclosure();
  const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure();
  const cancelRef = useRef<HTMLButtonElement>(null);
  const toast = useToast();
  const queryClient = useQueryClient();

  const { data: matchesData, isLoading } = useQuery({
    queryKey: ['matches', hunterFilter, mapFilter, resultFilter],
    queryFn: () =>
      matchesApi.getAll({
        hunter: hunterFilter || undefined,
        map_name: mapFilter || undefined,
        result: resultFilter || undefined,
      }),
  });

  const matches = matchesData?.matches;

  const { data: hunters } = useQuery({
    queryKey: ['hunters'],
    queryFn: masterApi.getHunters,
  });

  const { data: maps } = useQuery({
    queryKey: ['maps'],
    queryFn: masterApi.getMaps,
  });

  const deleteMutation = useMutation({
    mutationFn: matchesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matches'] });
      toast({
        title: '削除しました',
        status: 'success',
        duration: 3000,
      });
      onDeleteClose();
    },
    onError: () => {
      toast({
        title: '削除に失敗しました',
        status: 'error',
        duration: 3000,
      });
    },
  });

  const handleViewDetails = (match: MatchResponse) => {
    setSelectedMatch(match);
    onDetailOpen();
  };

  const handleDeleteClick = (matchId: number) => {
    setDeleteMatchId(matchId);
    onDeleteOpen();
  };

  const handleDeleteConfirm = () => {
    if (deleteMatchId) {
      deleteMutation.mutate(deleteMatchId);
    }
  };

  const getResultBadge = (result: string) => {
    switch (result) {
      case '勝利':
        return <Badge colorScheme="green">{result}</Badge>;
      case '敗北':
        return <Badge colorScheme="red">{result}</Badge>;
      default:
        return <Badge colorScheme="yellow">{result}</Badge>;
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <Center h="400px">
        <Spinner size="xl" />
      </Center>
    );
  }

  return (
    <Box>
      <Heading size="lg" mb={6}>
        履歴
      </Heading>

      {/* フィルター */}
      <HStack spacing={4} mb={6} flexWrap="wrap">
        <FormControl maxW="150px">
          <FormLabel fontSize="sm">結果</FormLabel>
          <Select
            size="sm"
            value={resultFilter}
            onChange={(e) => setResultFilter(e.target.value)}
          >
            <option value="">すべて</option>
            <option value="勝利">勝利</option>
            <option value="敗北">敗北</option>
            <option value="引き分け">引き分け</option>
          </Select>
        </FormControl>

        <FormControl maxW="150px">
          <FormLabel fontSize="sm">ハンター</FormLabel>
          <Select
            size="sm"
            value={hunterFilter}
            onChange={(e) => setHunterFilter(e.target.value)}
          >
            <option value="">すべて</option>
            {hunters?.map((hunter) => (
              <option key={hunter} value={hunter}>
                {hunter}
              </option>
            ))}
          </Select>
        </FormControl>

        <FormControl maxW="150px">
          <FormLabel fontSize="sm">マップ</FormLabel>
          <Select
            size="sm"
            value={mapFilter}
            onChange={(e) => setMapFilter(e.target.value)}
          >
            <option value="">すべて</option>
            {maps?.map((map) => (
              <option key={map} value={map}>
                {map}
              </option>
            ))}
          </Select>
        </FormControl>
      </HStack>

      {/* テーブル */}
      <Box overflowX="auto">
        <Table variant="simple" size="sm">
          <Thead>
            <Tr>
              <Th>日時</Th>
              <Th>結果</Th>
              <Th>ハンター</Th>
              <Th>マップ</Th>
              <Th>時間</Th>
              <Th>操作</Th>
            </Tr>
          </Thead>
          <Tbody>
            {matches?.map((match) => (
              <Tr key={match.id}>
                <Td>{formatDate(match.played_at || match.match_date)}</Td>
                <Td>{getResultBadge(match.result)}</Td>
                <Td>{match.hunter_character || '-'}</Td>
                <Td>{match.map_name}</Td>
                <Td>{match.match_duration || '-'}</Td>
                <Td>
                  <HStack spacing={1}>
                    <IconButton
                      aria-label="詳細"
                      icon={<FiEye />}
                      size="sm"
                      variant="ghost"
                      onClick={() => handleViewDetails(match)}
                    />
                    <IconButton
                      aria-label="削除"
                      icon={<FiTrash2 />}
                      size="sm"
                      variant="ghost"
                      colorScheme="red"
                      onClick={() => handleDeleteClick(match.id)}
                    />
                  </HStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </Box>

      {matches?.length === 0 && (
        <Center py={10}>
          <Text color="gray.500">試合データがありません</Text>
        </Center>
      )}

      {/* 詳細モーダル */}
      <Modal isOpen={isDetailOpen} onClose={onDetailClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>試合詳細</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            {selectedMatch && (
              <VStack spacing={4} align="stretch">
                <SimpleGrid columns={2} spacing={4}>
                  <Box>
                    <Text fontSize="sm" color="gray.500">結果</Text>
                    <Text>{getResultBadge(selectedMatch.result)}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.500">日時</Text>
                    <Text>{formatDate(selectedMatch.played_at || selectedMatch.match_date)}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.500">ハンター</Text>
                    <Text>{selectedMatch.hunter_character || '-'}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.500">マップ</Text>
                    <Text>{selectedMatch.map_name}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.500">試合時間</Text>
                    <Text>{selectedMatch.match_duration || '-'}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.500">特質</Text>
                    <Text>{selectedMatch.trait_used || '-'}</Text>
                  </Box>
                </SimpleGrid>

                {selectedMatch.persona && (
                  <Box>
                    <Text fontSize="sm" color="gray.500">人格</Text>
                    <Text>{selectedMatch.persona}</Text>
                  </Box>
                )}

                {selectedMatch.banned_characters && selectedMatch.banned_characters.length > 0 && (
                  <Box>
                    <Text fontSize="sm" color="gray.500">Banキャラ</Text>
                    <Text>{selectedMatch.banned_characters.join(', ')}</Text>
                  </Box>
                )}

                {selectedMatch.survivors && selectedMatch.survivors.length > 0 && (
                  <Box>
                    <Text fontSize="sm" color="gray.500" mb={2}>サバイバー</Text>
                    <Table size="sm" variant="simple">
                      <Thead>
                        <Tr>
                          <Th>キャラ</Th>
                          <Th>牽制</Th>
                          <Th>解読</Th>
                          <Th>救助</Th>
                        </Tr>
                      </Thead>
                      <Tbody>
                        {selectedMatch.survivors.map((s, i) => (
                          <Tr key={i}>
                            <Td>{s.character_name || '-'}</Td>
                            <Td>{s.kite_time || '-'}</Td>
                            <Td>{s.decode_progress || '-'}</Td>
                            <Td>{s.rescues}</Td>
                          </Tr>
                        ))}
                      </Tbody>
                    </Table>
                  </Box>
                )}
              </VStack>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>

      {/* 削除確認ダイアログ */}
      <AlertDialog
        isOpen={isDeleteOpen}
        leastDestructiveRef={cancelRef}
        onClose={onDeleteClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              試合を削除
            </AlertDialogHeader>
            <AlertDialogBody>
              この試合データを削除しますか？この操作は取り消せません。
            </AlertDialogBody>
            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onDeleteClose}>
                キャンセル
              </Button>
              <Button
                colorScheme="red"
                onClick={handleDeleteConfirm}
                ml={3}
                isLoading={deleteMutation.isPending}
              >
                削除
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  );
}
