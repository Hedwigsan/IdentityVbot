import easyocr
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import re
from pathlib import Path

class OCRProcessor:
    def __init__(self):
        self.reader = easyocr.Reader(['ja', 'en'], gpu=False)
        
        # キャラアイコンのテンプレート画像（必須）
        self.icon_templates = {}
        self._load_icon_templates()
        
        # マップ名リスト
        self.map_names = [
            "聖心病院", "軍需工場", "赤の教会", "湖景村",
            "月の河公園", "中華街", "白砂街", "永眠鎮"
        ]
        
        # 画面レイアウトの設定（相対座標）
        self.layout = {
            "icon_x_ratio": (0.03, 0.12),   # アイコンのX座標範囲（画面幅の3%~12%）
            "icon_size_ratio": 0.06,         # アイコンサイズ（画面幅の6%）
            "survivor_y_start": 0.25,        # サバイバーエリア開始（画面の25%）
            "survivor_y_end": 0.85,          # サバイバーエリア終了（画面の85%）
            "use_auto_detect": True,         # 自動検出を有効化
        }
    
    def _load_icon_templates(self):
        """キャラアイコンのテンプレート画像を読み込み（必須）"""
        template_dir = Path("templates/icons")
        
        if not template_dir.exists():
            print("⚠️  templates/icons/ ディレクトリが見つかりません")
            print("キャラアイコン画像を追加してください。詳細: ICON_GUIDE.md")
            return
        
        for icon_file in template_dir.glob("*.png"):
            char_name = icon_file.stem
            template = cv2.imread(str(icon_file), cv2.IMREAD_COLOR)
            if template is not None:
                # 複数サイズのテンプレートを生成（スケール不変性）
                self.icon_templates[char_name] = {
                    'original': template,
                    'sizes': [
                        cv2.resize(template, (60, 60)),
                        cv2.resize(template, (70, 70)),
                        cv2.resize(template, (80, 80)),
                        cv2.resize(template, (90, 90)),
                    ]
                }
        
        if self.icon_templates:
            print(f"✅ {len(self.icon_templates)}個のキャラアイコンを読み込みました")
        else:
            print("⚠️  キャラアイコンが見つかりません。ICON_GUIDE.mdを参照してください")
    
    def process_image(self, image_bytes: bytes) -> Dict:
        """画像から試合データを抽出"""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise Exception("画像の読み込みに失敗しました")
        
        # OCR実行
        results = self.reader.readtext(img)
        
        # データ構造化
        match_data = self._parse_match_data(results, img)
        
        return match_data
    
    def _parse_match_data(self, results: List, img: np.ndarray) -> Dict:
        """OCR結果から試合データを抽出"""
        height, width = img.shape[:2]
        
        match_data = {
            "result": None,
            "map_name": None,
            "duration": None,
            "survivors": []
        }
        
        # Y座標でソート（上から順に処理）
        sorted_results = sorted(results, key=lambda x: (x[0][0][1] + x[0][2][1]) / 2)
        
        for bbox, text, conf in sorted_results:
            # 座標を正規化
            y_center = (bbox[0][1] + bbox[2][1]) / 2 / height
            x_center = (bbox[0][0] + bbox[2][0]) / 2 / width
            
            # 勝利/敗北を検出
            if "勝利" in text:
                match_data["result"] = "勝利"
            elif "敗北" in text:
                match_data["result"] = "敗北"
            
            # マップ名を検出
            for map_name in self.map_names:
                if map_name in text:
                    match_data["map_name"] = map_name
                    break
            
            # 使用時間を検出（例: "4:17"）
            time_match = re.search(r'\d+:\d+', text)
            if time_match:
                match_data["duration"] = time_match.group()
        
        # サバイバー情報を抽出（画像認識ベース）
        match_data["survivors"] = self._extract_survivors(sorted_results, img)
        
        return match_data
    
    def _extract_survivors(self, results: List, img: np.ndarray) -> List[Dict]:
        """サバイバー4人の情報を抽出（画像認識ベース）"""
        height, width = img.shape[:2]
        survivors = []
        
        # 1. キャラアイコンの位置を検出（画面サイズ対応）
        icon_positions = self._detect_icon_positions(img)
        
        print(f"\n🔍 サバイバー認識開始... (画面サイズ: {width}x{height})")
        
        # 2. 各位置でアイコンを認識
        for position, icon_data in enumerate(icon_positions, 1):
            print(f"\nサバイバー {position}:")
            
            # 座標データを展開
            if len(icon_data) == 4:
                icon_x, icon_y, icon_w, icon_h = icon_data
            else:
                # 古い形式（互換性）
                icon_x, icon_y = icon_data
                icon_w = icon_h = int(width * self.layout['icon_size_ratio'])
            
            survivor = {
                "position": position,
                "character": None,
                "kite_time": None,
                "decode_progress": None,
                "board_hits": 0,
                "rescues": 0,
                "heals": 0
            }
            
            # アイコンを画像認識
            char_name = self._match_character_icon(
                img, 
                icon_x, 
                icon_y,
                width=icon_w,
                height=icon_h
            )
            
            if char_name:
                survivor["character"] = char_name
            else:
                print(f"  ❌ キャラアイコンを認識できませんでした (位置: x={icon_x}, y={icon_y})")
            
            # その行のテキストデータを取得
            row_data = self._get_row_text_data(results, icon_y + icon_h // 2, height)
            
            # 数値データを抽出
            survivor.update(row_data)
            
            if survivor["character"]:  # キャラが認識できた場合のみ追加
                survivors.append(survivor)
        
        print(f"\n✅ {len(survivors)}人のサバイバーを認識しました\n")
        
        return survivors
    
    def _get_row_text_data(self, results: List, target_y: int, img_height: int) -> Dict:
        """
        指定Y座標付近のテキストデータから数値情報を抽出
        
        Args:
            results: OCR結果
            target_y: 対象行のY座標
            img_height: 画像の高さ
        
        Returns:
            牽制時間、解読進捗などのデータ
        """
        data = {
            "kite_time": None,
            "decode_progress": None,
            "board_hits": 0,
            "rescues": 0,
            "heals": 0
        }
        
        # target_y付近（±50px）のテキストを収集
        row_texts = []
        for bbox, text, conf in results:
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            
            if abs(y_center - target_y) < 50:
                row_texts.append((bbox, text, conf))
        
        # X座標でソート（左から右へ）
        row_texts.sort(key=lambda x: x[0][0][0])
        
        # データ抽出
        for bbox, text, conf in row_texts:
            # 牽制時間（例: "20s", "34s"）
            time_match = re.search(r'(\d+)s', text)
            if time_match:
                data["kite_time"] = time_match.group()
                print(f"  ⏱️  牽制時間: {data['kite_time']}")
            
            # 解読進捗（例: "112%", "0%"）
            progress_match = re.search(r'(\d+)%', text)
            if progress_match:
                data["decode_progress"] = progress_match.group()
                print(f"  📊 解読進捗: {data['decode_progress']}")
            
            # 数値データ（板/救助/治療）
            if text.isdigit() and len(text) <= 2:
                num = int(text)
                if data["board_hits"] == 0:
                    data["board_hits"] = num
                elif data["rescues"] == 0:
                    data["rescues"] = num
                elif data["heals"] == 0:
                    data["heals"] = num
        
        return data
    
    def _match_character_icon(self, img: np.ndarray, x: int, y: int, width: int = 100, height: int = 100) -> Optional[str]:
        """
        指定座標周辺のキャラアイコンを画像マッチングで識別
        
        Args:
            img: 元画像
            x, y: アイコンの左上座標
            width, height: アイコン領域のサイズ
        
        Returns:
            キャラクター名（見つからない場合はNone）
        """
        if not self.icon_templates:
            print("⚠️  アイコンテンプレートが読み込まれていません")
            return None
        
        # アイコン領域を切り出し
        y1 = max(0, y)
        y2 = min(img.shape[0], y + height)
        x1 = max(0, x)
        x2 = min(img.shape[1], x + width)
        
        icon_region = img[y1:y2, x1:x2]
        
        if icon_region.size == 0:
            return None
        
        # 各テンプレートとマッチング（マルチスケール）
        best_match = None
        best_score = 0.65  # 閾値（65%以上の一致で認識）
        
        for char_name, template_data in self.icon_templates.items():
            # 複数サイズで試す
            for template in template_data['sizes']:
                # テンプレートがアイコン領域より大きい場合はスキップ
                if template.shape[0] > icon_region.shape[0] or template.shape[1] > icon_region.shape[1]:
                    continue
                
                # テンプレートマッチング
                try:
                    result = cv2.matchTemplate(icon_region, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(result)
                    
                    if max_val > best_score:
                        best_score = max_val
                        best_match = char_name
                except cv2.error:
                    continue
        
        if best_match:
            print(f"  🎯 アイコン認識: {best_match} (信頼度: {best_score:.2%})")
        
        return best_match
    
    def _detect_icon_positions(self, img: np.ndarray) -> List[Tuple[int, int]]:
        """
        画像内のキャラアイコンの位置を検出（画面サイズ対応）
        
        Returns:
            [(x, y, width, height), ...] のリスト
        """
        height, width = img.shape[:2]
        
        # 相対座標から実座標に変換
        icon_size = int(width * self.layout['icon_size_ratio'])
        x_start = int(width * self.layout['icon_x_ratio'][0])
        x_end = int(width * self.layout['icon_x_ratio'][1])
        
        y_start = int(height * self.layout['survivor_y_start'])
        y_end = int(height * self.layout['survivor_y_end'])
        
        # 自動検出を試みる
        if self.layout.get('use_auto_detect', False):
            detected = self._auto_detect_icons(img, x_start, x_end, y_start, y_end)
            if detected and len(detected) >= 2:  # 2人以上検出できたら採用
                print(f"✅ 自動検出: {len(detected)}個のアイコン位置を検出")
                return detected
            else:
                print("⚠️  自動検出失敗、推定位置を使用")
        
        # フォールバック: 等間隔で推定
        positions = []
        row_height = (y_end - y_start) / 4
        
        for i in range(4):
            y = int(y_start + i * row_height)
            x = x_start
            positions.append((x, y, icon_size, icon_size))
        
        return positions
    
    def _auto_detect_icons(self, img: np.ndarray, x_min: int, x_max: int, 
                          y_min: int, y_max: int) -> List[Tuple[int, int, int, int]]:
        """
        輪郭検出でアイコン位置を自動検出
        
        Returns:
            [(x, y, width, height), ...] のリスト
        """
        # 検出エリアを切り出し
        roi = img[y_min:y_max, x_min:x_max]
        
        # グレースケール化
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # エッジ検出
        edges = cv2.Canny(gray, 50, 150)
        
        # 輪郭検出
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # アイコンらしい矩形を抽出
        icon_candidates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # フィルタリング条件
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            # アイコンの条件:
            # - 面積が適切（画像の0.3%~3%）
            # - アスペクト比が正方形に近い（0.8~1.2）
            # - X座標が左側
            img_area = roi.shape[0] * roi.shape[1]
            
            if (0.003 < area / img_area < 0.03 and
                0.8 < aspect_ratio < 1.2 and
                x < roi.shape[1] * 0.3):  # 左側30%以内
                
                # 元画像での座標に変換
                abs_x = x_min + x
                abs_y = y_min + y
                icon_candidates.append((abs_x, abs_y, w, h))
        
        # Y座標でソート（上から順）
        icon_candidates.sort(key=lambda c: c[1])
        
        # 最大4個まで
        return icon_candidates[:4]

