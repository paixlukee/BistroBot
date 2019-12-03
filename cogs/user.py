import discord
from discord.ext import commands
import datetime
import requests
import random
import math
import time
from discord.ext.commands import errors, converter
from random import randint, choice as rnd
import aiohttp
import asyncio
import json
import os
import config
from pymongo import MongoClient
import pymongo
import string
import food

client = MongoClient(config.mongo_client)
db = client['siri']

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = 'r!'

        
    @commands.command(aliases=['User', 'Profile', 'profile'])
    async def user(self, ctx, user:discord.User=None):
        if not user:
            user = ctx.author
        post = db.market.find_one({"owner": int(user.id)})
        embed = discord.Embed(colour=0xa82021, description=str(user))
        embed.set_author(icon_url=user.avatar_url_as(format='png'), name="User Stats")
        embed.set_thumbnail(url=user.avatar_url_as(format='png'))
        embed.add_field(name="Restaurant", value=post['name'])
        embed.add_field(name="Money", value="$" + str(post['money']))
        await ctx.send(embed=embed)
        
    @commands.command(aliases=['Balance', 'bal'])
    async def balance(self, ctx, user:discord.User=None):
        if not user:
            user = ctx.author
        post = db.market.find_one({"owner": int(user.id)})
        await ctx.send(f"**{user.name}**'s balance is **{post['money']}**")



def setup(bot):
    bot.add_cog(Shop(bot))
