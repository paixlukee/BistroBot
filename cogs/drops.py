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
        self.loot.start()

    def cog_unload(self):
        self.loot.cancel()

    @tasks.loop(minutes=1)
    async def loot(self):
        servers = db.utility.find_one("utility": "lootboxes")['guilds']
        ntp = []
        ntp_g = []
        # {"gid": 0, "cid": 0, "opened_last": bool}
        for x in servers:
          if opened_last is True:
              ntp.append(x['cid'])
              ntp_g.append(x['gid'])
          else:
              pass
            
        for x in ntp:
            await bot.get_channel(int(ntp)).send("TEST")
            db.utility.update_one("utility": "lootboxes", "opened_last": False)

    @loot.before_loop
    async def before_loot(self):
        await self.bot.wait_until_ready()

    async def add_money(self, user:int, count):
        data = db.market.find_one({"owner": user})
        bal = data['money']
        money = int(bal) + count
        db.market.update_one({"owner": user}, {"$set":{"money": money}})

def setup(bot):
    bot.add_cog(Tasks(bot))
