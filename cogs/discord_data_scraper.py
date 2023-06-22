from discord.ext import commands, tasks
from discord.channel import TextChannel
from discord import Member
import os, dateutil, json, sys
from datetime import datetime

from utils.db import SupabaseInterface
from utils.api import GithubAPI
import csv

#CONSTANTS
RUNTIME_DATA_DIRECTORY = 'scraping-runtime-data'
RUNTIME_DATA_FILE = 'discordScraperRuntimeData.json'
CONTRIBUTOR_ROLE_ID = 973852365188907048
INTRODUCTIONS_CHANNEL_ID =1107343423167541328

#check id directory exists for scraping runtime data and create one if it doesn't
def createRuntimeDataDirectory():
    cwd = os.getcwd()
    path = f'{cwd}/{RUNTIME_DATA_DIRECTORY}'
    if not os.path.isdir(path):
        os.mkdir(path)
    
    return path
        



class DiscordDataScaper(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.runtimeDataDirectory = createRuntimeDataDirectory()
    
    # @commands.command()
    # async def introductions(self, ctx):
    #     guild = ctx.guild if ctx.guild else await self.bot.fetch_guild(os.getenv("SERVER_ID"))
    #     intro_channel = await guild.fetch_channel(os.getenv("INTRODUCTIONS_CHANNEL"))
    #     with open('introduced.csv', 'w') as file:
    #         writer = csv.writer(file)
    #         data = []
    #         async for message in intro_channel.history(limit=None):
    #             row = [message.author.id]
    #             if row not in data:
    #                 count+=1
    #                 data.append(row)
    #         writer.writerows(data)
    @commands.Cog.listener()
    async def on_message(self, message):
        contributor = SupabaseInterface("discord_engagement").read("contributor", message.author.id)
        print("message", len(message.content))
        if not contributor:
            SupabaseInterface("discord_engagement").insert({
                "contributor": message.author.id,
                "has_introduced": False,
                "total_message_count": 1,
                "total_reaction_count": 0})
            return
        if len(message.content)>20:
            if message.channel.id == INTRODUCTIONS_CHANNEL_ID:
                print("intro")
                SupabaseInterface("discord_engagement").update({"has_introduced":True}, "contributor", message.author.id)
            SupabaseInterface("discord_engagement").update({"total_message_count":contributor[0]["total_message_count"]+1}, "contributor", message.author.id)
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        message = reaction.message 
        contributor = SupabaseInterface("discord_engagement").read("contributor", message.author.id)[0]
        if not contributor:
            SupabaseInterface("discord_engagement").insert({
                "contributor": message.author.id,
                "has_introduced": False,
                "total_message_count": 0,
                "total_reaction_count": 1})
            return
        print("reaction")
        SupabaseInterface("discord_engagement").update({"total_reaction_count":contributor["total_reaction_count"]+1}, "contributor", message.author.id)


            
    
    @commands.command()
    async def add_engagement(self, ctx):
        await ctx.channel.send("started")
        def addEngagmentData(data):
            client = SupabaseInterface("discord_engagement")
            client.insert(data)
            return
        guild = await self.bot.fetch_guild(os.getenv("SERVER_ID")) #SERVER_ID Should be C4GT Server ID
        channels = await guild.fetch_channels()
        engagmentData = {}



        async for member in guild.fetch_members(limit=None):
            memberData = {
                "contributor": member.id,
                "has_introduced": False,
                "total_message_count": 0,
                "total_reaction_count": 0

            }
            engagmentData[member.id]= memberData
        # await ctx.channel.send('2')

        for channel in channels:
            # await ctx.channel.send(channel.name)
            print(channel.name)
            if isinstance(channel, TextChannel): #See Channel Types for info on text channels https://discordpy.readthedocs.io/en/stable/api.html?highlight=guild#discord.ChannelType
                # await ctx.send("text")
                async for message in channel.history(limit=None):
                    if message.author.id not in engagmentData.keys():
                        engagmentData[message.author.id]= {
                "contributor": message.author.id,
                "has_introduced": False,
                "total_message_count": 0,
                "total_reaction_count": 0}
                    # await ctx.send("msg")
                    if message.content=='':
                        # await ctx.send("10")
                        continue
                    if len(message.content)>20:
                        # await ctx.send("20")
                        engagmentData[message.author.id]["total_message_count"]+=1
                        if message.channel.id == INTRODUCTIONS_CHANNEL_ID:
                            engagmentData[message.author.id]["has_introduced"] =True
                    if message.reactions:
                        # await ctx.send("30")
                        engagmentData[message.author.id]["total_reaction_count"]+=len(message.reactions)
        # await ctx.channel.send('3')
        addEngagmentData(list(engagmentData.values()))
        print("Complete!", file=sys.stderr)
        # await ctx.channel.send("ended")
        return
    

    
    
    # @commands.command()
    # async def not_contributors(self, ctx):
    #     guild = ctx.guild if ctx.guild else await self.bot.fetch_guild(os.getenv("SERVER_ID"))
    #     orgAndMentors = [role for role in os.getenv("NON_CONTRIBUTOR_ROLES").split(',')]
    #     with open("not_contributors.csv", "w") as file:
    #         writer = csv.writer(file)
    #         data = []
    #         async for member in guild.fetch_members(limit=None):
    #             for role in member.roles:
    #                 if role.id in orgAndMentors:
    #                     user = [member.name, member.id, member.roles]
    #                     if user not in data:
    #                         data.append(user)
    #         writer.writerows(data)
    
    #Store all messages on Text Channels in the Discord Server to SupaBase
    @commands.command()
    async def add_messages(self,ctx):
        
        def addMessageData(data):
            client = SupabaseInterface("unstructured discord data")
            client.insert(data)
            return
        
        def recordLastRunTime(data, directory):
            with open(f'{directory}/{RUNTIME_DATA_FILE}', 'w+') as file:
                json.dump(data, file)
        
        def getLastRunTime(channelId):
            with open(f'{self.runtimeDataDirectory}/{RUNTIME_DATA_FILE}', 'r') as file:
                data = json.load(file)
                lastRuntime = data.get(str(channelId))
                if lastRuntime is None:
                    #all messages will be read
                    return None
                else:
                    return dateutil.parser.parse(lastRuntime)


        
        guild = await self.bot.fetch_guild(os.getenv("SERVER_ID")) #SERVER_ID Should be C4GT Server ID
        channels = await guild.fetch_channels()
        runtimeData = {}

        for channel in channels:
            print(channel.name)
            if isinstance(channel, TextChannel): #See Channel Types for info on text channels https://discordpy.readthedocs.io/en/stable/api.html?highlight=guild#discord.ChannelType
                messages = []
                last_run = getLastRunTime(channel.id)
                print(last_run)
                async for message in channel.history(limit=None, after =last_run ):
                    if message.content=='':
                        continue
                    msg_data = {
                        "channel": channel.id,
                        "channel_name": channel.name,
                        "text": message.content,
                        "author": message.author.id,
                        "author_name": message.author.name,
                        "author_roles": message.author.roles if isinstance(message.author, Member) else [],
                        "sent_at":str(message.created_at)
                    }
                    messages.append(msg_data)
                print(len(messages))
                addMessageData(messages)
            runtimeData[channel.id] = datetime.now().isoformat()
        recordLastRunTime(runtimeData, self.runtimeDataDirectory)
        print("Complete!")

async def setup(bot):
    await bot.add_cog(DiscordDataScaper(bot))