import discord
from discord.ext import commands

import datetime
import string
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

    async def get_shard(ctx, id):
        sr = id-1
        guilds = []
        for x in ctx.bot.guilds:
            if x.shard_id == sr:
                guilds.append(x)
        return len(guilds)

    async def run_cmd(self, cmd: str) -> str:
         process =\
         await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
         results = await process.communicate()
         return "".join(x.decode("utf-8") for x in results)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            embed = discord.Embed(colour=0x8980d9, description="Please take the time to fill out [this exit form](https://forms.gle/wkMNiSanpnpeLTt88). Thanks for using Bistro Bot.")
            embed.set_author(name="Goodbye!")
            await self.bot.get_user(guild.owner.id).send(embed=embed)
        except:
            pass



    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down..")
        await self.bot.logout()

    @commands.command(hidden=True)
    async def pull(self, ctx):
        if ctx.author.id == 396153668820402197:
            msg = await ctx.send("Pulling..")
            shell = await self.run_cmd('git pull Bistro --no-commit --no-edit --ff-only master')
            shell = str(shell)
            shell = shell.replace("https://github.com/paixlukee/BistroBot", "Github")
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
            await ctx.send(f"**{user}** was banned from using Bistro.")
            db.utility.update_one({"utility": "banlist"}, {"$push":{"banned": user.id}})
            embed = discord.Embed(colour=0x8980d9, description=f"You were banned from using **Bistro**. Reason: `{reason}`\n\nIf you would like to appeal, visit http://paixlukee.ml/restaurant/appeal.html.")
            embed.set_image(url="http://paixlukee.ml/m/6UK4U.jpg")
            await user.send(embed=embed)
        else:
            pass

    @commands.command(hidden=True)
    async def shell(self, ctx, *, code):
        if ctx.author.id == 396153668820402197:
            embed = discord.Embed(description=f"```css\nConnecting to shell..```")
            embed.set_author(name="Please Wait.", icon_url=ctx.me.avatar.with_format('png'))
            msg = await ctx.send(embed=embed)
            shell = await self.run_cmd(code)
            embed = discord.Embed(description=f"```css\n{shell}```")
            embed.set_author(name="Shell", icon_url=ctx.me.avatar.with_format('png'))
            await msg.delete()
            await ctx.send(embed=embed)
        else:
            pass


    @commands.hybrid_command(pass_context=True)
    async def ping(self, ctx: commands.Context):
        """Pong! View Bistro's ping"""
        t1 = time.perf_counter()
        await ctx.typing()
        t2 = time.perf_counter()
        ping = str(round((t2-t1)*1000))
        ol = round(ctx.bot.latency * 1000)
        sl = round(ctx.bot.latency * 1000)
        tl = round(ctx.bot.latency * 1000)
        if ol >= 90:
            oe = '<:idle:701016198531383316>'
        else:
            oe = '<:online:701012643263283242>'
        if sl >= 90:
            se = '<:idle:701016198531383316>'
        else:
            se = '<:online:701012643263283242>'
        if tl >= 90:
            te = '<:idle:701016198531383316>'
        else:
            te = '<:online:701012643263283242>'
        oc = await self.get_shard(1)
        sc = await self.get_shard(2)
        tc = await self.get_shard(3)
        shard = ctx.guild.shard_id + 1
        embed = discord.Embed(colour=0x8980d9, description=f"The ping for **{ctx.guild.name}** is `{ping}ms`.")
        embed.set_author(name="Pong!", icon_url=ctx.bot.user.avatar.url)
        embed.add_field(name=f"{oe} Shard #1", value=f"`{ol}ms`  `{oc} servers`")
        embed.add_field(name=f"{se} Shard #2", value=f"`{sl}ms`  `{sc} servers`")
        embed.add_field(name=f"{te} Shard #3", value=f"`{tl}ms`  `{tc} servers`")
        embed.set_footer(text=f"Shard ID: #{shard}")
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def invite(self, ctx: commands.Context):
        """Get Bistro's invite URL"""
        await ctx.send("Invite me to your server! <https://discord.com/oauth2/authorize?client_id=657037653346222102&permissions=274878180416&integration_type=0&scope=bot>")

    @commands.command(hidden=True)
    async def load(self, ctx, extension):
        print("\nLOAD INIT!\n")
        if ctx.author.id == 396153668820402197:
            try:
                if extension == 'all':
                    print('\x1b[1;36;40m' + '[UPDATE]: ' + '\x1b[0m' + 'Loaded all modules')
                    print("------\n\n")
                    loaded = []
                    not_loaded = []
                    for extension in extensions:
                        try:
                            await self.bot.load_extension(extension)
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
                    await self.bot.load_extension("cogs.{}".format(extension))
                    embed = discord.Embed(title="Cog loaded!", color=0x5bff69, description="<:CheckMark:1330789181470937139> **Cog:** `cogs\\{}.py`".format(extension))
                    await ctx.send(embed=embed)
                    print('\n\nCOG LOAD\n--[Cog loaded, {}.py]--\n\n'.format(extension))
            except Exception as error:
                print('\n\nEXTEN./COG ERROR: {} was not loaded due to an error: \n-- [{}] --\n\n'.format(extension, error))
                embed = discord.Embed(title="<:RedTick:653464977788895252> Error loading cog:", color=0xff775b, description="**Cog:** `cogs\\{}.py`\n**Errors:**\n```{}```".format(extension, error))
                await ctx.send(embed=embed)
        else:
            pass

    @commands.command(aliases=['un'], hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension):
        await self.bot.unload_extension("cogs.{}".format(extension))
        embed = discord.Embed(title="Cog unloaded!", color=0x5bff69, description="<:CheckMark:1330789181470937139> **Cog:** `cogs\\{}.py`".format(extension))
        print('\x1b[1;32;40m' + '[COG-RELOADED]: ' + '\x1b[0m' + '{} was unloaded successfully'.format(extension))
        await ctx.send(embed=embed)


    @commands.command(aliases=['re'], hidden=True)
    async def reload(self, ctx, extension):
        if ctx.author.id == 396153668820402197:
            try:
                await ctx.typing()
                await self.bot.unload_extension("cogs.{}".format(extension))
                await asyncio.sleep(1)
                await self.bot.load_extension("cogs.{}".format(extension))
                embed = discord.Embed(title="Cog reloaded!", color=0x5bff69, description="<:CheckMark:1330789181470937139> **Cog:** `cogs\\{}.py`".format(extension))
                try:
                    await self.bot.tree.sync()
                    embed.set_footer(text="All commands have been synced!")
                except Exception as e:
                    await ctx.send(f":warning: **SYNC ERROR**! {e}")
                await ctx.send(embed=embed)
                print('\x1b[1;32;40m' + '[COG-RELOADED]: ' + '\x1b[0m' + '{} was reloaded successfully'.format(extension))
            except Exception as error:
                print('\x1b[1;31;40m' + '[COG-RELOAD-ERROR]: ' + '\x1b[0m' + '{} was not reloaded due to an error: {} '.format(extension, error))
                embed = discord.Embed(title="<:RedTick:653464977788895252> Error reloading cog:", color=0xff775b, description="**Cog:** `cogs\\{}.py`\n**Errors:**\n```{}```".format(extension, error))
                await ctx.send(embed=embed)
        else:
            pass

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error): # <:RedTick:653464977788895252>
        if isinstance(error, commands.NotOwner):
            await ctx.send("<:RedTick:653464977788895252> You are not authorised to use this command!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"<:RedTick:653464977788895252> Error! `{error}`")
        elif isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            if hours >= 1:
                hours = f"{round(hours)}h"
            else:
                hours = ""
            await ctx.send(f"<:RedTick:653464977788895252> You are on cooldown! Please wait **{hours} {round(minutes)}m {round(seconds)}s**.")

        else:
            id = ''.join([random.choice(string.digits) if i % 2 == 0 else random.choice(string.ascii_letters) for i in range(7)])
            print("\x1b[1;31;40m" + f"[{type(error).__name__}]: " + "\x1b[0m" + str(error))
            ig = (TimeoutError, commands.CommandNotFound, commands.CommandOnCooldown, discord.Forbidden, commands.NoPrivateMessage, commands.DisabledCommand, commands.CheckFailure, commands.UserInputError)
            error = getattr(error, 'original', error)
            if isinstance(error, ig):
                return
            embed = discord.Embed(colour=0xff0000)
            embed.set_author(icon_url=ctx.bot.user.avatar.url, name="Command Error")
            embed.set_footer(text=f"Type: {type(error).__name__.upper()}")
            description = f"**Command**: {ctx.command.qualified_name}\n"\
                          f"**Author**: {ctx.author} `ID: {ctx.author.id}`\n"\
                          f"**Channel**: #{ctx.channel} `ID: {ctx.channel.id}`\n"\
                          f"**Error ID:** {id}"
            if ctx.guild:
                description += f'\n**Guild**: {ctx.guild} `ID: {ctx.guild.id}`'
            fe = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=False))
            desc = f"ERROR:\n\n{fe}"
            description += f'\n```py\n{fe}\n```'
            embed.description = description
            embed.timestamp = datetime.datetime.utcnow()
            try:
                r = requests.post(f"https://hastebin.com/documents", data=str(desc).encode('utf-8')).json()
                await self.bot.get_channel(658708974836645888).send(content=f"<https://hastebin.com/{r['key']}>")
            except:
                pass
            try:
                await self.bot.get_channel(658708974836645888).send(embed=embed)
                await ctx.send(f"<:RedTick:653464977788895252> Error! Please see our [Support Server](https://discord.gg/BCRtw7c) for more information. `Code: {id}`")
            except:
                pass
            if isinstance(error, commands.CommandInvokeError):
                error = getattr(error, 'original', error)
                if str(error).startswith("403"):
                    await ctx.author.send(f"I need the `send_messages` permission to speak in **#{ctx.channel.name}**!")



async def setup(bot):
    cog = Botdev(bot)
    await bot.add_cog(cog)
