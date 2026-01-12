from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ..database import get_supabase
from ..auth.dependencies import get_current_user
from .schemas import DeviceLayoutCreate, DeviceLayoutResponse, DeviceLayoutVoteRequest
from .service import LayoutService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/layouts", tags=["layouts"])


@router.get("/best", response_model=Optional[DeviceLayoutResponse])
async def get_best_layout(
    aspect_ratio: float = Query(..., description="画像のアスペクト比"),
    tolerance: float = Query(0.05, description="許容範囲（デフォルト: ±0.05）"),
    supabase=Depends(get_supabase)
):
    """
    指定されたアスペクト比に最も近いレイアウトを取得

    - **aspect_ratio**: 検索するアスペクト比（例: 2.1695）
    - **tolerance**: 許容範囲（デフォルト: ±0.05）

    投票数が最も多いレイアウトを返します。
    見つからない場合はnullを返します。
    """
    service = LayoutService(supabase)
    layout = service.get_best_layout(aspect_ratio, tolerance)
    return layout


@router.post("/save", response_model=DeviceLayoutResponse)
async def save_layout(
    layout: DeviceLayoutCreate,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    """
    レイアウトを保存（類似レイアウトがあれば投票、なければ新規作成）

    認証が必要です。

    - 同じアスペクト比（±0.05）と位置（±0.01）のレイアウトがあれば投票
    - なければ新規作成
    """
    service = LayoutService(supabase)
    try:
        saved_layout = service.save_layout(layout)
        return saved_layout
    except Exception as e:
        logger.error(f"Error saving layout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vote", response_model=DeviceLayoutResponse)
async def vote_layout(
    vote_request: DeviceLayoutVoteRequest,
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    """
    既存のレイアウトに投票

    認証が必要です。

    - **layout_id**: 投票するレイアウトのID
    """
    service = LayoutService(supabase)
    try:
        updated_layout = service.vote_layout(vote_request.layout_id)
        return updated_layout
    except Exception as e:
        logger.error(f"Error voting for layout: {e}")
        raise HTTPException(status_code=404, detail="Layout not found")
