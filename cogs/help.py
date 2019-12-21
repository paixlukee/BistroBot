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

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pr = 'r!'

    @commands.group(aliases=['cmds', 'commands', 'Help'])
    async def help(self, ctx, page=None):
        #keeping this hardcoded, because it will only make me do more work :)
        try:
            page = int(page.lower().replace("#", "").replace("page", ""))
        except:
            pass
        pages = [1,2,3,4]
        if not page or not page in pages: 
            embed = discord.Embed(colour=0xa82021, description="Welcome! Here is a list of commands that you are able to use.")
            embed.add_field(name="Page #1 | Restaurant", value="The main restaurant commands.")
            embed.add_field(name="Page #2 | User", value="Commands that interact with regular users.")
            embed.add_field(name="Page #3 | Inventory", value="Buy, use, and view items in your inventory.")
            embed.add_field(name="Page #4 | Bot", value="Commands that have to do with the main bot.")
            #embed.add_field(name="Page #4 | Configuration", value="Configurate guild-only settings,")
            embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Help Manual")
            embed.set_image(url="https://i.ibb.co/chxrYtn/restaurantbanner.png")
            embed.set_footer(text="To view a page, put the page number right after the command. Example: r!help 1")
            await ctx.send(embed=embed)
        elif page == 1:
            embed = discord.Embed(colour=0xa82021, description="The main restaurant commands.")
            embed.add_field(name=f"{self.pr}start", value="Create your restaurant")
            embed.add_field(name=f"{self.pr}restaurant [@user]", value="View your own restaurant")
            embed.add_field(name=f"{self.pr}rate <@user>", value="Rate a restaurant")
            embed.add_field(name=f"{self.pr}menu <restaurant-name>", value="View a restaurant menu")
            embed.add_field(name=f"{self.pr}set", value="Configurate your restaurant settings")
            embed.add_field(name=f"{self.pr}daily", value="Receive your daily cash")
            embed.add_field(name=f"{self.pr}work", value="Work at your restaurant and receive money")
            embed.add_field(name=f"{self.pr}clean", value="Clean your restaurant and receive EXP")
            embed.add_field(name=f"{self.pr}cook", value="Cook an item and receive EXP")
            embed.add_field(name=f"{self.pr}leaderboard", value="View the global restaurant leaderboard")
            embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Help Manual | Page 1")
            embed.set_image(url="https://i.ibb.co/chxrYtn/restaurantbanner.png")
            embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the command.")
            await ctx.send(embed=embed)
        elif page == 2:
            embed = discord.Embed(colour=0xa82021, description="Commands that interact with regular users.")
            embed.add_field(name=f"{self.pr}profile [@user]", value="View a user profile")
            embed.add_field(name=f"{self.pr}balance", value="View your balanece")
            embed.add_field(name=f"{self.pr}donate <@user> <amount>", value="Donate money to someone else")
            embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Help Manual | Page 2")
            embed.set_image(url="https://i.ibb.co/chxrYtn/restaurantbanner.png")
            embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the command.")
            await ctx.send(embed=embed)
        elif page == 3:
            embed = discord.Embed(colour=0xa82021, description="Buy, use, and view items in your inventory.")
            embed.add_field(name=f"{self.pr}inventory", value="View your inventory")
            embed.add_field(name=f"{self.pr}use <item>", value="View your balance")
            embed.add_field(name=f"{self.pr}buy", value="View shop and buy items")
            embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Help Manual | Page 3")
            embed.set_image(url="https://i.ibb.co/chxrYtn/restaurantbanner.png")
            embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the command.")
            await ctx.send(embed=embed)
        elif page == 4:
            embed = discord.Embed(colour=0xa82021, description="Commands that have to do with the main bot.")
            embed.add_field(name=f"{self.pr}ping", value="View the ping")
            embed.add_field(name=f"{self.pr}info", value="View information about Restaurant Bot")
            embed.add_field(name=f"{self.pr}invite", value="Get the invite URL")
            embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Restaurant Help Manual | Page 4")
            embed.set_image(url="https://i.ibb.co/chxrYtn/restaurantbanner.png")
            #embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the command.")
            await ctx.send(embed=embed)
        else:
            pass



def setup(bot):
    bot.add_cog(Help(bot))
