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


bot = commands.Bot(command_prefix="r!")


async def status_task():
    users = len(set(bot.get_all_members()))
    while True:
        await bot.change_presence(activity=discord.Game(name=f'r!help | {str(len(bot.guilds))}', type=2))
        await asyncio.sleep(30)

@bot.event
async def on_ready():
    print('\x1b[1;34;40m' + 'Discord Version: ' + '\x1b[0m' + f'{discord.__version__}\n------')
    print('\x1b[1;36;40m' + '[UPDATE]: ' + '\x1b[0m' + 'Logged in as: {bot.user.name} ({str(bot.user.id)})')
    print("\x1b[1;33;40m" + "[AWAITING]: " + "\x1b[0m" + "Run 'r!load all'")
    bot.loop.create_task(status_task())

@bot.event
async def on_guild_join(guild):
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
    embed.add_field(name="Join my support server!", value="https://discord.gg/tNf6REt")
    embed.set_image(url="https://i.ibb.co/mCD21pb/restaurantbanner.png")
    embed.set_footer(text="Restaurante created by lukee#0420 - Thank you for adding me!", icon_url=bot.user.avatar_url)
    for x in targets:
        try:
            await x.send(embed=embed)
        except:
            continue
        break


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    else:
        await bot.process_commands(message)


if __name__ == '__main__':
    bot.load_extension("cogs.bot")
    bot.remove_command("help")
    bot.load_extension("cogs.help")
    bot.load_extension("cogs.shop")


bot.run(config.token, bot=True, reconnect=True)
