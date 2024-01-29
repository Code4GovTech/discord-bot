from datetime import datetime

from discord.ext import commands

from config.server import ServerConfig
from helpers.supabaseClient import SupabaseClient

serverConfig = ServerConfig()


class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    def validUser(self, ctx):
        authorised_users = [
            1042682119035568178,
            1120262151676895274,
            1107555866422562926,
            1107555866422562926,
            599878601143222282,
        ]  # bhavya, devaraj, navaneeth, venkatesh, sukhpreet
        return ctx.author.id in authorised_users

    @commands.command(aliaes=["initiate"])
    async def getServerData(self, ctx):
        # add all chapters
        chapterRoles = []
        guild = self.bot.get_guild(serverConfig.SERVER)
        ## Clear Error
        oldRole = guild.get_role(973852365188907048)
        print("started")
        print(f"{len(oldRole.members)} have the old contributor role")
        for member in oldRole.members:
            print(member.joined_at)
            if member.joined_at.timestamp() > datetime(2022, 12, 25).timestamp():
                await member.remove_roles(oldRole, reason="mistakenly given")
                print("Member removed")

        for role in guild.roles:
            if role.name.startswith("College:"):
                orgName = role.name[len("College: ") :]
                chapterRoles.append(role)
                SupabaseClient().addChapter(orgName=orgName, type="COLLEGE")
            elif role.name.startswith("Corporate:"):
                orgName = role.name[len("Corporate: ") :]
                chapterRoles.append(role)
                SupabaseClient().addChapter(orgName=orgName, type="CORPORATE")

        print("added chapters")

        contributorsGithub = SupabaseClient().read_all("contributors_registration")
        contributorsDiscord = SupabaseClient().read_all("contributors_discord")

        ## Give contributor role
        contributorIds = [
            contributor["discord_id"] for contributor in contributorsGithub
        ]
        contributorRole = guild.get_role(serverConfig.Roles.CONTRIBUTOR_ROLE)
        count = [0, 0, 0]
        for member in guild.members:
            count[0] += 1
            if member.id in contributorIds:
                count[1] += 1
                if contributorRole not in member.roles:
                    count[2] += 1
                    await member.add_roles(contributorRole)

        print(count)

        SupabaseClient().updateContributors(guild.members)
        recordedMembers = [
            contributor["discord_id"] for contributor in contributorsDiscord
        ]
        print(f"{len(recordedMembers)} have their data saved")
        currentMembers = [member.id for member in guild.members]
        membersWhoLeft = list(set(recordedMembers) - set(currentMembers))
        print(f"{len(membersWhoLeft)} members left")
        SupabaseClient().deleteContributorDiscord(membersWhoLeft)
        print("Updated Contributors")


async def setup(bot):
    await bot.add_cog(ServerManagement(bot))
