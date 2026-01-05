# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

第五人格（Identity V）のハンター戦績を管理するWebアプリケーションです。試合結果のスクリーンショットをOCR解析してSupabaseデータベースに保存し、統計情報を提供します。

## 開発コマンド

### バックエンド（FastAPI）

```bash
cd backend

# 起動（シンプル版 - システムのPython使用）
python -m uvicorn app.main:app --reload

# バックグラウンド起動（推奨）
python -m uvicorn app.main:app --reload &

# PowerShellで仮想環境を明示的に使う場合
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload

# 依存パッケージインストール
pip install -r requirements.txt
```

### フロントエンド（React + Vite）

```bash
cd frontend

# 開発サーバー起動
npm run dev

# ビルド
npm run build

# 型チェック
npx tsc --noEmit
```

### 環境変数

**backend/.env**:
```
SUPABASE_URL=<SupabaseプロジェクトURL>
SUPABASE_KEY=<service_roleキー>
FRONTEND_URL=http://localhost:5173
```

**frontend/.env**:
```
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=<SupabaseプロジェクトURL>
VITE_SUPABASE_ANON_KEY=<Supabaseのanonキー>
```

### ネットワークアクセス設定（モバイル実機テスト用）

スマートフォンなどの実機でテストする場合：

1. **バックエンド**: `--host 0.0.0.0`オプションで起動
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0
   ```

2. **フロントエンド**: `vite.config.ts`で`host: true`が設定済み（全ネットワークインターフェースでリッスン）

3. **環境変数**: `frontend/.env`の`VITE_API_URL`をPCのIPアドレスに変更
   ```
   VITE_API_URL=http://192.168.x.x:8000
   ```

4. **CORS設定**: `backend/app/main.py`のCORS allow_originsにネットワークIPを追加済み

5. **Supabase設定**: Supabase Dashboard → Authentication → URL Configuration で、ネットワークIPのリダイレクトURLを追加
   ```
   http://192.168.x.x:5173/auth/callback
   ```

6. **注意**: 環境変数を変更した場合、Viteサーバーを再起動する必要があります

## アーキテクチャ

### バックエンド構成（FastAPI）

```
backend/app/
├── main.py          # エントリーポイント、CORS設定、ルーター登録
├── config.py        # Pydantic Settings（環境変数）
├── database.py      # Supabaseクライアント（シングルトン）
├── auth/
│   ├── router.py    # /auth/* エンドポイント（Google OAuth）
│   └── dependencies.py  # get_current_user（JWT検証）
├── matches/
│   ├── router.py    # /api/matches/* CRUD
│   ├── service.py   # ビジネスロジック
│   └── schemas.py   # Pydanticモデル
├── stats/
│   ├── router.py    # /api/stats/* 統計エンドポイント
│   ├── service.py   # 統計計算ロジック
│   └── schemas.py   # 統計レスポンスモデル
├── ocr/
│   ├── router.py    # /api/matches/analyze 画像解析
│   └── processor.py # OCR処理（yomitoku/easyocr + テンプレートマッチング）
├── master_data.py   # ハンター・サバイバー・特質・マップ定義
└── master_router.py # /api/master/* マスターデータAPI
```

### フロントエンド構成（React）

```
frontend/src/
├── main.tsx         # エントリー（Provider設定）
├── App.tsx          # ルーティング、PrivateRoute
├── pages/           # ページコンポーネント
│   ├── LoginPage.tsx
│   ├── AuthCallbackPage.tsx  # OAuth callback処理
│   ├── RecordPage.tsx        # 試合記録（2ステップ: upload→edit）
│   ├── StatsPage.tsx         # 統計（タブ切り替え）
│   ├── HistoryPage.tsx       # 履歴一覧・詳細・削除
│   └── SettingsPage.tsx
├── components/
│   ├── common/Header.tsx
│   ├── record/
│   │   ├── ImageUploader.tsx  # ドラッグ&ドロップ画像アップロード
│   │   └── MatchEditor.tsx    # OCR結果編集フォーム
│   └── stats/                 # 統計表示コンポーネント群
├── hooks/useAuth.ts   # 認証状態管理
├── services/api.ts    # Axiosベースのapi client
└── types/index.ts     # 全型定義
```

### データフロー

```
画像アップロード (RecordPage)
  ↓
POST /api/matches/analyze
  ↓
ocr/processor.py: process_image()
  ├─ yomitokuでOCR実行（テキスト抽出）
  └─ cv2.matchTemplateでアイコン認識
  ↓
AnalyzeResponse（OCR結果）
  ↓
MatchEditor（ユーザーが確認・編集）
  ↓
POST /api/matches（保存）
  ├─ matchesテーブル
  └─ survivorsテーブル
```

## OCR処理の仕組み

**OCRエンジン**: yomitoku 0.10.1（メイン）、easyocr（フォールバック）

**2段階処理**:
1. **テキストOCR**: 勝敗、マップ名、試合時間、試合日時を検出
2. **アイコン認識**: テンプレートマッチング（cv2.matchTemplate）
   - テンプレート: `backend/templates/icons/hunters/`, `survivors/`
   - 複数スケール（0.5x～1.5x）で試行、閾値40%以上

**座標設定**:
- アイコン位置は画面サイズの相対比率で固定
- 勝利時: ハンター→サバイバー1～4
- 敗北時: サバイバー1～4→ハンター
- 位置定義: `ocr/processor.py`の`layout`辞書

## データベーススキーマ

**matchesテーブル**:
- `user_id`: UUID（Supabase Auth）
- `result`: 勝利/敗北/引き分け
- `map_name`, `hunter_character`, `trait_used`, `persona`, `banned_characters`
- `played_at`: 実際の試合日時（OCR抽出）
- `match_date`: 記録日時

**survivorsテーブル**:
- `match_id`で紐付け
- `character_name`, `position`, `kite_time`, `decode_progress`, `rescues`, `heals`, `board_hits`

## 認証フロー

フロントエンドはSupabase Clientを直接使用してOAuth認証を実行：

1. `useAuth.ts`: `supabase.auth.signInWithOAuth({ provider: 'google' })`を呼び出し
2. `redirectTo`は`window.location.origin + '/auth/callback'`で動的に生成
3. Googleログイン後、Supabaseが`/auth/callback`にリダイレクト
4. `AuthCallbackPage.tsx`: `supabase.auth.getSession()`でセッション取得
5. セッションから`access_token`を取得し`localStorage`に保存
6. 以降のAPI呼び出し: `Authorization: Bearer <token>` ヘッダーで認証

**重要**: Supabase DashboardのAuthentication → URL ConfigurationでリダイレクトURLを設定すること
- 開発時: `http://localhost:5173/auth/callback`
- 実機テスト時: `http://[PCのIP]:5173/auth/callback`も追加

## 開発時の注意点

### バックエンド

- `SUPABASE_KEY`は**service_roleキー**を使用（RLS有効時も動作）
- OCR処理は重いため`run_in_executor`で非同期実行
- yomitokuはイベントループ衝突時にnest_asyncioで対処済み

### フロントエンド

- TanStack Queryのキャッシュ: `queryKey`でキャッシュが決まる
- 認証状態は`useAuth`フックで管理、`localStorage`にトークン保存
- Chakra UIのカラーモード: `useColorModeValue`でライト/ダーク対応
- レスポンシブデザイン: Chakra UIの`display={{ base: '...', md: '...' }}`でブレークポイント対応
  - `base`: モバイル（0px～）
  - `md`: タブレット以上（768px～）
  - Header.tsxではスマホ用にDrawerメニュー、タブレット以上で通常ナビゲーションを表示
- フォント: Open Sans（Google Fonts経由、`theme.ts`で設定）
- 新しいChakra UIコンポーネントを使用する場合、`@chakra-ui/icons`などの追加パッケージが必要な場合がある

## Conversation Guidelines

常に日本語で会話する

## 指示について

指示をする側も人間で間違うことがあります。こちらの指示を批判的に見て、間違っていることは指摘してください。指示された内容についてそのまま鵜呑みにせず、背景や説明不足だと感じたら確認をとってください。指示された案以外にも他に案がないかも考えて、良さそうな案があれば提案してください。

## 実装指針

- 段階的に進める: 一度に全てを変更せず、小さな変更を積み重ねる
- 複数のタスクを同時並行で進めない
- エラーは解決してから次へ進む
- エラーを無視して次のステップに進まない
- 指示にない機能を勝手に追加しない
- 周囲の似た実装を探し、それを参考にする
