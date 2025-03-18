import discord
from discord.ext import commands, tasks
import datetime
import random
import math
import time
from discord.ext.commands import errors, converter
from random import randint, choice as rnd
import asyncio
import json
import os
import config
from pymongo import MongoClient
import pymongo
import string
import requests
import motor.motor_asyncio
import trivia
import awards
from discord.ui import View, Button

client = motor.motor_asyncio.AsyncIOMotorClient(config.mongo_client)
db = client['siri']

bbux = "<:BistroBux:1324936072760786964>"

class Cookoff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_jmsg = None
        self.contest_msg = None
        self.gamestart_msg = None
        self.players = {}
        self.bet_amount = 0
        self.game_host = None

    @commands.hybrid_group(name="cookoff")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def contest(self, ctx: commands.Context):
        """Start a cooking challenge with other members"""
        if ctx.invoked_subcommand is None:
            post = await db.market.find_one({"owner": ctx.author.id})
            if post:
                embed = discord.Embed(colour=0x8980d9, description=f"Welcome to **Bistro Cook-Off**!\n\nThis is your chance to show the world what you're made of! "
                                    f"Play with up to 3 other people. You can bet up to {bbux}50, and the winner takes it all. Once started, you will play three minigame rounds in your DMs."
                                    "\n\nWanna give it a go? Hit `Create Game` below to start a game.")
                embed.set_image(url="https://media.discordapp.net/attachments/1325282246181130330/1329331828859076622/phonto.png?ex=6789f43d&is=6788a2bd&hm=7edc4d7b1d8874a61022a15dd74aba7201d6f516fa2b9f9374e0145d7a01484d&=&format=webp&quality=lossless&width=2160&height=462")
                view = pageBtns(self)
                self.contest_msg = await ctx.send(embed=embed, view=view)
            else:
                await ctx.send("<:RedTick:653464977788895252> You don't have a restaurant! Create one with `b.start`")

    @contest.hybrid_command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def start(self, ctx: commands.Context):
        """Start a cookoff"""
        if not self.game_jmsg:
            await ctx.send("<:RedTick:653464977788895252> There is no game to start! Start one with `b.cookoff`")
            return
        elif ctx.author.id != self.game_host:
            await ctx.send("<:RedTick:653464977788895252> Only the host can start the game!")
            return
        elif len(self.players) < 2:
            await ctx.send("<:RedTick:653464977788895252> Not enough players! You need at least 2 players to start the game.")
            return
        
        embed = discord.Embed(colour=0x8980d9, description=f"The game starts in 15 seconds!\n\n **Players:**\n * {'\n* '.join([str(ctx.guild.get_member(player_id).name) for player_id in self.players])}")
        embed.set_footer(text="The game will start in your DMs soon!")
        await self.game_jmsg.delete()
        self.gamestart_msg = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await self.start_game(ctx)

    async def start_game(self, ctx):
        tasks = [] 
        for player_id in self.players:
            player = ctx.guild.get_member(player_id)
            self.players[player_id] = {"points": 0} 
            await self.take_money(user=player_id, count=self.bet_amount)
            if player:
                post = await db.market.find_one({"owner": player.id})
                tasks.append(self.ask_questions(ctx, player))

        await asyncio.gather(*tasks)
        await asyncio.sleep(2)
        await self.determine_winner(ctx)
                
    async def ask_questions(self, ctx, player):
        post = await db.market.find_one({"owner": player.id})
        player_id = player.id
        await player.send("The game is starting in 10 seconds. Get ready!")
        await asyncio.sleep(10)
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
        embed = discord.Embed(colour=0x8980d9, description=f"Unscramble this item on your menu to start making it: `{sw}`")
        embed.set_footer(text=f"Round 1  |  Points: {self.players[player_id]["points"]}")
        await player.send(embed=embed)
        b = time.perf_counter()
        try:
            resp = await self.bot.wait_for('message', check=lambda m: m.author == player, timeout=20)
            a = time.perf_counter()
            tt = a-b
            round_one_pts = 0
            if tt <= 4:
                if resp.content.lower() == word.lower():
                    round_one_pts = 100
                else:
                    round_one_pts = 20
            elif tt < 7:
                if resp.content.lower() == word.lower():
                    round_one_pts = 90
                else:
                    round_one_pts = 15
            elif tt < 10:
                if resp.content.lower() == word.lower():
                    round_one_pts = 80
                else:
                    round_one_pts = 10
            elif tt < 13:
                if resp.content.lower() == word.lower():
                    round_one_pts = 70
                else:
                    round_one_pts = 0
            else:
                if resp.content.lower() == word.lower():
                    round_one_pts = 20
                else:
                    round_one_pts = 0
            if resp.content.lower() == word.lower():
                await player.send(f"You answered correctly and earned **{round_one_pts} points**! Get ready for the next one...")
            else:
                await player.send(f"You answered incorrectly and earned **{round_one_pts} points**! Get ready for the next one...")
        except asyncio.TimeoutError:
            await player.send("You took too long to answer and earned **0 points**!")
            round_one_pts = 0
        self.players[player_id]["points"] += round_one_pts
        await player.typing()
        await asyncio.sleep(3)
        bar_int = 0
        country = post['country']
        flist = None
        if word.endswith("s"):
            cfooda = "the " + word
        else:
            if word.startswith(("a", "e", "i", "o", "u")):
                cfooda = "an " + word
            else:
                cfooda = "a " + word

        done = False
        desc = f"Let's finish making {cfooda}!\n\nClick `stop` when the bar gets to red.\n\n`🟨`"
        embed = discord.Embed(description=desc)
        embed.set_footer(text=f"Round 2  |  Points: {self.players[player_id]["points"]}")
        button = Button(label="Stop", style=discord.ButtonStyle.red)
        view = View()
        view.add_item(button)
        round_two_pts = 0
        desc2 = ""
        async def button_callback(interaction):
            nonlocal done, bar_int, bar, desc2, round_two_pts
            if interaction.user == player:
                await interaction.response.defer()
                done = True
                if bar_int > 5:
                    desc2 = f"You left {cfooda} going for too long!"
                    round_two_pts = 0
                elif bar_int == 5:
                    desc2 = f"You made {cfooda} perfectly!"
                    round_two_pts = 100
                elif bar_int == 4:
                    desc2 = f"You almost made {cfooda} perfectly!"
                    round_two_pts = 80
                else:
                    desc2 = f"You undercooked {cfooda}!"
                    round_two_pts = 40

        button.callback = button_callback
        msg = await player.send(embed=embed, view=view)
        await asyncio.sleep(1)
        while bar_int <= 6 and not done:
            bar_int += 1
            bar = str(bar_int).replace("7", "`🟨🟨🟧🟧🟥⬛`").replace("6", "`🟨🟨🟧🟧🟥⬛`").replace("5", "`🟨🟨🟧🟧🟥`").replace("4", "`🟨🟨🟧🟧`").replace("3", "`🟨🟨🟧`").replace("2", "`🟨🟨`").replace("1", "`🟨`")
            embed = discord.Embed(description=f"Let's finish making {cfooda}!\n\nClick `stop` when the bar gets to red.\n\n{bar}")
            if bar_int == 7:
                desc2 = f"You left {cfooda} going for too long!"
                round_two_pts = 0
                done = True
            elif bar_int > 5:
                embed.color = 0x000000
                embed.set_footer(text=f"This isn't going well!")
            elif bar_int == 5:
                embed.color = 0xfc2121
            elif bar_int == 3 or bar_int == 4:
                embed.color = 0xfa8c16
            else:
                embed.color = 0xf9ff40
                embed.set_footer(text=f"You're making {cfooda}.")

            await msg.edit(embed=embed)
            await asyncio.sleep(0.6)
        if not done:
            desc2 = f"You left {cfooda} going for too long!"
            round_two_pts = 0
            done = True
        await player.send(f"{desc2} You received **{round_two_pts} points**. Last question is coming...")
        try:
            await msg.delete()
        except:
            pass
        self.players[player_id]["points"] += round_two_pts
        await player.typing()
        await asyncio.sleep(3)
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
        embed.description = "*What's a Cook Off without **trivia**?*\n\n**" + question['question'] + "**\n\n" + answers
        embed.set_footer(text="You have 25 seconds to respond with the correct letter.")
        await player.send(embed=embed)
        cl = None
        for x in choices:
            letter = x['letter']
            if x[letter] == question['correct']:
                cl = x['letter']
        b = time.perf_counter()
        try: 
            msg = await self.bot.wait_for('message', check=lambda x: x.author == player, timeout=25)
            a = time.perf_counter()
            tc = a-b
            if msg.content.lower() == cl or msg.content.lower() == question['correct'].lower():
                wrong = False
                if tc <= 6:
                    round_three_pts = 100
                    resp3 = "You've answered correctly in under 6 seconds!"
                elif tc <= 10:
                    round_three_pts = 80
                    resp3 = "You've answered correctly in under 10 seconds!"
                elif tc <= 15:
                    round_three_pts = 60
                    resp3 = "You've answered correctly in under 15 seconds!"
                else:
                    round_three_pts = 40
                    resp3 = "You've answered correctly!"
            else:
                wrong = True
            if wrong:
                resp3 = "You've answered incorrectly!"
                round_three_pts = 0
        except asyncio.TimeoutError:
            round_three_pts = 0
            resp3 = "You didn't answer in time!"
        await player.send(f"{resp3} You've earned {round_three_pts} points. Finalizing results...")
        await player.typing()
        self.players[player_id]["points"] += round_three_pts
        await asyncio.sleep(3)
        embed = discord.Embed(colour=0x8980d9, description=f"Your results...\n\n**Round 1**: {round_one_pts}\n**Round 2**: {round_two_pts}\n**Round 3**: {round_three_pts}\n\n**TOTAL**: {self.players[player_id]['points']} Points")
        embed.set_footer(text="Winner is being calculated! Check back in the discord server for the final result.")
        await player.send(embed=embed)
    

    async def determine_winner(self, ctx):
        winner_id = max(self.players, key=lambda player_id: self.players[player_id]["points"])
        winner = ctx.guild.get_member(winner_id)
        player_amnt = len(self.players)
        amnt_given = player_amnt * self.bet_amount
        await winner.send(f"Congratulations, you have won the Cook Off! You've been awarded {bbux}{amnt_given}.")
        await self.add_money(user=winner.id, count=amnt_given)
        sorted_players = sorted(self.players.items(), key=lambda x: x[1]["points"], reverse=True)
        description = f"The winner of the Cook Off is **{winner.name}** with {self.players[winner_id]['points']} points!\n\n**Leaderboard**:\n"
        place = 1
        for player_id, points in sorted_players:
            player = ctx.guild.get_member(player_id)
            description += f"`#{place}` **{player.name}** - {points['points']} points\n"
            place += 1

        embed = discord.Embed(colour=0x8980d9, description=description+ "\n\nThanks for playing!")        
        embed.set_image(url="https://media.discordapp.net/attachments/1325282246181130330/1329331828859076622/phonto.png?ex=6789f43d&is=6788a2bd&hm=7edc4d7b1d8874a61022a15dd74aba7201d6f516fa2b9f9374e0145d7a01484d&=&format=webp&quality=lossless&width=2160&height=462")
        await ctx.send(embed=embed)
        try:
            await self.gamestart_msg.delete()
        except:
            pass
        await asyncio.sleep(1)
        await self.clear_game()
        
    async def clear_game(self):
        self.game_jmsg = None
        self.gamestart_msg = None
        self.players.clear()
        self.game_host = None
        self.bet_amount = 0

    @contest.command()
    async def join(self, ctx: commands.Context):
        post = await db.market.find_one({"owner": ctx.author.id})
        if not post: 
            await ctx.send("<:RedTick:653464977788895252> You cannot join without having a restaurant! Create one with `b.start`")
        if not self.game_jmsg:
            await ctx.send("<:RedTick:653464977788895252>  There is no game to join!")
            return    
        if ctx.author.id in self.players:
            await ctx.send("<:RedTick:653464977788895252>  You're already in this game!")
            return
        if len(self.players) >= 4:
            await ctx.send("<:RedTick:653464977788895252> The game is already full! You cannot join.")
            return
        if post['money'] < self.bet_amount:
            await ctx.send("<:RedTick:653464977788895252> You cannot join because you don't have enough money to bet!")
        if self.gamestart_msg:
            await ctx.send(f"<:RedTick:653464977788895252> The game has already started!")
        
        self.players[ctx.author.id] = {"points": 0}  
        host = ctx.guild.get_member(self.game_host)

        embed = discord.Embed(colour=0x8980d9, description=f"Welcome to **Cook Off**!\n\n2 players are necessary to start the game. To join, type `b.cookoff join` and the bet will be taken from your balance.\n" \
                f"The host, **{host.name}**, can start the game with `b.cookoff start` or cancel it with `b.cookoff cancel`\n\n" \
                f"**Bet**: `{self.bet_amount}`\n**Stake**: `{self.bet_amount*len(self.players)}`\n**Players Joined**: `{len(self.players)}/4`\n* " + '\n* '.join([str(ctx.guild.get_member(player_id).name) for player_id in self.players]))
        embed.set_footer(text=f"Waiting on {host.name} to start the game...")
        await self.game_jmsg.edit(embed=embed)
        try:
            await ctx.message.delete()
        except:
            pass


    @contest.command(name=['cancel'])
    async def cancel_game(self, ctx: commands.Context):
        if ctx.author.id != self.game_host:
            await ctx.send("<:RedTick:653464977788895252> Only the host can cancel the game!")
            return
        await self.clear_game()
        await ctx.send("<:CheckMark:473276943341453312> The game has been canceled by the host.")
        if self.game_jmsg:
            await self.game_jmsg.delete()
            
    async def add_money(self, user:int, count):
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

    async def take_money(self, user:int, count:int):
        data = await db.market.find_one({"owner": user})
        bal = data['money']
        money = int(bal) - count
        await db.market.update_one({"owner": user}, {"$set":{"money": money}})


class pageBtns(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Create Game", style=discord.ButtonStyle.primary)
    async def create_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        def ans(m):
            return m.author == interaction.user
        await self.cog.contest_msg.delete()
        post = await db.market.find_one({"owner": interaction.user.id})
        embed = discord.Embed(colour=0x8980d9, description=f"{interaction.user.mention}, so you wanna play a round, huh? What do you want the bet to be? You can pick anything from {bbux}5 to {bbux}50.")
        embed.set_footer(text="You have 20 seconds to respond with a number.")
        count_msg = await interaction.channel.send(embed=embed)
        count = await interaction.client.wait_for('message', check=ans, timeout=20)
        
        try:
            await count_msg.delete()
            await count.delete()
        except:
            pass
        
        if count.content.isdigit() and 5 <= int(count.content) <= 50:
            self.cog.bet_amount = int(count.content) 
            embed = discord.Embed(colour=0x8980d9, description=f"Welcome to **Cook Off**!\n\n2 players are necessary to start the game. To join, type `b.cookoff join` and the bet will be taken from your balance.\n" \
                f"The host, **{interaction.user.name}**, can start the game with `b.cookoff start` or cancel it with `b.cookoff cancel`\n\n" \
                f"**Bet**: `{count.content}`\n**Stake**: `{self.cog.bet_amount}`\n**Players Joined**: `1/4`\n\n **(1)** {interaction.user.name}")
            embed.set_footer(text=f"Waiting on {interaction.user} to start the game...")
            self.cog.game_jmsg = await interaction.channel.send(embed=embed)
            self.cog.players[interaction.user.id] = {"points": 0}  
            self.cog.game_host = interaction.user.id
        else:
            await interaction.channel.send(f"<:RedTick:653464977788895252> The bet must be a number between {bbux}5 and {bbux}50. Restart the process with `b.cookoff`")

async def setup(bot):
    await bot.add_cog(Cookoff(bot))
