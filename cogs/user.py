import discord
from discord.ext import commands, tasks
import datetime
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
import requests
import trivia
from discoin import Client

#mongo
client = MongoClient(config.mongo_client)
db = client['siri']
#discoin
#loop = asyncio.get_event_loop()
#client = Client(config.discoin_token, "RBC", loop=loop)

class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = 'r!'
        self.discoin_client = Client(token=config.discoin_token, me="RBC", loop=bot.loop)
        self.discoin_update.start()

    def cog_unload(self):
        self.discoin_update.cancel()

    @tasks.loop(minutes=4.0)
    async def discoin_update(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(1)

        unhandled_transactions = await self.discoin_client.fetch_transactions()
        for transaction in unhandled_transactions:
            await self.discoin_client.handle_transaction(transaction.id)
            user = self.bot.get_user(transaction.user_id)
            await self.add_money(user=transaction.user_id, count=round(transaction.payout))
            if user:
                po = round(transaction.payout)
                cid = transaction.currency_from.id
                tid = transaction.id
                embed = discord.Embed(colour=0xa82021, title="Transaction successful", description=f"Your transfer from **{cid}** to **RBC** has been processed! You have received ${po}.\n\n[Transaction Receipt](https://dash.discoin.zws.im/#/transactions/{tid}/show)")
                await user.send(embed=embed)

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
        post = db.market.find_one({"owner": int(user.id)})
        if post:
            embed = discord.Embed(colour=0xa82021, description=str(user))
            embed.set_author(icon_url=user.avatar_url_as(format='png'), name="User Stats")
            embed.set_thumbnail(url=user.avatar_url_as(format='png'))
            embed.add_field(name="Restaurant", value=post['name'])
            embed.add_field(name="Money", value="$" + str(post['money']))
            await ctx.send(embed=embed)
        else:
            await ctx.send("<:RedTick:653464977788895252> This user doesn't have a restaurant")

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
            await ctx.send("<:RedTick:653464977788895252> This user doesn't have a restaurant")

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def donate(self, ctx, user: discord.User=None, count:int=None):
        posts_user = db.market.find_one({"owner": user.id})
        posts = db.market.find_one({"owner": ctx.author.id})

        if ctx.author == user:
            await ctx.send("<:RedTick:653464977788895252> You cannot donate money to yourself!")

        elif not count or not user:
            await ctx.send("<:RedTick:653464977788895252> You must include both the user and the amount of money. Example: `r!donate @lukee#0420 25`")

        elif count < 0:
            await ctx.send(f"<:RedTick:653464977788895252> You can't donate under **$1**.")

        elif not posts['money'] >= count:
            await ctx.send(f"<:RedTick:653464977788895252> You don't have enough money.")

        elif posts_user is None:
            await ctx.send(f"<:RedTick:653464977788895252> **{user.name}** doesn't have a restaurant.")

        elif not posts is None:
            await self.add_money(user=user.id, count=count)
            await self.take_money(user=ctx.author.id, count=count)
            await ctx.send(f"{user.mention}, **{ctx.message.author}** has donated **${count}** to you.")
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one by doing `r!start`.")

    @commands.command(pass_context=True, aliases=['Daily'])
    @commands.cooldown(1,86400, commands.BucketType.user)
    async def daily(self, ctx):
        posts = db.market.find_one({"owner": ctx.author.id})
        patrons = db.utility.find_one({"utility": "patrons"})
        if posts:
            ri = random.randint(1,6)
            rci = random.randint(140, 200)
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
            if 'worker' in posts:
                if posts['worker']:
                    rci = rci - 50
            else:
                pass
            chest = [f'• {rci} Cash']
            if ri == 1:
                pass
                #chest.append('• Cooldown Remover Potion (1x)')
                #db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"potion": "cooldown"}}})
            else:
                pass
            try:
                await self.add_money(user=ctx.author.id, count=rci)
                embed = discord.Embed(colour=0xa82021, description="\n".join(chest) + "\n\nWant even more money? Vote for me on [Discord Bot List](https://top.gg/bot/648065060559781889), and do `r!votereward` to receive another chest.")
                embed.set_thumbnail(url="http://pixelartmaker.com/art/f6d46bd306aacfd.png")
                embed.set_footer(text="Come back in 24 hours!")
                await ctx.send(embed=embed, content=f"{ctx.author.mention}, you opened your daily chest and received...")
            except Exception as e:
                await ctx.send("<:RedTick:653464977788895252> An error has occurred! The cooldown has been lifted. `{e}`")
                self.bot.get_command("daily").reset_cooldown(ctx)
            except:
                await ctx.send("<:RedTick:653464977788895252> An unknown error has occurred! The cooldown has been lifted.")
                self.bot.get_command("daily").reset_cooldown(ctx)
        else:
            await ctx.send("You don't have a restaurant. Create one by doing `r!start`.")

    @commands.command(aliases=['Inventory', 'inv'])
    async def inventory(self, ctx, page=1):
        post = db.market.find_one({"owner": ctx.author.id})
        if post:
            embed = discord.Embed(colour=0xa82021)
            embed.set_author(icon_url=ctx.author.avatar_url_as(format='png'), name="Your Inventory")
            names = []
            items_per_page = 12
            pages = math.ceil(len(post['inventory']) / 12)
            start = (page - 1) * 12
            end = start + 12
            for x in post['inventory'][start:end]:
                if 'colour' in x:
                    names.append(f"<:ColourIcon:659418340703469584> {x['colour']['colour']} ({x['colour']['rarity']})")
                elif 'banner' in x:
                    names.append(f"<:BannerIcon:657457820295495699> {x['banner']['name']} ({x['banner']['rarity']}) [[View]]({x['banner']['url']})")
                elif 'potion' in x:
                    names.append(f"<:CooldownPotion:715822985780658238> Cooldown Remover Potion (Uncommon)")
                elif 'item' in x:
                    if x['item'] == 'fish':
                        names.append(f":fishing_pole_and_fish: Fishing Rod (Common)")
                    elif x['item'] == 'ep':
                        names.append(f"<:ExperiencePotion:715822985780658238> Experience Potion (Common)")
                else:
                    pass
            if names:
                embed.description = "\n".join(names)
            else:
                embed.description = "Nothing to see here."
            np = page+1
            embed.set_footer(text=f"Page {page} of {pages} | r!inventory {np} to see the next page")
            await ctx.send(embed=embed)
        else:
            await ctx.send("You don't have a restaurant! Create one with `r!start`.")

    @commands.command(aliases=['Dine', 'Eat', 'eat'])
    @commands.cooldown(1,30, commands.BucketType.user)
    async def dine(self, ctx, *, restaurant=None):
        post = db.market.find_one({"owner":ctx.author.id})
        def nc(m):
            return m.author == ctx.message.author
        if ctx.message.mentions:
            if len(ctx.message.mentions) >= 2:
                res = db.market.find_one({"owner":ctx.message.mentions[0].id})
            else:
                res = db.market.find_one({"owner":ctx.message.mentions[0].id})
        elif db.market.find_one({"name": restaurant}):
            res = db.market.find_one({"name": restaurant})
        else:
            res = None
        if not restaurant:
            self.bot.get_command("dine").reset_cooldown(ctx)
            await ctx.send("<:RedTick:653464977788895252> You didn't include a restaurant! Example: `r!dine @lukee#0420` or `r!dine McDonalds`.")
        elif res['owner'] == ctx.author.id:
            self.bot.get_command("dine").reset_cooldown(ctx)
            await ctx.send("<:RedTick:653464977788895252> You can't dine in at your own restaurant.")
        elif res:
            items = []
            for x in res['items']:
                items.append(x['name'])
            li = ', '.join(items)
            embed = discord.Embed(colour=0xa82021, description=f"Welcome to {res['name']}!\n\nWhich item would you like to order?\n\n**Menu**: {li}")
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
                if x['name'] == chi.content:
                    newi.append(x)
            if chi.content in items:
                item = newi[0]
                if post['money'] >= item['price']:
                    rxp = round(1.2*item['price'])
                    await self.take_money(ctx.author.id, item['price'])
                    c = await self.add_exp(ctx.author.id, rxp)
                    await ctx.send(f"You've ordered a {item['name']} from {res['name']} for ${item['price']}. You've earned {c} EXP for dining in.")
                    price_paid = round(item['price']/1.8)
                    await self.add_money(res['owner'], round(item['price']/1.8))
                    await self.add_sold(res['owner'], item['name'])
                    if 'notifications' in res:
                        if res['notifications']:
                            if item['name'].startswith(("a", "e", "i", "o", "u")):
                                nn = "an " + item['name']
                            else:
                                nn = "a " + item['name']
                            nemb = discord.Embed(title="Dine-in Notification", description=f"Someone came to your restaurant and ordered {nn}. You have been paid ${price_paid}.")
                            nemb.set_footer(text="To turn these notifications off, do 'r!set notifications'")
                            await self.bot.get_user(res['owner']).send(embed=nemb)
                        else:
                            pass
                    else:
                        pass
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
    @commands.cooldown(1,10, commands.BucketType.user)
    async def use(self, ctx, *, item):
        post = db.market.find_one({"owner": ctx.author.id})
        item = item.lower().replace("(uncommon", "").replace("(common)", "").replace("uncommon", "").replace("common", "")
        #w = True
        if post:
            w = []
            for x in post['inventory']:
                if 'colour' in x:
                    if w:
                        pass
                    elif x['colour']['colour'].lower() == item.lower():
                        await asyncio.sleep(1)
                        db.market.update_one({"owner": ctx.author.id}, {"$set": {"colour": x['colour']['hex']}})
                        w.append(' ')
                    else:
                        pass
                elif 'banner' in x:
                    if w:
                        pass
                    elif x['banner']['name'].lower() == item.lower():
                        await asyncio.sleep(1)
                        db.market.update_one({"owner": ctx.author.id}, {"$set": {"banner": x['banner']['url']}})
                        w.append(' ')
                    else:
                        pass
                elif 'item' in x:
                    if w:
                        pass
                    elif item == 'fish':
                        await ctx.send("Incorrect Usage...")
                    elif item == 'experience potion':
                        w.append('+50 EXP has been added to your Restaurant.')
                        await self.add_exp(user=ctx.author.id, count=50)
                        db.market.update_one({"owner": ctx.author.id}, {"$pull": {"inventory":{"item": "ep"}}})
                    else:
                        pass



                elif 'potion' in x:
                    if not w:
                        if x['potion'] == 'cooldown':
                            def nc(m):
                                return m.author == ctx.message.author
                            embed = discord.Embed(colour=0xa82021, description=f"What command would you like to use this potion on? `Ex. daily`")
                            embed.set_footer(text="You have 90 seconds to reply")
                            embed.set_author(name="Cooldown Remover Potion", icon_url="https://cdn.discordapp.com/emojis/715822985780658238.png?v=1")
                            msg = await ctx.send(embed=embed)
                            resp = await self.bot.wait_for('message', check=nc, timeout=90)
                            try:
                                await resp.delete()
                                await msg.delete()
                            except:
                                pass
                            if not self.bot.get_command(resp.content.lower()):
                                await ctx.send("Error using potion, did you type it right? `Example: daily`")
                                w.append(1)
                            else:
                                self.bot.get_command(resp.content.lower()).reset_cooldown(ctx)
                                await ctx.send("Item used successfully.")
                                db.market.update_one({"owner": ctx.author.id}, {"$pull": {"inventory":{"potion": "cooldown"}}})
                                w.append(1)
                    else:
                        pass
                else:
                    pass
            if not w:
                await ctx.send(f"<:RedTick:653464977788895252> I could not find that in your inventory. Please only include the item name.")
            else:
                await ctx.send(f"Item used successfully. {w[0]}")
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `r!start`.")

    @commands.command(aliases=['Se2ll'])
    async def se2ll(self, ctx, *, item):
        post = db.market.find_one({"owner": ctx.author.id})
        item = item.lower().replace("(uncommon", "").replace("(common)", "").replace("uncommon", "").replace("common", "")
        w = True
        if post:
            for x in post['inventory']:
                if 'colour' in x:
                    if x['colour']['colour'].lower() == item:
                        await asyncio.sleep(1)
                        db.market.update_one({"owner": ctx.author.id}, {"$set": {"colour": None}})
                elif 'banner' in x:
                    if x['banner']['name'].lower() == item:
                        await asyncio.sleep(1)
                        db.market.delete_one({"owner": ctx.author.id}, {"$set": {"banner": None}})
                else:#if 'boost' in x:
                    w = False#names.append()
            if not w:
                await ctx.send("<:RedTick:653464977788895252> I could not find that in your inventory. Please only include the item name.")
            else:
                await ctx.send("Item sold successfully for")
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `r!start`.")

    @commands.command(pass_context=True, aliases=['Votereward'])
    @commands.cooldown(1, 43200, commands.BucketType.user)
    async def votereward(self, ctx): #http://pixelartmaker.com/art/f697739d6ed8a4b.png
        posts = db.market.find_one({"owner": ctx.author.id})
        rci = random.randint(50,100)
        r = requests.get(f"https://discordbots.org/api/bots/648065060559781889/check?userId={ctx.author.id}", headers={"Authorization": config.dbl_token}).json()
        if posts:
            if r['voted'] == 1:
                await self.add_money(user=ctx.author.id, count=rci)
                embed = discord.Embed(colour=0x7289da, description=f"{rci} Cash")
                embed.set_thumbnail(url="http://pixelartmaker.com/art/f697739d6ed8a4b.png")
                embed.set_footer(text="Thanks for upvoting! Come back in 12 hours!")
                await ctx.send(embed=embed, content=f"{ctx.author.mention}, you opened your DBL chest and received...")
            else:
                await ctx.send("You haven't upvoted! Upvote here: <https://top.gg/bot/648065060559781889/vote>")
                self.bot.get_command("votereward").reset_cooldown(ctx)
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one by doing `r!start`.")

    @commands.command(aliases=['Trivia'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def trivia(self, ctx):
        post = db.market.find_one({"owner": ctx.author.id})
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `r!start`.")
        else:
            embed = discord.Embed(colour=0xa82021)
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
            embed.set_footer(text="You have 90 seconds to respond with the correct letter.")
            await ctx.send(embed=embed)
            cl = None
            for x in choices:
                letter = x['letter']
                if x[letter] == question['correct']:
                    cl = x['letter']
            b = time.perf_counter()
            msg = await self.bot.wait_for('message', check=lambda x: x.author == ctx.author)
            a = time.perf_counter()
            tt = a-b
            if msg.content.lower() == cl or msg.content.lower() == question['correct'].lower():
                if tt <= 5:
                    await ctx.send("You've answered correctly in under 5 seconds. You've been awarded $10.")
                    await self.add_money(ctx.author.id, 10)
                elif tt <= 10:
                    await ctx.send("You've answered correctly in under 10 seconds. You've been awarded $8.")
                    await self.add_money(ctx.author.id, 8)
                else:
                    await ctx.send("You've answered correctly. You've been awarded $5.")
                    await self.add_money(ctx.author.id, 5)
            else:
                await ctx.send("You've answered incorrectly. You've been awarded $2 for your efforts.")
                await self.add_money(ctx.author.id, 2)



    @commands.command(aliases=['Beg'])
    @commands.cooldown(1, 90, commands.BucketType.user)
    async def beg(self, ctx):
        numb = random.randint(1,5)
        post = db.market.find_one({"owner": ctx.author.id})
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `r!start`.")
        elif numb == 1 or numb == 2:
            await ctx.send("The Bank of Restaria denied your request.")
        else:
            grant = numb*5
            await ctx.send(f"The Bank of Restaria granted you ${grant} for your restaurant.")
            await self.add_money(ctx.author.id, grant)

    @commands.command(aliases=['Donate'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def donation(self, ctx):
        embed = discord.Embed(colour=0xa82021, title="Donate", description="Want to support restaurant AND receive awesome rewards? To donate now or view information on rewards, click [here](https://www.patreon.com/join/paixlukee).")
        await ctx.send(embed=embed)

    @commands.command(pass_context=True, aliases=['Weekly'])
    @commands.cooldown(1,604800, commands.BucketType.user)
    async def weekly(self, ctx):
        posts = db.market.find_one({"owner": ctx.author.id})
        patrons = db.utility.find_one({"utility": "patrons"})
        if posts:
            rci = random.randint(1000, 1700)
            if ctx.author.id in patrons['silver'] or ctx.author.id in patrons['gold'] or ctx.author.id in patrons['diamond']:
                chest = [f'{rci} Cash']
                await self.add_money(user=ctx.author.id, count=rci)
                embed = discord.Embed(colour=0xa82021, description="\n".join(chest) + "\n\nP.S. Thanks for supporting me!")
                embed.set_thumbnail(url="http://pixelartmaker.com/art/134b1292dc645e7.png")
                embed.set_footer(text="Come back in 1 week!")
                await ctx.send(embed=embed, content=f"{ctx.author.mention}, you opened your patron weekly chest and received...")
            else:
                await ctx.send("<:RedTick:653464977788895252> You must be a silver+ patron to use this command! For more information on restaurant patronage, click \"Donate\" on the help command.")
                self.bot.get_command("weekly").reset_cooldown(ctx)
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one by doing `r!start`.")
            self.bot.get_command("weekly").reset_cooldown(ctx)

    @commands.command(aliases=['Work'])
    @commands.cooldown(1, 480, commands.BucketType.user)
    async def work(self, ctx):
        posts = db.utility.find_one({"utility": "res"})
        patrons = db.utility.find_one({"utility": "patrons"})
        user = db.market.find_one({"owner": ctx.author.id})
        now = datetime.datetime.now()
        celebrities = ["Taylor Swift", "Lady Gaga", "Zac Efron", "6ix9ine", "Brendon Urie", "Chris Pratt", "Katy Perry", "Ellen Degeneres", "David Dobrik", "Benedict Cumberpatch", "John Cena", "Miley Cyrus", "Kylie Jenner", "Victoria Justice", "Ariana Grande", "Ryan Gosling", "Selena Gomez", "Shawn Mendes", "Keanu Reeves", "Beyoncé", "Rihanna", "Eminem"]
        db.market.update_one({"owner": ctx.author.id}, {"$set":{"laststock": now.strftime("%d/%m/%Y %H:%M")}})
        if user:
            if ctx.author.id in patrons['bronze']:
                ml = 1.2
            elif ctx.author.id in patrons['silver']:
                ml = 1.4
            elif ctx.author.id in patrons['gold']:
                ml = 1.6
            elif ctx.author.id in patrons['diamond']:
                ml = 1.7
            else:
                ml = 1
            country = str(user['country'])
            rm = rnd(posts['resp'])['text']
            count = 0
            r1 = rnd(food.food[country])
            r2 = rnd(food.food[country])
            r3 = rnd(food.food[country])
            r4 = rnd(food.food[country])
            rm = rm.replace("CELEB", rnd(celebrities))
            if 'happy' in rm or 'refused' in rm:
                msg = str(rm).replace("ITEM", r1['name'])
            elif 'ITEM' in rm and not 'ITEM2' in rm:
                count = r1['price']
                count *= ml
                count = round(count)
                msg = str(rm).replace("ITEM", r1['name']).replace("COUNT", "$" + str(count))
                await self.add_money(user=ctx.author.id, count=count)
                await self.add_sold(user=ctx.author.id, sold=r1['name'])
            elif 'ITEM2' in rm and not 'ITEM4' in rm:
                count = r1['price']+r2['price']+r3['price']
                count *= ml
                count = round(count)
                msg = str(rm).replace("ITEM3", r3['name']).replace("ITEM2", r2['name']).replace("ITEM", r1['name']).replace("COUNT", "$" + str(count))
                await self.add_money(user=ctx.author.id, count=count)
                await self.add_sold(user=ctx.author.id, sold=r1['name'])
                await self.add_sold(user=ctx.author.id, sold=r2['name'])
                await self.add_sold(user=ctx.author.id, sold=r3['name'])
            else:
                count = r1['price']+r2['price']+r3['price']+r4['price']
                count *= ml
                count = round(count)
                msg = str(rm).replace("ITEM4", r4['name']).replace("ITEM3", r3['name']).replace("ITEM2", r2['name']).replace("ITEM", r1['name']).replace("COUNT", "$" + str(count))
                await self.add_money(user=ctx.author.id, count=count)
                await self.add_sold(user=ctx.author.id, sold=r1['name'])
                await self.add_sold(user=ctx.author.id, sold=r2['name'])
                await self.add_sold(user=ctx.author.id, sold=r3['name'])
                await self.add_sold(user=ctx.author.id, sold=r4['name'])
            if 'TIP2' in rm:
                tpct = random.randint(8,10)
                tpct *= ml
                tpct = round(tpct)
                if 'worker' in user:
                    if user['worker']:
                        wn = user['worker_name']
                        tpct = tpct + round(tpct*user['worker'][wn][1]['tips'])
                msg = msg.replace("TIP2", "$" + str(tpct))
                await self.add_money(user=ctx.author.id, count=tpct)
            elif 'TIP' in rm:
                tpc = random.randint(2,4)
                tpc *= ml
                tpc = round(tpc)
                if 'worker' in user:
                    if user['worker']:
                        wn = user['worker_name']
                        tpc = tpc + round(tpc*user['worker'][wn][1]['tips'])
                msg = msg.replace("TIP", "$" + str(tpc))
                await self.add_money(user=ctx.author.id, count=tpc)
            if r1['name'].endswith('s') or r1['name'].endswith('gna'):
                nn = r1['name']
            else:
                if r1['name'].startswith(("a", "e", "i", "o", "u")):
                    nn = "an " + r1['name']
                else:
                    nn = "a " + r1['name']
            msg = msg.replace(r1['name'], nn)
            await ctx.send(f"{ctx.author.mention}, {msg}")
        else:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant. Create one with `r!start`.")

    @commands.command(aliases=['Halloween', 'hlw'])
    @commands.cooldown(1, 21600, commands.BucketType.user)
    async def halloween(self, ctx):
        def check(m):
            return m.author == ctx.message.author
        await ctx.send(f"{ctx.author.mention}, You crossed a beautiful witch on your way to work. This could be bad! Do you wanna talk to her? (yes/no)")
        ans = await self.bot.wait_for('message', check=check, timeout=90)
        if ans.content.lower() == 'yes':
            rn = random.randint(1,3)
            if rn == 1:
                #BAD
                rnc = random.randint(1,2)
                if rnc == 1:
                    await ctx.send(f"Oh no! The witch put a late spell on you! You were 15 minutes late to work and lost 20 XP.")
                    await self.take_exp(user=ctx.author.id, count=20)
                elif rnc == 2:
                    await ctx.send(f"Oh no! The witch zapped your wallet out of your hand! You lost $15!")
                    await self.take_money(user=ctx.author.id, count=15)
            else:
                #GOOD
                rn2 = random.randint(1,6)
                if rn2 == 1:
                    db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"banner": {"name": "Take your heart", "url": "https://i.ibb.co/T0qtJbt/subsource-done-button-uid-9265-BBC3-1-BC1-4-FC9-9440-85008-F9-BEF32-1602184929808-source-other-origi.jpg",'rarity': 'Legendary'}}}})
                    desc = "Take your heart (Legendary) [View Banner](https://i.ibb.co/T0qtJbt/subsource-done-button-uid-9265-BBC3-1-BC1-4-FC9-9440-85008-F9-BEF32-1602184929808-source-other-origi.jpg)"
                elif rn2 == 2:
                    db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"banner": {"name": "Trick or Treat", "url": "https://i.ibb.co/Jv6Sjwg/subsource-done-button-uid-9265-BBC3-1-BC1-4-FC9-9440-85008-F9-BEF32-1602179605747-source-other-origi.jpg",'rarity': 'Rare'}}}})
                    desc = "Trick or Treat (Rare) [View Banner](https://i.ibb.co/Jv6Sjwg/subsource-done-button-uid-9265-BBC3-1-BC1-4-FC9-9440-85008-F9-BEF32-1602179605747-source-other-origi.jpg)"
                elif rn2 == 3:
                    db.market.update_one({"owner": ctx.author.id}, {"$push": {"inventory":{"banner": {"name": "Haunted", "url": "https://i.ibb.co/SVvXT90/source-sid-9265-BBC3-1-BC1-4-FC9-9440-85008-F9-BEF32-1602005240890-subsource-done-button-uid-9265-BB.jpg",'rarity': 'Rare'}}}})
                    desc = "Haunted (Rare) [View Banner](https://i.ibb.co/SVvXT90/source-sid-9265-BBC3-1-BC1-4-FC9-9440-85008-F9-BEF32-1602005240890-subsource-done-button-uid-9265-BB.jpg)"
                elif rn2 == 4 or rn2 == 5 or rn2 == 6:
                    rnm = random.randint(15,70)
                    await self.add_money(user=ctx.author.id, count=rnm)
                    desc = f"{rnm} Cash"
                embed = discord.Embed(colour=0x44165e, description=desc)
                embed.set_footer(text="Come back in 6 hours!")
                await ctx.send(embed=embed, content="The witch thought you were a kind soul and gave you an enchanted chest!")

        elif ans.content.lower() == 'no':
            await ctx.send("She sighed and walked away.")
            self.bot.get_command("spooky").reset_cooldown(ctx)
        else:
            await ctx.send("That's not an option! Example: `yes`")
            self.bot.get_command("spooky").reset_cooldown(ctx)


    @commands.group(aliases=['dsc', 'Discoin'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def discoin(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(colour=0xa82021, title="'Discoin' Command Group", description="Convert bot currencies from one to another bot, invest your earnings and get high returns!\n`r!discoin exchange <currency> <money-count>` - **Exchange Restaurant credits**\n`r!discoin bots` - **View all available bot currencies**")
            embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the command.")
            embed.set_thumbnail(url="https://avatars2.githubusercontent.com/u/30993376?s=200&v=4")
            await ctx.send(embed=embed)
            self.bot.get_command("discoin").reset_cooldown(ctx)

    @discoin.command(aliases=['Exchange'])
    async def exchange(self, ctx, toId, count : int):
        post = db.market.find_one({"owner": ctx.author.id})
        if not post:
            await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant yet! Create one with `r!create`")
        elif not post['money'] >= count:
            await ctx.send("<:RedTick:653464977788895252> You don't have enough to make that transaction!")
        else:
            r = await self.discoin_client.create_transaction(toId, count, ctx.author.id)
            embed = discord.Embed(colour=0xa82021, title="Exchange request sent", description=f"Exchanging ${count} for {r.payout} {toId}. \n\n[Track your transaction](https://dash.discoin.zws.im/#/transactions/{r.id}/show)")
            await ctx.send(embed=embed)
            await self.take_money(user=ctx.author.id, count=count)


    @discoin.command(aliases=['Bots'])
    async def bots(self, ctx):
        r = requests.get("https://discoin.zws.im/bots").json()
        desc = ""
        rbc_rate = 0
        for x in r:
            if x['currencies'][0]['id'] == "RBC":
                rbc_rate = x['currencies'][0]['value']
        for x in r:
            if not x['currencies'][0]['id'] == "RBC":
                name = x['name']
                id = x['currencies'][0]['id']
                uid = x['discord_id']
                rate = round(rbc_rate / x['currencies'][0]['value'], 4)
                desc += f"[{name}](https://top.gg/bot/{uid}) **ID:** `{id}` **Rate:** `$1 RBC = {rate} {id}`\n"
        embed = discord.Embed(colour=0xa82021, title="Available Bots Currencies", description=desc)
        await ctx.send(embed=embed)

    @commands.command(aliases=['bugreport'])
    async def reportbug(self, ctx, *, topic, option=None, description=None):
        if ctx.channel.id == 748162782586994728:
            await ctx.message.delete()
            args = topic.split('|')
            topic = args[0]
            option = args[1]
            description = args[2]
            if not description:
                await ctx.send(f"<:redtick:492800273211850767> {ctx.author.mention}, Incorrect Arguments. **Usage:** `r!reportbug <topic> <option> <description>` *Do not include < or > in your report.*", delete_after=10)
            if str(option).lower() not in ['major', 'minor', ' minor ', ' major ', 'minor ', 'major ', ' minor', ' major']:
                await ctx.send(f"<:redtick:492800273211850767> {ctx.author.mention}, Incorrect Arguments. Option must be either `Major` or `Minor`. Ex. `r!reportbug Help | Minor | description here`", delete_after=10)
            else:
                data = {
                        "name": description,
                        "desc": f'This is a user-submitted card.\n\n**Command/Topic:** {str(topic).capitalize()}\n\n**Description:** {description}\n\n**Submitted by:** {ctx.author} ({ctx.author.id})\n\n\nThis bug is **{str(option).upper()}**.',
                        "idList": '5f465a723958f77bdb8ca189',
                        "pos": 'top'
                }
                r = requests.post(f"https://api.trello.com/1/cards?key=4ae5477b485b5afa44ae72997bb53b54&token=ae0c71469c814c9335b57be7a35508f828e7d0f84af8adfa10fcce73888a49d6", data=data).json()
                trello_link = r['url']

                msg = await ctx.send(f"{ctx.author.mention}, your report has been sent! I've sent a transcipt to your DMs.", delete_after=10)

                embed = discord.Embed(colour=0x00f0ff, description="Bug Report Transcript")
                embed.add_field(name="Topic/Command:", value=str(topic).capitalize())
                embed.add_field(name="Option:", value=str(option).capitalize())
                embed.add_field(name="Description:", value=description)
                embed.add_field(name="Link:", value=trello_link)
                embed.set_footer(text="Thank you for submitting a bug!")
                await ctx.author.send(embed=embed)


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

    async def take_exp(self, user, count):
        data = db.market.find_one({"owner": user})
        bal = data['exp']
        exp = int(bal) - count
        db.market.update_one({"owner": user}, {"$set":{"exp": exp}})
        return count

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
        #if exp <= 500:
            #db.market.update_one({"owner": user.id}, {"$push": {"inventory":{"banner": {"name": "Lovely Hearts", "url": "http://paixlukee.ml/m/AEJSB.jpg", 'rarity': 'Legendary'}}}})
            #await bot.get_user(user).send("Congrats! You've hit 500 EXP with your restaurant! As a gift, the **Legendary** Lovely Hearts banner has been added to your inventory.")

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
    bot.add_cog(User(bot))
