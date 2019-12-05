import discord
from discord.ext import commands
import datetime
import requests
import random
import math
import time
from discord.ext.commands import errors, converter
from random import choice, randint
from random import choice, randint as rnd
import aiohttp
import asyncio
import json
import os
import config
import psutil

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = 'r!'
        self.process = psutil.Process(os.getpid())
        self.rs = []

    @commands.command(aliases=['Stats', 'info', 'botinfo', 'status'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def stats(self, ctx):
        
        users = len(set(self.bot.get_all_members()))
        channels = []
        for guild in self.bot.guilds:
            for channel in guild.channels:
                channels.append(channel)
        channels = len(channels)
        emojis = len(self.bot.emojis)
        commands = len(self.bot.all_commands)

        author = ctx.message.author

        ram = self.process.memory_full_info().rss / 1024**2

        stat = discord.Embed(colour=0xa82021, description=f"**Restaurant** `by lukee#0420`\n\n\n" \
        f"\> **Python**... `3.6`\n>" \
        f"\> **Ubuntu**... `18.04`\n>" \
        f"\> **RAM Usage**... `{ram:.2f}MB`\n\n"
        f"I am in **{str(len(self.bot.guilds))} servers**!\n"\
        f"I can view **{channels} channels**!\n"\
        f"I am with **{users} users**!\n"\
        f"I can use **{emojis} emojis**!\n"\
        f"[Invite](https://discordapp.com/api/oauth2/authorize?client_id=648065060559781889&permissions=8192&scope=bot) |"\
        f" [Support](https://discord.gg/BCRtw7c)")
        stat.set_footer(text="Thanks for using Restaurant! | Res-V1")
        await ctx.send(embed=stat)



def setup(bot):
    bot.add_cog(Dev(bot))
