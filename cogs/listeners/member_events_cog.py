from discord.ext import commands
import discord


class MemberEventsListener(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__()

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member):
        # Add them as a potential contributor
        # Check their roles
        pass

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member: discord.Member):
        # This event is called when a member leaves a server.
        # You can perform actions such as logging the event,
        # notifying a staff channel, or cleaning up user data.
        pass  # Replace with your code

    @commands.Cog.listener("on_member_update")
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        # This event is called when a Member updates their profile,
        # such as changing their nickname, avatar, roles, etc.
        # You can compare the 'before' and 'after' states to determine
        # what was changed and respond accordingly.
        pass  # Replace with your code

async def setup(bot: commands.Bot):
    await bot.add_cog(MemberEventsListener(bot))