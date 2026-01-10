import logging
from fastapi import Depends, HTTPException, Header
from typing import Optional
from ..database import get_supabase

logger = logging.getLogger(__name__)


async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    認証ミドルウェア
    AuthorizationヘッダーからJWTトークンを取得し、Supabaseで検証
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="認証が必要です")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="無効な認証形式です")

    token = authorization.split(" ")[1]

    try:
        supabase = get_supabase()
        user_response = supabase.auth.get_user(token)

        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="無効なトークンです")

        return user_response.user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"認証エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=401, detail="認証に失敗しました")


async def get_current_user_optional(authorization: Optional[str] = Header(None)):
    """
    オプショナル認証（未認証でも許可）
    """
    if not authorization:
        return None

    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
