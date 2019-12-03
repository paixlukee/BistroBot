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
     
    @commands.command(aliases=['Menu'])
    async def menu(self, ctx, *, restaurant=None):
        def nc(m):
            return m.author == ctx.message.author
        if not restaurant:
            await ctx.send("You must include the restaurant name. Example: `r!menu McDonalds`")
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
                    pn = int(choice.content)-1
                    embed = discord.Embed()
                    country = n[pn][str(pn)]['country']
                    #print(n)
                    #print(n[pn][pn+1])
                    embed.set_author(icon_url=self.flags[country], name=f"{n[pn][str(pn)]['name']}'s Menu")
                    desc = ""
                    for x in n[pn][str(pn)]['items']:
                        desc += f"{x['name']} | ${x['price']} | {x['sold']} Sold | {x['stock']} in Stock\n"
                    embed.description = desc
                    await ctx.send(embed=embed)
            elif post.count() == 1:
                post = db.market.find_one({"name": restaurant})
                embed = discord.Embed()
                country = str(post['country'])
                embed.set_author(icon_url=self.flags[country], name=f"{post['name']}'s Menu")
                desc = ""
                for x in post['items']:
                    desc += f"{x['name']} | ${x['price']} | {x['sold']} Sold | {x['stock']} in Stock\n"
                embed.description = desc  
                await ctx.send(embed=embed)
            else:
                await ctx.send("I couldn't find that restaurant in our database. Did you spell it right? Names are case sensitive.")
        
        
    @commands.command(aliases=['Rate'])
    async def rate(self, ctx, user:discord.User=None):
        post = db.market.find_one({"owner": user.id})
        def nc(m):
            return m.author == ctx.message.author
        if not user:
            await ctx.send("You must tag the restaurant owner. Example: `r!rate @lukee#0420`")
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
        
    @commands.group(aliases=['settings', 'Set', 'Settings'])
    async def set(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="'Set' Command Group", description="`r!set logo` - **Set Restaurant logo**\n`r!set description` - **Set Restaurant description**\n`r!set name` - **Set Restaurant name**\n`r!set price` - **Set the price of an item**")
            await ctx.send(embed=embed)
            
    @set.command(aliases=['Logo', 'image', 'icon'])
    async def logo(self, ctx):
        post = db.market.find_one({"owner": ctx.author.id})
        def react(reaction, user):
            return str(reaction.emoji) == '✅' or str(reaction.emoji) == '❎' and user != ctx.me
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
        if not link.content.startswith('http'):
            embed = discord.Embed(colour=0xa82021, description="That is not a valid link.")
            embed.set_author(name="Failed.")
            await msg.edit(embed=embed)
        else:
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
            db.market.update_one({"owner": ctx.author.id}, {"$set":{"name": name.content}})
        
    @commands.command(aliases=['Restaurant', 'shop'])
    async def restaurant(self, ctx, user:discord.User=None):
        if not user:
            user = ctx.author
        post = db.market.find_one({"owner": int(user.id)})
        if not post:
            await ctx.send(f'I couldn\'t find {user.name}\'s restaurant in our database.') 
        else:
            def react(reaction, user):
                return str(reaction.emoji) == '<:FilledStar:651156130424291368>'
            prices = []
            for item in post['items']:
                prices.append(item['price'])
            average = sum(prices)/len(prices)
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
            embed.add_field(name=":notepad_spiral: Menu", value=post['items'][0]['name'] + ", " + post['items'][1]['name'] + ", " + post['items'][2]['name'] + ", " + post['items'][3]['name'] + f"... To view the full menu, do `r!menu {post['name']}`")
            embed.add_field(name=":chart_with_upwards_trend: Most Sold item", value=list[0]['name'])
            embed.add_field(name=":moneybag: Average Price", value="$" + str(average))
            embed.add_field(name=":busts_in_silhouette: Customers", value=post['customers'])
            embed.add_field(name=":page_with_curl: Rating", value=stars)
            if not post['logo_url']:
                embed.set_thumbnail(url=ctx.me.avatar_url_as(format='png'))
            else:
                embed.set_thumbnail(url=post['logo_url'])
            embed.set_footer(text=f"Last Stock: {post['laststock']}")
            msg = await ctx.send(embed=embed)
            #await msg.add_reaction('<:FilledStar:651156130424291368>')            
                             

    @commands.command(aliases=['Start', 'create'])
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
                    embed = discord.Embed(colour=0xa82021, description='Great! What would you like ask your description? It must be 130 characters or less.')
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
                        await self.update_data(ctx.author, country.content.lower(), name.content, desc.content)
                        embed = discord.Embed(colour=0xa82021, description=f'And... Done! Your Restaurant has been created. \n\nI have given you $600 to start. View your restaurant with `{self.prefix}restaurant`')
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
        set6 = rnd(string.ascii_letters) 
        set7 = rnd(string.ascii_letters) 
        #items = []
        #for x in food.food:
            #if x == country:
                #items = x
                             
        id = str(set1) + set2 + set3 + str(set4) + set5 + set6 + set7      
        post = {
            "owner": user.id,
            "money":600,
            "items":food.food[country],
            "country":country,
            "name":name,
            "description":desc,
            "customers":0,
            "boost":None,
            "laststock": "Has not stocked yet.",
            "id":id,
            "logo_url":None,
            "ratings":[{"rating":5, "user":0}]
        }
        db.market.insert_one(post)

def setup(bot):
    bot.add_cog(Shop(bot))
