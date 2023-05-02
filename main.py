import os
import nextcord as discord
from nextcord.ext import commands
import datetime
import pytz
import csv


def get_target_date(timezone):
    now = datetime.datetime.now(timezone)
    yesterday = now - datetime.timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def write_log_to_csv(found_messages, target_date):
    file_name = f"discord_log_{target_date}.csv"
    with open(file_name, "w", encoding="utf-8", newline="") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Timestamp", "Channel", "Author", "Content"])

        for msg in found_messages:
            jst_created_at = convert_to_jst(msg.created_at)
            formatted_timestamp = jst_created_at.strftime("%Y-%m-%d %H:%M:%S")
            csv_writer.writerow([formatted_timestamp, msg.channel.name, str(msg.author), msg.content])

    return file_name


def convert_to_jst(dt):
    utc = pytz.utc
    jst = pytz.timezone("Asia/Tokyo")
    return dt.astimezone(jst)


async def fetch_logs(guild, target_date, member=None):
    found_messages = []
    for channel in guild.text_channels:
        if not member:
            try:
                async for msg in channel.history(limit=10000):
                    if msg.created_at.date() == target_date:
                        found_messages.append(msg)
            except discord.errors.Forbidden:
                print(f"Skipping channel {channel.name} due to insufficient permissions.")
                continue
        else:
            try:
                async for msg in channel.history(limit=10000, user=member):
                    if msg.created_at.date() == target_date:
                        found_messages.append(msg)
            except discord.errors.Forbidden:
                print(f"Skipping channel {channel.name} due to insufficient permissions.")
                continue

    if not found_messages:
        print(f"No messages found for date {target_date}.")

    return found_messages


async def send_log_to_channel(guild, log_file_name, channel_id):
    channel = guild.get_channel(channel_id)
    if channel is None:
        print(f"Error: Channel with ID {channel_id} not found.")
        return

    with open(log_file_name, "rb") as file:
        await channel.send(file=discord.File(file, filename=log_file_name))

TOKEN = os.environ["DISCORD_TOKEN"]
GUILD_ID = int(os.environ["GUILD_ID"])
DATE = get_target_date(pytz.timezone("Asia/Tokyo"))
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

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
        log_file_name = write_log_to_csv(found_messages, target_date)
        await send_log_to_channel(guild, log_file_name, CHANNEL_ID)
    else:
        print(f"No messages found for date {target_date}.")

    await bot.close()

bot.run(TOKEN)
