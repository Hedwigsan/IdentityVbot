import { useState } from 'react';
import {
  Box,
  Heading,
  VStack,
  useToast,
  Button,
  Alert,
  AlertIcon,
  AlertDescription,
  HStack,
  Text,
} from '@chakra-ui/react';
import { ImageUploader } from '../components/record/ImageUploader';
import { MatchEditor } from '../components/record/MatchEditor';
import { MultiMatchEditor } from '../components/record/MultiMatchEditor';
import { IconPositionAdjuster } from '../components/layout/IconPositionAdjuster';
import type { AnalyzeResponse, MatchCreateRequest, IconPosition, DeviceLayoutCreate } from '../types';
import { matchesApi, layoutApi } from '../services/api';

type Step = 'upload' | 'edit' | 'adjust';

export function RecordPage() {
  const [step, setStep] = useState<Step>('upload');
  const [analyzeResults, setAnalyzeResults] = useState<AnalyzeResponse[]>([]);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadedImageUrl, setUploadedImageUrl] = useState<string | null>(null);
  const [imageMetadata, setImageMetadata] = useState<{ width: number; height: number } | null>(null);
  const [isReanalyzing, setIsReanalyzing] = useState(false);
  const [reanalyzedPositions, setReanalyzedPositions] = useState<IconPosition[] | null>(null);
  const toast = useToast();

  const handleAnalyzeComplete = (results: AnalyzeResponse[], file?: File) => {
    setAnalyzeResults(results);

    // 単一ファイルの場合、画像情報を保存（位置調整用）
    if (file && results.length === 1) {
      setUploadedFile(file);
      const url = URL.createObjectURL(file);
      setUploadedImageUrl(url);

      // 画像サイズを取得
      const img = new Image();
      img.onload = () => {
        setImageMetadata({ width: img.width, height: img.height });
      };
      img.src = url;
    }

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
      cleanup();
    } catch (err) {
      toast({
        title: '保存に失敗しました',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleCancel = () => {
    cleanup();
  };

  const handleAdjustPosition = () => {
    setStep('adjust');
    setReanalyzedPositions(null);
  };

  const handleReanalyze = async (positions: IconPosition[]) => {
    if (!uploadedFile || !imageMetadata) {
      toast({
        title: 'エラー',
        description: '画像情報が見つかりません',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setIsReanalyzing(true);

    try {
      // カスタムレイアウトを使って再解析（保存はしない）
      const result = await matchesApi.analyzeWithLayout(uploadedFile, positions);
      setAnalyzeResults([result]);
      setReanalyzedPositions(positions);

      toast({
        title: '再認識完了',
        description: '結果を確認して「設定を保存」すると、今後自動的に設定が使用されます。',
        status: 'success',
        duration: 5000,
      });

      // 位置調整画面に留まる（「設定を保存」ボタンを表示するため）
    } catch (err) {
      console.error('Reanalyze error:', err);
      toast({
        title: '再認識に失敗しました',
        description: 'もう一度お試しください',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsReanalyzing(false);
    }
  };

  const handleSaveLayout = async (positions: IconPosition[]) => {
    if (!imageMetadata) {
      toast({
        title: 'エラー',
        description: '画像情報が見つかりません',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    try {
      const aspectRatio = imageMetadata.width / imageMetadata.height;
      const layoutData: DeviceLayoutCreate = {
        aspect_ratio: aspectRatio,
        screen_width: imageMetadata.width,
        screen_height: imageMetadata.height,
        icon_positions: positions,
      };

      await layoutApi.saveLayout(layoutData);

      toast({
        title: '設定を保存しました',
        description: '他のユーザーとも共有されます',
        status: 'success',
        duration: 3000,
      });
    } catch (err) {
      console.error('Save layout error:', err);
      toast({
        title: '保存に失敗しました',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const cleanup = () => {
    setStep('upload');
    setAnalyzeResults([]);
    setUploadedFile(null);
    if (uploadedImageUrl) {
      URL.revokeObjectURL(uploadedImageUrl);
      setUploadedImageUrl(null);
    }
    setImageMetadata(null);
    setReanalyzedPositions(null);
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
          <VStack spacing={4} align="stretch">
            {/* 認識失敗時の案内 */}
            {analyzeResults.length === 1 && uploadedFile && (
              <Alert status="info" borderRadius="md">
                <AlertIcon />
                <AlertDescription flex={1}>
                  認識結果が正しくない場合は、アイコン位置を調整できます
                </AlertDescription>
                <Button
                  size="sm"
                  colorScheme="blue"
                  onClick={handleAdjustPosition}
                >
                  位置を調整
                </Button>
              </Alert>
            )}

            {analyzeResults.length === 1 ? (
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
            )}
          </VStack>
        )}

        {step === 'adjust' && uploadedImageUrl && imageMetadata && (
          <VStack spacing={4} align="stretch">
            {/* 再認識結果の表示 */}
            {reanalyzedPositions && analyzeResults.length > 0 && (
              <Alert status="success" borderRadius="md">
                <AlertIcon />
                <VStack align="start" spacing={2} flex={1}>
                  <AlertDescription fontWeight="bold">
                    再認識結果
                  </AlertDescription>
                  <Text fontSize="sm">
                    勝敗: {analyzeResults[0].result || '不明'}、
                    マップ: {analyzeResults[0].map_name || '不明'}、
                    ハンター: {analyzeResults[0].hunter_character || '不明'}
                  </Text>
                  <Text fontSize="sm" fontWeight="medium">
                    サバイバー ({analyzeResults[0].survivors.filter(s => s.character_name).length}/4人認識):
                  </Text>
                  <VStack align="start" spacing={0} pl={2}>
                    {analyzeResults[0].survivors.map((survivor, index) => (
                      <Text key={index} fontSize="sm">
                        {index + 1}. {survivor.character_name || '認識失敗'}
                        {survivor.kite_time && ` (牽制: ${survivor.kite_time})`}
                      </Text>
                    ))}
                  </VStack>
                </VStack>
                <Button
                  size="sm"
                  colorScheme="green"
                  onClick={() => setStep('edit')}
                >
                  結果を確認
                </Button>
              </Alert>
            )}

            <IconPositionAdjuster
              imageUrl={uploadedImageUrl}
              imageWidth={imageMetadata.width}
              imageHeight={imageMetadata.height}
              onSave={handleSaveLayout}
              onReanalyze={handleReanalyze}
              isReanalyzing={isReanalyzing}
            />

            <HStack>
              <Button onClick={() => setStep('edit')} variant="ghost">
                戻る
              </Button>
            </HStack>
          </VStack>
        )}
      </VStack>
    </Box>
  );
}
