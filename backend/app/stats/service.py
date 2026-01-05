from typing import List, Optional, Dict
from ..database import get_supabase


class StatsService:
    """統計計算サービス"""

    def __init__(self):
        self.supabase = get_supabase()

    def get_overall_stats(self, user_id: str, hunter: str = None, persona: str = None, banned_characters: List[str] = None) -> Dict:
        """全体統計"""
        query = self.supabase.table("matches")\
            .select("*")\
            .eq("user_id", user_id)

        if hunter:
            query = query.eq("hunter_character", hunter)

        if persona:
            query = query.eq("persona", persona)

        if banned_characters:
            # banned_charactersはJSON配列として格納されているため、contains演算子を使用
            for banned_char in banned_characters:
                query = query.contains("banned_characters", [banned_char])

        response = query.execute()
        matches = response.data
        total = len(matches)
        wins = 0
        draws = 0
        losses = 0

        for m in matches:
            result = m.get("result")
            if result == "勝利":
                wins += 1
            elif result in ["辛勝", "平局", "引き分け"]:
                draws += 1
            else:
                losses += 1

        return {
            "total_matches": total,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "win_rate": f"{(wins/total*100):.1f}%" if total > 0 else "0%"
        }

    def get_survivor_pick_rates(self, user_id: str, hunter: str = None, limit: int = None, persona: str = None, banned_characters: List[str] = None) -> List[Dict]:
        """サバイバーキャラごとのピック回数"""
        # 最新のmatch_idを取得
        matches_query = self.supabase.table("matches")\
            .select("id")\
            .eq("user_id", user_id)\
            .order("match_date", desc=True)

        if hunter:
            matches_query = matches_query.eq("hunter_character", hunter)

        if persona:
            matches_query = matches_query.eq("persona", persona)

        if banned_characters:
            for banned_char in banned_characters:
                matches_query = matches_query.contains("banned_characters", [banned_char])

        if limit:
            matches_query = matches_query.limit(limit)

        matches_response = matches_query.execute()
        match_ids = [m["id"] for m in matches_response.data]

        if not match_ids:
            return []

        # survivorsテーブルから該当試合のサバイバーを取得
        response = self.supabase.table("survivors")\
            .select("character_name")\
            .in_("match_id", match_ids)\
            .execute()

        survivors = response.data

        # 集計
        pick_counts = {}
        for s in survivors:
            char = s.get("character_name")
            if char:
                pick_counts[char] = pick_counts.get(char, 0) + 1

        # ソート
        result = [{"character": k, "picks": v} for k, v in pick_counts.items()]
        result.sort(key=lambda x: x["picks"], reverse=True)

        return result

    def get_survivor_winrate(self, user_id: str, hunter: str = None, limit: int = None, persona: str = None, banned_characters: List[str] = None) -> List[Dict]:
        """サバイバーキャラごとの勝率"""
        # 最新のmatch_idを取得
        matches_query = self.supabase.table("matches")\
            .select("id, result")\
            .eq("user_id", user_id)\
            .order("match_date", desc=True)

        if hunter:
            matches_query = matches_query.eq("hunter_character", hunter)

        if persona:
            matches_query = matches_query.eq("persona", persona)

        if banned_characters:
            for banned_char in banned_characters:
                matches_query = matches_query.contains("banned_characters", [banned_char])

        if limit:
            matches_query = matches_query.limit(limit)

        matches_response = matches_query.execute()
        matches_dict = {m["id"]: m["result"] for m in matches_response.data}

        if not matches_dict:
            return []

        # survivorsテーブルから該当試合のサバイバーを取得
        response = self.supabase.table("survivors")\
            .select("character_name, match_id")\
            .in_("match_id", list(matches_dict.keys()))\
            .execute()

        survivors = response.data

        # キャラごとに勝率を集計
        survivor_stats = {}
        for s in survivors:
            char = s.get("character_name")
            match_id = s.get("match_id")

            if not char or match_id not in matches_dict:
                continue

            if char not in survivor_stats:
                survivor_stats[char] = {"total": 0, "wins": 0, "draws": 0, "losses": 0}

            survivor_stats[char]["total"] += 1
            result_text = matches_dict[match_id]
            if result_text == "勝利":
                survivor_stats[char]["wins"] += 1
            elif result_text in ["辛勝", "平局", "引き分け"]:
                survivor_stats[char]["draws"] += 1
            else:
                survivor_stats[char]["losses"] += 1

        # 結果を整形
        result = []
        for char, stats in survivor_stats.items():
            win_rate = (stats["wins"] / stats["total"] * 100) if stats["total"] > 0 else 0
            result.append({
                "character": char,
                "total": stats["total"],
                "wins": stats["wins"],
                "draws": stats["draws"],
                "losses": stats["losses"],
                "win_rate": win_rate,
                "win_rate_str": f"{win_rate:.1f}%"
            })

        # 勝率でソート（高い順）
        return sorted(result, key=lambda x: x["win_rate"], reverse=True)

    def get_avg_kite_time(self, user_id: str, hunter: str = None, limit: int = None, persona: str = None, banned_characters: List[str] = None) -> List[Dict]:
        """サバイバーキャラごとの平均牽制時間"""
        # 最新のmatch_idを取得
        matches_query = self.supabase.table("matches")\
            .select("id")\
            .eq("user_id", user_id)\
            .order("match_date", desc=True)

        if hunter:
            matches_query = matches_query.eq("hunter_character", hunter)

        if persona:
            matches_query = matches_query.eq("persona", persona)

        if banned_characters:
            for banned_char in banned_characters:
                matches_query = matches_query.contains("banned_characters", [banned_char])

        if limit:
            matches_query = matches_query.limit(limit)

        matches_response = matches_query.execute()
        match_ids = [m["id"] for m in matches_response.data]

        if not match_ids:
            return []

        # survivorsテーブルから該当試合のサバイバーを取得
        response = self.supabase.table("survivors")\
            .select("character_name, kite_time")\
            .in_("match_id", match_ids)\
            .execute()

        survivors = response.data

        # キャラごとに牽制時間を集計
        kite_data = {}
        for s in survivors:
            char = s.get("character_name")
            kite_time_str = s.get("kite_time", "0s")

            if not char or not kite_time_str:
                continue

            # "20s", "34s" などから秒数を抽出
            try:
                seconds = int(kite_time_str.replace("s", ""))
            except:
                continue

            if char not in kite_data:
                kite_data[char] = []
            kite_data[char].append(seconds)

        # 平均計算
        result = []
        for char, times in kite_data.items():
            avg = sum(times) / len(times)
            result.append({
                "character": char,
                "avg_kite_time": f"{avg:.1f}s",
                "samples": len(times)
            })

        return sorted(result, key=lambda x: float(x["avg_kite_time"].replace("s", "")), reverse=True)

    def get_map_stats(self, user_id: str, hunter: str = None, limit: int = None, persona: str = None, banned_characters: List[str] = None) -> List[Dict]:
        """マップごとの勝率"""
        query = self.supabase.table("matches")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("match_date", desc=True)

        if hunter:
            query = query.eq("hunter_character", hunter)

        if persona:
            query = query.eq("persona", persona)

        if banned_characters:
            for banned_char in banned_characters:
                query = query.contains("banned_characters", [banned_char])

        if limit:
            query = query.limit(limit)

        response = query.execute()
        matches = response.data

        # マップごとに集計
        map_stats = {}
        for m in matches:
            map_name = m.get("map_name")
            if not map_name:
                continue

            if map_name not in map_stats:
                map_stats[map_name] = {"total": 0, "wins": 0, "draws": 0, "losses": 0}

            map_stats[map_name]["total"] += 1
            result_text = m.get("result")
            if result_text == "勝利":
                map_stats[map_name]["wins"] += 1
            elif result_text in ["辛勝", "平局", "引き分け"]:
                map_stats[map_name]["draws"] += 1
            else:
                map_stats[map_name]["losses"] += 1

        result = []
        for map_name, stats in map_stats.items():
            win_rate = (stats["wins"] / stats["total"] * 100) if stats["total"] > 0 else 0
            result.append({
                "map_name": map_name,
                "total": stats["total"],
                "wins": stats["wins"],
                "draws": stats["draws"],
                "losses": stats["losses"],
                "win_rate": f"{win_rate:.1f}%"
            })

        return sorted(result, key=lambda x: x["total"], reverse=True)

    def get_recent_personas(self, user_id: str, limit: int = 10) -> List[str]:
        """最近使用した人格リストを取得"""
        response = self.supabase.table("matches")\
            .select("persona")\
            .eq("user_id", user_id)\
            .not_.is_("persona", "null")\
            .order("match_date", desc=True)\
            .limit(50)\
            .execute()

        # 重複を除いて最新limit件を返す
        personas = []
        seen = set()
        for m in response.data:
            persona = m.get("persona")
            if persona and persona not in seen:
                personas.append(persona)
                seen.add(persona)
            if len(personas) >= limit:
                break

        return personas


# シングルトンインスタンス
stats_service = StatsService()
