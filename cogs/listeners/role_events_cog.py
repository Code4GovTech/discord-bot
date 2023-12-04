from discord.ext import commands
import discord

from interfaces.supabase import SupabaseInterface


class RoleEventsListener(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        if role.name.startswith("College:"):
                orgName = role.name[len("College: "):]
                SupabaseInterface().addChapter(orgName=orgName, type='COLLEGE')
        elif role.name.startswith("Corporate:"):
                orgName = role.name[len("Corporate: "):]
                SupabaseInterface().addChapter(orgName=orgName, type='CORPORATE')

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        # Role Removal is not being handled this version, but it should be defined eventually
        pass

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        if after.name.startswith("College:"):
                orgName = after.name[len("College:"):]
                SupabaseInterface().addChapter(orgName=orgName, type='COLLEGE')
        elif after.name.startswith("Corporate:"):
                orgName = after.name[len("Corporate: "):]
                SupabaseInterface().addChapter(orgName=orgName, type='CORPORATE')


async def setup(bot: commands.Bot):
    await bot.add_cog(RoleEventsListener(bot))