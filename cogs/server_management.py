from discord.ext import commands
import discord, datetime

from config.server import ServerConfig
from interfaces.supabase import SupabaseInterface

serverConfig = ServerConfig()

class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    def validUser(self, ctx):
        authorised_users = [1042682119035568178, 1120262151676895274, 1107555866422562926, 1107555866422562926, 599878601143222282] #bhavya, devaraj, navaneeth, venkatesh, sukhpreet
        return ctx.author.id in authorised_users
    
    @commands.command(aliaes=['initiate'])
    async def initiateServerData(self, ctx):
        countingDate = datetime.datetime(2023,10,1,0,0,0,0)
        # add all chapters
        guild = self.bot.get_guild(serverConfig.SERVER)
        for role in guild.roles:
            if role.name.startswith("College:"):
                orgName = role.name[len("College: "):]
                SupabaseInterface('').addChapter(orgName=orgName, type='COLLEGE')
            elif role.name.startswith("Corporate:"):
                orgName = role.name[len("Corporate: "):]
                SupabaseInterface('').addChapter(orgName=orgName, type='CORPORATE')

        
        async for member in guild.fetch_members(limit=None):
            SupabaseInterface('').updateContributor(member)



    # async def notifs_on(self,ctx,channel: discord.TextChannel):
    #     try:
    #         SupabaseInterface("discord_channels").update({"should_notify": True}, "channel_id", channel.id)
    #         await ctx.send(f"Notifications have been turned on for {channel.name}")
    #     except Exception as e:
    #         print(e)
    #         await ctx.send("An unexpected error occured")

    # async def notifs_off(self, ctx, channel: discord.TextChannel):
    #     try:
    #         SupabaseInterface("discord_channels").update({"should_notify": False}, "channel_id", channel.id)
    #         await ctx.send(f"Notifications have been turned on for {channel.name}")
    #     except Exception as e:
    #         print(e)
    #         await ctx.send("An unexpected error occured")

    # async def 


async def setup(bot):
    await bot.add_cog(ServerManagement(bot))