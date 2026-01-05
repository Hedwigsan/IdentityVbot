# Identity Archive

第五人格（Identity V）ハンター戦績管理システム

試合結果のスクリーンショットをアップロードするだけで、OCRで自動解析してデータベースに保存。統計データで戦績を可視化します。

## 特徴

### 自動記録・OCR解析
- **試合結果のスクショをアップロードするだけ**で自動でデータ化
- **OCRで自動解析**: マップ、試合結果、試合時間、サバイバーキャラ、牽制時間、解読進捗など
- **ハンター自動検出**: 画像認識でハンターを自動識別

### 豊富な統計・分析機能
- **全体統計**: 勝率、総試合数
- **データ絞り込み**: ハンター、マップ、結果で条件指定
- **サバイバー統計**: ピック数、勝率
- **牽制時間分析**: サバイバーごとの平均牽制時間（ハンター別も可）
- **マップ勝率**: マップごとの戦績（ハンター別も可）
- **試合履歴**: 詳細データの閲覧・削除

---

## 技術スタック

### バックエンド
- **FastAPI** (Python 3.11+)
- **Supabase** (PostgreSQL + 認証)
- **yomitoku / easyocr** (OCR処理)
- **OpenCV** (画像処理・テンプレートマッチング)

### フロントエンド
- **React 18** + TypeScript
- **Vite** (ビルドツール)
- **Chakra UI** (UIライブラリ)
- **TanStack Query** (データフェッチ)
- **React Router** (ルーティング)

---

## プロジェクト構成

```
IdentityArchive/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPIエントリーポイント
│   │   ├── config.py            # 環境変数設定
│   │   ├── database.py          # Supabase接続
│   │   ├── auth/                # 認証（Google OAuth）
│   │   ├── matches/             # 試合CRUD
│   │   ├── stats/               # 統計
│   │   ├── ocr/                 # OCR処理
│   │   └── master_data.py       # マスターデータ
│   ├── templates/icons/         # アイコンテンプレート
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # Reactコンポーネント
│   │   ├── pages/               # ページコンポーネント
│   │   ├── hooks/               # カスタムフック
│   │   ├── services/            # API通信
│   │   └── types/               # 型定義
│   └── package.json
└── templates/icons/             # OCRテンプレート画像
```

---

## セットアップ

### 必要なもの
- Python 3.11以上
- Node.js 18以上
- Supabaseアカウント

### 1. Supabase設定

1. [Supabase](https://supabase.com)でプロジェクト作成
2. SQL Editorで以下を実行:

```sql
-- matchesテーブル
CREATE TABLE matches (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
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

-- RLS設定
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE survivors ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own matches" ON matches
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own survivors" ON survivors
    FOR ALL USING (
        EXISTS (SELECT 1 FROM matches WHERE matches.id = survivors.match_id AND matches.user_id = auth.uid())
    );

-- インデックス
CREATE INDEX idx_matches_user_id ON matches(user_id);
CREATE INDEX idx_matches_date ON matches(match_date DESC);
CREATE INDEX idx_survivors_match ON survivors(match_id);
```

3. Authentication → Providers で Google OAuth を設定

### 2. バックエンド

```bash
cd backend

# 仮想環境作成
python -m venv venv

# Windows PowerShell: 仮想環境アクティベート
.\venv\Scripts\Activate.ps1

# Linux/Mac: 仮想環境アクティベート
source venv/bin/activate

# 依存パッケージ
pip install -r requirements.txt

# 環境変数 (.env)
SUPABASE_URL=<SupabaseのURL>
SUPABASE_KEY=<Supabaseのservice_roleキー>
FRONTEND_URL=http://localhost:5173

# 起動（シンプル版 - システムまたは仮想環境のPythonを使用）
python -m uvicorn app.main:app --reload

# バックグラウンド起動の場合
python -m uvicorn app.main:app --reload &
```

### 3. フロントエンド

```bash
cd frontend

# 依存パッケージ
npm install

# 環境変数 (.env)
VITE_API_URL=http://localhost:8000

# 開発サーバー起動
npm run dev
```

### 4. アクセス

- フロントエンド: http://localhost:5173
- バックエンドAPI: http://localhost:8000
- APIドキュメント: http://localhost:8000/docs

---

## API エンドポイント

### 認証
| メソッド | パス | 説明 |
|----------|------|------|
| POST | `/auth/login` | Google OAuth開始 |
| POST | `/auth/token` | トークン交換 |
| GET | `/auth/me` | 現在のユーザー情報 |
| POST | `/auth/logout` | ログアウト |

### 試合記録
| メソッド | パス | 説明 |
|----------|------|------|
| POST | `/api/matches/analyze` | 画像アップロード→OCR解析 |
| POST | `/api/matches` | 試合データ保存 |
| GET | `/api/matches` | 試合一覧（フィルタ対応） |
| GET | `/api/matches/{id}` | 試合詳細 |
| DELETE | `/api/matches/{id}` | 試合削除 |

### 統計
| メソッド | パス | 説明 |
|----------|------|------|
| GET | `/api/stats/overall` | 全体統計 |
| GET | `/api/stats/survivors/picks` | サバイバーピック数 |
| GET | `/api/stats/survivors/winrate` | サバイバー勝率 |
| GET | `/api/stats/survivors/kite` | 平均牽制時間 |
| GET | `/api/stats/maps` | マップ勝率 |

### マスターデータ
| メソッド | パス | 説明 |
|----------|------|------|
| GET | `/api/master/hunters` | ハンター一覧 |
| GET | `/api/master/survivors` | サバイバー一覧 |
| GET | `/api/master/traits` | 特質一覧 |
| GET | `/api/master/maps` | マップ一覧 |

---

## ライセンス

MIT License
