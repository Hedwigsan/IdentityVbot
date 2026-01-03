import { useCallback, useState } from 'react';
import {
  Box,
  Card,
  CardBody,
  Text,
  VStack,
  Progress,
  useColorModeValue,
} from '@chakra-ui/react';
import { useDropzone } from 'react-dropzone';
import { FiUpload } from 'react-icons/fi';
import { matchesApi } from '../../services/api';
import type { AnalyzeResponse } from '../../types';

interface ImageUploaderProps {
  onAnalyzeComplete: (result: AnalyzeResponse) => void;
}

export function ImageUploader({ onAnalyzeComplete }: ImageUploaderProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const borderColor = useColorModeValue('gray.300', 'gray.600');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      setIsAnalyzing(true);
      setError(null);

      try {
        const result = await matchesApi.analyze(file);
        onAnalyzeComplete(result);
      } catch (err) {
        console.error('Analyze error:', err);
        setError('画像の解析に失敗しました。もう一度お試しください。');
      } finally {
        setIsAnalyzing(false);
      }
    },
    [onAnalyzeComplete]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg'],
    },
    maxFiles: 1,
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
                <Text fontWeight="medium">解析中...</Text>
                <Progress size="sm" isIndeterminate w="200px" />
                <Text fontSize="sm" color="gray.500">
                  5〜15秒かかる場合があります
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
                  PNG, JPG形式に対応
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
