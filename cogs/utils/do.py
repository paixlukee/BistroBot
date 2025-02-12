import discord
import datetime
import requests
import logging
import math
import re
import asyncio
import config
import subprocess

              
async def shell(cmd):
    process =\
    await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    results = await process.communicate()
    return "".join(x.decode("utf-8") for x in results)
