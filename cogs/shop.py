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
        self.countries = ['CHINA', 'FRANCE','GREECE', 'INDIA', 'ITALY', 'JAPAN', 'MEXICO', 'UNITED KINGDOM', 'UNITED STATES']
        self.flags = {"china":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_China.png", "france":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_France.png", 
                     "greece":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Greece.png", "india":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_India.png",
                     "italy": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Italy.png", "japan": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Japan.png",
                     "mexico":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Mexico.png", "united kingdom":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_United_Kingdom.png",
                     "united states": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_United_States.png"}
        
    @commands.command(aliases=['Restaurant', 'shop'])
    async def restaurant(self, ctx, user:discord.User=None):
        if not user:
            user = ctx.author
        post = db.market.find_one({"owner": ctx.author.id})
        if not post:
            await ctx.send(f'I couldn\'t find "{user}"s restaurant in our database.') 
        else:
            country = str(post['country']).lower()
            ldi = post['items']
            list = sorted(ldi, key=lambda x: x['sold'], reverse=True)
            embed = discord.Embed(colour=0x280071, description=post['description'])
            embed.set_author(icon_url=self.flags[country], name=post['name'])
            embed.add_field(name="Menu", value=post['items'][0]['name'] + ", " + post['items'][1]['name'] + ", " + post['items'][2]['name'] + f"... To view the full menu, do `r!menu {post['name']}`")
            embed.add_field(name="Most Sold item", value=list[0]['name'])
            embed.add_field(name="Customers", value=post['customers'])
            embed.set_thumbnail(url=post['logo_url'])
            embed.set_footer(text=f"Last Stock: {post['laststock']}")
            await ctx.send(embed=embed)
        

    @commands.command(aliases=['Start', 'create'])
    async def start(self, ctx):
        user = db.market.find_one({"owner": ctx.author.id})
        if not user:
            def check(m):
                return m.author == ctx.message.author
            embed = discord.Embed(colour=0x280071, description='Welcome to Restaurant! First off, which country do you want your theme as? Pick one from this list:\n'\
            ':flag_cn: China\n'\
            ':flag_fr: France\n'\
            ':flag_gr: Greece\n'\
            ':flag_in: India\n'\
            ':flag_it: Italy\n'\
            ':flag_jp: Japan\n'\
            ':flag_mx: Mexico\n'\
            ':flag_gb: United Kingdom\n'\
            ':flag_us: United States\n'
            )
            embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Creation")
            embed.set_footer(text="You have 90 seconds to reply")
            msg1 = await ctx.send(embed=embed)
            country = await self.bot.wait_for('message', check=check, timeout=90)
            try:
                await country.delete()
            except:
                pass
            if not country.content.upper() in self.countries:
                failed = discord.Embed(colour=0x280071, description="That is not in the list of countries.")
                failed.set_author(name="Creation Failed.")
                await msg1.edit(embed=failed)
            else:
                embed = discord.Embed(colour=0x280071, description='Great! What would you like to name your restaurant? It must be 36 characters or less.')
                embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Creation")
                embed.set_footer(text="You have 90 seconds to reply")
                await msg1.edit(embed=embed)
                name = await self.bot.wait_for('message', check=check, timeout=90)
                try:
                    await name.delete()
                except:
                    pass
                if len(str(name.content)) > 36:
                    failed = discord.Embed(colour=0x280071, description="Restaurant name must be 36 characters or less")
                    failed.set_author(name="Creation Failed.")
                    msg1.edit(embed=failed)
                else:
                    embed = discord.Embed(colour=0x280071, description='Great! What would you like ask your description? It must be 130 characters or less.')
                    embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Creation")
                    embed.set_footer(text="You have 90 seconds to reply")
                    await msg1.edit(embed=embed)
                    desc = await self.bot.wait_for('message', check=check, timeout=90)
                    try:
                        await desc.delete()
                    except:
                        pass
                    if len(str(desc.content)) > 130:
                        failed = discord.Embed(colour=0x280071, description="Restaurant description must be 130 characters or less")
                        failed.set_author(name="Creation Failed.")
                        await msg1.edit(embed=failed)
                    else:
                        await self.update_data(ctx.author, country.content.lower(), name.content, desc.content)
                        embed = discord.Embed(colour=0x280071, description=f'And... Done! Your Restaurant has been created. \n\nYou have been given 30 of each item and $500. View your restaurant with `{self.prefix}restaurant`')
                        embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Creation")
                        await msg1.edit(embed=embed)
        else:
            await ctx.send(f'You already have a restaurant created. View it with {self.prefix}restaurant')


    async def update_data(self, user, country, name, desc):
        set1 = random.randint(0,9)
        set2 = rnd(string.ascii_letters) 
        set3 = rnd(string.ascii_letters) 
        set4 = random.randint(0,9)
        set5 = rnd(string.ascii_letters) 
        print(food.food[0])
                             
        id = str(set1) + set2 + set3 + str(set4) + set5        
        post = {
            "owner": user.id,
            "money":300,
            "items":"",
            "country":country,
            "name":name,
            "description":desc,
            "customers":0,
            "boost":None,
            "laststock": "Has not stocked yet.",
            "id":id,
            "logo_url":None
        }
        db.market.insert_one(post)

def setup(bot):
    bot.add_cog(Shop(bot))
