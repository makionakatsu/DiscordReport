import discord
import os
import datetime
import pytz
from discord.ext import commands

TOKEN = os.environ["DISCORD_TOKEN"]
GUILD_ID = int(os.environ["GUILD_ID"])

japan_timezone = pytz.timezone("Asia/Tokyo")
now = datetime.datetime.now(japan_timezone)
twenty_four_hours_ago = now - datetime.timedelta(hours=24)
DATE = twenty_four_hours_ago.strftime("%Y-%m-%d")

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
    await bot.close()

bot.run(TOKEN)
