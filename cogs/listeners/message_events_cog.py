from discord.ext import commands
import discord

from config.server import ServerConfig
from interfaces.supabase import SupabaseInterface

serverConfig = ServerConfig()
supabaseClient = SupabaseInterface('')

# On join
# On Message
# on role

async def grantVerifiedRole(member: discord.Member):
        try:
            verifiedContributorRole = member.guild.get_role(serverConfig.Roles.CONTRIBUTOR_ROLE)
            if verifiedContributorRole:
                if verifiedContributorRole not in member.roles:
                    await member.add_roles(verifiedContributorRole, reason="Completed Auth and Introduction")
            else:
                print("Verified Contributor Role not found")
        except Exception as e:
            print("Exception while granting Role:", e)

class MessageEventsListener(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        #Listen for Introduction
        if message.channel.id == serverConfig.Channels.INTRODUCTION_CHANNEL:
            if await supabaseClient.memberIsAuthenticated(message.author):
                await grantVerifiedRole(message.author)
        else:
            return
    



async def setup(bot: commands.Bot):
    await bot.add_cog(MessageEventsListener(bot))




'''
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
'''