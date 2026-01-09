"""
iPad画像のアイコン位置を視覚的に解析するスクリプト
"""
import cv2
import numpy as np
import sys
sys.path.insert(0, 'backend')

from app.ocr.processor import OCRProcessor

def analyze_positions():
    # iPad画像を読み込み
    img = cv2.imread('test_ipad.PNG')
    height, width = img.shape[:2]
    aspect_ratio = width / height

    print(f"画像サイズ: {width}x{height}")
    print(f"アスペクト比: {aspect_ratio:.3f}")
    print()

    # processor.pyから実際の設定を取得
    processor = OCRProcessor(templates_path="backend/templates/icons")

    # アスペクト比に基づいてY座標を決定（processor.pyのロジックと同じ）
    if aspect_ratio > 2.0:
        current_y_ratios = [0.29, 0.42, 0.555, 0.69, 0.825]
        screen_type = "iPhone (wide)"
    elif aspect_ratio < 1.6:
        current_y_ratios = [0.33, 0.44, 0.555, 0.665, 0.78]
        screen_type = "iPad (square-ish)"
    else:
        current_y_ratios = [0.25, 0.37, 0.49, 0.61, 0.73]
        screen_type = "Other (medium)"

    print(f"画面タイプ: {screen_type}")
    print("\n現在のY座標:")
    for i, ratio in enumerate(current_y_ratios, 1):
        y = int(height * ratio)
        print(f"  Position {i}: Y={y} ({ratio*100:.1f}%)")

    print("\n画像にマーカーを描画して確認します...")

    # コピーを作成
    img_marked = img.copy()

    # X座標（左側） - processor.pyのlayout設定と同じ
    x_ratio = 0.23  # この値を調整してX位置を変更できます（例: 0.25～0.35）
    x = int(width * x_ratio)

    # アイコンサイズ - より大きく（見やすく）
    icon_size = int(width * 0.062)  # 0.04から0.06に拡大（50%増）

    # 現在の位置にマーカーを描画
    for i, ratio in enumerate(current_y_ratios, 1):
        y = int(height * ratio)

        # 赤い矩形を描画（線を太く）
        cv2.rectangle(img_marked, (x, y), (x + icon_size, y + icon_size), (0, 0, 255), 5)

        # ラベル
        cv2.putText(img_marked, f"Pos{i}", (x + icon_size + 10, y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # 画像を保存
    output_path = 'test_ipad_marked.png'
    cv2.imwrite(output_path, img_marked)
    print(f"\nマーカー付き画像を保存しました: {output_path}")
    print("この画像を確認して、アイコンの位置を手動で測定してください。")

if __name__ == "__main__":
    analyze_positions()
