import discord
from discord.ext import commands
import datetime
import time
import subprocess
import traceback
import requests
import random
from random import choice, randint
import aiohttp
import asyncio
import sys
import json
from pymongo import MongoClient
import schedule
import config
import logging 

client = MongoClient(config.mongo_client)
db = client['siri']

async def get_pre(bot, message):
    posts = db.utility.find_one({"utility": "prefixes"})
    try:    
        for x in posts.get("prefixes", []):
            if x['guild'] == message.guild.id:
                pref = x['prefix']
                return pref
            
        #return ['b.', f"<@!{bot.user.id}> ", f"<@{bot.user.id}> "]
     
    except Exception as e:
        print(f"Error w/ prefix in {message.guild.id}! E: {e}")
        return "b."
    return ['b.', f"<@!{bot.user.id}> ", f"<@{bot.user.id}> "]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

bot = commands.Bot(command_prefix=get_pre, intents=intents, sharded=True)
extensions = ['bot', 'help', 'shop', 'user', 'dev', 'tasks', 'cookoff', 'topgg']

async def status_task():
    users = len(set(bot.get_all_members()))
    await bot.change_presence(activity=discord.Game(name=f'b.help | bistrobot.co'))

@bot.event
async def on_ready():
    print(f'\x1b[1;36;40mDiscord Version:\x1b[0m {discord.__version__}\n------')
    print(f'\x1b[1;36;40m[ACTIVATED]\x1b[0m Logged in as {bot.user.name} ({bot.user.id})')
    print("\x1b[1;36;40m[WARNING]\x1b[0m BistroBot will soon take over the world..\n")
    bot.loop.create_task(status_task())

@bot.event
async def on_guild_join(guild):
    log = bot.get_channel(653466873089753098)
    embed = discord.Embed(colour=0x62f442, description=f"<:plus_icon:1341860287375998986> Bistro has joined `{guild.name}`! BB is now in `{str(len(bot.guilds))}` guilds!")
    online = len([x for x in guild.members if x.status == discord.Status.online])
    idle = len([x for x in guild.members if x.status == discord.Status.idle])
    dnd = len([x for x in guild.members if x.status == discord.Status.dnd])
    offline = len([x for x in guild.members if x.status == discord.Status.offline])
    embed.add_field(name=f"Members ({len(guild.members)}):", value=f"<:online:701012643263283242> {online} <:idle:701016198531383316> {idle} <:dnd:1341854951550226513> {dnd} <:offline:1341855008970379345> {offline}")
    embed.set_footer(text=f'ID: {guild.id}', icon_url=guild.icon.url if guild.icon else None)
    await log.send(embed=embed)
    embed = discord.Embed(description="Thank you for adding me! Do `b.help` to see a list of my commands. Do `b.start` to create your restaurant!")
    embed.add_field(name="Join my support server!", value="https://discord.gg/BCRtw7c")
    embed.set_image(url="https://media.discordapp.net/attachments/1325282246181130330/1328917037409374208/FF17CB1B-C653-4A06-A490-7BB9C4A38DFE.jpg?ex=678871ef&is=6787206f&hm=dba385547438a9343cd1c9c63b12a2b3e83af6c91ab06b9b0779d78e1d80142d&=&format=webp&width=2160&height=474")
    embed.set_footer(text="BistroBot created by paixlukee - Thank you for adding me!", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    for channel_name in ["bot", "bots", "bot-commands", "bot-spam", "bot-channel", "testing", "testing-1", "general", "shitposts", "off-topic", "media"]:
        channel = discord.utils.get(guild.text_channels, name=channel_name)
        if channel:
            try:
                await channel.send(embed=embed)
                break
            except discord.Forbidden:
                continue

@bot.event
async def on_guild_remove(guild):
    log = bot.get_channel(653466873089753098)
    embed = discord.Embed(colour=0xf44141, description=f"<:minus_icon:1341860249891639397> Bistro has been kicked from `{guild.name}`.. BB is now in `{str(len(bot.guilds))}` guilds.")
    embed.set_footer(text=f'ID: {guild.id}', icon_url=guild.icon.url if guild.icon else None)
    await log.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    else:
        await bot.process_commands(message)

@bot.event
async def on_error(event, *args, **kwargs):
    error_message = traceback.format_exc()

    logging.error(f"An error occurred in event {event}: {error_message}")

@bot.check
async def globally_block_dms(ctx):
    banlist = db.utility.find_one({"utility": "banlist"})
    if not banlist or 'banned' not in banlist or not isinstance(banlist['banned'], list):
        return True  
    return ctx.author.id not in banlist['banned']


async def main():
    async with bot:
        bot.remove_command("help")
        for extension in extensions:
            try:
                await bot.load_extension(f'cogs.{extension}')
            except Exception as e:
                print(f'Failed to load extension {extension}: {e}')
        await bot.start(config.token, reconnect=True)

if __name__ == '__main__':
    asyncio.run(main())