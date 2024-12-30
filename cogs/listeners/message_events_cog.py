import discord
from discord.ext import commands

from config.server import ServerConfig
from shared_migrations.db.discord_bot import DiscordBotQueries
serverConfig = ServerConfig()
postgresClient = DiscordBotQueries()


async def grantVerifiedRole(member: discord.Member):
    try:
        verifiedContributorRole = member.guild.get_role(
            serverConfig.Roles.CONTRIBUTOR_ROLE
        )
        if verifiedContributorRole:
            if verifiedContributorRole not in member.roles:
                await member.add_roles(
                    verifiedContributorRole, reason="Completed Auth and Introduction"
                )
        else:
            print("Verified Contributor Role not found")
    except Exception as e:
        print("Exception while granting Role:", e)


class MessageEventsListener(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        # Listen for Introduction
        if message.channel.id == serverConfig.Channels.INTRODUCTION_CHANNEL:
            if await postgresClient.memberIsAuthenticated(message.author):
                await grantVerifiedRole(message.author)
        else:
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(MessageEventsListener(bot))
