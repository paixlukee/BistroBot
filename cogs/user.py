import discord
from discord.ext import commands, tasks
import datetime
from datetime import timedelta, datetime as dttm
import random
import math
import time
from discord.ext.commands import errors, converter
from random import randint, choice as rnd
import aiohttp
import asyncio
import json
import os
import responses
from pytz import timezone, utc
import pytz
import config
from pymongo import MongoClient, ASCENDING
import pymongo
import string
from food import food
import requests
import motor.motor_asyncio
import trivia
import awards
import songs 
from discord.ui import View, Button


client = motor.motor_asyncio.AsyncIOMotorClient(config.mongo_client)
db = client['siri']

db.events.create_index([("expireAt", 1)], expireAfterSeconds=0)


bbux = "<:BistroBux:1324936072760786964>"


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = 'b.'

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 748162782586994728 and not message.author.id == 648065060559781889:
            await asyncio.sleep(0.5)
            await message.delete()

    @commands.command(aliases=['User', 'Profile', 'profile'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def user(self, ctx, user:discord.User=None):
        if not user:
            user = ctx.author
        post = await db.market.find_one({"owner": int(user.id)})
        if post:
            embed = discord.Embed(colour=0x8980d9, description=str(user))
            if post['colour']:
                if post['colour'] == 0x171717:
                    embed.colour = random.randint(0, 0xFFFFFF)
                else:
                    embed.colour = post['colour']
            embed.set_author(icon_url=user.avatar.url, name="User Stats")
            embed.set_thumbnail(url=user.avatar.url)
            if post['banner']:
                embed.set_image(url=post['banner'])
            embed.add_field(name="Restaurant", value=post['name'] + f" (Level {post['level']})")
            embed.add_field(name="Money", value="<:BistroBux:1324936072760786964>" + str(post['money']))
            embed.add_field(name="Luck", value=f"LVL {post['luck']}")
            embed.set_footer(text=f"User ID: {post['id']}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("<:RedTick:653464977788895252> This user doesn't have a restaurant")

    @commands.command(aliases=['Balance', 'bal'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def balance(self, ctx, user:discord.User=None):
        if not user:
            user = ctx.author
        post = await db.market.find_one({"owner": int(user.id)})
        if post:
            bal = format(post['money'], ",d")
            await ctx.send(f"**{user.name}**'s balance is **<:BistroBux:1324936072760786964>{bal}**.")
        else:
            await ctx.send("<:RedTick:653464977788895252> This user doesn't have a restaurant")

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def donate(self, ctx, user: discord.User=None, count:int=None):
        posts = await db.market.find_one({"owner": ctx.author.id})

        if ctx.author == user:
            await ctx.send("<:RedTick:653464977788895252> You cannot donate money to yourself!")

        elif not count or not user:
            await ctx.send("<:RedTick:653464977788895252> You must include both the user and the amount of money. Example: `b.donate @paixlukee 25`")

        elif count < 0:
            await ctx.send(f"<:RedTick:653464977788895252> You can't donate under **<:BistroBux:1324936072760786964>1**.")

        elif not posts['money'] >= count:
            await ctx.send(f"<:RedTick:653464977788895252> You don't have enough money.")


        elif posts:
            posts_user = await db.market.find_one({"owner": user.id})
            if not posts_user:
                await ctx.send(f"<:RedTick:653464977788895252> **{user.name}** doesn't have a restaurant.")
                return
            await self.add_money(user=user.id, count=count)
            await self.take_money(user=ctx.author.id, count=count)
            await ctx.send(f"{user.mention}, **{ctx.message.author}** has donated **<:BistroBux:1324936072760786964>{count}** to you.")
            if "donate_money" in posts['tasks']:
                user = posts
                ix = user['tasks'].index("donate_money")
                if user['task_list'][ix]['completed']+1 == 1:
                    await ctx.author.send(f"You have completed the **{user['task_list'][ix]['description']}** task. You have been awarded **{user['task_list'][ix]['rewards']} EXP**.")
                    await self.add_exp(user=ctx.author.id, count=user['task_list'][ix]['rewards'], multiplier=False)
                    await db.market.update_one({"owner": ctx.author.id, "task_list.name": "donate_money"},{"$set": {"task_list.$.completed": 1}})
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one by doing `b.start`.")

    @commands.command(pass_context=True, aliases=['Daily'])
    @commands.cooldown(1,86400, commands.BucketType.user)
    async def daily(self, ctx):
        posts = await db.market.find_one({"owner": ctx.author.id})
        patrons = await db.utility.find_one({"utility": "patrons"})
        if posts:
            ri = random.randint(1,6)
            rci = random.randint(60, 110)
            if ctx.author.id in patrons['bronze']:
                rci *= 1.2
                rci = round(rci)
            elif ctx.author.id in patrons['silver']:
                rci *= 1.4
                rci = round(rci)
            elif ctx.author.id in patrons['gold']:
                rci *= 1.6
                rci = round(rci)
            elif ctx.author.id in patrons['diamond']:
                rci *= 1.7
                rci = round(rci)
            if posts['worker']:
                rci -= 50
            if posts['chef']:
                if posts['chef'] == "m":
                    rci -= 20
                else:
                    rci -= 40
            if posts['customers'] > 2000:
                add_on = 150
            elif posts['customers'] > 1600:
                add_on = 120
            elif posts['customers'] > 800:
                add_on = 90
            elif posts['customers'] > 300:
                add_on = 40
            else:
                add_on = 30
            rci += add_on
            
            chest = [f'{rci} Cash']
            if random.randint(1,13) == 1:
                frag = await self.add_rand_fragment(ctx.author.id)
                if frag:
                    if frag == 'agility':
                        emoji = '<:AgilityFragment:1331502143760236574>'
                    elif frag == 'opportunity':
                        emoji = '<:OpportunityFragment:1331505178959937556>'
                    elif frag == 'endearing':
                        emoji = '<:EndearingFragment:1331823626080620574>'
                    elif frag == 'ambience':
                        emoji = '<:AmbienceFragment:1331825947036483675>'
                    embed = discord.Embed(colour=0x8980d9, description=f"* {emoji} Fragment of {frag.capitalize()}"+ "\n\nWant even more goodies? Upvote me on [Top.GG](https://top.gg/bot/657037653346222102/vote), and do `b.votereward` to receive another chest.")
                    embed.set_thumbnail(url="http://pixelartmaker.com/art/f6d46bd306aacfd.png")
                    embed.set_footer(text="Come back in 24 hours!")
                    if posts['colour']:
                        embed.colour = posts['colour']
                    await ctx.send(embed=embed, content=f"{ctx.author.mention}, you opened your daily chest and received...")                
                else:
                    await self.add_money(user=ctx.author.id, count=rci)
                    embed = discord.Embed(colour=0x8980d9, description="* "+"\n *".join(chest)+ "\n\nWant even more money? Upvote me on [Top.GG](https://top.gg/bot/657037653346222102/vote), and do `b.votereward` to receive another chest.")
                    embed.set_thumbnail(url="http://pixelartmaker.com/art/f6d46bd306aacfd.png")
                    embed.set_footer(text="Come back in 24 hours!")
                    if posts['colour']:
                        embed.colour = posts['colour']
                    await ctx.send(embed=embed, content=f"{ctx.author.mention}, you opened your daily chest and received...")
            else:
                try:
                    await self.add_money(user=ctx.author.id, count=rci)
                    embed = discord.Embed(colour=0x8980d9, description="* "+"\n *".join(chest)+ "\n\nWant even more money? Upvote me on [Top.GG](https://top.gg/bot/657037653346222102/vote), and do `b.votereward` to receive another chest.")
                    embed.set_thumbnail(url="http://pixelartmaker.com/art/f6d46bd306aacfd.png")
                    embed.set_footer(text="Come back in 24 hours!")
                    if posts['colour']:
                        embed.colour = posts['colour']
                    await ctx.send(embed=embed, content=f"{ctx.author.mention}, you opened your daily chest and received...")
                except:
                    await ctx.send("<:RedTick:653464977788895252> An unknown error has occurred! The cooldown has been lifted.")
                    self.bot.get_command("daily").reset_cooldown(ctx)
        else:
            await ctx.send("You don't have a restaurant. Create one by doing `b.start`.")

    @commands.command(aliases=['Inventory', 'inv'])
    async def inventory(self, ctx, page=1):
        post = await db.market.find_one({"owner": ctx.author.id})
        if post:
            embed = discord.Embed(colour=0x8980d9)
            embed.set_author(icon_url=ctx.author.avatar.url, name="Your Inventory")
            names = []
            items_per_page = 12
            pages = math.ceil(len(post['inventory']) / items_per_page)
            start = (page - 1) * items_per_page
            end = start + items_per_page
            for x in post['inventory'][start:end]:
                if 'colour' in x:
                    names.append(f"<:ColourIcon:659418340703469584> {x['colour']['colour']} ({x['colour']['rarity']})")
                elif 'banner' in x:
                    names.append(f"<:BannerIcon:657457820295495699> {x['banner']['name']} ({x['banner']['rarity']}) [[View]]({x['banner']['url']})")
                elif 'potion' in x:
                    names.append(f"<:CooldownPotion:715822985780658238> Cooldown Remover Potion (Uncommon)")
                elif 'item' in x:
                    if x['item'] == 'fish':
                        names.append(f":<:FishingRod:1333893065542336523> Fishing Rod (Common)")
                    elif x['item'] == 'ep':
                        names.append(f"<:ExperiencePotion:715822985780658238> Experience Potion (Common)")
                    elif x['item'] == 'tm':
                        names.append(f"<:TimeMachine:1333889857688436847> Time Machine (Common)")
                    elif x['item'] == 'fe':
                        names.append(f"<:FireExtinguisher:1333891774472523888> Fire Extinguisher (Common)")
                    elif x['item'] == 'ambience':
                        names.append("<:AmbienceStone:1331825641703604225> Stone of Ambience (Legendary)")
                else:
                    pass
            if names:
                embed.description = "\n".join(names)
            else:
                embed.description = "Nothing to see here."
            
            np = page + 1
            embed.set_footer(text=f"Page {page} of {pages}")
            
            # Pagination buttons
            prev_button = Button(label="←", custom_id="prev_page", style=discord.ButtonStyle.primary)
            next_button = Button(label="→", custom_id="next_page", style=discord.ButtonStyle.primary)
            
            if page == 1:
                prev_button.disabled = True
            if page == pages:
                next_button.disabled = True
            
            prev_button.callback = lambda interaction: self.inv_button_callback(interaction, ctx)
            next_button.callback = lambda interaction: self.inv_button_callback(interaction, ctx)

            view = View()
            view.add_item(prev_button)
            view.add_item(next_button)

            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send("You don't have a restaurant! Create one with `b.start`.")

    async def inv_button_callback(self, interaction, ctx):
        footer_text = interaction.message.embeds[0].footer.text
        current_page = int(footer_text.split("Page ")[1].split(" of")[0])

        if interaction.user != ctx.author:
            return
        
        if interaction.data['custom_id'] == 'next_page':
            await self.show_inventory_page(ctx, current_page + 1, interaction)
        elif interaction.data['custom_id'] == 'prev_page' and not current_page == 1:
            await self.show_inventory_page(ctx, current_page - 1, interaction)

    async def show_inventory_page(self, ctx, page, interaction):
        post = await db.market.find_one({"owner": ctx.author.id})
        if post:
            embed = discord.Embed(colour=0x8980d9)
            embed.set_author(icon_url=ctx.author.avatar.url, name="Your Inventory")
            names = []
            items_per_page = 12
            pages = math.ceil(len(post['inventory']) / items_per_page)
            start = (page - 1) * items_per_page
            end = start + items_per_page
            for x in post['inventory'][start:end]:
                if 'colour' in x:
                    names.append(f"<:ColourIcon:659418340703469584> {x['colour']['colour']} ({x['colour']['rarity']})")
                elif 'banner' in x:
                    names.append(f"<:BannerIcon:657457820295495699> {x['banner']['name']} ({x['banner']['rarity']}) [[View]]({x['banner']['url']})")
                elif 'potion' in x:
                    names.append(f"<:CooldownPotion:715822985780658238> Cooldown Remover Potion (Uncommon)")
                elif 'item' in x:
                    if x['item'] == 'fish':
                        names.append(f"<:FishingRod:1333893065542336523> Fishing Rod (Common)")
                    elif x['item'] == 'ep':
                        names.append(f"<:ExperiencePotion:715822985780658238> Experience Potion (Common)")
                    elif x['item'] == 'tm':
                        names.append(f"<:TimeMachine:1333889857688436847> Time Machine (Common)")
                    elif x['item'] == 'fe':
                        names.append(f"<:FireExtinguisher:1333891774472523888> Fire Extinguisher (Common)")
                    elif x['item'] == 'ambience':
                        names.append("<:AmbienceStone:1331825641703604225> Stone of Ambience (Legendary)")
                else:
                    pass
            if names:
                embed.description = "\n".join(names)
            else:
                embed.description = "Nothing to see here."

            embed.set_footer(text=f"Page {page} of {pages}")

            prev_button = Button(label="←", custom_id="prev_page", style=discord.ButtonStyle.primary)
            next_button = Button(label="→", custom_id="next_page", style=discord.ButtonStyle.primary)
            
            if page == 1:
                prev_button.disabled = True
            if page == pages:
                next_button.disabled = True

            prev_button.callback = lambda interaction: self.inv_button_callback(interaction, ctx)
            next_button.callback = lambda interaction: self.inv_button_callback(interaction, ctx)

            view = View()
            view.add_item(prev_button)
            view.add_item(next_button)

            await interaction.response.edit_message(embed=embed, view=view)


    @commands.command(aliases=['Dine', 'Eat', 'eat'])
    @commands.cooldown(1, 35, commands.BucketType.user)
    async def dine(self, ctx, *, restaurant=None):
        post = await db.market.find_one({"owner":ctx.author.id})
        def nc(m):
            return m.author == ctx.message.author
        if ctx.message.mentions:
            if len(ctx.message.mentions) >= 2:
                res = await db.market.find_one({"owner":ctx.message.mentions[0].id})
            else:
                res = await db.market.find_one({"owner":ctx.message.mentions[0].id})
        elif await db.market.find_one({"name": restaurant}):
            res = await db.market.find_one({"name": restaurant})
        else:
            res = None
        if not restaurant:
            self.bot.get_command("dine").reset_cooldown(ctx)
            await ctx.send("<:RedTick:653464977788895252> You didn't include a restaurant! Example: `b.dine @paixlukee` or `b.dine McDonalds`.")
        elif res['owner'] == ctx.author.id:
            self.bot.get_command("dine").reset_cooldown(ctx)
            await ctx.send("<:RedTick:653464977788895252> You can't dine in at your own restaurant.")
        elif res:
            items = []
            for x in res['items']:
                items.append(x['name'])
            li = ', '.join(items)
            embed = discord.Embed(colour=0x8980d9, description=f"Welcome to {res['name']}!\n\nWhich item would you like to order?\n\n**Menu**: {li}")
            embed.set_footer(text='You have 90 seconds to respond with a menu item.')
            cmsg = await ctx.send(embed=embed)
            chi = await self.bot.wait_for('message', check=nc, timeout=90)
            await cmsg.delete()
            try:
                await chi.delete()
            except:
                pass
            newi = []
            for x in res['items']:
                if x['name'] == chi.content or x['name'] == chi.content.title():
                    newi.append(x)
            if chi.content in items or chi.content.title() in items:
                item = newi[0]
                if post['money'] >= item['price']:
                    rxp = round(1.2*item['price'])
                    await self.take_money(ctx.author.id, item['price'])
                    c = await self.add_exp(ctx.author.id, rxp, check_tasks=True)
                    dEmbed = discord.Embed()
                    dEmbed.set_thumbnail(url=res['logo_url'])
                    dEmbed.set_footer(text="Enjoyed the service? Rate this restaurant with b.rate <@user>")
                    if post['colour']:
                        if post['colour'] == 0x171717:
                            dEmbed.colour = random.randint(0, 0xFFFFFF)
                        else:
                            dEmbed.colour = post['colour']
                    if "dinemsg" in res:
                        dinemsg = res['dinemsg'].replace("ITEM", item['name']).replace("COST", str(item['price']))
                        if dinemsg.endswith('.') or dinemsg.endswith('!') or dinemsg.endswith('?'):
                            p = ''
                        else:
                            p = '.'
                        dEmbed.description = f"{dinemsg}{p} You've earned {c} EXP for dining in."
                        await ctx.send(embed=dEmbed)
                    else:
                        dEmbed.description = f"You've ordered a {item['name']} from {res['name']} for <:BistroBux:1324936072760786964>{item['price']}. You've earned {c} EXP for dining in."
                        await ctx.send(embed=dEmbed)
                    price_paid = round(item['price']/1.8)
                    await self.add_money(res['owner'], round(item['price']/1.8))
                    await self.add_sold(res['owner'], item['name'])
                    current_customers = res['customers']
                    await db.market.update_one({"owner": res['owner']}, {"$set": {"customers": current_customers+1}})

                    if 'notifications' in res:
                        if res['notifications']:
                            if item['name'].startswith(("a", "e", "i", "o", "u")):
                                nn = "an " + item['name']
                            else:
                                nn = "a " + item['name']
                            nemb = discord.Embed(title="Dine-in Notification", description=f"Someone came to your restaurant and ordered {nn}. You have been paid <:BistroBux:1324936072760786964>{price_paid}.")
                            nemb.set_footer(text="To turn these notifications off, do 'b.set notifications'")
                            await self.bot.get_user(res['owner']).send(embed=nemb)
                            
                    if "dine_fifty" in post['tasks']:
                        user = post
                        ix = user['tasks'].index("dine_fifty")
                        if user['task_list'][ix]['completed']+1 == user['task_list'][ix]['total']:
                            await ctx.author.send(f"You have completed the **{user['task_list'][ix]['description']}** task. You have been awarded **{user['task_list'][ix]['rewards']} EXP**.")
                            await self.add_exp(user=ctx.author.id, count=user['task_list'][ix]['rewards'], multiplier=False)
                            await db.market.update_one({"owner": ctx.author.id, "task_list.name": "dine_fifty"},{"$inc": {"task_list.$.completed": 1}})
                        else:
                            await db.market.update_one({"owner": ctx.author.id, "task_list.name": "dine_fifty"},{"$inc": {"task_list.$.completed": 1}})

                else:
                    self.bot.get_command("dine").reset_cooldown(ctx)
                    await ctx.send("<:RedTick:653464977788895252> You don't have enough money for this.")
            else:
                self.bot.get_command("dine").reset_cooldown(ctx)
                await ctx.send("<:RedTick:653464977788895252> That item is not on the menu.")
        else:
            self.bot.get_command("dine").reset_cooldown(ctx)
            await ctx.send("<:RedTick:653464977788895252> I couldn't find that restaurant. Try tagging the owner instead.")

    @commands.command(aliases=['Use'])
    @commands.cooldown(1,8, commands.BucketType.user)
    async def use(self, ctx, *, item):
        post = await db.market.find_one({"owner": ctx.author.id})
        item = item.lower().replace("(uncommon)", "").replace("(common)", "").replace("uncommon", "").replace("common", "")
        is_banner = False
        if post:
            w = []
            no_fire = False
            for x in post['inventory']:
                if 'colour' in x:
                    if w:
                        pass
                    elif x['colour']['colour'].lower() == item.lower():
                        await asyncio.sleep(1)
                        await db.market.update_one({"owner": ctx.author.id}, {"$set": {"colour": x['colour']['hex']}})
                        w.append(' ')
                    else:
                        pass
                elif 'banner' in x:
                    if w:
                        pass
                    elif x['banner']['name'].lower() == item.lower():
                        await asyncio.sleep(1)
                        url = x['banner']['url'].replace('paixlukee.ml', 'paixlukee.dev')
                        await db.market.update_one({"owner": ctx.author.id}, {"$set": {"banner": url}})
                        award = await self.get_award(ctx.author.id, "set_banner")
                        is_banner = True
                        w.append(' ')
                    else:
                        pass
                elif 'item' in x:
                    if w:
                        pass
                    elif item == 'fish':
                        await ctx.send("Incorrect Usage... Try the `b.fish` command!")
                    elif item == 'experience potion':
                        if {"item": "ep"} in post['inventory']:
                            w.append('+50 EXP has been added to your restaurant.')
                            await self.add_exp(user=ctx.author.id, count=50, multiplier=False)
                            await db.market.update_one({"owner": ctx.author.id}, {"$pull": {"inventory":{"item": "ep"}}})
                        else:
                            pass
                    elif item == 'time machine':
                        to_reset = ["fish", "trivia"]
                        to_reset_dyna = ["cook", "work", "clean", "beg"]
                        if {"item": "tm"} in post['inventory']:
                            for command in to_reset:
                                cmd = self.bot.get_command(command)
                                cmd.reset_cooldown(ctx)
                            for cmd in to_reset_dyna:
                                result = await db.cooldowns.find_one({"user_id": ctx.author.id, "command_name": cmd})
                                if result:
                                    await db.cooldowns.delete_one({"user_id": ctx.author.id, "command_name": cmd})
                                
                            await db.market.update_one({"owner": ctx.author.id}, {"$pull": {"inventory":{"item": "tm"}}})
                            w.append("All cooldowns have been reset (excluding daily & weekly).")
                        else:
                            pass
                    elif item == 'fire extinguisher':
                        if {"item": "fe"} in post['inventory']:
                            if 'fire' in post['bonuses']:
                                w.append("Your restaurant is no longer on fire.")
                                await db.market.update_one({"owner": ctx.author.id}, {"$pull": {"bonuses": "fire"}})
                                await db.market.update_one({"owner": ctx.author.id}, {"$pull": {"inventory":{"item": "fe"}}})
                            else:
                                no_fire = True
                                w.append(" ")
                        else:
                            pass
                    
                    elif item == 'ambience' or item == 'stone of ambience':
                        w.append('Messages will now switch between random colors.')
                        await db.market.update_one({"owner": ctx.author.id}, {"$set": {"colour": 0x171717}})
                    else:
                        pass
                else:
                    pass
            if not w:
                await ctx.send(f"<:RedTick:653464977788895252> I could not find that in your inventory. Please only include the item name.")
            elif no_fire:
                await ctx.send(f"<:RedTick:653464977788895252> Your restaurant is not on fire.")
            else:
                await ctx.send(f"Item used successfully. {w[0]}")
                if is_banner:
                    if award:
                        await ctx.send(f"{ctx.author.mention}, You've earned the {awards.awards["set_banner"]["emoji"]} **Marketing Expert** award for setting a banner for the first time!")
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `b.start`.")

    @commands.command(aliases=['Se2ll'])
    async def se2ll(self, ctx, *, item):
        post = await db.market.find_one({"owner": ctx.author.id})
        item = item.lower().replace("(uncommon", "").replace("(common)", "").replace("uncommon", "").replace("common", "")
        w = True
        if post:
            for x in post['inventory']:
                if 'colour' in x:
                    if x['colour']['colour'].lower() == item:
                        await asyncio.sleep(1)
                        await db.market.update_one({"owner": ctx.author.id}, {"$set": {"colour": None}})
                elif 'banner' in x:
                    if x['banner']['name'].lower() == item:
                        await asyncio.sleep(1)
                        await db.market.delete_one({"owner": ctx.author.id}, {"$set": {"banner": None}})
                else:#if 'boost' in x:
                    w = False#names.append()
            if not w:
                await ctx.send("<:RedTick:653464977788895252> I could not find that in your inventory. Please only include the item name.")
            else:
                await ctx.send("Item sold successfully for")
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `b.start`.")

    @commands.command(pass_context=True, aliases=['Votereward'])
    @commands.cooldown(1, 43200, commands.BucketType.user)
    async def votereward(self, ctx):
        posts = await db.market.find_one({"owner": ctx.author.id})
        rci = random.randint(28,55)
        r = requests.get(f"https://top.gg/api/bots/657037653346222102/check?userId={ctx.author.id}", headers={"Authorization": config.dbl_token}).json()
        if posts:
            print(r)
            if r['voted'] == 1:
                await self.add_money(user=ctx.author.id, count=rci)
                embed = discord.Embed(colour=0xf04c62, description=f"{rci} Cash")
                embed.set_thumbnail(url="https://bistrobot.co/a/TopGGChest.png")
                embed.set_footer(text="Thanks for upvoting! Come back in 12 hours!")
                await ctx.send(embed=embed, content=f"{ctx.author.mention}, you opened your Top.GG chest and received...")
            else:
                await ctx.send("You haven't upvoted yet! Upvote here: <https://top.gg/bot/657037653346222102/vote>")
                self.bot.get_command("votereward").reset_cooldown(ctx)
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one by doing `b.start`.")
            
    @commands.command(aliases=['Karaoke'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def karaoke(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        event = await db.events.find_one({"user_id": ctx.author.id})
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one by doing `b.start`.")
            return
        if event:
            if event['type'] == 'kn':
                rms = rnd(songs.lyrics)
                embed = discord.Embed(colour=0x8980d9, description=f':notes: **Guess the Song!**\n\n**"**{rms['lyric']}**"**')
                embed.set_footer(text="Respond with the song name.")
                await ctx.send(embed=embed)
                b = time.perf_counter()
                resp = await self.bot.wait_for('message', check=lambda x: x.author == ctx.author)
                a = time.perf_counter()
                tm = a-b
                if resp.content.lower() == rms['song'].lower():
                    if tm < 6:
                        exp = 20
                    else:
                        exp = 15      
                    await ctx.send(f"{ctx.author.mention}, you guessed correctly! You have been awarded {exp} EXP!")
                    await self.add_exp(ctx.author.id, exp, check_tasks=True)
                else:
                    await ctx.send(f"{ctx.author.mention}, you guessed incorrectly! It was **{rms['song']}**")
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have an ongoing Karaoke event! Do `b.event` for more details.")
                
        

    @commands.command(aliases=['Trivia'])
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def trivia(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `b.start`.")
        else:
            embed = discord.Embed(colour=0x8980d9)
            footer = None
            question = rnd(trivia.questions)
            letters = ["a", "b", "c", "d"]
            cn = 0
            desc = ""
            choices = []
            for x in question['answers']:
                cn += 1
                if cn == 1:
                    choices.append({"a":question['answers'][0], "letter": "a"})
                elif cn == 2:
                    choices.append({"b":question['answers'][1], "letter": "b"})
                elif cn == 3:
                    choices.append({"c":question['answers'][2], "letter": "c"})
                else:
                    choices.append({"d":question['answers'][3], "letter": "d"})
            opt = []
            for x in choices:
                letter = x['letter']
                opt.append(f":regional_indicator_{x['letter']}: {x[letter]}")
            answers = "\n".join(opt)
            embed.description = question['question'] + "\n\n" + answers
            embed.set_footer(text="You have 90 seconds to answer.")
            if post['colour']:
                if post['colour'] == 0x171717:
                    embed.colour = random.randint(0, 0xFFFFFF)
                else:
                    embed.colour = post['colour']
            cl = None
            msg = None
            for x in choices:
                letter = x['letter']
                if x[letter] == question['correct']:
                    cl = x['letter']
            
            opportunity_used = False
            second_attempt = False
            sa_msg = None
            footer = None
            
            async def t_button_callback(interaction, letter, b):
                nonlocal opportunity_used, second_attempt, sa_msg, footer
                await interaction.response.defer()         
                a = time.perf_counter()
                tt = a-b
                event = await db.events.find_one({"user_id": ctx.author.id})
                if letter == cl or letter == question['correct'].lower():
                    wrong = False
                    if tt <= 5:
                        money = 12
                        resp = "You've answered correctly in under 5 seconds!"
                    elif tt <= 10:
                        money = 8
                        resp = "You've answered correctly in under 10 seconds!"
                    else:
                        money = 5
                        resp = "You've answered correctly!"
                    if event:
                        if event['type'] == 'ta':
                            money *= 1.7
                            money = round(money)
                else:
                    wrong = True
                    if 'opportunity' in post['stones'] and not opportunity_used:
                        opportunity_used = True
                        second_attempt = True
                        wrong = False
                        resp = "You answered incorrectly, but you have the <:OpportunityStone:1331504493015076914> **Opportunity Stone**! You get another chance!"
                        money = 0 

                if wrong:
                    if 'apron_uses' in post:
                        if post['apron_uses']:
                            uses_left = int(post['apron_uses'])-1
                            footer = f"You have {uses_left} Golden Apron uses left."
                            await db.market.update_one({"owner": ctx.author.id}, {"$set":{"apron_uses": uses_left}})
                    description = f"{ctx.author.mention}, You've answered incorrectly! You've been awarded {bbux}2 for your efforts."
                    await self.add_money(ctx.author.id, 2, check_tasks=True)
                else:
                    if second_attempt:
                        second_attempt = False
                        sa_msg = await ctx.send(resp)
                        return
                    if 'apron_uses' in post:
                        if post['apron_uses']:
                            uses_left = int(post['apron_uses'])-1
                            money = round(money * 1.25)
                            await db.market.update_one({"owner": ctx.author.id}, {"$set":{"apron_uses": uses_left}})
                            footer = f"You have {uses_left} Golden Apron uses left."
                    await self.add_money(ctx.author.id, money, check_tasks=True)
                    description = f"{ctx.author.mention}, {resp} You've been awarded {bbux}{money}."
                embed2 = discord.Embed(colour=0x8980d9, description=description)
                if footer:
                    embed2.set_footer(text=footer, icon_url="https://media.discordapp.net/attachments/1325282246181130330/1329660286302687257/New_Piskel.gif?ex=678b2624&is=6789d4a4&hm=6475df9cb8e5d82646fed8347eb825403e890f45061b28848b477d4e19ace3ce&=&width=1178&height=1060")
                await ctx.send(embed=embed2)
                if msg:
                    await msg.delete()
                if sa_msg:
                    await sa_msg.delete()
                try:
                    await interaction.message.delete()
                except:
                    pass
            
            b = time.perf_counter()
            a_btn = Button(label="A", custom_id="ltr_a", style=discord.ButtonStyle.primary)
            b_btn = Button(label="B", custom_id="ltr_b", style=discord.ButtonStyle.primary)    
            c_btn = Button(label="C", custom_id="ltr_c", style=discord.ButtonStyle.primary)    
            d_btn = Button(label="D", custom_id="ltr_d", style=discord.ButtonStyle.primary)               

            a_btn.callback = lambda interaction: t_button_callback(interaction, "a", b)
            b_btn.callback = lambda interaction: t_button_callback(interaction, "b", b)
            c_btn.callback = lambda interaction: t_button_callback(interaction, "c", b)
            d_btn.callback = lambda interaction: t_button_callback(interaction, "d", b)

            view = View()
            view.add_item(a_btn)
            view.add_item(b_btn)
            view.add_item(c_btn)
            view.add_item(d_btn)
        
            msg = await ctx.send(embed=embed, view=view)


    @commands.command(aliases=['Beg', 'loan', 'Loan'])
    async def beg(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        if post['luck'] > 3:
            numb = random.randint(1,5)
        elif post['luck'] > 1:
            numb = random.randint(1,6)
        else:
            numb = random.randint(1,7)
        bad_resp = ["bad credit score", "unstable income", "criminal record", "unstable employment history"]
        if 'agility' in post['stones']:
            cd_sec = 95
        else:
            cd_sec = 65
        on_cd, remaining = await self.dynamic_cd(ctx.author.id, "beg", cd_sec)
        if on_cd:
            c_min = int(remaining) // 60
            c_sec = int(remaining) % 60
            m_l = "m "
            if not c_min:
                c_min = ""
                m_l = ""
            await ctx.send(f"<:RedTick:653464977788895252> You are on cooldown! Please wait **{c_min}{m_l}{c_sec}s**.")
            return
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `b.start`.")
        else:
            embed = discord.Embed(colour=0x32a852)
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1325282246181130330/1327904413762719755/IMG_2584.png?ex=6784c2db&is=6783715b&hm=696fa2e9b7005a754e975c16485f371a3c6063aebdad7ed23eb48a87a1a2b4a2&=&format=webp&quality=lossless&width=1092&height=1046")
            if numb >= 4:
                resp = rnd(bad_resp)
                embed.description = f"{ctx.author.mention}, you have been denied for a loan due to your {resp}. Try again later!"
            else:
                grant = random.randint(5, 28)
                embed.description = f"{ctx.author.mention}, Bistaria Bank has granted you {bbux}{grant} for your restaurant!"
                await self.add_money(ctx.author.id, grant, check_tasks=True)
            await ctx.send(embed=embed)

    @commands.command(aliases=['Donation'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def donation(self, ctx):
        embed = discord.Embed(colour=0x8980d9, title="Donate", description="Want to support restaurant AND receive awesome rewards? To donate now or view information on rewards, click [here](https://www.patreon.com/join/paixlukee).")
        await ctx.send(embed=embed)

    @commands.command(pass_context=True, aliases=['Weekly'])
    @commands.cooldown(1,604800, commands.BucketType.user)
    async def weekly(self, ctx):
        posts = await db.market.find_one({"owner": ctx.author.id})
        patrons = await db.utility.find_one({"utility": "patrons"})
        if posts:
            rci = random.randint(400, 800)
            if patrons and any(patrons.get(key) and ctx.author.id in patrons[key] for key in ['silver', 'gold', 'diamond']):
                chest = [f'{rci} Cash']
                await self.add_money(user=ctx.author.id, count=rci)
                embed = discord.Embed(colour=0x8980d9, description="\n".join(chest) + "\n\nP.S. Thanks for supporting me!")
                embed.set_thumbnail(url="http://pixelartmaker.com/art/134b1292dc645e7.png")
                embed.set_footer(text="Come back in 1 week!")
                await ctx.send(embed=embed, content=f"{ctx.author.mention}, you opened your patron weekly chest and received...")
            else:
                await ctx.send("<:RedTick:653464977788895252> You must be a silver+ patron to use this command! For more information on BistroBot patronage, click \"Donate\" on the help command.")
                self.bot.get_command("weekly").reset_cooldown(ctx)
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one by doing `b.start`.")
            self.bot.get_command("weekly").reset_cooldown(ctx)

    @commands.command(aliases=['Work'])
    async def work(self, ctx):
        await ctx.typing()
        posts = responses.work
        patrons = await db.utility.find_one({"utility": "patrons"})
        user = await db.market.find_one({"owner": ctx.author.id})
        event = await db.events.find_one({"user_id": ctx.author.id})
        now = datetime.datetime.now()
        uses_left = 0
        celebrities = ["Drake", "Taylor Swift", "Lady Gaga", "Zac Efron", "6ix9ine", "Brendon Urie", "Tom Holland", "Katy Perry", "Ellen Degeneres", "Logan Paul", "Benedict Cumberpatch", "John Cena", "Miley Cyrus", "Kylie Jenner", "Dua Lipa", "Ariana Grande", "Ryan Gosling", "Selena Gomez", "Shawn Mendes", "Keanu Reeves", "Beyoncé", "Rihanna", "Eminem", "Gordon Ramsey", "Billie Eilish"]
        await db.market.update_one({"owner": ctx.author.id}, {"$set":{"laststock": now.strftime("%d/%m/%Y %H:%M")}})
        if 'agility' in user['stones']:
            cd_sec = 350
        else:
            cd_sec = 410
        on_cd, remaining = await self.dynamic_cd(ctx.author.id, "work", cd_sec)
        if on_cd:
            c_min = int(remaining) // 60
            c_sec = int(remaining) % 60
            m_l = "m "
            if not c_min:
                c_min = ""
                m_l = ""
            await ctx.send(f"<:RedTick:653464977788895252> You are on cooldown! Please wait **{c_min}{m_l}{c_sec}s**.")
            return
        if user:
            if ctx.author.id in patrons['bronze']:
                ml = 1.15
            elif ctx.author.id in patrons['silver']:
                ml = 1.25
            elif ctx.author.id in patrons['gold']:
                ml = 1.35
            elif ctx.author.id in patrons['diamond']:
                ml = 1.4
            else:
                ml = 1
            country = str(user['country'])
            rmb = rnd(posts)
            luck = user['luck']
            if rmb['good'] is False:
                if luck == 2:
                    randomChoice = random.randint(1, 10)
                    if randomChoice == 10:
                        rmb = rnd(posts)
                elif luck == 3:
                    randomChoice = random.randint(1, 5)
                    if randomChoice == 5:
                        rmb = rnd(posts)
                elif luck == 4:
                    randomChoice = random.randint(2, 5)
                    if randomChoice == 5:
                        rmb = rnd(posts)
                elif luck == 5 or luck == 6:
                    randomChoice = random.randint(3, 5)
                    if randomChoice == 5:
                        rmb = rnd(posts)
                elif luck > 6:
                    randomChoice = random.randint(4, 5)
                    if randomChoice == 5:
                        rmb = rnd(posts)
            rm = rmb['text']
            count = 0
            r1 = rnd(food[country])
            r2 = rnd(food[country])
            r3 = rnd(food[country])
            r4 = rnd(food[country])
            rm = rm.replace("CELEB", rnd(celebrities))
            if 'happy' in rm or 'refused' in rm:
                msg = str(rm).replace("ITEM", f"**{r1['name']}**")
            elif 'ITEM' in rm and not 'ITEM2' in rm:
                count = r1['price']
                count *= ml
                count = round(count)
                msg = str(rm).replace("ITEM", f"**{r1['name']}**").replace("COUNT", "<:BistroBux:1324936072760786964>" + str(count))
                #await self.add_money(user=ctx.author.id, count=count, check_tasks=True)
                await self.add_sold(user=ctx.author.id, sold=r1['name'])
            elif 'ITEM2' in rm and not 'ITEM4' in rm:
                count = r1['price']+r2['price']+r3['price']
                count *= ml
                count = round(count)
                msg = str(rm).replace("ITEM3", ).replace("ITEM2", f"**{r2['name']}**").replace("ITEM", f"**{r1['name']}**").replace("COUNT", "<:BistroBux:1324936072760786964>" + str(count))
                #await self.add_money(user=ctx.author.id, count=count, check_tasks=True)
                await self.add_sold(user=ctx.author.id, sold=r1['name'])
                await self.add_sold(user=ctx.author.id, sold=r2['name'])
                await self.add_sold(user=ctx.author.id, sold=r3['name'])
            else:
                count = r1['price']+r2['price']+r3['price']+r4['price']
                count *= ml
                count = round(count)
                msg = str(rm).replace("ITEM4", f"**{r4['name']}**").replace("ITEM3", f"**{r3['name']}**").replace("ITEM2", f"**{r2['name']}**").replace("ITEM", f"**{r1['name']}**").replace("COUNT", "<:BistroBux:1324936072760786964>" + str(count))
                #await self.add_money(user=ctx.author.id, count=count, check_tasks=True)
                await self.add_sold(user=ctx.author.id, sold=r1['name'])
                await self.add_sold(user=ctx.author.id, sold=r2['name'])
                await self.add_sold(user=ctx.author.id, sold=r3['name'])
                await self.add_sold(user=ctx.author.id, sold=r4['name'])
            mn_w = 0
            mn_a = 0
            mn_e = 0
            if 'TIP2' in rm:
                tpct = random.randint(7,10)
                tpct *= ml
                tpct = round(tpct)
                if 'worker' in user:
                    if user['worker']:
                        wn = user['worker_name']
                        mn_w = tpct * user['worker'][wn][1]['tips']
                if 'apron_uses' in user:
                    auses = user['apron_uses']
                    if auses:
                        mn_a = tpct * .25
                if event:
                    if event['type'] == 'ayce':
                        mn_e = tpct * .9
                tpct += round(mn_w+mn_a+mn_e)
                msg = msg.replace("TIP2", "<:BistroBux:1324936072760786964>" + str(tpct))
                await self.add_money(user=ctx.author.id, count=tpct, check_tasks=True)
            elif 'TIP3' in rm:
                tpct = random.randint(17, 22)
                tpct *= ml
                tpct = round(tpct)
                if 'worker' in user:
                    if user['worker']:
                        wn = user['worker_name']
                        mn_w = tpct * user['worker'][wn][1]['tips']
                if 'apron_uses' in user:
                    auses = user['apron_uses']
                    if auses:
                        mn_a = tpct * .25
                if event:
                    if event['type'] == 'ayce':
                        mn_e = tpct * .9
                tpct += round(mn_w+mn_a+mn_e)
                msg = msg.replace("TIP3", "<:BistroBux:1324936072760786964>" + str(tpct))
                await self.add_money(user=ctx.author.id, count=tpct, check_tasks=True)
            elif 'TIP' in rm:
                tpc = random.randint(2,6)
                tpc *= ml
                tpc = round(tpc)
                if 'worker' in user:
                    if user['worker']:
                        wn = user['worker_name']
                        mn_w = tpc * user['worker'][wn][1]['tips']
                if 'apron_uses' in user:
                    auses = user['apron_uses']
                    if auses:
                        mn_a = tpc * .25
                if event:
                    if event['type'] == 'ayce':
                        mn_e = tpc * .9
                tpc += round(mn_w+mn_a+mn_e)
                msg = msg.replace("TIP", "<:BistroBux:1324936072760786964>" + str(tpc))
                await self.add_money(user=ctx.author.id, count=tpc, check_tasks=True)
            if r1['name'].endswith('s') or r1['name'].endswith('gna'):
                nn = r1['name']
            else:
                if r1['name'].startswith(("a", "e", "i", "o", "u")):
                    nn = "an " + r1['name']
                else:
                    nn = "a " + r1['name']
            msg = msg.replace(r1['name'], nn)
            wk_emb = discord.Embed(colour=0x8980d9, description=f"{ctx.author.mention}, {msg}")
            if user['colour']:
                    wk_emb.colour = user['colour']
            if 'apron_uses' in user:
                if user['apron_uses']:
                    uses_left = int(user['apron_uses'])-1
                    await db.market.update_one({"owner": ctx.author.id}, {"$set":{"apron_uses": uses_left}})
                    wk_emb.set_footer(text=f"Your Golden Apron has {uses_left} uses left.", icon_url="https://media.discordapp.net/attachments/1325282246181130330/1329660286302687257/New_Piskel.gif?ex=678b2624&is=6789d4a4&hm=6475df9cb8e5d82646fed8347eb825403e890f45061b28848b477d4e19ace3ce&=&width=1178&height=1060")
            await ctx.send(embed=wk_emb)
            if "work_hundred" in user['tasks']:
                ix = user['tasks'].index("work_hundred")
                if user['task_list'][ix]['completed']+1 == user['task_list'][ix]['total']:
                    await ctx.author.send(f"You have completed the **{user['task_list'][ix]['description']}** task. You have been awarded **{user['task_list'][ix]['rewards']} EXP**.")
                    await self.add_exp(user=ctx.author.id, count=user['task_list'][ix]['rewards'], multiplier=False)
                    await db.market.update_one({"owner": ctx.author.id, "task_list.name": "work_hundred"},{"$inc": {"task_list.$.completed": 1}})
                else:
                    await db.market.update_one({"owner": ctx.author.id, "task_list.name": "work_hundred"},{"$inc": {"task_list.$.completed": 1}})
              
        else:            
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `b.start`")

    @commands.command(aliases=['bugreport'])
    async def reportbug(self, ctx, *, topic, option=None, description=None):
        if ctx.channel.id == 748162782586994728:
            await ctx.message.delete()
            args = topic.split('|')
            topic = args[0]
            option = args[1]
            description = args[2]
            if not description:
                await ctx.send(f"<:redtick:492800273211850767> {ctx.author.mention}, Incorrect Arguments. **Usage:** `b.reportbug <topic> <option> <description>` *Do not include < or > in your report.*", delete_after=10)
            if str(option).lower() not in ['major', 'minor', ' minor ', ' major ', 'minor ', 'major ', ' minor', ' major']:
                await ctx.send(f"<:redtick:492800273211850767> {ctx.author.mention}, Incorrect Arguments. Option must be either `Major` or `Minor`. Ex. `b.reportbug Help | Minor | description here`", delete_after=10)
            else:
                data = {
                        "name": description,
                        "desc": f'This is a user-submitted card.\n\n**Command/Topic:** {str(topic).capitalize()}\n\n**Description:** {description}\n\n**Submitted by:** {ctx.author} ({ctx.author.id})\n\n\nThis bug is **{str(option).upper()}**.',
                        "idList": '5f465a723958f77bdb8ca189',
                        "pos": 'top'
                }
                r = requests.post(f"https://api.trello.com/1/cards?key=4ae5477b485b5afa44ae72997bb53b54&token=ae0c71469c814c9335b57be7a35508f828e7d0f84af8adfa10fcce73888a49d6", data=data).json()
                trello_link = r['url']

                #msg = await ctx.send(f"{ctx.author.mention}, your report has been sent! I've sent a transcipt to your DMs.", delete_after=10)

                embed = discord.Embed(colour=0x8980d9, description="Bug Report Transcript")
                embed.add_field(name="Topic/Command:", value=str(topic).capitalize())
                embed.add_field(name="Option:", value=str(option).capitalize())
                embed.add_field(name="Description:", value=description)
                embed.add_field(name="Link:", value=trello_link)
                embed.set_footer(text="Thank you for submitting a bug!")
                await ctx.author.send(embed=embed)

    @commands.command(aliases=['Cooldown', 'cd', 'CD'])
    async def cooldown(self, ctx):
        embed = discord.Embed(colour=0x8980d9, description="All BB Cooldowns")
        cmds = ["daily", "weekly", "trivia", "fish"]
        cmds_db = ["beg", "clean","work", "cook",]
        for command in cmds:     
            cmd = self.bot.get_command(command)    
            remainder = cmd.get_cooldown_retry_after(ctx)
            if remainder > 0:
                cdtime = await self.format_time(remainder)
            else:
                cdtime = "*Ready to use!*"
            embed.add_field(name=str(cmd).upper(), value=cdtime)
        for cmd in cmds_db:
            remng = "*Ready to use!*"
       
            result = await db.cooldowns.find_one({"user_id": ctx.author.id, "command_name": cmd})
            if result:
                expires_at = result["expires_at"]
                if dttm.utcnow() < expires_at:
                    remng = (expires_at - dttm.utcnow()).total_seconds()
                    remng = str(round(remng)) + "s"
            else:
                remng = "*Ready to use!*"
            embed.add_field(name=str(cmd).upper(), value=remng)
        await ctx.send(embed=embed)
        
    @commands.command(aliases=['Stats'])
    async def stats(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `b.start`.")
            return
        embed = discord.Embed(colour=0x8980d9, description = "User Stats\n\n"\
            f"**Experience**: {post['exp']}\n"\
            f"**Total Experience**: {post['total_exp']}\n"\
            f"**Level**: {post['level']}\n"\
            f"**Customer Count**: {post['customers']}\n"\
            f"**Money**: {bbux}{post['money']}\n"\
            f"**Luck Level**: {post['luck']}\n"\
            f"**Menu Item Count**: {len(post['items'])}")
        await ctx.send(embed=embed)

    @commands.command(aliases=['Awards', 'badges'])
    async def awards(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        if post:
            embed = discord.Embed(colour=0x8980d9)
            description = "All Bistro Awards\n"
            for x in awards.awards:
                award = awards.awards[x]
                if x in post['awards']:
                    emoji = award['emoji']
                else:
                    emoji = award['grey_emoji']
                description += f"\n{emoji} **{award['name']}**\n{award['description']}"
            embed.description = description
            await ctx.send(embed=embed)
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `b.start`.")
          
            
    @commands.group(aliases=["Event"])
    async def event(self, ctx):
        if ctx.invoked_subcommand is None:
            post = await db.market.find_one({"owner": ctx.author.id})
            event = await db.events.find_one({"user_id": ctx.author.id})
            if not post:
                await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `b.start`.")
                return 
            if event:
                eastern = timezone('US/Eastern')
                cr_utc = event['createdAt'].replace(tzinfo=utc)
                exp_utc = event['expireAt'].replace(tzinfo=utc)
                created = cr_utc.astimezone(eastern).strftime('%m/%d **at** %I:%M %p')
                expires = exp_utc.astimezone(eastern).strftime('%m/%d **at** %I:%M %p')
                event_desc = ""
                if event['type'] == "tn":
                    event_desc = ":question: **Trivia Night**\n\nYou are currently hosting an event! You are earning +70% earnings on the `b.trivia` command until the event ends."
                elif event['type'] == "kn":
                    event_desc = ":notes: **Karaoke Night**\n\nYou are currently hosting an event! You can use the `b.karaoke` command until the event ends."
                elif event['type'] == "ayce":
                    event_desc = ":meat_on_bone: **All-You-Can-Eat**\n\nYou are currently hosting an event! You're earning **+90% Tips** (Work Cmd) & **+50% EXP** until the event ends."
                embed = discord.Embed(colour=0x8980d9)
                embed.description = f"{event_desc}\n\n**Started**: {created} **ET**\n**Ends**: {expires} **ET**"
                embed.set_footer(icon_url=ctx.author.avatar.url, text=f"Hosted by {ctx.author.name}")
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"{ctx.author.mention}, there is no ongoing event. Do `b.event start` to start one.")
            

        
    @event.command(aliases=['Start'])
    async def start(self, ctx):
        post = await db.market.find_one({"owner": ctx.author.id})
        event = await db.market.find_one({"user_id": ctx.author.id})
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `b.start`.")
            return 
        if event:
            await ctx.send(f"{ctx.author.mention}, you already have an ongoing event. Do `b.event` to view it.")
        else:
            msg = None
            event_started = False
            embed = discord.Embed(colour=0x8980d9)
            embed.description = "You want to start an event? You must pay a fee and have a certain amount of customers to start one. To check your customer count, do `b.restaurant` \n\n**Events only last 24 hours.**"\
                f"\n\n**[1] :question: Trivia Night** - Costs {bbux}60\n"\
                "You will earn +70% earnings with the trivia command. You must have at least 300 customers.\n"\
                f"\n\n**[2] :notes: Karaoke Night** - Costs {bbux}75\n"\
                "You gain the ability to use the `b.karaoke` command You You must have at least 500 customers.\n"\
                f"\n\n**[3] :meat_on_bone: All-You-Can-Eat** - Costs {bbux}100\n"\
                "You will earn +90% tips (Work cmd) and +50% EXP. You must have at least 1000 customers."
            embed.set_footer(text="Respond with the corresponding number to host the event")
            async def e_button_callback(interaction, opt):
                await interaction.response.defer()
                if opt == '1':
                    if post['customers'] < 300:
                        await ctx.send("<:RedTick:653464977788895252> You must have had at least 300 customers to start this event.")
                    elif post['money'] < 60:
                        await ctx.send(f"<:RedTick:653464977788895252> You need at least {bbux}60 to start this event.")
                    else:
                        event_started = True
                        await self.start_event(ctx, "tn")
                        await self.take_money(ctx.author.id, 60)
                        await ctx.send(f"{ctx.author.mention}, Your restaurant's **Trivia Night** has started! Check `b.event` to view information.")
                elif opt == '2':
                    if post['customers'] < 500:
                        await ctx.send("<:RedTick:653464977788895252> You must have had at least 500 customers to start this event.")
                    elif post['money'] < 75:
                        await ctx.send(f"<:RedTick:653464977788895252> You need at least {bbux}75 to start this event.")
                    else:
                        event_started = True
                        await self.start_event(ctx, "kn")
                        await self.take_money(ctx.author.id, 75)
                        await ctx.send(f"{ctx.author.mention}, Your restaurant's **Karaoke Night** has started! You can now use the `b.karaoke` command. Check `b.event` to view information.")
                elif opt == '3':
                    if post['customers'] < 1000:
                        await ctx.send("<:RedTick:653464977788895252> You must have had at least 1000 customers to start this event.")
                    elif post['money'] < 100:
                        await ctx.send(f"<:RedTick:653464977788895252> You need at least {bbux}100 to start this event.")
                    else:
                        event_started = True
                        await self.start_event(ctx, "ayce")
                        await self.take_money(ctx.author.id, 100)
                        await ctx.send(f"{ctx.author.mention}, Your restaurant's **All-You-Can-Eat** event has started! Check `b.event` to view information.")
                if msg:
                    await msg.delete()
                try:
                    await interaction.message.delete()
                except:
                    pass
                
                if event_started:
                    if "start_event" in post['tasks']:
                        user = post
                        ix = user['tasks'].index("start_event")
                        if user['task_list'][ix]['completed']+1 == 1:
                            await ctx.author.send(f"You have completed the **{user['task_list'][ix]['description']}** task. You have been awarded **{user['task_list'][ix]['rewards']} EXP**.")
                            await self.add_exp(user=ctx.author.id, count=user['task_list'][ix]['rewards'], multiplier=False)
                            await db.market.update_one({"owner": ctx.author.id, "task_list.name": "start_event"},{"$set": {"task_list.$.completed": 1}})
                            
            opt1 = Button(label="1", custom_id="e_opt1", style=discord.ButtonStyle.primary)    
            opt2 = Button(label="2", custom_id="e_opt2", style=discord.ButtonStyle.primary) 
            opt3 = Button(label="3", custom_id="e_opt3", style=discord.ButtonStyle.primary) 
            
            opt1.callback = lambda interaction: e_button_callback(interaction, '1')
            opt2.callback = lambda interaction: e_button_callback(interaction, '2')
            opt3.callback = lambda interaction: e_button_callback(interaction, '3')
            
            view = View()
            view.add_item(opt1)   
            view.add_item(opt2)   
            view.add_item(opt3)   
        
            msg = await ctx.send(embed=embed, view=view)      
            
            
    @commands.command(aliases=['Stones', 'Fragments', 'fragments'])   
    async def stones(self, ctx):
        await ctx.typing()
        post = await db.market.find_one({'owner': ctx.author.id})
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `b.start`.")
            return
        agility = '`0/4 owned`'
        opportunity = '`0/4 owned`'
        endearing = '`0/4 owned`'
        ambience = '`0/4 owned`'
        if 'fragments' in post and post['fragments']:
            for x in post['fragments']:
                
                if x['stone'] == 'agility' and 'agility' in post['stones']:
                    agility = '`Stone owned.`'
                elif x['stone'] == 'agility' and x['count'] >= 4:
                    agility = '`Ready to fuse!`'
                elif x['stone'] == 'agility':
                    agility = f'`{x['count']}/4` owned' 
                elif x['stone'] == 'opportunity' and 'opportunity' in post['stones']:
                    opportunity = '`Stone owned.`'
                elif x['stone'] == 'opportunity' and x['count'] >= 4:
                    opportunity = '`Ready to fuse!`'
                elif x['stone'] == 'opportunity':
                    opportunity = f'`{x['count']}/4` owned'
                elif x['stone'] == 'endearing' and 'endearing' in post['stones']:
                    endearing = '`Stone owned.`'
                elif x['stone'] == 'endearing' and x['count'] >= 4:
                    endearing = '`Ready to fuse!`'
                elif x['stone'] == 'endearing':
                    endearing = f'`{x['count']}/4` owned'
                elif x['stone'] == 'ambience' and 'ambience' in post['stones']:
                    ambience = '`Stone owned.`'
                elif x['stone'] == 'ambience' and x['count'] >= 4:
                    ambience = '`Ready to fuse!`'
                elif x['stone'] == 'ambience':
                    ambience = f'`{x['count']}/4` owned'
        
        async def fs_button_callback(interaction):
            await interaction.response.defer()
            if interaction.user != ctx.author:
                return
            try:
                if agility == '`Ready to fuse!`':
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"stones": "agility"}})
                    await interaction.followup.send("Your fragments have fused to become a <:AgilityStone:1331501018768347157> **Stone of Agility**. Your bonuses have been applied.", ephemeral=True)
                elif endearing == '`Ready to fuse!`':
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"stones": "endearing"}})
                    await interaction.followup.send("Your fragments have fused to become a <:EndearingStone:1331822694202871851> **Stone of Endearing**. Your bonuses have been applied.", ephemeral=True)
                elif opportunity == '`Ready to fuse!`':
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"stones": "opportunity"}})
                    await interaction.followup.send("Your fragments have fused to become a <:OpportunityStone:1331504493015076914> **Stone of Opportunity**. Your bonuses havee been applied.", ephemeral=True)
                elif ambience == '`Ready to fuse!`':
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"stones": "ambience"}})
                    await db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory": {"item": "ambience"}}})
                    await interaction.followup.send("Your fragments have fused to become a <:AmbienceStone:1331825641703604225> **Stone of Ambience**. Do `b.use Stone of Ambience` to apply the rainbow effect.", ephemeral=True)
            except Exception as e:
                print(e)    
                
        embed = discord.Embed(description = "**Enhancement Stones**\n\nIn Bistaria, there are stones much rarer than diamonds. "\
            "They are called *Enhancement Stones*. These stones are said to give powers to those who wield them. Though due to a major mine explosion, "\
            "80% of the world's supply has been left fragmented and scattered.\n\nStone Fragments can be found many different ways. You can find them with the `b.daily` command, "\
            "chests from the bot's store, the `b.fish` command, and even from unlocking levels. With the button below, you can fuse 4 fragments to create a full stone.\n\n"\
            "<:AgilityStone:1331501018768347157> **Stone of Agility**\nFaster work, beg, and clean cooldowns\n"\
            f"<:AgilityFragment:1331502143760236574> {agility}\n\n"\
            "<:OpportunityStone:1331504493015076914> **Stone of Opportunity**\nSecond chance on cook unscramble and trivia\n"\
            f"<:OpportunityFragment:1331505178959937556> {opportunity}\n\n"\
            "<:EndearingStone:1331822694202871851> **Stone of Endearing**\nHigher ratings and customer count\n"\
            f"<:EndearingFragment:1331823626080620574> {endearing}\n\n"\
            "<:AmbienceStone:1331825641703604225> **Stone of Ambience**\nA random embed color each command use\n"\
            f"<:AmbienceFragment:1331825947036483675> {ambience}\n\u200b")  
        
        fuse_btn = Button(label="Fuse Stone", custom_id="fuse_btn", style=discord.ButtonStyle.secondary)    
            
        statuses = [agility, opportunity, endearing, ambience]
        if statuses.count('`Ready to fuse!`') == 0:
            fuse_btn.disabled = True
            
        fuse_btn.callback = fs_button_callback
            
        view = View()
        view.add_item(fuse_btn)   
        
        await ctx.send(embed=embed, view=view)     

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
        

    async def format_time(self, seconds):
        hours, rem = divmod(seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        result = []

        if hours > 0:
            result.append(f"{hours:.0f}h")
        if minutes > 0:
            result.append(f"{minutes:.0f}m")
        if seconds > 0:
            result.append(f"{seconds:.0f}s")
        return " ".join(result)


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

    async def take_exp(self, user, count):
        data = await db.market.find_one({"owner": user})
        bal = data['exp']
        exp = int(bal) - count
        await db.market.update_one({"owner": user}, {"$set":{"exp": exp}})
        return count
    
    async def add_rand_fragment(self, user):
        post = await db.market.find_one({"owner": user})
        fragments = ['agility', 'opportunity', 'endearing', 'ambience']
        for x in post['stones']:
            fragments.remove(x)
        if not fragments:
            return None
        fragment = rnd(fragments)
        in_list = False
        for frag in post['fragments']:
            if fragment == frag:
                await db.market.update_one({"owner": user, "fragments.stone": fragment}, {"$inc": {"fragments.$.count": 1}})
                in_list = True
        if not in_list:
            await db.market.update_one({"owner": user}, {"$push": {"fragments": {"stone": fragment, "count": 1}}})
        return fragment
    
    
    async def add_exp(self, user, count, multiplier=True, check_tasks=False):
        data = await db.market.find_one({"owner": user})
        bal = data['exp']
        if multiplier:
            if 'worker' in data:
                if data['worker']:
                    wn = data['worker_name']
                    count = count + round(count*data['worker'][wn][0]['exp'])
            if 'fire' in data['bonuses']:
                count = count - round(count*0.4)
        else:
            pass
        exp = int(bal) + count
        await db.market.update_one({"owner": user}, {"$set":{"exp": exp}})
        await db.market.update_one({"owner": user}, {"$inc":{"total_exp": count}})
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

        return count

    async def add_sold(self, user, sold):
        item = sold
        data = await db.market.find_one({"owner": user})
        it = None
        for x in data['items']:
            if x['name'] == item:
                it = x
        bal = it['sold']
        tc = int(bal) + 1
        await db.market.update_one({"owner": user}, {"$pull":{"items": {"name": item, "price": it['price'], "stock": it['stock'], "sold": bal}}})
        await db.market.update_one({"owner": user}, {"$push":{"items": {"name": item, "price": it['price'], "stock": it['stock'], "sold": tc}}})

    async def start_event(self, ctx, event_type):
        event = {
            "type": event_type,
            "user_id": ctx.author.id,
            "createdAt": dttm.utcnow().replace(tzinfo=pytz.utc),
            "expireAt": dttm.utcnow().replace(tzinfo=pytz.utc) + timedelta(hours=24)
        }
        await db.events.insert_one(event)

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
           

async def setup(bot):
    await bot.add_cog(User(bot))
