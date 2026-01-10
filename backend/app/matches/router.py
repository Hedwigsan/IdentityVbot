import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ..auth.dependencies import get_current_user
from .schemas import MatchCreate, MatchResponse, MatchListResponse, SurvivorResponse
from .service import match_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/matches", tags=["matches"])


def _format_match_response(match_data: dict) -> MatchResponse:
    """試合データをレスポンス形式に変換"""
    survivors = []
    for s in match_data.get("survivors", []):
        survivors.append(SurvivorResponse(
            id=s["id"],
            match_id=s["match_id"],
            character_name=s.get("character_name"),
            position=s.get("position"),
            kite_time=s.get("kite_time"),
            decode_progress=s.get("decode_progress"),
            board_hits=s.get("board_hits", 0),
            rescues=s.get("rescues", 0),
            heals=s.get("heals", 0)
        ))

    return MatchResponse(
        id=match_data["id"],
        user_id=match_data["user_id"],
        result=match_data["result"],
        map_name=match_data["map_name"],
        match_duration=match_data.get("match_duration"),
        hunter_character=match_data.get("hunter_character"),
        trait_used=match_data.get("trait_used"),
        persona=match_data.get("persona"),
        banned_characters=match_data.get("banned_characters", []),
        played_at=match_data.get("played_at"),
        match_date=match_data["match_date"],
        created_at=match_data["created_at"],
        survivors=survivors
    )


@router.post("", response_model=MatchResponse)
async def create_match(match_data: MatchCreate, current_user=Depends(get_current_user)):
    """試合データを保存"""
    try:
        result = match_service.create_match(current_user.id, match_data)
        # 保存後に再取得してサバイバー情報も含める
        full_match = match_service.get_match(current_user.id, result["id"])
        return _format_match_response(full_match)

    except Exception as e:
        logger.error(f"試合保存エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="試合データの保存に失敗しました")


@router.get("", response_model=MatchListResponse)
async def get_matches(
    current_user=Depends(get_current_user),
    hunter: Optional[str] = Query(None),
    trait: Optional[str] = Query(None),
    map_name: Optional[str] = Query(None),
    persona: Optional[str] = Query(None),
    result: Optional[str] = Query(None),
    limit: Optional[int] = Query(None)
):
    """試合一覧を取得"""
    matches = match_service.get_matches(
        current_user.id,
        hunter=hunter,
        trait=trait,
        map_name=map_name,
        persona=persona,
        result=result,
        limit=limit
    )

    return MatchListResponse(
        matches=[_format_match_response(m) for m in matches],
        total=len(matches)
    )


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, current_user=Depends(get_current_user)):
    """試合詳細を取得"""
    match = match_service.get_match(current_user.id, match_id)

    if not match:
        raise HTTPException(status_code=404, detail="試合が見つかりません")

    return _format_match_response(match)


@router.delete("/{match_id}")
async def delete_match(match_id: int, current_user=Depends(get_current_user)):
    """試合を削除"""
    success = match_service.delete_match(current_user.id, match_id)

    if not success:
        raise HTTPException(status_code=404, detail="試合が見つかりません")

    return {"message": "試合を削除しました"}
