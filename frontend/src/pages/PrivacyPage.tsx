import { Box, Container, Heading, Text, VStack, Divider } from '@chakra-ui/react';

export function PrivacyPage() {
  return (
    <Container maxW="container.md" py={8}>
      <VStack spacing={6} align="stretch">
        <Heading size="xl">プライバシーポリシー</Heading>
        <Text color="gray.600" fontSize="sm">
          最終更新日: 2026年1月17日
        </Text>

        <Divider />

        <Box>
          <Heading size="md" mb={3}>
            第1条（個人情報の定義）
          </Heading>
          <Text>
            本プライバシーポリシーにおいて、「個人情報」とは、個人情報保護法に定める「個人情報」を指し、
            生存する個人に関する情報であって、当該情報に含まれる氏名、メールアドレス、その他の記述等により
            特定の個人を識別できるもの（他の情報と容易に照合することができ、それにより特定の個人を識別することができることとなるものを含む）を指します。
          </Text>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第2条（収集する情報）
          </Heading>
          <Text mb={2}>本サービスでは、以下の情報を収集します。</Text>
          <VStack align="stretch" spacing={2} pl={4}>
            <Text fontWeight="bold">1. Googleアカウント情報</Text>
            <VStack align="stretch" spacing={1} pl={4}>
              <Text>• メールアドレス</Text>
              <Text>• 氏名（Googleアカウントに登録されている名前）</Text>
              <Text>• プロフィール画像（Googleアカウントに設定されている画像）</Text>
            </VStack>
            <Text fontWeight="bold" mt={2}>2. ユーザーが入力したデータ</Text>
            <VStack align="stretch" spacing={1} pl={4}>
              <Text>• 試合記録（勝敗、マップ、ハンター、サバイバー情報等）</Text>
              <Text>• アップロードされた画像（OCR処理後に削除されます）</Text>
            </VStack>
            <Text fontWeight="bold" mt={2}>3. 自動的に収集される情報</Text>
            <VStack align="stretch" spacing={1} pl={4}>
              <Text>• アクセスログ（IPアドレス、ブラウザ情報、アクセス日時等）</Text>
              <Text>• Cookie情報（認証トークン等）</Text>
            </VStack>
          </VStack>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第3条（情報の利用目的）
          </Heading>
          <Text mb={2}>収集した情報は、以下の目的で利用します。</Text>
          <VStack align="stretch" spacing={2} pl={4}>
            <Text>• 本サービスの提供、運営、維持</Text>
            <Text>• ユーザー認証およびアカウント管理</Text>
            <Text>• ユーザーが入力した試合記録の保存および統計情報の表示</Text>
            <Text>• サービスの改善、新機能の開発</Text>
            <Text>• 不正利用の防止、セキュリティ対策</Text>
            <Text>• お問い合わせへの対応</Text>
          </VStack>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第4条（情報の第三者提供）
          </Heading>
          <VStack align="stretch" spacing={2}>
            <Text>
              運営者は、以下の場合を除き、ユーザーの個人情報を第三者に提供しません。
            </Text>
            <VStack align="stretch" spacing={1} pl={4}>
              <Text>• ユーザーの同意がある場合</Text>
              <Text>• 法令に基づく場合</Text>
              <Text>• 人の生命、身体または財産の保護のために必要がある場合であって、本人の同意を得ることが困難である場合</Text>
              <Text>• 国の機関もしくは地方公共団体またはその委託を受けた者が法令の定める事務を遂行することに対して協力する必要がある場合</Text>
            </VStack>
          </VStack>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第5条（外部サービスの利用）
          </Heading>
          <Text mb={2}>本サービスは、以下の外部サービスを利用しています。</Text>
          <VStack align="stretch" spacing={3} pl={4}>
            <Box>
              <Text fontWeight="bold">• Google OAuth 2.0（認証）</Text>
              <Text fontSize="sm" pl={4}>
                ユーザー認証のためにGoogleのOAuth 2.0を使用しています。
                Googleのプライバシーポリシーは
                <Text as="span" color="blue.500" textDecoration="underline" cursor="pointer">
                  こちら
                </Text>
                をご確認ください。
              </Text>
            </Box>
            <Box>
              <Text fontWeight="bold">• Supabase（データベース・認証基盤）</Text>
              <Text fontSize="sm" pl={4}>
                ユーザーデータおよび試合記録の保存にSupabaseを使用しています。
                データは暗号化されて保存され、アクセス制御により保護されています。
              </Text>
            </Box>
          </VStack>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第6条（Cookieの使用）
          </Heading>
          <Text>
            本サービスは、ユーザーの利便性向上およびセッション管理のためにCookieを使用します。
            Cookieには認証トークン等が含まれ、ブラウザのローカルストレージに保存されます。
            Cookieを無効にすると、本サービスの一部機能が利用できなくなる場合があります。
          </Text>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第7条（個人情報の開示・訂正・削除）
          </Heading>
          <VStack align="stretch" spacing={2}>
            <Text>ユーザーは、自己の個人情報について、以下の権利を有します。</Text>
            <VStack align="stretch" spacing={1} pl={4}>
              <Text>• 個人情報の開示請求</Text>
              <Text>• 個人情報の訂正・追加・削除の請求</Text>
              <Text>• 個人情報の利用停止・消去の請求</Text>
            </VStack>
            <Text mt={2}>
              これらの請求を行う場合、設定ページから直接データの確認・削除が可能です。
              その他のご要望については、お問い合わせください。
            </Text>
          </VStack>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第8条（データの保管期間）
          </Heading>
          <VStack align="stretch" spacing={2}>
            <Text>• アカウント情報および試合記録：アカウント削除まで保管</Text>
            <Text>• アップロードされた画像：OCR処理後、即座に削除</Text>
            <Text>• アクセスログ：最大90日間保管</Text>
          </VStack>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第9条（セキュリティ対策）
          </Heading>
          <VStack align="stretch" spacing={2}>
            <Text>運営者は、個人情報の保護のため、以下のセキュリティ対策を講じています。</Text>
            <VStack align="stretch" spacing={1} pl={4}>
              <Text>• SSL/TLS暗号化通信の使用</Text>
              <Text>• データベースのアクセス制御（RLS: Row Level Security）</Text>
              <Text>• OAuth 2.0による安全な認証</Text>
              <Text>• 定期的なセキュリティアップデート</Text>
            </VStack>
          </VStack>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第10条（プライバシーポリシーの変更）
          </Heading>
          <Text>
            運営者は、必要と判断した場合、ユーザーへの事前の通知なく本プライバシーポリシーを変更できるものとします。
            変更後のプライバシーポリシーは、本ページに掲載された時点で効力を生じます。
            重要な変更がある場合は、本サービス上で通知します。
          </Text>
        </Box>

        <Box>
          <Heading size="md" mb={3}>
            第11条（お問い合わせ）
          </Heading>
          <Text>
            本プライバシーポリシーに関するお問い合わせは、本サービスのお問い合わせフォームよりご連絡ください。
          </Text>
        </Box>

        <Divider />

        <Text fontSize="sm" color="gray.500" textAlign="center">
          以上
        </Text>
      </VStack>
    </Container>
  );
}
