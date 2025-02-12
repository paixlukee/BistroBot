import discord
from discord.ext import commands, tasks
import datetime
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import config
import pymongo

client = AsyncIOMotorClient(config.mongo_client)
db = client['siri']

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()

    @tasks.loop(hours=24)
    async def daily_task(self):
        current_time = datetime.datetime.now()
        if current_time.hour == 1 and current_time.minute == 0:
            await self.add_customers()
            all_users = db.market.find({'worker': {'$exists': True}})
            bulk_updates = []
            async for x in all_users:
                if 'worker' in x and x['worker']:
                    wn = x['worker_name']
                    if wn in x['worker']:
                        cash = x['worker'][wn][2]['pay']
                        bulk_updates.append(pymongo.UpdateOne({'owner': x['owner']}, {'$inc': {'money': cash}}))
                    if x['advert']:
                        bulk_updates.append(pymongo.UpdateOne({'owner': x['owner']}, {'$set': {'advert': None}}))
            if bulk_updates:
                try:
                    result = await db.market.bulk_write(bulk_updates)
                    print('\x1b[1;36;40m' + '[UPDATE]: ' + '\x1b[0m' + 'All Restaurants have been paid & customers added.')
                except Exception as e:
                    print(f"Error during bulk_write: {e}")

    @daily_task.before_loop
    async def before_daily_task(self):
        current_time = datetime.datetime.now()
        target_time = current_time.replace(hour=1, minute=0, second=0, microsecond=0)
        if current_time > target_time:
            target_time += datetime.timedelta(days=1)
        wait_time = (target_time - current_time).total_seconds()
        print(f'\nConnecting..\n\nDaily Tasks will be done in {round(wait_time/60)} minutes.\n------')
        await asyncio.sleep(wait_time)

    async def add_money(self, user: int, count: int):
        data = await db.market.find_one({"owner": user})
        if data:
            bal = data['money']
            money = int(bal) + count
            await db.market.update_one({"owner": user}, {"$set": {"money": money}})

    async def calc_customers(self, user: int):
        data = await db.market.find_one({"owner": user})
        if data:
            ratings = [rating['rating'] for rating in data['ratings']]
            avr = round(sum(ratings) / len(ratings)) if ratings else 0
            count = avr * 10 + data['level'] * 20
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
            return count
        else:
            return 0

    async def add_customers(self):
        all_users = db.market.find()
        bulk_updates = []
        async for x in all_users:
            per_day = await self.calc_customers(x['owner'])
            current = x['customers']
            bulk_updates.append(
                pymongo.UpdateOne(
                    {'owner': x['owner']},
                    {'$inc': {'customers': per_day}}
                )
            )
        if bulk_updates:
            try:
                result = await db.market.bulk_write(bulk_updates)
            except Exception as e:
                print(f"Error during bulk_write for customers: {e}")

async def setup(bot):
    await bot.add_cog(Tasks(bot))
