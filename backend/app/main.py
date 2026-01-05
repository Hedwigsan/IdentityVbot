from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .auth.router import router as auth_router
from .matches.router import router as matches_router
from .master_router import router as master_router
from .ocr.router import router as ocr_router
from .stats.router import router as stats_router

settings = get_settings()

app = FastAPI(
    title="Identity Archive API",
    description="第五人格ハンター戦績管理システム",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://192.168.11.5:5173",  # ネットワーク経由のアクセス
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(auth_router)
app.include_router(matches_router)
app.include_router(master_router)
app.include_router(ocr_router)
app.include_router(stats_router)


@app.get("/")
async def root():
    """ヘルスチェック"""
    return {
        "message": "Identity Archive API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}
