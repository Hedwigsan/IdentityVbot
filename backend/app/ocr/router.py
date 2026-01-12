import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Dict, Optional
from pathlib import Path
from ..auth.dependencies import get_current_user
from ..matches.schemas import AnalyzeResponse, SurvivorData
from ..database import get_supabase
from .processor import OCRProcessor
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/matches", tags=["ocr"])

# ファイルサイズ制限（10MB）
MAX_FILE_SIZE = 10 * 1024 * 1024

# OCRプロセッサをシングルトンで初期化（起動時に1回のみ）
# backendディレクトリからの相対パス
_ocr_processor = None


def get_ocr_processor(supabase=None) -> OCRProcessor:
    """OCRプロセッサを取得（遅延初期化）"""
    global _ocr_processor
    if _ocr_processor is None:
        # backend/app/ocr/router.py から backend/templates/icons への相対パス
        templates_path = Path(__file__).parent.parent.parent / "templates" / "icons"
        _ocr_processor = OCRProcessor(templates_path=str(templates_path), supabase_client=supabase)
    elif supabase and _ocr_processor.supabase is None:
        # Supabaseクライアントが設定されていない場合は設定
        _ocr_processor.supabase = supabase
    return _ocr_processor


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    """
    画像をアップロードしてOCR解析

    - 試合結果画像をアップロード
    - OCRで自動解析（5-15秒かかる場合があります）
    - 解析結果を返却（その後 POST /api/matches で保存）
    """
    # ファイルタイプチェック
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="画像ファイルをアップロードしてください")

    try:
        # 画像データを読み込み
        contents = await file.read()

        # ファイルサイズチェック
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"ファイルサイズが大きすぎます（最大10MB）"
            )

        # OCR処理（重い処理なのでスレッドプールで実行）
        loop = asyncio.get_event_loop()
        ocr = get_ocr_processor(supabase)
        result = await loop.run_in_executor(None, ocr.process_image, contents)

        # サバイバーデータを変換
        survivors = []
        for s in result.get("survivors", []):
            survivors.append(SurvivorData(
                character_name=s.get("character"),
                position=s.get("position"),
                kite_time=s.get("kite_time"),
                decode_progress=s.get("decode_progress"),
                board_hits=s.get("board_hits") or 0,
                rescues=s.get("rescues") or 0,
                heals=s.get("heals") or 0
            ))

        return AnalyzeResponse(
            result=result.get("result"),
            map_name=result.get("map_name"),
            duration=result.get("duration"),
            hunter_character=result.get("hunter_character"),
            played_at=result.get("played_at"),
            survivors=survivors
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR処理エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="画像の解析に失敗しました。別の画像をお試しください")


@router.post("/analyze-multiple", response_model=List[AnalyzeResponse])
async def analyze_multiple_images(
    files: List[UploadFile] = File(...),
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    """
    複数画像を一括でOCR解析
    """
    results = []

    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            continue

        try:
            contents = await file.read()

            # ファイルサイズチェック
            if len(contents) > MAX_FILE_SIZE:
                logger.warning(f"ファイルサイズ超過: {len(contents)} bytes")
                continue

            loop = asyncio.get_event_loop()
            ocr = get_ocr_processor(supabase)
            result = await loop.run_in_executor(None, ocr.process_image, contents)

            survivors = []
            for s in result.get("survivors", []):
                survivors.append(SurvivorData(
                    character_name=s.get("character"),
                    position=s.get("position"),
                    kite_time=s.get("kite_time"),
                    decode_progress=s.get("decode_progress"),
                    board_hits=s.get("board_hits") or 0,
                    rescues=s.get("rescues") or 0,
                    heals=s.get("heals") or 0
                ))

            results.append(AnalyzeResponse(
                result=result.get("result"),
                map_name=result.get("map_name"),
                duration=result.get("duration"),
                hunter_character=result.get("hunter_character"),
                played_at=result.get("played_at"),
                survivors=survivors
            ))

        except Exception as e:
            # エラーがあってもスキップして続行
            logger.error(f"画像解析エラー: {str(e)}", exc_info=True)
            continue

    return results


@router.post("/analyze-with-layout", response_model=AnalyzeResponse)
async def analyze_image_with_layout(
    file: UploadFile = File(...),
    layout: str = Form(...),
    current_user=Depends(get_current_user),
    supabase=Depends(get_supabase)
):
    """
    カスタムレイアウトを使用して画像をOCR解析

    - file: 試合結果画像
    - layout: JSON文字列形式のアイコン位置情報
      例: [{"x_ratio": 0.23, "y_ratio": 0.33, "size_ratio": 0.062}, ...]
    """
    # ファイルタイプチェック
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="画像ファイルをアップロードしてください")

    try:
        # レイアウトをパース
        try:
            custom_layout = json.loads(layout)
            if not isinstance(custom_layout, list) or len(custom_layout) != 5:
                raise ValueError("レイアウトは5要素の配列である必要があります")
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"無効なレイアウト形式: {str(e)}")

        # 画像データを読み込み
        contents = await file.read()

        # ファイルサイズチェック
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"ファイルサイズが大きすぎます（最大10MB）"
            )

        # OCR処理（カスタムレイアウトを渡す）
        loop = asyncio.get_event_loop()
        ocr = get_ocr_processor(supabase)
        result = await loop.run_in_executor(None, ocr.process_image, contents, custom_layout)

        # サバイバーデータを変換
        survivors = []
        for s in result.get("survivors", []):
            survivors.append(SurvivorData(
                character_name=s.get("character"),
                position=s.get("position"),
                kite_time=s.get("kite_time"),
                decode_progress=s.get("decode_progress"),
                board_hits=s.get("board_hits") or 0,
                rescues=s.get("rescues") or 0,
                heals=s.get("heals") or 0
            ))

        return AnalyzeResponse(
            result=result.get("result"),
            map_name=result.get("map_name"),
            duration=result.get("duration"),
            hunter_character=result.get("hunter_character"),
            played_at=result.get("played_at"),
            survivors=survivors
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR処理エラー: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="画像の解析に失敗しました。別の画像をお試しください")
