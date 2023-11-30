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
                orgName = role.name[len("College:"):]
                SupabaseInterface().addChapter(orgName=orgName, type='COLLEGE')

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        # Delete a Chapter if role is deleted?? (data will be afftecter)
        pass

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        if after.name.startswith("College:"):
                orgName = after.name[len("College:"):]
                SupabaseInterface().addChapter(orgName=orgName, type='COLLEGE')


async def setup(bot: commands.Bot):
    await bot.add_cog(RoleEventsListener(bot))