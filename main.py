import asyncio
import os
import sys
from typing import Union

import discord
from discord.ext import commands

from cogs.vcCog import VCProgramSelection
from shared_migrations.db.discord_bot import DiscordBotQueries
from dotenv import load_dotenv, find_dotenv


# Since there are user defined packages, adding current directory to python path
current_directory = os.getcwd()
sys.path.append(current_directory)

load_dotenv(find_dotenv())


class AuthenticationView(discord.ui.View):
    def __init__(self, discord_userdata):
        super().__init__()
        github_auth_url = os.getenv("GITHUB_AUTHENTICATION_URL")
        button = discord.ui.Button(
            label="Authenticate Github",
            style=discord.ButtonStyle.url,
            url=f"{github_auth_url}/{discord_userdata}",
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

    name = discord.ui.TextInput(
        label="Please Enter Your Name",
        placeholder="To give you the recognition you deserve, could you please share your full name for the certificates!",
    )

    country = discord.ui.TextInput(
        label="Please Enter Your Country",
        placeholder="We'd love to know where you're from!",
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            print('inside on submit')
            user = interaction.user
            # Upsert user data to db
            user_data = {
                "name": self.name.value,
                "discord_id": user.id,
                "country": self.country.value,
                "roles": user.roles,
                "joined_at": user.joined_at,
                "is_active": True,
                "discord_username": user.display_name,
                "email":""
            }
            print('user data before updating contributor is ', user_data)
        except Exception as e:
            print('exception e ', e)
        try:
            response = await DiscordBotQueries().updateContributor(user_data)
            print("DB updated for user:", user_data["discord_id"])
        except Exception as e:
            print("Failed to update credentials for user: "+e)

        verifiedContributorRoleID = int(os.getenv("VERIFIED_ROLE_ID"))
        if verifiedContributorRoleID in [role.id for role in user.roles]:
            print("Already a verified contributor. Stopping.")
            await interaction.response.send_message(
                "Thanks! You are already a verified contributor on our server!",
                ephemeral=True,
            )
        else:
            # User is not verified. Make them link with github and run polling to check when auth is done.
            await interaction.response.send_message(
                "Thanks! Now please sign in via Github!.\n\n*Please Note: Post Github Authentication it may take upto 10 mins for you to be verified on this discord server. If there is a delay, please check back.*",
                view=AuthenticationView(user.id),
                ephemeral=True,
            )

            async def hasIntroduced():
                print("Checking...")
                authentication = False
                while not authentication:
                    print("Not authenticated. Waiting")
                    await asyncio.sleep(15)
                    authentication = await DiscordBotQueries().read("contributors_registration", "discord_id", user.id)
                print("User has authenticated")
                return True

            try:
                await asyncio.wait_for(hasIntroduced(), timeout=300)
                verifiedContributorRole = user.guild.get_role(verifiedContributorRoleID)
                if verifiedContributorRole:
                    try:
                        await user.add_roles(
                            verifiedContributorRole,
                            reason="Completed Auth and Introduction",
                        )
                        print("Added " + verifiedContributorRole.name + " role for: "+str(user.id))
                    except Exception as e:
                        print(e)
                else:
                    print("Verified contributor role not found with ID")
            except asyncio.TimeoutError:
                print("Timed out waiting for authentication for: "+str(user.id))


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
        print("Token is: "+os.getenv("TOKEN"))
        await client.start(os.getenv("TOKEN"))


asyncio.run(main())
