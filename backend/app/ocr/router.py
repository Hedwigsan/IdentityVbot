import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from pathlib import Path
from ..auth.dependencies import get_current_user
from ..matches.schemas import AnalyzeResponse, SurvivorData
from .processor import OCRProcessor

router = APIRouter(prefix="/api/matches", tags=["ocr"])

# OCRプロセッサをシングルトンで初期化（起動時に1回のみ）
# backendディレクトリからの相対パス
_ocr_processor = None


def get_ocr_processor() -> OCRProcessor:
    """OCRプロセッサを取得（遅延初期化）"""
    global _ocr_processor
    if _ocr_processor is None:
        # backend/app/ocr/router.py から backend/templates/icons への相対パス
        templates_path = Path(__file__).parent.parent.parent / "templates" / "icons"
        _ocr_processor = OCRProcessor(templates_path=str(templates_path))
    return _ocr_processor


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
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

        # OCR処理（重い処理なのでスレッドプールで実行）
        loop = asyncio.get_event_loop()
        ocr = get_ocr_processor()
        result = await loop.run_in_executor(None, ocr.process_image, contents)

        # サバイバーデータを変換
        survivors = []
        for s in result.get("survivors", []):
            survivors.append(SurvivorData(
                character_name=s.get("character"),
                position=s.get("position"),
                kite_time=s.get("kite_time"),
                decode_progress=s.get("decode_progress"),
                board_hits=s.get("board_hits", 0),
                rescues=s.get("rescues", 0),
                heals=s.get("heals", 0)
            ))

        return AnalyzeResponse(
            result=result.get("result"),
            map_name=result.get("map_name"),
            duration=result.get("duration"),
            hunter_character=result.get("hunter_character"),
            played_at=result.get("played_at"),
            survivors=survivors
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR処理エラー: {str(e)}")


@router.post("/analyze-multiple", response_model=List[AnalyzeResponse])
async def analyze_multiple_images(
    files: List[UploadFile] = File(...),
    current_user=Depends(get_current_user)
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
            loop = asyncio.get_event_loop()
            ocr = get_ocr_processor()
            result = await loop.run_in_executor(None, ocr.process_image, contents)

            survivors = []
            for s in result.get("survivors", []):
                survivors.append(SurvivorData(
                    character_name=s.get("character"),
                    position=s.get("position"),
                    kite_time=s.get("kite_time"),
                    decode_progress=s.get("decode_progress"),
                    board_hits=s.get("board_hits", 0),
                    rescues=s.get("rescues", 0),
                    heals=s.get("heals", 0)
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
            print(f"[ERROR] Failed to analyze image: {e}")
            continue

    return results
