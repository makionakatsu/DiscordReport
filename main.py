import os
import discord
from discord.ext import commands
import datetime
import pytz

def get_target_date(timezone):
    now = datetime.datetime.now(timezone)
    yesterday = now - datetime.timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

async def fetch_logs(guild, target_date, member=None):
    found_messages = []
    for channel in guild.text_channels:
        if not member:
            channel_has_messages = False
            async for msg in channel.history(limit=10000).filter(lambda msg: msg.created_at.date() == target_date):
                channel_has_messages = True
                found_messages.append(msg)
                break
        else:
            try:
                async for msg in channel.history(limit=10000, user=member).filter(lambda msg: msg.created_at.date() == target_date):
                    found_messages.append(msg)
                    break
            except discord.errors.Forbidden:
                print(f"Skipping channel {channel.name} due to insufficient permissions.")
                continue

    if not found_messages:
        print(f"No messages found for date {target_date}.")

    return found_messages

TOKEN = os.environ["DISCORD_TOKEN"]
GUILD_ID = int(os.environ["GUILD_ID"])
DATE = get_target_date(pytz.timezone("Asia/Tokyo"))

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

    found_messages = await fetch_logs(guild, target_date)

    if found_messages:
        for msg in found_messages:
            print(f"{msg.author}: {msg.content}")

    await bot.close()

bot.run(TOKEN)
