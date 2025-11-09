import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View, Modal, TextInput
import os
from dotenv import load_dotenv
from database import Database
from ocr_processor import OCRProcessor
from datetime import datetime, timedelta
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

db = Database()
ocr = OCRProcessor()

# 第五人格のゲームデータ
SURVIVOR_CHARACTERS = [
    "医師", "弁護士", "泥棒", "庭師", "マジシャン",
    "冒険家", "傭兵", "空軍", "祭司", "機械技師",
    "オフェンス", "心眼", "調香師", "カウボーイ", "踊り子",
    "占い師", "納棺師", "探鉱者", "呪術師", "野人",
    "曲芸師", "一等航海士", "バーメイド", "ポストマン", "墓守",
    "「囚人」", "昆虫学者", "画家", "バッツマン", "玩具職人",
    "患者", "「心理学者」", "小説家", "「少女」", "泣きピエロ",
    "教授", "骨董商", "作曲家", "記者", "航空エンジニア",
    "応援団", "人形師", "火災調査員", "「レディ・ファウロ」", "「騎士」",
    "気象学者", "弓使い", "「脱出マスター」", "幻灯師", "幸運児"
]

HUNTER_CHARACTERS = [
    "復讐者", "道化師", "断罪狩人", "リッパー", "結魂者",
    "芸者", "白黒無常", "写真家", "狂眼", "黄衣の王",
    "夢の魔女", "泣き虫", "魔トカゲ", "血の女王", "ガードNo.26",
    "「使徒」", "ヴァイオリニスト", "彫刻師", "「アンデッド」", "破輪",
    "漁師", "蝋人形師", "「悪夢」", "書記官", "隠者",
    "夜の番人", "オペラ歌手", "「フールズ・ゴールド」", "時空の影", "「足萎えの羊」",
    "フラバルー", "雑貨商", "「ビリヤードプレイヤー」"
]

TRAITS = [
    "リッスン", "異常", "興奮", "巡視者", "瞬間移動", "監視者", "神出鬼没", "移形"
]

MAPS = [
    "軍需工場", "赤の教会", "聖心病院", "月の河公園", "レオの思い出",
    "永眠町", "中華街", "罪の森"
]

# インタラクティブUI用のクラス
class PersonaModal(Modal, title="人格を入力"):
    """人格入力用のモーダル"""
    persona_input = TextInput(
        label="人格",
        placeholder="例: 右下上、左右、オペラ人格 など 自由入力",
        required=False,
        max_length=50
    )

    def __init__(self, match_data_list, trait, banned_chars):
        super().__init__()
        self.match_data_list = match_data_list if isinstance(match_data_list, list) else [match_data_list]
        self.trait = trait
        self.banned_chars = banned_chars

    async def on_submit(self, interaction: discord.Interaction):
        persona = self.persona_input.value.strip() if self.persona_input.value else None

        # 複数の画像データを保存
        saved_count = 0
        for match_data in self.match_data_list:
            # データを保存
            match_data["trait_used"] = self.trait
            match_data["persona"] = persona
            match_data["banned_characters"] = self.banned_chars

            # データベースに保存
            saved = db.save_match(str(interaction.user.id), match_data)
            if saved:
                saved_count += 1

        # 結果表示（複数画像対応）
        embed = discord.Embed(
            title=f"✅ {len(self.match_data_list)}件の試合を記録しました",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )

        # 最初の試合データのみ詳細表示
        match_data = self.match_data_list[0]

        # 試合日時
        if match_data.get("played_at"):
            try:
                from datetime import datetime as dt
                played_dt = dt.fromisoformat(match_data["played_at"])
                embed.add_field(
                    name="📅 試合日時",
                    value=played_dt.strftime("%m月%d日 %H:%M"),
                    inline=True
                )
            except:
                pass

        # 試合結果
        result_emoji = "🏆" if match_data.get("result") == "勝利" else "💀"
        embed.add_field(
            name=f"{result_emoji} 試合結果",
            value=match_data.get("result", "不明"),
            inline=True
        )

        # マップ
        embed.add_field(
            name="🗺️ マップ",
            value=match_data.get("map_name", "不明"),
            inline=True
        )

        # 時間
        embed.add_field(
            name="⏱️ 使用時間",
            value=match_data.get("duration", "不明"),
            inline=True
        )

        # ハンター情報
        hunter_name = match_data.get("hunter_character")
        if hunter_name:
            embed.add_field(name="🔪 ハンター", value=hunter_name, inline=True)
        if self.trait:
            embed.add_field(name="⚡ 特質", value=self.trait, inline=True)
        if persona:
            embed.add_field(name="🎭 人格", value=persona, inline=True)

        # Ban情報
        if self.banned_chars:
            embed.add_field(
                name="🚫 Banキャラ",
                value=", ".join(self.banned_chars),
                inline=False
            )

        # サバイバー情報
        survivors = match_data.get("survivors", [])
        if survivors:
            survivor_text = ""
            for i, s in enumerate(survivors, 1):
                char = s.get("character") or "不明"
                kite = s.get("kite_time") if s.get("kite_time") is not None else "-"
                decode = s.get("decode_progress") if s.get("decode_progress") is not None else "-"
                board = s.get("board_hits") if s.get("board_hits") is not None else "-"
                rescue = s.get("rescues") if s.get("rescues") is not None else "-"
                heal = s.get("heals") if s.get("heals") is not None else "-"

                survivor_text += f"`{i}.` **{char}**\n"
                survivor_text += f"   牽制: {kite} | 解読: {decode}\n"
                survivor_text += f"   板: {board} | 救助: {rescue} | 治療: {heal}\n"

            embed.add_field(
                name=f"👥 サバイバー ({len(survivors)}人検出)",
                value=survivor_text or "検出できませんでした",
                inline=False
            )

        embed.set_footer(text=f"記録者: {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)


class SelectionView(View):
    """特質とBanキャラ選択用のView（ボタンなし）"""
    def __init__(self, message=None):
        super().__init__(timeout=300)  # 5分のタイムアウト
        self.trait = None
        self.ban_page1 = []
        self.ban_page2 = []
        self.message = message  # メッセージ参照を保持
        self.ocr_complete = False

        # 特質選択メニュー
        trait_select = Select(
            placeholder="⚡ 特質を選択してください",
            options=[discord.SelectOption(label=trait, value=trait) for trait in TRAITS],
            custom_id="trait_select",
            row=0
        )
        trait_select.callback = self.trait_callback
        self.add_item(trait_select)

        # Ban - 前半 (医師〜墓守) - 最大3人選択
        ban_p1_select = Select(
            placeholder="🚫 Banキャラ - 前半 (医師〜墓守)",
            options=[discord.SelectOption(label=char, value=char) for char in SURVIVOR_CHARACTERS[:25]],
            custom_id="ban_p1_select",
            min_values=0,
            max_values=3,
            row=1
        )
        ban_p1_select.callback = self.ban_page1_callback
        self.add_item(ban_p1_select)

        # Ban - 後半 (「囚人」〜幸運児) - 最大3人選択
        ban_p2_select = Select(
            placeholder="🚫 Banキャラ - 後半 (「囚人」〜幸運児)",
            options=[discord.SelectOption(label=char, value=char) for char in SURVIVOR_CHARACTERS[25:]],
            custom_id="ban_p2_select",
            min_values=0,
            max_values=3,
            row=2
        )
        ban_p2_select.callback = self.ban_page2_callback
        self.add_item(ban_p2_select)

    def get_status_text(self):
        """現在の選択状態を表示するテキストを生成"""
        status = "📝 **特質とBanキャラを選択してください**\n\n"

        if self.ocr_complete:
            status += "✅ 画像解析完了\n\n"
        else:
            status += "🔄 画像を解析中...\n解析完了を待たずに、先に選択できます！\n\n"

        # 現在の選択状態を表示
        if self.trait:
            status += f"⚡ 特質: **{self.trait}**\n"

        all_bans = []
        if self.ban_page1:
            all_bans.extend(self.ban_page1)
        if self.ban_page2:
            all_bans.extend(self.ban_page2)

        if all_bans:
            status += f"🚫 Ban: **{', '.join(all_bans[:3])}**"

        return status

    async def update_status(self):
        """選択状態を反映してメッセージを更新"""
        if self.message:
            try:
                await self.message.edit(content=self.get_status_text(), view=self)
            except:
                pass

    async def trait_callback(self, interaction: discord.Interaction):
        self.trait = interaction.data["values"][0]
        try:
            await interaction.response.defer()
        except discord.errors.NotFound:
            pass
        await self.update_status()

    async def ban_page1_callback(self, interaction: discord.Interaction):
        self.ban_page1 = interaction.data["values"]
        try:
            await interaction.response.defer()
        except discord.errors.NotFound:
            pass
        await self.update_status()

    async def ban_page2_callback(self, interaction: discord.Interaction):
        self.ban_page2 = interaction.data["values"]
        try:
            await interaction.response.defer()
        except discord.errors.NotFound:
            pass
        await self.update_status()


class ConfirmButtonView(View):
    """確定ボタン専用のView（別メッセージ用）"""
    def __init__(self, match_data_list, selection_view):
        super().__init__(timeout=300)
        self.match_data_list = match_data_list if isinstance(match_data_list, list) else [match_data_list]
        self.selection_view = selection_view

    @discord.ui.button(label="確定して人格を入力", style=discord.ButtonStyle.primary, row=0)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Ban選択を統合
        banned_chars = []

        # 前半と後半のBanを統合
        if self.selection_view.ban_page1:
            banned_chars.extend(self.selection_view.ban_page1)
        if self.selection_view.ban_page2:
            banned_chars.extend(self.selection_view.ban_page2)

        # 重複削除
        unique_bans = []
        for char in banned_chars:
            if char not in unique_bans:
                unique_bans.append(char)

        # 3人までに制限
        if len(unique_bans) > 3:
            unique_bans = unique_bans[:3]

        # 人格入力モーダルを表示（複数画像データを渡す）
        modal = PersonaModal(self.match_data_list, self.selection_view.trait, unique_bans)
        await interaction.response.send_modal(modal)
        self.stop()
        self.selection_view.stop()


class LimitButtonView(View):
    """件数選択ボタン用の汎用View"""
    def __init__(self, user_id: str, stat_type: str, hunter: str = None):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.stat_type = stat_type  # "survivor", "kite", "map", "survivor_winrate"
        self.hunter = hunter

    @discord.ui.button(label="📊 最新10戦", style=discord.ButtonStyle.secondary, row=0)
    async def show_10_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await self._show_stats(interaction, 10)

    @discord.ui.button(label="📊 最新50戦", style=discord.ButtonStyle.secondary, row=0)
    async def show_50_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await self._show_stats(interaction, 50)

    @discord.ui.button(label="📊 最新100戦", style=discord.ButtonStyle.secondary, row=0)
    async def show_100_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await self._show_stats(interaction, 100)

    @discord.ui.button(label="📊 全て", style=discord.ButtonStyle.primary, row=0)
    async def show_all_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await self._show_stats(interaction, None)

    async def _show_stats(self, interaction: discord.Interaction, limit: int):
        """統計データを表示"""
        await interaction.response.defer()

        if self.stat_type == "survivor":
            await self._show_survivor_stats(interaction, limit)
        elif self.stat_type == "kite":
            await self._show_kite_stats(interaction, limit)
        elif self.stat_type == "map":
            await self._show_map_stats(interaction, limit)
        elif self.stat_type == "survivor_winrate":
            await self._show_survivor_winrate_stats(interaction, limit)

        self.stop()

    async def _show_survivor_stats(self, interaction: discord.Interaction, limit: int):
        """サバイバー統計を表示"""
        pick_rates = db.get_survivor_pick_rates(self.user_id, limit)

        if not pick_rates:
            await interaction.followup.send("まだデータがありません。")
            return

        limit_text = f"最新{limit}戦" if limit else "全期間"
        embed = discord.Embed(
            title=f"👥 サバイバーキャラ統計 ({limit_text})",
            description="対戦したサバイバーキャラのピック数",
            color=discord.Color.purple()
        )

        # Top 15
        for i, data in enumerate(pick_rates[:15], 1):
            embed.add_field(
                name=f"{i}. {data['character']}",
                value=f"**{data['picks']}回**",
                inline=True
            )

        await interaction.followup.send(embed=embed)

    async def _show_kite_stats(self, interaction: discord.Interaction, limit: int):
        """牽制統計を表示"""
        kite_data = db.get_avg_kite_time_by_survivor(self.user_id, self.hunter, limit)

        if not kite_data:
            await interaction.followup.send("まだデータがありません。")
            return

        limit_text = f"最新{limit}戦" if limit else "全期間"
        hunter_text = f" vs {self.hunter}" if self.hunter else ""
        embed = discord.Embed(
            title=f"⏱️ サバイバーごとの平均牽制時間{hunter_text} ({limit_text})",
            color=discord.Color.orange()
        )

        for i, data in enumerate(kite_data[:15], 1):
            embed.add_field(
                name=f"{i}. {data['character']}",
                value=f"平均: **{data['avg_kite_time']}** (n={data['samples']})",
                inline=True
            )

        await interaction.followup.send(embed=embed)

    async def _show_map_stats(self, interaction: discord.Interaction, limit: int):
        """マップ統計を表示"""
        map_data = db.get_win_rate_by_hunter_and_map(self.user_id, self.hunter, limit)

        if not map_data:
            await interaction.followup.send("まだデータがありません。")
            return

        limit_text = f"最新{limit}戦" if limit else "全期間"
        hunter_text = f" vs {self.hunter}" if self.hunter else ""
        embed = discord.Embed(
            title=f"🗺️ マップごとの勝率{hunter_text} ({limit_text})",
            color=discord.Color.green()
        )

        for data in map_data:
            embed.add_field(
                name=data['map'],
                value=f"**{data['win_rate']}** ({data['wins']}/{data['total']})",
                inline=True
            )

        await interaction.followup.send(embed=embed)

    async def _show_survivor_winrate_stats(self, interaction: discord.Interaction, limit: int):
        """サバイバー勝率統計を表示（ソートボタン付き）"""
        winrate_data = db.get_win_rate_by_survivor(self.user_id, limit)

        if not winrate_data:
            await interaction.followup.send("まだデータがありません。")
            return

        # ソート選択用のViewを表示
        sort_view = WinrateSortView(winrate_data, limit)
        limit_text = f"最新{limit}戦" if limit else "全期間"

        await interaction.followup.send(
            f"📊 サバイバーキャラごとの勝率 ({limit_text})\n\n表示順を選択してください:",
            view=sort_view
        )


class WinrateSortView(View):
    """勝率統計ソート選択用のView"""
    def __init__(self, winrate_data: list, limit: int):
        super().__init__(timeout=300)
        self.winrate_data = winrate_data
        self.limit = limit

    @discord.ui.button(label="📈 勝率が高い順", style=discord.ButtonStyle.primary, row=0)
    async def sort_high_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await interaction.response.defer()
        # 勝率の高い順にソート
        sorted_data = sorted(self.winrate_data, key=lambda x: x['win_rate'], reverse=True)
        await self._show_sorted_stats(interaction, sorted_data, "勝率が高い順")
        self.stop()

    @discord.ui.button(label="📉 勝率が低い順", style=discord.ButtonStyle.secondary, row=0)
    async def sort_low_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await interaction.response.defer()
        # 勝率の低い順にソート
        sorted_data = sorted(self.winrate_data, key=lambda x: x['win_rate'])
        await self._show_sorted_stats(interaction, sorted_data, "勝率が低い順")
        self.stop()

    @discord.ui.button(label="📊 試合数が多い順", style=discord.ButtonStyle.secondary, row=0)
    async def sort_matches_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await interaction.response.defer()
        # 試合数の多い順にソート（デフォルト）
        sorted_data = sorted(self.winrate_data, key=lambda x: x['total'], reverse=True)
        await self._show_sorted_stats(interaction, sorted_data, "試合数が多い順")
        self.stop()

    async def _show_sorted_stats(self, interaction: discord.Interaction, sorted_data: list, sort_type: str):
        """ソート済みの勝率統計を表示"""
        limit_text = f"最新{self.limit}戦" if self.limit else "全期間"
        embed = discord.Embed(
            title=f"📊 サバイバーキャラごとの勝率 ({limit_text})",
            description=f"表示順: {sort_type}",
            color=discord.Color.blue()
        )

        # Top 15
        for i, data in enumerate(sorted_data[:15], 1):
            # 勝率で色分け（高勝率は緑、低勝率は赤のエモジ）
            if data['win_rate'] >= 60:
                rate_emoji = "🟢"
            elif data['win_rate'] >= 40:
                rate_emoji = "🟡"
            else:
                rate_emoji = "🔴"

            # 新形式: "29勝12分15敗/56戦"
            embed.add_field(
                name=f"{i}. {data['character']}",
                value=f"{rate_emoji} **{data['win_rate_str']}** ({data['wins']}勝{data['draws']}分{data['losses']}敗/{data['total']}戦)",
                inline=True
            )

        await interaction.followup.send(embed=embed)


class HunterSelectView(View):
    """ハンター選択用のView（kite_stats, map_stats用）"""
    def __init__(self, user_id: str, stat_type: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.stat_type = stat_type  # "kite" or "map"
        self.selected_hunter = None

        # ハンター選択 - 前半 (row 0)
        hunter_p1_options = [discord.SelectOption(label="全て", value="all", default=True)]
        hunter_p1_options.extend([discord.SelectOption(label=h, value=h) for h in HUNTER_CHARACTERS[:23]])
        hunter_p1_select = Select(
            placeholder="🔪 ハンター - 前半",
            options=hunter_p1_options,
            row=0
        )
        hunter_p1_select.callback = self.hunter_callback
        self.add_item(hunter_p1_select)

        # ハンター選択 - 後半 (row 1)
        hunter_p2_options = [discord.SelectOption(label="全て", value="all")]
        hunter_p2_options.extend([discord.SelectOption(label=h, value=h) for h in HUNTER_CHARACTERS[23:]])
        hunter_p2_select = Select(
            placeholder="🔪 ハンター - 後半",
            options=hunter_p2_options,
            row=1
        )
        hunter_p2_select.callback = self.hunter_callback
        self.add_item(hunter_p2_select)

    async def hunter_callback(self, interaction: discord.Interaction):
        value = interaction.data["values"][0]
        self.selected_hunter = None if value == "all" else value
        try:
            await interaction.response.defer()
        except:
            pass

    @discord.ui.button(label="件数を選択", style=discord.ButtonStyle.primary, row=2)
    async def confirm_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        await interaction.response.defer()

        # 件数選択用のViewを表示
        limit_view = LimitButtonView(self.user_id, self.stat_type, self.selected_hunter)
        hunter_text = f"**{self.selected_hunter}**" if self.selected_hunter else "**全ハンター**"
        await interaction.followup.send(
            f"ハンター: {hunter_text}\n\n集計する試合数を選択してください:",
            view=limit_view
        )
        self.stop()


class DataFilterView(View):
    """データフィルタリング用のView"""
    def __init__(self, user_id: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.filters = {
            "hunter": None,
            "trait": None,
            "map": None,
            "limit": None
        }

        # 特質選択 (row 0)
        trait_options = [discord.SelectOption(label="全て", value="all", default=True)]
        trait_options.extend([discord.SelectOption(label=t, value=t) for t in TRAITS])
        trait_select = Select(
            placeholder="⚡ 特質を選択",
            options=trait_options,
            custom_id="trait_select",
            row=0
        )
        trait_select.callback = self.trait_callback
        self.add_item(trait_select)

        # マップ選択 (row 1)
        map_options = [discord.SelectOption(label="全て", value="all", default=True)]
        map_options.extend([discord.SelectOption(label=m, value=m) for m in MAPS])
        map_select = Select(
            placeholder="🗺️ マップを選択",
            options=map_options,
            custom_id="map_select",
            row=1
        )
        map_select.callback = self.map_callback
        self.add_item(map_select)

        # ハンター選択 - 前半 (row 2)
        hunter_p1_options = [discord.SelectOption(label="全て", value="all", default=True)]
        hunter_p1_options.extend([discord.SelectOption(label=h, value=h) for h in HUNTER_CHARACTERS[:23]])
        hunter_p1_select = Select(
            placeholder="🔪 ハンター - 前半",
            options=hunter_p1_options,
            custom_id="hunter_p1_select",
            row=2
        )
        hunter_p1_select.callback = self.hunter_callback
        self.add_item(hunter_p1_select)

        # ハンター選択 - 後半 (row 3)
        hunter_p2_options = [discord.SelectOption(label="全て", value="all")]
        hunter_p2_options.extend([discord.SelectOption(label=h, value=h) for h in HUNTER_CHARACTERS[23:]])
        hunter_p2_select = Select(
            placeholder="🔪 ハンター - 後半",
            options=hunter_p2_options,
            custom_id="hunter_p2_select",
            row=3
        )
        hunter_p2_select.callback = self.hunter_callback
        self.add_item(hunter_p2_select)

    async def hunter_callback(self, interaction: discord.Interaction):
        value = interaction.data["values"][0]
        self.filters["hunter"] = None if value == "all" else value
        try:
            await interaction.response.defer()
        except:
            pass

    async def trait_callback(self, interaction: discord.Interaction):
        value = interaction.data["values"][0]
        self.filters["trait"] = None if value == "all" else value
        try:
            await interaction.response.defer()
        except:
            pass

    async def map_callback(self, interaction: discord.Interaction):
        value = interaction.data["values"][0]
        self.filters["map"] = None if value == "all" else value
        try:
            await interaction.response.defer()
        except:
            pass

    @discord.ui.button(label="📊 最新10戦", style=discord.ButtonStyle.secondary, row=4)
    async def show_10_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        self.filters["limit"] = 10
        await self._show_data(interaction)

    @discord.ui.button(label="📊 最新50戦", style=discord.ButtonStyle.secondary, row=4)
    async def show_50_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        self.filters["limit"] = 50
        await self._show_data(interaction)

    @discord.ui.button(label="📊 最新100戦", style=discord.ButtonStyle.secondary, row=4)
    async def show_100_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        self.filters["limit"] = 100
        await self._show_data(interaction)

    @discord.ui.button(label="📊 全て表示", style=discord.ButtonStyle.primary, row=4)
    async def show_all_button(self, interaction: discord.Interaction, _button: discord.ui.Button):
        self.filters["limit"] = None
        await self._show_data(interaction)

    async def _show_data(self, interaction: discord.Interaction):
        """データを取得して表示"""
        await interaction.response.defer()

        # フィルター適用してデータ取得
        matches = db.get_filtered_matches(self.user_id, self.filters)

        if not matches:
            await interaction.followup.send("❌ 条件に一致するデータが見つかりませんでした。")
            self.stop()
            return

        # 統計計算
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

        win_rate = (wins / total * 100) if total > 0 else 0

        # フィルター条件を表示
        filter_text = []
        if self.filters["hunter"]:
            filter_text.append(f"🔪 ハンター: {self.filters['hunter']}")
        if self.filters["trait"]:
            filter_text.append(f"⚡ 特質: {self.filters['trait']}")
        if self.filters["map"]:
            filter_text.append(f"🗺️ マップ: {self.filters['map']}")
        if self.filters["limit"]:
            filter_text.append(f"📊 件数: 最新{self.filters['limit']}戦")
        else:
            filter_text.append(f"📊 件数: 全て")

        filter_summary = "\n".join(filter_text) if filter_text else "フィルターなし（全データ）"

        # Embed作成
        embed = discord.Embed(
            title="📊 試合データ",
            description=f"**絞り込み条件:**\n{filter_summary}",
            color=discord.Color.blue()
        )

        
        # 戦績を "29勝12分15敗/56戦" 形式で表示
        record_text = f"{wins}勝{draws}分{losses}敗/{total}戦"

        embed.add_field(
            name="📈 統計",
            value=f"勝率: **{win_rate:.1f}%**\n"
                  f"戦績: **{record_text}**",
            inline=False
        )

        # 最近の試合結果（最大10件）
        recent_matches = matches[:10]
        match_list = []
        for i, m in enumerate(recent_matches, 1):
            result_emoji = "🏆" if m.get("result") == "勝利" else "💀"
            hunter = m.get("hunter_character", "不明")
            map_name = m.get("map_name", "不明")
            duration = m.get("match_duration", "不明")
            match_list.append(f"`{i}.` {result_emoji} {hunter} | {map_name} | {duration}")

        if match_list:
            embed.add_field(
                name=f"🎮 最近の試合 (最大10件表示)",
                value="\n".join(match_list),
                inline=False
            )

        await interaction.followup.send(embed=embed)
        self.stop()


@bot.event
async def on_ready():
    print(f'✅ {bot.user} がログインしました！')
    print(f'Bot ID: {bot.user.id}')
    print('---------------------------')

@bot.command(name='record', aliases=['r'])
async def record_match(ctx):
    """
    試合結果を記録

    使い方:
    !record (画像を添付)

    ※画像を1枚または複数枚添付してください
    ※複数画像の場合、すべての画像に同じ特質・Ban・人格が適用されます
    ※ハンターは自動検出されます
    ※特質・Ban・人格は画像解析中に選択できます
    """
    if not ctx.message.attachments:
        await ctx.send(
            "❌ **画像を添付してください！**\n\n"
            "**使い方:**\n"
            "`!r` (画像添付)\n\n"
            "複数枚の画像を同時に添付できます。\n"
            "画像解析中に特質・Ban・人格を選択できます"
            "インタラクションに失敗しても無視してください"
        )
        return

    # 先に選択UIを表示
    selection_view = SelectionView()
    selection_msg = await ctx.send(
        selection_view.get_status_text(),
        view=selection_view
    )
    # メッセージ参照を設定
    selection_view.message = selection_msg

    # 複数画像の場合
    image_count = len(ctx.message.attachments)
    processing_msg = await ctx.send(f"🔄 {image_count}枚の画像を解析中...")

    try:
        # 複数画像を処理
        match_data_list = []
        results_summary = []

        for i, attachment in enumerate(ctx.message.attachments, 1):
            # 画像ダウンロード
            image_bytes = await attachment.read()

            # OCR処理
            match_data = ocr.process_image(image_bytes)
            match_data_list.append(match_data)

            # 簡易サマリー作成
            hunter_name = match_data.get("hunter_character", "不明")
            result = match_data.get("result", "不明")
            map_name = match_data.get("map_name", "不明")
            duration = match_data.get("duration", "不明")

            results_summary.append(
                f"`{i}.` **{result}** | {map_name} | {duration} | ハンター: {hunter_name}"
            )

        # OCR結果をまとめて表示
        summary_text = f"✅ **{image_count}件の画像解析完了！**\n\n" + "\n".join(results_summary)
        await processing_msg.edit(content=summary_text)

        # 選択メッセージを更新（OCR完了状態に）
        selection_view.ocr_complete = True
        await selection_view.update_status()

        # 確定ボタンを別メッセージで送信（複数画像データを渡す）
        button_view = ConfirmButtonView(match_data_list, selection_view)
        await ctx.send(
            f"⬇️ **選択が完了したら下のボタンを押してください**\n"
            f"（{image_count}件の試合に同じ設定が適用されます）",
            view=button_view
        )

    except Exception as e:
        await processing_msg.edit(
            content=f"❌ **エラーが発生しました**\n```{str(e)}```"
        )
        print(f"Error in record_match: {e}")
        import traceback
        traceback.print_exc()

@bot.command(name='view', aliases=['v'])
async def view_data(ctx):
    """
    データを絞り込んで表示

    使い方:
    !view または !v

    ※条件を選択してデータを表示できます
    """
    view = DataFilterView(str(ctx.author.id))
    await ctx.send(
        "📊 **データを絞り込んで表示**\n\n"
        "条件を選択して「データを表示」ボタンを押してください。\n"
        "※「全て」を選択すると、その条件ではフィルタリングされません",
        view=view
    )

@bot.command(name='stats', aliases=['s'])
async def show_stats(ctx):
    """全体統計を表示"""
    stats = db.get_overall_stats(str(ctx.author.id))

    embed = discord.Embed(
        title=f"📊 {ctx.author.display_name} の全体統計",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    # 戦績を "29勝12分15敗/56戦" 形式で表示
    record_text = f"{stats['wins']}勝{stats['draws']}分{stats['losses']}敗/{stats['total_matches']}戦"

    embed.add_field(name="📈 総試合数", value=stats["total_matches"], inline=True)
    embed.add_field(name="📊 勝率", value=stats["win_rate"], inline=True)
    embed.add_field(name="🏆 戦績", value=record_text, inline=False)

    await ctx.send(embed=embed)

@bot.command(name='survivor_stats', aliases=['ss'])
async def survivor_stats(ctx):
    """
    サバイバーキャラごとの統計

    使い方:
    !survivor_stats または !ss

    ※集計する試合数を選択できます
    """
    view = LimitButtonView(str(ctx.author.id), "survivor")
    await ctx.send(
        "👥 **サバイバーキャラ統計**\n\n"
        "集計する試合数を選択してください:",
        view=view
    )

@bot.command(name='winrate_stats', aliases=['ws'])
async def winrate_stats(ctx):
    """
    サバイバーキャラごとの勝率

    使い方:
    !winrate_stats または !ws

    ※集計する試合数を選択できます
    """
    view = LimitButtonView(str(ctx.author.id), "survivor_winrate")
    await ctx.send(
        "📊 **サバイバーキャラごとの勝率**\n\n"
        "集計する試合数を選択してください:",
        view=view
    )

@bot.command(name='kite_stats', aliases=['ks'])
async def kite_stats(ctx):
    """
    サバイバーごとの平均牽制時間

    使い方:
    !kite_stats または !ks

    ※ハンターを絞り込んで、集計する試合数を選択できます
    """
    view = HunterSelectView(str(ctx.author.id), "kite")
    await ctx.send(
        "⏱️ **サバイバーごとの平均牽制時間**\n\n"
        "ハンターを選択してください（全てでも可）:",
        view=view
    )

@bot.command(name='map_stats', aliases=['ms'])
async def map_stats(ctx):
    """
    マップごとの勝率

    使い方:
    !map_stats または !ms

    ※ハンターを絞り込んで、集計する試合数を選択できます
    """
    view = HunterSelectView(str(ctx.author.id), "map")
    await ctx.send(
        "🗺️ **マップごとの勝率**\n\n"
        "ハンターを選択してください（全てでも可）:",
        view=view
    )

@bot.command(name='history', aliases=['h'])
async def show_history(ctx):
    """
    最近の試合履歴

    使い方:
    !history または !h

    ※固定で最新5戦を表示します
    """
    matches = db.get_recent_matches(str(ctx.author.id), 5)

    if not matches:
        await ctx.send("まだ試合が記録されていません。\n`!record` で記録を開始しましょう！")
        return

    embed = discord.Embed(
        title=f"📋 最近の試合履歴 (最新5戦)",
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )

    for i, match in enumerate(matches, 1):
        result_emoji = "🏆" if match.get("result") == "勝利" else "💀"

        survivors = match.get("survivors", [])
        survivor_names = [s.get("character_name") for s in survivors if s.get("character_name")]

        # 試合日時を表示（played_atがない場合はmatch_dateを使用）
        field_value = ""
        date_displayed = False
        if match.get("played_at"):
            try:
                from datetime import datetime as dt
                played_dt = dt.fromisoformat(match["played_at"])
                field_value += f"📅 {played_dt.strftime('%m/%d %H:%M')}\n"
                date_displayed = True
            except:
                pass

        if not date_displayed and match.get("match_date"):
            try:
                from datetime import datetime as dt
                match_dt = dt.fromisoformat(match["match_date"])
                field_value += f"📅 {match_dt.strftime('%m/%d %H:%M')} (記録日時)\n"
            except:
                pass

        field_value += f"**{match.get('result', '不明')}** | {match.get('map_name', '不明')}\n"

        if match.get("hunter_character"):
            field_value += f"🔪 ハンター: {match.get('hunter_character')}\n"

        # サバイバーを全て表示
        if survivor_names:
            field_value += f"👥 サバイバー: {', '.join(survivor_names)}"
        else:
            field_value += f"👥 サバイバー: データなし"

        embed.add_field(
            name=f"{result_emoji} 試合 {i}",
            value=field_value,
            inline=False  # 横並びではなく縦に表示
        )

    await ctx.send(embed=embed)

@bot.command(name='help', aliases=['commands'])
async def show_help(ctx):
    """コマンド一覧"""
    embed = discord.Embed(
        title="🎮 第五人格 ハンター戦績Bot",
        description="試合結果のスクショで自動記録＆分析！\nOCRで自動認識、統計データで戦績を可視化",
        color=discord.Color.gold()
    )

    # 記録コマンド
    embed.add_field(
        name="📸 試合記録",
        value=(
            "`!record` または `!r`\n"
            "試合結果を記録（画像添付必須、複数枚可）\n"
            "• 特質・Ban・人格は選択メニューで入力\n"
            "• 複数画像は同じ設定で一括記録"
        ),
        inline=False
    )

    # データ閲覧コマンド
    embed.add_field(
        name="📊 データ閲覧",
        value=(
            "`!view` または `!v`\n"
            "条件を絞り込んでデータを表示\n"
            "• ハンター、特質、マップで絞り込み\n"
            "• 表示件数を選択（10/50/100/全て）"
        ),
        inline=False
    )

    # 統計コマンド
    embed.add_field(
        name="📈 統計コマンド",
        value=(
            "`!s` - 全体統計\n"
            "`!ss` - サバイバーピック数\n"
            "`!ws` - サバイバーごとの勝率\n"
            "`!ks` - 平均牽制時間\n"
            "`!ms` - マップごとの勝率\n"
            "`!h` - 最新5戦の履歴(試合日時準拠)"
        ),
        inline=False
    )

    # その他
    embed.add_field(
        name="ℹ️ その他",
        value="`!help` - このヘルプを表示",
        inline=False
    )

    embed.set_footer(text="💡 統計コマンドは件数選択・フィルタリングに対応")

    await ctx.send(embed=embed)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        print("❌ DISCORD_BOT_TOKENが設定されていません")
        exit(1)

    bot.run(TOKEN)
