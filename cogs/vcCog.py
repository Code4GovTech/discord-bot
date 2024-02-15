from typing import Optional

from discord import Embed, Interaction, enums, ui
from discord.ext import commands

from config.server import ServerConfig
from helpers.supabaseClient import SupabaseClient

#             desc = f"""Hey {ctx.author.name}

# You have currently not earned any C4GT points or badges yet!
# But worry not, you can do so by solving issue tickets & earning more points✨

# **Discover issue tickets [here](https://www.codeforgovtech.in/community-program-projects).**🎟️🌟
# **Know more about [badges & points](https://github.com/Code4GovTech/C4GT/wiki/Point-System-for-Contributors)**🧗"""

#             noPointsGithubProfileEmbed = discord.Embed(title="", description=desc)
#             user = SupabaseClient().read(
#                 "github_profile_data", "discord_id", ctx.author.id
#             )
#             if len(user) == 0:
#                 await ctx.send("Oops! It seems you aren't currently registered")
#             elif len(user) == 1:
#                 data = user[0]
#                 if data["points"] == 0:
#                     await ctx.send(embed=noPointsGithubProfileEmbed)
#                 else:
#                     await ctx.send(embed=githubProfileInfoEmbed)


class VCView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(
        label="My Certificate",
        style=enums.ButtonStyle.blurple,
        custom_id="vc_view:my_cert:blurple",
    )
    async def getCertificateLink(self, interaction: Interaction, button: ui.Button):
        verifiedContributorRoleId = ServerConfig.Roles.CONTRIBUTOR_ROLE
        url = "http://139.59.20.91:9000/c4gt/Kanav%20Dwevedi_Ninja%20Badge.pdf"
        desc = f"""Hey {interaction.user.name}

You have earned a C4GT certificate for being an active DPG contributor and earning 50 DPG points! :partying_face:

Click [here]({url}) to access your certificate :page_with_curl:"""
        certificateLink = Embed(title="Certificates", description=desc)
        # if verifiedContributorRoleId not in [role.id for role in interaction.user.roles]:
        #     #Not a Verified Contributor
        #     await interaction.response.send_message("Not a verified contributor", ephemeral=True)
        # else:
        await interaction.response.send_message(embed=certificateLink, ephemeral=True)

    @ui.button(
        label="My DPG Profile",
        style=enums.ButtonStyle.blurple,
        custom_id="vc_view:my_profile:blurple",
    )
    async def getDPGProfile(self, interaction: Interaction, button: ui.Button):
        verifiedContributorRoleId = ServerConfig.Roles.CONTRIBUTOR_ROLE
        # if verifiedContributorRoleId not in [role.id for role in interaction.user.roles]:
        #     #Not a Verified Contributor
        #     await interaction.response.send_message("Not a verified contributor", ephemeral=True)
        if True:
            githubProfileInfoEmbed = Embed(
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
            message = f"""Snippet for your Github Profile README:
```[![C4GTGithubDisplay](https://kcavhjwafgtoqkqbbqrd.supabase.co/storage/v1/object/public/c4gt-github-profile/{interaction.user.id}githubdisplay.jpg)](https://github.com/Code4GovTech)
Know more about: Code For GovTech ([Website](https://www.codeforgovtech.in) | [GitHub](https://github.com/Code4GovTech/C4GT/wiki)) | [Digital Public Goods (DPGs)](https://digitalpublicgoods.net/digital-public-goods/) | [India & DPGs](https://government.economictimes.indiatimes.com/blog/digital-public-goods-digital-public-infrastructure-an-evolving-india-story/99532036)```"""

            await interaction.response.send_message(
                message, embed=githubProfileInfoEmbed, ephemeral=True
            )


class VerifiableCredentials(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(aliases=["vc", "certificate"])
    async def renderCertificateView(self, ctx):
        await ctx.channel.send("Certificates", view=VCView())


async def setup(bot):
    await bot.add_cog(VerifiableCredentials(bot))
