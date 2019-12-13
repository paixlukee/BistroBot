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
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def user(self, ctx, user:discord.User=None):
        if not user:
            user = ctx.author
        post = db.market.find_one({"owner": int(user.id)})
        if post:
            embed = discord.Embed(colour=0xa82021, description=str(user))
            embed.set_author(icon_url=user.avatar_url_as(format='png'), name="User Stats")
            embed.set_thumbnail(url=user.avatar_url_as(format='png'))
            embed.add_field(name="Restaurant", value=post['name'])
            embed.add_field(name="Money", value="$" + str(post['money']))
            await ctx.send(embed=embed)
        else:
            await ctx.send("This user doesn't have a restaurant")
        
    @commands.command(aliases=['Balance', 'bal'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def balance(self, ctx, user:discord.User=None):
        if not user:
            user = ctx.author
        post = db.market.find_one({"owner": int(user.id)})
        if post:
            bal = format(post['money'], ",d")
            await ctx.send(f"**{user.name}**'s balance is **${bal}**.")
        else:
            await ctx.send("This user doesn't have a restaurant")
                       
    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def donate(self, ctx, user: discord.User=None, count:int=None):
        posts_user = db.market.find_one({"owner": user.id})
        posts = db.market.find_one({"owner": ctx.author.id})                          

        if ctx.author == user:
            await ctx.send("You cannot donate money to yourself!")
                       
        elif not count or not user:
            await ctx.send("You must include both the user and the amount of money. Example: `r!donate @lukee#0420 25`")

        elif count < 0:
            await ctx.send(f"You can't donate under **$1**.")

        elif posts['money'] < count:
            await ctx.send(f"You don't have enough money.")

        elif posts_user is None:
            await ctx.send(f"**{user.name}** doesn't have a restaurant.")

        elif not posts is None:
            await self.add_money(user=user.id, count=count)
            await self.take_money(user=ctx.author.id, count=count)
            await ctx.send(f"{user.mention}, **{ctx.message.author}** has donated **${count}** to you.")
        else:
            await ctx.send("You don't have a restaurant. Create one by doing `r!start`.") 
                       
    @commands.command(pass_context=True, aliases=['Daily'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def daily(self, ctx):
        posts = db.market.find_one({"owner": ctx.author.id})                          
        count = 200   
        if posts:
            await self.add_money(user=ctx.author.id, count=count)
            embed = discord.Embed(colour=0xa82021, description="Want even more money? Vote for me on [Discord Bot List](https://top.gg/bot/648065060559781889), and do `r!votereward` to gain another $150.")
            await ctx.send(embed=embed, content=f"{ctx.author.mention}, you've received your daily **${count}**.")
        else:
            await ctx.send("You don't have a restaurant. Create one by doing `r!start`.") 
            
    @commands.command(pass_context=True, aliases=['Votereward'])
    @commands.cooldown(1, 43200, commands.BucketType.user)
    async def votereward(self, ctx):
        posts = db.market.find_one({"owner": ctx.author.id})                          
        count = 150
        foo = 'bar'
        if posts:
            if foo == 'bar':
                #await self.add_money(user=ctx.author.id, count=count)
                await ctx.send("This does nothing yet.")
            else:
                await ctx.send("You haven't upvoted! Upvote here: <https://top.gg/bot/648065060559781889>")
                self.bot.get_command("votereward").reset_cooldown(ctx)
        else:
            await ctx.send("You don't have a restaurant. Create one by doing `r!start`.") 
                       
    @commands.command(aliases=['Work'])
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def work(self, ctx):
        posts = db.utility.find_one({"utility": "res"})
        user = db.market.find_one({"owner": ctx.author.id})
        if user:
            country = str(user['country'])
            rm = rnd(posts['resp'])['text']
            count = 0
            r1 = rnd(food.food[country])
            r2 = rnd(food.food[country])
            r3 = rnd(food.food[country])
            r4 = rnd(food.food[country])
            if 'happy' in rm or 'refused' in rm:
                msg = str(rm).replace("ITEM", r1['name'])
            elif 'ITEM' in rm and not 'ITEM2' in rm:
                count = r1['price']
                msg = str(rm).replace("ITEM", r1['name']).replace("COUNT", "$" + str(count))
                await self.add_money(user=ctx.author.id, count=count)
                await self.add_sold(user=ctx.author.id, sold=r1['name'])
            elif 'ITEM2' in rm and not 'ITEM4' in rm:
                count = r1['price']+r2['price']+r3['price']
                msg = str(rm).replace("ITEM3", r3['name']).replace("ITEM2", r2['name']).replace("ITEM", r1['name']).replace("COUNT", "$" + str(count))
                await self.add_money(user=ctx.author.id, count=count)
                await self.add_sold(user=ctx.author.id, sold=r1['name'])
                await self.add_sold(user=ctx.author.id, sold=r2['name'])
                await self.add_sold(user=ctx.author.id, sold=r3['name'])
            else:
                count = r1['price']+r2['price']+r3['price']+r4['price']
                msg = str(rm).replace("ITEM4", r4['name']).replace("ITEM3", r3['name']).replace("ITEM2", r2['name']).replace("ITEM", r1['name']).replace("COUNT", "$" + str(count))
                await self.add_money(user=ctx.author.id, count=count)
                await self.add_sold(user=ctx.author.id, sold=r1['name'])
                await self.add_sold(user=ctx.author.id, sold=r2['name'])
                await self.add_sold(user=ctx.author.id, sold=r3['name'])
                await self.add_sold(user=ctx.author.id, sold=r4['name'])
            if 'TIP' in rm and not 'TIP2' in rm:
                tpc = random.randint(2,4)
                msg = msg.replace("TIP", str(tpc))
                await self.add_money(user=ctx.author.id, count=tpc)
            else:
                tpc = random.randint(8,10)
                msg = msg.replace("TIP", "$" + str(tpc))
                await self.add_money(user=ctx.author.id, count=tpc)

            await ctx.send(f"{ctx.author.mention}, {msg}")
        else:
            await ctx.send("You don't have a restaurant. Create one with `r!start`.")
                   

    async def add_money(self, user:int, count):
        data = db.market.find_one({"owner": user})
        bal = data['money']
        money = int(bal) + count
        db.market.update_one({"owner": user}, {"$set":{"money": money}})

    async def take_money(self, user:int, count:int):
        data = db.market.find_one({"owner": user})
        bal = data['money']
        money = int(bal) - count
        db.market.update_one({"owner": user}, {"$set":{"money": money}})
        
    async def add_sold(self, user, sold):
        item = sold
        data = db.market.find_one({"owner": user})
        it = None
        for x in data['items']:
            if x['name'] == item:
                it = x
        bal = it['sold']
        tc = int(bal) + 1
        db.market.update_one({"owner": user}, {"$pull":{"items": {"name": item, "price": it['price'], "stock": it['stock'], "sold": bal}}})
        db.market.update_one({"owner": user}, {"$push":{"items": {"name": item, "price": it['price'], "stock": it['stock'], "sold": tc}}})
                    

def setup(bot):
    bot.add_cog(Shop(bot))
