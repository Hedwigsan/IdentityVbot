import {
  Box,
  Heading,
  VStack,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Text,
  Card,
  CardBody,
  Link,
  Image,
} from '@chakra-ui/react';

export function HelpPage() {
  return (
    <Box>
      <Heading size="lg" mb={6}>
        ヘルプ
      </Heading>

      <VStack spacing={6} align="stretch">
        {/* 概要 */}
        <Card>
          <CardBody>
            <Heading size="md" mb={4}>
              Identity Archiveについて
            </Heading>
            <Text>
              Identity Archiveは、第五人格（Identity V）のハンター戦績を記録・分析するWebアプリケーションです。
              試合結果のスクリーンショットをアップロードすることで、自動的にデータを抽出し、統計情報を確認できます。
            </Text>
          </CardBody>
        </Card>

        {/* FAQ */}
        <Card>
          <CardBody>
            <Heading size="md" mb={4}>
              よくある質問
            </Heading>
            <Accordion allowToggle>
              <AccordionItem>
                <h2>
                  <AccordionButton>
                    <Box flex="1" textAlign="left" fontWeight="medium">
                      試合記録の方法は？
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                </h2>
                <AccordionPanel pb={4}>
                  <VStack align="stretch" spacing={3}>
                    <Text>1. ゲームの試合結果画面のスクリーンショットを撮影します</Text>
                    <Image
                      src="/example.png"
                      alt="試合結果画面の例"
                      borderRadius="md"
                      maxW="600px"
                      w="100%"
                      my={2}
                    />
                    <Text>2. 「記録」ページで画像をアップロードします（複数枚同時アップロード可能）</Text>
                    <Text>3. 自動解析された内容を確認・修正します</Text>
                    <Text>4. 人格、特質、BANキャラなどの共通設定を入力します</Text>
                    <Text>5. 「保存」ボタンで記録完了です</Text>
                  </VStack>
                </AccordionPanel>
              </AccordionItem>

              <AccordionItem>
                <h2>
                  <AccordionButton>
                    <Box flex="1" textAlign="left" fontWeight="medium">
                      複数の試合を一度に記録できますか？
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                </h2>
                <AccordionPanel pb={4}>
                  <Text>
                    はい、可能です。画像アップロード時に複数枚選択することで、まとめて記録できます。
                    人格や特質などの共通設定は全試合に一括適用されます。
                  </Text>
                </AccordionPanel>
              </AccordionItem>

              <AccordionItem>
                <h2>
                  <AccordionButton>
                    <Box flex="1" textAlign="left" fontWeight="medium">
                      統計情報の見方は？
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                </h2>
                <AccordionPanel pb={4}>
                  <VStack align="stretch" spacing={2}>
                    <Text>
                      「統計」ページでは、記録した試合データを様々な角度から分析できます。
                    </Text>
                    <Text>• 総合: 勝率、試合数、使用ハンターの統計</Text>
                    <Text>• ハンター別: ハンターごとの詳細な戦績</Text>
                    <Text>• マップ別: マップごとの勝率や試合数</Text>
                    <Text>• 期間フィルター: 日付範囲で絞り込み可能</Text>
                  </VStack>
                </AccordionPanel>
              </AccordionItem>

              <AccordionItem>
                <h2>
                  <AccordionButton>
                    <Box flex="1" textAlign="left" fontWeight="medium">
                      画像が正しく認識されない場合は？
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                </h2>
                <AccordionPanel pb={4}>
                  <VStack align="stretch" spacing={2}>
                    <Text>
                      使用端末によっては初回使用時は正しく認識されない可能性があります。画像認識後、ページ上部の「位置を調整」ボタンからアイコン位置を正しく設定してください。
                    </Text>
                    <Text>
                      また、画像解析後に表示される編集画面で、手動で修正することもできます。
                    </Text>
                    <Text>• 勝敗、マップ、使用ハンターなどをドロップダウンから選択</Text>
                    <Text>• サバイバー情報（キャラクター、牽制時間、解読進捗）を入力</Text>
                    <Text>• 修正後、保存してください</Text>
                  </VStack>
                </AccordionPanel>
              </AccordionItem>

              <AccordionItem>
                <h2>
                  <AccordionButton>
                    <Box flex="1" textAlign="left" fontWeight="medium">
                      記録した試合を削除できますか？
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                </h2>
                <AccordionPanel pb={4}>
                  <Text>
                    はい、「履歴」ページから試合を選択し、削除ボタンで削除できます。
                  </Text>
                </AccordionPanel>
              </AccordionItem>

              <AccordionItem>
                <h2>
                  <AccordionButton>
                    <Box flex="1" textAlign="left" fontWeight="medium">
                      対応している画像形式は？
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                </h2>
                <AccordionPanel pb={4}>
                  <Text>
                    PNG、JPG、JPEG形式の画像に対応しています。
                    スクリーンショットは鮮明であるほど、認識精度が向上します。
                  </Text>
                </AccordionPanel>
              </AccordionItem>
            </Accordion>
          </CardBody>
        </Card>

        {/* お問い合わせ */}
        <Card>
          <CardBody>
            <Heading size="md" mb={4}>
              お問い合わせ
            </Heading>
            <Text>
              不具合の報告や機能のご要望は、
              <Link href="https://x.com/Subwigsan" color="blue.500" isExternal ml={1}>
                X
              </Link>
              までお願いします。
            </Text>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  );
}
