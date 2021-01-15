import discord
from discord.ext import commands
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

async def get_pre(bot, message):
    posts = db.utility.find_one({"utility": "prefixes"})
    pref = "r!"
    for x in posts['prefixes']:
        if x['guild'] == message.guild.id:
            pref = x['prefix']
    return pref

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['V2'])
    async def v2(self, ctx):
        description = "Introducing... **Res V2**\n\n"\
                      "I am so glad we made it so far... 1.2k servers! I hope you enjoy this update and updates yet to come. Now here are the changes...!\n\n"\
                      "__**New Commands:**__\n"\
                      "`r!hire` - Hire an employee to help you work!\n"\
                      "`r!worker` - Manage your employee\n"\
                      "`r!discoin` - Manage discoin transactions\n\n"\
                      "*Wait... what's discoin?* To put it into simple terms... Its a way to convert restaurant currency to currency on others bots! To view available currencies, do `r!discoin bots`.\n\n"\
                      "__**Command Changes**__\n"\
                      "- Beg command cooldown is now 90 seconds instead of 60 seconds\n"\
                      "- Work command is now 7 minutes instead of 8 minutes\n"\
                      "- There are 8 new colours, 6 new banners, 7 new trivia questions, and 3 new work responses\n\n"\
                      "__**Style Changes**__\n"\
                      "- New banner for help command\n"\
                      "- Links have been put onto the help command\n"\
                      "- Emoji \"<:RedTick:653464977788895252>\" has been added to all error messages\n\n"\
                      "__**Bug Fixes**__\n"\
                      "- Fixed an error that would stop cooldowns from resetting on some errors\n"\
                      "- Fixed an error where sometimes the `r!daily` command wouldn't give you any money.\n"
        embed = discord.Embed(description=description)
        embed.set_footer(text="from lukee#0420", icon_url="https://images-ext-2.discordapp.net/external/_ULuCbUCIqYZnsc6J04zIVeuKvDhm6HlCxF6ZU0v338/%3Fsize%3D256%26f%3D.gif/https/cdn.discordapp.com/avatars/396153668820402197/a_802dfb76b03607e983c0dd7b171aa3d8.gif")
        await ctx.send(embed=embed)

    @commands.group(aliases=['cmds', 'commands', 'Help', 'h', '?'])
    async def help(self, ctx, page=None):
        #keeping this hardcoded, because it will only make me do more work :)
        post = db.market.find_one({"owner": ctx.author.id})
        pre = get_pre(bot, ctx.message)
        try:
            page = int(page.lower().replace("#", "").replace("page", ""))
        except:
            pass
        pages = [1,2,3,4]
        if not page or not page in pages:
            if not post:
                an = "It seems that you don't have a restaurant, do `r!start` to make one."
            else:
                an = ""
            embed = discord.Embed(colour=0xa82021, description=f"Welcome! Here is a list of commands that you are able to use. {an}")
            embed.add_field(name="Page #1 | Restaurant", value="The main restaurant commands.")
            embed.add_field(name="Page #2 | User", value="Commands that interact with regular users.")
            embed.add_field(name="Page #3 | Inventory", value="Buy, use, and view items in your inventory.")
            embed.add_field(name="Page #4 | Bot", value="Commands that have to do with the main bot.")
            #embed.add_field(name="EVENT! | Halloween", value="`r!eventinfo`\n`r!halloween`")
            embed.add_field(name="Links", value="[DBL](https://top.gg/bot/648065060559781889)\n[Donate](https://www.patreon.com/paixlukee)\n[Support Server](http://discord.gg/BCRtw7c)")
            #embed.add_field(name="Page #4 | Configuration", value="Configurate guild-only settings,")
            embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Help Manual")
            embed.set_image(url="http://paixlukee.dev/m/SUG3O.png")#reg: http://paixlukee.dev/m/FGGUC.png")
            embed.set_footer(text="To view a page, put the page number right after the command. Example: r!help 1")
            await ctx.send(embed=embed)
        elif page == 1:
            embed = discord.Embed(colour=0xa82021, description="The main restaurant commands.")
            embed.add_field(name=f"{pre}start", value="Create your restaurant")
            embed.add_field(name=f"{pre}restaurant [restaurant]", value="View your own restaurant")
            embed.add_field(name=f"{pre}rate <@user>", value="Rate a restaurant")
            embed.add_field(name=f"{pre}menu <restaurant>", value="View a restaurant menu")
            embed.add_field(name=f"{pre}set", value="Configurate your restaurant settings")
            embed.add_field(name=f"{pre}daily", value="Receive your daily cash")
            embed.add_field(name=f"{pre}work", value="Work at your restaurant and receive money")
            embed.add_field(name=f"{pre}beg", value="Beg the bank to give you a grant")
            embed.add_field(name=f"{pre}clean", value="Clean your restaurant and receive EXP")
            embed.add_field(name=f"{pre}cook", value="Cook an item and receive EXP")
            embed.add_field(name=f"{pre}fish", value="Go fishing and get money & EXP.")
            embed.add_field(name=f"{pre}trivia", value="Play trivia and earn money.")
            embed.add_field(name=f"{pre}leaderboard", value="View the global restaurant leaderboard")
            embed.add_field(name=f"{pre}hire", value="Hire an employee to help you work")
            embed.add_field(name=f"{pre}worker", value="View how your employee is doing")
            embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Help Manual | Page 1")
            embed.set_image(url="http://paixlukee.dev/m/FGGUC.png")
            embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the command.")
            await ctx.send(embed=embed)
        elif page == 2:
            embed = discord.Embed(colour=0xa82021, description="Commands that interact with regular users.")
            embed.add_field(name=f"{pre}profile [@user]", value="View a user profile")
            embed.add_field(name=f"{pre}balance", value="View your balance")
            embed.add_field(name=f"{pre}donate <@user> <amount>", value="Donate money to someone else")
            embed.add_field(name=f"{pre}dine <restaurant>", value="Dine at a restaurant and gain EXP")
            embed.add_field(name=f"{pre}donation", value="Donate to the bot")
            embed.add_field(name=f"{pre}discoin", value="Manage discoin transactions")
            embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Help Manual | Page 2")
            embed.set_image(url="http://paixlukee.dev/m/FGGUC.png")
            embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the command.")
            await ctx.send(embed=embed)
        elif page == 3:
            embed = discord.Embed(colour=0xa82021, description="Buy, use, and view items in your inventory.")
            embed.add_field(name=f"{pre}inventory", value="View your inventory")
            embed.add_field(name=f"{pre}use <item>", value="View your balance")
            embed.add_field(name=f"{pre}buy", value="View shop and buy items")
            embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Help Manual | Page 3")
            embed.set_image(url="http://paixlukee.dev/m/FGGUC.png")
            embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the command.")
            await ctx.send(embed=embed)
        elif page == 4:
            embed = discord.Embed(colour=0xa82021, description="Commands that have to do with the main bot.")
            embed.add_field(name=f"{pre}ping", value="View the ping")
            embed.add_field(name=f"{pre}info", value="View information about Restaurant Bot")
            embed.add_field(name=f"{pre}invite", value="Get the invite URL")
            embed.add_field(name=f"{pre}prefix <new-prefix>", value="Set server prefix. (requires `manage_server` permissions)")
            embed.add_field(name=f"{pre}patrons", value="View all of the current patrons")
            embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Help Manual | Page 4")
            embed.set_image(url="http://paixlukee.ml/m/FGGUC.png")
            #embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the command.")
            await ctx.send(embed=embed)
        else:
            pass



def setup(bot):
    bot.add_cog(Help(bot))
