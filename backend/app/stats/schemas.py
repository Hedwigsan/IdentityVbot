from pydantic import BaseModel
from typing import List, Optional


class OverallStats(BaseModel):
    """全体統計"""
    total_matches: int
    wins: int
    draws: int
    losses: int
    win_rate: str


class SurvivorPickStats(BaseModel):
    """サバイバーピック統計"""
    character: str
    picks: int


class SurvivorWinrateStats(BaseModel):
    """サバイバー勝率統計"""
    character: str
    total: int
    wins: int
    draws: int
    losses: int
    win_rate: float
    win_rate_str: str


class SurvivorKiteStats(BaseModel):
    """サバイバー牽制時間統計"""
    character: str
    avg_kite_time: str
    samples: int


class MapStats(BaseModel):
    """マップ統計"""
    map_name: str
    total: int
    wins: int
    draws: int
    losses: int
    win_rate: str
