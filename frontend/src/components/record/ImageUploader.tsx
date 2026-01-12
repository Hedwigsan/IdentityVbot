import { useCallback, useState } from 'react';
import {
  Box,
  Card,
  CardBody,
  Text,
  VStack,
  Progress,
  useColorModeValue,
  HStack,
  Badge,
} from '@chakra-ui/react';
import { useDropzone } from 'react-dropzone';
import { FiUpload } from 'react-icons/fi';
import { matchesApi } from '../../services/api';
import type { AnalyzeResponse } from '../../types';

interface ImageUploaderProps {
  onAnalyzeComplete: (results: AnalyzeResponse[], file?: File) => void;
}

export function ImageUploader({ onAnalyzeComplete }: ImageUploaderProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState({ current: 0, total: 0 });

  const borderColor = useColorModeValue('gray.300', 'gray.600');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      setIsAnalyzing(true);
      setError(null);
      setUploadProgress({ current: 0, total: acceptedFiles.length });

      try {
        const results: AnalyzeResponse[] = [];

        for (let i = 0; i < acceptedFiles.length; i++) {
          const file = acceptedFiles[i];
          setUploadProgress({ current: i + 1, total: acceptedFiles.length });

          try {
            const result = await matchesApi.analyze(file);
            results.push(result);
          } catch (err) {
            console.error(`Analyze error for file ${i + 1}:`, err);
            // 個別のエラーは無視して続行
          }
        }

        if (results.length === 0) {
          setError('すべての画像の解析に失敗しました。もう一度お試しください。');
        } else {
          // 単一ファイルの場合、ファイル情報も渡す
          onAnalyzeComplete(results, acceptedFiles.length === 1 ? acceptedFiles[0] : undefined);
        }
      } catch (err) {
        console.error('Analyze error:', err);
        setError('画像の解析に失敗しました。もう一度お試しください。');
      } finally {
        setIsAnalyzing(false);
        setUploadProgress({ current: 0, total: 0 });
      }
    },
    [onAnalyzeComplete]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
    },
    multiple: true,
    disabled: isAnalyzing,
  });

  return (
    <Card>
      <CardBody>
        <Box
          {...getRootProps()}
          border="2px dashed"
          borderColor={isDragActive ? 'blue.400' : borderColor}
          borderRadius="lg"
          p={10}
          textAlign="center"
          cursor={isAnalyzing ? 'not-allowed' : 'pointer'}
          bg={isDragActive ? hoverBg : 'transparent'}
          transition="all 0.2s"
          _hover={{ bg: isAnalyzing ? 'transparent' : hoverBg }}
        >
          <input {...getInputProps()} />
          <VStack spacing={4}>
            <Box fontSize="4xl" color="gray.400">
              <FiUpload />
            </Box>
            {isAnalyzing ? (
              <>
                <HStack spacing={2}>
                  <Text fontWeight="medium">解析中...</Text>
                  {uploadProgress.total > 0 && (
                    <Badge colorScheme="blue">
                      {uploadProgress.current} / {uploadProgress.total}
                    </Badge>
                  )}
                </HStack>
                <Progress size="sm" isIndeterminate w="200px" />
                <Text fontSize="sm" color="gray.500">
                  画像1枚につき5〜15秒かかる場合があります
                </Text>
              </>
            ) : (
              <>
                <Text fontWeight="medium">
                  {isDragActive
                    ? '画像をドロップしてください'
                    : '試合結果画像をドロップ、またはクリックして選択'}
                </Text>
                <Text fontSize="sm" color="gray.500">
                  PNG, JPG形式に対応（複数選択可能）
                </Text>
              </>
            )}
            {error && (
              <Text color="red.500" fontSize="sm">
                {error}
              </Text>
            )}
          </VStack>
        </Box>
      </CardBody>
    </Card>
  );
}
