import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Button,
  Text,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  useToast,
} from '@chakra-ui/react';
import { IconPosition } from '../../types';

interface IconPositionAdjusterProps {
  imageUrl: string;
  imageWidth: number;
  imageHeight: number;
  initialPositions?: IconPosition[];
  onSave: (positions: IconPosition[]) => void;
  onReanalyze: (positions: IconPosition[]) => void;
  isReanalyzing?: boolean;
}

interface DraggableMarker {
  x: number; // ピクセル座標
  y: number; // ピクセル座標
}

export const IconPositionAdjuster: React.FC<IconPositionAdjusterProps> = ({
  imageUrl,
  imageWidth,
  imageHeight,
  initialPositions,
  onSave,
  onReanalyze,
  isReanalyzing = false,
}) => {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [displayWidth, setDisplayWidth] = useState(800);
  const [displayHeight, setDisplayHeight] = useState(600);
  const scale = displayWidth / imageWidth;

  // マーカーの位置（ピクセル座標）
  const [markers, setMarkers] = useState<DraggableMarker[]>([]);

  // アイコンサイズ（比率）
  const [iconSizeRatio, setIconSizeRatio] = useState(0.05);

  const [draggingIndex, setDraggingIndex] = useState<number | null>(null);
  const toast = useToast();

  // 初期位置を設定
  useEffect(() => {
    if (initialPositions && initialPositions.length === 5) {
      const initialMarkers = initialPositions.map(pos => ({
        x: pos.x_ratio * imageWidth,
        y: pos.y_ratio * imageHeight,
      }));
      setMarkers(initialMarkers);
      setIconSizeRatio(initialPositions[0].size_ratio);
    } else {
      // デフォルト位置（等間隔）
      const defaultMarkers: DraggableMarker[] = [];
      const yStart = 0.3;
      const yStep = 0.15;
      const xPos = 0.25;

      for (let i = 0; i < 5; i++) {
        defaultMarkers.push({
          x: xPos * imageWidth,
          y: (yStart + yStep * i) * imageHeight,
        });
      }
      setMarkers(defaultMarkers);
    }
  }, [initialPositions, imageWidth, imageHeight]);

  // 表示サイズを計算
  useEffect(() => {
    const maxWidth = 800;
    const maxHeight = 600;
    const aspectRatio = imageWidth / imageHeight;

    let newWidth = maxWidth;
    let newHeight = maxWidth / aspectRatio;

    if (newHeight > maxHeight) {
      newHeight = maxHeight;
      newWidth = maxHeight * aspectRatio;
    }

    setDisplayWidth(newWidth);
    setDisplayHeight(newHeight);
  }, [imageWidth, imageHeight]);

  const handleMouseDown = (index: number) => (e: React.MouseEvent) => {
    e.preventDefault();
    setDraggingIndex(index);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (draggingIndex === null || !canvasRef.current) return;

    const rect = canvasRef.current.getBoundingClientRect();
    const displayX = e.clientX - rect.left;
    const displayY = e.clientY - rect.top;

    // 画像座標に変換
    const imageX = displayX / scale;
    const imageY = displayY / scale;

    // 境界チェック
    const clampedX = Math.max(0, Math.min(imageWidth, imageX));
    const clampedY = Math.max(0, Math.min(imageHeight, imageY));

    setMarkers(prev => {
      const newMarkers = [...prev];
      newMarkers[draggingIndex] = { x: clampedX, y: clampedY };
      return newMarkers;
    });
  };

  const handleMouseUp = () => {
    setDraggingIndex(null);
  };

  const getIconPositions = (): IconPosition[] => {
    return markers.map(marker => ({
      x_ratio: marker.x / imageWidth,
      y_ratio: marker.y / imageHeight,
      size_ratio: iconSizeRatio,
    }));
  };

  const handleReanalyze = () => {
    const positions = getIconPositions();
    onReanalyze(positions);
  };

  const handleSave = () => {
    const positions = getIconPositions();
    onSave(positions);
    toast({
      title: 'レイアウトを保存しました',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  const iconSize = iconSizeRatio * imageWidth * scale;

  return (
    <VStack spacing={4} align="stretch">
      <Text fontSize="lg" fontWeight="bold">
        アイコン位置調整
      </Text>
      <Text fontSize="sm" color="gray.600">
        5つのマーカーをドラッグして、各キャラクターアイコンの位置に合わせてください。
        上から順に：勝利時は「ハンター、サバイバー1〜4」、敗北時は「サバイバー1〜4、ハンター」です。
      </Text>

      {/* 画像プレビュー + マーカー */}
      <Box
        ref={canvasRef}
        position="relative"
        width={`${displayWidth}px`}
        height={`${displayHeight}px`}
        border="2px solid"
        borderColor="gray.300"
        borderRadius="md"
        overflow="hidden"
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        cursor={draggingIndex !== null ? 'grabbing' : 'default'}
      >
        {/* 画像 */}
        <img
          src={imageUrl}
          alt="Match result"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            pointerEvents: 'none',
            userSelect: 'none',
          }}
        />

        {/* マーカー */}
        {markers.map((marker, index) => (
          <Box
            key={index}
            position="absolute"
            left={`${marker.x * scale - iconSize / 2}px`}
            top={`${marker.y * scale - iconSize / 2}px`}
            width={`${iconSize}px`}
            height={`${iconSize}px`}
            border="3px solid"
            borderColor={index === 0 ? 'red.500' : 'blue.500'}
            bg={draggingIndex === index ? 'rgba(0, 123, 255, 0.3)' : 'rgba(0, 123, 255, 0.1)'}
            borderRadius="md"
            cursor="grab"
            onMouseDown={handleMouseDown(index)}
            transition="all 0.1s"
            _hover={{
              bg: 'rgba(0, 123, 255, 0.2)',
              borderWidth: '4px',
            }}
          >
            {/* 番号表示 */}
            <Box
              position="absolute"
              top="2px"
              left="2px"
              bg={index === 0 ? 'red.500' : 'blue.500'}
              color="white"
              px={1}
              borderRadius="sm"
              fontSize="2xs"
              fontWeight="bold"
              lineHeight="1"
              pointerEvents="none"
            >
              {index}
            </Box>
          </Box>
        ))}
      </Box>

      {/* サイズ調整 */}
      <Box>
        <Text fontSize="sm" fontWeight="medium" mb={2}>
          アイコンサイズ: {(iconSizeRatio * 100).toFixed(1)}%
        </Text>
        <Slider
          value={iconSizeRatio * 100}
          onChange={(val) => setIconSizeRatio(val / 100)}
          min={2}
          max={15}
          step={0.1}
        >
          <SliderTrack>
            <SliderFilledTrack />
          </SliderTrack>
          <SliderThumb />
        </Slider>
      </Box>

      {/* ボタン */}
      <HStack spacing={4}>
        <Button
          colorScheme="blue"
          onClick={handleReanalyze}
          isLoading={isReanalyzing}
          loadingText="再認識中..."
          flex={1}
        >
          この位置で再認識
        </Button>
        <Button
          colorScheme="green"
          onClick={handleSave}
          flex={1}
        >
          設定を保存
        </Button>
      </HStack>

      <Text fontSize="xs" color="gray.500">
        ※ 「この位置で再認識」をクリックすると、調整した位置で画像認識を再実行します。
        認識が成功したら「設定を保存」で他のユーザーとも共有されます。
      </Text>
    </VStack>
  );
};
