from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from decimal import Decimal


class IconPosition(BaseModel):
    """アイコン位置情報（相対座標）"""
    x_ratio: float = Field(..., description="X座標の比率（0.0～1.0）")
    y_ratio: float = Field(..., description="Y座標の比率（0.0～1.0）")
    size_ratio: float = Field(..., description="アイコンサイズの比率（0.0～1.0）")


class DeviceLayoutCreate(BaseModel):
    """デバイスレイアウト作成リクエスト"""
    aspect_ratio: Decimal = Field(..., description="アスペクト比（例: 2.1695）")
    screen_width: int = Field(..., gt=0, description="画面幅（ピクセル）")
    screen_height: int = Field(..., gt=0, description="画面高さ（ピクセル）")
    icon_positions: List[IconPosition] = Field(..., min_length=5, max_length=5, description="アイコン位置（5箇所）")


class DeviceLayoutResponse(BaseModel):
    """デバイスレイアウトレスポンス"""
    id: str
    aspect_ratio: Decimal
    screen_width: int
    screen_height: int
    icon_positions: List[IconPosition]
    vote_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeviceLayoutVoteRequest(BaseModel):
    """既存レイアウトへの投票リクエスト"""
    layout_id: str = Field(..., description="投票するレイアウトのID")
