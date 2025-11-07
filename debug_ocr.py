#!/usr/bin/env python3
"""
OCR座標デバッグツール

使い方:
python debug_ocr.py screenshot.png

機能:
- アイコン検出位置を視覚化
- OCR結果を画像上に表示
- 各解像度での動作確認
"""

import cv2
import numpy as np
from pathlib import Path
import sys
from ocr_processor import OCRProcessor

def debug_ocr(image_path: str):
    """OCR処理をデバッグモードで実行"""
    
    # 画像読み込み
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ 画像を読み込めません: {image_path}")
        return
    
    height, width = img.shape[:2]
    print(f"\n📐 画像サイズ: {width}x{height}")
    
    # OCRプロセッサ初期化
    ocr = OCRProcessor()
    
    # デバッグ用の画像を作成
    debug_img = img.copy()
    
    # 1. サバイバーエリアを描画
    y_start = int(height * ocr.layout['survivor_y_start'])
    y_end = int(height * ocr.layout['survivor_y_end'])
    cv2.rectangle(debug_img, 
                  (0, y_start), 
                  (width, y_end), 
                  (0, 255, 255), 2)
    cv2.putText(debug_img, "Survivor Area", 
                (10, y_start - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # 2. アイコン検出領域を描画
    x_start = int(width * ocr.layout['icon_x_ratio'][0])
    x_end = int(width * ocr.layout['icon_x_ratio'][1])
    cv2.rectangle(debug_img,
                  (x_start, y_start),
                  (x_end, y_end),
                  (255, 0, 255), 2)
    cv2.putText(debug_img, "Icon Search Area",
                (x_start, y_start - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
    
    # 3. アイコン位置を検出して描画
    icon_positions = ocr._detect_icon_positions(img)
    print(f"\n🎯 検出されたアイコン位置: {len(icon_positions)}個")

    for i, icon_data in enumerate(icon_positions, 1):
        if len(icon_data) == 4:
            x, y, w, h = icon_data
        else:
            x, y = icon_data
            w = h = int(width * ocr.layout['icon_size_ratio'])

        # キャラクター認識を試行
        char_name = ocr._match_character_icon(img, x, y, w, h)

        # アイコン領域を描画
        color = (0, 255, 0) if char_name else (0, 0, 255)  # 認識成功=緑、失敗=赤
        cv2.rectangle(debug_img, (x, y), (x + w, y + h), color, 3)

        # キャラクター名を表示
        label = char_name if char_name else f"Unknown {i}"
        cv2.putText(debug_img, label,
                   (x, y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        print(f"  アイコン {i}: x={x}, y={y}, size={w}x{h} → {char_name if char_name else '認識失敗'}")
    
    # 4. OCR結果を描画
    print("\n📝 OCR実行中...")
    results = ocr.reader.readtext(img)
    
    for bbox, text, conf in results:
        # バウンディングボックスを描画
        pts = np.array(bbox, dtype=np.int32)
        cv2.polylines(debug_img, [pts], True, (255, 0, 0), 1)
        
        # テキストを描画
        x, y = int(bbox[0][0]), int(bbox[0][1])
        cv2.putText(debug_img, text,
                   (x, y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
    
    print(f"✅ OCR完了: {len(results)}個のテキストを検出")
    
    # 5. 結果を保存
    output_path = Path(image_path).stem + "_debug.png"
    cv2.imwrite(output_path, debug_img)
    print(f"\n💾 デバッグ画像を保存: {output_path}")
    
    # 6. ウィンドウ表示（オプション）
    try:
        # リサイズ（大きすぎる場合）
        max_width = 1920
        if width > max_width:
            scale = max_width / width
            new_width = max_width
            new_height = int(height * scale)
            debug_img_resized = cv2.resize(debug_img, (new_width, new_height))
        else:
            debug_img_resized = debug_img
        
        cv2.imshow("OCR Debug", debug_img_resized)
        print("\n👀 ウィンドウを表示中... (何かキーを押すと終了)")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except:
        print("⚠️  ウィンドウ表示をスキップ（ヘッドレス環境）")
    
    # 7. 統計情報
    print("\n📊 統計情報:")
    print(f"  画像サイズ: {width}x{height}")
    print(f"  アイコン検出: {len(icon_positions)}個")
    print(f"  OCRテキスト: {len(results)}個")
    print(f"  相対座標設定:")
    print(f"    - icon_x_ratio: {ocr.layout['icon_x_ratio']}")
    print(f"    - icon_size_ratio: {ocr.layout['icon_size_ratio']}")
    print(f"    - survivor_y_start: {ocr.layout['survivor_y_start']}")
    print(f"    - survivor_y_end: {ocr.layout['survivor_y_end']}")

def main():
    if len(sys.argv) < 2:
        print("使い方: python debug_ocr.py <画像ファイル>")
        print("例: python debug_ocr.py screenshot.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"❌ ファイルが見つかりません: {image_path}")
        sys.exit(1)
    
    debug_ocr(image_path)

if __name__ == "__main__":
    main()
