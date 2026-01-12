-- デバイスレイアウトテーブルの作成
CREATE TABLE IF NOT EXISTS device_layouts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  aspect_ratio DECIMAL(6,4) NOT NULL,
  screen_width INT NOT NULL,
  screen_height INT NOT NULL,
  icon_positions JSONB NOT NULL,  -- [{x_ratio: 0.29, y_ratio: 0.29, size_ratio: 0.04}, ...]
  vote_count INT DEFAULT 1 CHECK (vote_count > 0),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- アスペクト比で高速検索できるようにインデックス作成
CREATE INDEX IF NOT EXISTS idx_device_layouts_aspect_ratio ON device_layouts(aspect_ratio);

-- 投票数でソートできるようにインデックス作成
CREATE INDEX IF NOT EXISTS idx_device_layouts_vote_count ON device_layouts(vote_count DESC);

-- RLS (Row Level Security) を有効化
ALTER TABLE device_layouts ENABLE ROW LEVEL SECURITY;

-- 全ユーザーが読み取り可能
CREATE POLICY "Anyone can read device layouts"
  ON device_layouts
  FOR SELECT
  USING (true);

-- 認証済みユーザーのみが挿入・更新可能
CREATE POLICY "Authenticated users can insert device layouts"
  ON device_layouts
  FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Authenticated users can update device layouts"
  ON device_layouts
  FOR UPDATE
  USING (auth.uid() IS NOT NULL);
