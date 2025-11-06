# 第五人格 ハンター戦績Bot

Discord Bot + Supabase で動作する第五人格のハンター戦績管理ツール

## 機能

### 📸 自動記録
- 試合結果のスクショをアップロードするだけで自動でデータ化
- OCRで自動解析（マップ、結果、サバイバーキャラ、牽制時間など）
- 手動入力（ハンター、特質、人格、Banキャラ）

### 📊 豊富な統計
- 全体統計（勝率、試合数）
- サバイバーキャラごとのピック数
- サバイバーキャラごとの平均牽制時間
- マップごとの勝率
- Banキャラごとの勝率
- 期間ごとの勝率

## セットアップ

### 1. 必要なアカウント

#### Discord Bot作成
1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」をクリック
3. Bot名を入力（例: 第五人格戦績Bot）
4. 左メニュー「Bot」→「Add Bot」
5. 「TOKEN」をコピー（後で使用）
6. 「Privileged Gateway Intents」で以下を有効化:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT
7. 左メニュー「OAuth2」→「URL Generator」
8. SCOPES: `bot`, `applications.commands`
9. BOT PERMISSIONS: `Send Messages`, `Read Messages`, `Attach Files`, `Embed Links`
10. 生成されたURLでサーバーに招待

#### Supabase プロジェクト作成
1. [Supabase](https://supabase.com) にアクセス
2. 「New Project」をクリック
3. プロジェクト名、データベースパスワードを設定
4. リージョンを選択（`Northeast Asia (Tokyo)` がおすすめ）
5. 作成完了後、Settings → API から以下を取得:
   - `URL`
   - `anon` キー

#### Supabase テーブル作成
SQL Editorで以下を実行:

```sql
-- matchesテーブル
CREATE TABLE matches (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    match_date TIMESTAMPTZ DEFAULT NOW(),
    result TEXT NOT NULL,
    match_duration TEXT,
    hunter_character TEXT,
    map_name TEXT NOT NULL,
    trait_used TEXT,
    persona TEXT,
    banned_characters TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- survivorsテーブル
CREATE TABLE survivors (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT REFERENCES matches(id) ON DELETE CASCADE,
    character_name TEXT NOT NULL,
    position INTEGER,
    kite_time TEXT,
    decode_progress TEXT,
    board_hits INTEGER DEFAULT 0,
    rescues INTEGER DEFAULT 0,
    heals INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_matches_user_id ON matches(user_id);
CREATE INDEX idx_matches_date ON matches(match_date DESC);
CREATE INDEX idx_matches_result ON matches(result);
CREATE INDEX idx_survivors_match ON survivors(match_id);
CREATE INDEX idx_survivors_character ON survivors(character_name);
```

### 2. ローカルでテスト

```bash
# 1. リポジトリをクローン（または作成）
git clone <your-repo>
cd identity-v-bot

# 2. 環境変数設定
cp .env.example .env
# .env を編集して取得したトークンとキーを設定

# 3. 依存パッケージインストール
pip install -r requirements.txt

# 4. Bot起動
python bot.py
```

### 3. Render にデプロイ

#### Renderアカウント作成
1. [Render](https://render.com) にアクセス
2. GitHubアカウントでサインアップ

#### Webサービス作成
1. Dashboard → 「New +」→「Web Service」
2. GitHubリポジトリを接続
3. 設定:
   - **Name**: `identityv-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Plan**: `Free`

#### 環境変数設定
Environment タブで以下を追加:
- `DISCORD_BOT_TOKEN`: Discordのトークン
- `SUPABASE_URL`: SupabaseのURL
- `SUPABASE_KEY`: Supabaseのanon key

#### デプロイ
「Create Web Service」をクリック

## 使い方

### コマンド一覧

#### 📸 記録
```
!record [ハンター] [特質] [人格] [Ban1] [Ban2]...
```
例:
```
!record 道化師 異常 中治り 機械技師 傭兵
```
※画像を添付すること

#### 📊 統計
```
!stats              # 全体統計
!survivor_stats     # サバイバーピック数
!kite_stats         # 平均牽制時間
!map_stats [ハンター] # マップ勝率
!ban_stats          # Ban勝率
!history [件数]     # 試合履歴
```

## トラブルシューティング

### OCRが正しく認識しない
- 画像の解像度を上げる
- スクショのタイミングを調整（結果画面が完全に表示されてから）
- 手動でデータを追加入力

### Botが起動しない
- `.env` の設定を確認
- Supabaseのテーブルが作成されているか確認
- ログを確認

## 今後の拡張予定
- [ ] Webダッシュボード
- [ ] グラフ表示
- [ ] データエクスポート（CSV/JSON）
- [ ] 詳細なフィルタリング機能
- [ ] 定期レポート機能

## ライセンス
MIT
