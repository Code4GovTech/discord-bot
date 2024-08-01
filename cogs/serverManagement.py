from datetime import datetime

from discord.ext import commands, tasks

from config.server import ServerConfig
from helpers.supabaseClient import SupabaseClient

serverConfig = ServerConfig()


class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.assign_contributor_role.start()

    def validUser(self, ctx):
        authorised_users = [
            1120262151676895274,
            1107555866422562926,
            1059343450312544266,
            1147918536912666756,
            691946275888955412
        ]  # devaraj, venkatesh, karn, mohit, vedant
        return ctx.author.id in authorised_users

    @commands.command(aliaes=["initiate"])
    async def updateServerData(self, ctx):
        # add all chapters
        await ctx.send('updateServerData running. Kindly wait for completion.')
        chapterRoles = []
        guild = self.bot.get_guild(serverConfig.SERVER)
        # Clear Error
        oldRole = guild.get_role(973852365188907048)
        print(f"{len(oldRole.members)} have the old contributor role")
        await ctx.send(f"{len(oldRole.members)} have the old contributor role")
        for member in oldRole.members:
            print(member.display_name)
            await ctx.send(f"{member.display_name} : {member.id} - Old contributor")
            if member.joined_at.timestamp() > datetime(2022, 12, 25).timestamp():
                await member.remove_roles(oldRole, reason="mistakenly given")
                print("Member removed")
                await ctx.send(f"Member {member.display_name} removed")
        for role in guild.roles:
            if role.name.startswith("College:"):
                orgName = role.name[len("College: "):]
                chapterRoles.append(role)
                SupabaseClient().addChapter(
                    roleId=role.id, orgName=orgName, type="COLLEGE"
                )
                await ctx.send(f"Added college {orgName} with roleId {role.id}")
            elif role.name.startswith("Corporate:"):
                orgName = role.name[len("Corporate: "):]
                chapterRoles.append(role)
                SupabaseClient().addChapter(
                   roleId=role.id, orgName=orgName, type="CORPORATE"
                )
                await ctx.send(f"Added corporate {orgName} with roleId {role.id}")

        print("added chapters")
        await ctx.send("Added Chapters")

        contributorsGithub = SupabaseClient().read_all("contributors_registration")
        contributorsDiscord = SupabaseClient().read_all_active("contributors_discord")

        # Give contributor role
        contributorIds = [
            contributor["discord_id"] for contributor in contributorsGithub
        ]
        contributorRole = guild.get_role(serverConfig.Roles.CONTRIBUTOR_ROLE)
        count = [0, 0, 0]
        memberIds = []
        for member in guild.members:
            memberIds.append(member.id)
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

        print(f"{len(memberIds)} are on discord")
        print(f"{len(recordedMembers)} have their data saved")
        await ctx.send(f"{len(memberIds)} members are on discord")
        await ctx.send(f"{len(recordedMembers)} members in our db")

        currentMembers = [member.id for member in guild.members]
        membersWhoLeft = list(set(recordedMembers) - set(currentMembers))
        print(f"{membersWhoLeft} members left")
        await ctx.send(f"{len(membersWhoLeft)} members left. Disabling them from our server")
        SupabaseClient().invalidateContributorDiscord(membersWhoLeft)
        print("Updated Contributors")
        await ctx.send("Server updated COMPLETED!")

    @tasks.loop(minutes=30)
    async def assign_contributor_role(self):
        guild = self.bot.get_guild(serverConfig.SERVER)
        contributorRole = guild.get_role(serverConfig.Roles.CONTRIBUTOR_ROLE)
        contributorsGithub = SupabaseClient().read_all("contributors_registration")

        contributorIds = [
            contributor["discord_id"] for contributor in contributorsGithub
        ]

        for member in guild.members:
            if member.id in contributorIds and contributorRole not in member.roles:
                await member.add_roles(contributorRole)

    @assign_contributor_role.before_loop
    async def before_assign_contributor_role(self):
        await self.bot.wait_until_ready()  # Wait until the bot is logged in and ready


async def setup(bot):
    await bot.add_cog(ServerManagement(bot))
