import discord
from discord.ext import commands
import datetime
import pytz

TOKEN = "your_discord_token"
GUILD_ID = 123456789
japan_timezone = pytz.timezone("Asia/Tokyo")
now = datetime.datetime.now(japan_timezone)
yesterday = now - datetime.timedelta(days=1)
DATE = yesterday.strftime("%Y-%m-%d")

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

    guild = discord.utils.get(bot.guilds, id=GUILD_ID)
    target_date = datetime.datetime.strptime(DATE, "%Y-%m-%d").date()

    if not guild:
        print("Error: Guild not found.")
        return

    log_file = open(f"discord_log_{DATE}.txt", "w", encoding="utf-8")

    for channel in guild.text_channels:
        try:
            async for msg in channel.history(limit=10000):
                if msg.created_at.date() == target_date:
                    log_file.write(f"[{channel.name}] {msg.author}: {msg.content}\n")

                    for attachment in msg.attachments:
                        log_file.write(f"Attachment: {attachment.url}\n")
        except discord.errors.Forbidden:
            print(f"Skipping channel {channel.name} due to insufficient permissions.")
            continue

    log_file.close()
    print("Log file created.")
    await bot.logout()  # ログ取得が完了したらBotをログアウトさせます

bot.run(TOKEN)

