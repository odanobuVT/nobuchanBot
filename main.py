import discord
from discord.ext import commands
import os #getenvに必須
from dotenv import load_dotenv
load_dotenv()
#from keep_alive import keep_alive

prefix = ['!', '?']
COGS = [
  #"confirm_temp",
  "schedule"
]

class JapaneseHelpCommand(commands.DefaultHelpCommand):
  def __init__(self):
    super().__init__()
    self.commands_heading = "コマンド:"
    self.no_category = "その他"
    self.command_attrs["help"] = "コマンド一覧と簡単な説明を表示"

  def get_ending_note(self):
    return (f"各コマンドの説明: {prefix[0]}help コマンド名\n"
            f"各カテゴリの説明: {prefix[0]}help カテゴリ名\n")

class MyBot(commands.Bot):
  """起動用のあれこれ"""
  async def setup_hook(self):
    for cog in COGS:
      try:
        await self.load_extension(cog)
      except Exception as e:
        print(e)
    await self.tree.sync()

  async def on_ready(self):
    print('Logged in as')
    for cog in COGS:
      try:
        await self.reload_extension(cog)
      except Exception as e:
        print(e)
    print(self.user.name)
    print(self.user.id)
    print('------')
    
    
# 接続に必要なオブジェクトを生成
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.presences = True
intents.members = True
bot: commands.Bot = MyBot(
  command_prefix = prefix,
  case_insensitive = True, #コマンドの大文字小文字を無視する(True)
  intents = intents, 
  status = discord.Status.online, 
  help_command = JapaneseHelpCommand()
)
  
#エラー処理
@bot.event
async def on_command_error(ctx: commands.Context, error):
  if ctx.author.bot:
      return
  if isinstance(error, commands.errors.CheckFailure):
    await ctx.send('ごめんなさい！こちらのコマンドを使用することは出来ません🤖💦', ephemeral = True)

while __name__ == '__main__':
  try:
    #keep_alive()
    bot.run(os.getenv("TOKEN"))
  except discord.errors.HTTPException as e:
    print(e)
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    os.system('kill 1')