import discord
from discord.ext import commands
from discord.ext import tasks
import datetime
import unicodedata
import json
import typing
import random

tz_jst = datetime.timezone(datetime.timedelta(hours=9), name = "JST")

times = [
  datetime.time(hour=3, tzinfo=tz_jst),
  datetime.time(hour=6, tzinfo=tz_jst),
  datetime.time(hour=9, tzinfo=tz_jst),
  datetime.time(hour=12, tzinfo=tz_jst),
  datetime.time(hour=15, tzinfo=tz_jst),
  datetime.time(hour=18, tzinfo=tz_jst),
  datetime.time(hour=19, tzinfo=tz_jst),
  datetime.time(hour=21, tzinfo=tz_jst),
  #datetime.time(hour=22, minute=1, tzinfo=tz_jst),
  datetime.time(hour=20, minute=30, tzinfo=tz_jst)
]


class Schedule(commands.Cog, name = 'スケジュール'):
  """おだのぶ様の管理サーバー用"""
  
  def __init__(self, bot: commands.Bot):
    super().__init__()
    self.bot: commands.Bot = bot
    self.tz_jst = tz_jst
    self.remind_check.start()
  
  def cog_unload(self):
    self.remind_check.cancel()

  async def cog_check(self, ctx: commands.Context):
    if ctx.author.bot:
      return False
    else:
      return True
  
  @commands.hybrid_command(name = "イベント作成", aliases = ["イベ", "event"])
  @discord.app_commands.rename(
    kibo = "規模",
    ticket = "チケット販売開始日",
    honban = "イベント本番日",
    role = "ロール",
    jibun = "自分に通知"
  )
  async def set_mid_event(
    self, ctx: commands.Context,
    kibo: typing.Literal["中規模","小規模（謎解き）"],
    ticket: str,
    honban: str,
    role: discord.Role,
    jibun: typing.Literal["はい","いいえ"]
  ):
    """イベントのリマインドを設定します。チャンネル毎に使い直してください
    
    Parameters
    -----------
    kibo
      中規模イベントか小規模（謎解き）イベントかを選択
    ticket
      6桁の数字で入力（全半角混在可、スペース入り可。その他のノイズ文字は不可）
    honban
      6桁の数字で入力（全半角混在可、スペース入り可。その他のノイズ文字は不可）
    role
      通知先ロールをプルダウンで選択（1つのみ）
    jibun
      自分に通知するかしないかを選択
    """
    ticket_str = unicodedata.normalize('NFKC', ticket).replace(' ', '')
    honban_str = unicodedata.normalize('NFKC', honban).replace(' ', '')
    if not len(ticket_str) == len(honban_str) == 6:
      embed = discord.Embed(
        title = f"{role.name}　へお知らせ\n自分に通知：{jibun}",
        description = f'エラーだよ。年月日は6桁の数字だよ！',
        color = discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255))
       )
      return await ctx.send(embed = embed, ephemeral = True)
    if jibun == "はい":
      notic_to_me = True
    else:
      notic_to_me = False
    if kibo == "中規模":
      jdata = "mid-eve_data.json"
      kibo = "m"
    elif kibo == "小規模（謎解き）":
      jdata = "small-eve_data.json"
      kibo = "s"
    with open(jdata, 'r') as f:
      data = json.load(f)
    data.update({
      str(ctx.channel.id): {
        "role": role.id,
        "guild": ctx.guild.id,
        "user": ctx.author.id,
        "notic_to_me": notic_to_me,
        "time": {},
        "status": {}
      }
    })
    print("data update:Complete")
    with open("prog_data.json", 'w') as f:
      json.dump(data, f, indent=2, ensure_ascii = False)
    ticket_time = ticket_str[:2] + "/" + ticket_str[2:4] + "/" + ticket_str[4:6]
    honban_time = honban_str[:2] + "/" + honban_str[2:4] + "/" + honban_str[4:6]
    data[str(ctx.channel.id)]["status"].update({
      "set_ticket": ticket_time,
      "set_honban": honban_time#,
      #"illust": "NO"
    })
    print("time conv:Complete")
    delta_t1 = datetime.timedelta(days=6, hours=15)
    delta_t2 = datetime.timedelta(days=2, hours=15)
    delta_t3 = datetime.timedelta(hours=9)
    delta_h1 = datetime.timedelta(days=13, hours=15)
    delta_h2 = datetime.timedelta(days=6, hours=15)
    delta_h3 = datetime.timedelta(days=5, hours=15)
    delta_h4 = datetime.timedelta(hours=9)
    delta_h5 = datetime.timedelta(hours=20, minutes=30)
    delta_h6 = datetime.timedelta(days=1, hours=19)
    delta_h7 = datetime.timedelta(days=4, hours=9)
    delta_h8 = datetime.timedelta(days=5, hours=9)
    #delta_i1 = datetime.timedelta(days=19, hours=12)
    #delta_i2 = datetime.timedelta(days=29, hours=15)
    s_format = '%y/%m/%d %H:%M'
    s_format2 = '%y/%m/%d'
    ticket_date = datetime.datetime.strptime(ticket_time, s_format2)
    honban_date = datetime.datetime.strptime(honban_time, s_format2)
    t1 = ticket_date - delta_t1
    t2 = ticket_date - delta_t2
    t3 = ticket_date + delta_t3
    h1 = honban_date - delta_h1
    h2 = honban_date - delta_h2
    h3 = honban_date - delta_h3
    h4 = honban_date + delta_h4
    h5 = honban_date + delta_h5
    h6 = honban_date + delta_h6
    h7 = honban_date + delta_h7
    h8 = honban_date + delta_h8
    #i1 = honban_date - delta_i1
    #i2 = honban_date - delta_i2
    for i in range(1,4):
      exec(f'data[str(ctx.channel.id)]["time"]["{str(kibo)}t{str(i)}"] = t{str(i)}.strftime(s_format)')
    for i in range(1,9):
      exec(f'data[str(ctx.channel.id)]["time"]["{str(kibo)}h{str(i)}"] = h{str(i)}.strftime(s_format)')
    #data[str(ctx.channel.id)]["status"].update({"i1": i1.strftime(s_format)})
    print("data add:Complete")
    with open(jdata, 'w') as f:
      json.dump(data, f, indent=2, ensure_ascii = False)
    status = data[str(ctx.channel.id)]["status"]
    time = data[str(ctx.channel.id)]["time"]
    if kibo == "m":
      desc = (
        f'チケット販売日：{status["set_ticket"]}'
        f'\n{time["mt1"]}　【チケット販売開始1週間前アナウンス】\n{time["mt2"]}　【チケット販売開始3日前アナウンス】\n{time["mt3"]}　【チケット販売開始当日アナウンス】'
        f'\n\nイベント本番日：{status["set_honban"]}'
        f'\n{time["mh1"]}　【チケット販売終了1週間前アナウンス】\n{time["mh2"]}　【チケット販売終了日アナウンス】'
        f'\n{time["mh3"]}　【最終打ち合わせについてのご連絡】\n{time["mh4"]}　【イベント本番！】'
        f'\n{time["mh5"]}　【イベント後の流れ】\n{time["mh6"]}　【後日販売直前アナウンス】'
        f'\n{time["mh7"]}　【後日販売終了日アナウンス】\n{time["mh8"]}　【イベント終了告知】'
        #f'\n{status["i1"]}　【新規絵提出期限】\n{time["i2"]}　【新規絵提出リマインド】'
      )
    elif kibo == "s":
      desc = (
        f'チケット販売日：{status["set_ticket"]}'
        f'\n{time["st1"]}　【チケット販売開始1週間前アナウンス】\n{time["st2"]}　【チケット販売開始3日前アナウンス】\n{time["st3"]}　【チケット販売開始当日アナウンス】'
        f'\n\nイベント本番日：{status["set_honban"]}'
        f'\n{time["sh1"]}　【チケット販売終了1週間前アナウンス】\n{time["sh2"]}　【チケット販売終了日アナウンス】'
        f'\n{time["sh3"]}　【最終打ち合わせについてのご連絡】\n{time["sh4"]}　【イベント本番！】'
        f'\n{time["sh5"]}　【イベント後の流れ】\n{time["sh6"]}　【後日販売直前アナウンス】'
        f'\n{time["sh7"]}　【後日販売終了日アナウンス】\n{time["sh8"]}　【イベント終了告知】'
        #f'\n{status["i1"]}　【新規絵提出期限】\n{time["i2"]}　【新規絵提出リマインド】'
      )
    embed = discord.Embed(
      title = f"{role.name}　へお知らせ\n自分に通知：{jibun}",
      description = desc,
      color = discord.Colour.brand_green()
    )
    await ctx.send(embed = embed, ephemeral = True)
    debug_txt = f"デバッグ用。※納品物では表示されません"
    #await ctx.send(debug_txt, embed=embed)

  @commands.hybrid_command(name = "進捗入力", aliases = ["進捗", "progress"])
  @discord.app_commands.rename(
    illust = "新規絵提出期限",
    performance_time = "公演時間",
    thumbnail = "サムネイル製作",
    announce = "告知用画像製作",
    poster = "ポスター製作",
    merch = "グッズ製作",
    memo = "イベント情報"
  )
  async def set_progress(
    self, ctx: commands.Context,
    illust: typing.Literal["OK","NO","既存絵"],
    performance_time: typing.Literal["前","後","両"],
    thumbnail: typing.Literal["OK","NO"],
    announce: typing.Literal["OK","NO"],
    poster: typing.Literal["OK","NO"],
    merch: typing.Literal["OK","製作中","NO"],
    *, memo: str = "メモなし"
  ):
    """イベントの進捗を設定します。チャンネル毎にイベント作成をしてからご利用ください
    
    Parameters
    -----------
    illust
      3つの選択肢から選択
    performance_time
      3つの選択肢から選択
    thumbnail
      2つの選択肢から選択
    announce
      2つの選択肢から選択
    poster
      2つの選択肢から選択
    merch
      3つの選択肢から選択
    memo
      自由文を入力
    """
    with open("prog_data.json", 'r') as f:
      data = json.load(f)
    if data == {} or str(ctx.channel.id) not in data:
      embed = discord.Embed(
        title = f"このチャンネルに進捗は無いよ！",
        color = discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255))
      )
      return await ctx.send(embed = embed, ephemeral = True)
    else:
      ch_data = data[str(ctx.channel.id)]
      if not ch_data["user"] == ctx.author.id:
        embed = discord.Embed(
          title = f"ごめんなさい！こちらのコマンドを使用することは出来ません🤖💦",
          color = discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        )
        return await ctx.send(embed = embed, ephemeral = True)
    ch_data["status"].update({
      "illust": illust,
      "performance_time": performance_time,
      "thumbnail": thumbnail,
      "announce": announce,
      "poster": poster,
      "merch": merch,
      "memo": memo
    })
    data[str(
      ctx.channel.id
    )].update(ch_data)
    print("data add:Complete")
    with open("data.json", 'w') as f:
      json.dump(data, f, indent=2, ensure_ascii = False)
    status = data[str(ctx.channel.id)]["status"]
    time = data[str(ctx.channel.id)]["time"]
    desc = (
      f'チケット販売日：{status["set_ticket"]}\nイベント本番日：{status["set_honban"]}\n'
      #f'\n{status["i1"]}　【新規絵提出期限】\n{time["i2"]}　【新規絵提出リマインド】'
      f'\n【新規絵提出期限】{status["illust"]}\n【公演時間】{status["performance_time"]}'
      f'\n【サムネイル製作】{status["thumbnail"]}\n【告知用画像製作】{status["announce"]}'
      f'\n【ポスター製作】{status["poster"]}\n【グッズ製作】{status["merch"]}'
      f'\n\n【メモ】\n{status["memo"]}'
    )
    embed = discord.Embed(
      title = f"このチャンネルに設定された進捗状況",
      description = desc,
      color = discord.Colour.blue()
    )
    await ctx.send(embed = embed, ephemeral = True)
    debug_txt = f"デバッグ用。※納品物では表示されません"
    #await ctx.send(debug_txt, embed=embed)
  
  @commands.hybrid_command(name = "最終打ち合わせ当日告知", aliases = ["最終", "final"])
  @discord.app_commands.rename(
    day = "日付",
    role = "ロール"
  )
  async def final_meeting(
    self, ctx: commands.Context,
    day: str,
    role: discord.Role
  ):
    """最終打ち合わせのリマインドを設定します。チャンネル毎に1つだけ設定できます
    
    Parameters
    -----------
    day
      6桁の数字で入力（全半角混在可、スペース入り可。その他のノイズ文字は不可）
    role
      通知先ロールをプルダウンで選択（1つのみ）
    """
    rim_day_str = unicodedata.normalize('NFKC', day).replace(' ', '')
    if len(rim_day_str) == 6:
      rim_day = rim_day_str[:2] + "/" + rim_day_str[2:4] + "/" + rim_day_str[4:6]
      rim_date = f"{rim_day} 09:00"
      with open("final_meet.json", 'r') as f:
        final_meet = json.load(f)
      final_meet.update({
        str(ctx.channel.id): {
          "role": role.id,
          "guild": ctx.guild.id,
          "user": ctx.author.id,
          "notic_to_me": True,
          "time": rim_date
          }
      })
      print("final_meet update:Complete")
      with open("final_meet.json", 'w') as f:
        json.dump(final_meet, f, indent=2, ensure_ascii = False)
      with open("final_meet.txt", 'r', encoding="utf-8") as f:
        desc = f.read()
      embed = discord.Embed(
        title = f"{role.name}　へお知らせ\n{rim_date}　【最終打ち合わせリマインド日時】",
        description = desc,
        color = discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255))
      )
    else:
      embed = discord.Embed(
        title =f"{role.name}　へお知らせ",
        description = f'エラーだよ。年月日は6桁の数字だよ！',
        color = discord.Colour.yellow()
      )
    await ctx.send(embed = embed, ephemeral = True)
    debug_txt = f"デバッグ用。※納品物では表示されません"
    #await ctx.send(debug_txt, embed=embed)
  
  @commands.hybrid_command(name = "フリーリマインド", aliases = ["フリー", "free"])
  @discord.app_commands.rename(
    rim_day = "リマインド日",
    rim_time = "通知時刻",
    memo = "メモ"
  )
  async def free_remind(
    self, ctx: commands.Context,
    rim_day: str,
    rim_time: typing.Literal["3:00", "6:00", "9:00", "12:00", "15:00", "18:00", "21:00"],
    *, memo: str
  ):
    """自由なリマインドを設定します。チャンネル毎に1つだけ設定できます
    
    Parameters
    -----------
    rim_day
      6桁の数字で入力（全半角混在可、スペース入り可。その他のノイズ文字は不可）
    rim_time
      通知時間をプルダウンで選択（1つのみ）
    memo
      リマインドしたい内容を自由文で入力
    """
    rim_day_str = unicodedata.normalize('NFKC', rim_day).replace(' ', '')
    if len(rim_day_str) == 6:
      rim_day = rim_day_str[:2] + "/" + rim_day_str[2:4] + "/" + rim_day_str[4:6]
      rim_date = f"{rim_day} {rim_time}"
      with open("free_rem.json", 'r') as f:
        free_rem = json.load(f)
      print(free_rem)
      free_rem.update({
        str(ctx.channel.id): {
          "guild": ctx.guild.id,
          "user": ctx.author.id,
          "time": rim_date,
          "memo": memo
          }
      })
      print("free_rem update:Complete")
      with open("free_rem.json", 'w') as f:
        json.dump(free_rem, f, indent=2, ensure_ascii = False)
      embed = discord.Embed(
        title = f"リマインド日時：{rim_date}",
        description = memo,
        color = discord.Colour.red()
      )
    else:
      embed = discord.Embed(
        title = f"メモのおさらいをするね",
        description = f'エラーだよ。年月日は6桁の数字だよ！',
        color = discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255))
      )
    await ctx.send(embed = embed, ephemeral = True)
    debug_txt = f"デバッグ用。※納品物では表示されません"
    #await ctx.send(debug_txt, embed=embed)
  
  @commands.hybrid_command(name = "各種確認", aliases = ["確認", "conf"])
  @discord.app_commands.rename(
    item = "確認する項目"
  )
  async def confirm_remind(
    self, ctx: commands.Context,
    item: typing.Literal["リマインド日時確認", "進捗確認", "コマンド確認", "テンプレ確認"]
    ):
    """各種項目を確認します
    
    Parameters
    -----------
    item
      確認する項目をプルダウンで選択
    """
    debug_txt = f"デバッグ用。※納品物では表示されません"
    if item == "リマインド日時確認":
      embed = discord.Embed(
        title = f"リマインド日時を表示します",
        color = discord.Colour.brand_green()
      )
      with open("mid-eve_data.json", 'r') as f:
        data = json.load(f)
      if data == {} or str(ctx.channel.id) not in data:
        embed.add_field(
          name = "エラー",
          value = f"このチャンネルに中規模イベントのリマインドは無いよ！"
        )
        #mid_ch_user = ctx.author.id
      else:
        mid_ch_data = data[str(ctx.channel.id)]
        GUILD_ID = mid_ch_data["guild"]
        use_guild = self.bot.get_guild(GUILD_ID)
        ROLE_ID = mid_ch_data["role"]
        role = use_guild.get_role(ROLE_ID)
        status = mid_ch_data["status"]
        time = mid_ch_data["time"]
        #mid_ch_user = mid_ch_data["user"]
        desc = (
          f'**{role.name}　へお知らせ予定**\n'
          f'チケット販売日：{status["set_ticket"]}'
          f'\n{time["mt1"]}　【チケット販売開始1週間前アナウンス】\n{time["mt2"]}　【チケット販売開始3日前アナウンス】\n{time["mt3"]}　【チケット販売開始当日アナウンス】'
          f'\n\nイベント本番日：{status["set_honban"]}'
          f'\n{time["mh1"]}　【チケット販売終了1週間前アナウンス】\n{time["mh2"]}　【チケット販売終了日アナウンス】'
          f'\n{time["mh3"]}　【最終打ち合わせについてのご連絡】\n{time["mh4"]}　【イベント本番！】'
          f'\n{time["mh5"]}　【イベント後の流れ】\n{time["mh6"]}　【後日販売直前アナウンス】'
          f'\n{time["mh7"]}　【後日販売終了日アナウンス】\n{time["mh8"]}　【イベント終了告知】'
          #f'\n{status["i1"]}　【新規絵提出期限】\n{time["i2"]}　【新規絵提出リマインド】'
        )
        embed.add_field(
          name = f"こちらは中規模イベント対象の演者様です",
          value = desc, inline = False
        )
      with open("small-eve_data.json", 'r') as f:
        data = json.load(f)
      if data == {} or str(ctx.channel.id) not in data:
        embed.add_field(
          name = "エラー",
          value = f"このチャンネルに小規模（謎解き）イベントのリマインドは無いよ！"
        )
        #small_ch_user = ctx.author.id
      else:
        small_ch_data = data[str(ctx.channel.id)]
        GUILD_ID = small_ch_data["guild"]
        use_guild = self.bot.get_guild(GUILD_ID)
        ROLE_ID = small_ch_data["role"]
        role = use_guild.get_role(ROLE_ID)
        status = small_ch_data["status"]
        time = small_ch_data["time"]
        #small_ch_user = small_ch_data["user"]
        desc = (
          f'**{role.name}　へお知らせ予定**\n'
          f'チケット販売日：{status["set_ticket"]}'
          f'\n{time["st1"]}　【チケット販売開始1週間前アナウンス】\n{time["st2"]}　【チケット販売開始3日前アナウンス】\n{time["st3"]}　【チケット販売開始当日アナウンス】'
          f'\n\nイベント本番日：{status["set_honban"]}'
          f'\n{time["sh1"]}　【チケット販売終了1週間前アナウンス】\n{time["sh2"]}　【チケット販売終了日アナウンス】'
          f'\n{time["sh3"]}　【最終打ち合わせについてのご連絡】\n{time["sh4"]}　【イベント本番！】'
          f'\n{time["sh5"]}　【イベント後の流れ】\n{time["sh6"]}　【後日販売直前アナウンス】'
          f'\n{time["sh7"]}　【後日販売終了日アナウンス】\n{time["sh8"]}　【イベント終了告知】'
          #f'\n{status["i1"]}　【新規絵提出期限】\n{time["i2"]}　【新規絵提出リマインド】'
        )
        embed.add_field(
          name = f"こちらは小規模イベント対象の演者様です",
          value = desc, inline = False
        )
      with open("final_meet.json", 'r') as f:
        data = json.load(f)
      if data == {} or str(ctx.channel.id) not in data:
        embed.add_field(
          name = "エラー",
          value = f"このチャンネルに最終打ち合わせ告知のリマインドは無いよ！"
        )
      else:
        ch_data = data[str(ctx.channel.id)]
        GUILD_ID = ch_data["guild"]
        use_guild = self.bot.get_guild(GUILD_ID)
        ROLE_ID = ch_data["role"]
        role = use_guild.get_role(ROLE_ID)
        time = ch_data["time"]
        embed.add_field(
          name = f"こちらは最終打ち合わせリマインド日時です",
          value= f"{time}に　{role.name}　へお知らせ"
        )
      await ctx.send(embed = embed, ephemeral = True)
      #await ctx.send(debug_txt, embed = embed)
    elif item == "進捗確認":
      with open("prog_data.json", 'r') as f:
        data = json.load(f)
      if data == {} or str(ctx.channel.id) not in data or data[str(ctx.channel.id)]["status"] == {}:
        embed = discord.Embed(
          title = f"このチャンネルに進捗の入力は無いよ！",
          color = discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        )
      else:
        ch_data = data[str(ctx.channel.id)]
        status = data[str(ctx.channel.id)]["status"]
        time = data[str(ctx.channel.id)]["time"]
        desc = (
          f'チケット販売日：{status["set_ticket"]}\nイベント本番日：{status["set_honban"]}\n'
          #f'\n{status["i1"]}　【新規絵提出期限】\n{time["i2"]}　【新規絵提出リマインド】'
          f'\n【新規絵提出期限】{status["illust"]}\n【公演時間】{status["performance_time"]}'
          f'\n【サムネイル製作】{status["thumbnail"]}\n【告知用画像製作】{status["announce"]}'
          f'\n【ポスター製作】{status["poster"]}\n【グッズ製作】{status["merch"]}'
          f'\n\n【メモ】\n{status["memo"]}'
        )
        embed = discord.Embed(
          title = f"このチャンネルに設定された進捗状況",
          description = desc,
          color = discord.Colour.blue()
        )
      await ctx.send(embed = embed, ephemeral = True)
      #await ctx.send(debug_txt, embed=embed)
    elif item == "コマンド確認":
      embed = discord.Embed(
        title = f"入力されているすべてのコマンドを確認します",
        color = discord.Colour.purple()
      )
      dt_now_jst = datetime.datetime.now(self.tz_jst)
      s_format = '%y/%m/%d %H:%M'
      now = datetime.datetime.strptime(dt_now_jst.strftime(s_format), s_format)
      eve = {}
      with open("mid-eve_data.json", 'r') as f:
        data = json.load(f)
      for k1, v1 in data.items():
        for k2, v2 in v1["time"].items():
          dt = datetime.datetime.strptime(v2, s_format)
          if now < dt:
            CHANNEL_ID = int(k1)
            channel = self.bot.get_channel(CHANNEL_ID)
            ticket = data[str(k1)]["status"]["set_ticket"]
            honban = data[str(k1)]["status"]["set_honban"]
            eve[str(v2)] = [channel.name, ticket, honban, k2]
            break
      conf = ""
      for k, v in eve.items():
        if v[3] == "mt1": l = "チケット①"
        if v[3] == "mt2": l = "チケット②"
        if v[3] == "mt3": l = "チケット③"
        if v[3] == "mh1": l = "本番①"
        if v[3] == "mh2": l = "本番②"
        if v[3] == "mh3": l = "本番③"
        if v[3] == "mh4": l = "本番④"
        if v[3] == "mh5": l = "本番⑤"
        if v[3] == "mh6": l = "本番⑥"
        if v[3] == "mh7": l = "本番⑦"
        if v[3] == "mh8": l = "本番⑧"
        conf += f"**{v[0]}**\n> チケット販売日 ⇒ {v[1]}\n> イベント本番日 ⇒ {v[2]}\n> 次回リマインド ⇒ {k}\n> ▼{l}\n\n"
      embed.add_field(
        name = f'中規模イベントリマインド：{len(eve)}件',
        value = conf
      )
      print("mid-eve success")
      eve = {}
      with open("small-eve_data.json", 'r') as f:
        data = json.load(f)
      for k1, v1 in data.items():
        for k2, v2 in v1["time"].items():
          dt = datetime.datetime.strptime(v2, s_format)
          if now < dt:
            CHANNEL_ID = int(k1)
            channel = self.bot.get_channel(CHANNEL_ID)
            ticket = data[str(k1)]["status"]["set_ticket"]
            honban = data[str(k1)]["status"]["set_honban"]
            eve[str(v2)] = [channel.name, ticket, honban, k2]
            break
      conf = ""
      for k, v in eve.items():
        if v[3] == "st1": l = "チケット①"
        if v[3] == "st2": l = "チケット②"
        if v[3] == "st3": l = "チケット③"
        if v[3] == "sh1": l = "本番①"
        if v[3] == "sh2": l = "本番②"
        if v[3] == "sh3": l = "本番③"
        if v[3] == "sh4": l = "本番④"
        if v[3] == "sh5": l = "本番⑤"
        if v[3] == "sh6": l = "本番⑥"
        if v[3] == "sh7": l = "本番⑦"
        if v[3] == "sh8": l = "本番⑧"
        conf += f"**{v[0]}**\n> チケット販売日 ⇒ {v[1]}\n> イベント本番日 ⇒ {v[2]}\n> 次回リマインド ⇒ {k}\n> ▼{l}\n\n"
      embed.add_field(
        name = f'小規模（謎解き）イベントリマインド：{len(eve)}件',
        value = conf
      )
      print("small-eve success")
      eve = {}
      with open("final_meet.json", 'r') as f:
        data = json.load(f)
      for k, v in data.items():
        time = v["time"]
        dt = datetime.datetime.strptime(time, s_format)
        if now < dt:
          CHANNEL_ID = int(k)
          channel = self.bot.get_channel(CHANNEL_ID)
          GUILD_ID = v["guild"]
          use_guild = self.bot.get_guild(GUILD_ID)
          ROLE_ID = v["role"]
          send_role = use_guild.get_role(ROLE_ID)
          eve[str(time)] = [channel.name, send_role.name]
      conf = ""
      for k, v in eve.items():
        conf += f"{k}▼{v[0]}\n"
      embed.add_field(
        name = f'最終打ち合わせ告知リマインド：{len(eve)}件',
        value = conf, inline = False
      )
      print("final-meet success")
      eve = {}
      with open("free_rem.json", 'r') as f:
        data = json.load(f)
      for v in data.values():
        time = v["time"]
        dt = datetime.datetime.strptime(time, s_format)
        if now < dt:
          eve[str(time)] = v["memo"]
      conf = ""
      for k, v in eve.items():
        conf += f"{k}▼{v}\n"
      embed.add_field(
        name = f'フリーリマインド：{len(eve)}件',
        value = conf, inline = False
      )
      print("free-rem success")
      await ctx.send(embed = embed, ephemeral = True)
      #await ctx.send(debug_txt, embed=embed)
    elif item == "テンプレ確認":
      text = f"適用されているすべてのテンプレを確認します"
      #await ctx.send(text, ephemeral = True)
      m_embed = discord.Embed(
        title = f"中規模イベントのテンプレ",
        color = discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255))
      )
      s_embed = discord.Embed(
        title = f"小規模ベントのテンプレ",
        color = discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255))
      )
      #print("embed Create success")
      num_maru = ["⓪", "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨"]
      for kibo in ["m", "s"]:
        if kibo == "m": await ctx.send(embed = m_embed, ephemeral = True)
        if kibo == "s": await ctx.send(embed = s_embed, ephemeral = True)
        for i in range(1,4):
          with open(f"{kibo}t{str(i)}.txt", "r", encoding = "utf-8") as f:
            temp = f.read()
          text = f"**チケット{num_maru[i]}**\n\n{temp}"
          await ctx.send(text, ephemeral = True)
          #exec(f'{kibo}_embed.add_field(name = "チケット{num_maru[i]}", value = temp, inline = False)')
        for i in range(1,9):
          with open(f"{kibo}h{str(i)}.txt", "r", encoding = "utf-8") as f:
            temp = f.read()
          text = f"**本番{num_maru[i]}**\n\n{temp}"
          await ctx.send(text, ephemeral = True)
          #exec(f'{kibo}_embed.add_field(name = "本番{num_maru[i]}", value = temp, inline = False)')
      with open(f"final_meet.txt", "r", encoding = "utf-8") as f:
        temp = f.read()
      final_embed = discord.Embed(
        title = f"最終打ち合わせ告知のテンプレ",
        #description = temp,
        color = discord.Colour.from_rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255))
      )
      await ctx.send(embed = final_embed, ephemeral = True)
      await ctx.send(temp, ephemeral = True)
      #await ctx.send(debug_txt, embed=embed)
  
  @tasks.loop(time=times)
  async def remind_check(self):
    dt_now_jst = datetime.datetime.now(self.tz_jst)
    now = dt_now_jst.strftime('%y/%m/%d %H:%M')
    print(now, "今")
    #フリーリマインドの処理開始
    with open("free_rem.json", 'r') as f:
      data = json.load(f)
    for k, v in data.items():
      if now == v["time"]:
        memo = v["memo"]
        CHANNEL_ID = int(k)
        channel = self.bot.get_channel(CHANNEL_ID)
        USER_ID = v["user"]
        print(USER_ID)
        user = self.bot.get_user(USER_ID)
        print(user)
        desc = f'{memo}'
        embed = discord.Embed(
          title = f"{channel}からのフリーリマインドです",
          description = desc,
          color = discord.Colour.red()
        )
        try:
          await user.send(embed = embed)
          debug_txt = f"デバッグ用。※納品物では表示されません"
          #await channel.send(debug_txt, embed=embed)
        except NameError:
          print("フリーリマインド処理でエラー発生")
    #最終打ち合わせ告知の処理開始
    with open("final_meet.json", 'r') as f:
      data = json.load(f)
    for k, v in data.items():
      if now == v["time"]:
        with open(f'final_meet.txt', 'r', encoding="utf-8") as f:
          speech = f.read()
        GUILD_ID = v["guild"]
        use_guild = self.bot.get_guild(GUILD_ID)
        ROLE_ID = v["role"]
        send_role = use_guild.get_role(ROLE_ID)
        CHANNEL_ID = int(k)
        channel = self.bot.get_channel(CHANNEL_ID)
        USER_ID = v["user"]
        user = use_guild.get_member(USER_ID)
        chat = f'{send_role.mention}{user.mention}\n{speech}'
        try:
          await channel.send(chat)
        except NameError:
          print("最終打ち合わせ処理でエラー発生")
    #イベント：中規模リマインドの処理開始
    with open("mid-eve_data.json", 'r') as f:
      data = json.load(f)
    if data == {}:
      print(f'mid-eve_data.jsonが初期状態です。\n「/イベント作成 中規模」を行ってください')
    else:
      rim_time = {}
      for k, v in data.items():
        rim_time[k] = v["time"]
      for k, v in rim_time.items():
        for k2, v2 in v.items():
          #if k2 == "i2":
          #  if not data[str(k)]["status"]["illust"] == "NO":
          #    print(f'イラスト：{data[str(k)]["status"]["illust"]}')
          #    continue
          if now == v2:
            with open(f'{k2}.txt', 'r', encoding="utf-8") as f:
              speech = f.read()
            GUILD_ID = data[str(k)]["guild"]
            use_guild = self.bot.get_guild(GUILD_ID)
            ROLE_ID = data[str(k)]["role"]
            send_role = use_guild.get_role(ROLE_ID)
            CHANNEL_ID = int(k)
            channel = self.bot.get_channel(CHANNEL_ID)
            USER_ID = data[str(k)]["user"]
            user = use_guild.get_member(USER_ID)
            if data[str(k)]["notic_to_me"] == True:
              chat = f'{send_role.mention}{user.mention}\n{speech}'
            else:
              chat = f'{send_role.mention}\n{speech}'
            try:
              await channel.send(chat)
            except NameError:
              print("中規模イベントリマインド処理でエラー発生")
    #イベント：小規模(謎解き)リマインドの処理開始
    with open("small-eve_data.json", 'r') as f:
      data = json.load(f)
    if data == {}:
      print(f'small-eve_data.jsonが初期状態です。\n「/イベント作成 小規模（謎解き）」を行ってください')
    else:
      rim_time = {}
      for k, v in data.items():
        rim_time[k] = v["time"]
      for k, v in rim_time.items():
        for k2, v2 in v.items():
          #if k2 == "i2":
          #  if not data[str(k)]["status"]["illust"] == "NO":
          #    print(f'イラスト：{data[str(k)]["status"]["illust"]}')
          #    continue
          if now == v2:
            with open(f'{k2}.txt', 'r', encoding="utf-8") as f:
              speech = f.read()
            GUILD_ID = data[str(k)]["guild"]
            use_guild = self.bot.get_guild(GUILD_ID)
            ROLE_ID = data[str(k)]["role"]
            send_role = use_guild.get_role(ROLE_ID)
            CHANNEL_ID = int(k)
            channel = self.bot.get_channel(CHANNEL_ID)
            USER_ID = data[str(k)]["user"]
            user = use_guild.get_member(USER_ID)
            if data[str(k)]["notic_to_me"] == True:
              chat = f'{send_role.mention}{user.mention}\n{speech}'
            else:
              chat = f'{send_role.mention}\n{speech}'
            try:
              await channel.send(chat)
            except NameError:
              print("小規模イベントリマインド処理でエラー発生")

  @remind_check.before_loop
  async def before_remind_check(self):
    print('waiting...')
    await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
  await bot.add_cog(Schedule(bot))