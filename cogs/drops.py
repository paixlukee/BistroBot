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

class Drops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loot.start()

    def cog_unload(self):
        self.loot.cancel()

    @tasks.loop(minutes=1)
    async def loot(self):
        lb = db.utility.find_one({"utility": "lootboxes"})
        servers = lb['guilds']
        ntp = []
        ntp_g = []
        for x in servers:
            if opened_last is True:
                ntp.append(x['cid'])
                ntp_g.append(x['gid'])
            else:
                pass
        print(ntp)

        for x in ntp:
            print('test2')
            await bot.get_channel(int(ntp)).send("TEST")
            db.utility.update_one({"utility": "lootboxes", "opened_last": False})

    @loot.before_loop
    async def before_loot(self):
        await self.bot.wait_until_ready()

    async def add_money(self, user:int, count):
        data = db.market.find_one({"owner": user})
        bal = data['money']
        money = int(bal) + count
        db.market.update_one({"owner": user}, {"$set":{"money": money}})

async def setup(bot):
    await bot.add_cog(Drops(bot))
