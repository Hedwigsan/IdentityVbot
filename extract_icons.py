#!/usr/bin/env python3
"""
キャラアイコン切り出しヘルパー

使い方:
1. 戦績画面のスクショを用意
2. このスクリプトを実行
3. 画像をクリックしてアイコン位置を指定
4. キャラ名を入力
5. 自動で切り出して保存
"""

import cv2
import numpy as np
from pathlib import Path
import sys

class IconExtractor:
    def __init__(self):
        self.current_img = None
        self.icons_dir = Path("templates/icons")
        self.icons_dir.mkdir(parents=True, exist_ok=True)
        
        self.click_points = []
        self.current_char_name = ""
        
    def mouse_callback(self, event, x, y, flags, param):
        """マウスクリックでアイコン領域を選択"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.click_points.append((x, y))
            cv2.circle(self.current_img_display, (x, y), 3, (0, 255, 0), -1)
            cv2.imshow("Icon Extractor", self.current_img_display)
            
            # 2点選択されたら矩形を描画
            if len(self.click_points) == 2:
                p1, p2 = self.click_points
                cv2.rectangle(self.current_img_display, p1, p2, (0, 255, 0), 2)
                cv2.imshow("Icon Extractor", self.current_img_display)
    
    def extract_icon(self, img_path: str):
        """画像からアイコンを切り出し"""
        img = cv2.imread(img_path)
        if img is None:
            print(f"❌ 画像を読み込めません: {img_path}")
            return
        
        self.current_img = img.copy()
        self.current_img_display = img.copy()
        
        print("\n📸 アイコン切り出しツール")
        print("=" * 50)
        print("1. 画像上でアイコンの左上をクリック")
        print("2. 次にアイコンの右下をクリック")
        print("3. キャラ名を入力してEnter")
        print("4. 'n' で次のアイコン、'q' で終了")
        print("=" * 50)
        
        cv2.namedWindow("Icon Extractor")
        cv2.setMouseCallback("Icon Extractor", self.mouse_callback)
        cv2.imshow("Icon Extractor", self.current_img_display)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            # 2点選択されたらキャラ名を入力
            if len(self.click_points) == 2:
                p1, p2 = self.click_points
                x1, y1 = min(p1[0], p2[0]), min(p1[1], p2[1])
                x2, y2 = max(p1[0], p2[0]), max(p1[1], p2[1])
                
                # アイコン領域を切り出し
                icon = self.current_img[y1:y2, x1:x2]
                
                # プレビュー表示
                cv2.imshow("Extracted Icon", icon)
                
                # キャラ名を入力
                print(f"\n切り出しサイズ: {icon.shape[1]}x{icon.shape[0]}px")
                char_name = input("キャラ名を入力 (例: 医師, 機械技師): ").strip()
                
                if char_name:
                    # 保存
                    save_path = self.icons_dir / f"{char_name}.png"
                    cv2.imwrite(str(save_path), icon)
                    print(f"✅ 保存しました: {save_path}")
                
                # リセット
                self.click_points = []
                self.current_img_display = self.current_img.copy()
                cv2.imshow("Icon Extractor", self.current_img_display)
                
            # 'q'で終了
            if key == ord('q'):
                break
        
        cv2.destroyAllWindows()
        print(f"\n✅ 完了！ {self.icons_dir} に保存されました")

def main():
    if len(sys.argv) < 2:
        print("使い方: python extract_icons.py <戦績画面のスクショ>")
        print("例: python extract_icons.py screenshot.png")
        sys.exit(1)
    
    img_path = sys.argv[1]
    extractor = IconExtractor()
    extractor.extract_icon(img_path)

if __name__ == "__main__":
    main()
