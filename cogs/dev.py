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
import re
from pymongo import MongoClient
import pymongo
import string
import food
import config
from .utils import do
import psutil
import food
import items
import extra

client = MongoClient(config.mongo_client)
db = client['siri']

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = 'b.'
        self.process = psutil.Process(os.getpid())
        self.rs = []
        self._last_result = None

    @commands.command(aliases=['tr'])
    @commands.is_owner()
    async def taskreset(self, ctx, me=None):
        if me:
            db.market.update_one({"owner": ctx.author.id}, {"$set": {"tasks": []}})
            db.market.update_one({"owner": ctx.author.id}, {"$set": {"task_list": []}})
            await ctx.send("Your tasks have been reset")
            return
        all = db.market.find()
        await ctx.send("Please wait...")
        count = 0
        for x in all:
            user = x['owner']
            if 'tasks' in x:
                db.market.update_one({"owner": user}, {"$set": {"tasks": []}})
                db.market.update_one({"owner": user}, {"$set": {"task_list": []}})
                count += 1
        await ctx.send(f"Done, tasks reset for `{count}` users.")

    @commands.command(aliases=['Message'])
    @commands.cooldown(1, 21600, commands.BucketType.user) # 6 hrs
    async def message(self, ctx, *, message=None):
        log = self.bot.get_channel(653466873089753098)
        if not message:
            await ctx.send("<:RedTick:653464977788895252> You need to include a message with your support ticket.")
        elif len(message) > 1600:
            await ctx.send("<:RedTick:653464977788895252> Your message can't be longer than 1,600 characters. If you want to write more, join the support server: <http://discord.gg/BCRtw7c>")
        else:
            embed = discord.Embed(colour=0xfcba03, description=f"User `{str(ctx.author)}` has sent you a support ticket.")
            embed.add_field(name=f"Message:", value=message)
            embed.set_footer(text=f'Guild ID: {ctx.guild.id} | User ID: {ctx.author.id}', icon_url=ctx.author.avatar_url_as(format='png'))
            await log.send(embed=embed)
            await ctx.send("Success! Your message has been sent to support. You should expect a message in your DMs when we get the chance! If you are reporting a serious bug, or having anymore questions, join the support server: <http://discord.gg/BCRtw7c>")

    @commands.command(aliases=['Info', 'botinfo', 'status'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def info(self, ctx):

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

        stat = discord.Embed(colour=0x8980d9, description=f"**Bistro** `by paixlukee`\n\n\n"\
        f"\\> **Python**... `3.2`\n"\
        f"\\> **Ubuntu**... `22`\n"\
        f"\\> **RAM Usage**... `{ram:.2f}MB`\n\n"\
        f"I am in **{str(len(self.bot.guilds))} servers**!\n"\
        f"I can view **{channels} channels**!\n"\
        f"I am with **{users} users**!\n"\
        f"I can use **{emojis} emojis**!\n\n"\
        f"[[Invite]](https://discord.com/oauth2/authorize?client_id=657037653346222102&permissions=274878180416&integration_type=0&scope=bot)"\
        f" [[Support]](https://discord.gg/BCRtw7c)")
        stat.set_footer(text="Thanks for using Bistro! | Res-V4")
        await ctx.send(embed=stat)

    @commands.command(aliases=['Prefix', 'setprefix'])
    @commands.cooldown(2, 20, commands.BucketType.user)
    async def prefix(self, ctx, prefix=None):
        cp = "b."
        await ctx.typing()
        current = db.utility.find_one({"utility": "prefixes", "prefixes.guild": ctx.guild.id})
        if ctx.author.guild_permissions.manage_guild:
            if not prefix:
                await ctx.send("<:RedTick:653464977788895252> You need to include a prefix! Example: `{cp}prefix ?`")
            elif len(prefix) > 4:
                await ctx.send("<:RedTick:653464977788895252> Prefix can't be longer than 4 characters!")
            elif current:
                if prefix == 'b.':
                    await ctx.send("<:CheckMark:1330789181470937139> Prefix reset.")
                    db.utility.update_one({"utility": "prefixes", "prefixes.guild": ctx.guild.id}, {"$pull": {"prefixes": {"guild": ctx.guild.id}}})
                else:
                    db.utility.update_one({"utility": "prefixes", "prefixes.guild": ctx.guild.id}, {"$set": {"prefixes.$.prefix": prefix}})
                    await ctx.send(f"<:CheckMark:1330789181470937139> BistroBot Prefix set! To reset it, do `{prefix}prefix {cp}`")
            elif prefix == 'b.':
                await ctx.send(f"<:RedTick:653464977788895252> That is the standard prefix of BistroBot!")
            else:
                db.utility.update_one({"utility": "prefixes"}, {"$push": {"prefixes": {"guild": ctx.guild.id, "prefix": prefix}}})
                await ctx.send(f"<:CheckMark:1330789181470937139> BistroBot Prefix set! To change it back, do `{prefix}prefix {cp}`")
        else:
            await ctx.send("<:RedTick:653464977788895252> You need `manage_server` permissions to change the server prefix!")

    @commands.command(aliases=['ptr'])
    async def patron(self, ctx, user_id:int, tier='BRONZE'):
        if ctx.author.id == 396153668820402197:
            db.utility.update_one({"utility": "patrons"}, {"$push":{tier.lower(): user_id}})
            if tier.lower() == "diamond":
                await self.add_rand_fragment(ctx.author.id, all=True)

            user = await self.bot.fetch_user(user_id)
            await ctx.send(f"<:CheckMark:1330789181470937139> **{str(user)}** is now a patron in the **{tier.upper()}** tier! Hell yeah!")
            embed = discord.Embed(colour=0x8980d9, title="Thanks!", description="Woah! Thank you so so so much for your patronage!\n\nAll of the rewards have been applied to your account. All tiers and information on them are listed [here](https://www.patreon.com/join/paixlukee).")
            try:
                await user.send(embed=embed)
            except:
                pass
        else:
            pass

    @commands.command(aliases=['uptr'])
    async def unpatron(self, ctx, user_id:int, tier='BRONZE'):
        if ctx.author.id == 396153668820402197:
            db.utility.update_one({"utility": "patrons"}, {"$pull":{tier.lower(): user_id}})
            user = await self.bot.fetch_user(user_id)
            await ctx.send(f"**{str(user)}** is no longer a patron in the **{tier.upper()}** tier. :(")
        else:
            pass

    @commands.command(aliases=['ptrs'])
    async def patrons(self, ctx):
        patrons = db.utility.find_one({"utility": "patrons"})
        bronze = []
        silver = []
        gold = []
        diamond = []
        for x in patrons['bronze']:
            user = await ctx.guild.fetch_member(x)
            bronze.append(f"{user.display_name} - {user.id}")
        for x in patrons['silver']:
            user = await ctx.guild.fetch_member(x)
            silver.append(f"{user.display_name} - {user.id}")
        for x in patrons['gold']:
            user = await ctx.guild.fetch_member(x)
            gold.append(f"{user.display_name} - {user.id}")
        for x in patrons['diamond']:
            user = await ctx.guild.fetch_member(x)
            diamond.append(f"{user.display_name} - {user.id}")
        embed = discord.Embed(description="Listed are users patronising:")
        if bronze:
            embed.add_field(name="Bronze", value=", ".join(bronze))
        if silver:
            embed.add_field(name="Silver", value=", ".join(silver))
        if gold:
            embed.add_field(name="Gold", value=", ".join(gold))
        if diamond:
            embed.add_field(name="Diamond", value=", ".join(diamond))
        else:
            pass
        await ctx.send(embed=embed)

    @commands.command(aliases=['debug', 'ev'])
    async def eval(self, ctx, *, code):
        if ctx.author.id == 396153668820402197:
            o_code = code
            code = code.replace('“', '"').replace('”', '"').replace("-silent", "").replace("-s", "").replace("```py", "").replace("```", "")
            try:
                env = {
                    'bot': ctx.bot,
                    'ctx': ctx,
                    'channel': ctx.message.channel,
                    'author': ctx.message.author,
                    'guild': ctx.message.guild,
                    'message': ctx.message,
                    'discord': discord,
                    'random': random,
                    'commands': commands,
                    'requests': requests,
                    'asyncio': asyncio,
                    're': re,
                    'os': os,
                    'pymongo': pymongo,
                    'MongoClient': client,
                    'json': json,
                    'db': db,
                    'rnd': rnd,
                    'food': food,
                    'extra': extra,
                    'items': items,
                    'do':do,
                    'time_rx': re.compile('[0-9]+'),
                    '_': self._last_result
                }

                try:
                    result = eval(code, env)
                except SyntaxError as e:
                    embed=discord.Embed(colour=0xff0000, description=f":inbox_tray: **INPUT**:\n```py\n{code}```\n:outbox_tray: **OUTPUT**:\n```py\n{e}```")
                    embed.set_footer(text="Error")
                    return await ctx.send(embed=embed)
                except Exception as e:
                    embed=discord.Embed(colour=0xff0000, description=f":inbox_tray: **INPUT**:\n```py\n{code}```\n:outbox_tray: **OUTPUT**:\n```py\n{e}```")
                    embed.set_footer(text="Error")
                    return await ctx.send(embed=embed)

                if asyncio.iscoroutine(result):
                    result = await result

                self._last_result = result

                if code == "bot.http.token":
                    embed=discord.Embed(colour=0x8980d9, description=f":inbox_tray: **INPUT**:\n```py\n{code}```\n:outbox_tray: **OUTPUT**:\n```py\n{result}```")
                    return await ctx.send(embed=embed)

                elif o_code.endswith(" -silent") or o_code.endswith(" -s"):
                    pass

                else:
                    if len(str(result)) > 1500:
                        r = requests.post(f"https://hastebin.com/documents", data=str(result).encode('utf-8')).json()
                        return await ctx.send(":weary::ok_hand: The output is too long to send to chat. Here is a hastebin file for ya.. :point_right: https://hastebin.com/" + r['key'])
                    else:
                        try:
                            embed=discord.Embed(colour=0x8980d9, description=f":inbox_tray: **INPUT**:\n```py\n\u200b{code}```\n:outbox_tray: **OUTPUT**:\n```py\n{result}```")
                            return await ctx.send(embed=embed)
                        except Exception as e:
                            embed=discord.Embed(colour=0xff0000, description=f":inbox_tray: **INPUT**:\n```py\n{code}```\n:outbox_tray: **OUTPUT**:\n```py\n{e}```")
                            embed.set_footer(text="Error")
                            return await ctx.send(embed=embed)
            except Exception as e:
                embed=discord.Embed(colour=0xff0000, description=f":inbox_tray: **INPUT**:\n```py\n{code}```\n:outbox_tray: **OUTPUT**:\n```py\n{e}```")
                embed.set_footer(text="Error")
                return await ctx.send(embed=embed)
        else:
            pass
        
    async def add_rand_fragment(self, user, all=False):
        post = db.market.find_one({"owner": user})
        fragments = ['agility', 'opportunity', 'endearing', 'ambience']
        exclude = post['stones']
        if all: 
            for fragment in fragments:
                if fragment in exclude: 
                    continue
                in_list = False
                for frag in post['fragments']:
                    if frag['stone'] == fragment:
                        db.market.update_one({"owner": user, "fragments.stone": fragment},{"$inc": {"fragments.$.count": 1}})
                        in_list = True
                        break
                if not in_list:
                    db.market.update_one({"owner": user}, {"$push": {"fragments": {"stone": fragment, "count": 1}}})
            return True



async def setup(bot):
    await bot.add_cog(Dev(bot))
