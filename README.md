# 第五人格 ハンター戦績Bot

Discord Bot + Supabase で動作する第五人格（Identity V）のハンター戦績管理ツール

試合結果のスクリーンショットをアップロードするだけで、OCRで自動解析してデータベースに保存。統計データで戦績を可視化します。

## 特徴

### 📸 自動記録・OCR解析
- **試合結果のスクショをアップロードするだけ**で自動でデータ化
- **OCRで自動解析**: マップ、試合結果、試合時間、サバイバーキャラ、牽制時間、解読進捗など
- **ハンター自動検出**: 画像認識でハンターを自動識別
- **複数画像対応**: 一度に複数の試合を記録可能
- **モバイル対応UI**: スマホでも使いやすい選択メニュー形式

### 📊 豊富な統計・分析機能
- **全体統計**: 勝率、総試合数
- **データ絞り込み**: ハンター、特質、マップで条件指定
- **サバイバー統計**: ピック数、勝率
- **牽制時間分析**: サバイバーごとの平均牽制時間（ハンター別も可）
- **マップ勝率**: マップごとの戦績（ハンター別も可）
- **試合履歴**: 最新5戦の詳細データ
- **件数選択**: 最新10/50/100戦、または全期間から選択可能

---

## 🚀 使い方（一般ユーザー向け）

### 1. Botをサーバーに招待

以下の招待リンクからBotをあなたのDiscordサーバーに追加してください：

**[Botを招待する](<招待リンク>)**

または、サーバー管理者に招待を依頼してください。

### 2. 使い方

#### 基本的な流れ

1. **試合を終える**
2. **結果画面のスクリーンショットを撮る**
3. **Discordで `!record` コマンドと画像を送信**
4. **選択メニューで特質・Ban・人格を入力**
5. **統計コマンドでデータを確認**

#### コマンド一覧

##### 📸 試合記録
```
!record (または !r)
```
- 画像を添付必須（複数枚可）
- 画像解析中に選択メニューで入力可能
- ハンターは自動検出
- 特質・Ban（最大3人）・人格を選択

**使用例**:
1. `!record` と入力して画像を添付
2. 特質を選択（リッスン、異常など）
3. Banキャラを選択（前半・後半リストから最大3人）
4. 「確定して人格を入力」ボタンをクリック
5. 人格を入力（例: 中治り、左右など）

##### 📊 データ閲覧
```
!view (または !v)
```
- 条件を絞り込んでデータを表示
- ハンター、特質、マップで絞り込み
- 表示件数を選択（10/50/100/全て）

##### 📈 統計コマンド

```
!stats (または !s)
全体統計（勝率、総試合数）

!survivor_stats (または !ss)
サバイバーキャラごとのピック数
→ 件数選択ボタンで集計範囲を指定

!winrate_stats (または !ws)
サバイバーキャラごとの勝率
→ 件数選択ボタンで集計範囲を指定
→ 勝率で色分け表示（🟢60%以上、🟡40-60%、🔴40%未満）

!kite_stats (または !ks)
サバイバーごとの平均牽制時間
→ ハンター選択 → 件数選択で集計範囲を指定

!map_stats (または !ms)
マップごとの勝率
→ ハンター選択 → 件数選択で集計範囲を指定

!history (または !h)
最新5戦の試合履歴（固定）
→ サバイバー全員の名前を表示
```

##### ℹ️ その他
```
!help
コマンド一覧を表示
```

#### 統計確認の例

```
!winrate_stats
↓
「📊 最新50戦」ボタンをクリック
↓
📊 サバイバーキャラごとの勝率 (最新50戦)
1. 医師: 🟢 75.0% (6勝2敗 / 8戦)
2. 祭司: 🟡 50.0% (3勝3敗 / 6戦)
...
```

### よくある質問

**Q: OCRが正しく認識しないことがあります**
- できるだけ高解像度でスクショを撮ってください
- 結果画面のアニメーションが完全に終わってから撮影してください
- 画面全体を撮影し、部分的な切り取りは避けてください

**Q: データは他の人と共有されますか？**
- いいえ、あなたのデータはあなたのDiscordアカウントにのみ紐付けられ、他のユーザーからは見えません

**Q: 過去の試合を削除できますか？**
- 現在は削除機能はありません（将来的に対応予定）

---

## 🛠️ セットアップ（開発者・ホスティング担当者向け）

このセクションは、Botを自分でホスティングする場合の手順です。一般ユーザーは読む必要はありません。

### 必要なもの

- Python 3.9以上
- Discordアカウント
- Supabaseアカウント（無料プラン可）
- サーバー環境（VPS、クラウドサービスなど）

### 1. Discord Bot作成

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」をクリック
3. Bot名を入力（例: 第五人格戦績Bot）
4. 左メニュー「Bot」→「Add Bot」
5. 「TOKEN」をコピー（後で使用）
6. 「Privileged Gateway Intents」で以下を有効化:
   - ✅ MESSAGE CONTENT INTENT
7. 左メニュー「OAuth2」→「URL Generator」
8. SCOPES: `bot`
9. BOT PERMISSIONS:
   - `Send Messages`
   - `Read Messages/View Channels`
   - `Attach Files`
   - `Embed Links`
   - `Read Message History`
10. 生成されたURLを保存（ユーザーへの招待リンクとして使用）

### 2. Supabase プロジェクト作成

1. [Supabase](https://supabase.com) にアクセスしてアカウント作成
2. 「New Project」をクリック
3. プロジェクト名、データベースパスワードを設定
4. リージョンを選択（`Northeast Asia (Tokyo)` 推奨）
5. 作成完了後、Settings → API から以下を取得:
   - `URL`
   - `service_role` キー（**重要**: anonキーではなくservice_roleキー）

### 3. Supabase テーブル作成

SQL Editorで以下のSQLを実行:

```sql
-- matchesテーブル
CREATE TABLE matches (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    match_date TIMESTAMPTZ DEFAULT NOW(),
    played_at TIMESTAMPTZ,
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
CREATE INDEX idx_matches_played_at ON matches(played_at DESC);
CREATE INDEX idx_matches_result ON matches(result);
CREATE INDEX idx_survivors_match ON survivors(match_id);
CREATE INDEX idx_survivors_character ON survivors(character_name);
```

**RLSを有効化する場合**（オプション）:
```sql
-- RLSを有効化
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE survivors ENABLE ROW LEVEL SECURITY;

-- service_roleキーを使用する場合、ポリシーは不要
```

### 4. ローカルセットアップ（開発・テスト用）

```bash
# 1. リポジトリをクローン
git clone <your-repo>
cd IdentityArchive

# 2. 仮想環境作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存パッケージインストール
pip install -r requirements.txt

# 4. 環境変数設定
# .env ファイルを作成して以下を記入:
DISCORD_BOT_TOKEN=<DiscordのBotトークン>
SUPABASE_URL=<SupabaseのURL>
SUPABASE_KEY=<Supabaseのservice_roleキー>

# 5. Bot起動
python bot.py
```

成功すると以下のメッセージが表示されます：
```
✅ <BotName> がログインしました！
Bot ID: <ID>
---------------------------
```

### 5. サーバーでの常時稼働

#### systemd（Linux）を使用する場合

`/etc/systemd/system/identityv-bot.service` を作成:

```ini
[Unit]
Description=Identity V Hunter Stats Discord Bot
After=network.target

[Service]
Type=simple
User=<ユーザー名>
WorkingDirectory=/path/to/IdentityArchive
Environment="PATH=/path/to/IdentityArchive/venv/bin"
ExecStart=/path/to/IdentityArchive/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

起動:
```bash
sudo systemctl daemon-reload
sudo systemctl enable identityv-bot
sudo systemctl start identityv-bot
sudo systemctl status identityv-bot
```

#### tmux/screenを使用する場合

```bash
# tmuxセッション作成
tmux new -s identityv-bot

# Bot起動
cd /path/to/IdentityArchive
source venv/bin/activate
python bot.py

# デタッチ: Ctrl+B → D
# 再アタッチ: tmux attach -t identityv-bot
```

#### クラウドサービス（Render、Railway等）を使用する場合

1. GitHubリポジトリにプッシュ
2. クラウドサービスでプロジェクトを接続
3. 環境変数を設定:
   - `DISCORD_BOT_TOKEN`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
4. ビルドコマンド: `pip install -r requirements.txt`
5. 起動コマンド: `python bot.py`
6. デプロイ

### トラブルシューティング

#### Botが応答しない
- `.env` ファイルの設定を確認
- `MESSAGE CONTENT INTENT` が有効か確認
- Botがサーバーに招待されているか確認
- コンソールのエラーログを確認

#### データが保存されない
- Supabaseのテーブルが正しく作成されているか確認
- `SUPABASE_KEY` が**service_roleキー**であることを確認（anonキーではない）
- RLSが有効化されている場合、service_roleキーを使用

#### メモリ不足
- サーバーのメモリを増やす
- 不要なプロセスを終了する

---

## 技術スタック

- **言語**: Python 3.9+
- **ライブラリ**:
  - `discord.py`: Discord Bot フレームワーク
  - `yomitoku`: 日本語OCRライブラリ
  - `opencv-python`: 画像処理
  - `supabase`: Supabaseクライアント
  - `python-dotenv`: 環境変数管理
- **データベース**: Supabase (PostgreSQL)
- **ホスティング**: VPS、クラウドサービス（Render、Railway等）

## プロジェクト構成

```
IdentityArchive/
├── bot.py              # Discord Bot メインファイル
├── database.py         # Supabaseデータベース操作
├── ocr_processor.py    # OCR画像解析処理
├── requirements.txt    # 依存パッケージ
├── .env               # 環境変数（要作成、.gitignoreに追加済み）
├── .gitignore
└── README.md
```

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します！バグ報告や機能要望はIssueでお願いします。

---

## 連絡先

問題や質問がある場合は、Issueを作成するか、Discordサーバーでお問い合わせください。
