import os
import discord
from discord.ext import commands
import datetime
import pytz

def get_target_date():
    japan_timezone = pytz.timezone("Asia/Tokyo")
    now = datetime.datetime.now(japan_timezone)
    yesterday = now - datetime.timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

async def fetch_logs(guild, target_date):
    log_file = open(f"discord_log_{target_date}.txt", "w", encoding="utf-8")

    for channel in guild.text_channels:
        try:
            print(f"Processing channel: {channel.name}")
            async for msg in channel.history(limit=10000):
                if msg.created_at.date() == target_date:
                    log_file.write(f"[{channel.name}] {msg.author}: {msg.content}\n")

                    for attachment in msg.attachments:
                        log_file.write(f"Attachment: {attachment.url}\n")
            print(f"Finished processing channel: {channel.name}")
        except discord.errors.Forbidden:
            print(f"Skipping channel {channel.name} due to insufficient permissions.")
            continue

    log_file.close()
    print("Log file created.")

TOKEN = os.environ["DISCORD_TOKEN"]
GUILD_ID = int(os.environ["GUILD_ID"])
DATE = get_target_date()

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

    await fetch_logs(guild, target_date)
    await bot.logout()

bot.run(TOKEN)
