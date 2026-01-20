import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """アプリケーション設定"""

    # Supabase
    supabase_url: str
    supabase_key: str

    # CORS
    frontend_url: str = "http://localhost:5173"

    # OCR
    ocr_templates_path: str = "templates/icons"
    ocr_lite_mode: bool = True  # liteモード（parseq-tiny）で高速推論

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
