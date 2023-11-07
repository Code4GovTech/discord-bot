from discord.ext import commands
import discord
from utils.db import SupabaseInterface

class Listeners(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot
    
    async def grantVerifiedRole(self, member: discord.Member):
        verifiedContributorRoleID = 1123967402175119482
        try:
            verifiedContributorRole = member.guild.get_role(verifiedContributorRoleID)
            if verifiedContributorRole:
                if verifiedContributorRole not in member.roles:
                    await member.add_roles(verifiedContributorRole, reason="Completed Auth and Introduction")
            else:
                print("Verified Contributor Role not found")
        except Exception as e:
            print("Exception while granting Role:", e)
    
    async def isAuthenticated(self, memberID: int) -> bool:
        if SupabaseInterface("contributors").read("discord_id", memberID):
            return True
        else:
            return False

    
    @commands.Cog.listener("on_message")
    async def listenForIntroduction(self, message: discord.Message):
        if message.channel.id == 1107343423167541328: #intro channel
            if await self.isAuthenticated(message.author.id):
                await self.grantVerifiedRole(message.author)
        else:
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot))
