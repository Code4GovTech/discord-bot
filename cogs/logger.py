import discord
from discord.ext import commands

import aiohttp
import os

'''
Webhook Logger
Purpose: Create persistent logs for Exceptions raised in discord bot
'''

class WebhookLogger(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.url = os.getenv("WEBHOOK_URL")
    
    async def saveToSupabase(self):
        pass

    async def log(self, content: str, username=None, embeds=[]):
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(url= self.url, session=session)
            await webhook.send(content=content, username=username, embeds=embeds)
    



async def setup(bot: commands.Bot):
    await bot.add_cog(WebhookLogger(bot))
