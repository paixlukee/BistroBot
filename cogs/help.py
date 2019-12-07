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

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = 'r!'

    @commands.group(aliases=['cmds', 'commands', 'Help'])
    async def help(self, ctx):
        embed = discord.Embed(description='Welcome to **Restaurant** Here is a list of commands that you are able to use.\n\n'\
        f'`{self.prefix}start` - **Create your own restaurant.**\n'\
        f'`{self.prefix}restaurant [@user]` - **Show restaurant details**\n'\
        f'`{self.prefix}random` - **View a random restaurant**\n'\
        f'`{self.prefix}menu <restaurant-name>` - **View a restaurant menu**\n'\
        f'`{self.prefix}rate <@user>` - **Rate someone\'s restaurant**\n'\
        f'`{self.prefix}set` - **Configurate your restaurant settings**\n'\
        f'`{self.prefix}buy` - **Buy an item from the restaurant shop**\n'\                  
        f'`{self.prefix}user [@user]` - **View a user profile**\n'\
        f'`{self.prefix}balance` - **View your balance**\n'\
        f'`{self.prefix}donate <@user> <amount>` - **Donate money to someone else**\n'\
        f'`{self.prefix}daily` - **Receive your daily cash**\n'\
        f'`{self.prefix}work` - **Work at your restaurant and get money**\n'\
        f'`{self.prefix}clean` - **Clean the restaurant and gain XP**\n'\
        )
        embed.set_image(url="https://i.ibb.co/chxrYtn/restaurantbanner.png")
        embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the command.")
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Help(bot))
