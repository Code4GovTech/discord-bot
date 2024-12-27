import discord
from discord.ext import commands

# from helpers.supabaseClient import PostgresClient
from shared_migrations.db.discord_bot import DiscordBotQueries


class RoleEventsListener(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.postgres_client = DiscordBotQueries()
        super().__init__()

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        if role.name.startswith("College:"):
            orgName = role.name[len("College: ") :]
            self.postgres_client.addChapter(roleId=role.id, orgName=orgName, type="COLLEGE")
        elif role.name.startswith("Corporate:"):
            orgName = role.name[len("Corporate: ") :]
            self.postgres_client.addChapter(
                roleId=role.id, orgName=orgName, type="CORPORATE"
            )

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        self.postgres_client.deleteChapter(roleID=role.id)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        if after.name.startswith("College:"):
            orgName = after.name[len("College: ") :]
            self.postgres_client.addChapter(
                roleId=after.id, orgName=orgName, type="COLLEGE"
            )
        elif after.name.startswith("Corporate:"):
            orgName = after.name[len("Corporate: ") :]
            self.postgres_client.addChapter(
                roleId=after.id, orgName=orgName, type="CORPORATE"
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(RoleEventsListener(bot))
