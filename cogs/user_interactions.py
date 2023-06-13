import discord
import os
from discord.ext import commands, tasks
import time, csv
from utils.db import SupabaseInterface
from utils.api import GithubAPI



#This is a Discord View that is a set of UI elements that can be sent together in a message in discord.
#This view send a link to Github Auth through c4gt flask app in the form of a button.
class AuthenticationView(discord.ui.View):
    def __init__(self, discord_userdata):
        super().__init__()
        button = discord.ui.Button(label='Authenticate Github', style=discord.ButtonStyle.url, url=f'{os.getenv("FLASK_HOST")}/authenticate/{discord_userdata}')
        self.add_item(button)
        self.message = None

class UserHandler(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    #Executing this command sends a link to Github OAuth App via a Flask Server in the DM channel of the one executing the command 
    @commands.command(aliases=['join'])
    async def join_as_contributor(self, ctx):
        #create a direct messaging channel with the one who executed the command
        dmchannel = ctx.author.dm_channel if ctx.author.dm_channel else await ctx.author.create_dm()
        userdata = str(ctx.author.id)
        view = AuthenticationView(userdata)
        await dmchannel.send("Please authenticate your github account to register for Code for GovTech 2023", view=view)

     



    

    @commands.command()
    async def announce(self, ctx):
        guild = ctx.guild if ctx.guild else await self.bot.fetch_guild(os.getenv("SERVER_ID"))
        count = 0
        with open('introduced.csv', 'w') as file:
            writer = csv.writer(file)
            data = []
            
        print(count)

        # async for member in guild.fetch_members(limit=None):
        #     print(member.id)
        #     count+=1
        # print(count)
        # members = [476285280811483140]
        # for member_id in members:
            # member = await guild.fetch_member(member_id)
            # dmchannel = member.dm_channel if member.dm_channel else await member.create_dm()
            # await dmchannel.send("Test Announcement")



    @commands.command()
    async def test(self,ctx):
        # print(os.getenv("SERVER_ID"))
        guild = await self.bot.fetch_guild(os.getenv("SERVER_ID"))
        channel = await guild.fetch_channel(973851473131761677)
        async for message in channel.history(limit=20):
            print(message.content, type(message.content))
            if message.content == '':
                print(True)
    
     
async def setup(bot):
    await bot.add_cog(UserHandler(bot))