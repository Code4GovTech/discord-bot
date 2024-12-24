from datetime import datetime

from discord.ext import commands, tasks

from config.server import ServerConfig
# from helpers.supabaseClient import PostgresClient
from shared_migrations.db.discord_bot import DiscordBotQueries

serverConfig = ServerConfig()


class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.postgres_client = DiscordBotQueries()

    def validUser(self, ctx):
        authorised_users = [
            1120262151676895274,
            1107555866422562926,
            1059343450312544266,
        ]  # devaraj, venkatesh, karn
        return ctx.author.id in authorised_users

    @commands.command(aliaes=["initiate"])
    async def updateServerData(self, ctx):
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
                self.postgres_client.addChapter(
                    roleId=role.id, orgName=orgName, type="COLLEGE"
                )
            elif role.name.startswith("Corporate:"):
                orgName = role.name[len("Corporate: ") :]
                chapterRoles.append(role)
                self.postgres_client.addChapter(
                    roleId=role.id, orgName=orgName, type="CORPORATE"
                )

        print("added chapters")

        contributorsGithub = self.postgres_client.read_all("contributors_registration")
        contributorsDiscord = self.postgres_client.read_all_active("contributors_discord")

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

        self.postgres_client.updateContributors(guild.members)
        recordedMembers = [
            contributor["discord_id"] for contributor in contributorsDiscord
        ]
        print(f"{len(recordedMembers)} have their data saved")
        currentMembers = [member.id for member in guild.members]
        membersWhoLeft = list(set(recordedMembers) - set(currentMembers))
        print(f"{len(membersWhoLeft)} members left")
        self.postgres_client.invalidateContributorDiscord(membersWhoLeft)
        print("Updated Contributors")

async def setup(bot):
    await bot.add_cog(ServerManagement(bot))
