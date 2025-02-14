import aiohttp
import config
import discord
from discord.ext import tasks, commands

class TopGG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_server_count.start()

    @tasks.loop(minutes=90)
    async def update_server_count(self):
        async with aiohttp.ClientSession() as session:
            url = f"https://top.gg/api/bots/657037653346222102/stats"
            headers = {"Authorization": config.dbl_token}
            data = {"server_count": len(self.bot.guilds)}
            async with session.post(url, json=data, headers=headers) as response:
                if not response.status == 200:
                    print('\x1b[1;31;40m' + '[TOP-GG-ERROR]: ' + '\x1b[0m' + f"Failed to update server_count: {response.status} - {await response.text()}")

    @update_server_count.before_loop
    async def before_update(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.update_server_count.cancel()

async def setup(bot):
    await bot.add_cog(TopGG(bot))
