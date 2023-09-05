import discord
from discord.ext import commands
from discord.ext import tasks
import datetime
import unicodedata
import json
import typing
import enum #enum.解禁

class templates(enum.Enum):
  def __new__(cls, value):
    obj = object.__new__(cls)
    obj._value_ = value
    return obj

  チケット1 = ("t1")
  チケット2 = ("t2")
  本番1 = ("h1")
  本番2 = ("h2")
  本番3 = ("h3")
  本番4 = ("h4")
  本番5 = ("h5")
  本番6 = ("h6")
  本番7 = ("h7")
  本番8 = ("h8")
  イラスト = ("i2")
  エラーメッセージ = ("error_mes")

tz_jst = datetime.timezone(datetime.timedelta(hours=9), name = "JST")


class Confirm_temp(commands.Cog, name = 'デバッグ用'):
  """テンプレ確認などの保管所"""
  
  def __init__(self, bot: commands.Bot):
    super().__init__()
    self.bot: commands.Bot = bot
    self.tz_jst = tz_jst

  async def cog_check(self, ctx: commands.Context):
    if ctx.author.bot:
      return False
    else:
      return True
  
  @commands.hybrid_command(name = "確認コマンド", aliases = ["確認", "confirm"])
  @discord.app_commands.rename(
    option = "確認する項目",
    template = "呼び出すテンプレ"
  )
  async def confirm(
    self, ctx: commands.Context,
    option: typing.Literal["進捗確認", "リマインド日時確認", "テンプレ確認"],
    template: templates = "h1"
    ):
    """各種設定を確認します
    
    Parameters
    -----------
    option
      どの項目を確認しますか？
    template
      どのテンプレを呼び出しますか？
    """
    with open("data.json", 'r') as f:
      data = json.load(f)
    if option == "進捗確認":
      if str(ctx.channel.id) not in data:
        with open(f"error_mes.txt", 'r', encoding="utf-8") as f:
          error_mes = f.read()
        embed = discord.Embed(
          title = error_mes,
          color = discord.Colour.red()
        )
        return await ctx.send(embed = embed, ephemeral = True)
      ch_data = data[str(ctx.channel.id)]
      status = data[str(ctx.channel.id)]["status"]
      time = data[str(ctx.channel.id)]["time"]
      desc = (
        f'チケット販売日：{status["set_ticket"]}\nイベント本番日：{status["set_honban"]}'
        f'\n\n{status["i1"]}　【新規絵提出期限】\n{time["i2"]}　【新規絵提出リマインド】'
        f'\n【演者様新規絵提出】{status["illust"]}\n【公演時間】{status["performance_time"]}'
        f'\n【サムネイル製作】{status["thumbnail"]}\n【告知用画像製作】{status["announce"]}'
        f'\n【ポスター製作】{status["poster"]}\n【グッズ製作】\n{status["merch"]}'
        f'\n\n【メモ】\n{status["memo"]}'
      )
      embed = discord.Embed(
        title = f"このチャンネルに設定された進捗状況",
        description = desc,
        color = discord.Colour.dark_blue()
      )
    elif option == "リマインド日時確認":
      if str(ctx.channel.id) not in data:
        embed = discord.Embed(
          title = f"このチャンネルにリマインドは無いよ！",
          color = discord.Colour.dark_blue()
        )
        return await ctx.send(embed = embed, ephemeral = True)
      ch_data = data[str(ctx.channel.id)]
      if not ch_data["user"] == ctx.author.id:
        with open(f"error_mes.txt", 'r', encoding="utf-8") as f:
          error_mes = f.read()
        embed = discord.Embed(
          title = error_mes,
          color = discord.Colour.red()
        )
        return await ctx.send(embed = embed, ephemeral = True)
      GUILD_ID = ch_data["guild"]
      use_guild = self.bot.get_guild(GUILD_ID)
      ROLE_ID = ch_data["role"]
      role = use_guild.get_role(ROLE_ID)
      status = ch_data["status"]
      time = ch_data["time"]
      desc = (
        f'チケット販売日：{status["set_ticket"]}'
        f'\n{time["t1"]}　【チケット販売開始2日前アナウンス】\n{time["t2"]}　【チケット販売開始当日アナウンス】'
        f'\n\nイベント本番日：{status["set_honban"]}'
        f'\n{time["h1"]}　【チケット販売終了1週間前アナウンス】\n{time["h2"]}　【チケット販売終了日アナウンス】'
        f'\n{time["h3"]}　【最終打ち合わせについてのご連絡】\n{time["h4"]}　【イベント本番！】'
        f'\n{time["h5"]}　【イベント後の流れ】\n{time["h6"]}　【後日販売直前アナウンス】'
        f'\n{time["h7"]}　【後日販売終了日アナウンス】\n{time["h8"]}　【イベント終了告知】'
        f'\n{status["i1"]}　【新規絵提出期限】\n{time["i2"]}　【新規絵提出リマインド】'
      )
      embed = discord.Embed(
        title = f"{role.name}　へお知らせ予定",
        description = desc,
        color = discord.Colour.dark_blue()
      )
    elif option == "テンプレ確認":
      if str(ctx.channel.id) not in data:
        with open(f"error_mes.txt", 'r', encoding="utf-8") as f:
          error_mes = f.read()
        embed = discord.Embed(
          title = error_mes,
          color = discord.Colour.red()
        )
        return await ctx.send(embed = embed, ephemeral = True)
      ch_data = data[str(ctx.channel.id)]
      if not ch_data["user"] == ctx.author.id:
        with open(f"error_mes.txt", 'r', encoding="utf-8") as f:
          error_mes = f.read()
        embed = discord.Embed(
          title = error_mes,
          color = discord.Colour.red()
        )
        return await ctx.send(embed = embed, ephemeral = True)
      with open(f"{template.value}.txt", 'r', encoding="utf-8") as f:
        speech = f.read()
      embed = discord.Embed(
          title = f"{template.name}を表示します",
          description = speech,
          color = discord.Colour.dark_blue()
        )
    await ctx.send(embed = embed, ephemeral = True)
    debug_txt = f"デバッグ用。※納品物では表示されません"
    await ctx.send(debug_txt, embed=embed)

async def setup(bot: commands.Bot):
  await bot.add_cog(Confirm_temp(bot))