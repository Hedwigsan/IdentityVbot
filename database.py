import os
from supabase import create_client, Client
from datetime import datetime
from typing import Dict, List, Optional

class Database:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)
    
    def save_match(self, user_id: str, match_data: Dict) -> Dict:
        """試合データを保存（ハンター情報 + サバイバー4人）"""

        # 1. 試合の基本情報を保存
        match_record = {
            "user_id": user_id,
            "match_date": datetime.now().isoformat(),
            "played_at": match_data.get("played_at"),  # 実際の試合日時
            "result": match_data.get("result"),
            "match_duration": match_data.get("duration"),
            "hunter_character": match_data.get("hunter_character"),
            "map_name": match_data.get("map_name"),
            "trait_used": match_data.get("trait_used"),
            "persona": match_data.get("persona"),
            "banned_characters": match_data.get("banned_characters", [])
        }
        
        response = self.supabase.table("matches").insert(match_record).execute()
        
        if not response.data:
            raise Exception("試合データの保存に失敗しました")
        
        match_id = response.data[0]["id"]
        
        # 2. サバイバー4人のデータを保存
        survivors = match_data.get("survivors", [])
        for survivor in survivors:
            survivor_record = {
                "match_id": match_id,
                "character_name": survivor.get("character"),
                "position": survivor.get("position"),
                "kite_time": survivor.get("kite_time"),
                "decode_progress": survivor.get("decode_progress"),
                "board_hits": survivor.get("board_hits", 0),
                "rescues": survivor.get("rescues", 0),
                "heals": survivor.get("heals", 0)
            }
            self.supabase.table("survivors").insert(survivor_record).execute()
        
        return response.data[0]
    
    def get_overall_stats(self, user_id: str) -> Dict:
        """全体統計"""
        response = self.supabase.table("matches")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()

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
    
    def get_win_rate_by_period(self, user_id: str, start_date: str, end_date: str) -> Dict:
        """期間ごとの勝率"""
        response = self.supabase.table("matches")\
            .select("*")\
            .eq("user_id", user_id)\
            .gte("match_date", start_date)\
            .lte("match_date", end_date)\
            .execute()

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
            "period": f"{start_date} ~ {end_date}",
            "total": total,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "win_rate": f"{(wins/total*100):.1f}%" if total > 0 else "0%"
        }
    
    def get_win_rate_by_survivor(self, user_id: str) -> List[Dict]:
        """サバイバーキャラごとの勝率"""
        # カスタムクエリ実行
        response = self.supabase.rpc(
            "get_survivor_win_rates",
            {"p_user_id": user_id}
        ).execute()

        return response.data

    def get_filtered_matches(self, user_id: str, filters: Dict) -> List[Dict]:
        """条件を指定して試合データを取得

        Args:
            user_id: ユーザーID
            filters: {
                "hunter": str | None,
                "trait": str | None,
                "persona": str | None,
                "map": str | None,
                "limit": int | None (10, 50, 100, None=全て)
            }
        """
        query = self.supabase.table("matches").select("*").eq("user_id", user_id)

        # フィルター適用
        if filters.get("hunter"):
            query = query.eq("hunter_character", filters["hunter"])

        if filters.get("trait"):
            query = query.eq("trait_used", filters["trait"])

        if filters.get("persona"):
            query = query.eq("persona", filters["persona"])

        if filters.get("map"):
            query = query.eq("map_name", filters["map"])

        # 最新順にソート
        query = query.order("match_date", desc=True)

        # 件数制限
        if filters.get("limit"):
            query = query.limit(filters["limit"])

        response = query.execute()
        return response.data
    
    def get_survivor_pick_rates(self, user_id: str, limit: int = None) -> List[Dict]:
        """サバイバーキャラごとのピック回数

        Args:
            user_id: ユーザーID
            limit: 集計する試合数制限（最新N戦）
        """
        # 最新のmatch_idを取得
        matches_query = self.supabase.table("matches")\
            .select("id")\
            .eq("user_id", user_id)\
            .order("match_date", desc=True)

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
    
    def get_win_rate_by_hunter_and_map(self, user_id: str, hunter: str = None, limit: int = None) -> List[Dict]:
        """ハンターごとのマップごとの勝率

        Args:
            user_id: ユーザーID
            hunter: ハンター名でフィルタ（Noneの場合全ハンター）
            limit: 集計する試合数制限（最新N戦）
        """
        query = self.supabase.table("matches")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("match_date", desc=True)

        if hunter:
            query = query.eq("hunter_character", hunter)

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
                map_stats[map_name] = {"total": 0, "wins": 0}

            map_stats[map_name]["total"] += 1
            if m.get("result") == "勝利":
                map_stats[map_name]["wins"] += 1

        result = []
        for map_name, stats in map_stats.items():
            win_rate = (stats["wins"] / stats["total"] * 100) if stats["total"] > 0 else 0
            result.append({
                "map": map_name,
                "total": stats["total"],
                "wins": stats["wins"],
                "win_rate": f"{win_rate:.1f}%"
            })

        return sorted(result, key=lambda x: x["total"], reverse=True)
    
    def get_avg_kite_time_by_survivor(self, user_id: str, hunter: str = None, limit: int = None) -> List[Dict]:
        """サバイバーキャラごとの平均牽制時間

        Args:
            user_id: ユーザーID
            hunter: ハンター名でフィルタ（Noneの場合全ハンター）
            limit: 集計する試合数制限（最新N戦）
        """
        # 最新のmatch_idを取得
        matches_query = self.supabase.table("matches")\
            .select("id")\
            .eq("user_id", user_id)\
            .order("match_date", desc=True)

        if hunter:
            matches_query = matches_query.eq("hunter_character", hunter)

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
    
    def get_win_rate_by_ban(self, user_id: str) -> List[Dict]:
        """Banキャラごとの勝率"""
        response = self.supabase.table("matches")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()
        
        matches = response.data
        
        # Banキャラごとに集計
        ban_stats = {}
        for m in matches:
            banned = m.get("banned_characters", [])
            result = m.get("result")
            
            for char in banned:
                if char not in ban_stats:
                    ban_stats[char] = {"total": 0, "wins": 0}
                
                ban_stats[char]["total"] += 1
                if result == "勝利":
                    ban_stats[char]["wins"] += 1
        
        result = []
        for char, stats in ban_stats.items():
            win_rate = (stats["wins"] / stats["total"] * 100) if stats["total"] > 0 else 0
            result.append({
                "banned_character": char,
                "total": stats["total"],
                "wins": stats["wins"],
                "win_rate": f"{win_rate:.1f}%"
            })
        
        return sorted(result, key=lambda x: x["total"], reverse=True)
    
    def get_recent_matches(self, user_id: str, limit: int = 10) -> List[Dict]:
        """最近の試合履歴（対戦日時の最新順、played_atがNULLの場合はmatch_dateでソート）"""
        response = self.supabase.table("matches")\
            .select("*, survivors(*)")\
            .eq("user_id", user_id)\
            .order("played_at", desc=True, nullsfirst=False)\
            .order("match_date", desc=True)\
            .limit(limit)\
            .execute()

        return response.data

    def get_win_rate_by_survivor(self, user_id: str, limit: int = None) -> List[Dict]:
        """サバイバーキャラごとの勝率

        Args:
            user_id: ユーザーID
            limit: 集計する試合数制限（最新N戦）
        """
        # 最新のmatch_idを取得
        matches_query = self.supabase.table("matches")\
            .select("id, result")\
            .eq("user_id", user_id)\
            .order("match_date", desc=True)

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

        # 試合数でソート（多い順）
        return sorted(result, key=lambda x: x["total"], reverse=True)
