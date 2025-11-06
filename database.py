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
        wins = len([m for m in matches if m.get("result") == "勝利"])
        
        return {
            "total_matches": total,
            "wins": wins,
            "losses": total - wins,
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
        wins = len([m for m in matches if m.get("result") == "勝利"])
        
        return {
            "period": f"{start_date} ~ {end_date}",
            "total": total,
            "wins": wins,
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
    
    def get_survivor_pick_rates(self, user_id: str) -> List[Dict]:
        """サバイバーキャラごとのピック回数"""
        response = self.supabase.table("survivors")\
            .select("character_name, match_id")\
            .execute()
        
        # user_idでフィルタ
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
    
    def get_win_rate_by_hunter_and_map(self, user_id: str, hunter: str = None) -> List[Dict]:
        """ハンターごとのマップごとの勝率"""
        query = self.supabase.table("matches")\
            .select("*")\
            .eq("user_id", user_id)
        
        if hunter:
            query = query.eq("hunter_character", hunter)
        
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
    
    def get_avg_kite_time_by_survivor(self, user_id: str) -> List[Dict]:
        """サバイバーキャラごとの平均牽制時間"""
        # matchesとsurvivorsを結合して取得
        response = self.supabase.table("survivors")\
            .select("character_name, kite_time, matches!inner(user_id)")\
            .eq("matches.user_id", user_id)\
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
        """最近の試合履歴"""
        response = self.supabase.table("matches")\
            .select("*, survivors(*)")\
            .eq("user_id", user_id)\
            .order("match_date", desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data
