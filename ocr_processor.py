import easyocr
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import re
from pathlib import Path

# yomitokuのインポート（オプション）
try:
    from yomitoku import DocumentAnalyzer  # type: ignore
    YOMITOKU_AVAILABLE = True
except ImportError:
    YOMITOKU_AVAILABLE = False
    DocumentAnalyzer = None  # type: ignore

class OCRProcessor:
    def __init__(self, use_yomitoku=True):
        self.use_yomitoku = use_yomitoku and YOMITOKU_AVAILABLE
        self.reader = None  # easyocrのreaderを初期化

        if self.use_yomitoku:
            try:
                print("[INFO] Initializing yomitoku...")
                self.yomitoku_analyzer = DocumentAnalyzer(device='cpu')  # GPUを使う場合は 'cuda'
                print("[SUCCESS] Using yomitoku OCR")
            except Exception as e:
                print(f"[WARNING] Failed to initialize yomitoku: {e}")
                print("[INFO] Falling back to easyocr")
                self.use_yomitoku = False
                self.reader = easyocr.Reader(['ja', 'en'], gpu=False)
        else:
            if not YOMITOKU_AVAILABLE:
                print("[WARNING] yomitoku not installed. Using easyocr")
            self.reader = easyocr.Reader(['ja', 'en'], gpu=False)
        
        # キャラアイコンのテンプレート画像（必須）
        self.icon_templates = {}
        self._load_icon_templates()
        
        # マップ名リスト
        self.map_names = [
            "聖心病院", "軍需工場", "赤の教会", "湖景村",
            "月の河公園", "中華街", "罪の森", "永眠町", "レオの思い出"
        ]
        
        # 画面レイアウトの設定（相対座標）
        self.layout = {
            "icon_x_ratio": (0.29, 0.34),  # アイコンのX座標範囲（画面幅の17.5%~20.5%）
            "icon_size_ratio": 0.04,         # アイコンサイズ（画面幅の3%）
            "survivor_y_start": 0.43,       # サバイバーエリア開始（画面の19.5%）
            "survivor_y_end": 0.95,         # サバイバーエリア終了（画面の57.5%）
            "icon_y_offset_ratio": 0.02,    # アイコンY座標のオフセット（画面高さの2%下に）
            "use_auto_detect": False,        # 自動検出を無効化（固定座標を使用）
        }
    
    def _load_icon_templates(self):
        """キャラアイコンのテンプレート画像を読み込み（必須）"""
        template_dir = Path("templates/icons")

        if not template_dir.exists():
            print("[WARNING] templates/icons/ directory not found")
            print("Please add character icon images. See ICON_GUIDE.md for details")
            return

        # .pngと.PNGの両方に対応
        for pattern in ["*.png", "*.PNG"]:
            for icon_file in template_dir.glob(pattern):
                char_name = icon_file.stem
                # 既に読み込み済みの場合はスキップ
                if char_name in self.icon_templates:
                    continue

                # Unicodeパス対応のためにnumpyで読み込む
                try:
                    with open(icon_file, 'rb') as f:
                        image_data = f.read()
                    nparr = np.frombuffer(image_data, np.uint8)
                    template = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                except Exception as e:
                    print(f"[WARNING] Failed to load {char_name}: {e}")
                    continue

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
            print(f"[SUCCESS] Loaded {len(self.icon_templates)} character icons")
        else:
            print("[WARNING] No character icons found. See ICON_GUIDE.md")
    
    def process_image(self, image_bytes: bytes) -> Dict:
        """画像から試合データを抽出"""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise Exception("画像の読み込みに失敗しました")

        # OCR実行
        if self.use_yomitoku:
            results = self._run_yomitoku_ocr(img)
        else:
            results = self._run_easyocr(img)

        # データ構造化
        match_data = self._parse_match_data(results, img)

        return match_data

    def _run_yomitoku_ocr(self, img: np.ndarray) -> List:
        """yomitokuでOCR実行"""
        try:
            # yomitokuで解析
            print("[DEBUG] Starting yomitoku analysis...")
            results = self.yomitoku_analyzer(img)

            # デバッグ: 結果の構造を確認
            print(f"[DEBUG] yomitoku result type: {type(results)}")
            if isinstance(results, dict):
                print(f"[DEBUG] yomitoku result keys: {results.keys()}")

            # yomitokuの結果をeasyocrの形式に変換
            # easyocr形式: [(bbox, text, confidence), ...]
            ocr_results = []

            # yomitokuの結果を解析
            # 結果は通常、'blocks'または'pages'という形式
            text_blocks = []

            if isinstance(results, dict):
                # pagesから全ブロックを取得
                if 'pages' in results and len(results['pages']) > 0:
                    page = results['pages'][0]
                    print(f"[DEBUG] Page keys: {page.keys() if isinstance(page, dict) else type(page)}")
                    if 'blocks' in page:
                        text_blocks = page['blocks']
                        print(f"[DEBUG] Number of blocks: {len(text_blocks)}")
                elif 'blocks' in results:
                    text_blocks = results['blocks']
                    print(f"[DEBUG] Number of blocks: {len(text_blocks)}")

            # デバッグ: 最初の数ブロックを表示
            for i, block in enumerate(text_blocks[:3]):
                print(f"  Block {i}: {block}")

            for block in text_blocks:
                # bboxを取得
                bbox_data = block.get('bbox', None)
                text = block.get('text', '')
                confidence = block.get('score', 1.0)  # yomitokuは'score'を使用

                if bbox_data and text:
                    # bboxを[[x1,y1], [x2,y1], [x2,y2], [x1,y2]]形式に変換
                    if len(bbox_data) == 4:  # [x1, y1, x2, y2]形式の場合
                        x1, y1, x2, y2 = bbox_data
                        bbox_formatted = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
                    elif len(bbox_data) == 8:  # [x1, y1, x2, y2, x3, y3, x4, y4]形式の場合
                        bbox_formatted = [
                            [bbox_data[0], bbox_data[1]],
                            [bbox_data[2], bbox_data[3]],
                            [bbox_data[4], bbox_data[5]],
                            [bbox_data[6], bbox_data[7]]
                        ]
                    else:
                        bbox_formatted = bbox_data

                    ocr_results.append((bbox_formatted, text, confidence))

            print(f"✅ yomitokuで{len(ocr_results)}個のテキストブロックを検出")

            # デバッグ: 最初の数個の結果を表示
            for i, (bbox, text, conf) in enumerate(ocr_results[:5]):
                print(f"  結果{i}: '{text}' (信頼度: {conf:.2f})")

            return ocr_results

        except Exception as e:
            print(f"⚠️  yomitoku OCRに失敗しました: {e}")
            import traceback
            traceback.print_exc()
            print("easyocrにフォールバック...")
            return self._run_easyocr(img)

    def _run_easyocr(self, img: np.ndarray) -> List:
        """easyocrでOCR実行（フォールバック）"""
        # readerが初期化されていない場合は初期化
        if self.reader is None:
            print("🔄 easyocrを初期化中...")
            self.reader = easyocr.Reader(['ja', 'en'], gpu=False)

        results = self.reader.readtext(
            img,
            paragraph=False,  # 段落検出を無効化
            min_size=5,       # 最小テキストサイズを小さく
            text_threshold=0.6,  # テキスト検出閾値を下げる
            low_text=0.3,     # 低信頼度テキストも検出
            link_threshold=0.3,  # リンク閾値を下げる
            canvas_size=2560,  # キャンバスサイズを大きく
            mag_ratio=1.5     # 拡大率
        )
        print(f"✅ easyocrで{len(results)}個のテキストブロックを検出")
        return results
    
    def _parse_match_data(self, results: List, img: np.ndarray) -> Dict:
        """OCR結果から試合データを抽出"""
        height, width = img.shape[:2]

        match_data = {
            "result": None,
            "map_name": None,
            "duration": None,
            "played_at": None,
            "survivors": []
        }
        
        # Y座標でソート（上から順に処理）
        sorted_results = sorted(results, key=lambda x: (x[0][0][1] + x[0][2][1]) / 2)
        
        for bbox, text, conf in sorted_results:
            # 座標を正規化
            y_center = (bbox[0][1] + bbox[2][1]) / 2 / height
            x_center = (bbox[0][0] + bbox[2][0]) / 2 / width

            # デバッグ出力
            print(f"OCR: '{text}' (信頼度: {conf:.2f}, Y: {y_center:.2%})")

            # 勝利/敗北/辛勝を検出（上部エリアの大きな文字）
            if y_center < 0.3:  # 画面上部30%以内
                if "勝利" in text or text == "勝":
                    match_data["result"] = "勝利"
                    print(f"  ✅ 勝利を検出")
                elif "敗北" in text or text == "敗":
                    match_data["result"] = "敗北"
                    print(f"  ✅ 敗北を検出")
                elif "辛勝" in text or text == "辛":
                    match_data["result"] = "辛勝"
                    print(f"  ✅ 辛勝を検出")

            # マップ名を検出
            for map_name in self.map_names:
                if map_name in text:
                    match_data["map_name"] = map_name
                    print(f"  🗺️  マップ: {map_name}")
                    break

            # 試合日時を検出（例: "11月2日12:57", "11/2 12:57"）
            # まず「使用時間」の前の部分だけを抽出
            datetime_patterns = [
                # "11月2日12:57 使用時間" のような場合、使用時間の前だけマッチ
                r'(\d{1,2})月(\d{1,2})日[^\d：:]*(\d{1,2}):(\d{2})[^0-9]*使用',
                r'(\d{1,2})月(\d{1,2})日\s*(\d{1,2}):(\d{2})',  # "11月2日12:57", "11月2日 12:57"
                r'(\d{1,2})/(\d{1,2})\s*(\d{1,2}):(\d{2})',     # "11/2 12:57"
                r'(\d{1,2})-(\d{1,2})\s*(\d{1,2}):(\d{2})',     # "11-2 12:57"
            ]
            for pattern in datetime_patterns:
                dt_match = re.search(pattern, text)
                if dt_match and not match_data["played_at"]:
                    month = int(dt_match.group(1))
                    day = int(dt_match.group(2))
                    hour = int(dt_match.group(3))
                    minute = int(dt_match.group(4))

                    # 有効な日時かチェック（時刻は試合開始時刻なので広範囲）
                    if 1 <= month <= 12 and 1 <= day <= 31 and 0 <= hour <= 23 and 0 <= minute <= 59:
                        from datetime import datetime
                        # 現在の年を使用
                        current_year = datetime.now().year
                        try:
                            played_datetime = datetime(current_year, month, day, hour, minute)
                            match_data["played_at"] = played_datetime.isoformat()
                            print(f"  📅 試合日時: {month}月{day}日 {hour}:{minute:02d}")
                        except ValueError:
                            pass  # 無効な日付の場合はスキップ
                    break

            # 使用時間を検出（例: "使用時間:4:17", "使用時間：4:17"）
            # より厳密なパターンで、日時と区別
            time_patterns = [
                r'使用時間[：:\s]*(\d{1,2}):(\d{2})',  # "使用時間:4:17", "使用時間：4:17"
                r'時間[：:\s]*(\d{1,2}):(\d{2})',      # "時間:4:17", "時間：4:17"
            ]
            for pattern in time_patterns:
                time_match = re.search(pattern, text)
                if time_match and not match_data["duration"]:
                    minutes = int(time_match.group(1))
                    seconds = int(time_match.group(2))
                    # 試合時間は通常15分以内
                    if minutes <= 15:
                        match_data["duration"] = f"{minutes}:{seconds:02d}"
                        print(f"  ⏱️  試合時間: {match_data['duration']}")
                        break
        
        # サバイバー情報を抽出（画像認識ベース）
        match_data["survivors"] = self._extract_survivors(sorted_results, img)

        # 勝敗が検出されなかった場合はデフォルト値を設定
        if match_data["result"] is None:
            match_data["result"] = "不明"
            print("⚠️  勝敗を検出できませんでした")

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
            "board_hits": None,
            "rescues": None,
            "heals": None
        }

        # target_y付近（画面高さの±8%）のテキストを収集
        tolerance = int(img_height * 0.08)
        row_texts = []
        for bbox, text, conf in results:
            y_center = (bbox[0][1] + bbox[2][1]) / 2

            if abs(y_center - target_y) < tolerance:
                row_texts.append((bbox, text, conf))

        # X座標でソート（左から右へ）
        row_texts.sort(key=lambda x: x[0][0][0])

        # データ抽出（より柔軟なパターンマッチング）
        detected_numbers = []  # 検出した数字を記録

        for bbox, text, conf in row_texts:
            # デバッグ出力
            print(f"    行データ: '{text}' (信頼度: {conf:.2f})")

            # テキストをクリーンアップ（スペース、特殊文字除去）
            clean_text = text.replace(" ", "").replace(",", "").replace(".", "")

            # 牽制時間（例: "20s", "34s", "205"（5→s誤認識）, "1分20s"）
            time_patterns = [
                r'(\d+)分(\d+)s',  # "1分20s"
                r'(\d+)分(\d+)秒',  # "1分20秒"
                r'(\d+)s',  # "20s"
                r'(\d+)秒',  # "20秒"
                r'(\d+)\s*[sS]',  # "20 s", "20S"
                r'(\d{1,3})5(?=\D|$)',  # "205" (5がsの誤認識)
            ]
            for i, pattern in enumerate(time_patterns):
                time_match = re.search(pattern, clean_text, re.IGNORECASE)
                if time_match and not data["kite_time"]:
                    if i <= 1:  # 分秒形式
                        minutes = int(time_match.group(1))
                        seconds = int(time_match.group(2))
                        total_seconds = minutes * 60 + seconds
                        data["kite_time"] = f"{total_seconds}s"
                    else:
                        time_value = time_match.group(1)
                        data["kite_time"] = time_value + "s"
                    print(f"  ⏱️  牽制時間: {data['kite_time']}")
                    break

            # 解読進捗（例: "112%", "0%", "1129"（9→%誤認識））
            progress_patterns = [
                r'(\d{1,3})\s*[%％]',  # "112%", "0 %", 全角パーセント
                r'(\d{1,3})(?=%)',  # "%"の直前の数字
                r'(\d{1,3})[9９](?=\D|$)',  # "1129", "112９" (9が%の誤認識)
            ]
            for pattern in progress_patterns:
                progress_match = re.search(pattern, clean_text)
                if progress_match and not data["decode_progress"]:
                    progress_value = progress_match.group(1)
                    data["decode_progress"] = progress_value + "%"
                    print(f"  📊 解読進捗: {data['decode_progress']}")
                    break

            # 単独の数字を抽出（板/救助/治療用）
            # 既に牽制時間や解読進捗として認識されていない数字のみ
            number_matches = re.findall(r'\b(\d{1,2})\b', clean_text)
            for num_str in number_matches:
                num = int(num_str)
                # 100以上は解読進捗の可能性があるのでスキップ
                if num < 100 and num_str not in str(data["kite_time"] or "") and num_str not in str(data["decode_progress"] or ""):
                    detected_numbers.append(num)

        # 検出した数字を板/救助/治療に割り当て
        # 通常は左から順に：板、救助、治療
        if len(detected_numbers) >= 1:
            data["board_hits"] = detected_numbers[0]
            print(f"  🛡️  板当て: {detected_numbers[0]}")
        if len(detected_numbers) >= 2:
            data["rescues"] = detected_numbers[1]
            print(f"  🚑 救助: {detected_numbers[1]}")
        if len(detected_numbers) >= 3:
            data["heals"] = detected_numbers[2]
            print(f"  💊 治療: {detected_numbers[2]}")

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

        # アイコン領域を切り出し（周辺のパディングを含める）
        padding = int(width * 0.1)  # 10%のパディング
        y1 = max(0, y - padding)
        y2 = min(img.shape[0], y + height + padding)
        x1 = max(0, x - padding)
        x2 = min(img.shape[1], x + width + padding)

        icon_region = img[y1:y2, x1:x2]

        if icon_region.size == 0:
            return None

        # 各キャラクターのベストスコアを記録
        char_scores = {}

        for char_name, template_data in self.icon_templates.items():
            max_score_for_char = 0.0

            # より多くのサイズで試す
            sizes = template_data['sizes']
            original = template_data['original']

            # 追加のスケールも試す（元のサイズに基づく）
            orig_h, orig_w = original.shape[:2]
            scales = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
            extra_sizes = []
            for scale in scales:
                new_size = (int(orig_w * scale), int(orig_h * scale))
                if 30 <= new_size[0] <= 150 and 30 <= new_size[1] <= 150:
                    extra_sizes.append(cv2.resize(original, new_size))

            all_templates = sizes + extra_sizes

            for template in all_templates:
                # テンプレートがアイコン領域より大きい場合はスキップ
                if template.shape[0] > icon_region.shape[0] or template.shape[1] > icon_region.shape[1]:
                    continue

                # TM_CCOEFF_NORMEDが最も信頼性が高い
                try:
                    result = cv2.matchTemplate(icon_region, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(result)

                    if max_val > max_score_for_char:
                        max_score_for_char = max_val

                except cv2.error:
                    continue

            char_scores[char_name] = max_score_for_char

        # スコアが最も高いキャラクターを選択
        if not char_scores:
            return None

        # スコアでソート
        sorted_scores = sorted(char_scores.items(), key=lambda x: x[1], reverse=True)

        best_char, best_score = sorted_scores[0]

        # デバッグ: トップ5を表示
        print(f"  📊 マッチングスコア (トップ5):")
        for char, score in sorted_scores[:5]:
            marker = "🎯" if char == best_char else "  "
            print(f"    {marker} {char}: {score:.2%}")

        # 閾値チェック（最低40%以上）
        if best_score < 0.40:
            print(f"  ❌ 最高スコアが閾値未満: {best_score:.2%} < 40%")
            return None

        # 2位との差が小さすぎる場合は信頼性が低いと判断
        if len(sorted_scores) > 1:
            second_score = sorted_scores[1][1]
            score_diff = best_score - second_score
            if score_diff < 0.05:  # 5%未満の差
                print(f"  ⚠️  2位との差が小さい: {score_diff:.2%} (1位: {best_score:.2%}, 2位: {second_score:.2%})")
                # それでも採用するが警告を出す

        print(f"  ✅ 認識結果: {best_char} (信頼度: {best_score:.2%})")
        return best_char
    
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

        # Y座標オフセットを取得（デフォルトは0）
        y_offset = int(height * self.layout.get('icon_y_offset_ratio', 0.0))

        for i in range(4):
            y = int(y_start + i * row_height + y_offset)
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

