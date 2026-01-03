from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SurvivorData(BaseModel):
    """サバイバーデータ"""
    character_name: Optional[str] = None
    position: Optional[int] = None
    kite_time: Optional[str] = None
    decode_progress: Optional[str] = None
    board_hits: int = 0
    rescues: int = 0
    heals: int = 0


class SurvivorResponse(SurvivorData):
    """サバイバーレスポンス"""
    id: int
    match_id: int


class MatchCreate(BaseModel):
    """試合作成リクエスト"""
    result: str
    map_name: str
    match_duration: Optional[str] = None
    hunter_character: Optional[str] = None
    trait_used: Optional[str] = None
    persona: Optional[str] = None
    banned_characters: List[str] = []
    played_at: Optional[datetime] = None
    survivors: List[SurvivorData] = []


class MatchResponse(BaseModel):
    """試合レスポンス"""
    id: int
    user_id: str
    result: str
    map_name: str
    match_duration: Optional[str]
    hunter_character: Optional[str]
    trait_used: Optional[str]
    persona: Optional[str]
    banned_characters: List[str]
    played_at: Optional[datetime]
    match_date: datetime
    created_at: datetime
    survivors: List[SurvivorResponse] = []


class MatchListResponse(BaseModel):
    """試合一覧レスポンス"""
    matches: List[MatchResponse]
    total: int


class MatchFilters(BaseModel):
    """試合フィルター"""
    hunter: Optional[str] = None
    trait: Optional[str] = None
    map_name: Optional[str] = None
    persona: Optional[str] = None
    limit: Optional[int] = None


class AnalyzeResponse(BaseModel):
    """OCR解析結果"""
    result: Optional[str] = None
    map_name: Optional[str] = None
    duration: Optional[str] = None
    hunter_character: Optional[str] = None
    played_at: Optional[str] = None
    survivors: List[SurvivorData] = []
