import os
import discord
from discord.ext import commands
import datetime
import pytz

# 環境変数からTOKENとGUILD_IDを取得
TOKEN = os.environ["DISCORD_TOKEN"]
GUILD_ID = int(os.environ["GUILD_ID"])

# 日本のタイムゾーンを設定
japan_timezone = pytz.timezone("Asia/Tokyo")

# 現在の日時を取得し、1日前の日付を計算
now = datetime.datetime.now(japan_timezone)
yesterday = now - datetime.timedelta(days=1)
DATE = yesterday.strftime("%Y-%m-%d")

# Intents設定
intents = discord.Intents.default()
intents.messages = True

# Botインスタンスを作成
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

    # ターゲットのギルドを取得
    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    target_date = datetime.datetime.strptime(DATE, "%Y-%m-%d").date()

    if not guild:
        print("Error: Guild not found.")
        return

    # ログファイルを作成
    log_file = open(f"discord_log_{DATE}.txt", "w", encoding="utf-8")

    # ギルド内のすべてのテキストチャンネルをループ
    for channel in guild.text_channels:
        try:
            print(f"Processing channel: {channel.name}")  # 処理開始のログ
            async for msg in channel.history(limit=5000):
                if msg.created_at.date() == target_date:
                    log_file.write(f"[{channel.name}] {msg.author}: {msg.content}\n")

                    for attachment in msg.attachments:
                        log_file.write(f"Attachment: {attachment.url}\n")
            print(f"Finished processing channel: {channel.name}")  # 処理完了のログ
        except discord.errors.Forbidden:
            print(f"Skipping channel {channel.name} due to insufficient permissions.")
            continue

    # ログファイルを閉じる
    log_file.close()
    print("Log file created.")
    await bot.logout()

bot.run(TOKEN)
