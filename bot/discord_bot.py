"""
discord_bot.py

Main bot process that interacts with Discord. 
Scheduled task checks for updates from modules and sends to Discord.
"""

import os
import asyncio
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from shelby import is_shelby_message, get_shelby_message
from patchnotes import fetch_latest_patchnotes
from redditmatches import fetch_latest_postmatches
from datetime import datetime
import log_module

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
CHANNEL_ID = int(os.getenv("MAIN_CHANNEL_ID"))

#24hr format
REDDIT_TIMES = [0, 8, 12, 16, 20, 23]
PATCH_TIME = [11, 16]

last_reddit_check = None
last_patch_check = None

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

logger = log_module.create_logger("valorant-bot.log")

@bot.event
async def on_ready():
    print(f"{bot.user} connected to {GUILD_ID}")
    scheduled_check_loop.start()
    # num_commands_synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    # print(f"Synced {len(num_commands_synced)} slash commands for guild {GUILD_ID}")

@bot.event
async def on_message(message: discord.Message):
    #ignore bot's messages
    if message.author.bot:
        return
    
    #send dms to bot to console
    if isinstance(message.channel, discord.DMChannel):
        print(f"{message.author}: {message.content}")
        return
    
    if(is_shelby_message(message)):
        await message.channel.send(get_shelby_message())
    
    await bot.process_commands(message)

"""
Checks every 30 minutes to see if the current hour is an hour to be checked for post matches or patch notes.
If it is a check hour, fetches the latest post matches/patch notes. If none, do nothing. Otherwise, post to Discord.
Note: task starts when script is run and checks are based on hour, not minutes.
"""
@tasks.loop(minutes=30)
async def scheduled_check_loop():
    global last_reddit_check, last_patch_check

    now = datetime.now() #separated so now can be stored and .date() can be checked
    current_hour = now.hour

    channel = bot.get_channel(CHANNEL_ID)
    
    if current_hour in REDDIT_TIMES:
        if not last_reddit_check or last_reddit_check.date() != now.date() or last_reddit_check.hour != current_hour:
            logger.info(f"Fetching Reddit posts for hour {current_hour}...")
            try:
                embeds = fetch_latest_postmatches()
                logger.info("Successfully fetched Reddit posts.")
            except Exception as e:
                logger.exception(f"Error while fetching Reddit posts: {e}")
            last_reddit_check = now
            if len(embeds) == 0:
                logger.info("No new Reddit posts.")
            else:
                for e in embeds:
                    await channel.send(embed=e)
                logger.info(f"Sent Reddit posts to channel {channel.name}")
    
    if current_hour in PATCH_TIME:
        if not last_patch_check or last_patch_check.date() != now.date() or last_patch_check.hour != current_hour:
            logger.info(f"Fetching patch notes for hour {current_hour}...")
            try:
                embed = fetch_latest_patchnotes()
                logger.info("Successfully fetched patch notes.")
            except Exception as e:
                logger.exception(f"Error while fetching patch notes: {e}")
            last_patch_check = now
            if embed is None:
                logger.info("No new patch notes.")
            else:
                await channel.send("##" + str(embed.title).replace("VALORANT", "") + "\n@here", embed=embed)
                logger.info(f"Sent patch notes to channel {channel.name}")


# Debug commands

# @bot.command(name="test")
# async def test(ctx):
#     embeds = fetch_latest_postmatches()
#     if len(embeds) == 0:
#         await ctx.send("No new post matches.")
#     else:
#         for e in embeds:
#             await ctx.send(embed=e)

# @bot.command(name="test2")
# async def test(ctx):
#     embed = fetch_latest_patchnotes()
#     if embed is None:
#         await ctx.send("No new patch notes.")
#     else:
#         await ctx.send("##" + str(embed.title).replace("VALORANT", "") + "\n@here", embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)