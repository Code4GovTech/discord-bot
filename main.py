import discord
from discord.ext import commands
import os, sys
import asyncio
import dotenv

#Since there are user defined packages, adding current directory to python path
current_directory = os.getcwd()
sys.path.append(current_directory)

dotenv.load_dotenv(".env")
intents = discord.Intents.all()

client = commands.Bot(command_prefix='!', intents=intents)

#alert message on commandline that bot has successfully logged in
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

#load cogs
async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with client:
        await load()
        await client.start(os.getenv("TOKEN"))


asyncio.run(main())


        


