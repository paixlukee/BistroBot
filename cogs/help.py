import discord
from discord.ext import commands
import datetime
import requests
import random
import math
import time
from discord.ext.commands import errors, converter
from discord import app_commands
from random import choice, randint
from random import choice, randint as rnd
import aiohttp
import asyncio
import json
import os
import config
from pymongo import MongoClient
import pymongo
from discord.ui import View, Button

client = MongoClient(config.mongo_client)
db = client['siri']

async def get_pre(bot, message):
    posts = db.utility.find_one({"utility": "prefixes"})
    pref = "/"#"b." <<<------------- DIS !!!!
    for x in posts['prefixes']:
        if x['guild'] == message.guild.id:
            pref = x['prefix']
    return pref



# CHANGE PREFIX ASAP AFTEER!
#
#      AHHHHHHHHHHHHH
#
#           !!!!

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_group(name="help")
    async def help_menu(self, ctx: commands.Context, page=None):
        """View Bistro's help menu"""
        try:
            #keeping this hardcoded, because it will only make me do more work :)
            print('\nSTART\n')
            post = db.market.find_one({"owner": ctx.author.id})
            content = None
            embed = discord.Embed(color=0x8980d9)
            embed.set_image(url="https://media.discordapp.net/attachments/1325282246181130330/1325282279689289788/E46C7244-B665-48E2-B1A5-46A671413153.jpg?ex=677b38ce&is=6779e74e&hm=bd4d2f636a706e6a6aac44aec429884b1a121ff43d9f3f4d155238e14bbcd6af&=&format=webp&width=1140&height=1046")
            embed.set_footer(text="Click a page # to view it | bistrobot.co/documentation")
            view = pageBtns()
            print('\nSEC!\n')
            if not post:
                content = f"You must start a restaurant with `b.start` to play Bistro!"
            await ctx.send(content=content, embed=embed, view=view)
        except Exception as e:
            print(e)



class pageBtns(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(discord.ui.Button(label="Support", url="https://discord.gg/BCRtw7c"))
        self.add_item(discord.ui.Button(label="Donate", url="https://www.patreon.com/join/paixlukee"))

    @discord.ui.button(label="1", style=discord.ButtonStyle.primary)
    async def page_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot = interaction.client
        post = db.market.find_one({"owner": interaction.user.id})
        pre = await get_pre(bot, interaction.message)
        embed = discord.Embed(colour=0x8980d9, description="The main restaurant commands.")
        embed.add_field(name=f"{pre}start", value="Create your restaurant")
        embed.add_field(name=f"{pre}restaurant [restaurant]", value="View a restaurant")
        embed.add_field(name=f"{pre}rate <@user>", value="Rate a restaurant")
        embed.add_field(name=f"{pre}menu <restaurant>", value="View a restaurant menu")
        embed.add_field(name=f"{pre}set", value="Configure your restaurant settings")
        embed.add_field(name=f"{pre}daily", value="Receive your daily cash")
        embed.add_field(name=f"{pre}work", value="Work at your restaurant and receive money")
        embed.add_field(name=f"{pre}beg", value="Beg the bank to give you a grant")
        embed.add_field(name=f"{pre}clean", value="Clean your restaurant and receive EXP")
        embed.add_field(name=f"{pre}cook", value="Cook an item and receive EXP")
        embed.add_field(name=f"{pre}fish", value="Go fishing and get money & EXP. Your rod has a chance of breaking per use.")
        embed.add_field(name=f"{pre}trivia", value="Play trivia and earn money")
        embed.add_field(name=f"{pre}slots", value="Use your income on a slot machine (Silver+ Patrons)")
        embed.add_field(name=f"{pre}leaderboard [page | restaurant]", value="View the global Bistro leaderboard")
        embed.add_field(name=f"{pre}hire", value="Hire an employee to help you work")
        embed.add_field(name=f"{pre}workers", value="View how your employees are doing")
        embed.add_field(name=f"{pre}advertise", value="Advertise your restaurant")
        embed.add_field(name=f"{pre}cookoff", value="Start a cook-off with other players")
        embed.add_field(name=f"{pre}event", value="Host an event")
        embed.add_field(name=f"{pre}stones", value="View and fuse *Enhancement Stones*")
        embed.add_field(name=f"{pre}tasks", value="View your weekly tasks")
        embed.set_author(icon_url=bot.user.avatar.with_format('png'), name="Bistro Help Manual | Page 1")
        embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the actual command.")
        await interaction.response.edit_message(embed=embed)


    @discord.ui.button(label="2", style=discord.ButtonStyle.primary)
    async def page_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot = interaction.client
        post = db.market.find_one({"owner": interaction.user.id})
        pre = await get_pre(bot, interaction.message)
        embed = discord.Embed(colour=0x8980d9, description="Commands that interact with regular users.")
        embed.add_field(name=f"{pre}profile [@user]", value="View a user profile")
        embed.add_field(name=f"{pre}balance", value="View your balance")
        embed.add_field(name=f"{pre}stats", value="View all user & restaurant stats")
        embed.add_field(name=f"{pre}awards", value="View your attainable rewards")
        embed.add_field(name=f"{pre}level", value="View level stats and how to level up.")
        embed.add_field(name=f"{pre}levelunlocks", value="View what each level unlocks")
        embed.add_field(name=f"{pre}donate <@user> <amount>", value="Donate money to another user")
        embed.add_field(name=f"{pre}dine <restaurant>", value="Dine at a restaurant and gain EXP")
        embed.add_field(name=f"{pre}donation", value="Donate to the bot")
        embed.set_author(icon_url=bot.user.avatar.with_format('png'), name="Bistro Help Manual | Page 2")
        embed.set_image(url="https://media.discordapp.net/attachments/1325282246181130330/1328917037409374208/FF17CB1B-C653-4A06-A490-7BB9C4A38DFE.jpg?ex=678871ef&is=6787206f&hm=dba385547438a9343cd1c9c63b12a2b3e83af6c91ab06b9b0779d78e1d80142d&=&format=webp&width=2160&height=474")
        embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the command.")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="3", style=discord.ButtonStyle.primary)
    async def page_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot = interaction.client
        post = db.market.find_one({"owner": interaction.user.id})
        pre = await get_pre(bot, interaction.message)
        embed = discord.Embed(colour=0x8980d9, description="Buy, use, and view items in your inventory.")
        embed.add_field(name=f"{pre}inventory", value="View your inventory")
        embed.add_field(name=f"{pre}use <item>", value="Use or equip an item")
        embed.add_field(name=f"{pre}buy", value="View shop and buy items")
        embed.add_field(name=f"{pre}buy chest", value="Buy a chest filled with random rewards")
        embed.add_field(name=f"{pre}buy custom", value="Buy a customization chest")
        embed.add_field(name=f"{pre}buy food", value="Buy a new food item for your meneu")
        embed.add_field(name=f"{pre}buy item", value="Buy an item")
        embed.set_author(icon_url=bot.user.avatar.with_format('png'), name="Bistro Help Manual | Page 3")
        embed.set_image(url="https://media.discordapp.net/attachments/1325282246181130330/1328917037409374208/FF17CB1B-C653-4A06-A490-7BB9C4A38DFE.jpg?ex=678871ef&is=6787206f&hm=dba385547438a9343cd1c9c63b12a2b3e83af6c91ab06b9b0779d78e1d80142d&=&format=webp&width=2160&height=474")
        embed.set_footer(text="Arguments are inside [] and <>. [] is optional and <> is required. Do not include [] or <> in the command.")
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="4", style=discord.ButtonStyle.primary)
    async def page_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot = interaction.client
        post = db.market.find_one({"owner": interaction.user.id})
        pre = await get_pre(bot, interaction.message)
        embed = discord.Embed(colour=0x8980d9, description="Commands that have to do with the main bot.")
        embed.add_field(name=f"{pre}ping", value="View the bot's ping")
        embed.add_field(name=f"{pre}info", value="View information about BistroBot")
        embed.add_field(name=f"{pre}invite", value="Get the invite URL")
        embed.add_field(name=f"{pre}prefix <new-prefix>", value="Set server prefix. (requires `manage_server` permissions)")
        embed.add_field(name=f"{pre}cooldowns", value="Check what commands have cooldowns")
        embed.set_author(icon_url=bot.user.avatar.with_format('png'), name="Bistro Help Manual | Page 4")
        embed.set_image(url="https://media.discordapp.net/attachments/1325282246181130330/1328917037409374208/FF17CB1B-C653-4A06-A490-7BB9C4A38DFE.jpg?ex=678871ef&is=6787206f&hm=dba385547438a9343cd1c9c63b12a2b3e83af6c91ab06b9b0779d78e1d80142d&=&format=webp&width=2160&height=474")
        await interaction.response.edit_message(embed=embed)



async def setup(bot):
    await bot.add_cog(Help(bot))