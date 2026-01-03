from fastapi import APIRouter
from typing import List
from .master_data import HUNTER_CHARACTERS, SURVIVOR_CHARACTERS, TRAITS, MAPS

router = APIRouter(prefix="/api/master", tags=["master"])


@router.get("/hunters", response_model=List[str])
async def get_hunters():
    """ハンター一覧を取得"""
    return HUNTER_CHARACTERS


@router.get("/survivors", response_model=List[str])
async def get_survivors():
    """サバイバー一覧を取得"""
    return SURVIVOR_CHARACTERS


@router.get("/traits", response_model=List[str])
async def get_traits():
    """特質一覧を取得"""
    return TRAITS


@router.get("/maps", response_model=List[str])
async def get_maps():
    """マップ一覧を取得"""
    return MAPS
