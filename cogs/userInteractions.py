import csv
import os

import discord
from discord.ext import commands, tasks

from helpers.supabaseClient import SupabaseClient

VERIFIED_CONTRIBUTOR_ROLE_ID = 1123967402175119482


class Announcement:
    def __init__(self, member):
        self.member = member

    async def create_embed(self):
        embed = discord.Embed(
            title=f"Hey {self.member.name}!",
            description=f"""
If you submitted a proposal and did not make it to the C4GT mentoring program  or you missed the deadline for applying, worry not!

**We have launched the C4GT Community Program Today!**🚀 🚀

Through this program you can contribute to multiple projects, build your skills & get exclusive rewards & goodies.

How will the Community Program work?🤔
- **Explore Projects** 📋 - Explore [projects](https://www.codeforgovtech.in/community-projects) as per your skills, interest in the domain & more.
- **Get Coding** 💻  - Interact with mentors for clarity if required & solve the project
- **Points & Rewards** 🎁 - On each PR merged, you will get points. These points will give you badges & C4GT goodies. Read more about the point system [here](https://github.com/Code4GovTech/C4GT/wiki/Point-System-for-Contributors)

How can you participate?
- **Link Discord & GitHub** 🤝 - Use this [link]({os.getenv('FLASK_HOST')}/authenticate/{self.member.id})  to connect these platforms, so we can track your activity & calculate points
- **Explore Issues Listed** 🖥️ - Keep an eye on our project page as more issues will be released every week.
- **Ask Questions** ❓ - Ask away your queries on the #c4gtcommunitychannel

So what are you waiting for? Let's get started!!""",
            color=0x00FFFF,
        )

        # embed.add_field(name="How will the Community Program work?🤔",
        #                 value="- **Explore Projects** 📋 - Explore [projects](https://c4gt-ccbp-projects.vercel.app/) as per your skills, interest in the domain & more.\n- **Get Coding** 💻 - Interact with mentors for clarity if required & solve the project\n- **Points & Rewards** 🎁 - On each PR merged, you will get points. These points will give you badges & C4GT goodies. Read more about the point system [here](https://github.com/Code4GovTech/C4GT/wiki/Point-System-for-Contributors)")

        # embed.add_field(name="How can you participate?",
        #                 value=f"- **Link Discord & GitHub** 🤝 - Use this [link]({os.getenv('''FLASK_HOST''')}/authenticate/{self.member.id}) to connect these platforms, so we can track your activity & calculate points\n- **Explore Issues Listed** 🖥️ - Keep an eye on our project page as more issues will be released every week.\n- **Ask Questions** ❓ - Ask away your queries on the #c4gtcommunitychannel")
        # embed.add_field(name="So what are you waiting for? Let's get started!!", value='')
        return embed


# This is a Discord View that is a set of UI elements that can be sent together in a message in discord.
# This view send a link to Github Auth through c4gt flask app in the form of a button.
class RegistrationModal(discord.ui.Modal, title="Contributor Registration"):
    name = discord.ui.TextInput(label="Name")


class AuthenticationView(discord.ui.View):
    def __init__(self, discord_userdata):
        super().__init__()
        self.timeout = None
        button = discord.ui.Button(
            label="Authenticate Github",
            style=discord.ButtonStyle.url,
            url=f"https://github-app.c4gt.samagra.io/authenticate/{discord_userdata}",
        )
        self.add_item(button)
        self.message = None


class UserHandler(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(aliases=["join"])
    async def join_as_contributor(self, ctx):
        # create a direct messaging channel with the one who executed the command
        if isinstance(ctx.channel, discord.DMChannel):
            userdata = str(ctx.author.id)
            view = AuthenticationView(userdata)
            await ctx.send(
                "Please authenticate your github account to register in the C4GT Community",
                view=view,
            )
        # Command logic for DMs
        else:
            # Command logic for other channels (e.g., servers, groups)
            await ctx.send("Please use this command in Bot DMs.")
        # Command logic for DMs
        userdata = str(ctx.author.id)
        view = AuthenticationView(userdata)
        # await dmchannel.send("Please authenticate your github account to register for Code for GovTech 2023", view=view)

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
            user = SupabaseClient().read(
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
            contributor = SupabaseClient().read(
                table="contributors_registration",
                query_key="discord_id",
                query_value=discord_id,
            )
            print(contributor)
            github_id = contributor[0]["github_id"]
            prs_raised = SupabaseClient().read(
                table="connected_prs", query_key="raised_by", query_value=github_id
            )
            prs_merged = SupabaseClient().read(
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
