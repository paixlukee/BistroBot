import discord
from discord.ext import commands

import datetime

import time
import subprocess
import traceback
from discord.ext.commands import errors, converter
import requests
import random
from random import choice as rnd
from random import choice, randint

import aiohttp
import asyncio
import sys
import json
from pymongo import MongoClient
import pymongo
import config

client = MongoClient(config.mongo_client)
db = client['siri']

extensions = ['cogs.utility', 'cogs.help', 'cogs.economy', 'cogs.dev', 'cogs.music', 'cogs.server', 'cogs.levels']

class Botdev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def run_cmd(self, cmd: str) -> str:
         process =\
         await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
         results = await process.communicate()
         return "".join(x.decode("utf-8") for x in results)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down..")
        await self.bot.logout()

    @commands.command(hidden=True)
    async def pull(self, ctx):
        if ctx.author.id == 396153668820402197:
            msg = await ctx.send("Pulling..")
            shell = await self.run_cmd('git pull Res --no-commit --no-edit --ff-only master')
            shell = str(shell)
            shell = shell.replace("https://github.com/paixlukee/RestaurantBot", "Github")
            embed = discord.Embed(description=f"```css\n{shell}```")
            embed.set_author(name="Pulled from Git", icon_url="https://avatars0.githubusercontent.com/u/9919?s=280&v=4")
            await msg.delete()
            await ctx.send(embed=embed)
        else:
            pass

    @commands.command(hidden=True)
    async def ban(self, ctx, id:int, *, reason):
        if ctx.author.id == 396153668820402197:
            user = self.bot.get_user(id)
            await ctx.send(f"**{user}** was banned from using Restaurant.")
            db.utility.update_one({"utility": "banlist"}, {"$push":{"banned": user.id}})
            embed = discord.Embed(colour=0xa82021, description=f"You were banned from using **Restaurant**. Reason: `{reason}`\n\nIf you would like to appeal, visit http://paixlukee.ml/restaurant/appeal.html.")
            embed.set_image(url="http://paixlukee.ml/m/6UK4U.jpg")
            await user.send(embed=embed)
        else:
            pass

    @commands.command(hidden=True)
    async def shell(self, ctx, *, code):
        if ctx.author.id == 396153668820402197:
            embed = discord.Embed(description=f"```css\nConnecting to shell..```")
            embed.set_author(name="Please Wait.", icon_url=self.bot.user.avatar_url)
            msg = await ctx.send(embed=embed)
            shell = await self.run_cmd(code)
            embed = discord.Embed(description=f"```css\n{shell}```")
            embed.set_author(name="Shell", icon_url=self.bot.user.avatar_url)
            await msg.delete()
            await ctx.send(embed=embed)
        else:
            pass


    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Get Res's Ping"""
        t1 = time.perf_counter()
        await ctx.trigger_typing()
        t2 = time.perf_counter()
        await ctx.send("Pong! `" + str(round((t2-t1)*1000)) + "ms`")

    @commands.command()
    async def invite(self, ctx):
        await ctx.send("Invite me to your server! <https://discordapp.com/api/oauth2/authorize?client_id=648065060559781889&permissions=10240&scope=bot>")

    @commands.command(hidden=True)
    async def load(self, ctx, extension):
        if ctx.author.id == 396153668820402197:
            try:
                if extension == 'all':
                    print('\x1b[1;36;40m' + '[UPDATE]: ' + '\x1b[0m' + 'Loaded all modules')
                    print("------\n\n")
                    loaded = []
                    not_loaded = []
                    for extension in extensions:
                        try:
                            self.bot.load_extension(extension)
                            loaded.append(f'`{extension}`')
                        except Exception as error:
                            not_loaded.append(f'`{extension}` - `{error}`')
                            print('\x1b[1;31;40m' + '[COG-LOAD-ERROR]: ' + '\x1b[0m' + '{} was not loaded due to an error: {} '.format(extension, error))

                    loaded = '\n'.join(loaded)
                    not_loaded = '\n'.join(not_loaded)
                    embed = discord.Embed(colour=0x0000ff)
                    embed.add_field(name='Loaded', value=loaded)
                    if not_loaded is None:
                        embed.add_field(name='Not Loaded', value=not_loaded)
                    await ctx.send(embed=embed)
                else:
                    self.bot.load_extension("cogs.{}".format(extension))
                    embed = discord.Embed(title="<:CheckMark:473276943341453312> Cog loaded:", color=0x5bff69, description="**Cog:** `cogs\{}.py`".format(extension))
                    await ctx.send(embed=embed)
                    print('\n\nCOG LOAD\n--[Cog loaded, {}.py]--\n\n'.format(extension))
            except Exception as error:
                print('\n\nEXTEN./COG ERROR: {} was not loaded due to an error: \n-- [{}] --\n\n'.format(extension, error))
                embed = discord.Embed(title="<:WrongMark:473277055107334144> Error loading cog:", color=0xff775b, description="**Cog:** `cogs\{}.py`\n**Errors:**\n```{}```".format(extension, error))
                await ctx.send(embed=embed)
        else:
            pass

    @commands.command(aliases=['un'], hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension):
        self.bot.unload_extension("cogs.{}".format(extension))
        embed = discord.Embed(title="<:CheckMark:473276943341453312> Cog unloaded:", color=0x5bff69, description="**Cog:** `cogs\{}.py`".format(extension))
        print('\x1b[1;32;40m' + '[COG-RELOADED]: ' + '\x1b[0m' + '{} was unloaded successfully'.format(extension))
        await ctx.send(embed=embed)


    @commands.command(aliases=['re'], hidden=True)
    async def reload(self, ctx, extension):
        if ctx.author.id == 396153668820402197:
            try:
                self.bot.unload_extension("cogs.{}".format(extension))
                self.bot.load_extension("cogs.{}".format(extension))
                embed = discord.Embed(title="<:CheckMark:473276943341453312> Cog reloaded:", color=0x5bff69, description="**Cog:** `cogs\{}.py`".format(extension))
                await ctx.send(embed=embed)
                print('\x1b[1;32;40m' + '[COG-RELOADED]: ' + '\x1b[0m' + '{} was reloaded successfully'.format(extension))
            except Exception as error:
                print('\x1b[1;31;40m' + '[COG-RELOAD-ERROR]: ' + '\x1b[0m' + '{} was not reloaded due to an error: {} '.format(extension, error))
                embed = discord.Embed(title="<:WrongMark:473277055107334144> Error reloading cog:", color=0xff775b, description="**Cog:** `cogs\{}.py`\n**Errors:**\n```{}```".format(extension, error))
                await ctx.send(embed=embed)
        else:
            pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("<:RedTick:653464977788895252> You are not authorised to use this command!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"<:RedTick:653464977788895252> Error! {error}")
        elif isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            if hours >= 1:
                hours = f"{round(hours)}h"
            else:
                hours = ""
            await ctx.send(f"<:RedTick:653464977788895252> You are on cooldown! Please wait **{hours} {round(minutes)}m {round(seconds)}s**.")
        elif isinstance(error, commands.CommandInvokeError):
            error = getattr(error, 'original', error)
            if str(error).startswith("403"):
                await ctx.author.send(f"I need the `send_messages` permission to speak in **#{ctx.channel.name}**!")
        else:
            print("\x1b[1;31;40m" + f"[{type(error).__name__}]: " + "\x1b[0m" + str(error))
            ig = (asyncio.futures.TimeoutError, commands.CommandNotFound, commands.CommandOnCooldown, discord.Forbidden, commands.NoPrivateMessage, commands.DisabledCommand, commands.CheckFailure, commands.UserInputError)
            error = getattr(error, 'original', error)
            if isinstance(error, ig):
                return
            embed = discord.Embed(colour=0xa82021)
            embed.set_author(icon_url=ctx.me.avatar_url_as(format='png'), name="Command Error")
            embed.set_footer(text=f"Type: {type(error).__name__.upper()}")
            description = f"**Command**: {ctx.command.qualified_name}\n"\
                          f"**Author**: {ctx.author} `ID: {ctx.author.id}`\n"\
                          f"**Channel**: #{ctx.channel} `ID: {ctx.channel.id}`"
            if ctx.guild:
                description += f'\n**Guild**: {ctx.guild} `ID: {ctx.guild.id}`'
            fe = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=False))
            description += f'\n```py\n{fe}\n```'
            embed.description = description
            embed.timestamp = datetime.datetime.utcnow()
            await self.bot.get_channel(658708974836645888).send(embed=embed)



def setup(bot):
    bot.add_cog(Botdev(bot))
