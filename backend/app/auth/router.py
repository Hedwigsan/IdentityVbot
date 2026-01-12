import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..database import get_supabase
from .dependencies import get_current_user
from ..config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Google OAuthのリダイレクトURL取得リクエスト"""
    redirect_url: Optional[str] = None


class LoginResponse(BaseModel):
    """Google OAuthのリダイレクトURLレスポンス"""
    url: str


class TokenRequest(BaseModel):
    """OAuthコールバック後のトークン交換リクエスト"""
    code: str


class TokenResponse(BaseModel):
    """認証トークンレスポンス"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


class UserResponse(BaseModel):
    """ユーザー情報レスポンス"""
    id: str
    email: Optional[str]
    name: Optional[str]
    avatar_url: Optional[str]


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Google OAuth認証URLを取得
    フロントエンドはこのURLにリダイレクトしてGoogleログインを開始
    """
    try:
        settings = get_settings()
        supabase = get_supabase()
        redirect_to = request.redirect_url or f"{settings.frontend_url}/auth/callback"

        response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_to
            }
        })

        return LoginResponse(url=response.url)

    except Exception as e:
        logger.error(f"認証エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="認証処理に失敗しました")


@router.post("/token", response_model=TokenResponse)
async def exchange_token(request: TokenRequest):
    """
    OAuthコールバックのcodeをトークンに交換
    """
    try:
        supabase = get_supabase()
        response = supabase.auth.exchange_code_for_session({"auth_code": request.code})

        if not response.session:
            raise HTTPException(status_code=400, detail="トークン交換に失敗しました")

        return TokenResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            expires_in=response.session.expires_in
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"トークン交換エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="トークン交換に失敗しました")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """
    リフレッシュトークンでアクセストークンを更新
    """
    try:
        supabase = get_supabase()
        response = supabase.auth.refresh_session(refresh_token)

        if not response.session:
            raise HTTPException(status_code=400, detail="トークン更新に失敗しました")

        return TokenResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            expires_in=response.session.expires_in
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"トークン更新エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="トークン更新に失敗しました")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    """
    現在のユーザー情報を取得
    """
    user_metadata = current_user.user_metadata or {}

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=user_metadata.get("full_name") or user_metadata.get("name"),
        avatar_url=user_metadata.get("avatar_url") or user_metadata.get("picture")
    )


@router.post("/logout")
async def logout(current_user=Depends(get_current_user)):
    """
    ログアウト（サーバー側ではセッション無効化）
    """
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
        return {"message": "ログアウトしました"}

    except Exception as e:
        logger.error(f"ログアウトエラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="ログアウトに失敗しました")
