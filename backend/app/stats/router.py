from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from ..auth.dependencies import get_current_user
from .schemas import (
    OverallStats,
    SurvivorPickStats,
    SurvivorWinrateStats,
    SurvivorKiteStats,
    MapStats
)
from .service import stats_service

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overall", response_model=OverallStats)
async def get_overall_stats(
    current_user=Depends(get_current_user),
    hunter: Optional[str] = Query(None, description="ハンターで絞り込み"),
    persona: Optional[str] = Query(None, description="人格で絞り込み"),
    banned_characters: Optional[str] = Query(None, description="BANキャラで絞り込み（カンマ区切り）")
):
    """全体統計を取得"""
    banned_list = banned_characters.split(",") if banned_characters else None
    stats = stats_service.get_overall_stats(current_user.id, hunter, persona, banned_list)
    return OverallStats(**stats)


@router.get("/survivors/picks", response_model=List[SurvivorPickStats])
async def get_survivor_picks(
    current_user=Depends(get_current_user),
    hunter: Optional[str] = Query(None, description="ハンターで絞り込み"),
    limit: Optional[int] = Query(None, description="集計する試合数"),
    persona: Optional[str] = Query(None, description="人格で絞り込み"),
    banned_characters: Optional[str] = Query(None, description="BANキャラで絞り込み（カンマ区切り）")
):
    """サバイバーピック数を取得"""
    banned_list = banned_characters.split(",") if banned_characters else None
    data = stats_service.get_survivor_pick_rates(current_user.id, hunter, limit, persona, banned_list)
    return [SurvivorPickStats(**d) for d in data]


@router.get("/survivors/winrate", response_model=List[SurvivorWinrateStats])
async def get_survivor_winrate(
    current_user=Depends(get_current_user),
    hunter: Optional[str] = Query(None, description="ハンターで絞り込み"),
    limit: Optional[int] = Query(None, description="集計する試合数"),
    persona: Optional[str] = Query(None, description="人格で絞り込み"),
    banned_characters: Optional[str] = Query(None, description="BANキャラで絞り込み（カンマ区切り）")
):
    """サバイバー勝率を取得"""
    banned_list = banned_characters.split(",") if banned_characters else None
    data = stats_service.get_survivor_winrate(current_user.id, hunter, limit, persona, banned_list)
    return [SurvivorWinrateStats(**d) for d in data]


@router.get("/survivors/kite", response_model=List[SurvivorKiteStats])
async def get_survivor_kite(
    current_user=Depends(get_current_user),
    hunter: Optional[str] = Query(None, description="ハンターで絞り込み"),
    limit: Optional[int] = Query(None, description="集計する試合数"),
    persona: Optional[str] = Query(None, description="人格で絞り込み"),
    banned_characters: Optional[str] = Query(None, description="BANキャラで絞り込み（カンマ区切り）")
):
    """サバイバー平均牽制時間を取得"""
    banned_list = banned_characters.split(",") if banned_characters else None
    data = stats_service.get_avg_kite_time(current_user.id, hunter, limit, persona, banned_list)
    return [SurvivorKiteStats(**d) for d in data]


@router.get("/maps", response_model=List[MapStats])
async def get_map_stats(
    current_user=Depends(get_current_user),
    hunter: Optional[str] = Query(None, description="ハンターで絞り込み"),
    limit: Optional[int] = Query(None, description="集計する試合数"),
    persona: Optional[str] = Query(None, description="人格で絞り込み"),
    banned_characters: Optional[str] = Query(None, description="BANキャラで絞り込み（カンマ区切り）")
):
    """マップ勝率を取得"""
    banned_list = banned_characters.split(",") if banned_characters else None
    data = stats_service.get_map_stats(current_user.id, hunter, limit, persona, banned_list)
    return [MapStats(**d) for d in data]


@router.get("/personas", response_model=List[str])
async def get_recent_personas(
    current_user=Depends(get_current_user)
):
    """最近使用した人格リストを取得"""
    return stats_service.get_recent_personas(current_user.id)
