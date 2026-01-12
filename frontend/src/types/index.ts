// ユーザー
export interface User {
  id: string;
  email?: string;
  name?: string;
  avatar_url?: string;
}

// サバイバーデータ
export interface SurvivorData {
  character_name?: string;
  position?: number;
  kite_time?: string;
  decode_progress?: string;
  board_hits: number;
  rescues: number;
  heals: number;
}

export interface SurvivorResponse extends SurvivorData {
  id: number;
  match_id: number;
}

// 試合データ
export interface MatchCreate {
  result: string;
  map_name: string;
  match_duration?: string;
  hunter_character?: string;
  trait_used?: string;
  persona?: string;
  banned_characters?: string[];
  played_at?: string;
  survivors: SurvivorData[];
}

// エイリアス
export type MatchCreateRequest = MatchCreate;

export interface MatchResponse {
  id: number;
  user_id: string;
  result: string;
  map_name: string;
  match_duration?: string;
  hunter_character?: string;
  trait_used?: string;
  persona?: string;
  banned_characters: string[];
  played_at?: string;
  match_date: string;
  created_at: string;
  survivors: SurvivorResponse[];
}

// OCR解析結果
export interface AnalyzeResponse {
  result?: string;
  map_name?: string;
  duration?: string;
  hunter_character?: string;
  played_at?: string;
  survivors: SurvivorData[];
}

// 統計
export interface OverallStats {
  total_matches: number;
  wins: number;
  draws: number;
  losses: number;
  win_rate: string;
}

export interface SurvivorPickStats {
  character: string;
  picks: number;
}

export interface SurvivorWinrateStats {
  character: string;
  total: number;
  wins: number;
  draws: number;
  losses: number;
  win_rate: number;
  win_rate_str: string;
}

export interface SurvivorKiteStats {
  character: string;
  avg_kite_time: string;
  samples: number;
}

export interface MapStats {
  map_name: string;
  total: number;
  wins: number;
  draws: number;
  losses: number;
  win_rate: string;
}

// 認証
export interface LoginResponse {
  url: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
}

// デバイスレイアウト
export interface IconPosition {
  x_ratio: number;
  y_ratio: number;
  size_ratio: number;
}

export interface DeviceLayout {
  id: string;
  aspect_ratio: number;
  screen_width: number;
  screen_height: number;
  icon_positions: IconPosition[];
  vote_count: number;
  created_at: string;
  updated_at: string;
}

export interface DeviceLayoutCreate {
  aspect_ratio: number;
  screen_width: number;
  screen_height: number;
  icon_positions: IconPosition[];
}
