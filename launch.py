import discord
from discord.ext import commands

import datetime

import time
import subprocess
import traceback
from discord.ext.commands import errors, converter
import requests
import random
from random import choice as rnd
from random import choice, randint

import aiohttp
import asyncio
import sys
import json

import config
from pymongo import MongoClient
import pymongo

client = MongoClient(config.mongo_client)
db = client['siri']

bot = commands.AutoShardedBot(shard_count=2, command_prefix=commands.when_mentioned_or("r!"))
extensions = ['help', 'shop', 'user', 'dev', 'dbl']

async def status_task():
    users = len(set(bot.get_all_members()))
    while True:
        await bot.change_presence(activity=discord.Game(name=f'r!help | {str(len(bot.guilds))} guilds', type=2))
        await asyncio.sleep(30)

@bot.event
async def on_ready():
    print('\x1b[1;34;40m' + 'Discord Version: ' + '\x1b[0m' + f'{discord.__version__}\n------')
    print('\x1b[1;36;40m' + '[UPDATE]: ' + '\x1b[0m' + 'Logged in as: {bot.user.name} ({str(bot.user.id)})')
    print("\x1b[1;33;40m" + "[AWAITING]: " + "\x1b[0m" + "Run 'r!load all'")
    bot.loop.create_task(status_task())

@bot.event
async def on_guild_join(guild):
    log = bot.get_channel(653466873089753098)
    server = guild
    embed = discord.Embed(colour=0x62f442, description=f"RB has joined `{guild.name}`! RB is now in `{str(len(bot.guilds))}` guilds!")
    online = len([x for x in guild.members if x.status == discord.Status.online])
    idle = len([x for x in guild.members if x.status == discord.Status.idle])
    dnd = len([x for x in guild.members if x.status == discord.Status.dnd])
    offline = len([x for x in guild.members if x.status == discord.Status.offline])
    embed.add_field(name=f"Members ({len(guild.members)}):", value=f"<:status_online:596576749790429200> {online} <:status_idle:596576773488115722> {idle} <:status_dnd:596576774364856321> {dnd} <:status_offline:596576752013279242> {offline}")
    embed.set_footer(text=f'ID: {guild.id}', icon_url=guild.icon_url_as(format='png'))
    await log.send(embed=embed)
    server = guild
    targets = [
            discord.utils.get(server.channels, name="bot"),
            discord.utils.get(server.channels, name="bots"),
            discord.utils.get(server.channels, name="bot-commands"),
            discord.utils.get(server.channels, name="bot-spam"),
            discord.utils.get(server.channels, name="bot-channel"),
            discord.utils.get(server.channels, name="testing"),
            discord.utils.get(server.channels, name="testing-1"),
            discord.utils.get(server.channels, name="general"),
            discord.utils.get(server.channels, name="shitposts"),
            discord.utils.get(server.channels, name="off-topic"),
            discord.utils.get(server.channels, name="media"),
            guild.get_member(guild.owner.id)
            ]
    embed = discord.Embed(description="Thank you for adding me! Do `r!help` to see a list of my commands. Do `r!start` to create your restaurant!")
    embed.add_field(name="Join my support server!", value="https://discord.gg/BCRtw7c")
    embed.set_image(url="https://i.ibb.co/mCD21pb/restaurantbanner.png")
    embed.set_footer(text="Restaurante created by lukee#0420 - Thank you for adding me!", icon_url=bot.user.avatar_url)
    for x in targets:
        try:
            await x.send(embed=embed)
        except:
            continue
        break

@bot.event
async def on_guild_remove(guild):
    log = bot.get_channel(653466873089753098)
    embed = discord.Embed(colour=0xf44141, description=f"RB has been kicked from `{guild.name}`.. RB is now in `{str(len(bot.guilds))}` guilds.")
    embed.set_footer(text=f'ID: {guild.id}', icon_url=guild.icon_url_as(format='png'))
    await log.send(embed=embed)


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    else:
        await bot.process_commands(message)

@bot.check
async def globally_block_dms(ctx):
    return ctx.author.id not in db.utility.find_one({"utility":"banlist"})



if __name__ == '__main__':
    bot.load_extension("cogs.bot")
    bot.remove_command("help")
    for x in extensions:
        bot.load_extension('cogs.'+x)



bot.run(config.token, bot=True, reconnect=True)
