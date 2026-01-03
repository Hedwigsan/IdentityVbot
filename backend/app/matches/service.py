from typing import List, Optional, Dict
from datetime import datetime
from ..database import get_supabase
from .schemas import MatchCreate, SurvivorData


class MatchService:
    """試合データのビジネスロジック"""

    def __init__(self):
        self.supabase = get_supabase()

    def create_match(self, user_id: str, match_data: MatchCreate) -> Dict:
        """試合データを保存"""
        # 1. 試合の基本情報を保存
        match_record = {
            "user_id": user_id,
            "match_date": datetime.now().isoformat(),
            "played_at": match_data.played_at.isoformat() if match_data.played_at else None,
            "result": match_data.result,
            "match_duration": match_data.match_duration,
            "hunter_character": match_data.hunter_character,
            "map_name": match_data.map_name,
            "trait_used": match_data.trait_used,
            "persona": match_data.persona,
            "banned_characters": match_data.banned_characters
        }

        response = self.supabase.table("matches").insert(match_record).execute()

        if not response.data:
            raise Exception("試合データの保存に失敗しました")

        match_id = response.data[0]["id"]

        # 2. サバイバーデータを保存
        for survivor in match_data.survivors:
            survivor_record = {
                "match_id": match_id,
                "character_name": survivor.character_name,
                "position": survivor.position,
                "kite_time": survivor.kite_time,
                "decode_progress": survivor.decode_progress,
                "board_hits": survivor.board_hits,
                "rescues": survivor.rescues,
                "heals": survivor.heals
            }
            self.supabase.table("survivors").insert(survivor_record).execute()

        return response.data[0]

    def get_match(self, user_id: str, match_id: int) -> Optional[Dict]:
        """試合詳細を取得"""
        response = self.supabase.table("matches")\
            .select("*, survivors(*)")\
            .eq("id", match_id)\
            .eq("user_id", user_id)\
            .single()\
            .execute()

        return response.data if response.data else None

    def get_matches(
        self,
        user_id: str,
        hunter: Optional[str] = None,
        trait: Optional[str] = None,
        map_name: Optional[str] = None,
        persona: Optional[str] = None,
        result: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """試合一覧を取得（フィルター対応）"""
        query = self.supabase.table("matches")\
            .select("*, survivors(*)")\
            .eq("user_id", user_id)

        if hunter:
            query = query.eq("hunter_character", hunter)

        if trait:
            query = query.eq("trait_used", trait)

        if map_name:
            query = query.eq("map_name", map_name)

        if persona:
            query = query.eq("persona", persona)

        if result:
            query = query.eq("result", result)

        query = query.order("match_date", desc=True)

        if limit:
            query = query.limit(limit)

        response = query.execute()
        return response.data

    def delete_match(self, user_id: str, match_id: int) -> bool:
        """試合を削除"""
        # まず所有権を確認
        match = self.get_match(user_id, match_id)
        if not match:
            return False

        # サバイバーは CASCADE で自動削除
        self.supabase.table("matches")\
            .delete()\
            .eq("id", match_id)\
            .eq("user_id", user_id)\
            .execute()

        return True

    def get_recent_matches(self, user_id: str, limit: int = 5) -> List[Dict]:
        """最近の試合履歴を取得"""
        response = self.supabase.table("matches")\
            .select("*, survivors(*)")\
            .eq("user_id", user_id)\
            .order("played_at", desc=True, nullsfirst=False)\
            .order("match_date", desc=True)\
            .limit(limit)\
            .execute()

        return response.data


# シングルトンインスタンス
match_service = MatchService()
