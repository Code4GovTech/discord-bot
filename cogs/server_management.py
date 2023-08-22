from discord.ext import commands
from utils.db import SupabaseInterface
import discord
class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    def validUser(self, ctx):
        authorised_users = [1042682119035568178, 1120262151676895274, 1107555866422562926, 1107555866422562926, 599878601143222282] #bhavya, devaraj, navaneeth, venkatesh, sukhpreet
        return ctx.author.id in authorised_users
        
    
    #Channel Notifications Management
    @commands.command()
    @commands.check(validUser)
    # async def assign_channel(self, ctx, product, channel: discord.TExt):
    #     pass

    async def dissociate_channel(self,ctx, args):
        pass

    async def notifs_on(self,ctx,channel: discord.TextChannel):
        try:
            SupabaseInterface("discord_channels").update({"should_notify": True}, "channel_id", channel.id)
            await ctx.send(f"Notifications have been turned on for {channel.name}")
        except Exception as e:
            print(e)
            await ctx.send("An unexpected error occured")

    async def notifs_off(self, ctx, channel: discord.TextChannel):
        try:
            SupabaseInterface("discord_channels").update({"should_notify": False}, "channel_id", channel.id)
            await ctx.send(f"Notifications have been turned on for {channel.name}")
        except Exception as e:
            print(e)
            await ctx.send("An unexpected error occured")

    # async def 


async def setup(bot):
    await bot.add_cog(ServerManagement(bot))