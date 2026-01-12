import logging
from typing import Optional, List, Dict, Any
from decimal import Decimal
from supabase import Client
from .schemas import DeviceLayoutCreate, DeviceLayoutResponse, IconPosition

logger = logging.getLogger(__name__)


class LayoutService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def get_best_layout(self, aspect_ratio: float, tolerance: float = 0.05) -> Optional[DeviceLayoutResponse]:
        """
        指定されたアスペクト比に最も近いレイアウトを取得（投票数が最も多いもの）

        Args:
            aspect_ratio: 検索するアスペクト比
            tolerance: 許容範囲（デフォルト: ±0.05）

        Returns:
            最適なレイアウト、または見つからない場合はNone
        """
        try:
            min_ratio = aspect_ratio - tolerance
            max_ratio = aspect_ratio + tolerance

            logger.info(f"Searching for layout with aspect ratio {aspect_ratio} (range: {min_ratio} - {max_ratio})")

            # アスペクト比の範囲内で、投票数が最も多いレイアウトを取得
            response = self.supabase.table('device_layouts').select('*').gte('aspect_ratio', min_ratio).lte('aspect_ratio', max_ratio).order('vote_count', desc=True).order('updated_at', desc=True).limit(1).execute()

            if not response.data:
                logger.info("No matching layout found")
                return None

            layout_data = response.data[0]
            logger.info(f"Found layout: ID={layout_data['id']}, aspect_ratio={layout_data['aspect_ratio']}, votes={layout_data['vote_count']}")

            # icon_positionsをIconPositionオブジェクトのリストに変換
            icon_positions = [IconPosition(**pos) for pos in layout_data['icon_positions']]

            return DeviceLayoutResponse(
                id=layout_data['id'],
                aspect_ratio=Decimal(str(layout_data['aspect_ratio'])),
                screen_width=layout_data['screen_width'],
                screen_height=layout_data['screen_height'],
                icon_positions=icon_positions,
                vote_count=layout_data['vote_count'],
                created_at=layout_data['created_at'],
                updated_at=layout_data['updated_at']
            )

        except Exception as e:
            logger.error(f"Error getting best layout: {e}")
            return None

    def find_similar_layout(self, layout_create: DeviceLayoutCreate, tolerance: float = 0.01) -> Optional[str]:
        """
        同じアスペクト比と位置の既存レイアウトを検索

        Args:
            layout_create: 検索するレイアウト情報
            tolerance: 位置の許容誤差（デフォルト: 0.01 = 1%）

        Returns:
            見つかった場合はレイアウトID、見つからない場合はNone
        """
        try:
            aspect_ratio_tolerance = 0.05
            min_ratio = float(layout_create.aspect_ratio) - aspect_ratio_tolerance
            max_ratio = float(layout_create.aspect_ratio) + aspect_ratio_tolerance

            # アスペクト比の範囲内のレイアウトを取得
            response = self.supabase.table('device_layouts').select('*').gte('aspect_ratio', min_ratio).lte('aspect_ratio', max_ratio).execute()

            if not response.data:
                return None

            # 位置が近いレイアウトを探す
            new_positions = [pos.dict() for pos in layout_create.icon_positions]

            for existing in response.data:
                existing_positions = existing['icon_positions']

                # 全ての位置が許容範囲内かチェック
                if self._positions_match(new_positions, existing_positions, tolerance):
                    logger.info(f"Found similar layout: ID={existing['id']}")
                    return existing['id']

            return None

        except Exception as e:
            logger.error(f"Error finding similar layout: {e}")
            return None

    def _positions_match(self, positions1: List[Dict], positions2: List[Dict], tolerance: float) -> bool:
        """2つの位置リストが許容範囲内で一致するかチェック"""
        if len(positions1) != len(positions2):
            return False

        for p1, p2 in zip(positions1, positions2):
            if (abs(p1['x_ratio'] - p2['x_ratio']) > tolerance or
                abs(p1['y_ratio'] - p2['y_ratio']) > tolerance or
                abs(p1['size_ratio'] - p2['size_ratio']) > tolerance):
                return False

        return True

    def create_layout(self, layout_create: DeviceLayoutCreate) -> DeviceLayoutResponse:
        """
        新しいレイアウトを作成

        Args:
            layout_create: 作成するレイアウト情報

        Returns:
            作成されたレイアウト
        """
        try:
            # icon_positionsをdict形式に変換
            icon_positions_dict = [pos.dict() for pos in layout_create.icon_positions]

            data = {
                'aspect_ratio': float(layout_create.aspect_ratio),
                'screen_width': layout_create.screen_width,
                'screen_height': layout_create.screen_height,
                'icon_positions': icon_positions_dict,
                'vote_count': 1
            }

            response = self.supabase.table('device_layouts').insert(data).execute()

            if not response.data:
                raise Exception("Failed to create layout")

            layout_data = response.data[0]
            logger.info(f"Created new layout: ID={layout_data['id']}")

            icon_positions = [IconPosition(**pos) for pos in layout_data['icon_positions']]

            return DeviceLayoutResponse(
                id=layout_data['id'],
                aspect_ratio=Decimal(str(layout_data['aspect_ratio'])),
                screen_width=layout_data['screen_width'],
                screen_height=layout_data['screen_height'],
                icon_positions=icon_positions,
                vote_count=layout_data['vote_count'],
                created_at=layout_data['created_at'],
                updated_at=layout_data['updated_at']
            )

        except Exception as e:
            logger.error(f"Error creating layout: {e}")
            raise

    def vote_layout(self, layout_id: str) -> DeviceLayoutResponse:
        """
        既存のレイアウトに投票（vote_countを+1）

        Args:
            layout_id: 投票するレイアウトのID

        Returns:
            更新されたレイアウト
        """
        try:
            # 現在のvote_countを取得
            response = self.supabase.table('device_layouts').select('vote_count').eq('id', layout_id).single().execute()

            if not response.data:
                raise Exception(f"Layout not found: {layout_id}")

            current_votes = response.data['vote_count']
            new_votes = current_votes + 1

            # vote_countを更新
            update_response = self.supabase.table('device_layouts').update({
                'vote_count': new_votes,
                'updated_at': 'NOW()'
            }).eq('id', layout_id).execute()

            if not update_response.data:
                raise Exception("Failed to update vote count")

            layout_data = update_response.data[0]
            logger.info(f"Voted for layout: ID={layout_id}, new vote_count={new_votes}")

            icon_positions = [IconPosition(**pos) for pos in layout_data['icon_positions']]

            return DeviceLayoutResponse(
                id=layout_data['id'],
                aspect_ratio=Decimal(str(layout_data['aspect_ratio'])),
                screen_width=layout_data['screen_width'],
                screen_height=layout_data['screen_height'],
                icon_positions=icon_positions,
                vote_count=layout_data['vote_count'],
                created_at=layout_data['created_at'],
                updated_at=layout_data['updated_at']
            )

        except Exception as e:
            logger.error(f"Error voting for layout: {e}")
            raise

    def save_layout(self, layout_create: DeviceLayoutCreate) -> DeviceLayoutResponse:
        """
        レイアウトを保存（既存の類似レイアウトがあれば投票、なければ新規作成）

        Args:
            layout_create: 保存するレイアウト情報

        Returns:
            保存されたレイアウト
        """
        # 類似レイアウトを検索
        existing_id = self.find_similar_layout(layout_create)

        if existing_id:
            # 既存レイアウトに投票
            logger.info(f"Similar layout found, voting for: {existing_id}")
            return self.vote_layout(existing_id)
        else:
            # 新規作成
            logger.info("No similar layout found, creating new one")
            return self.create_layout(layout_create)
