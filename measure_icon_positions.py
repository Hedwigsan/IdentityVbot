"""
iPad画像とiPhone画像のアイコン位置を手動で測定して比較
"""
import cv2
import numpy as np

def mouse_callback(event, x, y, flags, param):
    """マウスクリックでアイコン位置を取得"""
    if event == cv2.EVENT_LBUTTONDOWN:
        img, height, positions = param
        y_ratio = y / height
        print(f"クリック位置: X={x}, Y={y} (Y比率: {y_ratio:.3f})")
        positions.append((x, y, y_ratio))

        # マーカーを描画
        cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow('Image', img)

def measure_positions(image_path, label):
    """画像を表示してアイコン位置を手動測定"""
    img = cv2.imread(image_path)
    height, width = img.shape[:2]

    print(f"\n=== {label} ===")
    print(f"画像サイズ: {width}x{height}")
    print(f"アスペクト比: {width/height:.3f}")
    print("\nアイコンの中心をクリックしてください（上から順に5箇所）")
    print("ESCキーで終了\n")

    positions = []
    img_display = img.copy()

    cv2.namedWindow('Image')
    cv2.setMouseCallback('Image', mouse_callback, (img_display, height, positions))
    cv2.imshow('Image', img_display)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break

    cv2.destroyAllWindows()

    if positions:
        print(f"\n測定結果 ({len(positions)}箇所):")
        y_ratios = []
        for i, (x, y, y_ratio) in enumerate(positions, 1):
            print(f"  Position {i}: Y={y} ({y_ratio:.3f})")
            y_ratios.append(y_ratio)

        if len(y_ratios) >= 5:
            print(f"\nY座標配列（コピー用）:")
            print(f"  y_positions_ratio = {[round(r, 3) for r in y_ratios[:5]]}")
    else:
        print("測定されませんでした")

    return positions

if __name__ == "__main__":
    print("=== アイコン位置測定ツール ===")
    print("1. iPad画像")
    print("2. iPhone画像")
    choice = input("どちらを測定しますか？ (1/2): ")

    if choice == "1":
        measure_positions('test_ipad.PNG', 'iPad')
    elif choice == "2":
        measure_positions('test.PNG', 'iPhone')
    else:
        print("無効な選択です")
