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
import items
from threading import Thread
import extra
import workers
import schedule

client = MongoClient(config.mongo_client)
db = client['siri']

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = 'r!'
        self.countries = ['CHINA', 'FRANCE','GREECE', 'INDIA', 'ITALY', 'JAPAN', 'MEXICO', 'TURKEY','UNITED KINGDOM', 'UNITED STATES']
        self.flags = {"china":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_China.png", "france":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_France.png",
                     "greece":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Greece.png", "india":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_India.png",
                     "italy": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Italy.png", "japan": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Japan.png",
                     "mexico":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Mexico.png", "turkey": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Turkey.png","united kingdom":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_United_Kingdom.png",
                     "united states": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_United_States.png"}



    @commands.command(aliases=['Leaderboard', 'lb'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def leaderboard(self, ctx, page=1):
        await ctx.trigger_typing()
        start = (page - 1) * 8
        end = start + 8
        embed = discord.Embed(colour=0xa82021, description="Global Restaurant Leaderboard")
        find_c = db.market.find().sort("exp", -1)
        for x in find_c[start:end]:
            exp = format(x['exp'], ",d")
            embed.add_field(name=x['name'], value=f":bar_chart: {exp}", inline=False)
        embed.set_footer(text=f"Sort by: experience | r!lb {page+1} for next page")
        await ctx.send(embed=embed)

    @commands.command(aliases=['Delete'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def delete(self, ctx):
        def ans(m):
            return m.author == ctx.message.author
        post = db.market.find({"owner": ctx.author.id})
        if post:
            msg = await ctx.send("Are you sure you want to delete your restaurant? Deleting will erase all of your hardwork. If you're sure, reply with \"I'm sure\".")
            try:
                a = await self.bot.wait_for('message', check=ans, timeout=20)
            except asyncio.TimeoutError:
                await ctx.send('You took too long to answer. Deletion canceled.')
            else:
                if a.content.lower() == "i'm sure":
                    await ctx.send("Account deleted. Thanks for using Restaurant.")
                    db.market.delete_one({"owner": ctx.author.id})
                else:
                    await ctx.send('Deletion canceled.')
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `r!start`.")

    @commands.command(aliases=['Worker'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def worker(self, ctx):
        post = db.market.find_one({"owner": ctx.author.id})
        if 'worker' in post:
            if not post['worker']:
                await ctx.send("<:RedTick:653464977788895252> You didn't hire a co-worker! Do `r!hire` to hire one!")
            else:
                ratings = []
                for rating in post['ratings']:
                    ratings.append(rating['rating'])
                avr = round(sum(ratings)/len(ratings))
                if avr <= 2:
                    wr = ["Working at {} is really hard...", "The food here at {} isn't the greatest...", "I hate working at {}! It's disgusting here!", "I want to work somewhere else..."]
                else:
                    wr = ["I love working at {}! The food is delicious here!", "{} is such a great place to work at, I absolutely love it!", "The working environment here at {} is so positive!", "I love working here!"]
                comment = random.choice(wr).format(post['name'])
                worker_name = post['worker_name']
                desc = f"**Co-Worker:** {worker_name}\n\n"\
                       f"**EXP Bonus:** {round(post['worker'][worker_name][0]['exp']*100)}%\n"\
                       f"**Tips Bonus:** {round(post['worker'][worker_name][1]['tips']*100)}%\n"\
                       f"**Earns You:** ${round(post['worker'][worker_name][2]['pay'])}/day\n"\
                       f"\n**\"**{comment}**\"**"
                embed = discord.Embed(colour=0xa82021, description=desc)
                await ctx.send(embed=embed)
        else:
            await ctx.send("<:RedTick:653464977788895252> You didn't hire a co-worker! Do `r!hire` to get one!")

    @commands.command(aliases=['Hire'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hire(self, ctx):
        def a(m):
            return m.author == ctx.message.author
        post = db.market.find_one({"owner": ctx.author.id})
        c = str(post['country'])
        available = workers.list[c]
        wrks = [[key for key in available[0]][0], [key for key in available[1]][0], [key for key in available[2]][0], [key for key in available[3]][0]]
        wd = f"`{[key for key in available[0]][0]}` **-5% EXP** | **+40% Tips** | **Earns $5/day**\n"\
             f"`{[key for key in available[1]][0]}` **+12% EXP** | **+24% Tips** | **Earns $6/day**\n"\
             f"`{[key for key in available[2]][0]}` **+5% EXP** | **-20% Tips** | **Earns $12/day**\n"\
             f"`{[key for key in available[3]][0]}` **+30% EXP** | **+20% Tips** | **Earns $2/day**"
        embed = discord.Embed(description=f"Which worker would you like to hire? You can only have one at a time.\n\nEach employee costs $500 upfront and an additional $50 taken away from the daily command.\n\n{wd}")
        embed.set_footer(text="You have 60 seconds to reply.")
        await ctx.send(embed=embed)
        msg = await self.bot.wait_for('message', check=a, timeout=20)
        chosen = msg.content.capitalize()
        if not msg.content in wrks:
            await ctx.send(f"<:RedTick:653464977788895252> Error! That's not in the list of workers! Example: `{[key for key in available[1]][0]}`")
        else:
            chw = None
            for x in available:
                if chosen in x:
                    chw = x
            if not post['money'] >= 500:
                await ctx.send("<:RedTick:653464977788895252> You don't have enough money.")
            else:
                if not 'worker' in post:
                    db.market.update_one({"owner": ctx.author.id}, {"$set": {"worker": None}})
                    db.market.update_one({"owner": ctx.author.id}, {"$set": {"worker_name": None}})
                else:
                    pass
                await self.take_money(user=ctx.author.id, count=500)
                db.market.update_one({"owner": ctx.author.id}, {"$set": {"worker": chw}})
                db.market.update_one({"owner": ctx.author.id}, {"$set": {"worker_name": chosen}})
                me = discord.Embed(colour=0xa82021, description=f"Hello, {ctx.author.name.capitalize()}!\n\nThanks for hiring me! I hope that I can help make your restaurant the best in the world! If you ever want to check on me, do `r!worker`.")
                me.set_author(name=f"Message from {chosen}", icon_url="http://paixlukee.ml/m/SKRFY.png")
                await ctx.send(embed=me)




    @commands.command(aliases=['restaurantfuse'])
    async def fuse(self, ctx):
        embed = discord.Embed(colour=0xa82021)
        embed.set_author(name="Restaurant Fusing", icon_url=ctx.me.avatar_url_as(format='png'))
        embed.set_image(url="https://i.ibb.co/yNMrNnq/restaurantfuse.png")
        embed.description = "Want to have two food types in one restaurant?\n"\
                            "Fusing your restaurant will mix foods from two different countries.\n\n"\
                            "To fuse your restaurant, you need to have **2,000 or more experience**. It costs **$1,000** to fuse.\n\n"\
                            "Do `r!rfuse` to fuse your restaurant."
        await ctx.send(embed=embed)

    @commands.command()
    async def rfuse(self, ctx):
        def nc(m):
            return m.author == ctx.message.author
        post = db.market.find_one({"owner": ctx.author.id})
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `r!restaurant`.")
        elif post['exp'] <= 2000:
            await ctx.send("<:RedTick:653464977788895252> You don't have enough experience to fuse!")
        elif post['money'] <= 1000:
            await ctx.send("<:RedTick:653464977788895252> You don't have enough money to fuse!")
        else:
            embed = discord.Embed(colour=0xa82021, description="What country would you like to fuse with?")
            embed.set_footer(text="You have 90 seconds to answer.")
            embed.set_author(name="Restaurant Fusing", icon_url=ctx.me.avatar_url_as(format='png'))
            choice = await self.bot.wait_for('message', check=nc, timeout=90)
            if not choice.content.upper() in self.countries:
                embed = discord.Embed(colour=0xa82021, title="Fusing failed.", description="That is not a vaild country.")
            else:
                pass


    @commands.command(aliases=['Menu'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def menu(self, ctx, *, restaurant=None):
        def nc(m):
            return m.author == ctx.message.author
        if ctx.message.mentions:
            if len(ctx.message.mentions) >= 2:
                restaurant = db.market.find_one({"owner":ctx.message.mentions[1].id})['name']
            else:
                restaurant = db.market.find_one({"owner":ctx.message.mentions[0].id})['name']
        if not restaurant:
            await ctx.send("<:RedTick:653464977788895252> You must include the restaurant name. Example: `r!menu McDonalds`")
        else:
            post = db.market.find({"name": restaurant})
            if post.count() > 1:
                embed = discord.Embed(colour=0xa82021, title="Multiple results found.")
                cn = 0
                desc = ""
                n = []
                for x in post:
                    cn += 1
                    n.append({str(cn):x})
                    own = self.bot.get_user(x['owner'])
                    desc += f"[{cn}] {x['name']} | {own}\n"
                embed.description = desc
                embed.set_footer(text="You have 90 seconds to reply with the number.")
                await ctx.send(embed=embed)
                choice = await self.bot.wait_for('message', check=nc, timeout=90)
                if not choice.content.isdigit() or len(choice.content) > cn or len(choice.content) < 1:
                    embed = discord.Embed(colour=0xa82021, title="Failed", description="Invalid number.")
                    await ctx.send(embed=embed)
                else:
                    pn = int(choice.content)
                    embed = discord.Embed()
                    country = n[pn-1][str(pn)]['country']
                    embed.set_author(icon_url=self.flags[country], name=f"{n[pn-1][str(pn)]['name']}'s Menu")
                    desc = ""
                    for x in n[pn-1][str(pn)]['items']:
                        desc += f"{x['name']} | ${x['price']} | {x['sold']} Sold\n"
                    embed.description = desc
                    await ctx.send(embed=embed)
            elif post.count() == 1:
                post = db.market.find_one({"name": restaurant})
                embed = discord.Embed()
                country = str(post['country'])
                embed.set_author(icon_url=self.flags[country], name=f"{post['name']}'s Menu")
                desc = ""
                for x in post['items']:
                    desc += f"{x['name']} | ${x['price']} | {x['sold']} Sold\n"#| {x['stock']} in Stock
                embed.description = desc
                await ctx.send(embed=embed)
            else:
                await ctx.send("<:RedTick:653464977788895252> I couldn't find that restaurant in our database. Did you spell it right? Names are case sensitive.")


    @commands.command(aliases=['Rate'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def rate(self, ctx, user:discord.User=None):
        post = db.market.find_one({"owner": user.id})
        def nc(m):
            return m.author == ctx.message.author
        if not user:
            await ctx.send("<:RedTick:653464977788895252> You must tag the restaurant owner. Example: `r!rate @lukee#0420`")
        elif user == ctx.author:
            await ctx.send("<:RedTick:653464977788895252> You cannot rate your own restaurant.")
        else:
            posts = db.market.find_one({"owner": user.id})
            rus = []
            for x in posts['ratings']:
                rus.append(x['user'])
            if str(ctx.author.id) in rus:
                await ctx.send("<:RedTick:653464977788895252> You already rated this restaurant.")
            else:
                embed = discord.Embed(colour=0xa82021, description=f"Out of 5 stars, how would you rate {post['name']}?")
                embed.set_footer(text="You have 90 seconds to reply")
                msg = await ctx.send(embed=embed)
                rating = await self.bot.wait_for('message', check=nc, timeout=90)
                try:
                    await rating.delete()
                except:
                    pass
                if not rating.content.isdigit() or int(rating.content) > 5 or int(rating.content) < 0:
                    embed = discord.Embed(colour=0xa82021, description="The rating must be from 0-5.")
                    embed.set_author(name="Failed.")
                    await msg.edit(embed=embed)
                else:
                    embed = discord.Embed(colour=0xa82021, description=f"You have successfully rated {post['name']}.")
                    await msg.edit(embed=embed)
                    db.market.update_one({"owner": user.id}, {"$push":{"ratings": {"rating": int(rating.content), "user":str(ctx.author.id)}}})


    @commands.group(aliases=['Buy'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def buy(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(colour=0xa82021, title="'Buy' Command Group", description="`r!buy custom` - **Buy a restaurant customisation chest**\n`r!buy food` - **Buy a menu item and have it added to your menu**\n`r!buy item` - **Buy an item from the store**")
            await ctx.send(embed=embed)

    @buy.command(aliases=['Boost'])
    async def boost(self, ctx):
        x = 'x'
        #def nc(m):
            #return m.author == ctx.message.author
        #post = db.market.find_one({"owner": ctx.author.id})
        if x == 'y':
            embed = discord.Embed(colour=0xa82021, title="Which chest would you like to buy?", description="[1] Double EXP - 24 Hours - $900 <:EarningsBoost:651474110022418433>\n[2] Profile Banner Chest - $1,000 <:EarningsBoost2:651474232219271210>")
            embed.set_footer(text="You have 90 seconds to reply with the number")
            await ctx.send(embed=embed)
            choice = await self.bot.wait_for('message', check=nc, timeout=90)
            if int(choice.content) == 1:
                if post['money'] < 200:
                    await ctx.send("You don't have enough money for this.")
                else:
                    rn = random.randint(1,3)
                    if not rn == 1:
                        chosen = rnd(items.colours['common'])
                        db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"colour": chosen}}})
                        embed = discord.Embed(colour=0xa82021, description=f"{chosen['colour']} (Common)")
                        embed.set_thumbnail(url="http://pixelartmaker.com/art/5dd01d7e459201b.png")
                        embed.set_footer(text=f"Do r!inventory to check your inventory, or r!use {chosen['colour']} to use it.")
                        await ctx.send(embed=embed, content='you opened a Profile Colour Chest and received...')
                    else:
                        chosen = rnd(items.colours['uncommon'])
                        db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"colour": chosen}}})
                        embed = discord.Embed(colour=0xa82021, description=f"{chosen['colour']} (Uncommon)")
                        embed.set_thumbnail(url="http://pixelartmaker.com/art/5dd01d7e459201b.png")
                        embed.set_footer(text=f"Do r!inventory to check your inventory, or r!use {chosen['colour']} to use it.")
                        await ctx.send(embed=embed, content='you opened a Profile Colour Chest and received...')
            elif int(choice.content) == 2:
                if post['money'] < 200:
                    await ctx.send("You don't have enough money for this.")
                else:
                    rn = random.randint(1,3)
                    if not rn == 1:
                        chosen = rnd(items.banners['common'])
                        db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"banner": chosen}}})
                        embed = discord.Embed(colour=0xa82021, description=f"{chosen['name']} (Common) [View banner]({chosen['url']})")
                        embed.set_thumbnail(url="http://pixelartmaker.com/art/34fc7859370d585.png")
                        embed.set_footer(text=f"Do r!inventory to check your inventory, or r!use {chosen['name']} to use it.")
                        await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Banner Chest and received...')
                    else:
                        chosen = rnd(items.banners['uncommon'])
                        db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"banner": chosen}}})
                        embed = discord.Embed(colour=0xa82021, description=f"{chosen['name']} (Uncommon) [View banner]({chosen['url']})")
                        embed.set_thumbnail(url="http://pixelartmaker.com/art/34fc7859370d585.png")
                        embed.set_footer(text=f"Do r!inventory to check your inventory, or r!use {chosen['name']} to use it.")
                        await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Banner Chest and received...')
            else:
                await ctx.send("That is not an option.")

        else:
            await ctx.send("Boosts are still in the works! Suggest what you want to see here: <https://discord.gg/BCRtw7c>")

    @buy.command(aliases=['Item'])
    async def item(self, ctx):
        post = db.market.find_one({"owner": ctx.author.id})
        def nc(m):
            return m.author == ctx.message.author
        embed = discord.Embed(colour=0xa82021, title="Which item would you like to buy?", description="[1] Fishing Rod - $60 :fishing_pole_and_fish:\n[2] Experience Potion (+50 EXP) - $80 <:ExperiencePotion:715822985780658238>")
        embed.set_footer(text="You have 90 seconds to reply with the number, or say 'cancel' to cancel.")
        await ctx.send(embed=embed)
        choice = await self.bot.wait_for('message', check=nc, timeout=90)
        if choice.content == '1':
            if post['money'] < 60:
                await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this.")
            else:
                await ctx.send(f"{ctx.author.mention}, You bought 1 Fishing Rod. Do `r!fish` to use it.")
                await self.take_money(user=ctx.author.id, count=60)
                db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "fish"}}})
        elif choice.content == '2':
            if post['money'] < 80:
                await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this.")
            else:
                await ctx.send(f"{ctx.author.mention}, You bought 1 Experience Potion. Do `r!use Experience Potion` to use it.")
                db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "ep"}}})
                await self.take_money(user=ctx.author.id, count=80)
        elif choice.content.lower() == 'cancel':
            await ctx.send("Cancelled.")
        else:
            pass

    @buy.command(aliases=['Custom'])
    async def custom(self, ctx):
        def nc(m):
            return m.author == ctx.message.author
        post = db.market.find_one({"owner": ctx.author.id})
        if not 'colour' in post:
            db.market.update_one({"owner": ctx.author.id}, {"$set":{"colour": None}})
            db.market.update_one({"owner": ctx.author.id}, {"$set":{"banner": None}})
        else:
            pass
        embed = discord.Embed(colour=0xa82021, title="Which chest would you like to buy?", description="[1] Restaurant Colour Chest - $200 <:CustomChest1:655981726077550615>\n[2] Restaurant Banner Chest - $400 <:CustomChest2:655981738148888598>")
        embed.set_footer(text="You have 90 seconds to reply with the number")
        await ctx.send(embed=embed)
        choice = await self.bot.wait_for('message', check=nc, timeout=90)
        if int(choice.content) == 1:
            if post['money'] < 200:
                await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this.")
            else:
                await self.take_money(ctx.author.id, 200)
                rn = random.randint(1,3)
                if not rn == 1:
                    chosen = rnd(items.colours['common'])
                    chosen['rarity'] = "Common"
                    db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"colour": chosen}}})
                    embed = discord.Embed(colour=0xa82021, description=f"{chosen['colour']} (Common)")
                    embed.set_thumbnail(url="http://pixelartmaker.com/art/5dd01d7e459201b.png")
                    embed.set_footer(text=f"Do r!inventory to check your inventory, or r!use {chosen['colour']} to use it.")
                    await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Colour Chest and received...')
                else:
                    chosen = rnd(items.colours['uncommon'])
                    chosen['rarity'] = "Uncommon"
                    db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"colour": chosen}}})
                    embed = discord.Embed(colour=0xa82021, description=f"{chosen['colour']} (Uncommon)")
                    embed.set_thumbnail(url="http://pixelartmaker.com/art/5dd01d7e459201b.png")
                    embed.set_footer(text=f"Do r!inventory to check your inventory, or r!use {chosen['colour']} to use it.")
                    await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Colour Chest and received...')
        elif int(choice.content) == 2:
                if post['money'] < 400:
                    await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this.")
                else:
                    await self.take_money(ctx.author.id, 400)
                    banners_had = []
                    for x in post['inventory']:
                        if 'banner' in x:
                            banners_had.append(x['banner']['name'])
                        else:
                            pass
                    rn = ['common', 'common', 'common', 'common', 'common', 'common', 'uncommon', 'uncommon', 'uncommon', 'rare']
                    cr = rnd(rn)
                    if cr == 'common':
                        chosen = rnd(items.banners['common'])
                        chosen['rarity'] = "Common"
                        if chosen['name'] in banners_had:
                            embed = discord.Embed(colour=0xa82021, description=f"~~{chosen['name']} ({chosen['rarity']})~~\n\n**Duplicate!** You got $200 because this banner is already in your inventory.")
                            embed.set_thumbnail(url="http://pixelartmaker.com/art/34fc7859370d585.png")
                            await self.add_money(user=ctx.author.id, count=200)
                            await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Banner Chest and received...')
                        else:
                            db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"banner": chosen}}})
                            embed = discord.Embed(colour=0xa82021, description=f"{chosen['name']} (Common) [View banner]({chosen['url']})")
                            embed.set_thumbnail(url="http://pixelartmaker.com/art/34fc7859370d585.png")
                            embed.set_footer(text=f"Do r!inventory to check your inventory, or r!use {chosen['name']} to use it.")
                            await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Banner Chest and received...')
                    elif cr == 'uncommon':
                        chosen = rnd(items.banners['uncommon'])
                        chosen['rarity'] = "Common"
                        if chosen['name'] in banners_had:
                            embed = discord.Embed(colour=0xa82021, description=f"~~{chosen['name']} ({chosen['rarity']})~~\n\n**Duplicate!** You got $200 because this banner is already in your inventory.")
                            embed.set_thumbnail(url="http://pixelartmaker.com/art/34fc7859370d585.png")
                            await self.add_money(user=ctx.author.id, count=200)
                            await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Banner Chest and received...')
                        else:
                            db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"banner": chosen}}})
                            embed = discord.Embed(colour=0xa82021, description=f"{chosen['name']} (Uncommon) [View banner]({chosen['url']})")
                            embed.set_thumbnail(url="http://pixelartmaker.com/art/34fc7859370d585.png")
                            embed.set_footer(text=f"Do r!inventory to check your inventory, or r!use {chosen['name']} to use it.")
                            await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Banner Chest and received...')
                    elif cr == 'rare':
                        chosen = rnd(items.banners['rare'])
                        chosen['rarity'] = "Rare"
                        if chosen['name'] in banners_had:
                            embed = discord.Embed(colour=0xa82021, description=f"~~{chosen['name']} ({chosen['rarity']})~~\n\n**Duplicate!** You got $200 because this banner is already in your inventory.")
                            embed.set_thumbnail(url="http://pixelartmaker.com/art/34fc7859370d585.png")
                            await self.add_money(user=ctx.author.id, count=200)
                            await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Banner Chest and received...')
                        else:
                            db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"banner": chosen}}})
                            embed = discord.Embed(colour=0xa82021, description=f"{chosen['name']} (Rare) [View banner]({chosen['url']})")
                            embed.set_thumbnail(url="http://pixelartmaker.com/art/34fc7859370d585.png")
                            embed.set_footer(text=f"Do r!inventory to check your inventory, or r!use {chosen['name']} to use it.")
                            await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Banner Chest and received...')
                    else:
                        pass

        else:
            await ctx.send("<:RedTick:653464977788895252> That is not an option.")

    @buy.command(aliases=['Food'])
    async def food(self, ctx):
        def nc(m):
            return m.author == ctx.message.author
        post = db.market.find_one({"owner": ctx.author.id})
        embed = discord.Embed(colour=0xa82021, title="Which food item would you like to add to your menu?")
        embed.set_footer(text="You have 90 seconds to reply with the number")
        cn = 0
        desc = ""
        n = []
        items = []
        country = post['country']
        for x in post['items']:
            items.append(x['name'])
        for x in extra.extra[country]:
            if x['name'] in items:
                pass
            else:
                cn += 1
                n.append({str(cn):x})
                sp = x['price']
                desc += f"[{cn}] {x['name']} | Selling Price: {sp}\n"
        embed.description = f"All menu items cost $600\n{desc}. You must go in order."
        await ctx.send(embed=embed)
        choice = await self.bot.wait_for('message', check=nc, timeout=90)
        ch = choice.content.replace("[", "").replace("]", "").replace("r!", "")
        if post['money'] > 600:
            if ch in n[0]:
                name = n[0][ch]['name']
                await ctx.send(f'{ctx.author.mention}, Item {name} was added to your menu.')
                await self.take_money(ctx.author.id, 600)
                db.market.update_one({"owner": ctx.author.id}, {"$push": {"items":n[0][ch]}})
            else:
                await ctx.send("<:RedTick:653464977788895252> That is not an option.")
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this.")


    @commands.group(aliases=['settings', 'Set', 'Settings'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def set(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(colour=0xa82021, title="'Set' Command Group", description="`r!set logo` - **Set Restaurant logo**\n`r!set notifications` - **Set notifications for your Restaurant**\n`r!set description` - **Set Restaurant description**\n`r!set name` - **Set Restaurant name**\n`r!set price` - **Set the price of an item**")
            await ctx.send(embed=embed)
            self.bot.get_command("set").reset_cooldown(ctx)

    @set.command(aliases=['Notifications', 'notifs'])
    async def notifications(self, ctx):
        post = db.market.find_one({"owner": ctx.author.id})
        if not 'notifications' in post:
            db.market.update_one({"owner": ctx.author.id}, {"$set": {"notifications": True}})
            await ctx.send("Notifications turned on.")
        else:
            if post['notifications'] == False:
                db.market.update_one({"owner": ctx.author.id}, {"$set": {"notifications": True}})
                await ctx.send("Notifications turned on.")
            elif post['notifications'] == True:
                db.market.update_one({"owner": ctx.author.id}, {"$set": {"notifications": False}})
                await ctx.send("Notifications turned off.")
            else:
                pass


    @set.command(aliases=['Logo', 'image', 'icon'])
    async def logo(self, ctx):
        post = db.market.find_one({"owner": ctx.author.id})
        def react(reaction, user):
            return user != ctx.me and str(reaction.emoji) == '✅' or str(reaction.emoji) == '❎'
        def nc(m):
            return m.author == ctx.message.author
        embed = discord.Embed(colour=0xa82021, description="To keep NSFW off of Restaurant Bot, staff members must review every logo.\n\nReply with the image URL for your logo.")
        embed.set_footer(text="You have 90 seconds to reply")
        msg = await ctx.send(embed=embed)
        link = await self.bot.wait_for('message', check=nc, timeout=90)
        try:
            await link.delete()
        except:
            pass
        if link.content.startswith('http') and link.content.endswith('.jpg') or link.content.startswith('http') and link.content.endswith('.png') or link.content.startswith('http') and link.content.endswith('.jpeg') or link.content.startswith('http') and link.content.endswith('.gif'):
            embed = discord.Embed(colour=0xa82021, description="Perfect! Your image has been sent to the Restaurant Bot staff team for reviewal.\n\n This process may take up to 24 hours. But don't worry, it will probably be even quicker.")
            embed.set_footer(text="Too many NSFW requests can end up in a ban from Restaurant Bot!")
            await msg.edit(embed=embed)

            se = discord.Embed(description=link.content)
            se2 = discord.Embed()
            se.set_footer(icon_url=ctx.author.avatar_url_as(format='png'), text=f"{ctx.author} | {ctx.author.id}")
            se.set_thumbnail(url=link.content)
            se2.set_footer(icon_url=ctx.author.avatar_url_as(format='png'), text=f"{ctx.author} | {ctx.author.id}")
            se2.set_thumbnail(url=link.content)
            sem = await self.bot.get_channel(650994466307571714).send(embed=se)
            await sem.add_reaction('✅')
            await sem.add_reaction('❎')
            await asyncio.sleep(2)
            reaction, user = await self.bot.wait_for('reaction_add', check=react)
            if reaction.emoji == '✅':
                se2.description = '*Logo accepted*'
                await sem.edit(embed=se2)
                await ctx.author.send("Your logo has been accepted!")
                db.market.update_one({"owner": ctx.author.id}, {"$set":{"logo_url": link.content}})
            else:
                se2.description = '*Logo denied*'
                await sem.edit(embed=se2)
                await ctx.author.send("Your logo has been denied.")
        else:
            embed = discord.Embed(colour=0xa82021, description="That is not a valid link. It must end with `.png`, `.jpg`, `.jpeg`, or `.gif`.")
            embed.set_author(name="Failed.")
            await msg.edit(embed=embed)

    @set.command(aliases=['Description', 'desc'])
    async def description(self, ctx):
        def nc(m):
            return m.author == ctx.message.author
        embed = discord.Embed(colour=0xa82021, description="Descriptions must me 130 characters or less.\n\nReply with your desired description.")
        embed.set_footer(text="You have 90 seconds to reply")
        msg = await ctx.send(embed=embed)
        desc = await self.bot.wait_for('message', check=nc, timeout=90)
        try:
            await desc.delete()
        except:
            pass
        if len(desc.content) > 130:
            embed = discord.Embed(colour=0xa82021, description="Description is more than 130 characters.")
            embed.set_author(name="Failed.")
            await msg.edit(embed=embed)
        else:
            embed = discord.Embed(colour=0xa82021, description="Great! Your restaurant's description has been set!")
            await msg.edit(embed=embed)
            db.market.update_one({"owner": ctx.author.id}, {"$set":{"description": desc.content}})

    @set.command(aliases=['Name'])
    async def name(self, ctx):
        def nc(m):
            return m.author == ctx.message.author
        post = db.market.find_one({"owner": int(ctx.author.id)})
        if post:
            embed = discord.Embed(colour=0xa82021, description="Names must me 36 characters or less.\n\nReply with your desired name.")
            embed.set_footer(text="You have 90 seconds to reply")
            msg = await ctx.send(embed=embed)
            name = await self.bot.wait_for('message', check=nc, timeout=90)
            try:
                await name.delete()
            except:
                pass
            if len(name.content) > 130:
                embed = discord.Embed(colour=0xa82021, description="Name is more than 36 characters.")
                embed.set_author(name="Failed.")
                await msg.edit(embed=embed)
            else:
                embed = discord.Embed(colour=0xa82021, description="Awesome! Your restaurant's name has been set!")
                await msg.edit(embed=embed)
                new_name = str(name.content).replace('nigg','n*gg').replace('Nigg','N*gg').replace('NIGG','N*GG')
                db.market.update_one({"owner": ctx.author.id}, {"$set":{"name": new_name}})
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `r!start`.")

    @set.command(aliases=['Price'])
    async def price(self, ctx):
        def nc(m):
            return m.author == ctx.message.author
        post = db.market.find_one({"owner": int(ctx.author.id)})
        if post:
            embed = discord.Embed(colour=0xa82021, description="What item would you like to change the price of?")
            embed.set_footer(text="You have 90 seconds to reply")
            msg = await ctx.send(embed=embed)
            item = await self.bot.wait_for('message', check=nc, timeout=90)
            try:
                await item.delete()
            except:
                pass
            it = None
            for x in post['items']:
                if x['name'].lower() == item.content.lower():
                    it = x
            if not it:
                embed = discord.Embed(colour=0xa82021, description=f"That item is not on your menu. Check it with `r!menu {post['name']}`")
                embed.set_author(name="Failed.")
                await msg.edit(embed=embed)
            else:
                embed = discord.Embed(colour=0xa82021, description="What price do you want to set it at?\n\nIt may not be less than $1 or more than $45")
                await msg.edit(embed=embed)
                #db.market.update_one({"owner": ctx.author.id}, {"$set":{"name": name.content}})
                price = await self.bot.wait_for('message', check=nc, timeout=90)
                try:
                    await price.delete()
                except:
                    pass
                if not price.content.isdigit() or int(price.content) > 45 or int(price.content) < 1:
                    embed = discord.Embed(colour=0xa82021, description=f"Prices may not be less than $1 or more than $45")
                    embed.set_author(name="Failed.")
                    await msg.edit(embed=embed)
                else:
                    embed = discord.Embed(colour=0xa82021, description="Amazing! The price has been set.")
                    await msg.edit(embed=embed)
                    db.market.update_one({"owner": ctx.author.id}, {"$pull":{"items": it}})
                    db.market.update_one({"owner": ctx.author.id}, {"$push":{"items":{"name": it['name'],"price": int(price.content),"stock": it['stock'],"sold": it['sold']}}})
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `r!start`.")

    @set.command(aliases=['Stock'])
    @commands.is_owner()
    async def stock(self, ctx):
        # not gonna use
        def nc(m):
            return m.author == ctx.message.author
        post = db.market.find_one({"owner": int(ctx.author.id)})
        embed = discord.Embed(colour=0xa82021, description="What item would you like to stock?\n\nType all to stock all items.")
        embed.set_footer(text="You have 90 seconds to reply")
        msg = await ctx.send(embed=embed)
        item = await self.bot.wait_for('message', check=nc, timeout=90)
        try:
            await item.delete()
        except:
            pass
        it = None
        for x in post['items']:
            if x['name'].lower() == item.content.lower():
                it = x
        if not it:
            embed = discord.Embed(colour=0xa82021, description=f"That item is not on your menu. Check it with `r!menu {post['name']}`")
            embed.set_author(name="Failed.")
            await msg.edit(embed=embed)
        else:
            if it['price'] < 4:
                sp = it['price'] - 1
            elif it['price'] < 6:
                sp = it['price'] - 2
            else:
                sp = it['price'] - 3
            embed = discord.Embed(colour=0xa82021, description=f"How many would you like to stock?\n\nStocking this item once would cost you ${sp}.")
            await msg.edit(embed=embed)
            #db.market.update_one({"owner": ctx.author.id}, {"$set":{"name": name.content}})
            price = await self.bot.wait_for('message', check=nc, timeout=90)
            try:
                await price.delete()
            except:
                pass
            if not price.content.isdigit() or int(price.content) > 45 or int(price.content) < 1:
                embed = discord.Embed(colour=0xa82021, description=f"Prices may not be less than $1 or more than $45")
                embed.set_author(name="Failed.")
                await msg.edit(embed=embed)
            else:
                embed = discord.Embed(colour=0xa82021, description="Amazing! The price has been set.")
                await msg.edit(embed=embed)
                db.market.update_one({"owner": ctx.author.id}, {"$pull":{"items": it}})
                db.market.update_one({"owner": ctx.author.id}, {"$push":{"items":{"name": it['name'],"price": int(price.content),"stock": it['stock'],"sold": it['sold']}}})

    @commands.command(aliases=['Random', 'rr'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def random(self, ctx, user:discord.User=None):
        if not user:
            user = ctx.author
        rndm = random.randint(1, db.market.find().count())
        try:
            p = db.market.find().limit(2).skip(rndm).next()
            if p['owner'] == ctx.author.id:
                if db.market.find().count() == rndm:
                    post = db.market.find().limit(1).skip(rndm-1).next()
                else:
                    post = db.market.find().limit(1).skip(rndm+1).next()
            else:
                post = p
        except StopIteration:
            return
        if not post:
            await ctx.send(f'<:RedTick:653464977788895252> I couldn\'t find {user.name}\'s restaurant in our database.') #you will never see this error, but im not taking it out
        else:
            def react(reaction, user):
                return str(reaction.emoji) == '<:FilledStar:651156130424291368>'
            prices = []
            for item in post['items']:
                prices.append(item['price'])
            average = round(sum(prices)/len(prices))
            ratings = []
            for rating in post['ratings']:
                ratings.append(rating['rating'])
            avr = round(sum(ratings)/len(ratings))
            if avr == 0:
                stars = "<:EmptyStar:651156200142012427><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427>"
            elif avr == 1:
                stars = "<:FilledStar:651156130424291368><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427>"
            elif avr == 2:
                stars = "<:FilledStar:651156130424291368><:FilledStar:651156130424291368><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427>"
            elif avr == 3:
                stars = "<:FilledStar:651156130424291368><:FilledStar:651156130424291368><:FilledStar:651156130424291368><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427>"
            elif avr == 4:
                stars = "<:FilledStar:651156130424291368><:FilledStar:651156130424291368><:FilledStar:651156130424291368><:FilledStar:651156130424291368><:EmptyStar:651156200142012427>"
            elif avr == 5:
                stars = "<:FilledStar:651156130424291368><:FilledStar:651156130424291368><:FilledStar:651156130424291368><:FilledStar:651156130424291368><:FilledStar:651156130424291368>"
            country = str(post['country']).lower()
            ldi = post['items']
            list = sorted(ldi, key=lambda x: x['sold'], reverse=True)
            embed = discord.Embed(description=post['description'])
            embed.set_author(icon_url=self.flags[country], name=post['name'])
            embed.add_field(name=":notepad_spiral: Menu", value=post['items'][0]['name'] + ", " + post['items'][1]['name'] + ", " + post['items'][2]['name'] + f"... To view the full menu, do `r!menu {post['name']}`")
            embed.add_field(name=":bar_chart: Experience", value=format(post['exp'], ",d"))
            #embed.add_field(name=":chart_with_upwards_trend: Most Sold item", value=list[0]['name'])
            embed.add_field(name=":moneybag: Average Price", value="$" + str(average))
            embed.add_field(name=":page_with_curl: Rating", value=stars)
            embed.add_field(name=":name_badge: Owner", value=str(self.bot.get_user(post['owner'])).replace("None", "Unknown"))
            if not post['logo_url']:
                embed.set_thumbnail(url=ctx.me.avatar_url_as(format='png'))
            else:
                embed.set_thumbnail(url=post['logo_url'])
            embed.set_footer(text=f"Random Restaurant | Last Stock: {post['laststock']}")
            msg = await ctx.send(embed=embed)
            await msg.add_reaction('❤')

    @commands.command(aliases=['Slots', 'slot'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def slots(self, ctx, bet:int = None):
        on = False
        if on:
            posts = db.market.find_one({"owner": ctx.author.id})
            if bet == None:
                await ctx.send('<:RedTick:653464977788895252> Please provide your bet with the command. Example: `r!slots 50`')
            elif not int(posts['money']) >= int(bet) or int(posts['money']) == int(bet):
                await ctx.send('<:RedTick:653464977788895252> You don\'t have enough money.')
            elif int(bet) < 25:
                await ctx.send('<:RedTick:653464977788895252> Your bet must be above $25.')
            else:
                emojis = [':ramen:', ':cherries:', ':grapes:', ':banana:', ':poultry_leg:', ':pizza:', ':taco:', ':hamburger:', ':hotdog:']
                fruits = [':cherries:', ':grapes:', ':banana:']
                a = random.choice(emojis)
                b = random.choice(emojis)
                c = random.choice(emojis)
                d = random.choice(emojis)
                e = random.choice(emojis)
                f = random.choice(emojis)
                g = random.choice(emojis)
                h = random.choice(emojis)
                i = random.choice(emojis)
                if a == b == c:
                    if a == ':ramen:':
                        won = bet*6
                        slot1 = discord.Embed(colour=0xa82021, description=f"JACKPOT! You've won ${won}!\n\n{d}   {e}   {f} ` `\n{a}   {b}   {c} `<`\n{g}   {h}   {i} ` `")
                    else:
                        won = bet*3
                        slot1 = discord.Embed(colour=0xa82021, description=f"Amazing! You've won ${won}!\n\n{d}   {e}   {f} ` `\n{a}   {b}   {c} `<`\n{g}   {h}   {i} ` `")
                    await ctx.send(embed=slot1, content=f"{ctx.author.mention}, you've used some of your Restaurant income on a slot machine...")
                    await self.add_money(user=ctx.author.id, count=won)
                elif a == b or a == c or b == c:
                    won = bet*2
                    slot2 = discord.Embed(colour=0xa82021, description=f"Nice! You've won ${won}!\n\n{d}   {e}   {f} ` `\n{a}   {b}   {c} `<`\n{g}   {h}   {i} ` `")
                    await ctx.send(embed=slot2, content=f"{ctx.author.mention}, you've used some of your Restaurant income on a slot machine...")
                    await self.add_money(user=ctx.author.id, count=won)
                else:
                    if a in fruits and b in fruits and c in fruits:
                        won = bet*3
                        slot2 = discord.Embed(colour=0xa82021, description=f"Fruit Bonanza! You've won ${won}!\n\n{d}   {e}   {f} ` `\n{a}   {b}   {c} `<`\n{g}   {h}   {i} ` `")
                        await ctx.send(embed=slot2, content=f"{ctx.author.mention}, you've used some of your Restaurant income on a slot machine...")
                        await self.add_money(user=ctx.author.id, count=won)
                    else:
                        slot3 = discord.Embed(colour=0xa82021, description=f"Aw! You didn't win anything.\n\n{d}   {e}   {f} ` `\n{a}   {b}   {c} `<`\n{g}   {h}   {i} ` `")
                        await ctx.send(embed=slot3, content=f"{ctx.author.mention}, you've used some of your Restaurant income on a slot machine...")
                        await self.take_money(user=ctx.author.id, count=bet)
        else:
            await ctx.send("This command is currently disabled for all users.")

    @commands.command(aliases=['Clean'])
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def clean(self, ctx):
        post = db.market.find_one({"owner": ctx.author.id})
        to_clean = [{'name': 'sink', 'exp': 4}, {'name': 'oven', 'exp': 8}, {'name': 'counters', 'exp': 12}, {'name': 'floors', 'exp': 16}, {'name': 'bathrooms', 'exp': 20}, {'name': 'kitchen', 'exp': 24}]
        if post:
            rn = rnd(to_clean)
            count = await self.add_exp(user=ctx.author.id, count=rn['exp'])
            await ctx.send(f"{ctx.author.mention}, You cleaned the {rn['name']} and earned {count} EXP.")
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `r!start`.")

    @commands.command(aliases=['Fish'])
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def fish(self, ctx):
        post = db.market.find_one({"owner": ctx.author.id})
        to_fish = [{'name': 'a bag of sugar', 'money': 4, 'exp': 5}, {'name': 'some eggs', 'money': 3, 'exp': 3}, {'name': 'a fish', 'money': 11, 'exp': 17}, {'name': 'some rice', 'money': 3, 'exp': 19}, {'name': 'a bag of potatoes', 'money': 6, 'exp': 10}, {'name': 'a few apples', 'money': 7, 'exp': 11}, {'name': 'two bags of carrots', 'money': 8, 'exp': 12}, {'name': 'a bag of flour', 'money': 4, 'exp': 16}, {'name': 'a can of salt', 'money': 7, 'exp': 16}]
        if post:
            x = False
            for x in post['inventory']:
                if 'item' in x:
                    if x['item'] == 'fish':
                        fish = True
                        x = True
                    else:
                        fish = False
                else:
                    pass
            if not x:
                fish = False
            if not fish:
                await ctx.send("You don't have a fishing rod. Buy one by saying `r!buy item` and then saying `1`.")
                self.bot.get_command("fish").reset_cooldown(ctx)
            else:
                rn = rnd(to_fish)
                await self.add_exp(user=ctx.author.id, count=rn['exp'])
                await self.add_money(user=ctx.author.id, count=rn['money'])
                await ctx.send(f"{ctx.author.mention}, You threw out your fishing rod and got {rn['name']} which earned you ${rn['money']} & {rn['exp']} EXP.")
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `r!start`.")

    @commands.command(aliases=['Cookt', 'Baket', 'baket'])
    @commands.cooldown(1, 1, commands.BucketType.user)#cd 150
    async def cookt(self, ctx):
        def nc(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower().replace('r!', '') == 'stop'
        post = db.market.find_one({"owner": ctx.author.id})
        if post:
            bar_int = 1
            country = post['country']
            cfood = rnd(food.food[country])['name']
            if cfood.startswith(("a", "e", "i", "o", "u")):
                cfooda = "an " + cfood
            else:
                cfooda = "a " + cfood
            done = False
            desc = f"Say `stop` when the bar gets to red. Don't let it get burnt!\n\n`🟨`"
            embed = discord.Embed(colour=0xa82021, description=desc)
            embed.set_footer(text=f"You're cooking {cfooda}.")
            msg = await ctx.send(embed=embed)
            time.sleep(0.8)
            bar_int = 1
            done = False
            resp = self.bot.wait_for('message', check=nc, timeout=30)
            while bar_int <= 6:
                if done:
                    pass
                else:
                    bar_int += 1
                    bar = str(bar_int).replace("7", "`🟨🟨🟧🟥🟥⬛`").replace("6", "`🟨🟨🟧🟥🟥⬛`").replace("5", "`🟨🟨🟧🟥🟥`").replace("4", "`🟨🟨🟧🟥`").replace("3", "`🟨🟨🟧`").replace("2", "`🟨🟨`")
                    embed = discord.Embed(colour=0xa82021, description=f"Say `stop` when the bar gets to red. Don't let it get burnt!\n\n{bar}")
                    if bar_int == 7:
                        embed.set_footer(text=f"You burnt the {cfood}!")
                        done = True
                    elif bar_int > 6:
                        embed.set_footer(text=f"You're burning the {cfood}!")
                    else:
                        embed.set_footer(text=f"You're cooking {cfooda}.")
                    await msg.edit(embed=embed)
                    await asyncio.sleep(0.8)
            if resp.content:
                done = True
                await ctx.send('worked')

            #async def text():
            #loop = asyncio.get_event_loop()
            #wfm = loop.create_task(self.bot.wait_for('message', check=nc, timeout=90))
            #inc = loop.create_task(increase())
            #loop.run_until_complete(wfm)
            #wfm = asyncio.run_coroutine_threadsafe(wfm)
            #inc = asyncio.run_coroutine_threadsafe(inc)
            #wfm.result()
            #done = True
            #await ctx.send(wfm)
            #inc.result()
            #loop.run_until_complete(inc)
            #loop = asyncio.get_event_loop()
            #loop.run_until_complete(text())
            #resp = loop.run_until_complete(self.bot.wait_for('message', check=nc, timeout=240))
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `r!start`.")

    @commands.command(aliases=['Cook', 'Bake', 'bake'])
    @commands.cooldown(1, 150, commands.BucketType.user)
    async def cook(self, ctx):
        def nc(m):
            return m.author == ctx.author and m.channel == ctx.channel and not m.content.startswith("r!menu")
        post = db.market.find_one({"owner": ctx.author.id})
        #words = ['potato', 'bun', 'bread', 'cheese', 'tomato', 'olive', 'fish', 'seafood', 'chicken', 'lettuce', 'rice', 'ham', 'turkey', 'soup', 'meat', 'fruit', 'noodles', 'pie', 'water', 'milk', 'cake', 'juice', 'cookie', 'pepper']
        #to_cook = [{'adj': 'a tasty', 'exp': 10}, {'adj': 'a disgusting', 'exp': 0}, {'adj': 'a delicious', 'exp': 15}, {'adj': 'a burnt', 'exp': 1}, {'adj': 'an okay', 'exp': 3}, {'adj': 'a great', 'exp': 6}, {'adj': 'a great', 'exp': 9}, {'adj': 'a not-too-bad', 'exp': 4}]
        if post:
            word = rnd(post['items'])['name']
            ws = word.split(" ")
            new = []
            for x in ws:
                li = list(x)
                random.shuffle(li)
                sw = "".join(li)
                new.append(sw)
            sw = " ".join(new)
            na = word
            await ctx.send(f'{ctx.author.mention}, Unscramble this item on your menu to make it: `{sw}`')
            b = time.perf_counter()
            resp = await self.bot.wait_for('message', check=nc, timeout=240)
            a = time.perf_counter()
            tt = a-b
            if tt < 6:
                if resp.content.lower().lower() == word.lower():
                    c = await self.add_exp(user=ctx.author.id, count=20)
                    await ctx.send(f"Perfect! You made a delicious {na} in {round(tt)} seconds! You've earned {c} EXP.")
                else:
                    c = await self.add_exp(user=ctx.author.id, count=2)
                    await ctx.send(f"Uh oh! You failed to unscramble the letter. You've earned {c} EXP for making a bad {na}.")
            elif tt < 8:
                if resp.content.lower() == word.lower():
                    c = await self.add_exp(user=ctx.author.id, count=16)
                    await ctx.send(f"Amazing! You made a tasty {na} in {round(tt)} seconds! You've earned {c} EXP.")
                else:
                    c =await self.add_exp(user=ctx.author.id, count=1)
                    await ctx.send(f"Uh oh! You failed to unscramble the letter. You've earned {c} EXP for making a terrible {na}.")
            elif tt < 10:
                if resp.content.lower() == word.lower():
                    c = await self.add_exp(user=ctx.author.id, count=12)
                    await ctx.send(f"Great! You made a delicious {na} in {round(tt)} seconds! You've earned {c} EXP.")
                else:
                    await ctx.send(f"Uh oh! You failed to unscramble the letter. You've earned 0 EXP for making a disgusting {na}.")
            elif tt < 12:
                if resp.content.lower() == word.lower():
                    c = await self.add_exp(user=ctx.author.id, count=10)
                    await ctx.send(f"Nice! You made a good {na} in {round(tt)} seconds! You've earned {c} EXP.")
                else:
                    await ctx.send(f"Uh oh! You failed to unscramble the letter. You've earned 0 EXP for making a disgusting {na}.")
            elif tt < 14:
                if resp.content.lower() == word.lower():
                    c = await self.add_exp(user=ctx.author.id, count=8)
                    await ctx.send(f"OK! You made a not-too-bad {na} in {round(tt)} seconds! You've earned {c} EXP.")
                else:
                    await ctx.send(f"Uh oh! You failed to unscramble the letter. You've earned 0 EXP for making a disgusting {na}.")
            elif tt < 18:
                if resp.content.lower() == word.lower():
                    c = await self.add_exp(user=ctx.author.id, count=6)
                    await ctx.send(f"Eh! You made an okay {na} in {round(tt)} seconds! You've earned {c} EXP.")
                else:
                    await ctx.send(f"Uh oh! You failed to unscramble the letter. You've earned 0 EXP for making a disgusting {na}.")
            else:
                if resp.content.lower() == word.lower():
                    c = await self.add_exp(user=ctx.author.id, count=1)
                    await ctx.send(f"Uh oh! You made a disgusting {na} in {round(tt)} seconds! You've earned {c} EXP.")
                else:
                    await ctx.send(f"Uh oh! You failed to unscramble the letter. You've earned 0 EXP for making a disgusting {na}.")
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `r!start`.")

    @commands.command(aliases=['Restaurant', 'r'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def restaurant(self, ctx, *, restaurant=None):
        post = None
        if not restaurant:
            post = db.market.find_one({"owner":ctx.author.id})
        elif ctx.message.mentions:
            if len(ctx.message.mentions) >= 2:
                post = db.market.find_one({"owner":ctx.message.mentions[1].id})
            else:
                post = db.market.find_one({"owner":ctx.message.mentions[0].id})
        else:
            post = db.market.find_one({"name":restaurant})
        if not post:
            await ctx.send('<:RedTick:653464977788895252> I couldn\'t find that restaurant in our database.')
        else:
            def react(reaction, user):
                return str(reaction.emoji) == '<:FilledStar:651156130424291368>'
            prices = []
            for item in post['items']:
                prices.append(item['price'])
            average = round(sum(prices)/len(prices))
            ratings = []
            for rating in post['ratings']:
                ratings.append(rating['rating'])
            avr = round(sum(ratings)/len(ratings))
            if avr == 0:
                stars = "<:EmptyStar:651156200142012427><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427>"
            elif avr == 1:
                stars = "<:FilledStar:651156130424291368><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427>"
            elif avr == 2:
                stars = "<:FilledStar:651156130424291368><:FilledStar:651156130424291368><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427>"
            elif avr == 3:
                stars = "<:FilledStar:651156130424291368><:FilledStar:651156130424291368><:FilledStar:651156130424291368><:EmptyStar:651156200142012427><:EmptyStar:651156200142012427>"
            elif avr == 4:
                stars = "<:FilledStar:651156130424291368><:FilledStar:651156130424291368><:FilledStar:651156130424291368><:FilledStar:651156130424291368><:EmptyStar:651156200142012427>"
            elif avr == 5:
                stars = "<:FilledStar:651156130424291368><:FilledStar:651156130424291368><:FilledStar:651156130424291368><:FilledStar:651156130424291368><:FilledStar:651156130424291368>"
            country = str(post['country']).lower()
            ldi = post['items']
            patrons = db.utility.find_one({"utility": "patrons"})
            if post['owner'] in patrons['bronze']:
                badge = " <:BronzeBadge:667504528006053947>"
            elif post['owner'] in patrons['silver']:
                badge = " <:SilverBadge:667504497051959306>"
            elif post['owner'] in patrons['gold']:
                badge = " <:GoldBadge:667496167281655818>"
            elif post['owner'] in patrons['diamond']:
                badge = " <:DiamondBadge:667504465397416009>"
            else:
                badge = ""
            list = sorted(ldi, key=lambda x: x['sold'], reverse=True)
            embed = discord.Embed(description=post['description'])
            embed.set_author(icon_url=self.flags[country], name=post['name'])
            embed.add_field(name=":notepad_spiral: Menu", value=post['items'][0]['name'] + ", " + post['items'][1]['name'] + ", " + post['items'][2]['name'] + f"... To view the full menu, do `r!menu {post['name']}`")
            embed.add_field(name=":bar_chart: Experience", value=format(post['exp'], ",d"))
            embed.add_field(name=":moneybag: Average Price", value="$" + str(average))
            embed.add_field(name=":page_with_curl: Rating", value=stars)
            embed.add_field(name=":name_badge: Owner", value=str(self.bot.get_user(post['owner'])).replace("None", "Unknown") + badge)
            try:
                if post['banner']:
                    embed.set_image(url=post['banner'])
                else:
                    pass
                if post['colour']:
                    #postc = int(post['colour'])
                    #colour = postc.replace(16777215, 12763842)
                    #print(colour)
                    embed.colour = post['colour']
                else:
                    pass
            except:
                pass
            if not post['logo_url']:
                embed.set_thumbnail(url=ctx.me.avatar_url_as(format='png'))
            else:
                embed.set_thumbnail(url=post['logo_url'])
            embed.set_footer(text=f"Last Work: {post['laststock']}")
            msg = await ctx.send(embed=embed)

    @commands.command(aliases=['Start', 'create'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def start(self, ctx):
        user = db.market.find_one({"owner": ctx.author.id})
        if not user:
            def check(m):
                return m.author == ctx.message.author
            embed = discord.Embed(colour=0xa82021, description='Welcome to Restaurant! First off, which country do you want your theme as? Pick one from this list:\n'\
            ':flag_cn: China\n'\
            ':flag_fr: France\n'\
            ':flag_gr: Greece\n'\
            ':flag_in: India\n'\
            ':flag_it: Italy\n'\
            ':flag_jp: Japan\n'\
            ':flag_mx: Mexico\n'\
            ':flag_tr: Turkey\n'\
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
                failed = discord.Embed(colour=0xa82021, description="That is not in the list of countries.")
                failed.set_author(name="Creation Failed.")
                await msg1.edit(embed=failed)
            else:
                embed = discord.Embed(colour=0xa82021, description='Great! What would you like to name your restaurant? It must be 36 characters or less.')
                embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Creation")
                embed.set_footer(text="You have 90 seconds to reply")
                await msg1.edit(embed=embed)
                name = await self.bot.wait_for('message', check=check, timeout=90)
                try:
                    await name.delete()
                except:
                    pass
                if len(str(name.content)) > 36:
                    failed = discord.Embed(colour=0xa82021, description="Restaurant name must be 36 characters or less")
                    failed.set_author(name="Creation Failed.")
                    msg1.edit(embed=failed)
                else:
                    embed = discord.Embed(colour=0xa82021, description='Almost done! What would you like as your description? It must be 130 characters or less.')
                    embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Creation")
                    embed.set_footer(text="You have 90 seconds to reply")
                    await msg1.edit(embed=embed)
                    desc = await self.bot.wait_for('message', check=check, timeout=90)
                    try:
                        await desc.delete()
                    except:
                        pass
                    if len(str(desc.content)) > 130:
                        failed = discord.Embed(colour=0xa82021, description="Restaurant description must be 130 characters or less")
                        failed.set_author(name="Creation Failed.")
                        await msg1.edit(embed=failed)
                    else:
                        new_name = str(name.content).replace('nigg','n*gg').replace('Nigg','N*gg').replace('NIGG','N*GG').replace('fag', 'f*g').replace('FAG', 'f*g')
                        await self.update_data(ctx.author, country.content.lower(), new_name, desc.content)
                        embed = discord.Embed(colour=0xa82021, description=f'And... Done! Your Restaurant has been created. \n\nCheck your restaurant out with `{self.prefix}restaurant` and view all Restaurant commands with `r!help`.')
                        embed.add_field(name="Quick Tips", value=":one: [Earn some money](http://paixlukee.ml/m/PL0LD.mp4)\n:two: [Set a custom logo](http://paixlukee.ml/m/CBXXZ.mp4)\n:three: [Hire a worker](https://paixlukee.ml/m/1GZCD.mp4)\n:four: [Buy a custom item and use it](http://paixlukee.ml/m/DEMD4.mp4)")
                        embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Creation")
                        await msg1.edit(embed=embed)
        else:
            await ctx.send(f'<:RedTick:653464977788895252> You already have a restaurant created. View it with `r!restaurant`.')

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

    async def add_exp(self, user, count):
        data = db.market.find_one({"owner": user})
        bal = data['exp']
        if 'worker' in data:
            if data['worker']:
                wn = data['worker_name']
                count = count + round(count*data['worker'][wn][0]['exp'])
        exp = int(bal) + count
        db.market.update_one({"owner": user}, {"$set":{"exp": exp}})
        return count

    async def update_data(self, user, country, name, desc):
        set1 = random.randint(0,9)
        set2 = rnd(string.ascii_letters)
        set3 = rnd(string.ascii_letters)
        set4 = random.randint(0,9)
        set5 = rnd(string.ascii_letters)
        set6 = rnd(string.ascii_letters)
        set7 = rnd(string.ascii_letters)
        id = str(set1) + set2 + set3 + str(set4) + set5 + set6 + set7
        post = {
            "owner": user.id,
            "money":0,
            "items":food.food[country],
            "country":country,
            "name":name,
            "description":desc,
            "customers":0,
            "laststock": "Has not worked yet.",
            "id":id,
            "logo_url":None,
            "ratings":[{"rating":5, "user":0}],
            "exp":0,
            "inventory":[],
            "colour": None,
            "banner": None,
            "worker": None,
            "worker_name": None
        }
        db.market.insert_one(post)

def setup(bot):
    bot.add_cog(Shop(bot))
