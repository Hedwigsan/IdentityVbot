import { Box, Container, Heading, Text, VStack, Divider } from '@chakra-ui/react';

export function TermsPage() {
  return (
    <Container maxW="container.md" py={8}>
      <VStack spacing={6} align="stretch">
        <Heading size="xl">利用規約</Heading>
        <Text color="gray.600" fontSize="sm">
          最終更新日: 2026年1月17日
        </Text>

        <Divider />

        <Box>
          <Heading size="md" mb={3}>
            第1条（適用）
          </Heading>
          <Text>
            本利用規約（以下、「本規約」といいます）は、Identity Archive（以下、「本サービス」といいます）の利用条件を定めるものです。
            本サービスを利用するすべてのユーザー（以下、「ユーザー」といいます）は、本規約に同意したものとみなされます。
          </Text>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第2条（サービスの内容）
          </Heading>
          <Text>
            本サービスは、第五人格（Identity V）のハンター戦績を記録・管理するための非公式ファンサイトです。
            本サービスはNetEase Inc.とは一切関係がなく、個人が運営する非営利のファンメイドサイトです。
          </Text>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第3条（アカウント）
          </Heading>
          <VStack align="stretch" spacing={2}>
            <Text>1. ユーザーは、Googleアカウントを使用して本サービスにログインします。</Text>
            <Text>2. ユーザーは、自己の責任においてアカウントを管理するものとします。</Text>
            <Text>3. アカウントの不正利用が発見された場合、運営者は事前の通知なくアカウントを停止または削除することができます。</Text>
          </VStack>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第4条（禁止事項）
          </Heading>
          <Text mb={2}>ユーザーは、以下の行為を行ってはなりません。</Text>
          <VStack align="stretch" spacing={2} pl={4}>
            <Text>• 法令または公序良俗に違反する行為</Text>
            <Text>• 本サービスの運営を妨害する行為</Text>
            <Text>• 他のユーザーまたは第三者の権利を侵害する行為</Text>
            <Text>• 不正アクセスやシステムへの攻撃行為</Text>
            <Text>• 本サービスを営利目的で利用する行為</Text>
            <Text>• その他、運営者が不適切と判断する行為</Text>
          </VStack>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第5条（データの取り扱い）
          </Heading>
          <VStack align="stretch" spacing={2}>
            <Text>1. ユーザーが入力した試合記録データは、Supabaseのデータベースに保存されます。</Text>
            <Text>2. データはユーザー本人のみがアクセス可能であり、他のユーザーと共有されることはありません。</Text>
            <Text>3. 運営者は、サービス改善のため統計データを匿名化して利用する場合があります。</Text>
          </VStack>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第6条（免責事項）
          </Heading>
          <VStack align="stretch" spacing={2}>
            <Text>1. 本サービスは「現状有姿」で提供され、運営者は明示的または黙示的な保証を一切行いません。</Text>
            <Text>2. 運営者は、本サービスの利用に起因して発生した損害について、一切の責任を負いません。</Text>
            <Text>3. 本サービスは予告なく内容の変更、中断、終了する場合があります。</Text>
            <Text>4. OCR機能による自動読み取り結果は参考情報であり、正確性を保証するものではありません。</Text>
          </VStack>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第7条（著作権・商標）
          </Heading>
          <VStack align="stretch" spacing={2}>
            <Text>1. 第五人格（Identity V）およびそのすべてのゲーム内アセット、キャラクター名、画像等の著作権・商標権はNetEase Inc.に帰属します。</Text>
            <Text>2. 本サービスは非公式のファンメイドサイトであり、NetEase Inc.の承認または支援を受けていません。</Text>
            <Text>3. 本サービスのソースコードおよびオリジナルコンテンツの著作権は運営者に帰属します。</Text>
          </VStack>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第8条（規約の変更）
          </Heading>
          <Text>
            運営者は、必要と判断した場合、ユーザーへの事前の通知なく本規約を変更できるものとします。
            変更後の規約は、本ページに掲載された時点で効力を生じます。
          </Text>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第9条（準拠法・管轄裁判所）
          </Heading>
          <VStack align="stretch" spacing={2}>
            <Text>1. 本規約の解釈にあたっては、日本法を準拠法とします。</Text>
            <Text>2. 本サービスに関する紛争については、運営者の所在地を管轄する裁判所を専属的合意管轄とします。</Text>
          </VStack>
        </Box>

        <Divider />

        <Text fontSize="sm" color="gray.500" textAlign="center">
          以上
        </Text>
      </VStack>
    </Container>
  );
}
