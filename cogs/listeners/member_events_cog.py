import discord
from discord.ext import commands

from interfaces.supabase import SupabaseInterface


class MemberEventsListener(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__()

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member):
        SupabaseInterface().updateContributor(member)

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member: discord.Member):
        # Members leaving the discord server is not defined behavior as of now, but should be defined eventually
        pass

    @commands.Cog.listener("on_member_update")
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        SupabaseInterface().updateContributor(after)


async def setup(bot: commands.Bot):
    await bot.add_cog(MemberEventsListener(bot))
