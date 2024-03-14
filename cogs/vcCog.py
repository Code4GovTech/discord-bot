from asyncio import sleep
from io import BytesIO
from uuid import uuid4

from discord import Embed, File, Interaction, Member, Role, SelectOption, enums, ui
from discord.ext import commands

from config.server import ServerConfig
from helpers.supabaseClient import SupabaseClient

"""
with io.BytesIO(image_bytes) as image_file:
            # Create a discord.File object from this file-like object
            discord_file = discord.File(fp=image_file, filename='image.png')  # You can change 'image.png' to your preferred filename

            # Send the image in response to a command or an event
            await message.channel.send('Here is the image:', file=discord_file)
"""


class CommunityVCView(ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

    def isCommunityContributor(self, roles: list[Role]):
        CommunityContributorRoleID = ServerConfig.Roles.CONTRIBUTOR_ROLE
        if CommunityContributorRoleID in [role.id for role in roles]:
            return True
        return False

    def getCommunityMember(self, memberId: Member):
        data = SupabaseClient().getLeaderboard(memberId)
        if data:
            contributor = data[0]
            return contributor
        return None

    def generateCommunityContributorView(self, type):
        if type == "certificate":
            return """Hey {}

You have earned a C4GT certificate for being an active DPG contributor! :partying_face:

Click [here]({}) to access your certificate :page_with_curl:"""
        elif type == "stats":
            return ""

    def getCertificateLink(self, contributor):
        badgeName = "Bronze"
        if contributor["diamond_badge"]:
            badgeName = "Diamond"
        elif contributor["ruby_badge"]:
            badgeName = "Ruby"
        if contributor["gold_badge"]:
            badgeName = "Gold"
        if contributor["silver_badge"]:
            badgeName = "Silver"
        return f"""https://credentials.codeforgovtech.in/c4gt/{contributor["github_url"][len('https://github.com/'):]}_{badgeName}.pdf"""

    def getStatsShowcaseImage(self, discordId=None, type=None):
        print(f"{discordId}-c4gt-contributions.jpeg")
        imageBytes = SupabaseClient().getStatsStorage(
            f"{discordId}-c4gt-contributions.jpeg"
        )
        with BytesIO(imageBytes) as imageFile:
            discordFile = File(fp=imageFile, filename="image.jpeg")
            return discordFile

    @ui.button(
        label="My Certificate",
        style=enums.ButtonStyle.blurple,
        custom_id=f"vc_view_button:my_cert:blurple",
    )
    async def serveCertificateLink(self, interaction: Interaction, button: ui.Button):
        SupabaseClient().logVCAction(interaction.user, "My Certificate Button")
        contributor = self.getCommunityMember(interaction.user.id)
        if contributor["points"] < 10:
            await interaction.response.send_message(
                f"You don't have enough DPG points! Get coding and earn more points to get a C4GT Community Badge📈",
                ephemeral=True,
            )
            return
        elif self.isCommunityContributor(interaction.user.roles):
            url = self.getCertificateLink(contributor)
            desc = self.generateCommunityContributorView("certificate")
            certificate = Embed(
                title="Certificate", description=desc.format(interaction.user.name, url)
            )
            await interaction.response.send_message(embed=certificate, ephemeral=True)
        else:
            await interaction.response.send_message(
                "You must have a valid contributor or mentor role to get a certificate!",
                ephemeral=True,
            )

    @ui.button(
        label="My DPG Profile",
        style=enums.ButtonStyle.blurple,
        custom_id=f"vc_view:my_profile:blurple",
    )
    async def serveDPGProfile(self, interaction: Interaction, button: ui.Button):
        SupabaseClient().logVCAction(interaction.user, "DPG Profile Button")
        if not self.isCommunityContributor(interaction.user.roles):
            await interaction.response.send_message(
                "You're not currently a registered contributor! Head over to <#1211992155673862204> and register as a Verified C4GT Community Contributor :fireworks:",
                ephemeral=True,
            )
        else:
            contributor = self.getCommunityMember(interaction.user.id)
            if contributor["points"] < 10:
                await interaction.response.send_message(
                    f"You don't have enough DPG points! Get coding and earn more points to get a C4GT Community Badge📈",
                    ephemeral=True,
                )
                return

            githubProfileInfoEmbed = Embed(
                title="C4GT Contributions!",
                description="""
    You can showcase your achievements from the C4GT Community on your GitHub profile & distinguish yourself!🚀

    *Follow the following steps to showcase your skills:*


    1️⃣ It's essential to have a profile README on GitHub to showcase your achievements. If you don't have a profile README, create one by following the steps [here](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme#adding-a-profile-readme)

    2️⃣ A markdown snippet containing a link to your C4GT Stats Image will be shared with you here. Don't forget to copy it📋

    3️⃣ Then, open your profile README file on Github and edit it by adding the copied section from the bot response, wherever you want.💻

    4️⃣ Commit the changes to your README on github.

    *Congratulations on your hard work & achievement!!*🥳

    Your profile page will now show your achievements from the C4GT community.🏆""",
            )
            message = f"""Snippet for your Github Profile README:
    ```[![C4GTGithubDisplay](https://kcavhjwafgtoqkqbbqrd.supabase.co/storage/v1/object/public/c4gt-github-profile/{interaction.user.id}-c4gt-contributions.jpeg)](https://github.com/Code4GovTech)
    Know more about: Code For GovTech ([Website](https://www.codeforgovtech.in) | [GitHub](https://github.com/Code4GovTech/C4GT/wiki)) | [Digital Public Goods (DPGs)](https://digitalpublicgoods.net/digital-public-goods/) | [India & DPGs](https://government.economictimes.indiatimes.com/blog/digital-public-goods-digital-public-infrastructure-an-evolving-india-story/99532036)```"""

            await interaction.response.send_message(
                embed=githubProfileInfoEmbed,
                ephemeral=True,
                file=self.getStatsShowcaseImage(discordId=interaction.user.id),
            )
            await interaction.followup.send(message, ephemeral=True)


class DMPVCView(ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

    def isDMPContributor(self, roles: list[Role]):
        DMPContributorRoleID = 1208970779769970769
        if DMPContributorRoleID in [role.id for role in roles]:
            return True
        return False

    def isDMPMentor(self, roles: list[Role]):
        DMPMentorRoleID = 1208970918311763980
        if DMPMentorRoleID in [role.id for role in roles]:
            return True
        return False

    def getCertificateLink(self, discordId):
        return "https://cdn.codeforgovtech.in/c4gt/KDwevedi_C4GT.pdf"

    def generateDMPContributorView(self, type):
        if type == "certificate":
            return """Hey {}

You have earned a C4GT certificate for your contributions in the C4GT Mentoring Program! :partying_face:

Click [here]({}) to access your certificate :page_with_curl:"""
        elif type == "stats":
            return ""

    def generateDMPMentorView(self, type):
        if type == "certificate":
            return """Hey {}

You have earned a C4GT certificate for your contributions as a DMP Mentor! :partying_face:

Click [here]({}) to access your certificate :page_with_curl:"""
        elif type == "stats":
            return ""

    @ui.button(
        label="My Certificate",
        style=enums.ButtonStyle.blurple,
        custom_id=f"dmp_vc_view_button:my_cert:blurple",
    )
    async def serveCertificateLink(self, interaction: Interaction, button: ui.Button):
        if self.isDMPContributor(interaction.user.roles):
            url = self.getCertificateLink(interaction.user.id)
            desc = self.generateDMPContributorView("certificate")
            certificate = Embed(
                title="Certificate", description=desc.format(interaction.user.name, url)
            )
            await interaction.response.send_message(embed=certificate, ephemeral=True)
        elif self.isDMPMentor(interaction.user.roles):
            url = self.getCertificateLink(interaction.user.id)
            desc = self.generateDMPMentorView("certificate")
            certificate = Embed(
                title="Certificate", description=desc.format(interaction.user.name, url)
            )
            await interaction.response.send_message(embed=certificate, ephemeral=True)
        else:
            await interaction.response.send_message(
                "You must have a valid contributor or mentor role to get a certificate!",
                ephemeral=True,
            )


class VCProgramSelection(ui.View):
    def __init__(self, *, timeout=None):
        super().__init__(timeout=timeout)

    async def resetSelectMenu(self, interaction):
        # Create a new instance of the same view to reset the select menu
        new_view = VCProgramSelection(timeout=self.timeout)
        # Update the original message with the new view
        await interaction.response.edit_message(view=new_view)

    @ui.select(
        custom_id="program_selection:vc",
        placeholder="Which program are you seeking credentials for?",
        options=[
            SelectOption(label="Community Program", value="ccbp"),
            # SelectOption(label="Mentoring Program", value="dmp")
        ],
    )
    async def selectAProgram(self, interaction: Interaction, select: ui.Select):
        SupabaseClient().logVCAction(interaction.user, "Clicked on Dropdown")
        selected_option = select.values[0]
        if selected_option == "ccbp":
            await interaction.response.send_message(
                view=CommunityVCView(), ephemeral=True
            )
        # elif selected_option == "dmp":
        #     await interaction.response.send_message(view=DMPVCView(), ephemeral=True)
        else:
            await interaction.response.send_message(
                "Unknown selection.", ephemeral=True
            )
        await interaction.message.edit(view=VCProgramSelection(timeout=self.timeout))


class VerifiableCredentials(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(aliases=["vc", "certificate"])
    async def renderCertificateView(self, ctx):
        await ctx.channel.send("Certificates", view=CommunityVCView())

    @commands.command(aliases=["choose"])
    async def renderCertificateView(self, ctx):
        await ctx.channel.send("Programs", view=VCProgramSelection())


async def setup(bot):
    await bot.add_cog(VerifiableCredentials(bot))
