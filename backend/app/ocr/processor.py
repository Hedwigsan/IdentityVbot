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
    def __init__(self, use_yomitoku=True, templates_path: str = None):
        self.use_yomitoku = use_yomitoku and YOMITOKU_AVAILABLE
        self.reader = None  # easyocrのreaderを初期化
        self.templates_path = templates_path or "templates/icons"

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
        self.survivor_templates = {}  # サバイバーアイコン
        self.hunter_templates = {}    # ハンターアイコン
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
        base_dir = Path(self.templates_path)

        # サバイバーアイコンを読み込み
        survivor_dir = base_dir / "survivors"
        if survivor_dir.exists():
            self._load_templates_from_dir(survivor_dir, self.survivor_templates, "survivor")

        # ハンターアイコンを読み込み
        hunter_dir = base_dir / "hunters"
        if hunter_dir.exists():
            self._load_templates_from_dir(hunter_dir, self.hunter_templates, "hunter")

        # 旧形式の互換性: templates/icons直下にある場合はサバイバーとして扱う
        if base_dir.exists():
            for pattern in ["*.png", "*.PNG"]:
                for icon_file in base_dir.glob(pattern):
                    char_name = icon_file.stem
                    if char_name not in self.survivor_templates and char_name not in self.hunter_templates:
                        try:
                            with open(icon_file, 'rb') as f:
                                image_data = f.read()
                            nparr = np.frombuffer(image_data, np.uint8)
                            template = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                            if template is not None:
                                self.survivor_templates[char_name] = {
                                    'original': template,
                                    'sizes': [
                                        cv2.resize(template, (60, 60)),
                                        cv2.resize(template, (70, 70)),
                                        cv2.resize(template, (80, 80)),
                                        cv2.resize(template, (90, 90)),
                                    ]
                                }
                        except Exception as e:
                            print(f"[WARNING] Failed to load {char_name}: {e}")

        total = len(self.survivor_templates) + len(self.hunter_templates)
        if total > 0:
            print(f"[SUCCESS] Loaded {len(self.survivor_templates)} survivor and {len(self.hunter_templates)} hunter icons")
        else:
            print("[WARNING] No character icons found")

    def _load_templates_from_dir(self, directory: Path, templates_dict: dict, char_type: str):
        """指定ディレクトリからテンプレートを読み込む"""
        for pattern in ["*.png", "*.PNG"]:
            for icon_file in directory.glob(pattern):
                char_name = icon_file.stem

                if char_name in templates_dict:
                    continue

                try:
                    with open(icon_file, 'rb') as f:
                        image_data = f.read()
                    nparr = np.frombuffer(image_data, np.uint8)
                    template = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                except Exception as e:
                    print(f"[WARNING] Failed to load {char_type} {char_name}: {e}")
                    continue

                if template is not None:
                    templates_dict[char_name] = {
                        'original': template,
                        'sizes': [
                            cv2.resize(template, (60, 60)),
                            cv2.resize(template, (70, 70)),
                            cv2.resize(template, (80, 80)),
                            cv2.resize(template, (90, 90)),
                        ]
                    }
    
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

            # イベントループが既に実行中かチェック
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                # 既に実行中の場合は、nest_asyncioを試す
                print("[DEBUG] Event loop already running, trying nest_asyncio...")
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                    print("[DEBUG] nest_asyncio applied successfully")
                    results = self.yomitoku_analyzer(img)
                except ImportError:
                    # nest_asyncioが無い場合は、新しいスレッドで実行
                    print("[DEBUG] nest_asyncio not available, running in thread...")
                    import concurrent.futures
                    import threading

                    def run_in_thread():
                        # 新しいイベントループを作成
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            return self.yomitoku_analyzer(img)
                        finally:
                            new_loop.close()

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_thread)
                        results = future.result(timeout=60)
            except RuntimeError:
                # イベントループが実行中でない場合は通常実行
                print("[DEBUG] No event loop running, executing normally...")
                results = self.yomitoku_analyzer(img)

            # デバッグ: 結果の構造を確認
            print(f"[DEBUG] yomitoku result type: {type(results)}")

            # yomitokuの結果をeasyocrの形式に変換
            # easyocr形式: [(bbox, text, confidence), ...]
            ocr_results = []

            # yomitokuの結果を解析
            # yomitokuのバージョン0.10.1では、結果はtupleで (pages_data, ocr_results) の形式
            text_blocks = []

            if isinstance(results, tuple) and len(results) >= 1:
                # tuple形式: yomitoku 0.10.1では3要素
                # (DocumentAnalyzerSchema, None, None)
                # 最初の要素がDocumentAnalyzerSchemaオブジェクト
                doc_schema = results[0]

                # DocumentAnalyzerSchemaからOCR結果を取得
                # yomitoku 0.10.1では、wordsに単語レベルのOCR結果が含まれる
                if hasattr(doc_schema, 'words') and doc_schema.words:
                    print(f"[INFO] Found {len(doc_schema.words)} words")

                    for word in doc_schema.words:
                        # yomitokuの構造: content (text), points (bbox), rec_score (confidence)
                        if hasattr(word, 'content') and hasattr(word, 'points'):
                            text_blocks.append({
                                'text': word.content,
                                'bbox': word.points,
                                'score': getattr(word, 'rec_score', 1.0)
                            })

                # paragraphsも試す（より長いテキスト単位） - 重複を避けるため、wordsが空の場合のみ
                if not text_blocks and hasattr(doc_schema, 'paragraphs') and doc_schema.paragraphs:
                    print(f"[INFO] Found {len(doc_schema.paragraphs)} paragraphs")

                    for para in doc_schema.paragraphs:
                        if hasattr(para, 'content') and hasattr(para, 'bbox'):
                            text_blocks.append({
                                'text': para.content,
                                'bbox': para.bbox,
                                'score': getattr(para, 'score', 1.0)
                            })

                print(f"[DEBUG] Extracted {len(text_blocks)} text elements from document schema")

            elif isinstance(results, dict):
                # dict形式（旧バージョン対応）
                print(f"[DEBUG] yomitoku result keys: {results.keys()}")
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
            print(f"[DEBUG] Sample of text_blocks (type: {type(text_blocks)}):")
            for i, block in enumerate(text_blocks[:3]):
                print(f"  Block {i} (type: {type(block)}): {block}")

            for block in text_blocks:
                # blockがdictの場合
                if isinstance(block, dict):
                    # bboxを取得
                    bbox_data = block.get('bbox', None)
                    text = block.get('text', '')
                    confidence = block.get('score', 1.0)  # yomitokuは'score'を使用
                elif isinstance(block, (list, tuple)) and len(block) >= 3:
                    # tuple/list形式: (bbox, text, confidence)
                    bbox_data = block[0]
                    text = block[1]
                    confidence = block[2] if len(block) > 2 else 1.0
                else:
                    continue

                if bbox_data and text:
                    # bboxを[[x1,y1], [x2,y1], [x2,y2], [x1,y2]]形式に変換
                    if isinstance(bbox_data, list):
                        if len(bbox_data) == 4 and all(isinstance(coord, (int, float)) for coord in bbox_data):
                            # [x1, y1, x2, y2]形式の場合
                            x1, y1, x2, y2 = bbox_data
                            bbox_formatted = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
                        elif len(bbox_data) == 8:
                            # [x1, y1, x2, y2, x3, y3, x4, y4]形式の場合
                            bbox_formatted = [
                                [bbox_data[0], bbox_data[1]],
                                [bbox_data[2], bbox_data[3]],
                                [bbox_data[4], bbox_data[5]],
                                [bbox_data[6], bbox_data[7]]
                            ]
                        else:
                            # 既に[[x1,y1], [x2,y2], ...]形式の場合
                            bbox_formatted = bbox_data
                    else:
                        bbox_formatted = bbox_data

                    ocr_results.append((bbox_formatted, text, confidence))

            print(f"[SUCCESS] yomitoku detected {len(ocr_results)} text blocks")

            # デバッグ: 最初の数個の結果を表示
            for i, (bbox, text, conf) in enumerate(ocr_results[:5]):
                print(f"  Result {i}: '{text}' (confidence: {conf:.2f})")

            return ocr_results

        except Exception as e:
            print(f"[WARNING] yomitoku OCR failed: {e}")
            import traceback
            traceback.print_exc()
            print("[INFO] Falling back to easyocr...")
            return self._run_easyocr(img)

    def _run_easyocr(self, img: np.ndarray) -> List:
        """easyocrでOCR実行（フォールバック）"""
        # readerが初期化されていない場合は初期化
        if self.reader is None:
            print("[INFO] Initializing easyocr...")
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
        print(f"[SUCCESS] easyocr detected {len(results)} text blocks")
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

            # 勝利/敗北/相打ちを検出（画面上部40%以内 - より広範囲で検出）
            if y_center < 0.4:  # 画面上部40%以内に拡張
                # 相打ちを最初にチェック（「打」を含むため）
                if "相打" in text or text == "相":
                    match_data["result"] = "相打ち"
                    print(f"  [DETECTED] Draw (from: '{text}')")
                elif "勝利" in text or text == "勝":
                    match_data["result"] = "勝利"
                    print(f"  [DETECTED] Victory (from: '{text}')")
                # 敗北パターンを拡張（部分一致も含む）
                elif "敗北" in text or text == "敗" or "失敗" in text or text == "失":
                    match_data["result"] = "敗北"
                    print(f"  [DETECTED] Defeat (from: '{text}')")

            # マップ名を検出
            for map_name in self.map_names:
                if map_name in text:
                    match_data["map_name"] = map_name
                    print(f"  [MAP] {map_name}")
                    break

            # 試合日時を検出（例: "11月2日12:57", "11/2 12:57", "11月2日12.42"）
            # ピリオド(.)もコロン(:)として扱う
            datetime_patterns = [
                # "11月2日12:57 使用時間" のような場合、使用時間の前だけマッチ
                r'(\d{1,2})月(\d{1,2})日[^\d：:\.]*(\d{1,2})[:．.](\d{2})',
                r'(\d{1,2})/(\d{1,2})\s*(\d{1,2})[:．.](\d{2})',     # "11/2 12:57", "11/2 12.57"
                r'(\d{1,2})-(\d{1,2})\s*(\d{1,2})[:．.](\d{2})',     # "11-2 12:57"
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
                            print(f"  [DATETIME] {month}/{day} {hour}:{minute:02d}")
                        except ValueError:
                            pass  # 無効な日付の場合はスキップ
                    break

            # 使用時間を検出（例: "使用時間:4:17", "使用時間：4:17", "使用時間 : 5.43"）
            # ピリオド(.)もコロン(:)として扱う
            time_patterns = [
                r'使用時間\s*[：:\s]*(\d{1,2})[:．.](\d{2})',  # "使用時間:4:17", "使用時間 : 5.43"
                r'時間\s*[：:\s]*(\d{1,2})[:．.](\d{2})',      # "時間:4:17", "時間 : 5.43"
            ]
            for pattern in time_patterns:
                time_match = re.search(pattern, text)
                if time_match and not match_data["duration"]:
                    minutes = int(time_match.group(1))
                    seconds = int(time_match.group(2))
                    # 試合時間は通常15分以内
                    if minutes <= 15:
                        match_data["duration"] = f"{minutes}:{seconds:02d}"
                        print(f"  [DURATION] {match_data['duration']}")
                        break

        # サバイバー情報を抽出（画像認識ベース）
        # 試合結果を渡して位置調整に使用
        survivors, detected_hunter = self._extract_survivors(sorted_results, img, match_data["result"])
        match_data["survivors"] = survivors

        # ハンター情報を設定
        if detected_hunter:
            match_data["hunter_character"] = detected_hunter
            print(f"[AUTO-DETECTED] Hunter: {detected_hunter}")

        # 勝敗が検出されなかった場合はデフォルト値を設定
        if match_data["result"] is None:
            match_data["result"] = "不明"
            print("[WARNING] Could not detect match result")

        return match_data
    
    def _extract_survivors(self, results: List, img: np.ndarray, match_result: str = None) -> Tuple[List[Dict], Optional[str]]:
        """サバイバー4人の情報とハンター情報を抽出（画像認識ベース）

        Returns:
            Tuple[List[Dict], Optional[str]]: (サバイバーリスト, ハンター名)
        """
        height, width = img.shape[:2]
        survivors = []
        detected_hunter = None

        # 1. キャラアイコンの位置を検出（画面サイズ対応）
        # 試合結果を渡して、敗北時の位置調整を行う
        icon_positions = self._detect_icon_positions(img, match_result)

        print(f"\n[START] Survivor recognition... (Screen size: {width}x{height})")

        # 2. 各位置でアイコンを認識
        for position, icon_data in enumerate(icon_positions, 1):
            # ハンター位置を判定
            # 勝利時: Position 1がハンター
            # 敗北時: Position 5がハンター
            if match_result == "敗北":
                is_hunter_position = (position == 5)
            else:
                is_hunter_position = (position == 1)

            print(f"\nPosition {position} (Expected: {'Hunter' if is_hunter_position else 'Survivor'}):")

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
            char_name, char_type = self._match_character_icon(
                img,
                icon_x,
                icon_y,
                width=icon_w,
                height=icon_h
            )

            # ハンター位置の特別処理
            if is_hunter_position:
                if char_type == "hunter":
                    print(f"  [INFO] Hunter detected: {char_name} - skipping survivor list")
                    detected_hunter = char_name
                else:
                    # ハンター位置で認識されたがサバイバーと判定された場合
                    # ハンターアイコンテンプレートが不足している可能性が高い
                    print(f"  [INFO] Position {position} recognized as survivor '{char_name}' - assuming this is hunter (icon template missing)")
                    print(f"  [INFO] Skipping position {position} (hunter position)")
                # ハンター位置は常にスキップ
                continue

            if char_name:
                survivor["character"] = char_name
                survivor["type"] = char_type  # ハンターかサバイバーか
            else:
                print(f"  [FAILED] Could not recognize character icon (position: x={icon_x}, y={icon_y})")

            # サバイバーの場合のみデータを取得
            if char_type == "survivor":
                # その行のテキストデータを取得
                row_data = self._get_row_text_data(results, icon_y + icon_h // 2, height)
                # 数値データを抽出
                survivor.update(row_data)

            # サバイバーのみ追加（ハンターは除外）
            if survivor["character"] and char_type == "survivor":
                survivors.append(survivor)
            elif char_type == "hunter":
                print(f"  [INFO] Hunter detected: {char_name} - skipping survivor list")

        print(f"\n[SUCCESS] Recognized {len(survivors)} survivors\n")
        if detected_hunter:
            print(f"[SUCCESS] Hunter detected: {detected_hunter}\n")

        return survivors, detected_hunter
    
    def _get_row_text_data(self, results: List, target_y: int, img_height: int) -> Dict:
        """
        指定Y座標付近のテキストデータから数値情報を抽出
        ※ グローバルOCR順序で、ラベルの次のテキストを値として使用

        Args:
            results: OCR結果（グローバル順序）
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

        # target_y付近（画面高さの±8%）のテキストを「グローバルresults内で」探す
        tolerance = int(img_height * 0.08)

        # グローバルOCR結果から、この行に関連するテキストを収集
        row_texts = []
        for idx, (bbox, text, conf) in enumerate(results):
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            if abs(y_center - target_y) < tolerance:
                row_texts.append((idx, bbox, text, conf))

        if not row_texts:
            return data

        # X座標でソート（左から右へ）、X座標が近い場合はY座標でソート（上から下へ）
        # X座標を30ピクセル単位で丸めることで、縦に並んでいるテキストを正しくソート
        def sort_key(item):
            idx, bbox, text, conf = item
            x_center = (bbox[0][0] + bbox[2][0]) / 2
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            # X座標を30ピクセル単位で丸める（より広い範囲でグループ化）
            x_rounded = round(x_center / 30) * 30
            return (x_rounded, y_center)

        row_texts.sort(key=sort_key)

        # デバッグ出力: この行に含まれるテキストのインデックスと内容
        print(f"    [DEBUG] Row contains {len(row_texts)} texts")
        for idx, bbox, text, conf in row_texts:
            x_center = (bbox[0][0] + bbox[2][0]) / 2
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            print(f"    [Global {idx}, X:{x_center:.1f}, Y:{y_center:.1f}] '{text}' (confidence: {conf:.2f})")

        # X座標順（左→右）で、ラベルを検出し、その次のテキストを値として取得
        # 注意: ラベル検出の順序が重要（より具体的なものを先にチェック）
        for i, (idx, bbox, text, conf) in enumerate(row_texts):
            clean_text = text.replace(" ", "").replace(",", "").replace(".", "")

            # 解読進捗ラベルを検出
            if '解読' in text or '進捗' in text or '進排' in text or '進度' in text:
                print(f"    [DEBUG] Found decode label at row index {i} (global {idx}): '{text}'")
                # 次のテキストを確認（row_texts内で次）
                if i + 1 < len(row_texts):
                    next_idx, next_bbox, next_text, next_conf = row_texts[i + 1]
                    next_clean = next_text.replace(" ", "").replace(",", "").replace(".", "")
                    print(f"    [DEBUG] Next text at row index {i+1} (global {next_idx}): '{next_text}'")

                    # パーセント表記を探す
                    # まず、oを0に変換、gを%に変換
                    next_clean_normalized = next_clean.replace('o', '0').replace('O', '0').replace('g', '%').replace('G', '%')

                    progress_patterns = [
                        r'(\d{1,3})\s*[%％]',  # "112%", "0%", "100%"
                        r'(\d{1,3})[9９]',  # "1129" (9が%の誤認識)
                    ]
                    for pattern in progress_patterns:
                        match = re.search(pattern, next_clean_normalized)
                        if match:
                            value = match.group(1)
                            # ０を0に変換
                            if value == '０':
                                value = '0'
                            data["decode_progress"] = value + "%"
                            print(f"  [DECODE] {data['decode_progress']} (from: '{next_text}')")
                            break

            # 牽制ラベルを検出（「制」「への」でも可）
            elif '牽制' in text or '制' in text or 'への' in text or 'ハンターへの' in text:
                print(f"    [DEBUG] Found kite label at row index {i} (global {idx}): '{text}'")
                # 次のテキストを確認（row_texts内で次）
                if i + 1 < len(row_texts):
                    next_idx, next_bbox, next_text, next_conf = row_texts[i + 1]
                    next_clean = next_text.replace(" ", "").replace(",", "").replace(".", "")
                    print(f"    [DEBUG] Next text at row index {i+1} (global {next_idx}): '{next_text}'")

                    # 時間表記を探す
                    # まず、O/o→0、G→6に変換
                    next_clean_normalized = next_clean.replace('O', '0').replace('o', '0').replace('G', '6').replace('g', '6')

                    time_patterns = [
                        r'(\d+)分(\d+)[sS秒]',  # "1分20s"
                        r'(\d+)[sS秒]',  # "20s", "34s", "60s"
                    ]
                    for pattern in time_patterns:
                        match = re.search(pattern, next_clean_normalized)
                        if match:
                            if '分' in next_clean_normalized:
                                minutes = int(match.group(1))
                                seconds = int(match.group(2))
                                total_seconds = minutes * 60 + seconds
                                data["kite_time"] = f"{total_seconds}s"
                            else:
                                time_value = match.group(1)
                                data["kite_time"] = time_value + "s"
                            print(f"  [KITE] {data['kite_time']} (from: '{next_text}')")
                            break

            # 援助/救助ラベルを検出（板より前にチェック）
            elif '援助' in text or '救助' in text:
                # このラベルのX座標とY座標を取得
                label_x = (bbox[0][0] + bbox[2][0]) / 2
                label_y = (bbox[0][1] + bbox[2][1]) / 2

                # このラベルの下（Y座標が大きく、X座標が近い）にある数値を探す
                for j in range(i + 1, len(row_texts)):
                    next_idx, next_bbox, next_text, next_conf = row_texts[j]
                    next_x = (next_bbox[0][0] + next_bbox[2][0]) / 2
                    next_y = (next_bbox[0][1] + next_bbox[2][1]) / 2
                    next_clean = next_text.replace(" ", "").replace(",", "").replace(".", "")

                    # X座標が近く（±50ピクセル以内）、Y座標がラベルより下にある
                    if abs(next_x - label_x) < 50 and next_y > label_y:
                        # 次のテキストがラベルでないことを確認
                        is_label = ('解読' in next_text or '進捗' in next_text or '進排' in next_text or
                                   '牽制' in next_text or '制' in next_text or 'への' in next_text or
                                   '板' in next_text or '援助' in next_text or '救助' in next_text or '治療' in next_text)

                        if not is_label:
                            # 単独の数字を探す
                            number_match = re.match(r'^(\d{1,2})$', next_clean)
                            if number_match:
                                value = int(number_match.group(1))
                                data["rescues"] = value
                                print(f"  [RESCUE] {value} (from: '{next_text}' at X:{next_x:.1f}, Y:{next_y:.1f})")
                                break

            # 板ラベルを検出（「板命中」全体をチェック）
            elif '板' in text and '命中' in text:
                # 次のテキストを確認（row_texts内で次）
                if i + 1 < len(row_texts):
                    next_idx, next_bbox, next_text, next_conf = row_texts[i + 1]
                    next_clean = next_text.replace(" ", "").replace(",", "").replace(".", "")

                    # 次のテキストがラベルでないことを確認
                    is_label = ('解読' in next_text or '進捗' in next_text or '進排' in next_text or
                               '牽制' in next_text or '制' in next_text or 'への' in next_text or
                               '板' in next_text or '援助' in next_text or '救助' in next_text or '治療' in next_text)

                    if not is_label:
                        # 単独の数字を探す
                        number_match = re.match(r'^(\d{1,2})$', next_clean)
                        if number_match:
                            value = int(number_match.group(1))
                            data["board_hits"] = value
                            print(f"  [BOARD] {value} (from: '{next_text}')")

            # 治療ラベルを検出
            elif '治療' in text:
                # このラベルのX座標とY座標を取得
                label_x = (bbox[0][0] + bbox[2][0]) / 2
                label_y = (bbox[0][1] + bbox[2][1]) / 2

                # このラベルの下（Y座標が大きく、X座標が近い）にある数値を探す
                for j in range(i + 1, len(row_texts)):
                    next_idx, next_bbox, next_text, next_conf = row_texts[j]
                    next_x = (next_bbox[0][0] + next_bbox[2][0]) / 2
                    next_y = (next_bbox[0][1] + next_bbox[2][1]) / 2
                    next_clean = next_text.replace(" ", "").replace(",", "").replace(".", "")

                    # X座標が近く（±50ピクセル以内）、Y座標がラベルより下にある
                    if abs(next_x - label_x) < 50 and next_y > label_y:
                        # 次のテキストがラベルでないことを確認
                        is_label = ('解読' in next_text or '進捗' in next_text or '進排' in next_text or
                                   '牽制' in next_text or '制' in next_text or 'への' in next_text or
                                   '板' in next_text or '援助' in next_text or '救助' in next_text or '治療' in next_text)

                        if not is_label:
                            # 単独の数字を探す
                            number_match = re.match(r'^(\d{1,2})$', next_clean)
                            if number_match:
                                value = int(number_match.group(1))
                                data["heals"] = value
                                print(f"  [HEAL] {value} (from: '{next_text}' at X:{next_x:.1f}, Y:{next_y:.1f})")
                                break

        return data
    
    def _match_character_icon(self, img: np.ndarray, x: int, y: int, width: int = 100, height: int = 100) -> Tuple[Optional[str], Optional[str]]:
        """
        指定座標周辺のキャラアイコンを画像マッチングで識別
        ハンターとサバイバーの両方をチェックして、最もマッチするものを返す

        Args:
            img: 元画像
            x, y: アイコンの左上座標
            width, height: アイコン領域のサイズ

        Returns:
            (キャラクター名, タイプ): タイプは"hunter"または"survivor"
        """
        if not self.survivor_templates and not self.hunter_templates:
            print("[WARNING] Icon templates not loaded")
            return None, None

        # アイコン領域を切り出し（周辺のパディングを含める）
        padding = int(width * 0.1)  # 10%のパディング
        y1 = max(0, y - padding)
        y2 = min(img.shape[0], y + height + padding)
        x1 = max(0, x - padding)
        x2 = min(img.shape[1], x + width + padding)

        icon_region = img[y1:y2, x1:x2]

        if icon_region.size == 0:
            return None, None

        # 各キャラクターのベストスコアを記録 (キャラ名: (スコア, タイプ))
        char_scores = {}

        # サバイバーをチェック
        for char_name, template_data in self.survivor_templates.items():
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

            char_scores[char_name] = (max_score_for_char, "survivor")

        # ハンターをチェック
        for char_name, template_data in self.hunter_templates.items():
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

            char_scores[char_name] = (max_score_for_char, "hunter")

        # スコアが最も高いキャラクターを選択
        if not char_scores:
            return None, None

        # スコアでソート (スコアの数値でソート)
        sorted_scores = sorted(char_scores.items(), key=lambda x: x[1][0], reverse=True)

        best_char, (best_score, char_type) = sorted_scores[0]

        # 閾値チェック（最低40%以上）
        if best_score < 0.40:
            print(f"  [FAILED] Score below threshold: {best_score:.2%} < 40%")
            return None, None

        # 2位との差が小さすぎる場合は信頼性が低いと判断
        if len(sorted_scores) > 1:
            second_score = sorted_scores[1][1][0]
            score_diff = best_score - second_score
            if score_diff < 0.05:  # 5%未満の差
                print(f"  [WARNING] Small difference from 2nd place: {score_diff:.2%} (1st: {best_score:.2%}, 2nd: {second_score:.2%})")
                # それでも採用するが警告を出す

        print(f"  [RECOGNIZED] [{char_type.upper()}] {best_char} (confidence: {best_score:.2%})")
        return best_char, char_type
    
    def _detect_icon_positions(self, img: np.ndarray, match_result: str = None) -> List[Tuple[int, int]]:
        """
        画像内のキャラアイコンの位置を検出（画面サイズ対応）

        勝利時: ハンター、サバイバー1、サバイバー2、サバイバー3、サバイバー4
        敗北時: サバイバー1、サバイバー2、サバイバー3、サバイバー4、ハンター

        Args:
            img: 入力画像
            match_result: 試合結果（敗北時はハンターが最後に表示）

        Returns:
            [(x, y, width, height), ...] のリスト（5箇所）
        """
        height, width = img.shape[:2]

        # 相対座標から実座標に変換
        icon_size = int(width * self.layout['icon_size_ratio'])
        x_start = int(width * self.layout['icon_x_ratio'][0])

        # Y座標オフセットを取得（デフォルトは0）
        y_offset = int(height * self.layout.get('icon_y_offset_ratio', 0.0))

        # 位置は常に同じ5箇所
        y_positions_ratio = [0.29, 0.42, 0.555, 0.69, 0.825]

        if match_result == "敗北":
            print(f"[POSITION] Detecting 5 positions (defeat: survivors 1-4, then hunter)")
        else:
            print(f"[POSITION] Detecting 5 positions (victory: hunter, then survivors 1-4)")

        positions = []
        for y_ratio in y_positions_ratio:
            y = int(height * y_ratio + y_offset)
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

