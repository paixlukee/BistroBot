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

class Help:
    def __init__(self, bot):
        self.bot = bot
        self.prefix = 'r!'

    @commands.group(aliases=['cmds', 'commands', 'Help'])
    async def help(self, ctx):
        embed = discord.Embed(description='Welcome to **Restaurant** Here is a list of commands that you are able to use.\n\n'\
        f'`{self.prefix}start` - **Create your own restaurant.**\n'\
        f'`{self.prefix}restaurant [@user]` - **Show restaurant details**\n'\
        f'`{self.prefix}stock` - **Add more items to your restaurant\'s stock**\n'\
        f'`{self.prefix}boost` - **Buy a boost or view your current boost**\n'\
        f'`{self.prefix}daily` - **Receive your daily $200**\n'\
        f'`{self.prefix}payout` - **Collect your restaurant earnings**\n'\
        f'`{self.prefix}balance` - **Check your cash balance**\n'
        )
        embed.set_image(url="https://i.ibb.co/chxrYtn/restaurantbanner.png")
        embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the command.")
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Help(bot))
