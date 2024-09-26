import asyncio
import json
import os
import sys
from typing import Union

import aiohttp
import discord
import dotenv
from discord.ext import commands

from cogs.vcCog import VCProgramSelection
from helpers.supabaseClient import SupabaseClient

# Since there are user defined packages, adding current directory to python path
current_directory = os.getcwd()
sys.path.append(current_directory)

dotenv.load_dotenv(".env")


class AuthenticationView(discord.ui.View):
    def __init__(self, discord_userdata):
        super().__init__()
        button = discord.ui.Button(
            label="Authenticate Github",
            style=discord.ButtonStyle.url,
            url=f"https://backend.c4gt.samagra.io/authenticate/{discord_userdata}",
        )
        self.add_item(button)
        self.message = None


class RegistrationModal(discord.ui.Modal):
    def __init__(
        self,
        *,
        title: str = None,
        timeout: Union[float, None] = None,
        custom_id: str = None,
    ) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)

    async def post_data(self, table_name, data):
        url = f"{os.getenv('SUPABASE_KEY')}/rest/v1/{table_name}",
        headers = {
            "apikey": f"{os.getenv('SUPABASE_KEY')}",
            "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=headers, data=json.dumps(data)
            ) as response:
                if response.status == 200:
                    print("Data posted successfully")
                else:
                    print("Failed to post data")
                    print("Status Code:", response.status)

    name = discord.ui.TextInput(
        label="Please Enter Your Name",
        placeholder="To give you the recognition you deserve, could you please share your full name for the certificates!",
    )

    country = discord.ui.TextInput(
        label="Please Enter Your Country",
        placeholder="We'd love to know where you're from!",
    )

    async def on_submit(self, interaction: discord.Interaction):
        user = interaction.user
        supaClient = SupabaseClient()
        await interaction.response.send_message(
            "Thanks! Now please sign in via Github!",
            view=AuthenticationView(user.id),
            ephemeral=True,
        )
        await self.post_data("contributors_discord",
                             {
                                 "name": self.name.value,
                                 "discord_id": user.id,
                                 "country": self.country.value
                             }
                             )

        verifiedContributorRoleID = 1247854311191351307
        print("User:", type(user))
        if verifiedContributorRoleID in [role.id for role in user.roles]:
            return
        else:
            async def hasIntroduced():
                print("Checking hasIntroduced...")
                try:
                    print("Trying has authenticated")
                    authentication = supaClient.read(
                        "contributors_registration", "discord_id", user.id
                    )
                except Exception as e:
                    print("Failed hasIntroduced: "+e)
                print("Authentication: "+authentication)
                while not authentication:
                    print("Not authenticated")
                    await asyncio.sleep(30)
                print("Found!")
                discordEngagement = supaClient.read(
                    "discord_engagement", "contributor", user.id
                )[0]
                print("Discord engagement: "+discordEngagement)
                return discordEngagement["has_introduced"]

            try:
                print("Trying hasIntroduced")
                await asyncio.wait_for(hasIntroduced(), timeout=1000)
                print("Timedout on hasIntroduced")
                verifiedContributorRole = user.guild.get_role(verifiedContributorRoleID)
                if verifiedContributorRole:
                    if verifiedContributorRole not in user.roles:
                        await user.add_roles(
                            verifiedContributorRole,
                            reason="Completed Auth and Introduction",
                        )
            except asyncio.TimeoutError:
                print("Timed out waiting for authentication")


class RegistrationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Register",
        style=discord.enums.ButtonStyle.blurple,
        custom_id="registration_view:blurple",
    )
    async def reg(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RegistrationModal(
            title="Contributor Registration", custom_id="registration:modal"
        )
        await interaction.response.send_modal(modal)


class C4GTBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned_or("!"), intents=intents
        )

    async def setup_hook(self) -> None:
        # Register the persistent view for listening here.
        # Note that this does not send the view to any message.
        # In order to do this you need to first send a message with the View, which is shown below.
        # If you have the message_id you can also pass it as a keyword argument, but for this example
        # we don't have one.
        self.add_view(RegistrationView())
        self.add_view(VCProgramSelection())


client = C4GTBot()


@client.command(aliases=["registration"])
async def registerAsContributor(ctx):
    await ctx.channel.send(
        "Please register using Github to sign up as a C4GT Contributor",
        view=RegistrationView(),
    )


# alert message on commandline that bot has successfully logged in


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


# load cogs
async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")

    # ### All listener cogs
    for filename in os.listdir("./cogs/listeners"):
        if filename.endswith("cog.py"):
            await client.load_extension(f"cogs.listeners.{filename[:-3]}")


async def main():
    async with client:
        await load()
        await client.start(os.getenv("TOKEN"))


asyncio.run(main())
