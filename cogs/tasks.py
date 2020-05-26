import discord
from discord.ext import commands, tasks
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
from pymongo import MongoClient
import pymongo

client = MongoClient(config.mongo_client)
db = client['siri']

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pay.start()

    def cog_unload(self):
        self.pay.cancel()

    @tasks.loop(seconds=15.0)
    async def pay(self):
        print('Paying all restaurants...')
        all = db.market.find()
        for x in all:
            if 'worker' in x:
                if x['worker']:
                    print('test')
                    wn = x['worker_name']
                    cash = 1#x['worker'][wn][1]['pay']
                    await self.add_money(user=x['owner'], count=cash)
                    print('\x1b[1;36;40m' + '[UPDATE]: ' + '\x1b[0m' + 'All Restaurants have been paid.')

    @pay.before_loop
    async def before_pay(self):
        await self.bot.wait_until_ready()

    async def add_money(self, user:int, count):
        data = db.market.find_one({"owner": user})
        bal = data['money']
        money = int(bal) + count
        db.market.update_one({"owner": user}, {"$set":{"money": money}})

def setup(bot):
    bot.add_cog(Tasks(bot))
