import csv
import os

import discord
from discord.ext import commands, tasks
from dotenv import find_dotenv, load_dotenv

from helpers.supabaseClient import PostgresClient

load_dotenv(find_dotenv())

VERIFIED_CONTRIBUTOR_ROLE_ID = int(os.getenv("VERIFIED_ROLE_ID"))


class UserHandler(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.update_contributors.start()
        self.postgres_client = PostgresClient()

    @tasks.loop(minutes=60)
    async def update_contributors(self):
        print("update_contributors running")
        contributors = self.postgres_client.read_all("contributors_registration")
        print("Contributors in DB: ", len(contributors))
        guild = await self.bot.fetch_guild(os.getenv("SERVER_ID"))
        contributor_role = guild.get_role(VERIFIED_CONTRIBUTOR_ROLE_ID)
        for contributor in contributors:
            discord_id = contributor["discord_id"]
            try:
                member = await guild.fetch_member(discord_id)
                if contributor_role not in member.roles:
                    try:
                        await member.add_roles(contributor_role)
                        print(f"Gave {contributor_role.name} role to {member.name}")
                    except Exception as e:
                        print(f"{member.name} could not be given verified contributor role")
                else:
                    print(f"{member.name} is already a {contributor_role.name}")
            except:
                print(f"User with discord_id: {discord_id} is not a member of our server anymore")
                # TODO delete from supabase as well?
        return

    @commands.command(aliases=["badges"])
    async def list_badges(self, ctx):
        converseDesc = f"""Well done *{ctx.author.name}*! 👏

    You have engaged on the C4GT  discord community  with 10  or more messages and earned the **Converser Badge!** 💬 This badge shows that you are a friendly and helpful member of our community! 😊 """
        converseEmbed = discord.Embed(title="Converse Badge", description=converseDesc)
        converseEmbed.set_image(
            url="https://raw.githubusercontent.com/KDwevedi/testing_for_github_app/main/WhatsApp%20Image%202023-06-20%20at%202.57.12%20PM.jpeg"
        )

        rockstarDesc = f"""Amazing *{ctx.author.name}*! 🙌
    You have received 5 upvotes on your message and earned the **Rockstar Badge!** 🌟 You add so much value to our community and we are grateful for your contribution! 💖
    Please keep up the good work and share your expertise with us! 🙌
    """
        reactionsEmbed = discord.Embed(title="Rockstar Badge", description=rockstarDesc)
        reactionsEmbed.set_image(
            url="https://raw.githubusercontent.com/KDwevedi/testing_for_github_app/main/WhatsApp%20Image%202023-06-20%20at%202.57.12%20PM.jpeg"
        )

        await ctx.channel.send(embed=converseEmbed)
        await ctx.channel.send(embed=reactionsEmbed)

        return

    @tasks.loop(minutes=10)
    async def update_contributors(self):
        contributors = self.postgres_client.read_all("contributors_registration")
        guild = await self.bot.fetch_guild(os.getenv("SERVER_ID"))
        contributor_role = guild.get_role(VERIFIED_CONTRIBUTOR_ROLE_ID)
        count = 1
        for contributor in contributors:
            print(count)
            count += 1
            member = guild.get_member(contributor["discord_id"])
            if member and contributor_role not in member.roles:
                # Give Contributor Role
                print(member.name)
                await member.add_roles(contributor_role)
            print(f"Given Roles to {member.name if member else 'None'}")
           
        return

    @commands.command()
    async def github_profile(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            githubProfileInfoEmbed = discord.Embed(
                title="Show off your contributions on your github profile!",
                description="""Hey Contributor🔥

*Great work on contributing to Digital Public Goods*

You can showcase your achievements from the C4GT Community on your GitHub profile & distinguish yourself!🚀

*Follow the following steps to showcase your skills:*


1️⃣ It's essential to have a profile README on GitHub to showcase your achievements. If you don't have a profile README, create one by following the steps [here](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme#adding-a-profile-readme)

2️⃣ A link will be shared with you here. Don't forget to copy it📋

3️⃣ Then, open your profile README file on Github and edit it by adding the copied section from the bot response, wherever you want.💻

4️⃣ Commit the changes to your README on github.

*Congratulations on your hard work & achievement!!*🥳

Your profile page will now show your achievements from the C4GT community.🏆""",
            )

            desc = f"""Hey {ctx.author.name}

You have currently not earned any C4GT points or badges yet!
But worry not, you can do so by solving issue tickets & earning more points✨

**Discover issue tickets [here](https://www.codeforgovtech.in/community-program-projects).**🎟️🌟
**Know more about [badges & points](https://github.com/Code4GovTech/C4GT/wiki/Point-System-for-Contributors)**🧗"""

            noPointsGithubProfileEmbed = discord.Embed(title="", description=desc)
            user = self.postgres_client.read(
                "github_profile_data", "discord_id", ctx.author.id
            )
            if len(user) == 0:
                await ctx.send("Oops! It seems you aren't currently registered")
            elif len(user) == 1:
                data = user[0]
                if data["points"] == 0:
                    await ctx.send(embed=noPointsGithubProfileEmbed)
                else:
                    await ctx.send(embed=githubProfileInfoEmbed)
                    await ctx.send(
                        f"""Snippet for your Github Profile README:
```[![C4GTGithubDisplay](https://kcavhjwafgtoqkqbbqrd.supabase.co/storage/v1/object/public/c4gt-github-profile/{ctx.author.id}githubdisplay.jpg)](https://github.com/Code4GovTech)
Know more about: Code For GovTech ([Website](https://www.codeforgovtech.in) | [GitHub](https://github.com/Code4GovTech/C4GT/wiki)) | [Digital Public Goods (DPGs)](https://digitalpublicgoods.net/digital-public-goods/) | [India & DPGs](https://government.economictimes.indiatimes.com/blog/digital-public-goods-digital-public-infrastructure-an-evolving-india-story/99532036)```"""
                    )

    @update_contributors.before_loop
    async def before_update_loop(self):
        await self.bot.wait_until_ready()

    async def read_members_csv(self, file_path):
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row

            rows = []
            count = 0
            for row in reader:
                rows.append(row)
                count += 1
                if count == 10:
                    yield rows
                    rows = []
                    count = 0

            if rows:
                yield rows

    @commands.command(aliases=["point_system_breakdown", "point_system"])
    async def point_breakdown(self, ctx):
        message = f"""Hey **{ctx.author.name}**

Points are allocated on the following basis:bar_chart: :

:arrow_forward: **Number of PRs accepted**

:rocket:  **10 points per ticket are given**
:rocket: **Get more points for complex tickets**

- 1x for Low Complexity
- 2x for Medium Complexity
- 3x for High Complexity

:arrow_forward: **Number of PRs reviewed**

:rocket: **10 points per ticket for those who have been made a maintainer to review PRs**
:rocket:  **Get more points for complex tickets**

- 1x for Low Complexity
- 2x for Medium Complexity
- 3x for High Complexity
"""
        await ctx.channel.send(message)

    @commands.command(aliases=["my_points"])
    async def get_points(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            discord_id = ctx.author.id
            contributor = self.postgres_client.read(
                table="contributors_registration",
                query_key="discord_id",
                query_value=discord_id,
            )
            print(contributor)
            github_id = contributor[0]["github_id"]
            prs_raised = self.postgres_client.read(
                table="connected_prs", query_key="raised_by", query_value=github_id
            )
            prs_merged = self.postgres_client.read(
                table="connected_prs", query_key="merged_by", query_value=github_id
            )
            raise_points = 0
            merge_points = 0
            raiseTicketComplexity = {"low": 0, "medium": 0, "high": 0}
            mergeTicketComplexity = {"low": 0, "medium": 0, "high": 0}
            for pr in prs_raised:
                if pr["is_merged"]:
                    raise_points += pr["points"]
                    if pr["points"] == 10:
                        raiseTicketComplexity["low"] += 1
                    if pr["points"] == 20:
                        raiseTicketComplexity["medium"] += 1
                    if pr["points"] == 30:
                        raiseTicketComplexity["high"] += 1
            for pr in prs_merged:
                if pr["is_merged"]:
                    merge_points += pr["points"]
                    if pr["points"] == 10:
                        mergeTicketComplexity["low"] += 1
                    if pr["points"] == 20:
                        mergeTicketComplexity["medium"] += 1
                    if pr["points"] == 30:
                        mergeTicketComplexity["high"] += 1

            text = f"""Hey {ctx.author.name}

**You have a total of {raise_points+merge_points} points**🌟

▶️ **Points Basis PRs accepted - {raise_points} points**🔥

Number of tickets solved - {len(prs_raised)}
Points on tickets with low complexity - {raiseTicketComplexity["low"]*10} points
Points on tickets with medium complexity - {raiseTicketComplexity["medium"]*20} points
Points of tickets with high complexity - {raiseTicketComplexity["high"]*30} points

▶️ **Points as per PRs reviewed - {merge_points} points**🙌

Number of tickets reviewed - {len(prs_merged)}
Points on tickets with low complexity - {mergeTicketComplexity["low"]*10} points
Points on tickets with medium complexity - {mergeTicketComplexity["medium"]*20} points
Points of tickets with high complexity - {mergeTicketComplexity["high"]*30} points

Get coding and earn more points to get a spot on the leaderboard📈"""
            await ctx.channel.send(text)


async def setup(bot):
    await bot.add_cog(UserHandler(bot))
