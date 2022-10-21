import dbl
import discord
from discord.ext import commands
import config

class TopGG(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dblpy = dbl.DBLClient(self.bot, config.dbl_token, autopost=True)


async def setup(bot):
    await bot.add_cog(TopGG(bot))
