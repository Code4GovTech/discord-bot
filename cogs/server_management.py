from discord.ext import commands
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
    async def assign_channel(self, ctx, args):
        pass

    async def dissociate_channel(self,ctx, args):
        pass

    async def notifs_on(self,ctx,args):
        pass

    async def notifs_off(self, ctx, args):
        pass

    # async def 


async def setup(bot):
    await bot.add_cog(ServerManagement(bot))