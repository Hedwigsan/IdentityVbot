import { useState } from 'react';
import {
  Box,
  Heading,
  VStack,
  useToast,
} from '@chakra-ui/react';
import { ImageUploader } from '../components/record/ImageUploader';
import { MatchEditor } from '../components/record/MatchEditor';
import { MultiMatchEditor } from '../components/record/MultiMatchEditor';
import type { AnalyzeResponse, MatchCreateRequest } from '../types';
import { matchesApi } from '../services/api';

type Step = 'upload' | 'edit';

export function RecordPage() {
  const [step, setStep] = useState<Step>('upload');
  const [analyzeResults, setAnalyzeResults] = useState<AnalyzeResponse[]>([]);
  const toast = useToast();

  const handleAnalyzeComplete = (results: AnalyzeResponse[]) => {
    setAnalyzeResults(results);
    setStep('edit');
  };

  const handleSave = async (data: MatchCreateRequest | MatchCreateRequest[]) => {
    try {
      const dataArray = Array.isArray(data) ? data : [data];

      // 複数試合を順番に保存
      for (const match of dataArray) {
        await matchesApi.create(match);
      }

      toast({
        title: `${dataArray.length}件の試合を保存しました`,
        status: 'success',
        duration: 3000,
      });
      // リセット
      setStep('upload');
      setAnalyzeResults([]);
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
    setAnalyzeResults([]);
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

        {step === 'edit' && analyzeResults.length > 0 && (
          analyzeResults.length === 1 ? (
            <MatchEditor
              analyzeResult={analyzeResults[0]}
              onSave={handleSave}
              onCancel={handleCancel}
            />
          ) : (
            <MultiMatchEditor
              analyzeResults={analyzeResults}
              onSave={handleSave}
              onCancel={handleCancel}
            />
          )
        )}
      </VStack>
    </Box>
  );
}
