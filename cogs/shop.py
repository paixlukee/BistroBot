import discord
from discord.ext import commands
import datetime
from datetime import timedelta, datetime as dttm
import requests
import random
import math
import traceback
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
import quests
from threading import Thread
import extra
import workers
import awards
import schedule
import logging
from PIL import Image, ImageDraw
from io import BytesIO
from discord.ui import View, Button
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(config.mongo_client)
db = client['siri']

bbux = "<:BistroBux:1324936072760786964>"

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = 'b.'
        self.countries = ['CHINA', 'FRANCE','GREECE', 'INDIA', 'ITALY', 'JAPAN', 'MEXICO', 'RUSSIA','TURKEY','UNITED KINGDOM', 'UNITED STATES', 'CAFE', 'BAR', 'BAKERY', 'PIZZERIA', 'BRAZIL', 'SOUTH KOREA']
        self.flags = {"china":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_China.png", "france":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_France.png",
                     "greece":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Greece.png", "india":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_India.png",
                     "italy": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Italy.png", "japan": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Japan.png",
                     "mexico":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Mexico.png", "russia":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Russia.png", "turkey": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Turkey.png","united kingdom":"https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_United_Kingdom.png",
                     "united states": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_United_States.png", "south korea": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_South_Korea.png", 
                     "brazil": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Brazil.png", "bakery": "https://media.discordapp.net/attachments/1325282246181130330/1326089017204146176/3C40D072-4DD6-4E88-984E-6B840696A748.png?ex=67880b63&is=6786b9e3&hm=2ed7e672dc0967ec8b2d7684470bd7150460add228a638da00b8df678a1deb11&=&format=webp&quality=lossless&width=700&height=700",
                     "cafe": "https://media.discordapp.net/attachments/1325282246181130330/1326089126054854656/A65522AB-42C0-487E-B6D3-CB59D896DCF4.png?ex=67880b7d&is=6786b9fd&hm=85e39b1d2adb8566f4cbf118f93c70cee47f602f72e083e7c046c6763382b152&=&format=webp&quality=lossless&width=1046&height=1046",
                     "pizzeria": "https://media.discordapp.net/attachments/1325282246181130330/1326089393139748904/CC183333-A5B5-4C69-A1F1-3FACA9558B11.png?ex=67880bbc&is=6786ba3c&hm=a7c4367a54a4a44d73d87cb93463465d2a2eff9f4838a40a8f3e3677bf1c22b3&=&format=webp&quality=lossless&width=700&height=700",
                     "bar": "https://media.discordapp.net/attachments/1325282246181130330/1328889327542865992/3AEA0AEC-A6C7-4FEB-A70F-7A52E721ABBC.png?ex=679192a1&is=67904121&hm=486f7dfefbafb66b033840ba21d36a1a610a2a243685f606fc0c01a28f2939a9&=&format=webp&quality=lossless&width=700&height=700",
                     "singapore": "https://cdn2.iconfinder.com/data/icons/world-flag-icons/128/Flag_of_Singapore.png"}
        self.exp_needed = {"2": 200, "3": 400, "4": 700, "5": 1000, "6": 1500, "7": 2000, "8": 2500, "9": 3000, "10": 3500, "11": 4000, "12": 5000, "13": 6000, "14": 7500, "15": 9000}
        self.unlocks = {"2": ['Experience Potion', '+1 Luck Level'], "3": ['+1 Luck Level', '100 BB'], "4": ['Add a custom item to the menu', '100 BB'], "5": ['Custom dine message', '300 BB'], "6": ["Set a custom banner", '100 BB'], "7": ["500 BB"], "8": ["+1 Luck Level", '100 BB'], "9": ['1 of each Enhancement Fragment'],"10": ["Golden Apron", "500 BB"], "11": ['+50 Customers/day', '100 BB'], "12": ["Time Machine", '100 BB'], "13": ['+1 Luck Level', '100 BB'], "14": ["+1 Luck Level", '100 BB'], "15": ["Time Machine", "500 BB"]}
        self.levelEmoji = {"1": "<:levelone:796813114652753992>", "2": "<:leveltwo:796813114779762729>", "3": "<:levelthree:796813114640433152>", "4": "<:levelfour:796813115055538186>", "5": "<:levelfive:1328924307581177861> ", "6": "<:levelsix:1328924417342046208>",
                           "7": "<:levelseven:1328924460417286244>", "8": "<:leveleight:1328924512783433788>", "9": "<:levelnine:1328924559013056512>", "10": "<:levelten:1328924635739459676>", "11": "<:leveleleven:1328924731285700670>", "12": "<:leveltwelve:1328924789871743028>",
                           "13": "<:levelthirteen:1328924832422690857>", "14": "<:levelfourteen:1328924878400651345>", "15": "<:levelfifteen:1328924948143673384>"}

    @commands.command(aliases=['Leaderboard', 'lb'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def leaderboard(self, ctx, page="1"):
        if isinstance(page, int) or isinstance(page, str) and page.isdigit():
            page = int(page)
            await ctx.typing()
            start = (page - 1) * 8
            end = start + 8
            embed = discord.Embed(colour=0x8980d9, description="Global Bistro Leaderboard")
            find_c = await db.market.find().sort("total_exp", -1).to_list(length=None)
            for i, x in enumerate(find_c[start:end]):
                exp = format(x['total_exp'], ",d")
                level = x['level']
                emoji = ""
                if i == 0:
                    emoji = " :first_place:"
                elif i == 1:
                    emoji = " :second_place:"
                elif i == 2:
                    emoji = " :third_place:"
                embed.add_field(name=x['name'] + emoji, value=f"{self.levelEmoji[str(level)]} {exp} EXP", inline=False)

            embed.set_footer(text=f"Page {page} | b.lb {page + 1} for next page")

            prev_button = Button(label="←", custom_id="prev_page", style=discord.ButtonStyle.primary)
            next_button = Button(label="→", custom_id="next_page", style=discord.ButtonStyle.primary)
            
            if page == 1:
                prev_button.disabled = True

            prev_button.callback = lambda interaction: self.button_callback(interaction, ctx)
            next_button.callback = lambda interaction: self.button_callback(interaction, ctx)

            view = View()
            view.add_item(prev_button)
            view.add_item(next_button)

            await ctx.send(embed=embed, view=view)

        elif isinstance(page, str):
            # Handle the case where page is a restaurant name
            r = await db.market.find_one({"name": page})
            if not r:
                embed2 = discord.Embed(color=0x8980d9, description=f'<:RedTick:653464977788895252> Could not find a restaurant called "{page}". Try finding a page with `b.lb 7`')
                embed2.set_footer(text="This query is CASE SENSITIVE!")
                await ctx.send(embed=embed2)
                return
            tr_page = await db.market.find().sort("total_exp", -1).to_list(length=None)
            res_rank = None
            for idx, entry in enumerate(tr_page):
                if entry['name'].lower() == page.lower():
                    res_rank = idx
                    break
            page_num = (res_rank // 8) + 1
            start = (page_num - 1) * 8
            end = start + 8
            embed = discord.Embed(colour=0x8980d9, description="Global Bistro Leaderboard")
            for i, x in enumerate(tr_page[start:end]):
                exp = format(x['total_exp'], ",d")
                level = x['level']
                emoji = ""
                if i == 0:
                    emoji = " :first_place:"
                elif i == 1:
                    emoji = " :second_place:"
                elif i == 2:
                    emoji = " :third_place:"
                embed.add_field(name=x['name'] + emoji, value=f"{self.levelEmoji[str(level)]} {exp} EXP", inline=False)

            embed.set_footer(text=f"Page {page_num} | b.lb {page_num + 1} for next page")

            await ctx.send(embed=embed)
            
    async def button_callback(self, interaction, ctx):
        footer_text = interaction.message.embeds[0].footer.text
        current_page = int(footer_text.split("Page ")[1].split(" |")[0])
        
        if interaction.user != ctx.author:
            return
        if interaction.data['custom_id'] == 'next_page':
            await self.show_page(ctx, current_page + 1, interaction)
        elif interaction.data['custom_id'] == 'prev_page' and not current_page == 1:
            await self.show_page(ctx, current_page - 1, interaction)


    async def show_page(self, ctx, page, interaction):
        # Show the requested page again with the updated page number
        start = (page - 1) * 8
        end = start + 8
        embed = discord.Embed(colour=0x8980d9, description="Global Bistro Leaderboard")
        find_c = await db.market.find().sort("total_exp", -1).to_list(length=None)
        for i, x in enumerate(find_c[start:end]):
            exp = format(x['total_exp'], ",d")
            level = x['level']
            emoji = ""
            if i == 0:
                emoji = " :first_place:"
            elif i == 1:
                emoji = " :second_place:"
            elif i == 2:
                emoji = " :third_place:"
            embed.add_field(name=x['name'] + emoji, value=f"{self.levelEmoji[str(level)]} {exp} EXP", inline=False)

        embed.set_footer(text=f"Page {page} | b.lb {page + 1} for next page")

        prev_button = Button(label="←", custom_id="prev_page", style=discord.ButtonStyle.primary)
        next_button = Button(label="→", custom_id="next_page", style=discord.ButtonStyle.primary)
        
        
        
        if page == 1:
            prev_button.disabled = True
        prev_button.callback = lambda interaction: self.button_callback(interaction, ctx)
        next_button.callback = lambda interaction: self.button_callback(interaction, ctx)
        
        view = View()
        view.add_item(prev_button)
        view.add_item(next_button)

        await interaction.response.edit_message(embed=embed, view=view)

    @commands.command(aliases=['Delete'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def delete(self, ctx):
        def ans(m):
            return m.author == ctx.message.author
        post = await db.market.find({"owner": ctx.author.id})
        if post:
            msg = await ctx.send("Are you sure you want to delete your restaurant? Deleting will erase all of your hardwork. If you're sure, reply with \"I'm sure\".")
            try:
                a = await self.bot.wait_for('message', check=ans, timeout=20)
                resp = a.content.lower().replace("’", "'")
            except asyncio.TimeoutError:
                await ctx.send('You took too long to answer. Deletion canceled.')
            else:
                if resp == "i'm sure":
                    await ctx.send("Account deleted. Thanks for using Bistro.")
                    await db.market.delete_one({"owner": ctx.author.id})
                else:
                    await ctx.send('Deletion canceled.')
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `b.start`.")
            
    @commands.command(aliases=['Advertise', 'advert'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def advertise(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        celebrities = ["Taylor Swift", "Lady Gaga", "Zac Efron", "6ix9ine", "Brendon Urie", "Tom Holland", "Katy Perry", "Ellen DeGeneres", "Logan Paul", "Benedict Cumberpatch", "John Cena", "Miley Cyrus", "Kylie Jenner", "Dua Lipa", "Ariana Grande", "Ryan Gosling", "Selena Gomez", "Shawn Mendes", "Keanu Reeves", "Beyoncé", "Rihanna", "Eminem", "Gordon Ramsey", "Billie Eilish", "Drake", "Kendrick Lamar", "Zendaya"]
        def check(m):
                return m.author == ctx.message.author
        if post:
            if post['advert']:
                embed = discord.Embed(colour=0x8980d9)
                if post['advert'] == 'social_media':
                    text = 'Social Media Ad'
                    emoji = ':mobile_phone:'
                elif post['advert'] == 'tv_ad':
                    text = 'TV Advertisement'
                    emoji = ':tv:'
                elif post['advert'] == 'web_ad':
                    text = 'Web Advertisement'
                    emoji = ':computer:'
                elif post['advert'] == 'billboard':
                    text = 'Billboard'
                    emoji = ':frame_photo:'
                embed.description = f'{ctx.author.mention}, Your {emoji} **{text}** is in progress! You cannot buy another advert until your current one ends at **1 AM ET**.'
                await ctx.send(embed=embed)
            else:
                embed2 = discord.Embed(colour=0x8980d9, description = 'You can only buy one advert per day! Each advert lasts until the day is over.\n\n'
                f'**[1]  :mobile_phone: Social Media Ad** - {bbux}30\n'\
                '*An extra 30 customers today*\n'\
                f'**[2]  :computer: Web Ad** - {bbux}50\n'\
                '*An extra 60 customers today*\n'\
                f'**[3]  :tv: TV Ad** - {bbux}80\n'\
                '*An extra 100 customers today*\n'\
                f'**[4]  :frame_photo: Billboard** - {bbux}100\n'\
                '*An extra 125 customers today*\n')
                embed2.set_footer(text="You have 60 seconds to choose an option below.")
                count = 0
                past_count = post['customers_per_day']
                msg = None
                advert_start = False
                async def e_button_callback(interaction, opt):
                    insufficient = "f"
                    await interaction.response.defer()
                    if opt == "1":
                        if post['money'] < 30:
                            insufficient = "t"
                        else:
                            count = 30
                            advert_start = True
                            await self.take_money(user=ctx.author.id, count=30)
                            db.market.update_one({"owner": ctx.author.id}, {"$set": {"advert": "social_media"}})
                    elif opt == "2":
                        if post['money'] < 50:
                            insufficent = "t"
                        else:
                            count = 60
                            advert_start = True
                            await self.take_money(user=ctx.author.id, count=50)
                            db.market.update_one({"owner": ctx.author.id}, {"$set": {"advert": "web_ad"}})
                    elif opt == "3":
                        if post['money'] < 80:
                            insufficient = "t"
                        else:
                            count = 100
                            advert_start = True
                            await self.take_money(user=ctx.author.id, count=80)
                            db.market.update_one({"owner": ctx.author.id}, {"$set": {"advert": "tv_ad"}})
                    elif opt == "4":
                        if post['money'] < 100:
                            insufficient = "t"
                        else:
                            count = 125
                            advert_start = True
                            await self.take_money(user=ctx.author.id, count=100)
                            db.market.update_one({"owner": ctx.author.id}, {"$set": {"advert": "billboard"}})
                    if insufficient == "t":
                        await ctx.send(f"<:RedTick:653464977788895252> You have an insufficent balance! You only have {bbux}{post['money']}.")
                    elif insufficient == "f":
                        await ctx.send(f"{ctx.author.mention}, You bought an advert and asked **{rnd(celebrities)}** to star in it. You will now get an extra **{count} customers** today.")
                    if msg:
                        await msg.delete()
                    if advert_start:
                        if "advertise" in post['tasks']:
                            user = post
                            ix = user['tasks'].index("advertise")
                            if user['task_list'][ix]['completed']+1 == 1:
                                await ctx.author.send(f"You have completed the **{user['task_list'][ix]['description']}** task. You have been awarded **{user['task_list'][ix]['rewards']} EXP**.")
                                await self.add_exp(user=ctx.author.id, count=user['task_list'][ix]['rewards'], multiplier=False)
                                await db.market.update_one({"owner": ctx.author.id, "task_list.name": "advertise"},{"$set": {"task_list.$.completed": 1}})
                    try:
                        await interaction.message.delete()
                    except:
                        pass
                # imagine if i could code right........        
                opt1 = Button(label="1", custom_id="a_opt1", style=discord.ButtonStyle.primary)    
                opt2 = Button(label="2", custom_id="a_opt2", style=discord.ButtonStyle.primary) 
                opt3 = Button(label="3", custom_id="a_opt3", style=discord.ButtonStyle.primary) 
                opt4 = Button(label="4", custom_id="a_opt4", style=discord.ButtonStyle.primary) 
                
                opt1.callback = lambda interaction: e_button_callback(interaction, '1')
                opt2.callback = lambda interaction: e_button_callback(interaction, '2')
                opt3.callback = lambda interaction: e_button_callback(interaction, '3')
                opt4.callback = lambda interaction: e_button_callback(interaction, '4')
                
                view = View()
                view.add_item(opt1)   
                view.add_item(opt2)   
                view.add_item(opt3)   
                view.add_item(opt4)  
            
                msg = await ctx.send(embed=embed2, view=view)    
        

    @commands.command(aliases=['Workers'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def workers(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        if post['worker'] or post['chef']:
            desc = []
            ratings = []
            for rating in post['ratings']:
                ratings.append(rating['rating'])
            avr = round(sum(ratings)/len(ratings))
            if avr <= 2:
                wr = ["Working at {} is really hard...", "The food here at {} isn't the greatest...", "I hate working at {}! It's disgusting here!", "I want to work somewhere else...", "My boss doesn't care about his employees, I have never even gotten a raise... That's why I steal money from the register!", "This place gives me the creeps..", "I'd quit if I didn't have to pay child support...", "I'd rather work with Gordon Ramsay", "The food here is foul, not gonna lie", "This place needs a better owner!", "I dread waking up and coming here every day", "I am amazed that {} hasn't been shut down yet"]
            else:
                wr = ["I love working at {}! The food is delicious here!", "{} is such a great place to work at, I absolutely love it!", "The working environment here at {} is so positive!", "I love working here!", 
                      "I actually like coming to work!", "Better than my old job at McDonalds...", "I love {}... even my boss is great!", "This place is the bomb!", "I love my boss so much!", "I am so glad to be a part of the team!", "I love {}!"]
            comment = random.choice(wr).format(post['name'])
            comment2 = random.choice(wr).format(post['name'])
            if comment == comment2:
                comment2 = random.choice(wr).format(post['name'])
            if post['worker']:
                worker_name = post['worker_name']
                desc.append(f":technologist: **Manager:** {worker_name}\n\n"\
                       f"**EXP Bonus:** {round(post['worker'][worker_name][0]['exp']*100)}%\n"\
                       f"**Tips Bonus:** {round(post['worker'][worker_name][1]['tips']*100)}%\n"\
                       f"**Earns You:** <:BistroBux:1324936072760786964>{round(post['worker'][worker_name][2]['pay'])}/day\n"\
                       f"\n**\"**{comment}**\"**")
            if post['chef']:
                country = post['country']
                chef = post['chef']
                if chef == "m":        
                    chef_name = workers.chef_name[country][0]['m']
                    cd = "20"
                else:
                    chef_name = workers.chef_name[country][1]['w']  
                    cd = "40"
                    
                desc.append(f":cook: **Chef:** {chef_name}\n\n"\
                       f"**Cook Cooldown:** -{cd} seconds\n"\
                       f"\n**\"**{comment2}**\"**")
            
            embed = discord.Embed(colour=0x8980d9, description="\n\n".join(desc))
            if post['colour']:
                if post['colour'] == 0x171717:
                    embed.colour = random.randint(0, 0xFFFFFF)
                else:
                    embed.colour = post['colour']
            await ctx.send(embed=embed)
        else:
            await ctx.send("<:RedTick:653464977788895252> You didn't hire a co-worker! Do `b.hire` to get one!")

    @commands.command(aliases=['Hire'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def hire(self, ctx):
        def a(m):
            return m.author == ctx.message.author
        post = await db.market.find_one({"owner": ctx.author.id})
        c = str(post['country'])
        available = workers.list[c]
        chefs_avail = workers.chef_name[c]
        wrks = [[key for key in available[0]][0], [key for key in available[1]][0], [key for key in available[2]][0], [key for key in available[3]][0]]
        wd = f"<:W1:1325370058372812860> `{[key for key in available[0]][0]}` **-5% EXP** | **+40% Tips** | **Earns you <:BistroBux:1324936072760786964>14/day**\n"\
             f"<:M1:1325372100529225738> `{[key for key in available[1]][0]}` **+10% EXP** | **+20% Tips** | **Earns you <:BistroBux:1324936072760786964>12/day**\n"\
             f"<:W2:1325370773212233849> `{[key for key in available[2]][0]}` **+5% EXP** | **-10% Tips** | **Earns you <:BistroBux:1324936072760786964>20/day**\n"\
             f"<:M2:1325373899688509500> `{[key for key in available[3]][0]}` **+25% EXP** | **+10% Tips** | **Earns you <:BistroBux:1324936072760786964>8/day**"
        chefs = [chefs_avail[0]['m'], chefs_avail[1]['w']]
        chef_names = f"<:ChefM:1329677738059104307> `{chefs_avail[0]['m']}` **-20s Cook Cooldown** | **Costs {bbux}200 upfront, {bbux}20 from daily**\n"\
                     f"<:ChefW:1329678594741637171> `{chefs_avail[1]['w']}` **-40s Cook Cooldown** | **Costs {bbux}350 upfront, {bbux}40 from daily**"
        embed = discord.Embed(description=f"Which worker would you like to hire? You can only have one manager and one chef at a time.\n\n**Manager**:\nEach manager costs <:BistroBux:1324936072760786964>500 upfront and an additional <:BistroBux:1324936072760786964>50 taken away from the daily command.\n{wd}"\
            f"\n\n**Chef**:\nYou must have at least 500 customers to hire a chef\n{chef_names}\n\n**__NOTE__**: You must re-pay the upfront fee when switching workers")
        embed.set_footer(text="You have 60 seconds to reply.")
        await ctx.send(embed=embed)
        msg = await self.bot.wait_for('message', check=a, timeout=20)
        chosen = msg.content.capitalize()
        if msg.content in chefs:
            if post['customers'] < 500:
                await ctx.send("<:RedTick:653464977788895252> You must have had at least 500 customers to hire a chef!")
                return
            if msg.content == chefs[0]:
                if not post['money'] >= 200:
                    await ctx.send("<:RedTick:653464977788895252> You don't have enough money.")
                    return
                else:
                    await db.market.update_one({"owner": ctx.author.id}, {"$set": {"chef": "m"}})
                    emb = discord.Embed(colour=0x8980d9, description=f"Hello, {ctx.author.name.capitalize()}!\n\nThanks for hiring me! I hope that I can help make your restaurant amazing! If you ever want to check on me, do `b.workers`.")
                    emb.set_author(name=f"Message from {chefs_avail[0]['m']}", icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcStHcjAvE9Z_eC1quY6moMTU4aLWNkiusCAdA&s")
                    await ctx.send(embed=emb)
                    await self.take_money(user=ctx.author.id, count=200)
            else:               
                if not post['money'] >= 350:
                    await ctx.send("<:RedTick:653464977788895252> You don't have enough money.")
                    return
                else:
                    await db.market.update_one({"owner": ctx.author.id}, {"$set": {"chef": "w"}})
                    emb = discord.Embed(colour=0x8980d9, description=f"Hello, {ctx.author.name.capitalize()}!\n\nThanks for hiring me! I hope that I can help make your restaurant amazing! If you ever want to check on me, do `b.workers`.")
                    emb.set_author(name=f"Message from {chefs_avail[1]['w']}", icon_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcStHcjAvE9Z_eC1quY6moMTU4aLWNkiusCAdA&s")
                    await ctx.send(embed=emb)
                    await self.take_money(user=ctx.author.id, count=350)
                    
        elif msg.content in wrks:
            chw = None
            for x in available:
                if chosen in x:
                    chw = x
            if not post['money'] >= 500:
                await ctx.send("<:RedTick:653464977788895252> You don't have enough money.")
            else:
                if not 'worker' in post:
                    await db.market.update_one({"owner": ctx.author.id}, {"$set": {"worker": None}})
                    await db.market.update_one({"owner": ctx.author.id}, {"$set": {"worker_name": None}})
                else:
                    pass
                if post['worker'] == chosen:
                    await ctx.send(f"<:RedTick:653464977788895252> You already have this worker!")
                    return
                await self.take_money(user=ctx.author.id, count=500)
                await db.market.update_one({"owner": ctx.author.id}, {"$set": {"worker": chw}})
                await db.market.update_one({"owner": ctx.author.id}, {"$set": {"worker_name": chosen}})
                award = await self.get_award(ctx.author.id, "worker")
                me = discord.Embed(colour=0x8980d9, description=f"Hello, {ctx.author.name.capitalize()}!\n\nThanks for hiring me! I hope that I can help make your restaurant the best in the world! If you ever want to check on me, do `b.workers`.")
                me.set_author(name=f"Message from {chosen}", icon_url="http://paixlukee.dev/m/SKRFY.png")
                await ctx.send(embed=me)
                if award:
                    await ctx.send(f"{ctx.author.mention}, You achieved the {awards.awards["worker"]["emoji"]} **Teamwork** award for hiring a worker!")
        else:
            await ctx.send(f"<:RedTick:653464977788895252> That's not in the list of workers! Example: `{[key for key in available[1]][0]}`")




    @commands.command(aliases=['restaurantfuse'])
    async def fuse(self, ctx):
        embed = discord.Embed(colour=0x8980d9)
        embed.set_author(name="Restaurant Fusing", icon_url=ctx.bot.user.avatar.url)
        embed.set_image(url="https://i.ibb.co/yNMrNnq/restaurantfuse.png")
        embed.description = "Want to have two food types in one restaurant?\n"\
                            "Fusing your restaurant will mix foods from two different countries.\n\n"\
                            "To fuse your restaurant, you need to have **2,000 or more experience**. It costs **<:BistroBux:1324936072760786964>1,000** to fuse.\n\n"\
                            "Do `b.rfuse` to fuse your restaurant."
        await ctx.send(embed=embed)

    @commands.command()
    async def rfuse(self, ctx):
        def nc(m):
            return m.author == ctx.message.author
        post = await db.market.find_one({"owner": ctx.author.id})
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `b.restaurant`.")
        elif post['exp'] <= 2000:
            await ctx.send("<:RedTick:653464977788895252> You don't have enough experience to fuse!")
        elif post['money'] <= 1000:
            await ctx.send("<:RedTick:653464977788895252> You don't have enough money to fuse!")
        else:
            embed = discord.Embed(colour=0x8980d9, description="What country would you like to fuse with?")
            embed.set_footer(text="You have 90 seconds to answer.")
            embed.set_author(name="Restaurant Fusing", icon_url=ctx.bot.user.avatar.url)
            choice = await self.bot.wait_for('message', check=nc, timeout=90)
            if not choice.content.upper() in self.countries:
                embed = discord.Embed(colour=0x8980d9, title="Fusing failed.", description="That is not a vaild country.")
            else:
                pass


    @commands.command(aliases=['Menu'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def menu(self, ctx, *, restaurant=None):
        await ctx.typing()
        def nc(m):
            return m.author == ctx.message.author
        if ctx.message.mentions:
            if len(ctx.message.mentions) >= 2:
                restaurant = await db.market.find_one({"owner":ctx.message.mentions[1].id})['name']
            else:
                restaurant = await db.market.find_one({"owner":ctx.message.mentions[0].id})['name']
        if not restaurant:
            try:
                pr = await db.market.find_one({"owner": ctx.author.id})
                restaurant = pr['name']
            except:
                await ctx.send("<:RedTick:653464977788895252> You must include the restaurant name. Example: `b.menu McDonalds`")
                return
        post = await db.market.find({"name": restaurant}).to_list(length=None)
        post_count = await db.market.count_documents({"name": restaurant})
        if post_count > 1:
            embed = discord.Embed(colour=0x8980d9, title="Multiple results found.")
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
                embed = discord.Embed(colour=0x8980d9, title="Failed", description="Invalid number.")
                await ctx.send(embed=embed)
            else:
                pn = int(choice.content)
                embed = discord.Embed()
                country = n[pn-1][str(pn)]['country']
                embed.set_author(icon_url=self.flags[country], name=f"{n[pn-1][str(pn)]['name']}'s Menu")
                desc = ""
                for x in n[pn-1][str(pn)]['items']:
                    desc += f"{x['name']} | <:BistroBux:1324936072760786964>{x['price']} | {x['sold']} Sold\n"
                embed.description = desc
                await ctx.send(embed=embed)
        elif post_count == 1:
            post = await db.market.find_one({"name": restaurant})
            embed = discord.Embed()
            country = str(post['country'])
            embed.set_author(icon_url=self.flags[country], name=f"{post['name']}'s Menu")
            desc = ""
            for x in post['items']:
                desc += f"{x['name']} | <:BistroBux:1324936072760786964>{x['price']} | {x['sold']} Sold\n"#| {x['stock']} in Stock
            embed.description = desc
            if post['colour']:
                if post['colour'] == 0x171717:
                    embed.colour = random.randint(0, 0xFFFFFF)
                else:
                    embed.colour = post['colour']
            await ctx.send(embed=embed)
        else:
            await ctx.send("<:RedTick:653464977788895252> I couldn't find that restaurant in our database. Did you spell it right? Names are case sensitive.")


    @commands.command(aliases=['Rate'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def rate(self, ctx, user:discord.User=None):
        post = await db.market.find_one({"owner": user.id})
        def nc(m):
            return m.author == ctx.message.author
        if not user:
            await ctx.send("<:RedTick:653464977788895252> You must tag the restaurant owner. Example: `b.rate @paixlukee`")
        elif user == ctx.author:
            await ctx.send("<:RedTick:653464977788895252> You cannot rate your own restaurant.")
        else:
            posts = await db.market.find_one({"owner": user.id})
            rus = []
            for x in posts['ratings']:
                rus.append(x['user'])
            if str(ctx.author.id) in rus:
                await ctx.send("<:RedTick:653464977788895252> You already rated this restaurant.")
            else:
                embed = discord.Embed(colour=0x8980d9, description=f"Out of 5 stars, how would you rate {post['name']}?")
                embed.set_footer(text="You have 90 seconds to reply")
                msg = await ctx.send(embed=embed)
                rating = await self.bot.wait_for('message', check=nc, timeout=90)
                try:
                    await rating.delete()
                except:
                    pass
                if not rating.content.isdigit() or int(rating.content) > 5 or int(rating.content) < 0:
                    embed = discord.Embed(colour=0x8980d9, description="The rating must be from 0-5.")
                    embed.set_author(name="Failed.")
                    await msg.edit(embed=embed)
                else:
                    embed = discord.Embed(colour=0x8980d9, description=f"You have successfully rated {post['name']}.")
                    await msg.edit(embed=embed)
                    await db.market.update_one({"owner": user.id}, {"$push":{"ratings": {"rating": int(rating.content), "user":str(ctx.author.id)}}})


    @commands.group(aliases=['Buy'])
    async def buy(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(colour=0x8980d9, title="'Buy' Command Group", description="`b.buy custom` - **Buy a restaurant customisation chest**\n`b.buy chest` - **Buy a chest filled with random goods**\n`b.buy food` - **Buy a menu item and have it added to your menu**\n`b.buy item` - **Buy an item from the store**")
            await ctx.send(embed=embed)
            
    @buy.command(aliases=['Chest', 'chests'])
    async def chest(self, ctx):
        await ctx.typing()
        post = await db.market.find_one({"owner": ctx.author.id})
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Start one with `b.")
            return
        msg = None
        embed = discord.Embed(colour=0x8980d9, title="Which chests would you like to buy?", description=
        "Chests can include: banners, colors, shop items, money or enhancement fragments\n\n"\
        f"**[1] <:CommonChest:1332452120787423302> Common Chest** - {bbux}200\n"\
        f"**[2] <:UncommonChest:1332452893323694141> Uncommon Chest** - {bbux} 300")
        embed.set_footer(text="Choose a number below to buy it.")
        async def chest_cb1(interaction, msg):
            if post['money'] < 200:
                await interaction.followup.send(f"<:RedTick:653464977788895252> You don't have enough money! Balance: {bbux}{post['money']}")
                return
            await self.take_money(ctx.author.id, 200)
            options = ['color'] * 10 +  ['banner'] * 7 + ['rod'] * 4 + ['apron'] * 4 + ['extinguisher'] * 2 + ['exp'] * 3 + ['tm'] * 3 + ['money'] * 3 + ['fragment'] * 2
            ran_opt1 = rnd(options)
            ran_opt2 = rnd(options)
            both_opts = [ran_opt1, ran_opt2]
            opts_toprint = []
            for opt in both_opts:
                if opt == 'color':
                    owned_colors = {item['colour']['colour'] for item in post['inventory'] if 'colour' in item}
                    colors_f = {
                        rarity: [color for color in items.colours[rarity] if color['colour'] not in owned_colors]
                        for rarity in items.colours
                    }
                    rarity = 'common'
                    if not colors_f['common']:
                        rarity = 'uncommon'
                    chosen = rnd(colors_f[rarity])
                    chosen['rarity'] = rarity.capitalize()
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"colour": chosen}}})
                    opts_toprint.append(f"<:ColourIcon:659418340703469584> {chosen['colour']}")
                elif opt == 'banner':
                    owned_banners = {item['banner']['name'] for item in post['inventory'] if 'banner' in item}
                    banners_f = {
                        rarity: [banner for banner in items.banners[rarity] if banner['name'] not in owned_banners]
                        for rarity in ['common', 'uncommon', 'rare']
                    }
                    rr = ['common'] * 6 + ['uncommon'] * 3 + ['rare']
                    rarity = rnd(rr)
                    chosen = rnd(banners_f[rarity])
                    chosen['rarity'] = rarity.capitalize()
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"banner": chosen}}})
                    opts_toprint.append(f"<:BannerIcon:657457820295495699> {chosen['name']}")
                elif opt == 'rod':
                    opts_toprint.append("<:FishingRod:1333893065542336523> Fishing Rod")
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "fish"}}})
                elif opt == 'tm':
                    opts_toprint.append("<:TimeMachine:1333889857688436847> Time Machine")
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "tm"}}})
                elif opt == 'exp':
                    opts_toprint.append("<:ExperiencePotion:715822985780658238> Experience Potion")
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "ep"}}})
                elif opt == 'extinguisher':
                    opts_toprint.append("<:FireExtinguisher:1333891774472523888> Fire Extinguisher")
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "fe"}}})
                elif opt == 'apron':
                    if 'apron_uses' in post:
                        uses = post['apron_uses']
                        opts_toprint.append("<:GoldenApron:1327865002559803452> +20 Golden Apron uses")
                        await db.market.update_one({"owner": ctx.author.id}, {"$inc": {"apron_uses": 20}})
                    else:
                        opts_toprint.append("<:GoldenApron:1327865002559803452> Golden Apron")
                        await db.market.update_one({"owner": ctx.author.id}, {"$set": {"apron_uses": 20}})           
                elif opt == 'money':
                    rn_m = random.randint(60, 130)
                    opts_toprint.append(f"{bbux}{rn_m}")
                    await self.add_money(ctx.author.id, rn_m)
                elif opt == 'fragment':
                    frag = await self.add_rand_fragment(ctx.author.id)
                    if not frag:
                        await self.add_money(ctx.author.id, 150)
                        opts_toprint.append(f"{bbux}150")
                    else:
                        if frag == 'agility': 
                            opts_toprint.append(f"<:AgilityFragment:1331502143760236574> Fragment of Agility")
                        elif frag == 'opportunity':
                            opts_toprint.append(f"<:OpportunityFragment:1331505178959937556> Fragment of Opportunity")
                        elif frag == 'endearing':
                            opts_toprint.append(f"<:EndearingFragment:1331823626080620574> Fragment of Endearing")
                        elif frag == 'ambience':
                            opts_toprint.append(f"<:AmbienceFragment:1331825947036483675> Fragment of Ambience")
            embed_2 = discord.Embed(colour=0x8980d9, description="* "+"\n* ".join(opts_toprint))
            embed_2.set_thumbnail(url="https://media.discordapp.net/attachments/1325282246181130330/1332452463932080138/New_Piskel_49.png?ex=67954e8f&is=6793fd0f&hm=8e702bf420f47d161ead96e3f305fac5ac9d457ce306ec55c690bbee683a8f44&=&format=webp&quality=lossless&width=1092&height=780")
            await ctx.send(embed=embed_2, content=f"{ctx.author.mention}, you opened a Common Chest and received...")
            await msg.delete()              
            try:
                await interaction.message.delete()
            except:
                pass
                                 
                        
        async def chest_cb2(interaction, msg):
            if post['money'] < 300:
                await interaction.followup.send(f"<:RedTick:653464977788895252> You don't have enough money! Balance: {bbux}{post['money']}")
                return
            options = ['color'] * 8 +  ['banner'] * 10 + ['apron'] * 7 + ['extinguisher'] * 2 + ['exp'] * 5 + ['tm'] * 4 + ['money'] * 3 + ['fragment'] * 3
            ran_opt1 = rnd(options)
            ran_opt2 = rnd(options)
            both_opts = [ran_opt1, ran_opt2]
            opts_toprint = []
            for opt in both_opts:
                if opt == 'color':
                    owned_colors = {item['colour']['colour'] for item in post['inventory'] if 'colour' in item}
                    colors_f = {
                        rarity: [color for color in items.colours[rarity] if color['colour'] not in owned_colors]
                        for rarity in items.colours
                    }
                    rarity = 'uncommon'
                    chosen = rnd(colors_f[rarity])
                    chosen['rarity'] = rarity.capitalize()
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"colour": chosen}}})
                    opts_toprint.append(f"<:ColourIcon:659418340703469584> {chosen['colour']}")
                elif opt == 'banner':
                    owned_banners = {item['banner']['name'] for item in post['inventory'] if 'banner' in item}
                    banners_f = {
                        rarity: [banner for banner in items.banners[rarity] if banner['name'] not in owned_banners]
                        for rarity in ['common', 'uncommon', 'rare']
                    }
                    rr = ['uncommon'] * 4 + ['rare'] * 2
                    rarity = rnd(rr)
                    if not banners_f['rare']:
                        rarity = 'uncommon'
                    chosen = rnd(banners_f[rarity])
                    chosen['rarity'] = rarity.capitalize()
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"banner": chosen}}})
                    opts_toprint.append(f"<:BannerIcon:657457820295495699> {chosen['name']}")
                elif opt == 'tm':
                    opts_toprint.append(":clock: Time Machine")
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "tm"}}})
                elif opt == 'exp':
                    opts_toprint.append("<:ExperiencePotion:715822985780658238> Experience Potion")
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "ep"}}})
                elif opt == 'extinguisher':
                    opts_toprint.append(":fire_extinguisher: Fire Extinguisher")
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "fe"}}})
                elif opt == 'money':
                    rn_m = random.randint(100, 200)
                    opts_toprint.append(f"{bbux}{rn_m}")
                    await self.add_money(ctx.author.id, rn_m)
                elif opt == 'apron':
                    if 'apron_uses' in post:
                        uses = post['apron_uses']
                        opts_toprint.append("<:GoldenApron:1327865002559803452> +20 Golden Apron uses")
                        await db.market.update_one({"owner": ctx.author.id}, {"$inc": {"apron_uses": 20}})
                    else:
                        opts_toprint.append("<:GoldenApron:1327865002559803452> Golden Apron")
                        await db.market.update_one({"owner": ctx.author.id}, {"$set": {"apron_uses": 20}})
                elif opt == 'fragment':
                    frag = await self.add_rand_fragment(ctx.author.id)
                    if frag == 'agility': 
                        opts_toprint.append(f"<:AgilityFragment:1331502143760236574> Fragment of Agility")
                    elif frag == 'opportunity':
                        opts_toprint.append(f"<:OpportunityFragment:1331505178959937556> Fragment of Opportunity")
                    elif frag == 'endearing':
                        opts_toprint.append(f"<:EndearingFragment:1331823626080620574> Fragment of Endearing")
                    elif frag == 'ambience':
                        opts_toprint.append(f"<:AmbienceFragment:1331825947036483675> Fragment of Ambience")  
            embed_2 = discord.Embed(colour=0x8980d9, description="* "+"\n* ".join(opts_toprint))
            embed_2.set_thumbnail(url="https://media.discordapp.net/attachments/1325282246181130330/1332453341170765844/New_Piskel_50.png?ex=67954f60&is=6793fde0&hm=557c19c74ce95c28e58377a0bb62f4714c73eb9147edd14c2fd55c3106523ad5&=&format=webp&quality=lossless&width=1092&height=780")
            await ctx.send(embed=embed_2, content=f"{ctx.author.mention}, you opened an Uncommon Chest and received...")
            await msg.delete()
            try:
                await interaction.message.delete()
            except:
                pass
            
        ch_btn1 = Button(label="1", custom_id="chest_btn1", style=discord.ButtonStyle.primary)   
        ch_btn2 = Button(label="2", custom_id="chest_btn2", style=discord.ButtonStyle.primary)           

        ch_btn1.callback = lambda interaction: chest_cb1(interaction, msg)
        ch_btn2.callback = lambda interaction: chest_cb2(interaction, msg)

        view = View()
        view.add_item(ch_btn1)
        view.add_item(ch_btn2)
        msg = await ctx.send(embed=embed, view=view)
        

    @buy.command(aliases=['Item'])
    async def item(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        def nc(m):
            return m.author == ctx.message.author
        if post['level'] >= 2:
            uy = "<:BistroBux:1324936072760786964>100 "
        else:
            uy = ":lock: *Unlocks at Level 2*"
        embed = discord.Embed(colour=0x8980d9, title="Which item would you like to buy?", description=
        "**[1]   <:FishingRod:1333893065542336523> Fishing Rod -** <:BistroBux:1324936072760786964>60\n"\
        "Allows you to fish with the `b.fish` command (Chance of breaking with each use)\n"\
        "**[2]   <:FishingBoat:1333885562519814265> Fishing Boat -** <:BistroBux:1324936072760786964>150\n"\
        "You earn +25% EXP and +30% BB while fishing\n"\
        f"**[3]   <:ExperiencePotion:715822985780658238> Experience Potion -** {uy}\n"\
        "Gives you +50 EXP\n"\
        f"**[4]   <:TimeMachine:1333889857688436847> Time Machine -** {bbux}60\n"\
        "Allows you to reset all cooldowns (excl. daily & weekly)\n"\
        f"**[5]   <:GoldenApron:1327865002559803452> Golden Apron -** {bbux}180\n"\
        "Gives you +25% earnings on the work and trivia commands (20 uses)\n"
        f"**[6]   <:FireExtinguisher:1333891774472523888> Fire Extinguisher -** {bbux}45\n"\
        "Clears a kitchen fire"
        )
        embed.set_footer(text="You have 90 seconds to click a number below.")
        msg = None
        async def it_button_callback(interaction, option):
            await interaction.response.defer()
            if option == '1':
                if post['money'] < 60:
                    await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this.")
                else:
                    await ctx.send(f"{ctx.author.mention}, You bought a Fishing Rod! Do `b.fish` to use it.")
                    await self.take_money(user=ctx.author.id, count=60)
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "fish"}}})
            if option == '2':
                if post['money'] < 150:
                    await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this.")
                else:
                    if 'fishing_boat' in post['bonuses']:
                        await ctx.send("<:RedTick:653464977788895252> You already own a fishing boat!")
                    await ctx.send(f"{ctx.author.mention}, You bought a Fishing Boat! You will now earn +25% EXP and +30% {bbux} with the `b.fish` command.")
                    await self.take_money(user=ctx.author.id, count=150)
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"bonuses": "fishing_boat"}})
            elif option == '3':
                if post['money'] < 100:
                    await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this!")
                elif not post['level'] >= 2:
                    await ctx.send("<:RedTick:653464977788895252> You must be at least Level 2 to unlock this! For more information, send `b.level`.")
                else:
                    await ctx.send(f"{ctx.author.mention}, You bought an Experience Potion! Do `b.use Experience Potion` to use it.")
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "ep"}}})
                    await self.take_money(user=ctx.author.id, count=80)
            elif option == '4':
                if post['money'] < 60:
                    await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this!")
                else:
                    await self.take_money(user=ctx.author.id, count=85)
                    await ctx.send(f"{ctx.author.mention}, You bought a Time Machine! Do `b.use Time Machine` to use it.")
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "tm"}}})

            elif option == '5':
                if post['money'] < 180:
                    await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this!")
                else: 
                    if 'apron_uses' in post:
                        await self.take_money(user=ctx.author.id, count=180)
                        uses = post['apron_uses']
                        await ctx.send(f"{ctx.author.mention}, You have upgraded your Golden Apron! You now have {uses+20} uses.")
                        await db.market.update_one({"owner": ctx.author.id}, {"$set": {"apron_uses": uses+20}})
                    else:
                        await self.take_money(user=ctx.author.id, count=180)
                        await ctx.send(f"{ctx.author.mention}, You bought a Golden Apron! You can use this 20 times (`b.work` & `b.trivia` only).")
                        await db.market.update_one({"owner": ctx.author.id}, {"$set": {"apron_uses": 20}})
            elif option == '6':
                if post['money'] < 45:
                    await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this!")    
                else:
                    await self.take_money(user=ctx.author.id, count=45)
                    await ctx.send(f"{ctx.author.mention}, you bought a Fire Extinguisher! Use this with `b.use Fire Extinguisher`")        
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "fe"}}})
            if msg:
                await msg.delete()
            try:
                await interaction.message.delete()
            except:
                pass
        
        #kms
        opt1 = Button(label="1", custom_id="opt1", style=discord.ButtonStyle.primary)    
        opt2 = Button(label="2", custom_id="opt2", style=discord.ButtonStyle.primary) 
        opt3 = Button(label="3", custom_id="opt3", style=discord.ButtonStyle.primary) 
        opt4 = Button(label="4", custom_id="opt4", style=discord.ButtonStyle.primary) 
        opt5 = Button(label="5", custom_id="opt5", style=discord.ButtonStyle.primary) 
        opt6 = Button(label="6", custom_id="opt6", style=discord.ButtonStyle.primary)   
        
        if 'fishing_boat' in post['bonuses']:
            opt2.disabled = True   

        opt1.callback = lambda interaction: it_button_callback(interaction, '1')
        opt2.callback = lambda interaction: it_button_callback(interaction, '2')
        opt3.callback = lambda interaction: it_button_callback(interaction, '3')
        opt4.callback = lambda interaction: it_button_callback(interaction, '4')
        opt5.callback = lambda interaction: it_button_callback(interaction, '5')
        opt6.callback = lambda interaction: it_button_callback(interaction, '6')

        view = View()
        view.add_item(opt1)   
        view.add_item(opt2)   
        view.add_item(opt3)   
        view.add_item(opt4)   
        view.add_item(opt5)   
        view.add_item(opt6)   
    
        msg = await ctx.send(embed=embed, view=view)      
        
    @buy.command(aliases=['Custom'])
    async def custom(self, ctx):
        def nc(m):
            return m.author == ctx.message.author
        post = await db.market.find_one({"owner": ctx.author.id})
        if not 'colour' in post:
            await db.market.update_one({"owner": ctx.author.id}, {"$set":{"colour": None}})
            await db.market.update_one({"owner": ctx.author.id}, {"$set":{"banner": None}})
        else:
            pass
        embed = discord.Embed(colour=0x8980d9, title="Which chest would you like to buy?", description="**[1] <:CustomChest1:655981726077550615> Restaurant Color Chest** - <:BistroBux:1324936072760786964>200\n**[2] <:CustomChest2:655981738148888598> Restaurant Banner Chest** - <:BistroBux:1324936072760786964>300")
        embed.set_footer(text="You have 90 seconds to choose a number.")
        t_msg = None
        async def rcb_callback(interaction, choice):
            await interaction.response.defer()
            if choice == 1:
                if post['money'] < 200:
                    await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this.")
                else:
                    await self.take_money(ctx.author.id, 200)
                    owned_colors = {item['colour']['colour'] for item in post['inventory'] if 'colour' in item}
                    colors_f = {
                        rarity: [color for color in items.colours[rarity] if color['colour'] not in owned_colors]
                        for rarity in items.colours
                    }
                    rn = random.randint(1,3)
                    if not colors_f['common']:
                        rn = 1
                    if not rn == 1:
                        chosen = rnd(colors_f['common'])
                        chosen['rarity'] = "Common"
                        await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"colour": chosen}}})
                        embed = discord.Embed(colour=0x8980d9, description=f"{chosen['colour']} (Common)")
                        embed.set_thumbnail(url="http://pixelartmaker.com/art/5dd01d7e459201b.png")
                        embed.set_footer(text=f"Do b.inventory to check your inventory, or b.use {chosen['colour']} to use it.")
                        await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Colour Chest and received...')
                    else:
                        chosen = rnd(colors_f['uncommon'])
                        chosen['rarity'] = "Uncommon"
                        await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"colour": chosen}}})
                        embed = discord.Embed(colour=0x8980d9, description=f"{chosen['colour']} (Uncommon)")
                        embed.set_thumbnail(url="http://pixelartmaker.com/art/5dd01d7e459201b.png")
                        embed.set_footer(text=f"do b.inventory to check your inventory, or b.use {chosen['colour']} to use it.")
                        await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Colour Chest and received...')
            elif choice == 2:
                    if post['money'] < 300:
                        await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this.")
                    else:
                        await self.take_money(ctx.author.id, 300)
                        owned_banners = {item['banner']['name'] for item in post['inventory'] if 'banner' in item}
                        banners_f = {
                            rarity: [banner for banner in items.banners[rarity] if banner['name'] not in owned_banners]
                            for rarity in ['common', 'uncommon', 'rare']
                        }
                        rn = ['common'] * 6 + ['uncommon'] * 3 + ['rare']
                        cr = rnd(rn)
                        if cr == 'common':
                            chosen = rnd(banners_f['common'])
                            chosen['rarity'] = "Common"
                            await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"banner": chosen}}})
                            embed = discord.Embed(colour=0x8980d9, description=f"{chosen['name']} (Common) [View banner]({chosen['url']})")
                            embed.set_thumbnail(url="http://pixelartmaker.com/art/34fc7859370d585.png")
                            embed.set_footer(text=f"do b.inventory to check your inventory, or b.use {chosen['name']} to use it.")
                            await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Banner Chest and received...')
                        elif cr == 'uncommon':
                            chosen = rnd(banners_f['uncommon'])
                            chosen['rarity'] = "Common"
                            await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"banner": chosen}}})
                            embed = discord.Embed(colour=0x8980d9, description=f"{chosen['name']} (Uncommon) [View banner]({chosen['url']})")
                            embed.set_thumbnail(url="http://pixelartmaker.com/art/34fc7859370d585.png")
                            embed.set_footer(text=f"do b.inventory to check your inventory, or b.use {chosen['name']} to use it.")
                            await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Banner Chest and received...')
                        elif cr == 'rare':
                            chosen = rnd(banners_f['rare'])
                            chosen['rarity'] = "Rare"
                            await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"banner": chosen}}})
                            embed = discord.Embed(colour=0x8980d9, description=f"{chosen['name']} (Rare) [View banner]({chosen['url']})")
                            embed.set_thumbnail(url="http://pixelartmaker.com/art/34fc7859370d585.png")
                            embed.set_footer(text=f"do b.inventory to check your inventory, or b.use {chosen['name']} to use it.")
                            await ctx.send(embed=embed, content=f'{ctx.author.mention}, you opened a Profile Banner Chest and received...')
                        else:
                            pass 
            if t_msg:
                await t_msg.delete()
            try:
                await interaction.message.delete()
            except:
                pass 
                        
        btn1 = Button(label="1", custom_id="chc1", style=discord.ButtonStyle.primary)
        btn2 = Button(label="2", custom_id="chc2", style=discord.ButtonStyle.primary)       


        btn1.callback = lambda interaction: rcb_callback(interaction, 1)
        btn2.callback = lambda interaction: rcb_callback(interaction, 2)

        view = View()
        view.add_item(btn1)
        view.add_item(btn2)
        t_msg = await ctx.send(embed=embed, view=view)
                    

    @buy.command(aliases=['Food'])
    async def food(self, ctx):
        def nc(m):
            return m.author == ctx.message.author
        post = await db.market.find_one({"owner": ctx.author.id})
        embed = discord.Embed(colour=0x8980d9, title="Which food item would you like to add to your menu?")
        embed.set_footer(text="Click the button below to buy the item")
        desc = ""
        n = []
        items = []
        no_items = False
        country = post['country']
        #for x in post['items']:
         #   items.append(x['name'])
        filtered = [item for item in extra.extra[country] if item not in post['items']]
        for i, x in enumerate(filtered):
            if i == 0:
                n.append({str(i):x})
                sp = x['price']
                desc += f"**Next Item**:\n{x['name']} | Selling Price: {sp}\n\n"
            else:
                n.append({str(i):x})
                sp = x['price']
                desc += f"* {x['name']} | Selling Price: {sp}\n"
        if not n:
            desc = "*No more extra menu items to buy...*"
        embed.description = f"Each menu item costs <:BistroBux:1324936072760786964>500. You must buy them in the order.\n\n{desc}"
        food_msg = None
        async def buy_callback(interaction):
            await interaction.response.defer(ephemeral=True)
            name = n[0]['0']['name']
            await self.take_money(ctx.author.id, 500)
            await db.market.update_one({"owner": ctx.author.id}, {"$push": {"items":n[0]['0']}})
            await interaction.followup.send(f'{ctx.author.mention}, Item **{name}** was added to your menu.', ephemeral=True)
            if food_msg:
                await food_msg.delete()
            try:
                await interaction.message.delete()
            except:
                pass
            
        buybtn = Button(label="Buy Next Item", custom_id="buy_btn", style=discord.ButtonStyle.primary)
        buybtn.callback = buy_callback
        view = View()
        view.add_item(buybtn) 
        if post['money'] < 500 or not n:
            buybtn.disabled = True
        food_msg = await ctx.send(embed=embed, view=view)
                

    @commands.group(aliases=['settings', 'Set', 'Settings'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def set(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(colour=0x8980d9, title="'Set' Command Group", description="`b.set logo` - **Set Restaurant logo**\n`b.set notifications` - **Set notifications for your Restaurant**\n`b.set description` - **Set Restaurant description**\n`b.set name` - **Set Restaurant name**\n`b.set special` - **Set your specialty item**\n`b.set item` - **Set your custom item (Level 3+)**\n`b.set dine` - **Set your dine message (Level 5+)**\n`b.set banner` - **Set a custom banner (Level 6+)**")
            await ctx.send(embed=embed)
            self.bot.get_command("set").reset_cooldown(ctx)
            
    @set.command(aliases=['Special'])
    async def special(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        if not post:
           await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Do `b.start` to start one.") 
        view = self.DropdownView(ctx, post, cog=self)
        embed = discord.Embed(colour=0x8980d9, description="Select a food item to set it as your special:")
        msg = await ctx.send(embed=embed, view=view)

    @set.command(aliases=['Notifications', 'notifs'])
    async def notifications(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        if not 'notifications' in post:
            await db.market.update_one({"owner": ctx.author.id}, {"$set": {"notifications": True}})
            await ctx.send("<:CheckMark:1330789181470937139> Notifications turned on.")
        else:
            if post['notifications'] == False:
                await db.market.update_one({"owner": ctx.author.id}, {"$set": {"notifications": True}})
                await ctx.send("<:CheckMark:1330789181470937139> Notifications turned on.")
            elif post['notifications'] == True:
                await db.market.update_one({"owner": ctx.author.id}, {"$set": {"notifications": False}})
                await ctx.send("<:CheckMark:1330789181470937139> Notifications turned off.")
            else:
                pass

    @set.command(aliases=['dinemessage', 'Dine'])
    async def dine(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        def check(m):
                return m.author == ctx.message.author
        if post['level'] < 5:
            await ctx.send("<:RedTick:653464977788895252> You must be level 5 or higher to set a custom item!")
        else:
            embed = discord.Embed(colour=0x8980d9, description='What are you going to set your custom dine message? You must include COST and ITEM in your message, and it must be 200 characters or less.\n\nExample: `You\'ve ordered ITEM for <:BistroBux:1324936072760786964>COST! Have a good day!`')
            embed.set_author(icon_url=ctx.bot.user.avatar.url, name="Custom Item Creation")
            embed.set_footer(text="You have 90 seconds to reply")
            await ctx.send(embed=embed)
            msg = await self.bot.wait_for('message', check=check, timeout=90)
            dine = msg.content
            newmsg = dine.replace("nigg", "n*gg").replace("fag", "f*g").replace("fuck", "f*ck").replace("penis", "p*nis").replace("vagin", "v*gin")
            if len(newmsg) > 200:
                failed = discord.Embed(colour=0x8980d9, description="Dine messages must be 200 characters or less")
                failed.set_author(name="Creation Failed.")
                await ctx.send(embed=failed)
            elif not "COST" in newmsg or not "ITEM" in newmsg:
                failed = discord.Embed(colour=0x8980d9, description="You must include both COST and ITEM in your message! This makes the user know what they bought and how much it was!\n\nYou input: You bought a ITEM for <:BistroBux:1324936072760786964>COST!\nDine message: You bought a Pizza for <:BistroBux:1324936072760786964>5!")
                failed.set_author(name="Creation Failed.")
                await ctx.send(embed=failed)
            else:
                embed = discord.Embed(colour=0x8980d9, description=f'Perfect! Your dine message has been set!')
                embed.set_author(icon_url=ctx.bot.user.avatar.url, name="Custom Item Creation")
                await ctx.send(embed=embed)
                await db.market.update_one({"owner": ctx.author.id}, {"$set": {"dinemsg": newmsg}})

    @set.command(name="item", aliases=['custom', 'customitem', 'Item'])
    async def _item(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        def check(m):
                return m.author == ctx.message.author
        if "customitem" in post:
            await ctx.send("<:RedTick:653464977788895252> You have already created your custom item!")
        elif post['level'] < 3:
            await ctx.send("<:RedTick:653464977788895252> You must be level 3 or higher to set a custom item!")
        else:
            embed = discord.Embed(colour=0x8980d9, description='What are you going to name your custom item? It cannot be longer than 14 characters.')
            embed.set_author(icon_url=ctx.bot.user.avatar.url, name="Custom Item Creation")
            embed.set_footer(text="You have 90 seconds to reply")
            await ctx.send(embed=embed)
            msg = await self.bot.wait_for('message', check=check, timeout=90)
            item = msg.content
            newitem = item.lower().replace("nigg", "n*gg").replace("fag", "f*g").replace("fuck", "f*ck").replace("penis", "p*nis").replace("vagin", "v*gin")
            string = []
            for x in newitem.split(' '):
                string.append(x.capitalize())
            newitem = " ".join(string)
            if len(newitem) > 14:
                failed = discord.Embed(colour=0x8980d9, description="Item name must be 14 characters or less")
                failed.set_author(name="Creation Failed.")
                await ctx.send(embed=failed)
            else:
                embed = discord.Embed(colour=0x8980d9, description=f'Perfect! How much should "{newitem}" cost? It must be between <:BistroBux:1324936072760786964>1 and <:BistroBux:1324936072760786964>10')
                embed.set_author(icon_url=ctx.bot.user.avatar.url, name="Custom Item Creation")
                embed.set_footer(text="You have 90 seconds to reply")
                await ctx.send(embed=embed)
                msg = await self.bot.wait_for('message', check=check, timeout=90)
                price = int(msg.content)
                if price > 10 or price < 1:
                    failed = discord.Embed(colour=0x8980d9, description="Item cost must be between <:BistroBux:1324936072760786964>1 and <:BistroBux:1324936072760786964>10!")
                    failed.set_author(name="Creation Failed.")
                    await ctx.send(embed=failed)
                else:
                    embed = discord.Embed(colour=0x8980d9, description=f'Awesome! Menu item, "{newitem}", has been added to your menu!')
                    embed.set_author(icon_url=ctx.bot.user.avatar.url, name="Custom Item Creation")
                    await ctx.send(embed=embed)
                    await db.market.update_one({"owner": ctx.author.id}, {"$push":{"items": {"name": newitem, "price": price, "stock": 0, "sold": 0}}})
                    await db.market.update_one({"owner": ctx.author.id}, {"$set": {"customitem": True}})



    @set.command(aliases=['Logo', 'image', 'icon'])
    async def logo(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        def react(reaction, user):
            return user != ctx.me and str(reaction.emoji) == '✅' or str(reaction.emoji) == '❎'
        def nc(m):
            return m.author == ctx.message.author
        embed = discord.Embed(colour=0x8980d9, description="To keep NSFW off of Restaurant Bot, staff members must review every logo.\n\nReply with the image URL for your logo.")
        embed.set_footer(text="You have 90 seconds to reply")
        msg = await ctx.send(embed=embed)
        link = await self.bot.wait_for('message', check=nc, timeout=90)
        try:
            await link.delete()
        except:
            pass
        if link.content.startswith('http') and link.content.endswith('.jpg') or link.content.startswith('http') and link.content.endswith('.png') or link.content.startswith('http') and link.content.endswith('.jpeg') or link.content.startswith('http') and link.content.endswith('.gif'):
            embed = discord.Embed(colour=0x8980d9, description="Perfect! Your image has been sent to the Restaurant Bot staff team for reviewal.\n\n This process may take up to 24 hours. But don't worry, it will probably be even quicker.")
            embed.set_footer(text="Too many NSFW requests can end up in a ban from Restaurant Bot!")
            await msg.edit(embed=embed)

            se = discord.Embed(description=link.content)
            se2 = discord.Embed()
            se.set_footer(icon_url=ctx.author.avatar.url, text=f"{ctx.author} | {ctx.author.id}")
            se.set_thumbnail(url=link.content)
            se2.set_footer(icon_url=ctx.author.avatar.url, text=f"{ctx.author} | {ctx.author.id}")
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
                await db.market.update_one({"owner": ctx.author.id}, {"$set":{"logo_url": link.content}})
                await self.get_award(ctx.author.id, "logo_approved")
            else:
                se2.description = '*Logo denied*'
                await sem.edit(embed=se2)
                await ctx.author.send("Your logo has been denied.")
        else:
            embed = discord.Embed(colour=0x8980d9, description="That is not a valid link. It must end with `.png`, `.jpg`, `.jpeg`, or `.gif`.")
            embed.set_author(name="Failed.")
            await msg.edit(embed=embed)

    @set.command(aliases=['Banner'])
    async def banner(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        patrons = await db.utility.find_one({'utility': 'patrons'})
        def react(reaction, user):
            return user != ctx.me and str(reaction.emoji) == '✅' or str(reaction.emoji) == '❎'
        def nc(m):
            return m.author == ctx.message.author
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `b.start`.")
        else:
            if post['level'] > 5 or patrons and any(patrons.get(key) and ctx.author.id in patrons[key] for key in ['silver', 'gold', 'diamond']):
                embed = discord.Embed(colour=0x8980d9, description="To keep NSFW off of Restaurant Bot, staff members must review every banner.\n\nReply with the image URL for your banner.")
                embed.set_footer(text="You have 90 seconds to reply")
                msg = await ctx.send(embed=embed)
                link = await self.bot.wait_for('message', check=nc, timeout=90)
                try:
                    await link.delete()
                except:
                    pass
                ctx.typing()
                embed = discord.Embed(colour=0x8980d9)
                embed.set_footer(text="Loading...")
                await msg.edit(embed=embed)
                ar = await self.get_image_dimensions(link.content)
                if not ar:
                    embed = discord.Embed(colour=0x8980d9, description="The image should have an aspect ratio between 3:1 and 7:1. ")
                    embed.set_author(name="Failed.")
                    await msg.edit(embed=embed)
                else: 
                    if ar == 0:
                        embed = discord.Embed(colour=0x8980d9, description="That is not a valid link, I was unable to insert it. ")
                        embed.set_author(name="Failed.")
                        await msg.edit(embed=embed)
                    elif not 3 <= ar <= 7:
                        embed = discord.Embed(colour=0x8980d9, description="The image should have an aspect ratio between 3:1 and 7:1. ")
                        embed.set_author(name="Failed.")
                        await msg.edit(embed=embed)
                    else:
                        embed = discord.Embed(colour=0x8980d9, description="Perfect! Your image has been sent to the Restaurant Bot staff team for reviewal.\n\n This process may take up to 24 hours. But don't worry, it will probably be even quicker.")
                        embed.set_footer(text="Too many inappropriate requests can end up in a ban from Restaurant Bot!")
                        await msg.edit(embed=embed)

                        se = discord.Embed(description=link.content)
                        se2 = discord.Embed()
                        se.set_footer(icon_url=ctx.author.avatar.url, text=f"{ctx.author} | {ctx.author.id}")
                        se.set_thumbnail(url=link.content)
                        se2.set_footer(icon_url=ctx.author.avatar.url, text=f"{ctx.author} | {ctx.author.id}")
                        se2.set_thumbnail(url=link.content)
                        sem = await self.bot.get_channel(650994466307571714).send(embed=se)
                        await sem.add_reaction('✅')
                        await sem.add_reaction('❎')
                        await asyncio.sleep(2)
                        reaction, user = await self.bot.wait_for('reaction_add', check=react)
                        if reaction.emoji == '✅':
                            se2.description = '*Banner accepted*'
                            await sem.edit(embed=se2)
                            await ctx.author.send("Your logo has been accepted!")
                            await db.market.update_one({"owner": ctx.author.id}, {"$set":{"logo_url": link.content}})
                            await self.get_award(ctx.author.id, "set_banner")
                        else:
                            se2.description = '*Banner denied*'
                            await sem.edit(embed=se2)
                            await ctx.author.send("**Your logo has been denied.** Our reviewers are not very strict, so this could have been an error! If you believe so, visit our support server: https://discord.gg/BCRtw7c")
            else:
                await ctx.send("Your restaurant must be at least level 6 to set a custom banner. You can purchase a set one with `r!buy custom`.")


    @set.command(aliases=['Description', 'desc'])
    async def description(self, ctx):
        def nc(m):
            return m.author == ctx.message.author
        embed = discord.Embed(colour=0x8980d9, description="Descriptions must me 130 characters or less.\n\nReply with your desired description.")
        embed.set_footer(text="You have 90 seconds to reply")
        msg = await ctx.send(embed=embed)
        desc = await self.bot.wait_for('message', check=nc, timeout=90)
        try:
            await desc.delete()
        except:
            pass
        if len(desc.content) > 130:
            embed = discord.Embed(colour=0x8980d9, description="Description is more than 130 characters.")
            embed.set_author(name="Failed.")
            await msg.edit(embed=embed)
        else:
            embed = discord.Embed(colour=0x8980d9, description="Great! Your restaurant's description has been set!")
            await msg.edit(embed=embed)
            desc_stripped = str(desc.content).replace('nigg','n*gg').replace('Nigg','N*gg').replace('NIGG','N*GG').replace("fag", "f*g").replace("Fag", "F*g").replace("FAG", "F*G")
            await db.market.update_one({"owner": ctx.author.id}, {"$set":{"description": desc_stripped}})

    @set.command(aliases=['Name'])
    async def name(self, ctx):
        def nc(m):
            return m.author == ctx.message.author
        post = await db.market.find_one({"owner": int(ctx.author.id)})
        if post:
            embed = discord.Embed(colour=0x8980d9, description="Names must me 36 characters or less.\n\nReply with your desired name.")
            embed.set_footer(text="You have 90 seconds to reply")
            msg = await ctx.send(embed=embed)
            name = await self.bot.wait_for('message', check=nc, timeout=90)
            try:
                await name.delete()
            except:
                pass
            if len(name.content) > 130:
                embed = discord.Embed(colour=0x8980d9, description="Name is more than 36 characters.")
                embed.set_author(name="Failed.")
                await msg.edit(embed=embed)
            else:
                embed = discord.Embed(colour=0x8980d9, description="Awesome! Your restaurant's name has been set!")
                await msg.edit(embed=embed)
                new_name = str(name.content).replace('nigg','n*gg').replace('Nigg','N*gg').replace('NIGG','N*GG')
                await db.market.update_one({"owner": ctx.author.id}, {"$set":{"name": new_name}})
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `b.start`.")

    @set.command(aliases=['Stock'])
    @commands.is_owner()
    async def stock(self, ctx):
        # not gonna use
        def nc(m):
            return m.author == ctx.message.author
        post = await db.market.find_one({"owner": int(ctx.author.id)})
        embed = discord.Embed(colour=0x8980d9, description="What item would you like to stock?\n\nType all to stock all items.")
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
            embed = discord.Embed(colour=0x8980d9, description=f"That item is not on your menu. Check it with `b.menu {post['name']}`")
            embed.set_author(name="Failed.")
            await msg.edit(embed=embed)
        else:
            if it['price'] < 4:
                sp = it['price'] - 1
            elif it['price'] < 6:
                sp = it['price'] - 2
            else:
                sp = it['price'] - 3
            embed = discord.Embed(colour=0x8980d9, description=f"How many would you like to stock?\n\nStocking this item once would cost you <:BistroBux:1324936072760786964>{sp}.")
            await msg.edit(embed=embed)
            #await db.market.update_one({"owner": ctx.author.id}, {"$set":{"name": name.content}})
            price = await self.bot.wait_for('message', check=nc, timeout=90)
            try:
                await price.delete()
            except:
                pass
            if not price.content.isdigit() or int(price.content) > 45 or int(price.content) < 1:
                embed = discord.Embed(colour=0x8980d9, description=f"Prices may not be less than <:BistroBux:1324936072760786964>1 or more than <:BistroBux:1324936072760786964>45")
                embed.set_author(name="Failed.")
                await msg.edit(embed=embed)
            else:
                embed = discord.Embed(colour=0x8980d9, description="Amazing! The price has been set.")
                await msg.edit(embed=embed)
                await db.market.update_one({"owner": ctx.author.id}, {"$pull":{"items": it}})
                await db.market.update_one({"owner": ctx.author.id}, {"$push":{"items":{"name": it['name'],"price": int(price.content),"stock": it['stock'],"sold": it['sold']}}})

    @commands.command(aliases=['Random', 'rr'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def random(self, ctx, user:discord.User=None):
        if not user:
            user = ctx.author
        rn_count = await db.market.count_documents({})
        rndm = random.randint(1, rn_count)
        try:
            p = await db.market.find().limit(2).skip(rndm).next()
            if p['owner'] == ctx.author.id:
                if rn_count == rndm:
                    post = await db.market.find().limit(1).skip(rndm-1).next()
                else:
                    post = await db.market.find().limit(1).skip(rndm+1).next()
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
            embed.add_field(name=":notepad_spiral: Menu", value=post['items'][0]['name'] + ", " + post['items'][1]['name'] + ", " + post['items'][2]['name'] + f"... To view the full menu, do `b.menu {post['name']}`")
            embed.add_field(name=":bar_chart: Experience", value=format(post['exp'], ",d"))
            #embed.add_field(name=":chart_with_upwards_trend: Most Sold item", value=list[0]['name'])
            embed.add_field(name=":moneybag: Average Price", value="<:BistroBux:1324936072760786964>" + str(average))
            embed.add_field(name=":page_with_curl: Rating", value=stars)
            embed.add_field(name=":name_badge: Owner", value=str(self.bot.get_user(post['owner'])).replace("None", "Unknown"))
            if not post['logo_url']:
                embed.set_thumbnail(url=ctx.bot.user.avatar.url)
            else:
                embed.set_thumbnail(url=post['logo_url'])
            embed.set_footer(text=f"Random Restaurant | Last Stock: {post['laststock']}")
            msg = await ctx.send(embed=embed)
            await msg.add_reaction('❤')

    @commands.command(aliases=['Slots', 'slot'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def slots(self, ctx, bet:int = None):
        await ctx.typing()
        posts = await db.market.find_one({"owner": ctx.author.id})
        patrons = await db.utility.find_one({"utility": "patrons"})
        if not posts:
            await ctx.send("<:RedTick:653464977788895252> You do not have a restaurant! Start one with `b.start`")
        if patrons and any(patrons.get(key) and ctx.author.id in patrons[key] for key in ['silver', 'gold', 'diamond']):
            posts = await db.market.find_one({"owner": ctx.author.id})
            if bet == None:
                await ctx.send('<:RedTick:653464977788895252> Please provide your bet with the command. Example: `b.slots 50`')
            elif not int(posts['money']) >= int(bet) or int(posts['money']) == int(bet):
                await ctx.send('<:RedTick:653464977788895252> You don\'t have enough money.')
            elif int(bet) < 20:
                await ctx.send('<:RedTick:653464977788895252> Your bet must be above <:BistroBux:1324936072760786964>20.')
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
                        won = bet*5
                        slot1 = discord.Embed(colour=0x8980d9, description=f"JACKPOT! You've won <:BistroBux:1324936072760786964>{won}!\n\n{d}   {e}   {f} ` `\n{a}   {b}   {c} `<`\n{g}   {h}   {i} ` `")
                    else:
                        won = bet*2
                        slot1 = discord.Embed(colour=0x8980d9, description=f"Amazing! You've won <:BistroBux:1324936072760786964>{won}!\n\n{d}   {e}   {f} ` `\n{a}   {b}   {c} `<`\n{g}   {h}   {i} ` `")
                    await ctx.send(embed=slot1, content=f"{ctx.author.mention}, you've used some of your Restaurant income on a slot machine...")
                    await self.add_money(user=ctx.author.id, count=won, check_tasks=True)
                elif a == b or a == c or b == c:
                    won = bet*2
                    slot2 = discord.Embed(colour=0x8980d9, description=f"Nice! You've won <:BistroBux:1324936072760786964>{won}!\n\n{d}   {e}   {f} ` `\n{a}   {b}   {c} `<`\n{g}   {h}   {i} ` `")
                    await ctx.send(embed=slot2, content=f"{ctx.author.mention}, you've used some of your Restaurant income on a slot machine...")
                    await self.add_money(user=ctx.author.id, count=won, check_tasks=True)
                else:
                    if a in fruits and b in fruits and c in fruits:
                        won = bet*2
                        slot2 = discord.Embed(colour=0x8980d9, description=f"Fruit Bonanza! You've won <:BistroBux:1324936072760786964>{won}!\n\n{d}   {e}   {f} ` `\n{a}   {b}   {c} `<`\n{g}   {h}   {i} ` `")
                        await ctx.send(embed=slot2, content=f"{ctx.author.mention}, you used some of your Restaurant income on a slot machine...")
                        await self.add_money(user=ctx.author.id, count=won, check_tasks=True)
                    else:
                        slot3 = discord.Embed(colour=0x8980d9, description=f"Aw! You didn't win anything.\n\n{d}   {e}   {f} ` `\n{a}   {b}   {c} `<`\n{g}   {h}   {i} ` `")
                        await ctx.send(embed=slot3, content=f"{ctx.author.mention}, you used some of your Restaurant income on a slot machine...")
                        await self.take_money(user=ctx.author.id, count=bet)
        else:
            await ctx.send("<:RedTick:653464977788895252> You must be a patron to use this command! Do `b.donation` for more info.")

    @commands.command(aliases=['Clean'])
    async def clean(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `b.start`.")
            return
        if 'agility' in post['stones']:
            cd_sec = 130
        else:
            cd_sec = 95
        on_cd, remaining = await self.dynamic_cd(ctx.author.id, "clean", cd_sec)
        if on_cd:
            c_min = int(remaining) // 60
            c_sec = int(remaining) % 60
            m_l = "m "
            if not c_min:
                c_min = ""
                m_l = ""
            await ctx.send(f"<:RedTick:653464977788895252> You are on cooldown! Please wait **{c_min}{m_l}{c_sec}s**.")
            return
        to_clean = [{'name': 'sink', 'exp': 6}, {'name': 'oven', 'exp': 12}, {'name': 'counters', 'exp': 16}, {'name': 'floors', 'exp': 18}, {'name': 'bathrooms', 'exp': 22}, {'name': 'kitchen', 'exp': 26}]
        rn = rnd(to_clean)
        count = await self.add_exp(user=ctx.author.id, count=rn['exp'])
        await ctx.send(f"{ctx.author.mention}, You cleaned the {rn['name']} and earned {count} EXP.")
        if "clean_onefifty" in post['tasks']:
            user = post
            ix = user['tasks'].index("clean_onefifty")
            if user['task_list'][ix]['completed']+1 == user['task_list'][ix]['total']:
                await ctx.author.send(f"You have completed the **{user['task_list'][ix]['description']}** task. You have been awarded **{user['task_list'][ix]['rewards']} EXP**.")
                await self.add_exp(user=ctx.author.id, count=user['task_list'][ix]['rewards'], multiplier=False)
                await db.market.update_one({"owner": ctx.author.id, "task_list.name": "clean_onefifty"},{"$inc": {"task_list.$.completed": 1}})
            else:
                await db.market.update_one({"owner": ctx.author.id, "task_list.name": "clean_onefifty"},{"$inc": {"task_list.$.completed": 1}})

    @commands.command(aliases=['Fish'])
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def fish(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        to_fish = [{'name': 'a bag of sugar', 'money': 4, 'exp': 10}, {'name': 'some eggs', 'money': 3, 'exp': 8}, {'name': 'a fish', 'money': 11, 'exp': 19}, {'name': 'a bag of rice', 'money': 3, 'exp': 21}, {'name': 'a bag of potatoes', 'money': 6, 'exp': 12}, {'name': 'an apple', 'money': 7, 'exp': 20}, {'name': 'two bags of carrots', 'money': 8, 'exp': 24}, {'name': 'a bag of flour', 'money': 4, 'exp': 18}, {'name': 'a can of salt', 'money': 7, 'exp': 16}, {'name': 'a worm', 'money': 2, 'exp': 3}, {'name': 'a candy wrapper', 'money': 2, 'exp': 12}, {'name': 'a bag of onions', 'money': 9, 'exp': 14}]
        if post:
            fish = False
            item = None
            pole_broke = False
            luck = post['luck']
            for x in post['inventory']:
                if 'item' in x:
                    if x['item'] == 'fish':
                        fish = True
                        item = x
                    else:
                        pass
                else:
                    pass
            if not fish:
                await ctx.send("You don't have a fishing rod. Buy one by saying `b.buy item` and then clicking `1`.")
                self.bot.get_command("fish").reset_cooldown(ctx)
            else:
                if random.randint(1, 17) == 1:
                    frag = await self.add_rand_fragment(ctx.author.id)
                    if not frag:
                        await self.add_money(ctx.author.id, 120, check_tasks=True)
                        embed = discord.Embed(color=0x81d1e3, description=f"{ctx.author.mention}, You threw your fishing rod out and received {bbux}120!")
                        embed.set_thumbnail(url="https://i.ibb.co/Ps5Rny2k/Fishing-Rod-Sm-1.png")
                        await ctx.send(embed=embed)
                    else:
                        if frag == 'agility':
                            emoji = '<:AgilityFragment:1331502143760236574>'
                        elif frag == 'opportunity':
                            emoji = '<:OpportunityFragment:1331505178959937556>'
                        elif frag == 'endearing':
                            emoji = '<:EndearingFragment:1331823626080620574>'
                        elif frag == 'ambience':
                            emoji = '<:AmbienceFragment:1331825947036483675>'
                        embed2 = discord.Embed(color=0x81d1e3, description=f"{ctx.author.mention}, you threw your fishing rod out and received a {emoji} **Fragment of {frag.capitalize()}**!")
                        embed2.set_thumbnail(url="https://i.ibb.co/Ps5Rny2k/Fishing-Rod-Sm-1.png")
                        await ctx.send(embed=embed2)
                else:
                    rn = rnd(to_fish)
                    money = rn['money']
                    exp = rn['exp']
                    if 'fishing_boat' in post['bonuses']:
                        money*=1.3
                        exp*=1.25
                        money = round(money)
                        exp = round(exp)
                    await self.add_exp(user=ctx.author.id, count=exp)
                    await self.add_money(user=ctx.author.id, count=money, check_tasks=True)
                    if luck == 2:
                        rn2 = random.randint(1, 9)
                    if luck == 3:
                        rn2 = random.randint(1, 11)
                    if luck == 4:
                        rn2 = random.randint(1, 12)
                    if luck == 5:
                        rn2 = random.randint(1, 13)
                    if luck == 6:
                        rn2 = random.randint(1, 15)
                    if luck == 7:
                        rn2 = random.randint(1, 16)    
                    if luck >= 8:
                        rn2 = random.randint(1, 18)       
                    else:
                        rn2 = random.randint(1, 7)
                    if rn2 == 1:
                        bmsg = "\n\n**Unfortunately, your rod broke after you reeled in your rewards.**"
                        db.market.update_one({"owner": ctx.author.id}, {"$pull": {"inventory": item}})
                        award = await self.get_award(ctx.author.id, "broken_pole")
                        pole_broke = True
                    else:
                        bmsg = ""
                    embed = discord.Embed(color=0x81d1e3, description=f"{ctx.author.mention}, You threw your fishing rod out and got **{rn['name']}** which earned you <:BistroBux:1324936072760786964>{money} & {exp} EXP. {bmsg}")
                    embed.set_thumbnail(url="https://i.ibb.co/Ps5Rny2k/Fishing-Rod-Sm-1.png")
                    await ctx.send(embed=embed)   
                    if pole_broke:
                        if award:
                            await ctx.send(f"Even though you broke your fishing pole, you received the {awards.awards["broken_pole"]["emoji"]} **Sad Fisherman** award! View awards with `b.awards`")
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `b.start`.")

    @commands.command(aliases=['Cook', 'Bake', 'bake'])
    #@commands.cooldown(1, 90, commands.BucketType.user)
    async def cook(self, ctx):
        def nc(m):
            return m.author == ctx.author and m.channel == ctx.channel and not m.content.startswith("r!menu")
        post = await db.market.find_one({"owner": ctx.author.id})
        rating = 5
        rn = rnd([1,2])
        if post['luck'] == 2:     
            fire_chance = random.randint(1, 5)
        elif post['luck'] == 3:
            fire_chance = random.randint(1, 7)
        elif post['luck'] == 4:
            fire_chance = random.randint(1, 10)
        elif post['luck'] == 5:
            fire_chance = random.randint(1, 12)
        elif post['luck'] == 6:
            fire_chance = random.randint(1, 14)
        elif post['luck'] == 7:
            fire_chance = random.randint(1, 16)
        elif post['luck'] > 7:
            fire_chance = random.randint(1, 20)
        else:
            fire_chance = random.randint(1, 4)
        if post:
            if post['chef'] == 'm':
                cd_sec = 80
            elif post['chef'] == 'w':
                cd_sec = 60
            else:
                cd_sec = 100
            on_cd, remaining = await self.dynamic_cd(ctx.author.id, "cook", cd_sec)
            if on_cd:
                await ctx.send(f"<:RedTick:653464977788895252> You are on cooldown! Please wait **{int(remaining)} seconds**.")
                return
            if rn == 1:
                country = post['country']
                flist = None
                for c in food.can_burn:
                    if country in c:
                        flist = c
                word = rnd(flist[country])
                if word.endswith("s"):
                    ltr_a = ""
                else:
                    ltr_a = " a"
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
                resp = await self.bot.wait_for('message', check=nc, timeout=120)
                a = time.perf_counter()
                tt = a-b
                chance_of_fire = False
                retry_allowed = True
                if tt < 6:
                    if resp.content.lower().lower() == word.lower():
                        c = await self.add_exp(user=ctx.author.id, count=27)
                        await ctx.send(f"Perfect! You made{ltr_a} delicious **{na}** in {round(tt)} seconds! You've earned **{c} EXP**.")
                        rating = 5
                    else:
                        if retry_allowed and 'opportunity' in post['stones']:
                            await ctx.send(f"You failed to unscramble the letter, but you have the <:OpportunityStone:1331504493015076914> **Opportunity Stone**! One more chance, what is `{sw}`?")
                            resp2 = await self.bot.wait_for('message', check=nc, timeout=120)
                            if resp2.content.lower() == word.lower():
                                c = await self.add_exp(user=ctx.author.id, count=7)
                                await ctx.send(f"I knew you could do it! You received **{c} EXP** for making{ltr_a} **{na}**.")
                            else:
                                c = await self.add_exp(user=ctx.author.id, count=2)
                                await ctx.send(f"Uh oh! You failed again to unscramble the letters. You've earned **{c}** EXP for making{ltr_a} bad **{na}**.")
                                rating = 3
                                chance_of_fire = True
                            return
                        c = await self.add_exp(user=ctx.author.id, count=2)
                        await ctx.send(f"Uh oh! You failed to unscramble the letters. You've earned **{c} EXP** for making{ltr_a} bad **{na}**.")
                        rating = 3
                        chance_of_fire = True
                elif tt < 8:
                    if resp.content.lower() == word.lower():
                        c = await self.add_exp(user=ctx.author.id, count=20)
                        await ctx.send(f"Amazing! You made{ltr_a} tasty **{na}** in {round(tt)} seconds! You've earned **{c} EXP**.")
                        rating = 5
                    else:
                        if retry_allowed and 'opportunity' in post['stones']:
                            await ctx.send(f"You failed to unscramble the letter, but you have the <:OpportunityStone:1331504493015076914> **Opportunity Stone**! One more chance, what is `{sw}`?")
                            resp2 = await self.bot.wait_for('message', check=nc, timeout=120)
                            if resp2.content.lower() == word.lower():
                                c = await self.add_exp(user=ctx.author.id, count=7)
                                await ctx.send(f"I knew you could do it! You received **{c} EXP** for making{ltr_a} **{na}**.")
                            else:
                                c = await self.add_exp(user=ctx.author.id, count=2)
                                await ctx.send(f"Uh oh! You failed again to unscramble the letters. You've earned **{c}** EXP for making{ltr_a} bad **{na}**.")
                                rating = 3
                                chance_of_fire = True
                            return
                        c = await self.add_exp(user=ctx.author.id, count=1)
                        await ctx.send(f"Uh oh! You failed to unscramble the letters. You've earned **{c} EXP** for making{ltr_a} terrible **{na}**.")
                        rating = 2
                        chance_of_fire = True
                elif tt < 10:
                    if resp.content.lower() == word.lower():
                        c = await self.add_exp(user=ctx.author.id, count=16)
                        await ctx.send(f"Great! You made{ltr_a} delicious **{na}** in {round(tt)} seconds! You've earned **{c}** EXP.")
                        rating = 5
                    else:
                        if retry_allowed and 'opportunity' in post['stones']:
                            await ctx.send(f"You failed to unscramble the letter, but you have the <:OpportunityStone:1331504493015076914> **Opportunity Stone**! One more chance, what is `{sw}`?")
                            resp2 = await self.bot.wait_for('message', check=nc, timeout=120)
                            if resp2.content.lower() == word.lower():
                                c = await self.add_exp(user=ctx.author.id, count=7)
                                await ctx.send(f"I knew you could do it! You received **{c} EXP** for making{ltr_a} **{na}**.")
                            else:
                                c = await self.add_exp(user=ctx.author.id, count=2)
                                await ctx.send(f"Uh oh! You failed again to unscramble the letters. You've earned **{c}** EXP for making{ltr_a} bad **{na}**.")
                                rating = 3
                                chance_of_fire = True
                            return
                        await ctx.send(f"Uh oh! You failed to unscramble the letters. You've earned **0 EXP** for making{ltr_a} disgusting {na}.")
                        rating = 1
                        chance_of_fire = True
                elif tt < 12:
                    if resp.content.lower() == word.lower():
                        c = await self.add_exp(user=ctx.author.id, count=14)
                        await ctx.send(f"Nice! You made{ltr_a} good **{na}** in {round(tt)} seconds! You've earned **{c} EXP**.")
                        rating = 4
                    else:
                        if retry_allowed and 'opportunity' in post['stones']:
                            await ctx.send(f"You failed to unscramble the letter, but you have the <:OpportunityStone:1331504493015076914> **Opportunity Stone**! One more chance, what is `{sw}`?")
                            resp2 = await self.bot.wait_for('message', check=nc, timeout=120)
                            if resp2.content.lower() == word.lower():
                                c = await self.add_exp(user=ctx.author.id, count=7)
                                await ctx.send(f"I knew you could do it! You received **{c} EXP** for making{ltr_a} **{na}**.")
                            else:
                                c = await self.add_exp(user=ctx.author.id, count=2)
                                await ctx.send(f"Uh oh! You failed again to unscramble the letters. You've earned **{c}** EXP for making{ltr_a} bad **{na}**.")
                                rating = 3
                                chance_of_fire = True
                            return
                        await ctx.send(f"Uh oh! You failed to unscramble the letters. You've earned **0 EXP** for making{ltr_a} disgusting **{na}**.")
                        rating = 1
                        chance_of_fire = True
                elif tt < 14:
                    if resp.content.lower() == word.lower():
                        c = await self.add_exp(user=ctx.author.id, count=8)
                        await ctx.send(f"OK! You made {ltr_a} not-too-bad **{na}** in {round(tt)} seconds! You've earned **{c} EXP**.")
                        rating = 4
                    else:
                        if retry_allowed and 'opportunity' in post['stones']:
                            await ctx.send(f"You failed to unscramble the letter, but you have the <:OpportunityStone:1331504493015076914> **Opportunity Stone**! One more chance, what is `{sw}`?")
                            resp2 = await self.bot.wait_for('message', check=nc, timeout=120)
                            if resp2.content.lower() == word.lower():
                                c = await self.add_exp(user=ctx.author.id, count=7)
                                await ctx.send(f"I knew you could do it! You received **{c} EXP** for making{ltr_a} **{na}**.")
                            else:
                                c = await self.add_exp(user=ctx.author.id, count=2)
                                await ctx.send(f"Uh oh! You failed again to unscramble the letters. You've earned **{c}** EXP for making{ltr_a} bad **{na}**.")
                                rating = 3
                                chance_of_fire = True
                            return
                        await ctx.send(f"Uh oh! You failed to unscramble the letters. You've earned **0 EXP** for making{ltr_a} disgusting {na}.")
                        rating = 1
                        chance_of_fire = True
                elif tt < 18:
                    if resp.content.lower() == word.lower():
                        c = await self.add_exp(user=ctx.author.id, count=6)
                        await ctx.send(f"Eh! You made {ltr_a} decent **{na}** in {round(tt)} seconds! You've earned **{c} EXP**.")
                        rating = 3
                    else:
                        await ctx.send(f"Uh oh! You failed to unscramble the letters. You've earned 0 EXP for making{ltr_a} disgusting {na}.")
                        rating = 1
                        chance_of_fire = True
                else:
                    chance_of_fire = True
                    if resp.content.lower() == word.lower():
                        c = await self.add_exp(user=ctx.author.id, count=1)
                        await ctx.send(f"Uh oh! You made {ltr_a} disgusting **{na}** in {round(tt)} seconds! You've earned **{c} EXP**.")
                        rating = 3
                    else:
                        if retry_allowed and 'opportunity' in post['stones']:
                            await ctx.send(f"You failed to unscramble the letter, but you have the <:OpportunityStone:1331504493015076914> **Opportunity Stone**! One more chance, what is `{sw}`?")
                            resp2 = await self.bot.wait_for('message', check=nc, timeout=120)
                            if resp2.content.lower() == word.lower():
                                c = await self.add_exp(user=ctx.author.id, count=7)
                                await ctx.send(f"I knew you could do it! You received **{c} EXP** for making{ltr_a} **{na}**.")
                            else:
                                c = await self.add_exp(user=ctx.author.id, count=2)
                                await ctx.send(f"Uh oh! You failed again to unscramble the letters. You've earned **{c}** EXP for making{ltr_a} bad **{na}**.")
                                rating = 3
                                chance_of_fire = True
                            return
                        await ctx.send(f"Uh oh! You failed to unscramble the letters. You've earned **0 EXP** for making{ltr_a} disgusting **{na}**.")
                        rating = 1
                if chance_of_fire:
                    if not "fire" in post['bonuses']:
                        if fire_chance == 1:
                            embed = discord.Embed(color=0xff1f1f, description=f":fire: **FIRE!** :fire:\n\nYou burnt the {na} so bad that it caused a kitchen fire! You will receive -40% EXP on all commands until you use a fire extinguisher!\n\nTo buy an extinguisher, do `b.buy item`")
                            db.market.update_one({"owner": ctx.author.id}, {"$push": {"bonuses": "fire"}})
                            await ctx.send(embed=embed)
                        
            else:
                chance_of_fire = False
                bar_int = 0
                country = post['country']
                flist = None
                for c in food.can_burn:
                    if country in c:
                        flist = c
                cfood = rnd(flist[country])
                if cfood.endswith("s"):
                    cfooda = "the " + cfood
                else:
                    if cfood.startswith(("a", "e", "i", "o", "u")):
                        cfooda = "an " + cfood
                    else:
                        cfooda = "a " + cfood

                done = False
                desc = f"Click `stop` when the bar gets to red. Don't burn it!\n\n`🟨`"
                embed = discord.Embed(description=desc)
                embed.set_footer(text=f"You're cooking {cfooda}.")

                button = Button(label="Stop", style=discord.ButtonStyle.red)
                view = View()
                view.add_item(button)

                async def button_callback(interaction):
                    nonlocal done, bar_int, bar
                    if interaction.user == ctx.author:
                        await interaction.response.defer()
                        done = True
                        if bar_int > 5:
                            embed.set_footer(text=None)
                            embed.description = f"You burnt **{cfooda}**! No EXP for you...\n\n{bar}"
                            embed.color = 0x000000
                            chance_of_fire = True
                            rating = 1
                        elif bar_int == 5:
                            embed.set_footer(text=None)
                            exp_r = await self.add_exp(user=ctx.author.id, count=23)
                            embed.description = f"You cooked **{cfooda}** perfectly! You received {exp_r} EXP!\n\n{bar}"
                            rating = 5
                        elif bar_int == 4:
                            embed.set_footer(text=None)
                            exp_r = await self.add_exp(user=ctx.author.id, count=15)
                            embed.description = f"You almost cooked **{cfooda}** perfectly. You received {exp_r} for the effort!\n\n{bar}"
                            rating = 4
                        else:
                            embed.set_footer(text=None)
                            exp_r = await self.add_exp(user=ctx.author.id, count=5)
                            embed.description = f"You undercooked **{cfooda}**! You received {exp_r} EXP for the effort!\n\n{bar}"
                            rating = 3
                        await interaction.edit_original_response(embed=embed, view=None)

                button.callback = button_callback
                await asyncio.sleep(1)
                msg = await ctx.send(embed=embed, view=view)
                while bar_int <= 6 and not done:
                    await asyncio.sleep(0.15)
                    bar_int += 1
                    bar = str(bar_int).replace("7", "`🟨🟨🟧🟧🟥⬛`").replace("6", "`🟨🟨🟧🟧🟥⬛`").replace("5", "`🟨🟨🟧🟧🟥`").replace("4", "`🟨🟨🟧🟧`").replace("3", "`🟨🟨🟧`").replace("2", "`🟨🟨`").replace("1", "`🟨`")
                    embed = discord.Embed(description=f"Click `stop` when the bar gets to red. Don't burn it!\n\n{bar}")
                    if bar_int == 7:
                        embed.set_footer(text=None)
                        embed.description = f"You burnt **{cfooda}**! No EXP for you...\n\n{bar}"
                        rating = 1
                        chance_of_fire = True
                        embed.color = 0x000000
                        done = True
                    elif bar_int > 5:
                        embed.color = 0x000000
                        embed.set_footer(text=f"You're burning the {cfood}!")
                    elif bar_int == 5:
                        embed.color = 0xfc2121
                    elif bar_int == 3 or bar_int == 4:
                        embed.color = 0xfa8c16
                    else:
                        embed.color = 0xf9ff40
                        embed.set_footer(text=f"You're cooking {cfooda}.")

                    await msg.edit(embed=embed)
                    await asyncio.sleep(0.6)
                if not done:
                    
                    embed.set_footer(text=None)
                    embed.description = f"You burnt **{cfooda}**! No EXP for you...\n\n{bar}"
                    embed.color = 0x000000
                    rating = 1
                    chance_of_fire = True
                    done = True

                await msg.edit(view=None)
                if chance_of_fire:
                    if not "fire" in post['bonuses']:
                        if fire_chance == 1:
                            embed = discord.Embed(color=0xff1f1f, description=f":fire: **FIRE!** :fire:\n\nYou burnt the {cfood} so bad that it caused a kitchen fire! You will receive -40% EXP on all commands until you use a fire extinguisher!\n\nTo buy an extinguisher, do `b.buy item`")
                            db.market.update_one({"owner": ctx.author.id}, {"$push": {"bonuses": "fire"}})
                            await ctx.send(embed=embed)
            await self.add_rating(user=ctx.author.id, rating=rating)
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `b.start`.")
            

    @commands.command(aliases=['Restaurant', 'r'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def restaurant(self, ctx, *, restaurant=None):
        await ctx.typing()
        post = None
        if not restaurant:
            post = await db.market.find_one({"owner":ctx.author.id})
        elif ctx.message.mentions:
            if len(ctx.message.mentions) >= 2:
                post = await db.market.find_one({"owner":ctx.message.mentions[1].id})
            else:
                post = await db.market.find_one({"owner":ctx.message.mentions[0].id})
        else:
            post = await db.market.find_one({"name":restaurant})
        if not post:
            await ctx.send('<:RedTick:653464977788895252> I couldn\'t find that restaurant in our database.')
        else:
            stones_ta = []
            for x in post['stones']:
                if x == 'agility':
                    stones_ta.append("<:AgilityStone:1331501018768347157>")
                elif x == 'opportunity':
                    stones_ta.append("<:OpportunityStone:1331504493015076914>")
                elif x == 'endearing':
                    stones_ta.append("<:EndearingStone:1331822694202871851>")
                elif x == 'ambience':
                    stones_ta.append("<:AmbienceStone:1331825641703604225>")
            event = await db.events.find_one({"user_id": post['owner']})
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
            patrons = await db.utility.find_one({"utility": "patrons"})
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
            fire_msg = ""
            if 'fire' in post['bonuses']:
                fire_msg = ":fire: **ON FIRE** :fire:\n"
            embed = discord.Embed(description=fire_msg+f"{" ".join(stones_ta)}\n{post['description']}\n\u200b")
            level = int(post['level'])
            owner = post['owner']
            perday = await self.calc_customers(owner)
            emoji = self.levelEmoji[str(level)]
            
            embed.set_author(icon_url=self.flags[country], name=post['name']) #+ f" {self.levelEmoji[level]}")
            #embed.add_field(name="Menu", value=post['items'][0]['name'] + ", " + post['items'][1]['name'] + ", " + post['items'][2]['name'] + f"... View the full menu with `b.menu {post['name']}`")
            embed.add_field(name="Rating", value=stars)
            if post['special']:
                embed.add_field(name="Specialty", value=post['special'])
            embed.add_field(name="Average Price", value="<:BistroBux:1324936072760786964>" + str(average))
            embed.add_field(name="Experience", value=format(post['exp'], ",d") + f" ({emoji})")
            embed.add_field(name="Customers", value=f"{post['customers']} ({perday}/day)")
            if post['awards']:
                award_emoji = []
                for award in post['awards']:
                    award_emoji.append(awards.awards[award]['emoji'])
                embed.add_field(name="Awards", value=" ".join(award_emoji))
            if event: 
                if event['type'] == 'tn':
                    e_desc = ":question: Trivia Night"
                elif event['type'] == 'kn':
                    e_desc = ":notes: Karaoke Night"
                elif event['type'] == 'ayce':
                    e_desc = ":meat_on_bone: All-You-Can-Eat"
                embed.add_field(name="ONGOING EVENT!", value=e_desc)
            
            #await ctx.send(f"id > {post['owner']}")
            embed.add_field(name="Owner", value=str(self.bot.get_user(owner)).replace("None", "Unknown") + badge)
            try:
                if post['banner']:
                    embed.set_image(url=post['banner'])
                else:
                    pass
                if post['colour']:
                    if post['colour'] == 0x171717:
                        embed.colour = random.randint(0, 0xFFFFFF)
                    else:
                        embed.colour = post['colour']
                else:
                    pass
            except:
                pass
            if not post['logo_url']:
                embed.set_thumbnail(url=ctx.bot.user.avatar.url)
            else:
                embed.set_thumbnail(url=post['logo_url'])
            embed.set_footer(text=f"Level {level} | Last Work: {post['laststock']}")
            view = self.ButtonView(self.bot, user_id=post['owner'], cog=self)
            msg = await ctx.send(embed=embed, view=view)

    @commands.command(aliases=['Level'])
    @commands.cooldown(1,3, commands.BucketType.user)
    async def level(self, ctx):
        user = await db.market.find_one({"owner": ctx.author.id})
        nextLevel = str(user['level']+1)
        if user['level'] != 15:
            cl = f"will level up to Level {nextLevel} next"
            a = True
        else:
            cl = f"cannot level up further"
            a = False
        embed = discord.Embed(colour=0x8980d9, description=f"{self.levelEmoji[str(user['level'])]} You are currently Level {user['level']}, which means you {cl}.\n\nBistro Levels are bought with EXP. The more you level up, the more the next level will cost. You get money and cool perks for leveling up! To level up, do `b.levelup`. Or if you want to see all the unlockables, do `b.levelunlocks`")
        embed.set_author(name="Bistro Leveling", icon_url=ctx.me.avatar.with_format('png'))
        if a:
            embed.set_footer(text=f"You need {self.exp_needed[nextLevel]} EXP to level up to {nextLevel}!")
        await ctx.send(embed=embed)

    @commands.command(aliases=['Levelunlocks', 'lvlunlocks'])
    @commands.cooldown(1,3, commands.BucketType.user)
    async def levelunlocks(self, ctx):
        description = "All Level Unlockables\n\n"
        for key, val in self.unlocks.items():
            emoji = self.levelEmoji[str(key)]
            exp = self.exp_needed[key]
            description += f"{emoji} **Level {key}** `{exp} EXP req.`\n{", ".join(val)}\n"
        embed = discord.Embed(colour=0x8980d9, description=description)
        await ctx.send(embed=embed)

    @commands.command(aliases=["Levelup", "LevelUp"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def levelup(self, ctx):
        user = await db.market.find_one({"owner": ctx.author.id})
        nextLevel = user['level']+1
        if not user:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `b.start`.")
        elif user['level'] >= 15:
            await ctx.send("<:RedTick:653464977788895252> You are currently level 15 (max level) and cannot level further.")
        elif user['exp'] < self.exp_needed[str(nextLevel)]:
            await ctx.send("<:RedTick:653464977788895252> You do not have enough EXP to perform this action! See your progression with `b.level`.")
        else:
            await self.take_exp(ctx.author.id, self.exp_needed[str(nextLevel)])   
            if nextLevel == 2:
                money = 100
                await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "ep"}}})
                await db.market.update_one({"owner": ctx.author.id}, {"$inc": {"luck": 1}})
            elif nextLevel == 3:
                money = 100
                await db.market.update_one({"owner": ctx.author.id}, {"$inc": {"luck": 1}})
            elif nextLevel == 5:
                money = 300
            elif nextLevel == 6:
                money = 100
                await db.market.update_one({"owner": ctx.author.id}, {"$inc": {"luck": 1}})
            elif nextLevel == 7:
                money = 500
            elif nextLevel == 8:
                money = 100
                await db.market.update_one({"owner": ctx.author.id}, {"$inc": {"luck": 1}})
            elif nextLevel == 9:
                money = 100
                frag = await self.add_rand_fragment(ctx.author.id, all=True)
            elif nextLevel == 10:
                money = 500
                await db.market.update_one({"owner": ctx.author.id}, {"$inc": {"apron_uses": 20}})
            elif nextLevel == 12:
                money = 100
                await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "tm"}}})
            elif nextLevel == 13:
                money = 100
                await db.market.update_one({"owner": ctx.author.id}, {"$inc": {"luck": 1}})
            elif nextLevel == 15:
                money = 500
                await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"item": "tm"}}})
            else:
                money = 100
                             
            await self.add_money(ctx.author.id, money)
            await ctx.typing()
            await asyncio.sleep(0.3)
            cl = user['level']
            unlocks = "\n* " + "\n* ".join(self.unlocks[str(nextLevel)])
            nextUnlocks = "* " + "\n* ".join(self.unlocks[str(nextLevel+1)])
            embed = discord.Embed(colour=0x8980d9, description=f"{self.levelEmoji[str(nextLevel)]} **Level up!** You've unlocked...\n{unlocks}")
            embed.add_field(name="Next Unlocks...", value=nextUnlocks)
            #embed.set_footer(text=f"You've also earned {money} BB for leveling up!")
            await ctx.send(embed=embed)
            await db.market.update_one({"owner": ctx.author.id}, {"$set":{"level": nextLevel}})
            if "levelup" in user['tasks']:
                ix = user['tasks'].index("levelup")
                if user['task_list'][ix]['completed']+1 == 1:
                    await ctx.author.send(f"You have completed the **{user['task_list'][ix]['description']}** task. You have been awarded **{user['task_list'][ix]['rewards']} EXP**.")
                    await self.add_exp(user=ctx.author.id, count=user['task_list'][ix]['rewards'], multiplier=False)
                    await db.market.update_one({"owner": ctx.author.id, "task_list.name": "levelup"},{"$set": {"task_list.$.completed": 1}})


    @commands.command(aliases=['Start', 'create'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def start(self, ctx):
        user = await db.market.find_one({"owner": ctx.author.id})
        if not user:
            def check(m):
                return m.author == ctx.message.author
            
            cancel_event = asyncio.Event()
            to_delete = None

            class CancelView(View):
                def __init__(self):
                    super().__init__()

                @discord.ui.button(label="X", style=discord.ButtonStyle.danger)
                async def cancel_button(self, interaction: discord.Interaction, button: Button):
                    if interaction.user == ctx.author and not button.disabled:
                        button.disabled = True
                        await interaction.response.send_message("Creation process canceled.", ephemeral=True)
                        cancel_event.set()
                        if to_delete:
                            await to_delete.delete()

            view = CancelView()
            
            embed = discord.Embed(colour=0x8980d9, description='Welcome to **Bistro**! First off, which **theme** would you like? Pick one from this list:\n\n'\
            ':cupcake: Bakery\n'\
            ':beers: Bar\n'\
            ':coffee: Cafe\n'\
            ':pizza: Pizzeria\n\n'\
            ':flag_br: Brazil\n'\
            ':flag_cn: China\n'\
            ':flag_fr: France\n'\
            ':flag_gr: Greece\n'\
            ':flag_in: India\n'\
            ':flag_it: Italy\n'\
            ':flag_jp: Japan\n'\
            ':flag_mx: Mexico\n'\
            ':flag_ru: Russia\n'\
            ':flag_sg: Singapore\n'\
            ':flag_kr: South Korea\n'\
            ':flag_tr: Turkey\n'\
            ':flag_gb: United Kingdom\n'\
            ':flag_us: United States\n'
            )
            embed.set_author(icon_url=ctx.bot.user.avatar.url, name="Restaurant Creation")
            embed.set_footer(text="You have 90 seconds to reply | You CANNOT change your theme later on!")
            msg1 = await ctx.send(embed=embed, view=view)
            country = await self.bot.wait_for('message', check=check, timeout=90)
            if cancel_event.is_set():
                to_delete = msg1
                return
            try:
                await country.delete()
            except:
                pass
            if not country.content.upper() in self.countries:
                failed = discord.Embed(colour=0xff0000, description="That is not in the list of countries.")
                failed.set_author(name="Creation Failed. Please try the command again.")
                await msg1.edit(embed=failed, view=None)
            else:
                embed = discord.Embed(colour=0x8980d9, description='Great! What would you like to **name** your restaurant? It must be 36 characters or less. You can change this later on!')
                embed.set_author(icon_url=ctx.bot.user.avatar.url, name="Restaurant Creation")
                embed.set_footer(text="You have 90 seconds to reply")
                ms1 = await msg1.edit(embed=embed, view=view)
                name = await self.bot.wait_for('message', check=check, timeout=90)
                if cancel_event.is_set():
                    to_delete = ms1
                    return
                try:
                    await name.delete()
                except:
                    pass
                if len(str(name.content)) > 36:
                    failed = discord.Embed(colour=0xff0000, description="Restaurant name must be 36 characters or less")
                    failed.set_author(name="Creation Failed. Please try the command again.")
                    msg1.edit(embed=failed, view=None)
                else:
                    embed = discord.Embed(colour=0x8980d9, description='Almost done! What would you like as your **description**? It must be 130 characters or less. You can change this later on!')
                    embed.set_author(icon_url=ctx.bot.user.avatar.url, name="Restaurant Creation")
                    embed.set_footer(text="You have 90 seconds to reply")
                    ms2 = await msg1.edit(embed=embed, view=view)
                    desc = await self.bot.wait_for('message', check=check, timeout=90)
                    if cancel_event.is_set():
                        to_delete = ms2
                        return
                    try:
                        await desc.delete()
                    except:
                        pass
                    if len(str(desc.content)) > 130:
                        failed = discord.Embed(colour=0xff0000, description="Restaurant description must be 130 characters or less")
                        failed.set_author(name="Creation Failed. Please try the command again.")
                        await msg1.edit(embed=failed, view=None)
                    else:
                        new_name = str(name.content).replace('nigg','n*gg').replace('Nigg','N*gg').replace('NIGG','N*GG').replace('fag', 'f*g').replace('FAG', 'f*g').replace("Fag", "F*g")
                        await self.update_data(ctx.author, country.content.lower(), new_name, desc.content)
                        embed = discord.Embed(colour=0x8980d9, description=f'And... Done! Your Restaurant has been created. \n\nCheck your restaurant out with `{self.prefix}restaurant` and view all Restaurant commands with `b.help`.')
                        embed.add_field(name="Quick Tips", value=":one: [Earn some money](https://bistrobot.co/a/earn-money.mov)\n:two: [Set a custom logo](https://bistrobot.co/a/set-restaurant-logo.mov)\n:three: [Hire a worker](https://bistrobot.co/a/hire-worker.mov)\n:four: [Buy a custom item and use it](https://bistrobot.co/a/use-item.mov)\n:five: [Level up your Restaurant](https://docs.google.com/document/d/1sTv9vN3TucTGx8rmRHw6FDfTvJ_TWJN7vVitqrqDLP0/edit?usp=sharing)\n\n:file_folder: [Documentation](https://bistrobot.co/documentation)\n:grey_question: [FAQ](https://bistrobot.co/faq)")
                        embed.set_author(icon_url=ctx.bot.user.avatar.url, name="Restaurant Creation")
                        await msg1.edit(embed=embed, view=None)
        else:
            await ctx.send(f'<:RedTick:653464977788895252> You already have a restaurant created. View it with `b.restaurant`.')

    @commands.command(aliases=['Tasks', 'challenges', 'quests'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def tasks(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You do not have a restaurant! Start one with `b.start`")
            return
        if not 'tasks' in post or post['tasks'] == []:
            ms = await ctx.send("Setting your challenges. Please wait...")
            await ctx.typing()
            t1 = random.choice(quests.questlist1)
            t2 = random.choice(quests.questlist2)
            t3 = random.choice(quests.questlist3)
            await db.market.update_one({"owner": ctx.author.id}, {"$set": {"task_list": [t1, t2, t3]}})
            await db.market.update_one({"owner": ctx.author.id}, {"$set": {"tasks": [t1['name'], t2['name'], t3['name']]}})
            await asyncio.sleep(2)
            await ms.delete()
        post = await db.market.find_one({"owner": ctx.author.id})
        task1 = post['task_list'][0]
        task2 = post['task_list'][1]
        task3 = post['task_list'][2]
        progress_1 = task1['completed']/task1['total']
        if progress_1 >= 1:
            bar1 = '<:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764>'
        elif progress_1 >= 0.8:
            bar1 = '<:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764><:blacksq:829872214899556392>'
        elif progress_1 >= 0.6:
            bar1 = '<:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764><:blacksq:829872214899556392><:blacksq:829872214899556392>'
        elif progress_1 >= 0.4:
            bar1 = '<:greensq:829870925583089764><:greensq:829870925583089764><:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392>'
        elif progress_1 >= 0.2:
            bar1 = '<:greensq:829870925583089764><:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392>'
        else:
            bar1 = '<:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392>'
        progress_2 = task2['completed']/1
        if progress_2 == 1:
            bar2 = '<:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764>'
        else:
            bar2 = '<:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392>'
        progress_3 = task3['completed']/task3['total']
        if progress_3 >= 1:
            bar3 = '<:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764>'
        elif progress_3 >= 0.8:
            bar3 = '<:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764><:blacksq:829872214899556392>'
        elif progress_3 >= 0.6:
            bar3 = '<:greensq:829870925583089764><:greensq:829870925583089764><:greensq:829870925583089764><:blacksq:829872214899556392><:blacksq:829872214899556392>'
        elif progress_3 >= 0.4:
            bar3 = '<:greensq:829870925583089764><:greensq:829870925583089764><:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392>'
        elif progress_3 >= 0.2:
            bar3 = '<:greensq:829870925583089764><:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392>'
        else:
            bar3 = '<:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392><:blacksq:829872214899556392>'
            
        if task1['completed'] >= task1['total']:
            task1_comp = 'Completed'
        else:
            task1_comp = f"{task1['completed']}/{task1['total']}"
        if task2['completed'] == 1:
            task2_comp = 'Completed'
        else:
            task2_comp = "0/1"
        if task3['completed'] >= task3['total']:
            task3_comp = "Completed"
        else:
            task3_comp = f"{task3['completed']}/{task3['total']}"
        embed=discord.Embed(colour=0x8980d9, description=f"**{task1['description']}**\n{bar1} *({task1_comp})* `{task1['rewards']} EXP`"\
        f"\n**{task2['description']}**\n{bar2} *({task2_comp})* <:BistroBux:1324936072760786964>`{task2['rewards']}`"\
        f"\n**{task3['description']}**\n{bar3} *({task3_comp})* <:BistroBux:1324936072760786964>`{task3['rewards']}`")
        embed.set_author(name="Weekly Tasks", icon_url=ctx.author.avatar.url)
        embed.set_footer(text="Tasks reset weekly.")
        await ctx.send(embed=embed)
        
    async def dynamic_cd(self, user, cmd, cd_time):
        result = await db.cooldowns.find_one({"user_id": user, "command_name": cmd})
        if result:
            expires_at = result["expires_at"]
            if dttm.utcnow() < expires_at:
                remaining_time = (expires_at - dttm.utcnow()).total_seconds()
                return True, remaining_time
        expires_at = dttm.utcnow() + timedelta(seconds=cd_time)
        await db.cooldowns.update_one(
            {"user_id": user, "command_name": cmd},
            {"$set": {"expires_at": expires_at}},
            upsert=True
        )
        return False, None

    
    async def get_image_dimensions(self, url:str):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            img = Image.open(response.raw)
            width, height = img.size
            ar = width / height
            return ar
        except:
            return 0

    async def get_award(self, user, award):
        post = await db.market.find_one({"owner": user})
        has_award = False
        added = False
        for x in post['awards']:
            if x == award:
                has_award = True
        if not has_award:
            await db.market.update_one({"owner": user}, {"$push": {"awards": award}})
            added = True
        return added

    async def luck_up(self, user:int):
        data = await db.market.find_one({"owner": user})
        new_lvl = data['luck'] + 1
        await db.market.update_one({"owner": user}, {"$set":{"luck": new_lvl}})


    async def add_money(self, user:int, count, check_tasks=False):
        data = await db.market.find_one({"owner": user})
        bal = data['money']
        money = int(bal) + count
        await db.market.update_one({"owner": user}, {"$set":{"money": money}})
        if data['money'] >= 500 and not 'fivehundred_bbux' in data['awards']:
            award = await self.get_award(user, "fivehundred_bbux")
        elif data['money'] >= 1500 and not 'thousand_bbux' in data['awards']:
            award = await self.get_award(user, "thousand_bbux")
        elif data['money'] >= 3000 and not 'twothousand_bbux' in data['awards']:
            award = await self.get_award(user, "twothousand_bbux")
        if check_tasks:
            if "earn_money" in data['tasks']:
                ix = data['tasks'].index("earn_money")
                if data['task_list'][ix]['completed']+count >= data['task_list'][ix]['total']:
                    await ctx.author.send(f"You have completed the **{data['task_list'][ix]['description']}** task. You have been awarded {bbux}**{data['task_list'][ix]['rewards']}**.")
                    await db.market.update_one({"owner": user}, {"$inc":{"money": data['task_list'][ix]['rewards']}})
                    await db.market.update_one({"owner": user}, {"$pull":{"tasks": "earn_money"}})
                    await db.market.update_one({"owner": user, "task_list.name": "earn_money"},{"$inc": {"task_list.$.completed": count}})
                else:
                    await db.market.update_one({"owner": user, "task_list.name": "earn_money"},{"$inc": {"task_list.$.completed": count}})

    async def take_money(self, user:int, count:int):
        data = await db.market.find_one({"owner": user})
        bal = data['money']
        money = int(bal) - count
        await db.market.update_one({"owner": user}, {"$set":{"money": money}})

    async def add_exp(self, user, count, check_tasks=False):
        data = await db.market.find_one({"owner": user})
        bal = data['exp']
        if 'worker' in data:
            if data['worker']:
                wn = data['worker_name']
                count = count + round(count*data['worker'][wn][0]['exp'])
        if 'fire' in data['bonuses']:
            count = count - round(count*0.4)
        exp = int(bal) + count
        await db.market.update_one({"owner": user}, {"$set":{"exp": exp}})
        await db.market.update_one({"owner": user}, {"$inc":{"total_exp": count}})
        return count
        if check_tasks:
            if "earn_exp" in data['tasks']:
                ix = data['tasks'].index("earn_exp")
                if data['task_list'][ix]['completed']+count >= data['task_list'][ix]['total']:
                    await ctx.author.send(f"You have completed the **{data['task_list'][ix]['description']}** task. You have been awarded {bbux}**{data['task_list'][ix]['rewards']}**.")
                    await db.market.update_one({"owner": user}, {"$inc":{"money": data['task_list'][ix]['rewards']}})
                    await db.market.update_one({"owner": user}, {"$pull":{"tasks": "earn_exp"}})
                    await db.market.update_one({"owner": user, "task_list.name": "earn_exp"},{"$inc": {"task_list.$.completed": count}})
                else:
                    await db.market.update_one({"owner": user, "task_list.name": "earn_exp"},{"$inc": {"task_list.$.completed": count}})

    async def take_exp(self, user, count):
        data = await db.market.find_one({"owner": user})
        bal = data['exp']
        exp = int(bal) - count
        await db.market.update_one({"owner": user}, {"$set":{"exp": exp}})
        return count

    async def add_rating(self, user, rating):
        post = await db.market.find_one({"owner": user})
        if 'endearing' in post['stones']:
            if rating < 5:
                rating += 1
        await db.market.update_one({"owner": user}, {"$push":{"ratings": {"rating": rating, "user": 1}}})
        
    async def add_rand_fragment(self, user, all=False):
        post = await db.market.find_one({"owner": user})
        fragments = ['agility', 'opportunity', 'endearing', 'ambience']
        exclude = post['stones']
        if all: 
            for fragment in fragments:
                if fragment in exclude: 
                    continue
                in_list = False
                for frag in post['fragments']:
                    if frag['stone'] == fragment:
                        await db.market.update_one({"owner": user, "fragments.stone": fragment},{"$inc": {"fragments.$.count": 1}})
                        in_list = True
                        break
                if not in_list:
                    await db.market.update_one({"owner": user}, {"$push": {"fragments": {"stone": fragment, "count": 1}}})
            return True
        
        for x in exclude:
            if x in fragments:
                fragments.remove(x)
        if not fragments:
            return None
        fragment = rnd(fragments)
        in_list = False
        for frag in post['fragments']:
            if fragment == frag['stone']:
                await db.market.update_one({"owner": user, "fragments.stone": fragment}, {"$inc": {"fragments.$.count": 1}})
                in_list = True
                break
        if not in_list:
            await db.market.update_one({"owner": user}, {"$push": {"fragments": {"stone": fragment, "count": 1}}})
        return fragment

    async def calc_customers(self, user):
        data = await db.market.find_one({"owner": user})
        customers = data['customers']
        ratings = []
        for rating in data['ratings']:
            ratings.append(rating['rating'])
        avr = round(sum(ratings)/len(ratings))
        count = avr * 10
        count += data['level'] * 20
        if data['advert']:
            if data['advert'] == "social_media":
                count += 30
            elif data['advert'] == "web_ad":
                count += 60
            elif data['advert'] == "tv_media":
                count += 100
            elif data['advert'] == "billboard":
                count += 125
        if data['level'] > 8:
            count +=50
        if data['level'] > 10:
            count +=50
        if 'endearing' in data['stones']:
            n_c = round(count*1.13)
            count = n_c
        if data['customers'] >= 500 and not 'fivehundred_customers' in data['awards']:
            award = await self.get_award(user, "fivehundred_customers")
        elif data['customers'] >= 1500 and not 'fifteenhundred_customers' in data['awards']:
            award = await self.get_award(user, "fifteenhundred_customers")
        elif data['customers'] >= 3000 and not 'threethousand_customers' in data['awards']:
            award = await self.get_award(user, "threethousand_customers")
        elif data['customers'] >= 5000 and not 'fivethousand_customers' in data['awards']:
            award = await self.get_award(user, "fivethousand_customers")
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
            "customers_per_day": 0,
            "laststock": "Has not worked yet.",
            "id":id,
            "logo_url": None,
            "banner": None,
            "ratings":[{"rating":5, "user":0}],
            "exp":0,
            "total_exp": 0,
            "level": 1,
            "luck": 1,
            "inventory":[],
            "colour": None,
            "banner": None,
            "worker": None,
            "worker_name": None,
            "chef": None,
            "notifications": False,
            "task_list": [],
            "tasks": [],
            "tasks_completed": 0,
            "awards": [],
            "customers_per_day": 0,
            "bonuses": [],
            "advert": None,
            "special": None,
            "stones": [],
            "fragments": []

        }
        await db.market.insert_one(post)
        
    class ButtonView(discord.ui.View):
        def __init__(self, bot, user_id, cog):
            super().__init__(timeout=60)
            self.bot = bot
            self.user_id = user_id
            self.cog = cog

        @discord.ui.button(label="📃 Menu", style=discord.ButtonStyle.secondary)
        async def button_callback(self, interac: discord.Interaction, button: discord.ui.Button):
            try:
                await interac.response.defer()
                post = await db.market.find_one({"owner": self.user_id})
                if not post:
                    await interac.followup.send("Error getting menu info.", ephemeral=True)
                    return
                clr = post.get('colour', 0x8980d9)
                embed = discord.Embed(color=clr)
                country = str(post['country'])
                embed.set_author(icon_url=self.cog.flags.get(country, ''), name=f"{post['name']}'s Menu")
                desc = ""
                for x in post['items']:
                    desc += f"{x['name']} | <:BistroBux:1324936072760786964>{x['price']} | {x['sold']} Sold\n"#| {x['stock']} in Stock
                embed.description = desc
                if post['colour']:
                    if post['colour'] == 0x171717:
                        embed.colour = random.randint(0, 0xFFFFFF)
                    else:
                        embed.colour = post['colour']
                await interac.followup.send(embed=embed)
            except Exception as e:
                print(dir(interac), interac)
                error = getattr(e, 'original', e)
                error_message = traceback.format_exc()
                e = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=False))
                print(e)
                
    class SpecialDropdown(discord.ui.Select):
        def __init__(self, ctx, post):
            options = []
            self.ctx = ctx
            for x in post['items']:
                options.append(discord.SelectOption(label=x['name']))
            super().__init__(placeholder="Choose an special item...", max_values=1, min_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            if self.ctx.author.id == interaction.user.id:
                await interaction.response.send_message(f"<:CheckMark:1330789181470937139> **{self.values[0]}** has been selected as your restaurant special.", ephemeral=True)
                await db.market.update_one({"owner": interaction.user.id}, {"$set": {"special": self.values[0]}})
                await interaction.message.delete()
                try: 
                    await self.ctx.message.delete()
                except:
                    pass

    class DropdownView(discord.ui.View):
        def __init__(self, ctx, post, cog):
            super().__init__()
            self.add_item(cog.SpecialDropdown(ctx, post))
            

async def setup(bot):
    await bot.add_cog(Shop(bot))
