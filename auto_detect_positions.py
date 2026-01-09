"""
iPad画像から自動的にアイコン位置を検出
"""
import cv2
import numpy as np

def detect_icon_positions(image_path):
    """画像からアイコン位置を自動検出"""
    img = cv2.imread(image_path)
    height, width = img.shape[:2]

    print(f"画像サイズ: {width}x{height}")
    print(f"アスペクト比: {width/height:.3f}\n")

    # 左側の領域を切り出し（X座標0.25-0.35）
    x_start = int(width * 0.25)
    x_end = int(width * 0.35)
    roi = img[:, x_start:x_end]

    # グレースケール化
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # エッジ検出
    edges = cv2.Canny(gray, 50, 150)

    # 水平方向のプロファイルを計算（各行のエッジピクセル数）
    horizontal_profile = np.sum(edges, axis=1)

    # ピークを検出（アイコンの境界）
    peaks = []
    threshold = np.max(horizontal_profile) * 0.3
    in_peak = False
    peak_start = 0

    for y, value in enumerate(horizontal_profile):
        if value > threshold and not in_peak:
            in_peak = True
            peak_start = y
        elif value <= threshold and in_peak:
            in_peak = False
            peak_center = (peak_start + y) // 2
            peaks.append(peak_center)

    print(f"検出されたピーク数: {len(peaks)}")

    # Y座標の大きい順にソート（上から下へ）
    peaks.sort()

    # 各ピークの相対Y座標を計算
    print("\n検出されたアイコン位置:")
    y_ratios = []
    for i, y in enumerate(peaks[:10], 1):  # 最大10個
        y_ratio = y / height
        y_ratios.append(y_ratio)
        print(f"  Position {i}: Y={y} ({y_ratio:.3f})")

    if len(y_ratios) >= 5:
        print(f"\n推奨Y座標配列:")
        print(f"  y_positions_ratio = {[round(r, 3) for r in y_ratios[:5]]}")

    # 視覚化用に画像を保存
    img_marked = img.copy()
    for y in peaks[:5]:
        cv2.line(img_marked, (0, y), (width, y), (0, 0, 255), 2)

    output_path = image_path.replace('.PNG', '_detected.png')
    cv2.imwrite(output_path, img_marked)
    print(f"\n検出結果を保存しました: {output_path}")

if __name__ == "__main__":
    print("=== iPad画像のアイコン位置自動検出 ===\n")
    detect_icon_positions('test_ipad.PNG')
    print("\n=== iPhone画像のアイコン位置自動検出 ===\n")
    detect_icon_positions('test.PNG')
