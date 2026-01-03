import { useState } from 'react';
import {
  Box,
  Heading,
  VStack,
  useToast,
} from '@chakra-ui/react';
import { ImageUploader } from '../components/record/ImageUploader';
import { MatchEditor } from '../components/record/MatchEditor';
import type { AnalyzeResponse, MatchCreateRequest } from '../types';
import { matchesApi } from '../services/api';

type Step = 'upload' | 'edit';

export function RecordPage() {
  const [step, setStep] = useState<Step>('upload');
  const [analyzeResult, setAnalyzeResult] = useState<AnalyzeResponse | null>(null);
  const toast = useToast();

  const handleAnalyzeComplete = (result: AnalyzeResponse) => {
    setAnalyzeResult(result);
    setStep('edit');
  };

  const handleSave = async (data: MatchCreateRequest) => {
    try {
      await matchesApi.create(data);
      toast({
        title: '保存しました',
        status: 'success',
        duration: 3000,
      });
      // リセット
      setStep('upload');
      setAnalyzeResult(null);
    } catch (err) {
      toast({
        title: '保存に失敗しました',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleCancel = () => {
    setStep('upload');
    setAnalyzeResult(null);
  };

  return (
    <Box>
      <Heading size="lg" mb={6}>
        試合記録
      </Heading>

      <VStack spacing={6} align="stretch">
        {step === 'upload' && (
          <ImageUploader onAnalyzeComplete={handleAnalyzeComplete} />
        )}

        {step === 'edit' && analyzeResult && (
          <MatchEditor
            analyzeResult={analyzeResult}
            onSave={handleSave}
            onCancel={handleCancel}
          />
        )}
      </VStack>
    </Box>
  );
}
