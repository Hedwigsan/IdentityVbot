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
    "「フラバルー」", "雑貨商", "「ビリヤードプレイヤー」"
]

TRAITS = [
    "リッスン", "異常", "興奮", "巡視者", "瞬間移動", "監視者", "神出鬼没", "移形"
]

# インタラクティブUI用のクラス
class PersonaModal(Modal, title="人格を入力"):
    """人格入力用のモーダル"""
    persona_input = TextInput(
        label="人格",
        placeholder="例: 中治り、左右、破壊欲 など",
        required=False,
        max_length=50
    )

    def __init__(self, match_data, trait, banned_chars):
        super().__init__()
        self.match_data = match_data
        self.trait = trait
        self.banned_chars = banned_chars

    async def on_submit(self, interaction: discord.Interaction):
        persona = self.persona_input.value.strip() if self.persona_input.value else None

        # データを保存
        self.match_data["trait_used"] = self.trait
        self.match_data["persona"] = persona
        self.match_data["banned_characters"] = self.banned_chars

        # データベースに保存
        saved = db.save_match(str(interaction.user.id), self.match_data)

        # 結果表示
        embed = discord.Embed(
            title="✅ 試合を記録しました",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )

        # 試合日時
        if self.match_data.get("played_at"):
            try:
                from datetime import datetime as dt
                played_dt = dt.fromisoformat(self.match_data["played_at"])
                embed.add_field(
                    name="📅 試合日時",
                    value=played_dt.strftime("%m月%d日 %H:%M"),
                    inline=True
                )
            except:
                pass

        # 試合結果
        result_emoji = "🏆" if self.match_data.get("result") == "勝利" else "💀"
        embed.add_field(
            name=f"{result_emoji} 試合結果",
            value=self.match_data.get("result", "不明"),
            inline=True
        )

        # マップ
        embed.add_field(
            name="🗺️ マップ",
            value=self.match_data.get("map_name", "不明"),
            inline=True
        )

        # 時間
        embed.add_field(
            name="⏱️ 使用時間",
            value=self.match_data.get("duration", "不明"),
            inline=True
        )

        # ハンター情報
        hunter_name = self.match_data.get("hunter_character")
        if hunter_name:
            embed.add_field(name="🔪 ハンター (自動検出)", value=hunter_name, inline=True)
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
        survivors = self.match_data.get("survivors", [])
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
    def __init__(self, match_data, selection_view):
        super().__init__(timeout=300)
        self.match_data = match_data
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

        # 人格入力モーダルを表示
        modal = PersonaModal(self.match_data, self.selection_view.trait, unique_bans)
        await interaction.response.send_modal(modal)
        self.stop()
        self.selection_view.stop()


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

    ※画像を添付してください
    ※ハンターは自動検出されます
    ※特質・Ban・人格は画像解析中に選択できます
    """
    if not ctx.message.attachments:
        await ctx.send(
            "❌ **画像を添付してください！**\n\n"
            "**使い方:**\n"
            "`!record` (画像添付)\n\n"
            "画像解析中に特質・Ban・人格を選択できます"
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

    processing_msg = await ctx.send("🔄 画像を解析中...")

    try:
        # 画像ダウンロード
        attachment = ctx.message.attachments[0]
        image_bytes = await attachment.read()

        # OCR処理
        match_data = ocr.process_image(image_bytes)

        # OCR結果を表示
        hunter_name = match_data.get("hunter_character", "不明")
        result = match_data.get("result", "不明")
        map_name = match_data.get("map_name", "不明")
        duration = match_data.get("duration", "不明")

        await processing_msg.edit(
            content=f"✅ **画像解析完了！**\n\n"
                    f"📊 結果: **{result}**\n"
                    f"🗺️ マップ: **{map_name}**\n"
                    f"⏱️ 使用時間: **{duration}**\n"
                    f"🔪 ハンター: **{hunter_name}** (自動検出)"
        )

        # 選択メッセージを更新（OCR完了状態に）
        selection_view.ocr_complete = True
        await selection_view.update_status()

        # 確定ボタンを別メッセージで送信
        button_view = ConfirmButtonView(match_data, selection_view)
        await ctx.send(
            "⬇️ **選択が完了したら下のボタンを押してください**",
            view=button_view
        )

    except Exception as e:
        await processing_msg.edit(
            content=f"❌ **エラーが発生しました**\n```{str(e)}```"
        )
        print(f"Error in record_match: {e}")
        import traceback
        traceback.print_exc()

@bot.command(name='stats', aliases=['s'])
async def show_stats(ctx):
    """全体統計を表示"""
    stats = db.get_overall_stats(str(ctx.author.id))
    
    embed = discord.Embed(
        title=f"📊 {ctx.author.display_name} の全体統計",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    embed.add_field(name="📈 総試合数", value=stats["total_matches"], inline=True)
    embed.add_field(name="🏆 勝利", value=stats["wins"], inline=True)
    embed.add_field(name="💀 敗北", value=stats["losses"], inline=True)
    embed.add_field(name="📊 勝率", value=stats["win_rate"], inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='survivor_stats', aliases=['ss'])
async def survivor_stats(ctx):
    """サバイバーキャラごとの統計"""
    pick_rates = db.get_survivor_pick_rates(str(ctx.author.id))
    
    if not pick_rates:
        await ctx.send("まだデータがありません。")
        return
    
    embed = discord.Embed(
        title="👥 サバイバーキャラ統計",
        description="対戦したサバイバーキャラのピック数",
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )
    
    # Top 10
    for i, data in enumerate(pick_rates[:10], 1):
        embed.add_field(
            name=f"{i}. {data['character']}",
            value=f"**{data['picks']}回**",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command(name='kite_stats', aliases=['ks'])
async def kite_stats(ctx):
    """サバイバーごとの平均牽制時間"""
    kite_data = db.get_avg_kite_time_by_survivor(str(ctx.author.id))
    
    if not kite_data:
        await ctx.send("まだデータがありません。")
        return
    
    embed = discord.Embed(
        title="⏱️ サバイバーごとの平均牽制時間",
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    
    for i, data in enumerate(kite_data[:10], 1):
        embed.add_field(
            name=f"{i}. {data['character']}",
            value=f"平均: **{data['avg_kite_time']}** (n={data['samples']})",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command(name='map_stats', aliases=['ms'])
async def map_stats(ctx, hunter: str = None):
    """マップごとの勝率"""
    map_data = db.get_win_rate_by_hunter_and_map(str(ctx.author.id), hunter)
    
    if not map_data:
        await ctx.send("まだデータがありません。")
        return
    
    title = f"🗺️ マップごとの勝率"
    if hunter:
        title += f" ({hunter})"
    
    embed = discord.Embed(
        title=title,
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    
    for data in map_data:
        embed.add_field(
            name=data['map'],
            value=f"**{data['win_rate']}** ({data['wins']}/{data['total']})",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command(name='ban_stats', aliases=['bs'])
async def ban_stats(ctx):
    """Banキャラごとの勝率"""
    ban_data = db.get_win_rate_by_ban(str(ctx.author.id))
    
    if not ban_data:
        await ctx.send("まだデータがありません。")
        return
    
    embed = discord.Embed(
        title="🚫 Banキャラごとの勝率",
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    
    for data in ban_data[:10]:
        embed.add_field(
            name=data['banned_character'],
            value=f"**{data['win_rate']}** ({data['wins']}/{data['total']})",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command(name='history', aliases=['h'])
async def show_history(ctx, limit: int = 5):
    """最近の試合履歴"""
    matches = db.get_recent_matches(str(ctx.author.id), limit)
    
    if not matches:
        await ctx.send("まだ試合が記録されていません。\n`!record` で記録を開始しましょう！")
        return
    
    embed = discord.Embed(
        title=f"📋 最近の試合履歴 (直近{len(matches)}件)",
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )
    
    for i, match in enumerate(matches, 1):
        result_emoji = "🏆" if match.get("result") == "勝利" else "💀"

        survivors = match.get("survivors", [])
        survivor_names = [s.get("character_name") for s in survivors if s.get("character_name")]

        # 試合日時を表示
        field_value = ""
        if match.get("played_at"):
            try:
                from datetime import datetime as dt
                played_dt = dt.fromisoformat(match["played_at"])
                field_value += f"📅 {played_dt.strftime('%m/%d %H:%M')}\n"
            except:
                pass

        field_value += f"**{match.get('result', '不明')}** | {match.get('map_name', '不明')}\n"
        if match.get("hunter_character"):
            field_value += f"ハンター: {match.get('hunter_character')}\n"
        if survivor_names:
            field_value += f"相手: {', '.join(survivor_names[:2])}..."

        embed.add_field(
            name=f"{result_emoji} 試合 {i}",
            value=field_value,
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command(name='help', aliases=['commands'])
async def show_help(ctx):
    """コマンド一覧"""
    embed = discord.Embed(
        title="🎮 第五人格 ハンター戦績Bot",
        description="試合結果のスクショで自動記録＆分析！",
        color=discord.Color.gold()
    )
    
    commands_list = [
        ("📸 記録コマンド", ""),
        ("!record", "試合結果を記録（画像添付必須）\n※ハンターは自動検出\n※特質・Ban・人格は選択メニューから入力"),
        ("", ""),
        ("📊 統計コマンド", ""),
        ("!stats", "全体統計を表示"),
        ("!survivor_stats", "サバイバーキャラごとのピック数"),
        ("!kite_stats", "サバイバーごとの平均牽制時間"),
        ("!map_stats [ハンター]", "マップごとの勝率"),
        ("!ban_stats", "Banキャラごとの勝率"),
        ("!history [件数]", "最近の試合履歴"),
        ("", ""),
        ("ℹ️ その他", ""),
        ("!help", "このヘルプを表示"),
    ]
    
    for name, value in commands_list:
        if name and not value:
            embed.add_field(name=name, value="\u200b", inline=False)
        elif name and value:
            embed.add_field(name=name, value=value, inline=False)
    
    embed.set_footer(text="エイリアスコマンド: !r, !s, !ss, !ks, !ms, !bs, !h")
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        print("❌ DISCORD_BOT_TOKENが設定されていません")
        exit(1)
    
    bot.run(TOKEN)
