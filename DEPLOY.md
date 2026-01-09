# Renderへのデプロイ手順

## 前提条件

- GitHubリポジトリにコードをpush済み
- Renderアカウント作成済み（https://render.com）
- Supabaseプロジェクト作成済み

## 1. バックエンド（FastAPI）のデプロイ

### 1.1 Renderでサービスを作成

1. Render Dashboardにログイン
2. 「New +」→ 「Web Service」をクリック
3. GitHubリポジトリを接続・選択
4. 以下の設定を入力:
   - **Name**: `identity-archive-backend`
   - **Region**: `Oregon (US West)`（日本に近いリージョンを選択）
   - **Branch**: `master` または `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 1.2 環境変数を設定

「Environment」タブで以下を追加:

- `SUPABASE_URL`: `https://your-project.supabase.co`
- `SUPABASE_KEY`: Supabaseの**service_role**キー
- `FRONTEND_URL`: フロントエンドのURL（後で設定、例: `https://identity-archive.onrender.com`）
- `PYTHON_VERSION`: `3.11.0`

### 1.3 デプロイ

「Create Web Service」をクリックして自動デプロイ開始。

完了後、バックエンドのURLをメモ（例: `https://identity-archive-backend.onrender.com`）

## 2. フロントエンド（React）のデプロイ

### 2.1 Renderで静的サイトを作成

1. Render Dashboardで「New +」→ 「Static Site」をクリック
2. 同じGitHubリポジトリを選択
3. 以下の設定を入力:
   - **Name**: `identity-archive`
   - **Branch**: `master` または `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

### 2.2 環境変数を設定

「Environment」タブで以下を追加:

- `VITE_API_URL`: バックエンドのURL（例: `https://identity-archive-backend.onrender.com`）
- `VITE_SUPABASE_URL`: `https://your-project.supabase.co`
- `VITE_SUPABASE_ANON_KEY`: Supabaseの**anon**キー（publicキー）

### 2.3 デプロイ

「Create Static Site」をクリックして自動デプロイ開始。

完了後、フロントエンドのURLをメモ（例: `https://identity-archive.onrender.com`）

## 3. CORS設定とSupabase設定の更新

### 3.1 バックエンドのCORS設定

バックエンドの環境変数`FRONTEND_URL`をフロントエンドのURLに更新:
- `FRONTEND_URL`: `https://identity-archive.onrender.com`

Render Dashboardで環境変数を変更後、自動的に再デプロイされます。

### 3.2 Supabaseのリダイレクト設定

1. Supabase Dashboard → Authentication → URL Configuration
2. 「Redirect URLs」にフロントエンドのコールバックURLを追加:
   - `https://identity-archive.onrender.com/auth/callback`

## 4. 動作確認

1. フロントエンドURL（`https://identity-archive.onrender.com`）にアクセス
2. ログインボタンをクリックしてGoogle認証が動作するか確認
3. 試合記録、統計表示などの機能をテスト

## トラブルシューティング

### ビルドエラーが出る場合

- **バックエンド**: `requirements.txt`に必要な依存パッケージが全て含まれているか確認
- **フロントエンド**: `package.json`と`package-lock.json`がコミットされているか確認

### CORS エラーが出る場合

- バックエンドの`FRONTEND_URL`環境変数が正しいフロントエンドURLになっているか確認
- `backend/app/main.py`のCORS設定を確認

### 認証エラーが出る場合

- Supabaseの「Redirect URLs」にフロントエンドのコールバックURLが追加されているか確認
- フロントエンドの`VITE_SUPABASE_URL`と`VITE_SUPABASE_ANON_KEY`が正しいか確認

### 画像解析が動作しない場合

- バックエンドのログを確認（Render Dashboard → Logs）
- OCRライブラリ（yomitoku、easyocr）がインストールされているか確認
- テンプレート画像ファイル（`backend/templates/icons/`）がGitにコミットされているか確認

## 注意事項

### 無料プランの制限

Renderの無料プランには以下の制限があります:

- **バックエンド（Web Service）**:
  - 15分間アクセスがないとスリープモード
  - 月750時間まで無料
  - 初回アクセス時にコールドスタート（30秒〜1分）

- **フロントエンド（Static Site）**:
  - 月100GBの帯域幅
  - CDN配信

### スリープ対策

バックエンドがスリープしないようにする方法:

1. **有料プランにアップグレード**（月$7〜）
2. **外部サービスで定期的にpingする**（例: UptimeRobot、cron-job.org）

### データベースのバックアップ

Supabaseで定期的にバックアップを取ることを推奨します。

## 自動デプロイ

GitHubにpushすると、Renderが自動的に検知して再デプロイします:

- `master`/`main`ブランチへのpush → 本番環境に自動デプロイ
- プルリクエスト → プレビュー環境を自動作成（有料プラン）

## カスタムドメインの設定

Renderでカスタムドメインを使用する場合:

1. Render Dashboard → Settings → Custom Domain
2. ドメインを入力（例: `identity-archive.example.com`）
3. DNS設定でCNAMEレコードを追加
4. SSL証明書が自動的に発行される

詳細: https://render.com/docs/custom-domains
